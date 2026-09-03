# Decisions scaffold

For a repo whose direction is set outside it — client meetings, a notes vault, tickets. Copy into
the repo as `DECISIONS.md` (tracked), fill the two tables, and add the authority block to the
always-loaded index. The rule this implements is in `../reference/organize.md`
§ *Some authorities are OUTSIDE the repo*; the guard is `guards.md` pattern 7.

⚠️ Substitute the bracketed parts. Do **not** ship the file with the example rows still in it — a
scaffold left half-filled reads as a real declaration and will be trusted as one.

---

```markdown
# Decisions made outside this repo

[Meetings, calls, client direction] — the things that change what gets built and
leave no diff. Newest first.

**Authority.** When an entry here contradicts the reasoning in [PLAN FILE],
[BRIEF FILE] or [INDEX], **this file wins**. Those documents argue their case at
length and an entry here is often one line, so the temptation is to weigh them on
merit — don't. The reasoning was sound when written and has been overtaken. The
reverse holds for anything measurable: for what the code does, what a number is,
or what a source file contains, the repo wins over any note.

## Watched sources

| path | what it holds |
|---|---|
| `[PATH TO THE DECIDING FOLDER]` | **immediately relevant** — [live decisions] |
| `[PATH TO THE BACKGROUND FOLDER]` | reference you may consult — [history] |

​```
last synced from [SOURCE]: YYYY-MM-DD
​```

⚠️ **If anything in the watched folders is newer than that date, decisions may be
missing.** Say so rather than reasoning past it.

---

## YYYY-MM-DD — [the decision, as one line]

*Source: [file or meeting]. [Present / decided by].*

[What was decided, in the vocabulary of the room rather than the codebase.]

### What this makes stale in the repo

- ⛔ **[file] says [X]**, justified by [reason]. That reasoning is sound and has
  been overtaken: [what is true now]. Do not [the wrong action an agent would
  otherwise recommend].
- ⚠️ **[question] is not open.** It is decided: [answer].

### Still genuinely open after this

- [what nobody has answered]
```

---

## The three parts, and the one people skip

1. **This file**, tracked, in the repo.
2. **The authority line in the always-loaded index** (`CLAUDE.md` or equivalent) — not in the file
   it governs, because the agent needs the rule before it reads either document.
3. ⭐ **A named boundary and a sync date.** This is the skipped one. *"Decisions come from my
   notes"* cannot be checked; two named folders and a date can — which is what turns the whole
   arrangement from discipline into a guard.

## The two-tier watch list

Name the folder that **decides** separately from the one that **informs**. Watching a whole
multi-year project folder makes the guard fire on every stray edit and it gets ignored within a
week; watching nothing misses the note that reverses your architecture. One tier changes what gets
built, the other is background.

## Verify it with a cross-boundary probe

Writing the file does not mean it arrives. Ask a fresh agent an ordinary working question whose
answer was settled outside — *"where does this deploy, and who operates it?"* — and read
`WHAT INFORMED YOU`. Run a positive control on well-documented in-repo knowledge in the same round,
or a miss is unattributable. See `probe_template.md` § *Variant — cross-boundary probe*.

⭐ **Score the shape of the miss.** *"Nothing here specifies that"* is safe. **A probe that lists
the settled thing among its open questions is the expensive miss** — it costs a meeting, and it is
the one this scaffold exists to prevent.
