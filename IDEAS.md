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
