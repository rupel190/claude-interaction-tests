# Doc guards — what a machine CAN check

Probes measure whether documentation **fires**. Guards check the properties a machine can verify
on every commit, so probe runs stay rare. They are complementary and the division is clean:

```
guard   cheap, every commit, mechanical    "is this property still true?"
probe   costly, occasional, judgement      "does an agent recall this?"
```

⛔ **Neither substitutes for the other.** A guard cannot tell you an entry is phrased too narrowly
to fire; a probe cannot run on every push.

## The eight patterns

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

### 7. Cross-boundary freshness (**staleness must announce itself**)
**Catches:** a decision made outside the repo — in a notes vault, a ticket, a meeting write-up —
that never arrived, in the window where an agent will confidently reason past it.
**Shape:** the inbound log carries a `last synced from <source>: <date>` line. The guard compares
it to the newest artefact on the other side and fails when the source is ahead. It cannot tell you
*what* is missing; it makes "something may be" a stated fact instead of a silence.
*Origin: a client meeting reversed a documented direction and the repo never heard. Probed six days
later, an agent listed the settled decision as the first thing to go and decide.*

⭐ **This is the one guard whose value is a hedge rather than a fact.** Everything else here
asserts a property is still true. This one converts an invisible gap into an audible *"I may be
working from a stale picture"* — which is the difference between the safe and expensive failure
shapes in `probes.md` § *Not every miss costs the same*.

⚠️ It needs the boundary to be enumerable — one vault folder, one label, one directory. If
"outside" has no address, this guard cannot be written, and that is itself worth knowing before
you rely on the transport.

### 8. Declared boundary ↔ actual index (**the ignore file is intent, not reality**)
**Catches:** knowledge quietly excluded from version control, and excluded material quietly
tracked. Both are the same defect — a boundary that is *declared* and never *compared to reality*.
**Shape:** two directions, and you need both.

```bash
# A — tracked DESPITE matching an ignore rule.  Exact; git has it built in.
git ls-files -i -c --exclude-standard

# B — knowledge sitting inside a fully-ignored tree.  Heuristic; scope it (below).
fd -e md -t f . --no-ignore --exclude .git | while read -r f; do
  git check-ignore -q "$f" && ! git ls-files --error-unmatch "$f" >/dev/null 2>&1 && echo "$f"
done
```

*Origin: one session, both directions, three repos. A found 47 files tracked under an ignore rule
added five months after them, and 1 more elsewhere. B found the **author's own fix from that same
session** — a defect correction written into a file inside the ignored tree, with a commit message
asserting the fix while git held no record of it.*

⭐ **The fix for an accepted exception is to DECLARE it, never to silence the check.** Both hits
above were legitimate; the problem was that the exception lived only in the index. Writing it into
the ignore file makes the file describe what is true and returns the check to empty — which is the
same move as declaring an authority instead of letting it be inferred.

⛔ **Two mechanics that will waste your afternoon:**

- **`git check-ignore -v <file>` reports NO RULE for a tracked file** and exits 1 — git's model is
  that ignore rules do not apply to tracked files. So the obvious way to diagnose a direction-A hit
  says "nothing matches" and reads exactly like a broken guard. Use `--no-index` to see the rule.
- **You cannot re-include a file whose parent DIRECTORY is excluded.** `Images/` + `!Images/Samples/`
  silently does nothing. It has to be `Images/*` + `!Images/Samples/`, and the difference is
  invisible until you test it.

⚠️ **Direction B over-fires unless you scope it**, because generated output is markdown too. Run it
raw and you get every `comparison_report.md` under `tests/output/`. Exclude the regenerable trees
first, or it produces noise and gets switched off — which is the failure mode this whole file is
about. Direction A needs no scoping and is worth wiring up on its own.

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

### ⚠️ "Fail on what you cannot see" is too blunt — classify first

The first attempt at this fix failed on *every* non-literal, and it was wrong. Scanning for
declared values, three cases look identical to a bare `isinstance` check and are not:

| the site | example | what it means | do |
|---|---|---|---|
| **literal** | `precision=4` | a declared value | collect it |
| **forwarding** | `precision=self.precision` | declares **nothing** — passes one through | skip; there is nothing to miss |
| **computed** | `precision=f(x)`, an f-string, a conditional | a declared value the scan **cannot read** | ⛔ fail, with the line |

⛔ **Failing on forwarding makes the guard unusable** — every wrapper and every constructor forwards
— and the usual response is to loosen it back to silence. The distinction between *"a value I cannot
read"* and *"no value here at all"* is what makes a loud guard survivable.

### The declaration hatch: legal invisibility that still gets checked

Some indirection is legitimate (a helper resolving several keys through one parameter). The hatch
that works has three parts, and the second is what stops it becoming a hole:

1. **Declare** the file and **what it reads** — an allowlist entry, not a blanket exemption.
2. ⭐ **Check the declared names anyway**, against the same registry every visible name is checked
   against. Declaring something cannot exempt it from the actual rule; it only exempts it from
   being *seen* automatically.
3. ⭐ **Fail on a stale declaration** — if the file no longer has an unresolvable site, the entry
   must go. An allowlist that outlives its reason quietly widens what the guard permits, and
   nothing else will ever notice.

### ⭐ Guards catch each other — build the network, not the guard

Registering the two newly-visible switches immediately failed a *different* guard, one requiring
every value-carrying switch to name the code that consumes it. Nothing had connected those two
tests; the second simply refused to let a switch exist without a consumer.

**A guard network has emergent coverage a single guard cannot.** When adding one, check what else
goes red — that is the network telling you what your change actually means, and it is usually the
cheapest review you will get.

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
