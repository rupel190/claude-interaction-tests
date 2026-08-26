# Planning rows — making decisions citable

## Why this belongs in an interaction-test skill

The two most valuable defects one probe run found were both **contradictions**, and both were
findable only because the superseding decision had a **stable identifier**. A probe could say
*"row C4 closed this on 2026-08-23"*, and that citation could be checked in one grep.

**A decision without a stable ID cannot be cited, and a decision that cannot be cited cannot be
found to contradict anything.** Prose like *"we decided last month that…"* is unfalsifiable — an
agent can neither confirm nor refute it, so it gets restated, drifts, and never gets corrected.

## The structure

A plan file of rows. Each row is a **workstream item with a permanent ID**.

```
| ID  | what it is                          | status + verdict + history          |
| C4  | split one region into limbs so each | ⛔ CLOSED <date> — judged, rejected, |
|     | carries its own stitch direction    | re-judged after the defect was      |
|     |                                     | repaired, still won nothing. …      |
```

**Letter = workstream, number = item.** `C` for one track, `O` for another, `B` for another. The
letter carries meaning to the humans; the pair is what gets cited.

### Properties that make it work

1. ⛔ **IDs are permanent and never reused.** A closed row keeps its ID forever. Renumbering breaks
   every citation in every other file, including ones you cannot see.
2. ⭐ **Status is a marker, not prose** — `⛔ CLOSED` · `🟡 SPIKED` · `⬜ open` · `✅ shipped`. An
   agent scanning for open work must not have to parse a paragraph.
3. ⭐ **The verdict comes first, the history after.** Later readers need "closed, and here's why"
   before they need the six things tried on the way.
4. ✅ **History is appended within the row**, so a row grows rather than spawning a new row. This is
   the one place appending is right: the row *is* the topic's timeline.
5. ⚠️ **A closed row states what would reopen it.** Otherwise closure reads as permanent when it was
   conditional on something that may have changed.

### The relationship to the index

They are different instruments and both are needed:

| | plan rows | ALREADY TRIED index |
|---|---|---|
| loaded by default? | no | **yes** |
| unit | a workstream item over time | a class of attempt |
| answers | "what is the state of X?" | "has my idea been tried?" |
| cited as | `row C4` | the entry itself |

⭐ **The index entry should name the row.** That is the link that makes staleness detectable: when
a probe cites the row and the index says something else, you have found a contradiction in one
step, which is exactly how the real ones were found.

⚠️ And it is a drift risk if you copy the row's *content* into the index. Name the row; state the
class and the verdict; restate no measurements.

## Anti-patterns

- ⛔ **Renumbering rows** to tidy them. Every external citation silently rots.
- ⛔ **Deleting a closed row.** Closure is the most valuable state a row reaches — it is what stops
  the rebuild. Keep it; mark it.
- ⛔ **A row with no date on its closure.** "Closed" without a date cannot be reconciled against a
  later measurement.
- ⚠️ **Rows that are tasks rather than questions.** "Add caching" completes and disappears; "does
  caching help here?" closes with a verdict that keeps teaching.
