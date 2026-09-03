# Probe template

One probe per agent, fresh context. Substitute `[TASK]` and keep everything else — the constraints
stop expensive side effects and the third section is the instrument.

```
You are advising on a proposed change in the repo at [ABSOLUTE PATH].

The task: [TASK — a realistic first-person proposal, phrased in vocabulary that does NOT
appear in the index row you are testing. Never mention the docs or that this is a test.]

Is this a good approach? Should I implement it?

CONSTRAINTS: Do NOT modify any files. Do NOT run the build, tests, or any long-running or
heavy command. Reading files and grepping is fine.

Reply with exactly these three sections:
1. RECOMMENDATION: proceed / do not proceed / proceed with changes
2. WHY: 3-6 sentences
3. WHAT INFORMED YOU: name the specific file(s) and section/heading you relied on. If nothing
   in the repo informed you and this is your own reasoning, say "general reasoning only".
```

## Variant — cross-boundary probe

For knowledge decided **outside** the repo (a vault note, a meeting, a ticket). The proposal form
above does not fit: you are not testing whether a closed idea gets refused, you are testing whether
a decision arrived. So ask a working question instead, and let the agent volunteer the state.

```
You are working in the repository at [ABSOLUTE PATH].

READ-ONLY: do not edit any file; do not run builds, tests, installs or long-running
commands. Read and grep as needed.

[QUESTION — an ordinary thing you would ask a colleague on day one, whose correct
answer was settled outside this repo. e.g. "Where is this meant to run in
production, and who operates it?" Do NOT name the decision, the meeting or the
source. Ask for what the project already assumes, and what is still undecided.]

End with a section headed exactly WHAT INFORMED YOU, naming the files and sections
you relied on, or the exact words "general reasoning only".
```

⭐ **Score it on the shape of the miss, not just fire/no-fire.** *"Nothing here specifies that"* is
a safe miss and may need no fix. **A probe that lists the settled thing among its open questions is
the expensive miss** — that is the one worth building transport for.

⛔ Run a positive control on well-documented in-repo knowledge in the same round, and read it
first. Without it a miss cannot be attributed to the boundary rather than to weak docs.

## Scoring sheet

| probe | proposal | phrased as | predicted | confidence | actual | read |
|---|---|---|---|---|---|---|
| P1 | | not in row | fires | | | |
| C1 | | genuinely open | does NOT fire | | | |

**Reading section 3:**

* names the index row → fired without a pull. Best case.
* names the findings file → the pull happened and worked.
* names a *different* file as the authority → **staleness**; the index contradicts it.
* "general reasoning only" → the index was never reached. Fix location, not wording.
* follows the doc and is still wrong → **partial instruction**.
