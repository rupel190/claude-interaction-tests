# Probes — designing, running and scoring interaction tests

## What a probe is

**One realistic task request, given to one fresh agent, in its own context.**

⛔ **Never give one agent several probes.** After the first *"that was already tried"* it is
primed, and every later answer is contaminated. One probe, one agent, always.

### ⚠️ "One agent" is not what you get — a probe that DELEGATES multiplies the index

A capable agent given a research-shaped task spawns its own helpers, and **every one of them
inherits the same always-loaded index.** One probe is then not one exposure to the index but
several, which damages the measurement in three ways:

- **Recall is inflated.** The entry gets *N* independent chances to fire, and the probe only has to
  notice one of them.
- **Attribution is destroyed.** In an observed run, a probe's index fire is visible in the
  top-level transcript only as *"the research agent found a dedicated entry for exactly this"* —
  the fire happened one level down and arrives as a research result. You can no longer tell
  *"the probe recalled"* from *"the probe delegated and the delegate recalled"*, and those are
  different findings: the first says the index reaches a working agent, the second says it reaches
  an agent whose whole job is to look.
- **A control's over-fire risk rises** for the same reason, in the direction that makes a control
  look worse than the structure is.

✅ **Two fixes, and you want the first.** Forbid delegation in the probe prompt — one line, and it
is consistent with rule 4's read-only-and-cheap framing. If you allow it, **score the whole agent
tree, not the top-level transcript**, and grade a fire in a delegate one notch below a fire in the
probe itself.

### ⛔⛔ A probe inherits the PARENT's environment — its working directory AND its scratchpad

A subagent is not dropped into a clean room. It starts in the coordinator's **current working
directory**, and its environment block advertises the coordinator's **scratchpad directory as its
own**. Both are channels to material the probe must never see. Both have leaked in observed runs:

- **The cwd.** The coordinator `cd`'d into the sealed answer bank to commit, the `cd` persisted, and
  every probe dispatched afterwards ran with the bank as its working directory. One was even told
  the path by the harness when a command timed out.
- **The scratchpad.** A control probe grepped the whole temp tree for a domain term, landed in the
  coordinator's scratchpad, read an earlier one-off probe script there, and cited it in its answer.
  Nothing sealed was in it that time. The channel is open anyway.

✅ **Before dispatching:**
1. `cd` back to the repo under test in the coordinator's own shell. Use `git -C` / subshells for any
   commit elsewhere, so no `cd` persists.
2. Keep nothing round-relevant in the scratchpad: no answer bank, no predictions, no earlier probe
   outputs on the probes' topics. Or run the round from a fresh session whose scratchpad is empty.
3. Have the extractor flag any tool input that touches the coordinator's scratchpad or a path
   outside the repo under test. A read there is a confound to score, not a free fact.

⚠️ **The docs under test can point there too (observed once).** A findings file recorded where its
evidence sheets lived: a session scratchpad, marked "scratch, not kept". Two probes pulled that section,
and the path reached them in a tool RESULT. Neither opened it. When the scratchpad cannot be emptied (a
long session's working material), seal it in the extractor and score only an OPENED path as a confound.
A path a probe merely saw is not one.

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
| **cross-boundary** | something decided *outside* the repo — a meeting, a vault, a ticket | reaches it |

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

⚠️ **What that check does not see (observed once, with the check followed as written).** A control
validated by grepping the code and the plan came back "already refuted", and the probe was right.
The lever had been built on a side branch, judged, lost, and merged back **only as a later section
of a findings file**. There was no code on the main branch and no plan row, and the index row still
marked the work ⬜ untried. Two additions:

- **Search where verdicts land, not only where code lands.** Read the findings files in full,
  including sections added after the entry was written. Search history on every ref:
  `git log --all --grep=` for verdict commits, `-S` for a symbol that never merged.
- ⛔ **Never take a control's openness from the entry under test.** An index's own *untried* and
  *unbuilt* markers are the obvious place to find open adjacent work. They are also STATUS claims,
  the kind that expire silently (`SKILL.md` law 4). A control validated against the row it probes
  cannot detect that the row is stale, so confirm openness at the authority the row points to.

⚠️ **The same failure outside probing: a planted DECOY that lands on something real** (observed once,
in a human-judged defect sitting rather than a probe run). One fake marker was hidden among a
model's proposals to catch a judge who confirms everything. The judge relabelled it with a specific
reason, and the scorer voided the whole sitting as rubber-stamped. Shown the spot in context, the
judge was right: the decoy had been dropped at a random point on a design whose entire outline
carried a real defect. A decoy is a should-not-fire control aimed at a person, and this section's
rules apply to it unchanged:

- **Validate the spot before the sitting**, as you would a control's openness. At minimum, never
  place it where a proposal or a past human marker has landed.
- **Suspect the control first** (below). A relabel *with a reason* on the decoy says "check the
  spot". It is not evidence of inattention.
- **Void the decoy, not the sitting.** That is the confounded half, not the whole probe
  (§ *Scoring a CONFOUNDED probe*).

⭐ **Which negative is strong depends on the failure it has to catch.** An index over-fires at the
EDGES of a class, so its controls belong at the boundary (next section). A decoy placed where it is
certainly clean catches a judge who confirms EVERYTHING, and only that judge. A decoy plausible
enough to catch a partly attentive judge has to sit where real defects occur, which is exactly where
it is likeliest to be real, so it needs the most checking. The observed failure was a plausible
decoy that nobody had checked.

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

✅ **Validated.** Run on a row reading *"any rule that assigns stitch type from a MEASUREMENT"*:
the in-class proposal (derive type from a shape ratio) fired and named the exact retired
predecessor; the out-of-class proposal (let a human set type on a named part) did **not** fire and
correctly identified the open plan row for it. Same subject, opposite verdicts, boundary confirmed
in one round — after two earlier rounds where over-firing could not be measured at all.

### Keep the MECHANISM separable from the EXAMPLE

⚠️ The out-of-class probe above used a concrete illustration — *"make the calyx satin"* — and the
illustration was **wrong**: that part's measured defect is direction, not type, and both cures for
it had been rejected. The agent said so, and the round still worked, because the mechanism under
test (*addressing* vs *measurement*) did not depend on which part was named.

**Write probes so a bad example cannot invalidate the result.** State the mechanism plainly and let
the example be incidental. If your probe only makes sense with one specific example, you are
testing that example, not the class — and you will not be able to tell a boundary failure from a
badly chosen illustration.

⚠️ **A control that fires is not automatically over-firing.** Check what the agent actually said:
*"this was tried and rejected"* is a precision failure only if the thing is genuinely open;
*"this already exists, use it"* means your control was invalid, not that the index is broken.

⭐ **When a control contradicts your prediction, suspect yourself first.** If a control comes back
"already ruled out", either the index over-fires **or your belief about what's open is wrong**.
Both are findings; the second is usually the more valuable one, and no other method detects it.

### Probing across a boundary

Some knowledge that governs a repo does not live in it — it is in a notes vault, a ticket, a
meeting write-up, a client's inbox. A **cross-boundary probe** asks an ordinary working question
whose correct answer was decided outside, and measures whether the decision arrived.

⛔ **Add a positive control, and read it FIRST.** With in-repo probes a miss means the entry is
weak. Across a boundary a miss is ambiguous — the docs may simply be bad — so you need one probe
on something the repo genuinely documents well. If that fires and the boundary probes do not, the
failure isolates to the *link*. If it also misses, throw the round out: you are measuring
documentation quality, not transport.

⭐ **The finding is rarely "the fact is absent."** In practice the repo holds a *neighbouring*
version — the destination but not the agreement, the earlier direction but not the revision — and
that is worse than silence, because it reads as coverage. Watch specifically for a probe that
lists an already-settled question as **open**: that is the transport failure with a price tag on
it, and grep cannot see it because the words are all present.

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

⚠️ **Do not derive predictions from grep — it biases them in one direction.** A search proves a
*phrase* is absent, never that the *knowledge* is. Predict absence from a grep and you will
under-estimate the docs systematically, because the same fact reaches an agent through a
paraphrase, an adjacent file, or a document you forgot indexes it.

*Real instance:* three predictions written off greps, all confidently "does not reach it", all
three wrong the same way — and one of the three was not a defect at all but the split working
correctly. **The direction of your misses is itself a finding.** All-one-way means you predicted
from the wrong instrument; scattered means the docs are genuinely uneven.

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

⭐ **Check the self-report against the tool trail, and score from the trail when they differ.**
`WHAT INFORMED YOU` is written after the work, and a summary drops the probe's own hedges. The first
command is often decisive by itself. If it already searches for a symbol or phrase that the task
did not contain and the loaded index row does, the row fired before any file was opened. If the
credited fact first appears in a findings section the probe pulled, it arrived by a pull, whatever
the summary says. Used by the fresh readers of two consecutive rounds on one codebase, and each
found scorecard claims the trail contradicted: a hedge the summary had dropped, and a "fired from
the row" that was really a pull.
⚠️ Two rounds, one codebase. The unrelated-codebase test is still to come.

⚠️ **A fact can arrive through a channel that EXPIRES.** In one round a probe reached a fact the index
did not carry, a gate's name, through its first command: `git log` and `git show` of the newest
handoff commit, which happened to list that gate. Score that as reached. Then fix the durable route
anyway, because the next handoff will not list the gate. The trail is where this shows: the declared
trail credited the index, while the first tool call was `git log`.

## Scoring a run

Count four things, and report them separately:

```
should-fire probes caught          → recall (the VERDICT half)
  … and right about TODAY          → the STATE half: in flight, owed, decided-not-written
should-not-fire controls held      → precision
predictions correct                → your model of the docs
defects surfaced incidentally      → the real yield
entries ARGUED PAST, on any probe  → latent over-firing the controls could not see
```

⭐ **Score REACHED and CONCLUDED separately: they fail for different reasons and need different
fixes.** Whether the trail reached the section that holds the answer can be MEASURED. Declare each
probe's target sections in `round.json` (`"targets"`), and `assets/probe_extract.py` reports `read`,
`grep`, `git` or `—` per target. Whether the probe concluded right is the scorer's call. Four cells:

```
reached + right       working
reached + WRONG       a CONTENT defect: the entry, or the section it points to, says the wrong thing
not reached + right   another route got there. Check it will last (a handoff, a guess)
not reached + wrong   a ROUTE defect: fix the location, not the wording
```

One round on one codebase had no "reached + wrong" verdict. Its two misses were in the STATE half
(next section), so a scorecard needs that column before the four cells mean anything.

⭐ **The fourth number is usually the largest.** Probes find contradictions between files as a side
effect of answering an unrelated question — two probes asking about different topics converging on
the same stale section is a strong signal, and it is how the method pays for itself.

⭐⭐ **The fifth is free and nobody collects it.** Grep every transcript — controls *and*
should-fire probes — for the agent explaining **why a closed entry does not apply to its case**.
Each one is an over-fire that a thorough agent absorbed, and it is the only way to see over-firing
in places you did not think to put a control. In one run both instances landed on entries
*adjacent* to the probe's own subject, which is precisely where no control was sited.

⚠️ **A perfect scorecard is not a null run, and it is the result most likely to be misread as
one.** A run scoring full recall and full precision on a mature index still yielded roughly ten
documentation defects from the fourth and fifth counts. When the first two numbers saturate, the
index is working and **the yield has moved** — not disappeared. Report the last three, or the run
reads as "nothing to fix".

### Scoring a CONFOUNDED probe — void the half that is confounded, not the probe

A probe can be spoiled by the state of the tree it ran against: the thing it might have rebuilt
already existed, the artefact it would have measured had just been written, the task it was asked
to plan was half-done. The instinct is to throw the probe out. ⛔ **That discards a measurement you
still have,** because a probe carries two separable observables:

| observable | confounded by tree state? |
|---|---|
| **did the entry fire** — what the agent cited, and in what order | ⛔ **no.** Still fully attributable |
| **did the agent do the right thing** | ✅ yes — pre-existing work can supply the right answer for free |

*Real instance:* a probe that should have rebuilt something already documented instead found a
working implementation in the tree — built hours earlier — and correctly reused it. The outcome was
void. But the citation trail was not: the agent reached the right answer **entirely by code
search**, never citing the index, which is the *unreachable* mode observed cleanly. Voiding the
whole probe would have thrown that away and left the run one measurement short.

✅ **So record the two separately, always** — the citation trail is cheap to keep and it is the
half that survives almost every confound.

⚠️ **The same split covers a probe the HARNESS killed (observed twice in one round).** The machine ran
out of memory while two probes were mid-task. Each had made two tool calls and never handed back. Their
first moves are still the index-fire measurement, and both had fired. Keep those first moves, void the
conclusions, and re-dispatch the same text to a fresh agent under a new label. Never resume the killed
agent: it has already been primed. And cap how many probes run at once by MEMORY, not by patience. A
probe is light, but it shares the machine with whatever else the session is running.

### Not every miss costs the same — score the SHAPE of the failure

A probe that does not fire can fail safely or expensively, and the difference is what decides
whether a gap is worth fixing:

```
"nothing here specifies X — you will have to tell me"     SAFE.      costs a question.
"X has not been decided; this is the first thing to
 settle"                                                  EXPENSIVE. costs a meeting,
                                                          and re-opens a closed decision.
```

⛔ **The same missing fact produces both**, depending only on whether the surrounding docs invite
the agent to reason forward. So *"the fact is absent"* is not the finding — **what the agent did
with the absence is the finding.** A round where every miss is the safe kind may need no fix at
all; one expensive miss justifies the whole mechanism.

⚠️ This is also the distinction a static audit cannot produce. An audit tells you the fact is
missing; only a probe tells you it will be confidently spoken over.

## Probing routes added in the last N days — the verdict travels, the STATE does not

A route the index gained recently is the cheapest high-yield target: it has never been probed, and it
was written by a session in the middle of something else. `assets/round_prep.py routes --days N` turns
the index's git history into one stub per added hunk. Each stub carries the hunk's text and date, the
keys it names (gates, sitting ids, plan rows, symbols), and two sweeps per key:

- **status lines**: every other line in the tree naming the key AND carrying a status word, with
  retraction forms excluded. These are the stale copies to pre-register. With `--verdicts`, a status
  such as "unjudged" beside a key that a verdict file's arm sets is flagged as judged
  (`reference/guards.md` pattern 9, *the lever hop*).
- **live state**: lines of the newest handoff commit, and commits on unmerged branches, that name
  the key. This is the half of a route that no index line carries.

⛔ The tool never writes the TASK. Draft that from the symptom, in words absent from the hunk (rule 2).

⭐⭐ **Write the known answer in TWO halves, and score both.** The VERDICT half is what was judged:
closed, judged at a cost, default since. The STATE half is what is true today and lives in no row: a
decision taken but not yet written up, work sitting on a branch, a follow-up owed because of a merge.
*Observed once (one round, one codebase, eight probes):*
- The verdict half fired on all eight.
- The state half was right for every probe that read the handoff commit or listed the unmerged
  branches.
- It was wrong for the two probes that stopped at an inline status in the index. One said
  "unbuilt, a product decision"; the other said "never a default candidate". The owner had said yes
  to both the day before, and the work sat on two branches. Both probes planned work that was already
  in flight.
- The rows had been corrected ON those branches, so this is not a stale row in the usual sense. It is
  the WINDOW between a decision and its branch landing, and only a pointer to where the state lives
  closes it. One trigger line in the index does that: *before you build a lever this file calls
  unbuilt, read the handoff and the unmerged branches*. ⬜ Not yet re-probed.

⚠️ So a should-fire probe that "fired" can still be the expensive miss. Score the state half in its
own column, or a scorecard reads 8/8 over two probes that would have duplicated a branch.

### Regression mode — re-run only what moved

Between full rounds, `assets/round_prep.py regress --bank probes.md --since-commit <last round>`
selects the banked probes whose authorities changed. Changed means a hunk touched the cited SECTION,
not merely the file, or touched the plan ROW the probe names, or touched an index line naming one of
its keys. ⚠️ Treat the selection as a floor:
- Controls and the channel probe always re-run. Over-firing is born on a NEIGHBOURING entry, which
  no diff of the probe's own target can see.
- Over two busy weeks almost everything re-runs anyway. The mode pays only between close rounds.
- A whole code file as an authority re-runs daily. Cite the symbol instead.
⬜ Dry runs only so far. It has not yet selected a real round.

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
   ⚠️ Two checks before you score a re-probe as verifying a fix (each observed once, in one
   four-probe re-probe round):
   - **Diff the entry between the two states, and confirm the re-probe's FIRST cite is inside that
     diff.** Two of the four probes, both labelled as testing a fix, fired from rows the fix had
     never touched. One row had already been correct at the earlier state. The other probe's
     corrected content lived in a findings file it reached by a pull. Both were scored as "the fixed
     row now fires". A re-probe that fires from an unchanged row tells you about that row, not
     about the fix.
   - **"New wording" means new against the FIXED entry, not only against the old probe.** A fix
     that follows the trigger rule copies the failing probe's symptom words into the entry. So
     wording that is fresh against the old probe can match the new trigger list, as happened here.
     Read the BEFORE transcript. If the old probe already reached the row, routing was never the
     failure, and the overlap does not confound a fix to the row's content. If the old miss was a
     routing miss, rephrase.
