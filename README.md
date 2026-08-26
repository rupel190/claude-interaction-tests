# Interaction Tests

**Tests for whether your AI agent actually recalls what your documentation knows.**

Not tests of your code. Tests of the *interaction* between an agent and the context structure you
built for it — the `CLAUDE.md`, the `docs/`, the rules, the memory, the docstrings.

---

## The problem

You work on a project for months with coding agents. You notice context issues. People say the
model is "forgetting" or "misremembering", which leads to esoteric fixes — treat it like a person,
treat it like a machine, apologise to it, threaten it.

Then you find `CLAUDE.md`, and a large context window stops looking like enough. Then you find the
rest of them: `PLAN.md`, `BENCHMARK.md`, `PROJECT_STATUS.md`, `RESEARCH_FINDINGS.md`,
`*_REFERENCE.md`. Then you land in **drift** — every document quietly getting ready to contradict
the others, despite careful incremental updates.

So you fix it. You make `CLAUDE.md` an index. You add rules for what to do on new findings. You
single-source your numbers.

**But does it work?**

That question has no answer today. You cannot unit-test whether a paragraph *fires*. You cannot
grep for "did the agent recognise this had already been decided". Every existing tool checks
whether documentation is **correct**; none checks whether it is **reached**.

## The claim

We stopped trusting code, so we wrote tests. We now don't trust agents — and we write none.

**Test-driven development is back. Just not how you expected.** The unit under test is not a
function. It is a *retrieval structure under realistic pressure*: does a fresh agent, mid-task,
carrying its own vocabulary and its own momentum, recall the thing that stops it doing the wrong
thing?

Its nearest relatives are information-retrieval evaluation and instructional design — neither of
which anyone currently applies to agent context. And unlike TDD, **the controls do the heavy
lifting**: the most valuable result an interaction test produces is usually one that proves *your*
belief wrong, not the system's.

## What it found, on a real repo

One 6-probe run against a 165 KB `CLAUDE.md` and its surrounding docs:

- a section of `CLAUDE.md` **contradicting** the authority that superseded it — surfaced twice,
  independently, by two probes that were asking about different things
- a findings file **asserting as established** a mechanism its own source docstring flags as
  *"not yet traced end to end, so do not assume it"* — in a file that had been read line-by-line
  that same day, by the person who wrote it, without noticing
- a procedural instruction that was **true and incomplete**: "pin this cache" — while a second,
  uncached call left the run nondeterministic anyway
- the discovery that most operational truth in the repo lived in **source docstrings** that no
  index pointed at

None of these are findable by reading. Reading is what produced them.

## What's here

| file | what it is |
|---|---|
| `SKILL.md` | the method, as a Claude Code skill. Start here |
| `reference/organize.md` | the documentation architecture being tested |
| `reference/probes.md` | designing, running and scoring interaction tests |
| `reference/taxonomy.md` | the six failure modes, their tells, and their fixes |
| `reference/drift-protection.md` | rules and guards that stop the structure decaying |
| `reference/planning-rows.md` | making decisions *citable* so contradictions can be found |
| `assets/` | copy-in guard test, probe template, index scaffold |

## Install

```bash
git clone <this repo> ~/src/interaction-tests
ln -s ~/src/interaction-tests ~/.claude/skills/interaction-tests
```

Then ask Claude Code to *"run interaction tests on this project's docs"* or
*"restructure CLAUDE.md as an index"*.

## Two rules that carry most of the value

1. **The index must be useful when the pull does NOT happen.** Its presence is guaranteed — it's in
   the system prompt. The *pull* is the unreliable step. So every entry carries its own verdict.
2. **Phrase entries as classes, not instances.** You closed *"ordering by summed painted area"*.
   The next session will propose *median* area. Only a class-level entry fires.

## Origin

Developed 2026-08 while restructuring the documentation of a production embroidery-digitizing
pipeline, and validated on it. The failure taxonomy is empirical — every mode in it was found by a
probe, not derived from theory.
