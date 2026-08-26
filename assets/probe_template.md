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
