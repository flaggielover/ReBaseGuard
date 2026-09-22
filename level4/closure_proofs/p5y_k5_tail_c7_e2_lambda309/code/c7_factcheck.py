"""C7 Phase 13 -- governance fact verification.

Purpose. This programme has repeatedly shipped statements its own tree contradicted: a repair
recorded as landed that had not (four times across C4/C5), and a reviewer's claim adopted unverified
and published false (C6, `subdivision_depth`). This module exists so that C7 does not do it again,
and so that any claim a REVIEWER makes is verified before it is absorbed rather than after.

It REFUSES rather than notes. Three independent checks:

  1. every number of >= 6 significant digits asserted in a prose file must occur in a committed JSON
     artifact -- prose may not carry a figure that no producer emitted;
  2. every baseline C7 quotes from a predecessor must match that predecessor's committed file exactly;
  3. artifact ordering against the gate must be reported truthfully, distinguishing the load-bearing
     certificate from analysis artifacts.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C

NUM = re.compile(r"(?<![\w.])(\d+\.\d{5,})(?![\w])")


def numbers_in(text: str) -> set[str]:
    return {m.group(1).rstrip("0").rstrip(".") for m in NUM.finditer(text)}


def flatten(o, acc: set[str]) -> None:
    if isinstance(o, dict):
        for v in o.values():
            flatten(v, acc)
    elif isinstance(o, list):
        for v in o:
            flatten(v, acc)
    else:
        s = str(o)
        acc.add(s)
        for m in NUM.finditer(s):
            acc.add(m.group(1).rstrip("0").rstrip("."))
        if isinstance(o, (int, float)):
            acc.add(f"{o:.15f}".rstrip("0").rstrip("."))


def main() -> int:
    findings: list[dict] = []

    # ---- check 1: prose figures must be backed by a producer ------------------------------------
    artifact_nums: set[str] = set()
    artifacts = sorted((C.NS / "evidence").rglob("*.json")) + [C.NS / "config" / "FEASIBILITY_GATES_C7.json"]
    for a in artifacts:
        flatten(json.loads(a.read_text()), artifact_nums)
    # exact rational values also count as backing, via their decimal expansion
    # Match by ROUNDING, not by string prefix. Prefix matching is unsound in the direction that
    # matters: it accepts a corrupted long number whenever a shorter truncation of the true value is
    # a prefix of it, so "3.297250999" would be waved through by the presence of "3.29725". A prose
    # figure is backed iff some artifact value rounds to it AT THE PRECISION THE PROSE QUOTES, which
    # permits honest rounding of a longer value and nothing else.
    art_vals = []
    for q in artifact_nums:
        try:
            art_vals.append(F(q))
        except (ValueError, ZeroDivisionError):
            pass

    def backed_by_rounding(n: str) -> bool:
        dec = len(n.split(".")[1])
        tol = F(1, 2 * 10 ** dec)
        target = F(n)
        return any(abs(v - target) <= tol for v in art_vals)

    prose = sorted(C.NS.rglob("*.md"))
    for p in prose:
        for n in sorted(numbers_in(p.read_text())):
            backed = backed_by_rounding(n)
            if not backed:
                findings.append({"check": "PROSE_FIGURE_UNBACKED", "file": str(p.relative_to(C.NS)),
                                 "value": n,
                                 "detail": "asserted in prose but emitted by no committed producer"})

    # ---- check 2: predecessor baselines must match their source files ----------------------------
    c4, c5 = C.c4_cell309(), C.c5_critical_a0()
    cert = C.load(C.NS / "evidence" / "certificate" / "C7_CERTIFICATE.json")
    expect = {
        "C4 floor": (cert["baseline_C4"]["float"], c4["lower_bound_float"]),
        # these are stored as EXACT rationals in the certificate; compare via Fraction, not via a
        # float() that would raise on "a/b" -- the comparison must not be weakened to string equality
        "C5-T critical A0": (float(F(cert["phase10_downstream_feasibility"]["critical_A0_C5T"])),
                             c5["critical_A0_C5T"]),
        "certified A0 at 309": (float(F(cert["phase11_family_exhaustion"]["certified_A0_at_309"])),
                                c4["A0_certified_float"]),
        "model sha256": (cert["model_sha256"], C.sha256_file(C.MODEL)),
    }
    for name, (claimed, actual) in expect.items():
        if claimed != actual:
            findings.append({"check": "BASELINE_MISMATCH", "name": name,
                             "claimed": claimed, "actual_in_source": actual})

    # ---- check 3: artifact ordering against the frozen gate --------------------------------------
    gate_rel = "level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/config/FEASIBILITY_GATES_C7.json"
    order = C.git("log", "--format=%H", "--reverse").splitlines()

    def first_commit(rel: str) -> str | None:
        out = C.git("log", "--format=%H", "--diff-filter=A", "--", rel).splitlines()
        return out[-1] if out else None

    gate_c = first_commit(gate_rel)
    gi = order.index(gate_c) if gate_c in order else -1
    ordering = []
    for rel, kind in (("evidence/certificate/C7_CERTIFICATE.json", "LOAD_BEARING"),
                      ("evidence/phase1/C7_LEDGER.json", "ANALYSIS"),
                      ("evidence/mutations/C7_MUTATIONS.json", "ANALYSIS"),
                      ("evidence/b0/C7_B0_AUDIT.json", "STATE_AUDIT")):
        full = f"level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/{rel}"
        c = first_commit(full)
        ai = order.index(c) if c in order else -1
        rel_pos = ("AFTER_GATE" if ai > gi else "SAME_COMMIT_AS_GATE" if ai == gi else "BEFORE_GATE")
        ordering.append({"artifact": rel, "kind": kind, "position": rel_pos})
        if kind == "LOAD_BEARING" and rel_pos != "AFTER_GATE":
            findings.append({"check": "GATE_ORDERING", "artifact": rel,
                             "detail": f"load-bearing artifact is {rel_pos}, must be AFTER_GATE"})

    # ---- check 4: every evidence artifact's self-sha must match its own content ------------------
    for a in sorted((C.NS / "evidence").rglob("*.json")):
        obj = json.loads(a.read_text())
        if "sha256" not in obj:
            continue
        body = {k: v for k, v in obj.items() if k != "sha256"}
        if C.sha256_obj(body) != obj["sha256"]:
            findings.append({"check": "SELF_SHA_MISMATCH", "file": str(a.relative_to(C.NS))})

    out = {
        "schema": "C7_HANDOVER_FACT_VERIFICATION/1",
        "purpose": ("verify C7's own claims, and any claim a reviewer makes, against the committed "
                    "tree BEFORE absorbing them"),
        "artifacts_scanned": [str(a.relative_to(C.NS)) for a in artifacts],
        "prose_scanned": [str(p.relative_to(C.NS)) for p in prose],
        "gate_ordering": ordering,
        "gate_ordering_note": (
            "The LOAD-BEARING artifact is the certificate, and it is AFTER the gate, which is the "
            "requirement that matters. The ledger landed in the SAME COMMIT as the gate and was in "
            "fact produced BEFORE it in wall-clock order. That is disclosed here and in the gate's "
            "own disclosure_of_non_blindness section rather than presented as a clean freeze."),
        "findings": findings,
        "FACT_CHECK_CLASS": "PASS" if not findings else "REFUSE",
    }
    p = C.NS / "evidence" / "governance" / "HANDOVER_FACT_VERIFICATION.json"
    s = C.write_evidence(p, out)
    print(f"FACT_CHECK_CLASS = {out['FACT_CHECK_CLASS']}   findings = {len(findings)}")
    for f_ in findings:
        print(f"  {f_['check']:<24} {json.dumps({k: v for k, v in f_.items() if k != 'check'})[:110]}")
    print("\ngate ordering:")
    for o in ordering:
        print(f"  {o['kind']:<14} {o['position']:<22} {o['artifact']}")
    print(f"\nwrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
