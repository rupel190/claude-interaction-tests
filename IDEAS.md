# Ideas

Things worth considering for this skill that are **not yet validated**. Nothing here
has been through a run; nothing here should be cited as method.

⛔⛔ **ANONYMOUS. This repository is published; the codebases it learns from are not.**
Never name a client, a project, a product, a partner or a person. Never quote a figure that
identifies one — a price, a part number, a customer's design. ⭐ The MECHANISM is the whole value
and it survives anonymisation intact: *"one quantity computed in two places disagreed by 20%"* teaches
exactly what the real numbers taught, and *"a regulatory-compliance selector with no call site"*
teaches exactly what naming the regulation would. ⚠️ Entries drafted before this rule were
generalised while still unpushed (2026-09-10, and 2026-09-15 for the two carried
over from a second checkout); check any new entry against it before committing,
because a push cannot be taken back. An entry graduates by
being tried, measured and then written into `SKILL.md` or `reference/` — or by being
recorded as declined, which is worth as much.

---

## Differential testing, as a third complementary technique

*Raised 2026-09-08, from a run on a client codebase that read a third party's cost estimator and
found five defects in it. ⚠️ Details generalised — see the anonymity rule at the top of this file.*

`SKILL.md` already draws one division: **probes find what does not fire; an audit finds
what does not exist.** There is a third thing neither of them finds — **what a program
contradicts about itself** — and the technique for it is cheap enough to belong beside
the other two.

**The move.** Run the same inputs down two paths that ought to agree, and look at the
disagreement rather than at either answer. Shapes that keep paying:

- **One quantity computed in two places.** A total summed in the calculation layer and
  summed again by an exporter. In the case that raised this, the screen and the workbook the tool emails out
  disagreed by about 20% per unit — the same run, the same config, the same instant, two
  different lists of line items.
- **Defined against called.** A function that implements a check, and no call site.
  There a regulatory-compliance selector existed in full, with the reference tables behind it,
  and the shipped path used a variant that hardcoded `compliant: true`.
- **A label against what it governs.** A field called "Margin" that moves three of five
  cost categories, because the other two come from a published price list.
- **Two conventions for one kind of line.** Rounding applied per-item on one path and
  on the total on another.
- **A schedule against its own boundaries.** Walking a tiered rate across each
  threshold; there, four boundaries where a *larger* job produced a *smaller* fee.

⭐ **Why it is worth a section rather than a footnote: the findings survive a stale
reference.** A probe measures recall against documents that may be out of date; an
audit compares a system to an external truth that may itself have moved. Differential
testing compares a system to itself, so *"your price data is old"* and *"that document
was superseded"* are not available as rebuttals. That makes it the technique of choice
when the finding has to be defended to someone who owns the system — which is exactly
when interaction testing is weakest, because the person can always dispute the doc.

⚠️ **The boundary, and it is a real one: it finds disagreement, not wrongness.** If both
paths are wrong in the same way it sees nothing at all, and it cannot tell you which of
two disagreeing answers is correct — only that somebody must decide. It is also blind to
anything computed exactly once, which is most code.

**Where it would attach.** `SKILL.md`'s *"What this method does NOT find"* already lists
**config and data surfaces** as a weakness — *"a shared dict key whose meaning differs
between producers makes two runs look comparable when they are not"*. That is precisely
a differential-testing target, so the section is where this lands if it graduates: the
division becomes **probes find what does not fire; an audit finds what does not exist;
differential testing finds what does not agree.**

**What would have to be shown first.** Whether it can be *specified* the way probes can.
Probes have a construction discipline — one per agent, predictions written first,
controls in both directions. The equivalent here would be a way to enumerate candidate
path-pairs in an unfamiliar codebase without simply relying on someone noticing. Until
that exists this is a skilled manual technique, not a method, and `SKILL.md` should not
claim otherwise.

### ⭐ A probe performed it SPONTANEOUSLY, and it paid — plus a candidate enumeration rule

*Observed 2026-09-16, in a seven-probe run nobody had told about this entry.*

A probe asked to build a small measurement script discovered that the **predicate it had to
implement had three implementations already in the tree**, and that they did not agree. Instead of
picking one, it computed all three and **printed the disagreement as a control column**. The result
was a mixed one of exactly the useful kind: two of the three agreed on every case — a null that
retired a documented worry — while the third diverged on a specific, already-known-and-unresolved
boundary. The probe then reported the divergence as *expected* rather than as a bug, because it
could see which of the three it was.

⭐ **This is the first evidence the technique can be REACHED rather than only wielded**, and it
suggests the enumeration rule this entry says is missing — and it is small enough to state:

> **When you must implement a predicate the codebase already has an opinion about, count the
> opinions before writing yours.** Grep for the concept, not the function name; if more than one
> implementation exists, the deliverable is the comparison, not a choice.

⚠️ **It does not generalise to the whole technique, and I will not pretend it does.** This case had
the easiest possible trigger — the agent *had to write* the thing, so the duplicates were directly
in its way. The hard cases in the parent entry (a total summed in two layers, a defined-but-never-
called check) have no such forcing move, and nothing here says how to find those. What it does
establish is that **a build-it probe is a delivery vehicle for differential testing**, which makes
the two techniques cheaper together than separately — the probe was already running.

---

## Harvest the misses from ordinary work — and tell the caller you want them

*Raised 2026-09-09, from a long session on a client codebase in which the assistant failed three
of this skill's own probe questions live, unprompted, while doing unrelated work.*

A designed probe is expensive: one agent per probe, predictions written first, controls
in both directions. That cost is what makes the method trustworthy and it is also what
makes runs rare. Meanwhile **every ordinary session generates the same phenomenon for
free** — an agent proposes something the docs forbid, restates a documented fact
wrongly, or re-derives a finding that is already written down — and nobody collects it.

**The move.** Two halves, and the second is what makes the first happen.

1. **Treat a live miss as a probe result.** When an agent notices mid-task that it got
   something wrong that the docs already knew, that is a probe firing, with the extra
   information a designed probe cannot have: the agent can say **what it read and what
   it did not**. A probe tells you a row did not fire. A live miss tells you *why*.
2. **The skill should ask.** An agent that invokes this skill is exactly the population
   that generates these, and it has no reason to think anyone wants them. A short
   section telling the caller *"if you caught yourself missing something the docs knew,
   report it back in this shape"* costs one paragraph and turns every invocation into a
   potential data point.

**What the session produced, as the worked example.** Three misses, each with a distinct
mechanism, none of which a designed probe would have surfaced as cheaply:

- **Proposed changing a shipped integration contract** — the single move the plan's ownership track
  explicitly forbids. *Mechanism:* read the document that NAMED the topic and not the one
  that held the METHOD. The index routed by subject; the governing rule lived elsewhere.
- **Asserted a fact the authority contradicts** — a claim about which side of an integration
  owns a job, stated against the ownership table that says the opposite.
  *Mechanism:* inference from a partial read, stated with the confidence of a lookup.
- **Re-derived a finding already written down** and presented it as new — after the user
  had explicitly warned that the docs had changed. *Mechanism:* **selective re-read biased
  by prior.** The warning was heeded by re-reading the files already expected to matter,
  which is precisely the set that cannot contain a surprise.

⭐ **That third mechanism is the one worth designing against**, and it suggests a probe
shape: ask a question whose answer lives in a file the agent has **no reason to expect**.
Probes that ask about the obvious file test routing; probes that ask about the unexpected
file test whether the index is doing any work at all.

## Close the loop on the RUN, not just on the misses — and say so in the skill

*Raised 2026-09-16 by the caller of a run, mid-run: "feel free to set out an agent afterwards to
improve the skill based on the outcome too. That's a thing the skill should announce itself."*

The skill already asks for misses harvested from **ordinary** work (above). It says nothing about
the much richer artefact a **run** produces and then throws away.

A run generates four things the skill cannot get anywhere else, and all four are gone the moment
the session ends:

1. **Predictions against outcomes.** Written first, by discipline. Where the predictor was wrong
   about their own docs is the single most informative row in the table, and it is never about the
   codebase — it is about which entry SHAPES fire and which do not.
2. **Which probe FRAMINGS worked.** `SKILL.md` already claims build-it beats is-this-allowed. A run
   either supports that or does not, per probe, for free.
3. **Failure modes observed against the six named.** A run that keeps producing something that is
   not cleanly any of them is the evidence for a seventh.
4. ⭐ **Knowledge the probe INVENTED.** Observed in the run that raised this: a probe recalled a
   documented noise floor correctly and then added an argument the documentation did not contain —
   that a *second* correlated case agreeing made the result LESS credible rather than more, because
   both were named in the noise record. **A probe is scored as a recall test; it is also a fresh
   reader of the material, and a fresh reader occasionally sees further than the author.** Nothing
   in the method currently has a place to put that, so it survives only if someone notices.

**The move.** Two halves.

- **Add a sixth move to the five**, or a closing step: *after scoring, dispatch a fresh agent to
  fold the run's outcome back into `SKILL.md` / `reference/` / `IDEAS.md`.* One paragraph in the
  index, the same way the harvest section works.
- ⚠️ **It must be a FRESH agent, not the one that ran the probes.** The runner wrote the
  predictions and is invested in them; it is the worst possible reader of its own scorecard. The
  improver should get the results table and the probe transcripts, and not the runner's narrative.

⚠️ **And it must distinguish two outputs that a run mixes together**: fixes to the *docs under
test* (which belong to the project) and fixes to the *method* (which belong here). A run naturally
produces far more of the former, and the latter is what evaporates, because it looks like a
digression from the task that was actually commissioned.

⛔ **Not validated.** Nothing here has been through a run of its own. The obvious risk is that a
method which updates itself from every run drifts toward whatever the most recent codebase happened
to need — the same overfitting the skill warns about for probes. A graduation bar is probably
"observed in two runs on unrelated codebases", not "observed once".

### ⚖️ First execution — what it did and did not establish

*Written by the fresh reader, not the runner, on the seven-probe run that raised this entry.*

**Claim 4 — knowledge the probe INVENTS — is SUPPORTED and has graduated** to `SKILL.md`
§ *Knowledge the probe INVENTS*. Four instances in one run, not one, and the shape turned out
**narrower and more useful than this entry claimed**: the probes did not have outside insight, they
took a rule the docs already state and **extended it one step to a case the docs never applied it
to**. That narrowness is what makes it safe to act on and tells you where it belongs — back in the
entry it extends, as a widened scope. ⭐ An unexpected corollary: this is the **one** yield that did
*not* correlate with build-it framing. The single write-it-up probe surfaced zero artefact defects
and produced the run's cleanest invention.

**Claim 2 — which probe FRAMINGS worked — is SUPPORTED and has graduated**, as a measured
observation rather than an assertion: five of five build-it framings surfaced documentation defects
incidentally, the one write-it-up framing surfaced none.

**Claim 1 — predictions against outcomes — is SUPPORTED, with a twist the entry did not anticipate.**
The predictor's most consequential error was **not about their own docs at all. It was about the
HARNESS** — the reachable-channels table, written from assumption, declaring a channel unreachable
that was in fact loaded into every probe. That excused a real miss as untestable. Two runs have now
got that same row wrong, in opposite directions, which is a two-observation bar met; the rule and
the per-tier framing are now in `SKILL.md`'s checklist.

**Claim 3 — a seventh failure mode — got NOTHING either way.** No observed failure resisted the six.
What the run produced instead was a *refinement* of an existing one (over-firing appears on
should-fire probes, with a "broad class, narrow verdict" mechanism), which is the healthier outcome
and is now in `reference/taxonomy.md`.

⛔ **The MOVE itself — "dispatch a fresh agent afterwards" — remains UNVALIDATED, and I cannot
validate it, because I am it.** A single agent reporting that its own commission was worthwhile is
the incentive problem this file warns about two entries down. What can be said from the outside:
the runner's scorecard and the transcripts **disagreed in three places**, all in the direction of
the runner being harder on their docs than the evidence warranted, and none of the three was
recoverable from the runner's narrative. Whether that is worth a standing sixth move, or whether it
was a one-off property of a run whose predictor was unusually invested, needs a **second run on an
unrelated codebase** — the bar this entry itself set. Do not promote it on this one.

⚠️ **And one cost is now measured rather than guessed:** folding a run back in produced edits to
five method files from a single run. That is exactly the drift rate this entry worried about. If it
does become a standing move, it needs a discipline the harvest section already has — **a validated
tier and an unvalidated tier** — or the method acquires a new claim every time anyone uses it.

## A candidate seventh failure mode: ambiguity that propagates

Same session, and it is not cleanly any of the six. A load-bearing sentence in a findings
file had **two readings**, both fully present in the words. It was copied verbatim into a
plan row, and from there into a subagent's brief; the subagent built a measurement
instrument against the wrong reading and validated it end to end before anyone noticed.

⚠️ **The index worked perfectly at every step.** The row fired, the agent pulled the right
file, the sentence was current and true. **Copying preserved the ambiguity while stripping
the surrounding context that would have resolved it** — so each hop made the wrong reading
more load-bearing and less checkable.

It is adjacent to **partial instruction** but distinguishable by its tell: partial
instruction is *incomplete* and you cannot see what is missing; this is *complete* and
you cannot see which of two things it says. And it has a signature the others lack —
**the error appears one or two hops away from the file that caused it**, in a document
that merely quoted it.

⚠️ **Still at one instance after a second run — and the absence is worth recording.** A
seven-probe run in 2026-09 produced no second case: every failure it found sat cleanly inside the
six, and the only structural result was a *refinement* of over-firing rather than a new class. That
is weak evidence **against** promotion, not neutral — a mode that does not recur across two rounds
on an actively-churning repo is a candidate for being an instance of something else. ⬜ Leave it
here; do not move it to `reference/taxonomy.md` on the strength of a single sighting, and if a
third round also produces nothing, close it as a variant of partial instruction rather than letting
it sit open indefinitely.

⛔ **The boundary.** One instance. It may just be partial instruction wearing a different
coat, and calling it a mode on n=1 would be exactly the over-naming this skill warns
about elsewhere. What would settle it is whether the fix differs: partial instruction is
fixed by *adding* the missing clause, and this would be fixed by *disambiguating in
place* — which, if true, means an index that only routes is insufficient and a
verdict-bearing index has to carry the reading, not just the pointer.

**Where it would attach.** The harvest idea belongs near *Quick start* (it changes when
you run, not how). The seventh mode belongs in `reference/taxonomy.md` **only after a
second instance**, and it should be recorded as a candidate there in the meantime, since
"we saw this once" is itself worth writing down.

**What would have to be shown first.** For the harvest: that a self-reported miss is
*honest*. An agent grading its own recall has an obvious incentive problem, and the three
above were only credible because each was contradicted by a specific document that could
be quoted back. A reported miss without that citation is an anecdote, so the report shape
must require the contradicting file and line — otherwise this collects impressions rather
than data.

## Data provenance as a probe target

**Found:** 2026-09-08, in a client's production-dashboard repo (a separate project).

That repo carries a hand-written `DATA_PROVENANCE.md` — a table mapping every field
to its source, explicitly separating **direct copies** from **estimates and
heuristics**, tiered by how much downstream weight rides on each guess. It is good
documentation, and it had drifted: every line reference into one script was stale by
35–42 lines, another by ~370, and one estimation was described **backwards** (it said
a default fires for unparseable timestamps; the code skips those and defaults
elsewhere).

**Why this belongs here.** It is a documentation genre this method has not looked at,
and it fails in a way probes should catch:

- A provenance doc asserts *code-anchored facts* — file, line, join key, "this value
  is copied, that one is inferred". Those are checkable, unlike most prose.
- Its drift is **silent and directional**: line numbers only ever go stale in one
  direction, and a reader who trusts a stale reference lands in unrelated code and
  concludes the doc is wrong about the substance too.
- The doc dates itself ("as of 2026-06-11"), which reads as honesty but functions as
  a licence to not update — the same move as a stale `last synced` line.

**What to try.**
1. A probe class for "is this field measured or assumed?" — the estimate/copy
   boundary is exactly the kind of thing an agent silently flattens. Ask a fresh
   agent to price or reason with a documented estimate and see whether the estimate's
   status survives into the answer.
2. A guard for **line references in prose** — cheap and mechanical. Any `file:line`
   or `§` citation in a tracked doc, checked against the file. Closest existing
   relative is `reference/drift-protection.md`.
3. Consider whether the copy-vs-inferred distinction generalises beyond data docs.
   An architecture doc has the same split: what the code *does* versus what someone
   *believes* it does. The second kind is what re-litigation feeds on.

**Open:** whether this is a new failure mode or an instance of one already in the
taxonomy. It looks like drift with a sharper edge, not a new class — but the
verification story is different, because these claims are machine-checkable and most
documentation claims are not.

## A same-session index edit is untestable by subagent probe

**Found:** 2026-09-08, running a verification round on the embroidery-digitizing pipeline
immediately after editing that repo's index.

Ten blind probes, three of them aimed at `CLAUDE.md` rows edited earlier the same
session — a widened trigger list and one new ALREADY TRIED row. **All three came back
inconclusive, and it took a probe to work out why:** the project-instruction snapshot
loaded into a subagent's context is captured from the **parent session's start**, not
read from disk at launch. The session began before the edits, so every probe inherited
the pre-commit file.

It was diagnosable only because two probes left fingerprints. One quoted a `CLAUDE.md`
line naming a script path that had been corrected hours earlier and **no longer existed
anywhere in the repo**. Another compared its own first-command timestamp against the
commit and said so outright: *"a row written to fix non-firing rows then failed to fire,
for a different reason."*

**Why this belongs here.** The checklist already says to write down which channels the
harness can reach before running. I did that — for the notes vault and for user-level
memory, and got **both wrong in the permissive direction** (both turned out reachable).
The channel I missed was the ordinary one: the file under test. The failure has a shape
worth naming — *the exotic boundaries get checked and the default one gets assumed*,
when a caching mechanism is exactly what a default channel would have.

⛔⛔ **HAPPENED AGAIN, 2026-09-16, on the SAME row and in the OPPOSITE direction — so the lesson is
not "be less permissive", it is "stop writing this table from assumption".** That run's table
declared the out-of-tree memory channel **unreachable**, and then drew a consequence from it: that
anything living only there was *untestable by this method* and a miss on it *must not be scored*.
Both halves were wrong — the channel's **index file was loaded into every probe**, and probes cited
entries from it by name without ever opening a file. A real miss was pre-emptively excused.

⭐ **Two runs, opposite errors, one row: that is a met bar, and the rule has graduated** to
`SKILL.md`'s checklist — *measure it with one throwaway probe; do not reason about where files
live*.

⭐⭐ **The deeper correction, which is what makes the row keep failing: a LOCATION IS NOT A CHANNEL.**
At that location an *index* file was loaded while the detail files it points at were only pulled —
so "reachable" and "unreachable" were **both** wrong answers, and any single-column table forces
you to pick one of them. Record reachability **per tier**, exactly as this method already splits an
index from its findings files. The harness has the same two-tier shape as the thing being tested,
and nobody had noticed.

**Consequences for a run.**
- A round cannot validate index edits made in the session that ran it. Re-running from
  the same session does not help; the snapshot is equally stale.
- ⛔ It silently converts should-fire probes into **inconclusives that look like passes**
  when the agent finds the fact by another route. Two of the three did exactly that —
  they located the underlying rules by searching the findings files directly, which reads
  as a pass and measures nothing about the row.
- ⭐ That accidental result is worth keeping: if a probe reaches the fact *without* the
  index row, the row may be **unnecessary** rather than merely unproven. Worth designing
  for deliberately — an index-blind arm as a control on whether a row earns its place.

**What to try.**
1. Add a **snapshot-freshness check** to the pre-run checklist: have one throwaway probe
   quote a string you changed this session, and read it before scoring anything else.
   Same shape as the cross-boundary positive control, and same reason — an unattributable
   miss is worse than no probe.
2. State the rule in the non-negotiables: **edit, end the session, then probe.**
3. Consider whether the method should recommend probing from a *separate* session by
   default, which also removes the author's own priming from the run.
## The harness already exists — `claude plugin eval`

**Found:** 2026-09-15, surveying the Claude Code plugin directory.

Claude Code ships a test runner for skills, and its experimental design is this method's
probe protocol with different vocabulary. Plainly: **you write a prompt, you write grader
files, and it runs that prompt twice over — once with the skill available, once with it
removed — then reports the difference between the two scores.**

| this method | `claude plugin eval` |
|---|---|
| a probe prompt | `prompt.md` (or `case.yaml`) |
| the scoring sheet | `graders/*.md`, types `regex \| tool_order \| tool_used \| file_exists \| llm \| baseline` |
| a fresh agent per probe | one clean agent run per case |
| a should-NOT-fire control | `--ablation with-without` — a second arm with the skill **removed**, scored as a delta |
| "did it fire", noted apart from "was it right" | graders marked `with-only`, incl. `tool_used: Skill`, **excluded from the score** |
| one shot | `--runs 3` by default |
| your judgement | `--threshold 0.8`, exit 1 below it |

Two of those rows are the interesting ones. The **ablation arm** is a control: if a case
scores the same with the skill and without it, the skill did nothing — the model already
knew, or the entry never fired. And keeping `tool_used: Skill` **out** of the score is the
same separation this method insists on, for the same reason: if firing counted toward the
score, a case could pass by firing and then answering badly, or fail despite a correct
answer the model already had.

Anthropic's own shipped example is a should-fire / should-not-fire list:

```json
{"query": "Help me with this USAMO geometry problem",      "should_trigger": true},
{"query": "Generate 10 practice problems similar to AIME", "should_trigger": false},
{"query": "What is a good textbook for competition math?", "should_trigger": false}
```

Those are controls. Law 2 — entries are classes, not instances — is exactly what decides
whether row 1 fires while rows 2 and 3 stay quiet.

**What it does NOT do.** Its target is a *plugin*. It can measure whether this skill fires;
it cannot be pointed at a repository and asked whether that repo's `CLAUDE.md` fires, which
is the thing this method exists to do. And it is an empty harness — no opinion about what to
probe, no vocabulary rule, no class-vs-instance rule, no failure taxonomy. **It is the runner
this method lacks; this method is the content it lacks.**

⛔ **It cannot be run here.** `plugin eval` is early access, enabled per organization
server-side. Every invocation prints `` `plugin eval` is currently in early access `` and
exits 1 — `--help` still renders, which makes it look available. Not a setting and not a
NixOS problem: none of the flag-blocking variables (`DISABLE_TELEMETRY`, `DO_NOT_TRACK`,
`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DISABLE_GROWTHBOOK`) are set on this machine.
So everything here is unvalidated by construction — which is why it is in this file.

**What to try.**
1. Write the cases regardless: four should-fire, phrased in vocabulary **not** in this
   skill's `description:`, and two should-NOT-fire controls. The sharpest control is
   *"audit this CLAUDE.md for accuracy"* — that is a documentation-authoring request, which
   is a different skill's job, and this one firing on it would be a latent over-fire.
2. Run those same cases by hand as subagent probes now. The protocol already exists in
   `reference/probes.md`; only the runner is missing. ⚠️ Mind the same-session snapshot trap
   from the entry above — edit, end the session, then probe.
3. ⭐ Steal the ablation idea for index rows. A **row-blind arm** — the same probe against a
   copy of the repo with one index row removed — measures whether that row earns its place.
   The entry above reached this accidentally, when probes found the fact by another route and
   the pass measured nothing about the row. Deliberate is better than accidental.

**Open:** whether a case's `scaffold_script` (author-supplied bash, run per case) can
materialise a fixture repo carrying a known `CLAUDE.md`. If it can, the harness stops being
"a runner for this skill" and becomes "a runner for this method".

## Marketplace positioning: authoring is not verification

**Found:** 2026-09-15, comparing this skill against the official plugin directory.

The nearest thing in the directory is `claude-md-management` (Anthropic, ~312k installs):
it finds every `CLAUDE.md`, grades it A–F against a rubric, prints a report, and then edits
the files. **That is authoring. This is verification.** Its method is to read the document
and judge it; this skill's second paragraph is `⛔ A read-through cannot substitute.` Nothing
in it measures whether a paragraph is ever *reached*. The two are not substitutes and a user
can legitimately want both — that framing should survive into any listing text.

⛔ **One concrete conflict, worth warning users about.** That rubric scores *"Conciseness —
no verbose explanations"* as a quality criterion. Law 1 puts every entry's verdict inline so
the index is useful when the pull does not happen — which reads, to that rubric, as verbosity.
Pointed at an index built this way it will propose deleting the verdicts, and it has `Edit`
in its frontmatter.

**What to try.**
1. Ship an `evals/` suite with the listing. Of the 54 plugins whose source is readable in the
   marketplace repo (39 first-party, 15 vendored external), **exactly one carries an `evals/`
   directory at all** — the remaining ~242 entries live in third-party repos that were not
   checked, so treat this as directional, not a census. Still: a skill about proving that
   documentation fires, shipping evidence that it fires, is an argument nothing else is
   making.
2. Submission is a form (`clau.de/plugin-directory-submission`), reviewed for quality and
   security; entries pin your repo at a sha. Locally, `claude plugin validate .` and
   `claude plugin tag`.

**Open:** the name. `interaction-tests` already needs a disclaimer in the README against
Storybook's unrelated meaning, and a directory listing gives you no room for a disclaimer —
the description line does all the work. Worth deciding before submitting rather than after,
since a rename post-listing costs a `renames:` entry in someone else's manifest.

---

## A defined-but-unread constant is a note from someone who already tried

*Raised 2026-09-18, from a run where a named constant with no call site turned out to carry a
diagnosis in its birth commit. ⚠️ Generalised — see the anonymity rule at the top.*

A codebase audit found a module-level constant, documented with a clear comment stating the
threshold it represented, and **referenced nowhere**. The obvious readings are both wrong and both
common: *dead code, delete it*, or *an oversight, wire it up*.

`git log -S '<NAME>'` gave the real story in one command. The constant was **born in the commit
that reverted its own consumer** — a gate that had been tried twice and rolled back, whose message
recorded exactly why it failed: the quantity was being asked of the wrong *granularity*. The author
kept the number and dropped the mechanism. Re-read at the granularity the revert message pointed
at, the same constant worked, and the change needed **no new constant at all**.

⭐ **The value was never the number; it was the diagnosis attached to it.** Someone had already
established that the quantity mattered and that one way of applying it does not work. That is
precisely the class of fact this skill exists to make recallable — and it was recallable, in the
one place nobody looks, because a constant's provenance is not a place anyone thinks to pull.

**Why it belongs here rather than in a style guide.** The skill's index-over-findings model assumes
the durable facts live in files an agent can be pointed at. This one lived in **commit messages**,
which no index covers, no `CLAUDE.md` links, and no probe currently targets. If a meaningful share
of "why did we stop doing X" answers are only in history, then history is an un-indexed tier of the
same evidence base, and an agent that never runs `git log -S` cannot reach it.

**What to try.**
1. **A probe for the history tier.** Give a fresh agent a task whose correct answer is recorded
   only in a revert commit message, and see whether it ever consults history. Prediction, written
   first: it will not — agents read files, and reach for `git log` mainly to describe recent work
   rather than to ask why something stopped.
2. **A candidate rule for the index**, if the probe fails: *before deleting an unreferenced symbol,
   or before rebuilding the capability it names, run `git log -S` on it.* Cheap, one command, and
   its failure mode is a wasted minute.
3. **A guard**: a check that lists exported/module-level symbols with no reader. ⚠️ Not to fail on
   them — plenty are legitimately for callers outside the tree — but to make the population visible,
   since nobody currently knows how large it is.

**Open.** Whether the ⛔ ALREADY TRIED index shape should carry a `git log -S` trigger term at all,
or whether that pushes a general habit into a project-specific file. And whether "the reason we
stopped" is systematically under-indexed compared with "what we decided" — this is one instance,
and one instance is an anecdote.
