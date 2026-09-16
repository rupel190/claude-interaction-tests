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
1 MAP        where does each KIND of fact live —      → reference/organize.md
             INCLUDING the kinds decided outside the repo
2 ORGANIZE   index (loaded) over findings (pulled)   → reference/organize.md
3 PROTECT    rules + guards so it cannot decay       → reference/drift-protection.md
             the eight guard patterns a machine CAN check, and where each RUNS → reference/guards.md
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
[ ] MEASURE WHICH CHANNELS THE HARNESS REACHES, before running anything — and ⛔ do not write
    that table from assumption. Two runs have now got the same row wrong from assumption, in
    OPPOSITE directions (once permissive, once restrictive). One throwaway probe asking the agent
    to report what it was handed settles it in a minute. Unstated or wrong, a miss is
    misattributed to the docs after the fact, and a real miss is excused as untestable
[ ] ⚠️ Record that table PER TIER, never per location. A location is not one channel: an INDEX
    file there may be loaded into every probe while the detail files it points at are only
    pulled. For such a location "reachable" and "unreachable" are both wrong answers — it is the
    same index-over-findings split this method prescribes, now applying to the harness itself
[ ] Run probes: one per fresh agent, blind, read-only, vocabulary NOT in the entry
[ ] Include should-NOT-fire controls — always
[ ] If knowledge governs this repo from OUTSIDE it (vault, tickets, meetings):
    copy assets/decisions_scaffold.md, name the watched folders and a sync date,
    put the authority line in the INDEX (not in the file it governs), then probe
    it — cross-boundary probe plus a positive control read FIRST, or a miss is
    unattributable. Rule: reference/organize.md § authorities OUTSIDE the repo
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
  ⭐ **But this depends on how the probe is FRAMED, and you can buy some of it back for free.** A
  probe phrased *"is this allowed?"* only reads prose. A probe phrased **"build this / plan this"**
  forces the agent to open the artefacts the prose depends on — so it finds vanished evidence,
  contaminated numbers and mis-stated corpora as a side effect of trying to do the work. **Prefer
  build-it framings for should-fire probes**; they cost nothing extra and they audit while they
  recall.
  ✅ **Measured once, and the split was total.** In a seven-probe run, **all five** build-it /
  plan-it framings surfaced documentation defects incidentally — a planning doc's claim falsified
  by one environment default, a predicate carrying **three** disagreeing definitions across the
  tree, a refuted figure standing as fact in a live docstring, one session's result recorded three
  different ways in one file, and a documented precondition that did not exist. The **one**
  write-it-up framing recalled perfectly and surfaced **none**. ⚠️ One run, so the direction is
  established and the rate is not.
  ⭐ **But the two framings yield different KINDS, and only build-it is about the artefacts.** The
  write-up probe produced the run's cleanest piece of *invented* reasoning — it took a documented
  rule one step further than the documentation had — while the build-it probes produced defects in
  things on disk. See *Knowledge the probe invents*, below.
- **Config and data surfaces.** An unregistered flag, or a shared dict key whose meaning differs
  between producers, makes two runs look comparable when they are not — and no amount of
  documentation testing sees it.

⭐ The division is clean: **probes find what does not fire; an audit finds what does not exist.**

⛔ **And when you run that audit, require it to list what is WORKING.** An audit that reports only
problems reads as a mandate to change everything it names, and its next reader will "fix" decisions
that were deliberate and already paid for. A section of *"these are load-bearing, do not touch"* is
what makes the rest of it safe to act on — and it is the same instinct as the declined-proposal row
in `reference/organize.md`: **recording a settled decision is as valuable as recording a defect.**

## If you caught a miss, send it back

⭐ **The best data for this skill is produced by agents who are not running it.** Every ordinary
session in which an agent proposes something the docs forbid, restates a documented fact wrongly,
or re-derives a finding that is already written down is this method's phenomenon occurring in the
wild — and it carries something a designed probe cannot: the agent knows **what it read and what
it did not**. A probe tells you a row did not fire. A live miss tells you why.

So when it happens to you, in any project, record it. The shape that makes it usable:

```
what I did wrong          — the claim, or the action taken
what the docs already say — file and line, quoted
what I read instead       — and why that seemed sufficient at the time
```

⛔ **The file-and-line is not optional.** An agent grading its own recall has an obvious incentive
problem, and a document that can be quoted back against the claim is the only thing that makes the
report checkable. Without it this collects impressions.

⚠️ **It is not a probe result and must never be counted as one.** Probe discipline — blind, one per
agent, predictions written first, controls both ways — is what makes those trustworthy, and none of
it applies here. Treat a reported miss as a **lead for where to point the next probe**, not as a
measurement.

## Knowledge the probe INVENTS — capture it, or it dies with the run

⭐ **A probe is scored as a recall test, and it is also a fresh reader of the material.** A fresh
reader occasionally sees further than the author, and nothing in a scorecard has a column for that,
so it survives only if someone notices. Observed three times in one run, across **both** framings.

**What it actually looks like, and the shape is narrower than "insight":** the probe takes a rule
the docs already state and **extends it one step to a case the docs never applied it to.** One
recalled a documented noise floor correctly, then argued that a *second* correlated case agreeing
made the result **less** credible rather than more — because both were named in the noise record, so
agreement is what the noise looks like. The docs contain every premise and not the conclusion.
Another turned *"instrument the function, do not re-implement it"* into *"this predicate has three
implementations in the tree, so compute all three and print the disagreement as a control column"*.

⭐ **That narrowness is what makes it trustworthy and tells you where to file it.** It is not an
outside idea needing its own evidence; it is the scope of an existing entry, discovered by someone
applying it. So it belongs back in **that entry**, as a widened scope or an added consequence —
not as a new row, and not in a session summary nobody reads.

⚠️ **Do not confuse it with a probe being right about the codebase.** The test is whether the
claim is *absent from the docs and derivable from them*. A probe that merely reports what a file
says has recalled, not invented.

## Non-negotiables

- ⛔ **Controls in both directions, every run.** An index that flags *everything* as already-tried
  is exactly as broken as one that flags nothing — and it fails invisibly, by suppressing
  legitimate work rather than permitting duplicated work.
  ⚠️ **Score HOW a control passed, not just that it did. A control that proceeds only after
  reading past the entry — into the findings file, the source, another doc — is a LATENT
  over-fire, not a pass.** The entry alone said "closed"; a less thorough agent stops there and
  silently drops legitimate work. Fix the entry, not the probe: state the distinction the escaping
  agent had to go and find.
  ⭐⭐ **And score EVERY probe for it, not only the controls — a latent over-fire shows up just as
  readily on a should-fire probe, where nobody is looking for it.** The tell is textual and costs
  nothing to grep: **the agent writes a paragraph explaining why a closed entry does not apply to
  it.** That paragraph is an over-fire that a thorough agent absorbed. Observed twice in one run,
  both times on should-fire probes, both times on an entry *adjacent* to the one under test — so
  neither was anywhere a control had been sited, and no control could have been sited everywhere.
  ✅ **The prescribed fix is now verified, not merely prescribed.** An entry that had blocked a
  probe in an earlier run gained one clause naming the licensed exception; re-probed with fresh
  wording, the new agent proceeded and **quoted that clause from the index** without opening
  anything else. One entry, before and after — the strongest single confirmation this method has.
- ⛔ **Write predictions before results.** A miss then localises one wrong belief. Expect some
  misses to be **yours** — a control that contradicts your prediction because the docs are stale is
  the most valuable result this method produces, and nothing else detects it.
- ⛔ **Mutation-test the guard**, and again after any change to it. A guard that has quietly stopped
  biting is worse than no guard, and a scoping change is where that happens.
- ⛔ **One probe per agent.** After the first *"already tried"* an agent is primed; a second probe
  in the same context measures nothing.
- ⚠️ **Never mention the docs, the index, or the test in a probe.** The probe is a task.
