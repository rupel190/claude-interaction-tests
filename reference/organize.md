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

## Move 3 — Write the maintenance rule at the point of use

Put it *in* the index, immediately above the entries — not in a separate contributing guide. The
session that needs it is the session adding an entry, and it will be looking at the table.

See `drift-protection.md` for the rule text and the reasoning behind each clause.
