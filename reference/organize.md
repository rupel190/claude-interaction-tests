# Organize — the structure being tested

## Move 1 — MAP the knowledge locations first

⛔ **Do not start by editing `CLAUDE.md`.** Start by finding out where the project's operational
truth actually lives. It is rarely all in `docs/`.

⭐⭐ **The finding that motivates this move: in a real repo, most operational truth lived in SOURCE
DOCSTRINGS.** Probes reached for `run_gates.py`, `thread_survival.py`, `ab_elicit.py`,
`report_common.py`, `conftest.py` — that is where the env-override semantics, the substring-match
gotcha and the "there are at least two causes" hedge were written. Excellent material, discoverable
only by an agent that thinks to grep for it, and invisible to anyone maintaining `docs/`.

**A documentation index that indexes only documentation is indexing the minority of what the
project knows.**

### The source-of-truth map

Put this in the index. One row per *kind* of fact, naming the single authority for it.

| kind of fact | authority | never |
|---|---|---|
| tunable values, thresholds, defaults | the code symbol | restated in prose |
| what a gate does / its semantics | the gate module's docstring | inferred from its name |
| whether a lever is closed | the ALREADY TRIED index | re-derived per session |
| measurement setup traps | the tool's own docstring + BEFORE YOU MEASURE | assumed |
| plan status of a workstream | the plan file's row | summarised elsewhere |
| a judged verdict | the findings file for that topic | quoted with numbers in the index |

⚠️ Two properties make a row worth writing: it names **one** authority, and it names what the fact
must **never** be. The second half is what stops the copy that drifts.

### Verify the map with a reachability probe

Not all probes test recall. One should test **location**: give an agent a task whose answer lives
only in a docstring, and see whether it gets there.

* Reaches it → the location is discoverable; index it so it stays so.
* Answers "general reasoning only" → **unreachable**. Fix the *location*, not the wording: point
  the index at the file, or lift the fact into a doc.

## Move 2 — Index over findings

The always-loaded file becomes an **index**; derivations move to per-topic findings files.

```
CLAUDE.md            loaded every turn      entries, verdicts, pointers, rules
docs/FINDINGS/*.md   pulled on demand       measurements, tables, verbatim notes, history
```

This is **not** RAG. The index is in the system prompt, so its presence is guaranteed. The only
unreliable step is the pull — which is why law 1 exists.

### Two indexes, not one

They catch different failures and must not be merged.

**⛔ ALREADY TRIED** — *don't rebuild this.* Closed levers, refuted approaches, retired tools,
rejected rules. Prevents duplicated work.

**⚠️ BEFORE YOU MEASURE** — *don't invalidate your result.* Caches to pin, env vars to set,
controls that must exist, definitions that must be stated. These do not break anything: they
produce a **confident wrong number**, which is worse, because nothing downstream flags it.

⚠️ Every entry in the second index must state its **scope boundary** — what it does *not* cover.
This is the only prevention for *partial instruction*: "pin cache A" invites the belief that
nondeterminism is handled. "Pin cache A; note this does **not** cover call B, which needs cache C"
does not.

### Anatomy of an entry

```
| already tried — do not rebuild        | how it closed          | pull            |
| **CLASS description** — instance,     | ⛔ verdict, stated so  | `path/to/       |
| instance, instance. Triggers: symbol, | it stops a rebuild     |  findings.md`   |
| env var, step name, symptom words     | with no pull needed    |                 |
```

Four parts, all load-bearing:

1. **The class** — what fires on a differently-worded proposal.
2. **The instances** — trigger terms; the specific things tried.
3. **The verdict** — inline, because the pull may not happen.
4. **The pointer** — where the evidence lives, restating none of it.

### A third kind of row: the DECLINED proposal

Not everything worth recording was tried. Some things were **proposed, considered with evidence,
and deliberately not done** — and they will be proposed again, because the reasoning that suggested
them was sound.

⛔ **Do not file these as refuted.** "We tried it and it failed" and "we considered it and chose
not to" are different facts, and blurring them makes the index untrustworthy in both directions.
Mark them distinctly (`⚠️ considered <date> and DECLINED`) and require two extra things:

1. ⭐ **The evidence that informed the decision** — otherwise the next session cannot tell a
   judgement from a whim, and will reasonably re-open it.
2. ⭐ **The condition that would REOPEN it.** A decision with no reopen condition reads as
   permanent when it was contingent. *"Reopen if a probe ever fails on this file"* converts a
   standing "no" into a testable one.

### ⛔ Dated reports do not expire — record decisions AGAINST them

An audit, a research pass or a consultant's report is a **point-in-time snapshot**. It keeps
recommending whatever it recommended, forever, and it gets re-read. If you decline one of its
recommendations, the report will not learn.

*Real instance:* an audit recommended restructuring a large plan file. The recommendation was
sound, and was declined on evidence the audit did not have — interaction probes showing the file
worked as-is. Without a record, the next session reads the audit, sees a sensible unimplemented
recommendation, and re-litigates a decision already made with better information.

✅ **The decision goes in the live index, not in the report.** Never edit a dated report to reflect
a later decision — that destroys its value as a snapshot. Instead the index row names the report
and says *"this recommendation was read and declined, not missed."*

### What stays loaded, what moves

| stays in the index | moves to a findings file |
|---|---|
| that something was tried and how it closed | by how much, on what corpus, in which run |
| active gates, defaults, and how to opt out | the A/B that chose the default |
| standing architecture a session needs | the derivation of that architecture |
| the judge's raw preferences, if short | the session notes behind them |
| procedural traps + their scope boundaries | the incident that taught each one |

⚠️ **Do not over-cut.** If the binding constraint is attention rather than capacity — and with a
large context window it usually is — then over-cutting is the failure mode. An entry compressed
past the point where it fires costs you exactly the rebuild you were preventing. Keep recall
generous; cut evidence hard.

## ⛔ Extraction ORPHANS locations — check before and after

**When you move a section out of the always-loaded file, every *location* it mentioned leaves with
it.** The index gains one pointer (to the new findings file) and silently loses every pointer that
section carried. Nothing warns you, and the result is the **unreachable** mode created *by* the
restructure meant to prevent it.

*Real instance:* a restructure moved one section to a findings file. The always-loaded file went
from four mentions of a `rulebook/` directory — the project's craft-rule authority, containing the
reason a whole class of output was mis-tagged — to **zero**. An audit found it; nobody reading the
diff had.

✅ **The check is mechanical and takes seconds.** Before and after the extraction, diff the set of
paths and directory names the index mentions:

```bash
grep -oE '`[a-zA-Z0-9_./-]+/[a-zA-Z0-9_./-]*`' INDEX.md | sort -u > /tmp/before.txt
# ...extract...
grep -oE '`[a-zA-Z0-9_./-]+/[a-zA-Z0-9_./-]*`' INDEX.md | sort -u > /tmp/after.txt
comm -23 /tmp/before.txt /tmp/after.txt      # locations you just made unreachable
```

Anything that dropped out must be re-added to the index — usually to the source-of-truth map — or
deliberately re-homed. ⚠️ **Do this per extraction, not once at the end**: after several moves you
can no longer tell which section owned which reference.

### Archiving is an extraction — same orphan risk, plus two rules of its own

Moving a doc to `archive/` is the same operation as moving a section to a findings file, so run the
same location diff. Two extra rules:

1. ⛔ **The archive must stay reachable from the index**, with a README saying *why each item is
   there*. An archive nothing points at is the unreachable mode by construction — you have not
   removed the material, you have hidden it.
2. ⛔ **The archive README must state precedence in its first line**: if an archived doc disagrees
   with a live one, **the live one wins**. Otherwise a future agent finds an archived answer, has
   no way to know it is stale, and cites it with confidence.

⚠️ Check for live→archive links after the move. A live doc pointing into the archive is the wrong
way round: either the target should not have been archived, or the pointer should be updated to say
"archived — kept as provenance".

## Durability — the bottom tier of the evidence base

An index points at findings; findings cite **artefacts** — run directories, output bundles,
generated reports. That bottom tier is where the strategy usually rots, because it is large,
untracked, and nobody is watching it.

⛔ **A measurement whose artefact is gone is unfalsifiable.** It reads as evidence and cannot be
checked, re-derived, or refuted. In one audited repo, several run directories cited *by name* in
the docs no longer existed — the verdicts resting on them had quietly become assertions.

✅ **The fix that works is small, tracked and self-describing.** Not the 18 GB of raw output — a
per-session JSON holding the inputs, the arms, and the raw answers, committed alongside the docs.
It is a fraction of a percent of the size and it is the only tier that survives a disk.

**Checklist:**
- [ ] Every artefact a findings file cites is either **tracked**, or has a tracked summary
- [ ] Raw judgements (A/B answers, rankings, labels) are committed as data, not just prose
- [ ] The index's source-of-truth map **names that durable location** — otherwise it is unreachable
- [ ] Periodically: extract every artefact name the docs cite and check it still exists

## Move 3 — Write the maintenance rule at the point of use

Put it *in* the index, immediately above the entries — not in a separate contributing guide. The
session that needs it is the session adding an entry, and it will be looking at the table.

See `drift-protection.md` for the rule text and the reasoning behind each clause.
