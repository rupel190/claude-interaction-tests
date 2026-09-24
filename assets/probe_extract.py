#!/usr/bin/env python3
"""probe_extract — turn a round of blind interaction-test probes into a scoring skeleton.

Given the task IDs of a round's probe agents, this reads each agent's JSONL transcript and writes
a ``results-skeleton.md`` holding, per probe:

* the DELIVERED REPORT, verbatim — the hand-back message, never a summary of it. The scorer reads
  the body. A probe's own TL;DR, and any text it wrote AFTER handing back (which its caller never
  received), are shown separately and labelled "do not score from this".
* the HEDGES in that body — sentences where the probe says what it did NOT check ("general
  reasoning only", "I did not open", "quoted from"). A scorecard that repeats a probe's confident
  line while dropping its hedge is relay drift in the scorecard itself.
* the TOOL TRAIL — every file it searched or read, in order, with line ranges mapped to the
  markdown headings they cover.
* an INDEX-FIRE hint for the first move — whether the search terms and paths of the probe's FIRST
  tool call appear in the always-loaded instruction files it was handed, and which block of those
  files matches best. The first move is made before any file is opened, so terms that can only
  have come from the always-loaded index are the machine-visible trace of that index firing.
* the DECLARED trail — the probe's own ``WHAT INFORMED YOU`` section, first item surfaced.
* grep FLAGS, as candidates for a human to adjudicate, never as verdicts:
  - boilerplate: known over-fire text (configure per repo, e.g. a freshness caveat that an
    always-loaded instruction adds to every answer);
  - argued-past: sentences that explain why a closed / rejected / refuted entry does NOT apply —
    the latent over-fire tell. A candidate whose contrast phrase already appears in the index is
    marked "echoes index": the probe may be restating the entry rather than arguing past it.
    ⭐ Plus a STRUCTURAL tell no phrase list can see: the report PROCEEDS while naming a CLOSED row of
    the delivered index by its title. An argue-past is often implicit — a variant proposed inside a
    closed class, with only a sibling's inapplicability explained — and this is how it shows.
* HARNESS facts, measured from the transcript rather than assumed: agent type, model, working
  directory, the instruction files actually delivered (bytes, sha256, and — given ``--repo`` — the
  commit whose content they match), expected strings present or absent in them, first-turn prompt
  tokens, turns, tool calls, and violations (edits, delegation, touching a sealed path).

What it does NOT establish
--------------------------
* It never scores. "fired?", "which copy", "right answer?" are left as ⬜ for the scorer.
* The index-fire hint is lexical. A probe can recall an entry and search in its own words (no
  hint), or search a common word that happens to be in the index (a false hint). Read the block it
  names before crediting it.
* The flags are regex heuristics with known false positives. They exist so nothing is MISSED;
  every flagged line still needs reading. The closed-row tell matches a row's TITLE as the report
  quotes it (first 28 normalised characters), so a paraphrased citation is missed.
* Headings for a read range are taken from the file at the commit the probe's own git snapshot
  names (falling back to the working tree); a file edited since may map differently.
* The gitStatus a probe receives is taken when the probe LAUNCHES, while its instruction files are
  a snapshot from when the parent PROCESS started — the two can disagree. The delivered content is
  the authority on what the probe was given; match it by content, never by the git snapshot.

Transcripts are found by task ID under (in order) any ``--transcript-glob`` given, then
``~/.claude/projects/*/*/subagents/agent-{id}.jsonl`` and
``$TMPDIR/claude-*/*/*/tasks/{id}.output`` (often a symlink to the former). A plain-text
``.output`` (not JSONL) is accepted and treated as the report alone.

Usage
-----
    probe_extract.py ROUND_DIR [LABEL=TASK_ID ...] [--ids FILE] [--repo PATH]
                     [--config FILE] [--expect STR ...] [--expect-absent STR ...]
                     [--sealed PATH ...] [--out FILE]

``ROUND_DIR/ids.txt`` (``LABEL TASK_ID`` per line, ``#`` comments) is read when no IDs are
given. ``ROUND_DIR/predictions.md`` is read for a markdown table whose first cell starts with
each label; its expected/predicted and confidence columns are copied into the table.
``ROUND_DIR/round.json`` may carry ``{"expect": [...], "expect_absent": [...], "sealed": [...]}``:
strings the round assumes the delivered index DOES / does NOT carry, checked per probe.

The config (``--config``, default ``extract.json`` beside this script, optional) is JSON:
    {"repo": "/path/to/repo-under-test",
     "sealed": ["/path/to/answer-bank"],
     "boilerplate": ["regex", ...],
     "argued_past_extra": ["regex", ...],
     "closed_table_header": "regex matching the header row of the index's closed-entries table",
     "hedge_extra": ["regex", ...]}
Relative paths in the config resolve against the config file's directory.

Standard library only; Python 3.10+.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ----------------------------------------------------------------------------- defaults

DEFAULT_TRANSCRIPT_GLOBS = [
    "~/.claude/projects/*/*/subagents/agent-{id}.jsonl",
    os.path.join(os.environ.get("TMPDIR", "/tmp"), "claude-*/*/*/tasks/{id}.output"),
]

# Sentences where a probe declares the limits of its own evidence. Deliberately epistemic: a
# caveat about the PLAN ("this moves trims") is not a hedge; "I did not open X" is.
HEDGE_PATTERNS = [
    r"general reasoning only",
    r"\bI (?:did not|didn't|have not|haven't|could not|couldn't) (?:open|read|check|verify|"
    r"confirm|run|re-?measure|measure|look|test|find|see|reproduce)",
    r"\b(?:not|never) (?:verified|confirmed|re-?measured|checked|opened)\b",
    r"\bunverified\b",
    r"\bquoted from\b",
    r"\brests? on\b",
    r"\b(?:I|we) (?:assume|am assuming|believe|suspect|infer)\b",
    r"\b(?:unclear|not established|cannot tell|can't tell|could not determine)\b",
    r"\bnothing (?:in the repo|here) (?:informed|says|specifies)\b",
    r"\bfrom memory\b",
]

# Contrast + closure: the probe explains why something closed does not bind its case.
ARGUED_PAST_PATTERNS = [
    r"\b(?:does not|doesn't|do not|don't|would not|wouldn't) (?:apply|bind|cover|reach|block|"
    r"govern|forbid|close)\b",
    r"\bnot (?:the same|what (?:was|the \w+ (?:row|entry)) (?:tried|rejected|refuted|closed))",
    r"\b(?:is|was|remains|stays) (?:still )?(?:open|live)\b.{0,40}\bnot (?:closed|dead)\b",
    r"\bopen,? not closed\b",
    r"\bnot closed\b",
    r"\b(?:differs|different|distinct) from (?:the |what |that )?(?:\w+ ){0,4}"
    r"(?:tried|rejected|refuted|closed|retired)",
    r"\bunlike the (?:\w+ ){0,3}(?:rejected|refuted|closed|retired|tried)",
    r"\boutside (?:the|that|this) (?:closed )?(?:class|row|entry|verdict)\b",
    r"\b(?:the|that|this) (?:row|entry|verdict|refutation|rejection) (?:is|was) (?:about|"
    r"scoped to|limited to|only about)\b",
    r"\b(?:revisit|reopen)(?:ing)? condition\b.{0,60}\b(?:met|holds|satisfied)\b",
    r"\bnot (?:an instance|a case|a variant) of\b",
    r"\bdoes not fall (?:under|inside|within)\b",
    # a hold / rejection whose stated reason has lapsed
    r"\bunblocked\b",
    r"\bno longer (?:applies|apply|blocks|holds|binds|stands|relevant)\b",
    r"\b(?:held|blocked|parked|shelved|deferred|closed|rejected)\b[^.]{0,40}\bonly because\b",
    r"\b(?:hold|blocker|precondition|prerequisite)\b[^.]{0,60}\b(?:is|has been|was) (?:now )?"
    r"(?:met|lifted|gone|satisfied|cleared)\b",
]

STOP = {"the", "and", "has", "have", "been", "was", "were", "that", "this", "its",
         "does", "doesn", "don", "with", "for", "but", "are", "is", "what", "from", "still"}

SUMMARY_PATTERNS = [r"TL;DR", r"^\s*▶", r"^\s*(?:\*\*)?(?:Summary|In short|Bottom line)\b"]

ALWAYS_LOADED_HINTS = [r"CLAUDE\.md", r"\.claude/rules", r"MEMORY\.md", r"\bin context\b",
                       r"\bpreloaded\b", r"\balways[- ]loaded\b", r"\bthe index\b",
                       r"\bsystem prompt\b"]

READ_CMDS = {"cat", "head", "tail", "sed", "less", "bat", "nl", "wc", "awk", "cut", "jq", "diff"}
SEARCH_CMDS = {"rg", "grep", "egrep", "ag", "ack", "git-grep"}
LIST_CMDS = {"fd", "find", "ls", "tree", "stat", "du"}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
DELEGATE_TOOLS = {"Agent", "Task"}
RISKY_BASH = [r"\bsed -i\b", r"\bgit (?:commit|push|checkout|reset|stash|rebase|merge)\b",
              r"\bpytest\b", r"\bnix develop\b", r"(?<![<>=\d&])>>?(?![&=])\s*(?!/dev/null)[\w./~-]+",
              r"\brm -", r"\bmv \b", r"\btee\b"]
NOISE_CMDS = {"echo", "printf", "true", "false", "sleep", ":"}
FILE_RE = re.compile(r"(?:(?:\.{1,2}/|/|~/)?[\w@.+-]+/)*[\w@.+-]+\.(?:md|py|pyi|yaml|yml|json|"
                     r"jsonl|toml|txt|csv|html|svg|sh|nix|cfg|ini|exp|inf)\b")

# ----------------------------------------------------------------------------- data


@dataclass
class Step:
    n: int
    tool: str
    kind: str                 # search | read | list | git | python | other | write | delegate
    target: str               # file / pattern / command gist
    lines: tuple[int, int] | None = None
    terms: list[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class Probe:
    label: str
    task_id: str
    path: Path | None
    meta: dict = field(default_factory=dict)
    prompt: str = ""
    report: str = ""
    report_source: str = ""
    post_text: str = ""
    steps: list[Step] = field(default_factory=list)
    instructions: list[dict] = field(default_factory=list)
    cwd: str = ""
    model: str = ""
    date: str = ""
    git_head: str = ""
    first_turn_tokens: int | None = None
    turns: int = 0
    output_tokens: int = 0
    violations: list[str] = field(default_factory=list)
    sealed_hits: list[str] = field(default_factory=list)
    repo_root: str = ""
    error: str = ""


# ----------------------------------------------------------------------------- loading


def find_transcript(task_id: str, globs: list[str]) -> Path | None:
    p = Path(os.path.expanduser(task_id))
    if p.exists():
        return p
    for g in globs:
        hits = sorted(glob.glob(os.path.expanduser(g.format(id=task_id))))
        if hits:
            return Path(hits[0]).resolve()
    return None


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text":
                    out.append(c.get("text", ""))
                elif c.get("type") == "tool_result":
                    out.append(_text_of(c.get("content")))
            elif isinstance(c, str):
                out.append(c)
        return "\n".join(out)
    return "" if content is None else str(content)


def load_probe(label: str, task_id: str, globs: list[str], sealed: list[str]) -> Probe:
    path = find_transcript(task_id, globs)
    pr = Probe(label=label, task_id=task_id, path=path)
    if path is None:
        pr.error = "transcript not found"
        return pr
    meta_path = path.with_suffix(".meta.json")
    if meta_path.exists():
        try:
            pr.meta = json.loads(meta_path.read_text())
        except json.JSONDecodeError:
            pass
    raw = path.read_text(errors="replace")
    lines = raw.splitlines()
    try:
        records = [json.loads(ln) for ln in lines if ln.strip()]
    except json.JSONDecodeError:
        pr.report, pr.report_source = raw, "plain-text output file (no transcript structure)"
        return pr

    seen_requests: dict[str, dict] = {}
    results: dict[str, str] = {}
    last_text_after_tools: list[str] = []
    handback_seen = False
    step_n = 0
    for rec in records:
        rtype = rec.get("type")
        if rtype == "attachment":
            att = rec.get("attachment") or {}
            at = att.get("type")
            if at == "instructions":
                pr.instructions = [
                    {"path": f.get("path", "?"), "type": f.get("type", "?"),
                     "content": f.get("content", "")}
                    for f in att.get("files", [])]
            elif at == "environment":
                pr.cwd = (att.get("snapshot") or {}).get("workingDirectory", pr.cwd)
            elif at == "model":
                pr.model = (att.get("identity") or {}).get("modelId", "")
            elif at == "date":
                pr.date = att.get("date", "")
            elif at == "session_context":
                gs = (att.get("context") or {}).get("gitStatus", "")
                m = re.search(r"Recent commits:\s*\n([0-9a-f]{6,40})", gs)
                if m:
                    pr.git_head = m.group(1)
            continue
        if not pr.cwd and rec.get("cwd"):
            pr.cwd = rec["cwd"]
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        content = msg.get("content")
        if role == "user" and not pr.prompt and rtype == "user" and not rec.get("isMeta"):
            pr.prompt = _text_of(content)
            continue
        if role == "user" and isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    results[c.get("tool_use_id", "")] = _text_of(c.get("content"))
        if role != "assistant":
            continue
        rid = rec.get("requestId") or msg.get("id") or rec.get("uuid")
        usage = msg.get("usage") or {}
        if rid not in seen_requests:
            seen_requests[rid] = usage
            if pr.first_turn_tokens is None and usage:
                pr.first_turn_tokens = (usage.get("input_tokens", 0)
                                        + usage.get("cache_creation_input_tokens", 0)
                                        + usage.get("cache_read_input_tokens", 0))
        elif usage.get("output_tokens", 0) >= seen_requests[rid].get("output_tokens", 0):
            seen_requests[rid] = usage
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text" and c.get("text", "").strip():
                if handback_seen:
                    pr.post_text += c["text"].strip() + "\n"
                else:
                    last_text_after_tools.append(c["text"])
            elif c.get("type") == "tool_use":
                name, inp = c.get("name", "?"), c.get("input") or {}
                if name == "SubagentHandback":
                    pr.report = inp.get("message", "")
                    pr.report_source = "SubagentHandback message (what the caller received)"
                    handback_seen = True
                    continue
                last_text_after_tools = []
                step_n += 1
                pr.steps.extend(parse_tool_call(step_n, name, inp))
                if name in WRITE_TOOLS:
                    pr.violations.append(f"step {step_n}: {name} {inp.get('file_path', '')}")
                if name in DELEGATE_TOOLS:
                    pr.violations.append(f"step {step_n}: delegated via {name} "
                                         f"({inp.get('subagent_type', '')})")
                if name == "Bash":
                    cmd = inp.get("command", "")
                    for pat in RISKY_BASH:
                        m = re.search(pat, _strip_heredocs(cmd))
                        if m:
                            pr.violations.append(f"step {step_n}: possible write/long-run "
                                                 f"`{m.group(0).strip()}` (check by hand)")
                            break
                blob = json.dumps(inp)
                for s in sealed:
                    if s and s in blob:
                        pr.sealed_hits.append(f"step {step_n}: tool input names sealed path {s}")
    if not pr.report:
        pr.report = "\n".join(last_text_after_tools).strip()
        pr.report_source = "final assistant text (no hand-back tool call found)"
    pr.turns = len(seen_requests)
    pr.output_tokens = sum(u.get("output_tokens", 0) for u in seen_requests.values())
    for tid, txt in results.items():
        for s in sealed:
            if s and s in txt:
                pr.sealed_hits.append(f"a tool RESULT shown to the probe names sealed path {s}: "
                                      f"«{_snip(txt, txt.find(s), 90)}»")
    for s in sealed:
        if s and pr.cwd and (pr.cwd == s or pr.cwd.startswith(s.rstrip('/') + '/')):
            pr.sealed_hits.insert(0, f"⛔ the probe's WORKING DIRECTORY is inside sealed path {s}")
    pr.repo_root = _repo_from_steps(pr) or ""
    return pr


# ----------------------------------------------------------------------------- tool parsing


def _strip_heredocs(cmd: str) -> str:
    return re.sub(r"<<-?\s*['\"]?(\w+)['\"]?\n.*?\n\s*\1\b", "<<HEREDOC", cmd, flags=re.S)


def _split_segments(cmd: str) -> list[list[str]]:
    cmd = _strip_heredocs(cmd)
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        lex.commenters = ""
        toks = list(lex)
    except ValueError:
        return [s.split() for s in re.split(r"\s*(?:;|&&|\|\||\||\n)\s*", cmd) if s.strip()]
    segs, cur = [], []
    for t in toks:
        if t and set(t) <= set(";&|"):
            if cur:
                segs.append(cur)
            cur = []
        elif "\n" in t and not t.strip():
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        segs.append(cur)
    return segs


_VALUE_FLAGS_SEARCH = {"-g", "--glob", "-t", "--type", "-T", "--type-not", "-m", "--max-count",
                       "-A", "-B", "-C", "--context", "-M", "--max-columns", "-f", "--file",
                       "--include", "--exclude", "-j", "--threads", "--sort", "-r", "--replace"}


def _pattern_terms(pattern: str) -> list[str]:
    """Split a search regex into top-level alternatives."""
    parts, depth, cur = [], 0, ""
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\" and i + 1 < len(pattern):
            cur += pattern[i:i + 2]
            i += 2
            continue
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch == "|" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    parts.append(cur)
    return [p for p in (x.strip() for x in parts) if len(re.sub(r"\\.|[^\w]", "", p)) >= 4]


def parse_tool_call(n: int, name: str, inp: dict) -> list[Step]:
    if name == "Read":
        off, lim = inp.get("offset"), inp.get("limit")
        rng = None
        if off or lim:
            a = int(off or 1)
            rng = (a, a + int(lim or 2000) - 1)
        return [Step(n, name, "read", inp.get("file_path", "?"), rng)]
    if name == "Grep":
        pat = inp.get("pattern", "")
        return [Step(n, name, "search", inp.get("path", ".") or ".", None, _pattern_terms(pat),
                     raw=pat)]
    if name == "Glob":
        return [Step(n, name, "list", inp.get("pattern", "?"))]
    if name in WRITE_TOOLS:
        return [Step(n, name, "write", inp.get("file_path", "?"))]
    if name in DELEGATE_TOOLS:
        return [Step(n, name, "delegate", inp.get("description", "?"))]
    if name != "Bash":
        return [Step(n, name, "other", json.dumps(inp)[:80])]
    cmd = inp.get("command", "")
    steps: list[Step] = []
    for seg in _split_segments(cmd):
        while seg and (re.match(r"^\w+=", seg[0]) or seg[0] in {"timeout", "env", "nice",
                                                                 "time", "command"}):
            seg = seg[1:] if not seg[0] == "timeout" else seg[2:]
        if not seg:
            continue
        head = os.path.basename(seg[0])
        args = seg[1:]
        if head in NOISE_CMDS or head.startswith("-") or head.startswith("$("):
            continue
        if head == "cd":
            steps.append(Step(n, "Bash", "cd", args[0] if args else "~"))
            continue
        if head in {"nix", "direnv"}:
            continue
        if head in SEARCH_CMDS or (head == "git" and args[:1] == ["grep"]):
            if head == "git":
                args = args[1:]
            pattern, paths = None, []
            i = 0
            while i < len(args):
                a = args[i]
                if a in ("-e", "--regexp") and i + 1 < len(args):
                    pattern = args[i + 1] if pattern is None else pattern + "|" + args[i + 1]
                    i += 2
                    continue
                if a in _VALUE_FLAGS_SEARCH:
                    i += 2
                    continue
                if a.startswith("-"):
                    i += 1
                    continue
                if pattern is None:
                    pattern = a
                else:
                    paths.append(a)
                i += 1
            terms = _pattern_terms(pattern or "")
            for p in paths or ["."]:
                steps.append(Step(n, "Bash", "search", p, None, terms, raw=pattern or ""))
            continue
        if head == "sed":
            rng, files = None, []
            for a in args:
                m = re.fullmatch(r"'?(\d+),(\d+)p'?", a)
                if m:
                    rng = (int(m.group(1)), int(m.group(2)))
                elif not a.startswith("-") and FILE_RE.search(a) and not a.startswith("s/"):
                    files.append(a)
            for f in files:
                steps.append(Step(n, "Bash", "read", f, rng))
            continue
        if head in READ_CMDS:
            rng = None
            if head == "head":
                for i, a in enumerate(args):
                    if a == "-n" and i + 1 < len(args) and args[i + 1].isdigit():
                        rng = (1, int(args[i + 1]))
                    elif re.fullmatch(r"-\d+", a):
                        rng = (1, int(a[1:]))
            for a in args:
                if not a.startswith("-") and FILE_RE.fullmatch(a.strip("'\"")):
                    steps.append(Step(n, "Bash", "read", a, rng))
            continue
        if head in LIST_CMDS:
            steps.append(Step(n, "Bash", "list", " ".join(seg)[:90]))
            continue
        if head == "git":
            sub = args[0] if args else ""
            terms = []
            for i, a in enumerate(args):
                if a == "-S" and i + 1 < len(args):
                    terms.append(re.escape(args[i + 1]))
                elif a.startswith("-S") and len(a) > 2:
                    terms.append(re.escape(a[2:]))
                elif a.startswith("--grep="):
                    terms.append(a[7:])
            showpath = [a.split(":", 1)[1] for a in args if re.match(r"^[\w./~^-]+:[\w./-]+$", a)]
            steps.append(Step(n, "Bash", "git", " ".join(seg)[:90], None, terms))
            for sp in showpath:
                steps.append(Step(n, "Bash", "read", sp))
            continue
        if head.startswith("python"):
            code = " ".join(seg)
            files = [m.group(0) for m in FILE_RE.finditer(code)]
            steps.append(Step(n, "Bash", "python", " ".join(seg)[:90]))
            for f in files:
                if not f.startswith(("self.", "os.", "re.", "json.")):
                    steps.append(Step(n, "Bash", "read", f))
            continue
        steps.append(Step(n, "Bash", "other", " ".join(seg)[:90]))
    return steps


def _repo_from_steps(pr: Probe) -> str | None:
    for s in pr.steps:
        if s.kind == "cd" and os.path.isdir(os.path.expanduser(s.target)):
            return os.path.expanduser(s.target)
    return None


# ----------------------------------------------------------------------------- analysis


def _snip(text: str, i: int, width: int = 160) -> str:
    a = max(0, i - width // 3)
    return re.sub(r"\s+", " ", text[a:a + width]).strip()


def sentences(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z⛔⚠️⭐✅⬜*`(])", line):
            s = s.strip()
            if s:
                out.append(s)
    return out


QUOTED_RE = re.compile(r"\*?\"[^\"]{2,}\"\*?|“[^”]{2,}”|\*[^*\s][^*]{1,}[^*\s]\*(?!\*)")


def grep_sentences(text: str, patterns: list[str], flags=re.I, strip_quotes: bool = False,
                   follow_colon: bool = False) -> list[str]:
    """Sentences matching any pattern. ``strip_quotes`` ignores text inside quotes and *italics*
    (a quoted user saying "I suspect" is not the probe hedging). ``follow_colon`` appends the bullet
    lines that follow a matching line ending in ':' — a hedge often names its scope as a list."""
    hits = []
    lines = text.splitlines()
    for li, line in enumerate(lines):
        for s in sentences(line):
            probe_s = QUOTED_RE.sub(" ", s) if strip_quotes else s
            if any(re.search(p, probe_s, flags) for p in patterns):
                if follow_colon and s.rstrip().endswith(":"):
                    tail = []
                    for nxt in lines[li + 1:]:
                        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", nxt):
                            tail.append(nxt.strip())
                        else:
                            break
                    s = s + (" " + " ".join(tail) if tail else "")
                hits.append(s)
    return hits


def split_informed(report: str) -> tuple[str, list[str]]:
    m = re.search(r"^.*WHAT INFORMED YOU.*$", report, re.M | re.I)
    if not m:
        return "", []
    sect = report[m.end():]
    items, cur = [], ""
    for line in sect.splitlines():
        if re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", line):
            if cur.strip():
                items.append(cur.strip())
            cur = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", line)
        elif line.strip():
            cur += " " + line.strip()
        elif cur.strip():
            items.append(cur.strip())
            cur = ""
    if cur.strip():
        items.append(cur.strip())
    return sect.strip(), items


def summary_block(report: str) -> str:
    """The report's own summary block, if it has one: from a TL;DR / Summary line to the next rule
    line (a run of dashes or box-drawing characters) or heading; else ''."""
    lines = report.splitlines()
    for i, line in enumerate(lines):
        if re.search(r"TL;DR|^\s*(?:\*\*)?(?:Summary|In short|Bottom line)\b", line):
            out = [line]
            for nxt in lines[i + 1:]:
                if re.match(r"^[`\s]*[─—-]{5,}[`\s]*$", nxt) or re.match(r"^#{1,6}\s", nxt):
                    break
                out.append(nxt)
            return "\n".join(out)
    return ""


def recommendation(report: str) -> str:
    m = re.search(r"RECOMMENDATION\W*\s*(.+)", report, re.I)
    if not m:
        return "—"
    line = m.group(1).strip().strip("*").strip()
    m2 = re.match(r"(do not proceed|don't proceed|proceed with changes|proceed)", line, re.I)
    return m2.group(1).lower() if m2 else line[:60]


def index_blocks(instructions: list[dict]) -> list[tuple[str, int, str]]:
    """Split each delivered file into blocks: a table row, a bullet with its continuation
    lines, a heading, or a paragraph."""
    blocks = []
    for f in instructions:
        name = f["path"]
        cur, start = [], 0
        for i, line in enumerate(f["content"].splitlines(), 1):
            starts_new = (not line.strip() or line.lstrip().startswith(("|", "#"))
                          or re.match(r"^\s{0,1}(?:[-*]|\d+\.)\s", line))
            if starts_new and cur:
                blocks.append((name, start, "\n".join(cur)))
                cur = []
            if line.strip():
                if not cur:
                    start = i
                cur.append(line)
        if cur:
            blocks.append((name, start, "\n".join(cur)))
    return blocks


CLOSURE_RE = re.compile(r"⛔|\brefuted\b|\brejected\b|\bclosed\b|\bdead\b|\bretired\b|"
                        r"\bdo not (?:ship|build|rebuild)\b", re.I)


def closed_rows(instructions: list[dict], header_re: str | None) -> list[str]:
    """Titles of the always-loaded index's CLOSED rows: table rows carrying a closure marker. With
    ``header_re`` (config ``closed_table_header``) only rows of a table whose header line matches it
    count — e.g. the "already tried" table — so a caveat column elsewhere cannot pose as a closure."""
    titles = []
    for f in instructions:
        in_table, eligible = False, header_re is None
        for line in f["content"].splitlines():
            if not line.lstrip().startswith("|"):
                in_table, eligible = False, header_re is None
                continue
            if not in_table:
                in_table = True
                if header_re is not None:
                    eligible = bool(re.search(header_re, line, re.I))
                continue  # the header row itself
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not eligible or len(cells) < 2 or re.fullmatch(r":?-{2,}:?", cells[0] or "--"):
                continue
            if CLOSURE_RE.search(" ".join(cells[1:])):
                m = re.search(r"\*\*(.+?)\*\*", cells[0])
                titles.append((m.group(1) if m else cells[0]).strip())
    return titles


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[`*_\"“”'’]", "", t)).strip().lower()


def cited_closed(body: str, titles: list[str]) -> list[str]:
    """Closed-row titles the report names (first 28 normalised characters of the title)."""
    nb = _norm(body)
    return [t for t in titles if len(_norm(t)) >= 12 and _norm(t)[:28] in nb]


def first_move_match(pr: Probe) -> dict:
    """Which always-loaded block do the FIRST tool call's terms and paths point at?"""
    first = [s for s in pr.steps if s.n == 1 and s.kind != "cd"]
    if not first or not pr.instructions:
        return {}
    regs: list[tuple[str, re.Pattern]] = []
    for s in first:
        for t in s.terms:
            try:
                regs.append((t, re.compile(t, re.I)))
            except re.error:
                regs.append((t, re.compile(re.escape(t), re.I)))
        if s.kind in ("search", "read") and s.target not in (".", "?"):
            rel = re.sub(r"^(?:\./)+", "", s.target)
            base = os.path.basename(rel)
            if len(base) >= 4 and "." in base:
                regs.append((base, re.compile(re.escape(base), re.I)))
    if not regs:
        return {}
    blocks = [b for b in index_blocks(pr.instructions) if not b[0].endswith("/.claude/CLAUDE.md")
              or len(pr.instructions) == 1]
    df = {t: sum(1 for b in blocks if r.search(b[2])) for t, r in regs}
    found = [t for t in df if df[t] > 0]
    best, best_score, best_terms = None, 0.0, []
    for b in blocks:
        terms = [t for t, r in regs if df[t] and r.search(b[2])]
        score = sum(1.0 / df[t] for t in terms)
        if score > best_score:
            best, best_score, best_terms = b, score, terms
    return {"terms": [t for t, _ in regs], "found": found, "df": df, "block": best,
            "score": best_score, "block_terms": best_terms}


def md_headings(path: str, rng: tuple[int, int], repo: str, commit: str) -> list[str]:
    if not path.endswith(".md") or not repo:
        return []
    rel = path
    if os.path.isabs(path):
        try:
            rel = os.path.relpath(path, repo)
        except ValueError:
            return []
    text = None
    if commit and not rel.startswith(".."):
        try:
            text = subprocess.run(["git", "-C", repo, "show", f"{commit}:{rel}"],
                                  capture_output=True, text=True, timeout=10).stdout or None
        except (OSError, subprocess.SubprocessError):
            text = None
    if text is None:
        p = Path(repo) / rel
        if not p.exists():
            return []
        text = p.read_text(errors="replace")
    lines = text.splitlines()
    a, b = rng
    heads, enclosing = [], None
    for i, line in enumerate(lines, 1):
        if re.match(r"^#{1,6}\s", line):
            if i < a:
                enclosing = line
            elif i <= b:
                heads.append(line)
    if heads:  # keep the most major level present in the range, so a long read names its sections
        top = min(len(h) - len(h.lstrip("#")) for h in heads)
        heads = [h for h in heads if len(h) - len(h.lstrip("#")) == top]
    out = ([enclosing] if enclosing else []) + heads
    return [re.sub(r"^#+\s*|\*\*|`", "", h).strip()[:70] for h in out]


def match_commit(content: str, path: str, repo: str) -> str:
    if not repo or not path.startswith(repo.rstrip("/") + "/"):
        p = Path(path)
        if p.exists():
            same = p.read_text(errors="replace").rstrip("\n") == content.rstrip("\n")
            return "= current file" if same else "≠ current file (edited since the snapshot)"
        return "file gone"
    rel = os.path.relpath(path, repo)
    try:
        log = subprocess.run(["git", "-C", repo, "log", "--format=%h", "-40", "--", rel],
                             capture_output=True, text=True, timeout=20).stdout.split()
    except (OSError, subprocess.SubprocessError):
        log = []
    want = content.rstrip("\n")
    wt = Path(path)
    for h in log:
        blob = subprocess.run(["git", "-C", repo, "show", f"{h}:{rel}"], capture_output=True,
                              text=True).stdout
        if blob.rstrip("\n") == want:
            tag = f"= commit {h}"
            if wt.exists() and wt.read_text(errors="replace").rstrip("\n") != want:
                tag += " (working tree has moved on)"
            return tag
    if wt.exists() and wt.read_text(errors="replace").rstrip("\n") == want:
        return "= working tree (uncommitted)"
    return "matches no recent commit"


def load_predictions(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    preds: dict[str, dict] = {}
    header: list[str] | None = None
    for line in path.read_text().splitlines():
        if not line.lstrip().startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        m = re.match(r"\**`?([A-Za-z]+\d+[a-z]?)\b", cells[0])
        if not m:
            continue
        row = dict(zip(header, cells))
        preds.setdefault(m.group(1), row)
    return preds


def pick(row: dict, *keys: str) -> str:
    for k in row:
        if any(key in k for key in keys):
            return row[k]
    return ""


# ----------------------------------------------------------------------------- report


def short(path: str, repo: str) -> str:
    if repo and os.path.isabs(path) and path.startswith(repo.rstrip("/") + "/"):
        path = os.path.relpath(path, repo)
    return path


def trail(pr: Probe, repo: str) -> list[str]:
    """Files in order of first touch; a file only ever SEARCHED (never read) is marked (grep)."""
    order, read = [], set()
    for s in pr.steps:
        if s.kind in ("read", "search") and s.target not in (".", "?"):
            key = short(s.target, repo)
            if key not in order:
                order.append(key)
            if s.kind == "read":
                read.add(key)
    return [(os.path.basename(k.rstrip("/")) or k) + ("" if k in read else "(grep)")
            for k in order]


def block_title(text: str) -> str:
    m = re.search(r"\*\*(.+?)\*\*", text)
    t = m.group(1) if m else re.sub(r"^[\s|#*-]+", "", text)
    t = re.sub(r"[`*]", "", t).strip()
    return t[:48] + ("…" if len(t) > 48 else "")


def md_escape_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def analyse(pr: Probe, cfg: dict, repo: str) -> dict:
    body = pr.report
    informed_text, informed = split_informed(body)
    body_no_informed = body[: body.find(informed_text)] if informed_text else body
    boiler = grep_sentences(body, cfg.get("boilerplate", [])) if cfg.get("boilerplate") else []
    argued = grep_sentences(body_no_informed, ARGUED_PAST_PATTERNS + cfg.get("argued_past_extra",
                                                                           []))
    idx_text = "\n".join(f["content"] for f in pr.instructions).lower()
    idx_blocks = [b[2].lower() for b in index_blocks(pr.instructions)]
    argued_marked = []
    for s in argued:
        echo = False
        for p in ARGUED_PAST_PATTERNS + cfg.get("argued_past_extra", []):
            m = re.search(p, s, re.I)
            if not m:
                continue
            phrase = m.group(0).lower()
            core = {w for w in re.findall(r"[a-z]{3,}", QUOTED_RE.sub(" ", phrase).replace(
                "(", " ").replace(")", " ")) if w not in STOP}
            core = {w for w in core if w not in re.findall(r"[a-z]{3,}", " ".join(
                re.findall(r"\([^)]*\)", phrase)))}
            if phrase in idx_text or (len(core) >= 2 and any(all(w in b for w in core)
                                                   for b in idx_blocks)):
                echo = True
        argued_marked.append((s, echo))
    hedges = grep_sentences(body, HEDGE_PATTERNS + cfg.get("hedge_extra", []),
                            strip_quotes=True, follow_colon=True)
    summary = grep_sentences(body, SUMMARY_PATTERNS, re.I | re.M)
    sblock = summary_block(body)
    body_only_hedges = [h for h in hedges if sblock and h.split(" - ")[0][:60] not in sblock]
    fm = first_move_match(pr)
    closed = cited_closed(body, closed_rows(pr.instructions, cfg.get("closed_table_header")))
    rec = recommendation(body)
    past_closed = closed if rec.startswith("proceed") else []
    first_decl = informed[0] if informed else ""
    decl_index = bool(first_decl) and any(re.search(p, first_decl, re.I)
                                          for p in ALWAYS_LOADED_HINTS)
    return {"informed": informed, "informed_text": informed_text, "boiler": boiler,
            "argued": argued_marked, "hedges": hedges, "summary": summary, "fm": fm,
            "body_only_hedges": body_only_hedges,
            "first_decl": first_decl, "decl_index": decl_index, "rec": rec,
            "cited_closed": closed, "past_closed": past_closed,
            "trail": trail(pr, repo)}


def first_cite_cell(a: dict) -> str:
    fm = a["fm"]
    strong = fm and fm.get("score", 0) >= 0.25
    title = f" «{block_title(fm['block'][2])}»" if strong and fm.get("block") else ""
    prefix = ""
    if a["decl_index"] and strong:
        prefix = f"index{title} [declared + first-move terms]"
    elif a["decl_index"]:
        prefix = "index [declared only]"
    elif strong:
        prefix = f"index?{title} [first-move terms only]"
    t = a["trail"][:4]
    parts = ([prefix] if prefix else []) + t
    cell = " → ".join(parts) if parts else "—"
    if len(a["trail"]) > 4:
        cell += f" … (+{len(a['trail']) - 4})"
    return cell


def render(probes: list[Probe], analyses: dict, preds: dict, cfg: dict, repo: str,
           expect: list[str], sealed: list[str], cmdline: str,
           expect_absent: list[str] | None = None) -> str:
    expect_absent = expect_absent or []
    L: list[str] = []
    L.append("# Results skeleton — generated by `probe_extract.py`, to be SCORED BY A HUMAN\n")
    L.append(f"Command: `{cmdline}`\n")
    L.append("⛔ Score from each probe's BODY and tool trail below, never from a summary line. "
             "Every flag is a candidate for reading, not a verdict. ⬜ columns are the scorer's.\n")

    # ------------------------------------------------ harness
    L.append("## Harness — measured from the transcripts\n")
    snaps = {}
    for pr in probes:
        key = tuple((f["path"], hashlib.sha256(f["content"].encode()).hexdigest()[:12])
                    for f in pr.instructions)
        snaps.setdefault(key, []).append(pr.label)
    if len(snaps) == 1 and probes and probes[0].instructions:
        L.append(f"✅ All {len(probes)} probes received the SAME always-loaded instruction set:\n")
    elif len(snaps) > 1:
        L.append("⛔ Probes received DIFFERENT instruction sets — do not pool them:\n")
    for key, labels in snaps.items():
        L.append(f"- received by {', '.join(labels)}:")
        pr0 = next(p for p in probes if p.label == labels[0])
        for f in pr0.instructions:
            sha = hashlib.sha256(f["content"].encode()).hexdigest()[:12]
            L.append(f"  - `{f['path']}` ({f['type']}, {len(f['content'].encode())} B, "
                     f"sha256 {sha}) {match_commit(f['content'], f['path'], repo)}")
    if expect:
        L.append("\nExpected strings in the delivered instructions (the freshness check):\n")
        for e in expect:
            have = [p.label for p in probes if any(e in f["content"] for f in p.instructions)]
            miss = [p.label for p in probes if p.label not in have]
            mark = "✅" if not miss else ("⛔" if not have else "⚠️")
            L.append(f"- {mark} `{e}` — present in {len(have)}/{len(probes)}"
                     + (f"; ABSENT in {', '.join(miss)}" if miss else ""))
    if expect_absent:
        L.append("\nStrings ASSUMED ABSENT from the delivered instructions (a probe aimed at them is "
                 "a reachability probe; if one is present, score that probe on its pre-registered "
                 "in-index branch):\n")
        for e in expect_absent:
            have = [p.label for p in probes if any(e in f["content"] for f in p.instructions)]
            mark = "✅ absent" if not have else "⚠️ PRESENT"
            L.append(f"- {mark} `{e}`" + (f" — in {', '.join(have)}" if have else ""))
    L.append("")
    L.append("| probe | task id | agent type | model | cwd | git HEAD at launch | "
             "1st-turn prompt tok | turns | tool calls |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for pr in probes:
        cwd = pr.cwd
        if any(cwd == s or cwd.startswith(s.rstrip('/') + '/') for s in sealed if s):
            cwd = f"⛔ {cwd}"
        ncalls = len({s.n for s in pr.steps})
        L.append(f"| {pr.label} | `{pr.task_id}` | {pr.meta.get('agentType', '?')} | "
                 f"{pr.model or '?'} | `{cwd}` | {pr.git_head or '?'} | "
                 f"{pr.first_turn_tokens if pr.first_turn_tokens is not None else '?'} | "
                 f"{pr.turns} | {ncalls} |")
    probs = [(pr.label, v) for pr in probes for v in pr.violations + pr.sealed_hits]
    if probs:
        L.append("\n⚠️ Violations and sealing hits:\n")
        for lab, v in probs:
            L.append(f"- {lab}: {v}")
    else:
        L.append("\n✅ No edits, no delegation, no sealed path touched.")
    L.append("")

    # ------------------------------------------------ table
    L.append("## Scorecard skeleton\n")
    L.append("| probe | predicted | rec (from body) | fired? | first cite (index hint → files in "
             "tool order) | boilerplate | argued-past candidates | hedges in body |")
    L.append("|---|---|---|---|---|---|---|---|")
    for pr in probes:
        a = analyses[pr.label]
        row = preds.get(pr.label, {})
        pred = pick(row, "expected", "predicted", "prediction")
        conf = pick(row, "conf")
        pred_cell = (pred + (f" ({conf})" if conf else "")) or "—"
        boiler = "none" if not a["boiler"] else f"⚠️ {len(a['boiler'])}: «{a['boiler'][0][:70]}»"
        if a["argued"]:
            s, echo = a["argued"][0]
            arg = (f"⚠️ {len(a['argued'])}: «{s[:70]}»" + (" (echoes index)" if echo else ""))
        else:
            arg = "none"
        if a["past_closed"]:
            arg += f" · ⚠️ proceeds while citing {len(a['past_closed'])} closed row(s)"
        hed = str(len(a["hedges"])) if a["hedges"] else "0"
        if a["body_only_hedges"]:
            hed += f" (⛔ {len(a['body_only_hedges'])} outside its own TL;DR)"
        L.append("| " + " | ".join(md_escape_cell(x) for x in [
            pr.label, pred_cell[:160], a["rec"], "⬜", first_cite_cell(a), boiler, arg, hed])
            + " |")
    L.append("")

    # ------------------------------------------------ per probe
    for pr in probes:
        a = analyses[pr.label]
        L.append(f"## {pr.label} — `{pr.task_id}` ({pr.meta.get('description', '')})\n")
        if pr.error:
            L.append(f"⛔ {pr.error}\n")
            continue
        L.append(f"Transcript: `{pr.path}`  \nReport source: {pr.report_source}\n")
        task = re.sub(r"\s+", " ", pr.prompt).strip()
        L.append(f"**Task (first 500 chars):** {task[:500]}{'…' if len(task) > 500 else ''}\n")
        fm = a["fm"]
        L.append("### Index-fire hint for the first move\n")
        if not fm:
            L.append("— no searchable terms or paths in the first tool call.\n")
        else:
            L.append(f"First-move terms/paths: {', '.join(f'`{t}`' for t in fm['terms'][:12])}  ")
            L.append(f"Found in the always-loaded files: "
                     f"{', '.join(f'`{t}` ({fm['df'][t]} blocks)' for t in fm['found'][:12]) or 'none'}  ")
            if fm.get("block"):
                name, line, text = fm["block"]
                L.append(f"Best-matching block (score {fm['score']:.2f}, terms "
                         f"{', '.join(fm['block_terms'])}): `{os.path.basename(name)}` line {line}")
                L.append("\n> " + re.sub(r"\s+", " ", text)[:300] + " …\n")
        L.append("### Tool trail (in order)\n")
        if not pr.steps:
            L.append("— no tool calls.\n")
        for s in pr.steps:
            if s.kind == "cd":
                continue
            extra = ""
            if s.lines:
                extra = f" L{s.lines[0]}–{s.lines[1]}"
                heads = md_headings(s.target if os.path.isabs(s.target) else
                                    os.path.join(pr.repo_root or repo, s.target),
                                    s.lines, repo, pr.git_head)
                if heads:
                    extra += " § " + " · ".join(heads[:4])
            terms = f" terms: {', '.join(f'`{t}`' for t in s.terms[:6])}" if s.terms else ""
            L.append(f"{s.n}. {s.kind} `{short(s.target, repo)}`{extra}{terms}")
        L.append("")
        L.append("### Declared trail — first item of WHAT INFORMED YOU\n")
        L.append(f"{a['first_decl'][:400] or '⛔ no WHAT INFORMED YOU section found'}\n")
        L.append("### Flags (candidates — read each)\n")
        L.append(f"- boilerplate: {len(a['boiler'])}")
        for s in a["boiler"]:
            L.append(f"  - «{s[:300]}»")
        L.append(f"- argued-past: {len(a['argued'])}")
        for s, echo in a["argued"]:
            L.append(f"  - «{s[:300]}»" + (" — echoes the index's own wording" if echo else ""))
        if a["past_closed"]:
            L.append("- ⚠️ PROCEEDS while naming closed row(s) — the structural argued-past tell; read "
                     "why each does not bind (an implicit argue-past has no phrase to grep):")
            for t in a["past_closed"]:
                L.append(f"  - «{t}»")
        elif a["cited_closed"]:
            L.append("- names closed row(s), and does not proceed: "
                     + " · ".join(f"«{t[:60]}»" for t in a["cited_closed"]))
        L.append(f"- hedges (a summary of this probe must keep these): {len(a['hedges'])}")
        for s in a["hedges"]:
            L.append(f"  - «{s[:300]}»")
        if a["summary"]:
            L.append(f"- ⚠️ the report carries its own summary line(s) — score from the body: "
                     + " / ".join(f"«{s[:120]}»" for s in a["summary"][:3]))
            if a["body_only_hedges"]:
                L.append(f"  - ⛔ {len(a['body_only_hedges'])} hedge(s) appear ONLY outside that "
                         "summary — a scorecard quoting the summary drops them:")
                for h in a["body_only_hedges"]:
                    L.append(f"    - «{h[:240]}»")
        L.append("")
        L.append("### The delivered report, verbatim\n")
        L.append("````text")
        L.append(pr.report.rstrip())
        L.append("````\n")
        if pr.post_text.strip():
            L.append("### Text written AFTER the hand-back — the caller never received it; "
                     "do not score from it\n")
            L.append("````text")
            L.append(pr.post_text.strip())
            L.append("````\n")
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("round_dir", type=Path)
    ap.add_argument("ids", nargs="*", help="LABEL=TASK_ID (or a transcript path)")
    ap.add_argument("--ids", dest="ids_file", type=Path)
    ap.add_argument("--predictions", type=Path)
    ap.add_argument("--repo", type=str)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--expect-absent", action="append", default=[])
    ap.add_argument("--sealed", action="append", default=[])
    ap.add_argument("--transcript-glob", action="append", default=[])
    ap.add_argument("--out", type=str)
    args = ap.parse_args(argv)

    cfg_path = args.config or Path(__file__).with_name("extract.json")
    cfg: dict = {}
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text())
        base = cfg_path.parent
        for k in ("repo",):
            if cfg.get(k):
                cfg[k] = str((base / os.path.expanduser(cfg[k])).resolve())
        cfg["sealed"] = [str((base / os.path.expanduser(s)).resolve())
                         for s in cfg.get("sealed", [])]
    round_cfg_path = args.round_dir / "round.json"
    round_cfg = json.loads(round_cfg_path.read_text()) if round_cfg_path.exists() else {}
    repo = os.path.expanduser(args.repo or cfg.get("repo", "") or "")
    expect = args.expect + round_cfg.get("expect", [])
    expect_absent = args.expect_absent + round_cfg.get("expect_absent", [])
    sealed = [os.path.abspath(os.path.expanduser(s))
              for s in args.sealed + cfg.get("sealed", []) + round_cfg.get("sealed", [])]

    pairs: list[tuple[str, str]] = []
    for item in args.ids:
        lab, _, tid = item.partition("=")
        pairs.append((lab, tid) if tid else (Path(lab).stem, lab))
    ids_file = args.ids_file or (args.round_dir / "ids.txt")
    if not pairs and ids_file.exists():
        for line in ids_file.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                lab, tid = line.split()[:2]
                pairs.append((lab, tid))
    if not pairs:
        ap.error("no task IDs: pass LABEL=ID arguments or write ROUND_DIR/ids.txt")

    globs = args.transcript_glob + DEFAULT_TRANSCRIPT_GLOBS
    probes = [load_probe(lab, tid, globs, sealed) for lab, tid in pairs]
    analyses = {pr.label: analyse(pr, cfg, repo) for pr in probes}
    preds = load_predictions(args.predictions or (args.round_dir / "predictions.md"))
    cmdline = "probe_extract.py " + " ".join(shlex.quote(a) for a in (argv or sys.argv[1:]))
    text = render(probes, analyses, preds, cfg, repo, expect, sealed, cmdline, expect_absent)
    out = args.out or str(args.round_dir / "results-skeleton.md")
    if out == "-":
        sys.stdout.write(text)
    else:
        Path(out).write_text(text)
        print(f"wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
