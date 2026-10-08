#!/usr/bin/env python3
"""round_prep — prepare an interaction-test round from git history. Two subcommands.

``routes``  — what the always-loaded index GAINED since a date, as probe stubs.
    Reads the index's diff since ``--since`` (or ``--days``), groups the added lines into ROUTES
    (one diff hunk each, dated by blame), pulls the KEYS out of each route (backticked gate and
    symbol names, sitting ids, plan-row ids, file paths, ``§`` references), and for every key runs
    two sweeps a runner otherwise does by hand:

    * **stale copies** — every other line in the tree that names the key AND carries a status word
      (unjudged, staged, off by default, unbuilt …), minus the retraction forms
      (``(said "…" until <date>)``). These are the candidates to pre-register: a status written
      where the thing is DEFINED (a gate's docstring, a stager's label) is not corrected by the
      commit that corrected the index.
    * **live state** — the part of a route the index never carries: lines of the newest handoff
      commit naming the key, and commits on branches NOT merged into ``--base`` that name it or
      add/remove it (``-S``). A route's VERDICT travels into the index; what is in progress, owed
      or broken since does not, and a probe's answer is only complete with both halves.

    It prints a markdown skeleton with a probe stub per route. ⛔ It never writes the TASK: draft
    that from the symptom, in words absent from the route's lines (``reference/probes.md`` rule 2).

``regress`` — which banked probes to re-run, because their targets changed since a commit.
    Parses a probe bank (``## <ID> — …`` sections), collects each probe's authorities (file
    paths, and ``file.md § N`` section references) and keys, and compares them with
    ``git diff <since>..HEAD``: a section-level authority counts as changed only when a hunk
    touches that section's lines, so a findings file edited daily does not re-run everything.
    An index line naming one of the probe's keys that changed counts too.

What it does NOT establish
--------------------------
* Both sweeps are LEXICAL. A status claim that names no key, a stale copy that paraphrases, and
  live state recorded under another name are invisible. Read every candidate before registering
  it; a candidate is a line to read, never a finding.
* ``routes`` sees what the index ADDED. A route the index carried before and whose meaning
  changed elsewhere (a verdict that landed only in a findings file) is the status sweep's job.
* ``regress`` reads a whole-file authority at file level, except a markdown file the probe cites
  by ROW id (``O24``), which counts as changed only when a hunk touches that row. A code file
  edited daily therefore re-runs its probes daily: name the symbol, not the file, where you can.
* ``regress`` is a floor, not a selection. A probe whose own target did not move can still
  regress through a NEIGHBOURING entry (an over-fire is born on the adjacent row), and the
  harness itself moves (the loaded index is a process-start snapshot). Always re-run the controls
  and at least one untouched probe, which this tool lists as ``always``.
* The index the probes LOAD is the snapshot from the parent process start, not HEAD. Diff the two
  before trusting either sweep (``probe_extract.py`` matches the delivered content to a commit).

Usage
-----
    round_prep.py routes  --repo PATH (--since YYYY-MM-DD | --days N) [--index CLAUDE.md]
                          [--base main] [--exclude PATHSPEC ...] [--handoff-grep REGEX]
                          [--max-hits N] [--near N] [--verdicts PATHSPEC] [--out FILE]
    round_prep.py regress --repo PATH --bank probes.md --since-commit SHA [--index CLAUDE.md]
                          [--out FILE]

Standard library only; Python 3.10+.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

#: Words that make a line a STATUS claim. Case-insensitive; matched on the hit line only.
STATUS_RE = re.compile(
    r"\b(?:un-?judged|not (?:yet )?judged|awaiting(?: (?:his|the|a))? (?:verdict|yes|answer)|"
    # "staged" only as a STATE ("`x` staged,", "(staged", "is staged"), never the verb of a history
    # line ("Staged by …", "arms as staged", "staged in `tips1`")
    r"(?<!as )staged(?=\s*(?:[,;)—–]|$|, unjudged|, awaiting))|\(staged\b|\bis staged\b|"
    r"unbuilt|not (?:yet )?built|untried|not (?:yet )?tried|unmeasured|"
    r"(?:off|on) by default|default (?:off|on)|gated off|ships (?:gated )?off|"
    r"held until|on hold|open, unbuilt)\b|⬜",
    re.I)
#: Retraction / history forms — a hit line carrying one is not a current claim.
HISTORY_RE = re.compile(r"\(said\s+[\"“].*?[\"”]\s+until\b|\buntil 20\d\d-\d\d-\d\d|"
                        r"[\"”'*]\s*until\b|\buntil (?:its|his|the) (?:verdict|yes)\b|"
                        r"\bwas (?:the )?default\b", re.I)
#: File types whose statements WRAP across lines with the key on one line and the status further
#: down (a gate's description string, a docstring sentence). Markdown is excluded: a table row is
#: one line, and a paragraph mixes subjects, so a look-ahead there attributes a status to the
#: wrong key.
NEAR_SUFFIXES = (".py", ".pyi", ".ts", ".js", ".rs", ".go", ".java", ".rb", ".sh")
#: Paths never swept for stale copies (history by location). Extend with --exclude.
DEFAULT_EXCLUDES = ["docs/archive", "docs/verdicts", "docs/AUDIT", "tests/output"]

BACKTICK_RE = re.compile(r"`([^`\n]{2,80})`")
SECTION_RE = re.compile(r"§\s*([0-9]+(?:\.[0-9]+)*)")
FILE_RE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:md|py|json|yaml|yml|toml))\b")
GATE_RE = re.compile(r"^[A-Z][A-Z0-9_]{3,}$")
SITTING_RE = re.compile(r"^[a-z][a-z_]*[0-9]+[a-z]?$")
ROW_RE = re.compile(r"^[A-Z]{1,2}[0-9]{1,3}(?:\.[0-9]+)?$")
SYMBOL_RE = re.compile(r"^[A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)+$")
STOP = {"TODO", "NOTE", "HEAD", "MAIN", "README"}


def git(repo: str, *args: str, check: bool = False) -> str:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


# ──────────────────────────────────────────────────────────────── keys

@dataclass
class Keys:
    gates: list[str] = field(default_factory=list)
    sittings: list[str] = field(default_factory=list)
    rows: list[str] = field(default_factory=list)
    symbols: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)

    def sweepable(self) -> list[str]:
        """Keys specific enough to grep the tree for (not files, not bare section numbers)."""
        return _uniq(self.gates + self.sittings + self.rows + self.symbols)


def _uniq(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out


def extract_keys(text: str) -> Keys:
    k = Keys()
    for span in BACKTICK_RE.findall(text):
        tok = span.strip().split("=")[0].strip().rstrip("()")
        tok = tok.split("[")[0]
        if not tok or tok in STOP:
            continue
        if FILE_RE.fullmatch(tok):
            k.files.append(tok)
        elif GATE_RE.match(tok):
            k.gates.append(tok)
        elif ROW_RE.match(tok):
            k.rows.append(tok)
        elif SITTING_RE.match(tok):
            k.sittings.append(tok)
        elif SYMBOL_RE.match(tok) and len(tok) >= 6:
            k.symbols.append(tok)
    k.files += FILE_RE.findall(text)
    k.sections += SECTION_RE.findall(text)
    for name in ("gates", "sittings", "rows", "symbols", "files", "sections"):
        setattr(k, name, _uniq(getattr(k, name)))
    return k


# ──────────────────────────────────────────────────────────────── routes

@dataclass
class Route:
    start: int                      # first added line, in the index at HEAD
    added: list[str]
    removed: list[str]
    commits: list[tuple[str, str, str]] = field(default_factory=list)   # (sha, date, subject)
    keys: Keys = field(default_factory=Keys)


def index_routes(repo: str, index: str, since: str) -> tuple[str, list[Route]]:
    shas = git(repo, "log", f"--since={since}", "--format=%H", "--reverse", "--", index).split()
    if not shas:
        return "", []
    parent = git(repo, "rev-parse", "--verify", "-q", f"{shas[0]}^").strip()
    base = parent or git(repo, "hash-object", "-t", "tree", "/dev/null").strip()
    diff = git(repo, "diff", "-U0", base, "HEAD", "--", index)
    routes: list[Route] = []
    cur: Route | None = None
    for line in diff.splitlines():
        m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if m:
            cur = Route(int(m.group(1)), [], [])
            routes.append(cur)
        elif cur is not None and line.startswith("+") and not line.startswith("+++"):
            cur.added.append(line[1:])
        elif cur is not None and line.startswith("-") and not line.startswith("---"):
            cur.removed.append(line[1:])
    routes = [r for r in routes if r.added]
    for r in routes:
        blame = git(repo, "blame", "--line-porcelain", "-L",
                    f"{r.start},{r.start + len(r.added) - 1}", "HEAD", "--", index)
        seen = {}
        sha = None
        for bl in blame.splitlines():
            m = re.match(r"^([0-9a-f]{40}) \d+ \d+", bl)
            if m:
                sha = m.group(1)
                seen.setdefault(sha, ["", ""])
            elif sha and bl.startswith("author-time "):
                seen[sha][0] = date.fromtimestamp(int(bl.split()[1])).isoformat()
            elif sha and bl.startswith("summary "):
                seen[sha][1] = bl[len("summary "):]
        r.commits = sorted(((s[:7], d, subj) for s, (d, subj) in seen.items()),
                           key=lambda c: c[1])
        # Keys from the ADDED text only — but a changed line's old copy tells you what it said.
        new_text = "\n".join(r.added)
        old_keys = extract_keys("\n".join(r.removed)).sweepable()
        r.keys = extract_keys(new_text)
        # A key present before and after this change is not what the route GAINED; keep it,
        # but list gained keys first.
        gained = [x for x in r.keys.sweepable() if x not in old_keys]
        kept = [x for x in r.keys.sweepable() if x in old_keys]
        r.keys.gates = [x for x in gained + kept if x in r.keys.gates]
    return base[:7], routes


#: The status words a VERDICT expires (a judgement lands); default/build words expire otherwise.
UNJUDGED_RE = re.compile(r"\b(?:un-?judged|not (?:yet )?judged|staged|awaiting)\b|\(staged", re.I)
_FILE_CACHE: dict[tuple[str, str], list[str]] = {}


def _lines_at_head(repo: str, path: str) -> list[str]:
    key = (repo, path)
    if key not in _FILE_CACHE:
        _FILE_CACHE[key] = git(repo, "show", f"HEAD:{path}").splitlines()
    return _FILE_CACHE[key]


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def judged_in(repo: str, key: str, verdict_glob: str) -> list[str]:
    """Verdict files whose text sets ``KEY=`` — the LEVER hop of pattern 9: a status claim keyed by
    a gate is decided by the sitting that judged an arm setting that gate."""
    if not verdict_glob:
        return []
    out = git(repo, "grep", "-l", "-E", "-e", rf"\b{re.escape(key)}=", "HEAD", "--", verdict_glob)
    return [ln.split(":", 1)[1] for ln in out.splitlines() if ":" in ln]


def stale_copies(repo: str, key: str, index: str, excludes: list[str], cap: int, near: int,
                 verdict_glob: str) -> list[str]:
    """Lines naming ``key`` that carry a current STATUS claim — on the line itself, or (``near``)
    further down the same indented statement or paragraph, which is where a long gate docstring
    or a wrapped sentence puts it."""
    spec = ["--", "."] + [f":(exclude){e}" for e in excludes]
    out = git(repo, "grep", "-n", "-I", "-F", "-e", key, "HEAD", *spec)
    verdicts = judged_in(repo, key, verdict_glob)
    hits, seen = [], set()
    for line in out.splitlines():
        parts = line.split(":", 3)          # HEAD:path:line:text
        if len(parts) < 4:
            continue
        _, path, ln, text = parts
        n = int(ln)
        found = None
        if STATUS_RE.search(text) and not HISTORY_RE.search(text):
            found = (n, text, 0)
        elif near and path.endswith(NEAR_SUFFIXES):
            lines = _lines_at_head(repo, path)
            base = _indent(lines[n - 1]) if 0 < n <= len(lines) else 0
            for j in range(n, min(n + near, len(lines))):
                nxt = lines[j]
                if not nxt.strip() or _indent(nxt) < base or (key not in nxt and _names_other(nxt)):
                    break
                if STATUS_RE.search(nxt):
                    if not HISTORY_RE.search(nxt) and "(said" not in lines[j - 1]:
                        found = (j + 1, nxt, j + 1 - n)
                    break
        if not found or (path, found[0]) in seen:
            continue
        seen.add((path, found[0]))
        where = "INDEX" if path == index else path
        tag = f" (+{found[2]} lines below the key)" if found[2] else ""
        flag = ""
        if verdicts and UNJUDGED_RE.search(found[1]):
            flag = " ⛔ judged in " + ", ".join(v.rsplit("/", 1)[-1] for v in verdicts[:3])
        hits.append(f"{where}:{found[0]}{tag}{flag}: {found[1].strip()[:150]}")
    hits.sort(key=lambda h: "⛔" not in h)
    if len(hits) > cap:
        hits = hits[:cap] + [f"… {len(hits) - cap} more"]
    return hits


#: A line that opens another registry entry ends the statement the key opened (e.g. the next
#: ``Gate("…"`` row); generic: a line whose first token is a quoted ALL-CAPS name.
_OTHER_ENTRY_RE = re.compile(r"^\s*(?:\w+\()?[\"'][A-Z][A-Z0-9_]{3,}[\"']")


def _names_other(line: str) -> bool:
    return bool(_OTHER_ENTRY_RE.match(line))


def live_state(repo: str, key: str, base: str, handoff_re: str, since: str) -> list[str]:
    out = []
    sha = git(repo, "log", "--all", "-1", "-i", "-E", f"--grep={handoff_re}", "--format=%h").strip()
    if sha:
        body = git(repo, "show", "-s", "--format=%B", sha)
        for bl in body.splitlines():
            if key in bl:
                out.append(f"handoff {sha}: {bl.strip()[:170]}")
    branches = git(repo, "branch", "--no-merged", base, "--format=%(refname:short)").split()
    for b in branches:
        msgs = git(repo, "log", f"{base}..{b}", f"--since={since}", "-F", f"--grep={key}",
                   "--format=%h %ad %s", "--date=short").splitlines()
        picks = git(repo, "log", f"{base}..{b}", f"--since={since}", f"-S{key}",
                    "--format=%h %ad %s", "--date=short").splitlines()
        for c in _uniq(msgs + picks)[:4]:
            out.append(f"branch {b} (not merged into {base}): {c[:150]}")
    return out


def cmd_routes(a: argparse.Namespace) -> int:
    since = a.since or (date.today() - timedelta(days=a.days)).isoformat()
    base_sha, routes = index_routes(a.repo, a.index, since)
    lines = [f"# Routes the index gained since {since}",
             "",
             f"Repo `{a.repo}` · index `{a.index}` · diff `{base_sha or '∅'}..HEAD` "
             f"({git(a.repo, 'rev-parse', '--short', 'HEAD').strip()}) · branches compared "
             f"against `{a.base}`.",
             "",
             "⚠️ Every hit below is a LINE TO READ, not a finding. The sweeps are lexical "
             "(module docstring, *What it does NOT establish*).",
             ""]
    if not routes:
        lines.append("No added lines in the index since that date.")
    excludes = DEFAULT_EXCLUDES + list(a.exclude)
    for i, r in enumerate(routes, 1):
        when = ", ".join(f"`{s}` {d} — {subj[:70]}" for s, d, subj in r.commits) or "?"
        lines += [f"## R{i} — index line {r.start} · {when}", "", "```"]
        shown = r.added[:8]
        lines += [ln[:200] for ln in shown]
        if len(r.added) > 8:
            lines.append(f"… {len(r.added) - 8} more added lines")
        lines += ["```", ""]
        if r.removed:
            lines += [f"Replaced {len(r.removed)} line(s); the old text is the pre-route state "
                      "(diff it for what the route CHANGED, not only what it added).", ""]
        k = r.keys
        lines.append(
            "Keys — gates: " + (", ".join(f"`{x}`" for x in k.gates) or "—")
            + " · sittings: " + (", ".join(f"`{x}`" for x in k.sittings) or "—")
            + " · rows: " + (", ".join(f"`{x}`" for x in k.rows) or "—")
            + " · symbols: " + (", ".join(f"`{x}`" for x in k.symbols) or "—"))
        lines.append("Authorities named — files: " + (", ".join(f"`{x}`" for x in k.files) or "—")
                     + " · sections: " + (", ".join(f"§ {x}" for x in k.sections) or "—"))
        lines.append("")
        for key in k.sweepable():
            stale = stale_copies(a.repo, key, a.index, excludes, a.max_hits, a.near,
                                 a.verdicts)
            live = live_state(a.repo, key, a.base, a.handoff_grep, since)
            if not stale and not live:
                continue
            lines.append(f"**`{key}`**")
            for h in stale:
                lines.append(f"- status line: {h}")
            for h in live:
                lines.append(f"- live state: {h}")
            lines.append("")
        lines += [
            f"Probe stub for R{i}:",
            "",
            "```",
            f"## <ID> — <the SYMPTOM, in words absent from the lines above> · GAINED ({r.commits[-1][1] if r.commits else '?'})",
            "**Task:** <first person, a realistic request; build-it / plan-it framing>",
            "- **Known answer:** <from the AUTHORITY, read in full — never from this sheet>",
            "- **Authority:** the index lines above · <the sections named, as read>",
            "- **stale copies:** <the status lines above that are really stale, after reading each>",
            "- **live state:** <handoff / branch hits that change the right answer today>",
            "- **Expensive miss:** … **Safe miss:** …",
            "```",
            ""]
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text)
        print(f"wrote {a.out} ({len(routes)} routes)")
    else:
        sys.stdout.write(text)
    return 0


# ──────────────────────────────────────────────────────────────── regress

@dataclass
class BankProbe:
    pid: str
    title: str
    text: str
    files: list[str]
    sections: list[tuple[str, str]]       # (file, section number)
    keys: list[str]
    always: bool


def parse_bank(path: Path) -> list[BankProbe]:
    text = path.read_text()
    out = []
    parts = re.split(r"(?m)^(##\s+.+)$", text)
    for i in range(1, len(parts) - 1, 2):
        head, body = parts[i], parts[i + 1]
        body = re.split(r"(?m)^#\s", body)[0]
        m = re.match(r"^##\s+(\S+)\s+[—-]+\s*(.*)$", head)
        if not m:
            continue
        pid, title = m.group(1), m.group(2)
        k = extract_keys(body)
        secs = []
        for fm in re.finditer(r"`?((?:[\w.-]+/)*[\w.-]+\.md)`?\s*§\s*([0-9]+(?:\.[0-9]+)*)", body):
            secs.append((fm.group(1), fm.group(2)))
        always = bool(re.search(r"\bCONTROL\b|channel probe|\bharness\b", head, re.I))
        out.append(BankProbe(pid, title, body, k.files, _uniq(secs), k.sweepable(), always))
    return out


def resolve(repo: str, f: str, tracked: list[str]) -> list[str]:
    if f in tracked:
        return [f]
    return [t for t in tracked if t.endswith("/" + f)]


def section_range(repo: str, path: str, num: str) -> tuple[int, int] | None:
    text = git(repo, "show", f"HEAD:{path}")
    lines = text.splitlines()
    # the number must OPEN the heading (after markers, emoji and an optional §): a bare search
    # would match "31" inside a date in an earlier heading
    pat = re.compile(r"^(#{1,6})\s+(?:[^\w\s§]+\s*)*(?:§\s*)?" + re.escape(num) + r"(?![0-9]|\.[0-9])")
    for i, ln in enumerate(lines):
        mm = pat.match(ln)
        if mm:
            level = len(mm.group(1))
            end = len(lines)
            for j in range(i + 1, len(lines)):
                h = re.match(r"^(#{1,6})\s", lines[j])
                if h and len(h.group(1)) <= level:
                    end = j
                    break
            return i + 1, end
    # bold-numbered paragraphs ("**8.12.7 …**") are sections too in some findings files
    pat2 = re.compile(r"^\*\*" + re.escape(num) + r"(?![0-9]|\.[0-9])")
    for i, ln in enumerate(lines):
        if pat2.match(ln):
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if re.match(r"^(#{1,6}\s|\*\*[0-9]+(?:\.[0-9]+)+\b)", lines[j]):
                    end = j
                    break
            return i + 1, end
    return None


def changed_ranges(repo: str, since: str, path: str) -> list[tuple[int, int]]:
    diff = git(repo, "diff", "-U0", since, "HEAD", "--", path)
    out = []
    for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff, re.M):
        a = int(m.group(1))
        n = int(m.group(2)) if m.group(2) is not None else 1
        out.append((a, a + max(n, 1) - 1))
    return out


def cmd_regress(a: argparse.Namespace) -> int:
    probes = parse_bank(Path(a.bank))
    tracked = git(a.repo, "ls-files").splitlines()
    changed = set(git(a.repo, "diff", "--name-only", a.since_commit, "HEAD").splitlines())
    idx_diff = git(a.repo, "diff", "-U0", a.since_commit, "HEAD", "--", a.index)
    idx_lines = [ln[1:] for ln in idx_diff.splitlines()
                 if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    rows = []
    for p in probes:
        why = []
        for f, num in p.sections:
            for path in resolve(a.repo, f, tracked):
                if path not in changed:
                    continue
                rng = section_range(a.repo, path, num)
                if rng is None:
                    why.append(f"{path} changed (§ {num} not found at HEAD — moved or renamed?)")
                    continue
                if any(x <= rng[1] and y >= rng[0] for x, y in changed_ranges(a.repo,
                                                                              a.since_commit,
                                                                              path)):
                    why.append(f"{path} § {num} changed")
        sectioned = {s[0] for s in p.sections}
        row_keys = [k for k in p.keys if ROW_RE.match(k)]
        for f in p.files:
            if f in sectioned or any(f.endswith(s) or s.endswith(f) for s in sectioned):
                continue
            for path in resolve(a.repo, f, tracked):
                if path not in changed or path == a.index:
                    continue
                if path.endswith(".md") and row_keys:
                    # a plan file is cited by ROW: changed only if a hunk touches one of its rows
                    d = git(a.repo, "diff", "-U0", a.since_commit, "HEAD", "--", path)
                    touched = [r for r in row_keys if re.search(rf"^[+-].*\*\*{re.escape(r)}\*\*", d,
                                                             re.M)]
                    if touched:
                        why.append(f"{path} rows {', '.join(touched)} changed")
                    continue
                why.append(f"{path} changed")
        hit = [k for k in p.keys if any(k in ln for ln in idx_lines)]
        if hit:
            why.append("index lines naming " + ", ".join(f"`{k}`" for k in hit[:5]) + " changed")
        verdict = "RE-RUN" if why else ("always" if p.always else "skip")
        if p.always and why:
            verdict = "RE-RUN (always)"
        rows.append((p.pid, p.title[:60], verdict, "; ".join(_uniq(why))[:300] or "—"))
    lines = [f"# Regression selection since `{a.since_commit}`",
             "",
             f"Repo `{a.repo}` at `{git(a.repo, 'rev-parse', '--short', 'HEAD').strip()}`; bank "
             f"`{a.bank}`; {len(changed)} files changed.",
             "",
             "⚠️ A floor, not a selection: re-run every `always` row too, and remember that the "
             "index a probe LOADS is the process-start snapshot, not HEAD.",
             "",
             "| probe | title | verdict | why |",
             "|---|---|---|---|"]
    lines += [f"| {pid} | {t.replace('|', '/')} | {v} | {w.replace('|', '/')} |"
              for pid, t, v, w in rows]
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text)
        print(f"wrote {a.out} ({sum(1 for r in rows if r[2].startswith('RE-RUN'))} to re-run)")
    else:
        sys.stdout.write(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("routes", help="probe stubs for what the index gained since a date")
    r.add_argument("--repo", required=True)
    r.add_argument("--index", default="CLAUDE.md")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--since")
    g.add_argument("--days", type=int)
    r.add_argument("--base", default="main")
    r.add_argument("--exclude", action="append", default=[])
    r.add_argument("--handoff-grep", default="handoff")
    r.add_argument("--max-hits", type=int, default=10)
    r.add_argument("--near", type=int, default=30,
                   help="look this many lines down the same statement for a status word")
    r.add_argument("--verdicts", default="",
                   help="pathspec of verdict files; a gate set as KEY= in one is JUDGED")
    r.add_argument("--out")
    q = sub.add_parser("regress", help="banked probes whose targets changed since a commit")
    q.add_argument("--repo", required=True)
    q.add_argument("--bank", required=True)
    q.add_argument("--since-commit", required=True)
    q.add_argument("--index", default="CLAUDE.md")
    q.add_argument("--out")
    a = ap.parse_args(argv)
    return cmd_routes(a) if a.cmd == "routes" else cmd_regress(a)


if __name__ == "__main__":
    raise SystemExit(main())
