# Probes — designing, running and scoring interaction tests

## What a probe is

**One realistic task request, given to one fresh agent, in its own context.**

⛔ **Never give one agent several probes.** After the first *"that was already tried"* it is
primed, and every later answer is contaminated. One probe, one agent, always.

## The five design rules

1. **Blind.** Never mention the docs, the index, or that this is a test. The probe is a task. An
   agent told to check the index will check the index; that measures nothing.
2. **Different vocabulary.** Phrase the proposal in words that are **not** in the entry you are
   testing. Matching your own wording proves only that string matching works. This is the single
   most important rule — it is what distinguishes a class-level entry from an instance-level one.
3. **Realistic framing.** *"Here's my idea, should I implement it?"* — first person, with a
   plausible motivation. Not a quiz, not a lookup request.
4. **Read-only and cheap.** Forbid edits and long-running commands explicitly, or a probe will run
   your test suite, your pipeline, or your billing.
5. **Instrument the answer.** Require a `WHAT INFORMED YOU` section naming files and sections
   relied on, or "general reasoning only". **This is the measurement.** Without it you learn the
   agent's opinion; with it you learn whether your structure fired.

## Controls are mandatory, in both directions

⛔ An index that flags **everything** as already-tried is exactly as broken as one that flags
nothing — and it fails *invisibly*, by suppressing legitimate work instead of permitting duplicated
work. Nothing in a mechanical guard can detect this.

| probe kind | proposes | expected |
|---|---|---|
| **should-fire** | something genuinely closed, phrased differently | fires |
| **should-not-fire** | genuinely open, novel, or adjacent-but-different work | does **not** fire |
| **reachability** | something answerable only from a docstring or non-indexed file | reaches it |

A run with no should-not-fire control is not an interaction test. It is a demo.

### ⛔ Validate the control BEFORE the run, or you test your own ignorance

A should-not-fire control is only a control if the work it proposes is **genuinely open**. Picking
one is harder than it looks, and getting it wrong silently costs you the only measurement that
detects over-firing.

*Real instance, twice in two rounds:* both controls came back "already ruled out" and both times
**the agent was right and the prediction was wrong** — once because the action the idea fed had
been closed, once because the capability already existed in four scripts. Useful findings, but
after two rounds **over-firing was still untested**, because no valid negative had been run.

✅ **Cheap fix — spend two minutes before the round:** grep for the mechanism, the symbol, and the
obvious synonyms, and check the plan file says the work is open. If anything comes back, the
control is invalid; pick another.

### Weak negatives pass for free — aim at the boundary

⚠️ Verifying openness is necessary and not sufficient. A control so unrelated that nothing could
plausibly fire — *"add a GraphQL API"* to an image pipeline — passes trivially and measures
nothing. Over-firing happens at the **edges of a class**, so that is where a negative has to sit.

**A strong negative is both:**
- **genuinely open** — verified by grep and by the plan's own status, and
- **adjacent to a closed class**, differing from it by *mechanism* rather than by subject.

⭐ **The cleanest form is a paired probe on ONE row:** one proposal inside the class and one
outside it, same subject, different mechanism. If the row fires on the first and stays silent on
the second, the boundary is where you drew it — which is a far stronger result than either probe
alone, and it isolates precision from recall in a single round.

⚠️ **A control that fires is not automatically over-firing.** Check what the agent actually said:
*"this was tried and rejected"* is a precision failure only if the thing is genuinely open;
*"this already exists, use it"* means your control was invalid, not that the index is broken.

⭐ **When a control contradicts your prediction, suspect yourself first.** If a control comes back
"already ruled out", either the index over-fires **or your belief about what's open is wrong**.
Both are findings; the second is usually the more valuable one, and no other method detects it.

## Write predictions first

Before any probe runs, record for each: the expected outcome **and your confidence**.

```
probe  proposal                          phrased as       predicted     confidence
P1     rank blocks by MEDIAN area        size statistic   fires         high
P3     curvature variance, medial axis   not in entry     fires         ~65%
C1     use source shading for direction  genuinely open   does NOT fire ~55%
```

A miss then localises **one** wrong belief instead of being rationalised after the fact. The
confidence column matters: a confident miss is a different problem from an uncertain one.

## Reading `WHAT INFORMED YOU`

This is the diagnostic. Map the answer to a mode:

| the probe cited | means | action |
|---|---|---|
| the index entry itself | fired with no pull — best case | none |
| the findings file | the pull happened and worked | none |
| a **different** file as authority | **staleness** — your index contradicts it | correct in place |
| a source docstring you never indexed | **unreachable** — knowledge outside the map | index the location |
| "general reasoning only" | the structure was never reached | fix location, not wording |
| the doc, and it is still wrong | **partial instruction** | state the scope boundary |

## Scoring a run

Count four things, and report them separately:

```
should-fire probes caught          → recall
should-not-fire controls held      → precision
predictions correct                → your model of the docs
defects surfaced incidentally      → the real yield
```

⭐ **The fourth number is usually the largest.** Probes find contradictions between files as a side
effect of answering an unrelated question — two probes asking about different topics converging on
the same stale section is a strong signal, and it is how the method pays for itself.

## How many probes

Six is enough for a first pass on one topic cluster and will find real defects. It is **not**
coverage. Scale by topic, not by confidence: one should-fire probe per index entry class you
actually care about, plus at least one control, plus one reachability probe.

⚠️ Probes written by the person who wrote the index are the method's weakest point — you cannot
fully un-know your own wording. Mitigate by drafting probes from the *symptom* ("the grey lines get
buried") rather than from the entry, and by having a second person or a fresh agent write some.

## After the run

1. Fix what was found — **in place**, per `drift-protection.md`.
2. Add anything the probes taught you to the relevant index, with its scope boundary.
3. **Re-probe the fixed entries** with new wording. A fix verified by the probe that found it is
   not verified.
