# The six failure modes

Every mode here was found by a probe on a real repo, not derived from theory. Each entry gives the
**tell** (how it shows up in a probe result), why other methods miss it, the **fix**, and the
**prevention**.

| mode | tell | read-through finds it? | guard test finds it? |
|---|---|---|---|
| Drift | two files state one fact differently | only if you read both at once | ✅ if numbers are guarded |
| Staleness | probe cites a *different* file as authority | ⛔ each file reads fine alone | ⛔ |
| Partial instruction | probe obeys the doc and is still wrong | ⛔ the text is **true** | ⛔ |
| Over-firing | a control declines legitimate work | ⛔ nothing looks wrong | ⛔ |
| Unreachable | probe finds it somewhere nothing indexes | ⛔ | ⛔ |
| Confidence drift | source hedges, doc asserts | ⛔ the doc is well written | ⛔ |

⭐ **Five of six are invisible to both a read-through and a unit test.** That is the argument for
the method in one line.

---

## 1. Drift

**One derived fact written down twice, each copy maintained separately.** Both look authoritative;
nothing executes a paragraph, so neither is ever checked against the other.

*Real instance:* a variant documented with a config value in three files that the code had **never**
contained — invented in a doc commit and copied twice.

**Fix:** make the answer exist once. **Prevention:** the index restates no measurement; numbers
that live in code are referenced by symbol, never by value; a guard test asserts it.

## 2. Staleness

**A document contradicts the authority that superseded it.** Each file is internally consistent, so
nothing looks broken until an agent cites the other one at you.

*Real instance:* the loaded index still framed a workstream as "the gate is missing, build it" while
the plan file had **closed** it — judged, rejected, re-judged with the defect repaired, still
rejected. The plan file even flagged the contradiction in its own text, where nobody read it.

**Fix:** correct in place, and point at the authority. **Prevention:** declare one authority per
fact kind (`organize.md`); when you close something, the closing session updates the index in the
same commit.

⭐ **Tell to watch for: two probes on unrelated topics both citing the same third file.** That is
staleness announcing itself.

⛔ **The dangerous sub-case: the stale document is BETTER ARGUED than the thing that superseded
it.** Reasoning accumulates in a repo — a position gets defended, measured, cross-referenced, and
earns its place. The decision that overturns it arrives as one line in a meeting note, because
that is how decisions actually arrive. An agent weighing the two on merit picks the stale one
**every time**, and it is right to, given only the two texts.

*Real instance:* a repo ranked auto-detection last and mock-only, justified by *"the estimators
already produce structured markup — the machine-readable data exists without any vision model."*
A client meeting six days later made auto-detection the centre of the feature. Probed, the agent
recommended **correcting the specification** to remove what the client had just asked for.

**Fix:** declare the authority explicitly, at the point of use — *"when `DECISIONS.md` contradicts
the reasoning here, `DECISIONS.md` wins; the reasoning was sound when written and has been
overtaken."* **Prevention:** authority is a property you assign per *kind of fact*, never one an
agent infers from how well a passage argues. Quality of argument is the exact signal that fails
here.

⛔ **Corrections are a prime source of this mode, not a cure for it** — a fix that names a
*forward* direction ("the live route is X") is a fresh claim with a short shelf life. See
`drift-protection.md` § *Corrections decay too*.

## 3. Partial instruction

**Advice that is true and incomplete, and reads as complete.** The agent obeys it, believes the
problem is handled, and stops looking.

*Real instance:* *"any A/B on this variant must pin the brief cache."* True. But one variant makes a
**second** model call with its own separate cache, so an agent that pins the first believes
nondeterminism is handled while the run still moves between arms.

**⛔ This is the nastiest mode, because a missing instruction leaves you searching and a partial one
ends the search with false confidence.**

**Fix:** state what the instruction does *not* cover. **Prevention:** every procedural entry carries
an explicit scope boundary — *"this does not cover X"* — as a required field, not a nicety.

⭐ **The cheapest variant to catch: a documented COMMAND that does not run.** One audited repo's
most-read section told you to run two tools that were not installed, and had for months — the
instruction is true as *intent* and fails at the prompt. **Every command your docs tell someone to
run should be executed by a guard**, or at minimum have its binary checked for existence. This is
the one partial-instruction case a machine can find, so there is no excuse for finding it by hand.

## 4. Over-firing

**The index suppresses legitimate work.** An entry scoped by *topic* instead of by *mechanism*
catches everything nearby, and an agent declines work that was never closed.

**⛔ It fails invisibly.** Duplicated work is at least visible when you notice the rebuild;
suppressed work looks like an agent being appropriately careful.

**Fix:** scope the class by **mechanism**, not subject area. *"Any rule that reorders colour
blocks"* is a mechanism; *"colour block stuff"* is a topic and will over-fire.
**Prevention:** should-not-fire controls in every run. Nothing else detects this.

⚠️ Distinguish genuine over-firing from a correct refusal you did not expect — check whether the
probe's *action* was closed even if its *signal* was novel. That distinction is often the finding.

## 5. Unreachable

**Knowledge sitting where no index points.** Usually source docstrings, sometimes a research
directory, sometimes memory. The material is often excellent; it is simply invisible to anyone
maintaining `docs/`.

*Real instance:* probes drew env-override semantics, a substring-matching gotcha and a
"there are at least two causes" hedge from five different module docstrings. None was indexed.

**Fix:** index the *location*, not just the document — see the source-of-truth map in
`organize.md`. **Prevention:** run a reachability probe each pass.

## 6. Confidence drift

**The doc asserts what its own source hedges.** No number is wrong. The certainty is.

*Real instance:* a tool's docstring recorded *"there are at least TWO causes and this file
originally claimed one"* and, of one design, *"not yet traced end to end, so do not assume it."*
The findings file stated the mechanism flatly, with a causal *"which is why"* — and had been read
line-by-line that same day, by the person who wrote it, without anyone noticing.

**⛔ Uniquely resistant to review, because the prose is good.** A hedge is the easiest thing to lose
when text is summarised, moved, or tightened — and summarising, moving and tightening is exactly
what documentation maintenance is.

**Fix:** restore the hedge, and carry the *reason* for it. **Prevention:** when moving a claim
between files, diff it against its source, not against the previous copy.

---

## Diagnosing from a result

```
probe fired, cited the entry            ✅ working
probe fired, cited findings file        ✅ working, pull succeeded
probe did not fire on closed work       → entry too narrow. Lead with the CLASS
control fired on open work              → OVER-FIRING. Re-scope by mechanism
cited a different file as authority     → STALENESS. Correct in place
cited a docstring you never indexed     → UNREACHABLE. Extend the map
"general reasoning only"                → never reached. Location problem
obeyed the doc and was still wrong      → PARTIAL INSTRUCTION. Add scope boundary
doc more certain than its source        → CONFIDENCE DRIFT. Restore the hedge
```
