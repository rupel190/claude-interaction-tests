---
name: interaction-tests
description: Organize a project's agent-facing documentation (CLAUDE.md, docs/, rules, memory, docstrings) as a verdict-bearing INDEX over pulled findings files, then VERIFY it works by running blind interaction tests — probes measuring whether a fresh agent actually recalls what the docs know. Use when agent-facing docs grew past a screen, when an agent rebuilt or re-litigated something already decided, when CLAUDE.md is large or contradicts other docs, when documentation drift is suspected, or when asked to audit, restructure, shrink, or verify documentation an agent reads.
---

# Interaction Tests

**An interaction test does not test code. It tests how an agent interacts with the context
structure you gave it** — whether a fresh agent, mid-task, carrying its own vocabulary, recalls
the thing that stops it doing the wrong thing.

⛔ **A read-through cannot substitute.** A read-through is what produced the docs. Someone who
edited a file line-by-line the same day still misses that it overstates its own source; a probe
catches it in one shot.

This skill is itself built the way it tells you to build: this file is the index, `reference/`
holds the detail. **Pull the reference file when its subject is in play.**

## The five moves

```
1 MAP        where does each KIND of fact live?      → reference/organize.md
2 ORGANIZE   index (loaded) over findings (pulled)   → reference/organize.md
3 PROTECT    rules + guards so it cannot decay       → reference/drift-protection.md
             the six guard patterns a machine CAN check → reference/guards.md
4 TEST       blind probes with controls              → reference/probes.md
5 READ       diagnose by failure mode, then fix      → reference/taxonomy.md
```

`reference/planning-rows.md` covers making decisions **citable**, which is what lets a probe say
*"row C4 closed this"* and lets you find contradictions precisely.

## The three laws

Everything else follows from these.

**1. The index must be useful when the pull does NOT happen.**
Its presence is guaranteed — it is in the system prompt. The *pull* is the unreliable step. So
every entry carries its own verdict inline. An entry saying only *"see the file"* teaches nothing
to the agent that does not look.

**2. Entries are CLASSES, not instances.**
A session closes something *while doing something else*, so its instinct is to write the entry in
the vocabulary of its own task. That entry will never fire for anyone else.

```
✗  "ordering colour blocks by summed painted area — rejected"
✓  "any global rule ranking blocks by a SIZE STATISTIC — rejected.
    tried: summed area, per-path area, two-level blocked"
```
The instances stay, as trigger terms. The class is what fires on *median* area — or on a phrasing
nobody has used yet.

**3. Events in the index, measurements in the findings file.**

| kind | example | drifts? | recall value | home |
|---|---|---|---|---|
| **event** | "X was tried and rejected" | never — append-only | high | index |
| **measurement** | "13/19 designs worse" | yes | low | findings file |

⛔ A number written in two places is the dominant documentation bug: both copies look
authoritative and nothing executes a paragraph. A number that lives in **code** is referenced by
symbol, never by value.

## Quick start

```
[ ] MAP the knowledge locations — including source docstrings (reference/organize.md)
[ ] Build two indexes: ALREADY TRIED and BEFORE YOU MEASURE
[ ] Write the maintenance rule at the point of use
[ ] Copy assets/test_docs_index.py, adjust, MUTATION-TEST it
[ ] Write predictions + confidence, before running anything
[ ] Run probes: one per fresh agent, blind, read-only, vocabulary NOT in the entry
[ ] Include should-NOT-fire controls — always
[ ] Score by failure mode (reference/taxonomy.md), fix, re-probe
[ ] After each extraction: diff the LOCATIONS the index names, re-add what dropped
[ ] Check every artefact your findings cite still exists — unfalsifiable is not evidence
```

## The six failure modes

Full tells and fixes in `reference/taxonomy.md`. Named here so you recognise them in a result:

| mode | one-line tell |
|---|---|
| **Drift** | two files state the same fact differently |
| **Staleness** | a probe cites a *different* file as the authority |
| **Partial instruction** | a probe obeys the doc and is still wrong |
| **Over-firing** | a control declines legitimate work |
| **Unreachable** | a probe finds the fact somewhere nothing indexes |
| **Confidence drift** | the source hedges; the doc asserts |

⭐ **Partial instruction is the nastiest.** *"Pin the cache"* is **true**, and an agent that obeys
it believes nondeterminism is handled while a second uncached call still moves. **A missing
instruction leaves you searching; a partial one ends the search with false confidence.**

## What this method does NOT find

⚠️ Probes measure **recall of what is written**. They are weak at three things, and a conventional
static audit is strong at all three — run both, they are complementary rather than competing:

- **What was never written.** A probe cannot miss what it never had reason to ask about.
- **Decay in the evidence base.** Artefacts a findings file cites can vanish without any probe
  noticing, because the *prose* still reads fine.
- **Config and data surfaces.** An unregistered flag, or a shared dict key whose meaning differs
  between producers, makes two runs look comparable when they are not — and no amount of
  documentation testing sees it.

⭐ The division is clean: **probes find what does not fire; an audit finds what does not exist.**

## Non-negotiables

- ⛔ **Controls in both directions, every run.** An index that flags *everything* as already-tried
  is exactly as broken as one that flags nothing — and it fails invisibly, by suppressing
  legitimate work rather than permitting duplicated work.
- ⛔ **Write predictions before results.** A miss then localises one wrong belief. Expect some
  misses to be **yours** — a control that contradicts your prediction because the docs are stale is
  the most valuable result this method produces, and nothing else detects it.
- ⛔ **Mutation-test the guard**, and again after any change to it. A guard that has quietly stopped
  biting is worse than no guard, and a scoping change is where that happens.
- ⛔ **One probe per agent.** After the first *"already tried"* an agent is primed; a second probe
  in the same context measures nothing.
- ⚠️ **Never mention the docs, the index, or the test in a probe.** The probe is a task.
