# Drift protection — rules and guards

Documentation decays in one specific way: **a session closes something while doing something else,
and writes it down for itself instead of for the next reader.** Everything here defends against
that.

## The maintenance rule

Put this **in the index**, immediately above the entries. Not in a contributing guide — the session
that needs it is the one adding an entry, and it will be looking at the table.

> **THE RULE for adding an entry — follow it or the index decays**
>
> You will almost always close a lever **while doing something else**, and your instinct will be to
> write the entry in the vocabulary of *your* task. Write it for the next session instead.
>
> 1. ⭐ **Phrase it as the CLASS, not your instance.** List your variant as one instance. A session
>    proposing a differently-worded variant must still match. **An entry naming only your variant
>    will not fire.**
> 2. ⭐ **Carry the verdict in the entry itself.** Assume the reader never opens the file — the pull
>    is the one unreliable step in this design.
> 3. ⛔ **No measurements.** Numbers live in the findings file, or in code by symbol, exactly once.
> 4. ⭐ **Spell out the trigger terms** — env vars, symbols, step names, and *symptom words* an
>    agent would arrive carrying. This is what makes the pull happen at all.
> 5. ⚠️ **State the scope boundary** for anything procedural — what this does *not* cover.
> 6. ✅ **Append a new result; do not overwrite a verdict you merely disagree with.**
> 7. ⭐⭐ **But when you PROVE something wrong, CORRECT IT IN PLACE.** Do not leave the wrong
>    statement standing with a correction beside it. Fix the claim; keep **one short line** saying
>    what changed; put the story in the findings file. ⚠️ Rule 6 governs **new** results, rule 7
>    governs **falsified** ones — the licence to rewrite comes from disproof, never disagreement.
> 8. ✅ **Every findings file must be reachable from an entry** — guarded by a test.

### Why rule 7 matters more than it looks

Appending a correction rather than fixing the claim is **the growth mechanism**. Both versions stay
loaded forever and the reader adjudicates. One observed repo shipped a table with three wrong cells
for months *directly beneath a note saying it was wrong* — the error and its refutation coexisting
because there was nowhere to put the correction except beside the error.

⚠️ The usual objection is history loss. **Version control preserves it.** `git log -p` recovers any
claim a correction overwrites, so correcting in place costs nothing that matters.

## Declare one authority per fact kind

Drift needs two copies. The cheapest prevention is to make the second copy illegitimate by name —
see the source-of-truth map in `organize.md`. A row that says *"thresholds live in the code symbol,
**never** restated in prose"* converts a future drift into a rule violation someone can point at.

## The mechanical guard

A unit test cannot check whether an entry *fires*, but it can pin the structural properties so they
do not decay between interaction-test runs. Copy `assets/test_docs_index.py` and adjust. It checks:

- every entry carries a verdict → works when unpulled
- no entry restates a measurement → outside inline-code spans
- every findings file is reachable → nothing is invisible
- no pointer targets a missing file
- the maintenance rule itself still exists → the discipline cannot be silently deleted

⛔ **Mutation-test it.** Inject each violation, confirm the *right* assertion fails, restore. Then
**re-run the mutations after any change to the guard's own parser** — a scoping change is exactly
where a guard quietly stops biting, and it will still report all-green while checking nothing.

```
M1  add an entry containing a measurement      → expect: measurement test fails
M2  add an entry with no verdict marker        → expect: verdict test fails
M3  delete one clause of the maintenance rule  → expect: rule test fails
M4  create an unreferenced findings file       → expect: reachability test fails
M5  point an entry at a nonexistent file       → expect: pointer test fails
```

Each mutation should fail **exactly one** assertion. If a mutation fails none, the guard is
decorative. If it fails several, your assertions overlap and a real failure will be hard to read.

## What the guard cannot do

⚠️ It cannot tell you whether an entry is phrased generically enough to fire, whether it over-fires,
whether it is stale against another file, or whether it overstates its source. **Those are the four
modes that actually bite, and only probes find them.** The guard exists so those probe runs stay
rare; it does not replace them.

## Cadence

- **Guard test:** every commit, via CI.
- **Interaction tests:** after any restructure, after any session that closes several levers, and
  on a slow periodic beat otherwise. A run is cheap — a handful of parallel read-only agents.
- **Reachability probe:** every run, cheapest insurance against the mode nothing else sees.
