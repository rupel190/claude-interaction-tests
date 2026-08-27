"""Template: pin the STRUCTURAL properties of a Claude-facing documentation index.

Copy into the project's test suite and adjust the constants below. This guards the properties an
interaction test is too slow to check on every commit — but it cannot check the one that matters
most (whether a row is phrased generically enough to FIRE). Keep both.

⛔ Mutation-test every assertion after copying, and again after any change to `_rows()`:
   inject the violation, confirm the right assertion fails, restore. A guard that has quietly
   stopped biting is worse than no guard, and a scoping change is where that happens.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---- adjust for your project -------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
INDEX_FILE = ROOT / "CLAUDE.md"
FINDINGS_DIR = ROOT / "docs" / "FINDINGS"
INDEX_HEADING = "## ⛔ ALREADY TRIED"
TABLE_HEADER = "| already tried"
VERDICT_MARKERS = ("⛔", "✅", "⚠️", "⭐")
RULE_CLAUSES = ["CLASS, not your instance", "verdict in the row", "No measurements",
                "CORRECT IT IN PLACE"]
# Measurements, after inline-code spans (which hold identifiers like `flat3x3`) are stripped.
MEASUREMENT = re.compile(r"\d+\s*(?:×|%|/\s*\d+|–\s*\d+|mm\b|st/cm)")
# ------------------------------------------------------------------------------


def _index_block() -> str:
    text = INDEX_FILE.read_text(encoding="utf-8")
    assert INDEX_HEADING in text, f"{INDEX_FILE.name} has lost its {INDEX_HEADING!r} section"
    rest = text[text.index(INDEX_HEADING) + len(INDEX_HEADING):]
    nxt = rest.find("\n## ")
    return rest[:nxt] if nxt != -1 else rest


def _rows() -> list[str]:
    """Only the closed-work table — any other list in the block is a different kind of thing."""
    block = _index_block()
    start = block.index(TABLE_HEADER)
    return [
        ln for ln in block[start:].splitlines()
        if ln.startswith("| ") and not ln.startswith("|---") and TABLE_HEADER not in ln
    ]


def test_the_index_still_has_rows() -> None:
    assert len(_rows()) >= 5, "the index has been gutted"


@pytest.mark.parametrize("clause", RULE_CLAUSES)
def test_the_maintenance_rule_survives(clause: str) -> None:
    """Without the rule, the next session writes task-specific rows that never fire again."""
    assert clause in _index_block(), f"the index's maintenance rule has lost: {clause!r}"


def test_every_row_carries_its_own_verdict() -> None:
    """The pull is the unreliable step, so a row must stop a rebuild on its own."""
    naked = [r for r in _rows() if not any(m in r for m in VERDICT_MARKERS)]
    assert not naked, "rows useless to an agent that does not open the file:\n" + "\n".join(naked)


def test_no_row_restates_a_measurement() -> None:
    """Numbers belong in the findings file or in code, once. Two copies always drift."""
    bad = []
    for row in _rows():
        hits = MEASUREMENT.findall(re.sub(r"`[^`]*`", "", row))
        if hits:
            bad.append(f"{hits} in: {row[:110]}")
    assert not bad, "measurements restated in the index:\n" + "\n".join(bad)


def test_every_findings_file_is_reachable() -> None:
    """A findings file nobody links to is invisible to every future session."""
    if not FINDINGS_DIR.is_dir():
        pytest.skip("no findings dir yet")
    block = _index_block()
    orphans = [p.name for p in sorted(FINDINGS_DIR.glob("*.md")) if p.name not in block]
    assert not orphans, f"unreachable findings files: {orphans}"


def test_declined_rows_state_what_would_reopen_them() -> None:
    """A decision with no reopen condition reads as permanent when it was contingent."""
    bad = [r for r in _rows() if "DECLINED" in r.upper() and "reopen" not in r.lower()]
    assert not bad, "declined rows with no reopen condition:\n" + "\n".join(bad)


def test_no_pointer_targets_a_missing_file() -> None:
    refs = set(re.findall(r"`((?:docs|\.)/[\w/.-]+\.md)`", _index_block()))
    missing = sorted(r for r in refs if not (ROOT / r).exists())
    assert not missing, f"the index points at files that do not exist: {missing}"
