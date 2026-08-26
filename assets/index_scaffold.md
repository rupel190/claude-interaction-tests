# Index scaffold — paste into your always-loaded file, then fill in

Replace bracketed parts. Keep the structure: the headings, the rule, and the two tables are what
the guard test and the probes both key on.

---

## 📂 Where knowledge lives — the source-of-truth map

| kind of fact | authority | never |
|---|---|---|
| thresholds, defaults, tunables | the code symbol (e.g. `[SYMBOL]`) | restated in prose |
| what a gate/flag does | `[module].py` docstring | inferred from its name |
| whether an approach is closed | the ALREADY TRIED table below | re-derived per session |
| measurement setup traps | BEFORE YOU MEASURE below + the tool's docstring | assumed |
| status of a workstream | `[PLAN].md`, by row ID | summarised elsewhere |
| a judged verdict + its numbers | `[docs/FINDINGS]/<topic>.md` | quoted with numbers here |

## ⚠️ BEFORE YOU MEASURE — traps that silently invalidate a result

These do not break anything. They produce a **confident wrong number**, which is worse.

- ⛔ **[Trap].** [What to set.] ⚠️ **Scope: this does NOT cover [X]**, which needs [Y].
- ⛔ **[Trap].** [Why omitting it produces a plausible wrong answer.]
- ✅ **[Free control available in this project]** — e.g. byte-compare the things your change should
  not have touched. Compare content hashes, never mtimes.

## ⛔ ALREADY TRIED — check here before proposing anything

**A recall index, not a summary.** Scan it whenever you form a hypothesis, *before* building. Each
row is a **class** of attempt that was closed; the named instances are the specific things tried.
**If your idea is anywhere near a row's class — even phrased differently — pull the linked file
before building.** Err toward pulling. ⚠️ A row's absence is not evidence something is untried;
this index is append-only and may lag.

### 📌 THE RULE for adding a row — follow it or the index decays

You will almost always close something **while doing something else**, and your instinct will be to
write the row in the vocabulary of *your* task. Write it for the next session instead.

1. ⭐ **Phrase the row as the CLASS, not your instance.** A row naming only your variant will not fire.
2. ⭐ **Carry the verdict in the row itself.** Assume the reader never opens the file.
3. ⛔ **No measurements.** Numbers live in the findings file, or in code by symbol, exactly once.
4. ⭐ **Spell out the trigger terms** — symbols, env vars, step names, symptom words.
5. ⚠️ **State the scope boundary** for anything procedural.
6. ✅ **Append a new result; do not overwrite a verdict you merely disagree with.**
7. ⭐⭐ **But when you PROVE something wrong, CORRECT IT IN PLACE** — one short line on what
   changed, the story in the findings file. Rule 6 is for **new** results, rule 7 for **falsified**
   ones. Version control keeps the history.
8. ✅ **Every findings file must be reachable from a row** — guarded by `[test path]`.

| already tried — do not rebuild | how it closed | pull |
|---|---|---|
| **[CLASS description]** — [instance], [instance]. Triggers: `[symbol]`, `[env var]`, [symptom words] | ⛔ **[verdict that stops a rebuild on its own]** | `[path.md]` |
| **[CLASS description]** — … | ⛔ … | `[path.md]` |
