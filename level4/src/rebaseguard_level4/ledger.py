"""Scientific result ledger.

Every Level 4 statement carries exactly one status.  The statuses are ordered by
how much they license you to say, and the *upgrade rule* is one-directional:

    FROZEN-PROVED      machine-checked in Lean (Level 1-3).           immutable
    FROZEN-CERTIFIED   enclosed by outward-rounded Arb (Level 1-3).   immutable
    RIGOROUS-CERTIFIED analytic lemmas + validated numerics in which
                       EVERY approximation between the true mathematical
                       object and the computed one is explicitly bounded.
    REPRODUCED         a frozen/historical number re-obtained here
                       with recorded seeds and code.
    METHOD-DEFINITION  a definition this work introduces (a policy or
                       protocol). True by construction, so it is neither
                       proved nor measured -- but it IS falsifiable in the
                       sense that it must be well-posed and outcome-blind.
    NEW-NUMERICAL      a new Monte Carlo result of this work (exploratory).
    CONFIRMATORY-NUMERICAL
                       a Monte Carlo result from a PREREGISTERED confirmatory
                       experiment: hypothesis, margin, estimator, shift set and
                       decision rule were all frozen, and the seeds were new,
                       before any outcome was generated. Still Monte Carlo --
                       it is never RIGOROUS-CERTIFIED.
    CANDIDATE          a numerically located object that may not exist.
    FAILED-TO-REPRODUCE  a prior claim this work could not recover.
    OPEN               stated, not settled.
    BLOCKED            cannot proceed without resolving something.

NEW-NUMERICAL never becomes a theorem.  ``Ledger.add`` refuses theorem
vocabulary on any status weaker than FROZEN-PROVED, because the failure mode
this guards against is not malice but drift: a phrase that starts as "suggests"
and ends, six documents later, as "shows".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

STATUSES = (
    "FROZEN-PROVED",
    "FROZEN-CERTIFIED",
    "RIGOROUS-CERTIFIED",
    "REPRODUCED",
    "METHOD-DEFINITION",
    "NEW-NUMERICAL",
    "CONFIRMATORY-NUMERICAL",
    "CANDIDATE",
    "FAILED-TO-REPRODUCE",
    "OPEN",
    "BLOCKED",
)

# Statuses whose statements are allowed to use proof vocabulary.  Everything
# else is guarded, because the failure mode is drift: a phrase that starts as
# "suggests" ends, six documents later, as "shows".
PROOF_STATUSES = ("FROZEN-PROVED", "FROZEN-CERTIFIED", "RIGOROUS-CERTIFIED")

_THEOREM_WORDS = re.compile(
    r"\b(proved|proven|proof|theorem|qed|establishes that|we prove|"
    r"rigorously shows?|certified)\b",
    re.IGNORECASE,
)


@dataclass(slots=True)
class LedgerEntry:
    id: str
    statement: str
    status: str
    evidence: list[str] = field(default_factory=list)
    notes: str = ""
    numbers: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "status": self.status,
            "evidence": self.evidence,
            "notes": self.notes,
            "numbers": self.numbers,
        }


class Ledger:
    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    def add(
        self,
        id: str,
        statement: str,
        status: str,
        *,
        evidence: Iterable[str] = (),
        notes: str = "",
        numbers: dict[str, Any] | None = None,
    ) -> LedgerEntry:
        if status not in STATUSES:
            raise ValueError(f"unknown status {status!r}; expected one of {STATUSES}")
        if any(e.id == id for e in self._entries):
            raise ValueError(f"duplicate ledger id {id!r}")
        if status not in PROOF_STATUSES:
            hit = _THEOREM_WORDS.search(statement)
            if hit:
                raise ValueError(
                    f"entry {id!r} has status {status} but its statement uses the "
                    f"proof word {hit.group(0)!r}; restate it as a numerical "
                    f"finding or cite the frozen entry that actually proves it"
                )
        entry = LedgerEntry(id, statement, status, list(evidence), notes,
                            dict(numbers or {}))
        self._entries.append(entry)
        return entry

    def entries(self) -> list[LedgerEntry]:
        return list(self._entries)

    def as_dict(self) -> dict[str, Any]:
        counts: dict[str, int] = {s: 0 for s in STATUSES}
        for entry in self._entries:
            counts[entry.status] += 1
        return {
            "schema": "rebaseguard-level4-ledger/1",
            "statuses": list(STATUSES),
            "counts": counts,
            "entries": [e.as_dict() for e in self._entries],
        }

    def to_markdown(self, title: str = "ReBaseGuard Level 4 — Result Ledger") -> str:
        lines = [
            f"# {title}",
            "",
            "Statuses are defined in `level4/src/rebaseguard_level4/ledger.py`.",
            "`NEW-NUMERICAL` and `CANDIDATE` entries are Monte Carlo findings and",
            "are **not** proofs. `FROZEN-*` entries are Level 1–3 results quoted",
            "here unchanged. `RIGOROUS-CERTIFIED` means the analytic lemmas are",
            "proved and **every** approximation between the true mathematical",
            "object and the computed one is explicitly bounded — not merely that",
            "interval arithmetic was used somewhere.",
            "",
            "| ID | Status | Statement | Evidence |",
            "|---|---|---|---|",
        ]
        for e in self._entries:
            evidence = "<br>".join(f"`{p}`" for p in e.evidence) or "—"
            statement = e.statement.replace("|", "\\|")
            lines.append(f"| `{e.id}` | **{e.status}** | {statement} | {evidence} |")
        notes = [e for e in self._entries if e.notes]
        if notes:
            lines += ["", "## Notes", ""]
            for e in notes:
                lines.append(f"- **`{e.id}`** — {e.notes}")
        return "\n".join(lines) + "\n"

    def write(self, json_path: Path, markdown_path: Path,
              title: str | None = None) -> None:
        import json

        json_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(self.as_dict(), indent=2))
        markdown_path.write_text(
            self.to_markdown() if title is None else self.to_markdown(title))
