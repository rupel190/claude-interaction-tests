# Doc guards — what a machine CAN check

Probes measure whether documentation **fires**. Guards check the properties a machine can verify
on every commit, so probe runs stay rare. They are complementary and the division is clean:

```
guard   cheap, every commit, mechanical    "is this property still true?"
probe   costly, occasional, judgement      "does an agent recall this?"
```

⛔ **Neither substitutes for the other.** A guard cannot tell you an entry is phrased too narrowly
to fire; a probe cannot run on every push.

## The six patterns

Each was found in production use, guarding a defect that had already happened.

### 1. Doc ↔ code number agreement
**Catches:** prose quoting a value the code does not contain.
**Shape:** parse the code (AST, not regex — comments and retired entries lie), extract every value
of the thing, compare to what the doc claims.
*Origin: a config value documented in three files that the code had **never** contained — invented
in a docs commit and copied twice.*

### 2. Doc claim ↔ code reality
**Catches:** a plan row claiming something is unbuilt while the code runs it.
**Shape:** for each row marked open/unbuilt, assert the thing it asks for is absent from the code.
*Origin: nine stale rows at once, every one the same shape — the work shipped and nothing told the
row that asked for it.*

### 3. Declared ↔ implemented (**silence must not look like a pass**)
**Catches:** a declared check, rule, or hook that nobody implemented — indistinguishable from one
that ran and passed.
**Shape:** enumerate declarations from the spec, enumerate implementations from the code, assert
the sets match; an unimplemented declaration must **fail loudly**, never return an empty result.

### 4. Single-source a derived fact
**Catches:** two computations of one number drifting apart.
**Shape:** assert the two call sites resolve to the same function, or that a report and an audit
import the same module. Best applied where a number appears in both a doc and a tool.

### 5. Structural properties of the index
**Catches:** decay of the index itself — entries losing verdicts, measurements creeping back,
findings files becoming unreachable, the maintenance rule being deleted.
**Shape:** see `../assets/test_docs_index.py`.

### 6. Control rows for tooling that reads docs
**Catches:** a script that summarises or scores your docs being wrong in a way that looks right.
**Shape:** a fixture row whose correct output you fix in advance, plus a row that must NOT match.
*Origin: a plan-status tool special-cased an id prefix instead of dispatching on structure — it
fixed four rows and silently broke two.*

## ⛔ The cross-cutting failure: liveness is not completeness

The most common defect **in the guards themselves**.

```python
found = scan_for_literals(tree)
assert found, "the scan broke"      # ← liveness. Catches TOTAL breakage only.
```

That assertion fires when the scan finds *nothing*. It cannot fire when the scan finds *most*
things — which is the real case: one call site becomes a variable, a computed key, an f-string,
while the rest stay literals. The scan returns a plausible non-empty set and reports success.

*Measured in one repo: of four AST-based guards, two asserted liveness and two asserted nothing.
None asserted completeness. The consequence was a real hole — an output-affecting flag read via a
non-literal key was invisible to the completeness scan built to find exactly that.*

✅ **Assert completeness, or fail on the thing you cannot analyse:**

```python
for node in walk(tree):
    if is_the_call(node):
        if not isinstance(node.key, ast.Constant):
            pytest.fail(f"{loc(node)}: non-literal key — this guard cannot see it. "
                        f"Make it a literal, or register it explicitly.")
```

⭐⭐ **The irony worth remembering: one audited repo had built pattern 3 — a guard whose entire
purpose is "a declared-but-unimplemented check must be loud, not silent" — and four of its own AST
guards had that exact bug.** The lesson had been learned in one place and never generalised.
**When you write a guard, ask what it does when it cannot see.**

## Mutation-test every guard

Non-negotiable, and doubly so after any change to the guard's own parsing. See
`drift-protection.md`. Each mutation should fail **exactly one** assertion: none means the guard is
decorative, several means your assertions overlap and a real failure will be unreadable.

## What to guard, and what not to

⛔ **Do not aim for full coverage.** Guarding everything produces brittle tests over prose that
legitimately changes, and the maintenance cost lands on exactly the files people edit most.

Guard a doc when it has at least one of:
- a **number or name that also exists in code** (patterns 1, 2)
- a **copy** of something maintained elsewhere (pattern 4)
- **structural rules** you rely on (pattern 5)
- a **tool that reads it** (pattern 6)

Leave alone: narrative, rationale, model references, session notes, anything with no machine-
checkable counterpart. *In one repo this came to 8 documents guarded and 16 deliberately not —
and the split was right.*

⚠️ Reachability is the cheap exception: even an unguarded doc should be **named by the index**, or
nobody will find it. That is one line, not a test per file.
