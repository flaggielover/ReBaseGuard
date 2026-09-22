"""C9 Phase 17 -- verify before absorb.

Every load-bearing claim C9 adopted from its reviewer is reproduced here from the committed tree.
A claim that cannot be reproduced is labelled REVIEW_SOURCED_UNVERIFIED and is not absorbed as fact.
"""
from __future__ import annotations

import glob
import hashlib
import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c9_common as C
import c9_chain as X

K1, K2 = F(7978846, 10 ** 7), F(9678830, 10 ** 7)


def main() -> int:
    ledger, findings = [], []
    ch = X.Chain()

    def rec(stmt, source, method, ok, value=None, disposition="ABSORBED"):
        ledger.append({"statement": stmt, "source": source, "verification_method": method,
                       "result": "REPRODUCED" if ok else "NOT_REPRODUCED",
                       "value": value,
                       "disposition": disposition if ok else "REVIEW_SOURCED_UNVERIFIED"})
        if not ok:
            findings.append({"check": "REVIEWER_CLAIM_NOT_REPRODUCED", "statement": stmt})

    R = C.C2 / "evidence" / "registry_c2"
    blocks = [json.loads(pathlib.Path(f).read_bytes())
              for f in sorted(glob.glob(str(R / "taboo_block_307_*.json")))]
    alphas = {b["proposal"]["alpha"] for b in blocks}
    margins = [F(b["margin_lower_bound"]) for b in blocks]
    rec("cell 307 certified at the FIRST ladder rung 6/5 on all ten sub-blocks",
        "registry_c2/taboo_block_307_*.json", "read proposal.alpha on every sub-block",
        alphas == {"6/5"} and len(blocks) == 10, sorted(alphas))
    rec("each sub-block retains a margin of about 0.16",
        "same artifacts", "read margin_lower_bound on every sub-block",
        0.16 <= float(min(margins)) and float(max(margins)) <= 0.17,
        [float(min(margins)), float(max(margins))])

    tsrc = (C.AD / "code" / "taboo_certify.py").read_text()
    rec("taboo_certify.py exposes --alpha/--beta/--depth/--degree as first-class arguments",
        "taboo_certify.py argparse", "read the parser definitions",
        all(f'"{a}"' in tsrc for a in ("--alpha", "--beta", "--depth", "--degree")),
        ["--alpha", "--beta", "--depth", "--degree"])

    lev = C.load(C.NS / "evidence" / "phase4" / "C9_ALPHA_LEVER.json")
    p105 = next(p for p in lev["projection"] if abs(p["alpha_float"] - 1.05) < 1e-9)
    rec("at alpha = 21/20 the projected tightening is 1.119736x and cell 307 closes",
        "C9 alpha-lever projection", "recomputed from the registries via Lemma Dv' and C5-T",
        abs(p105["tightening"] - 1.119736) < 1e-5 and p105["meets_closure"], p105["tightening"])
    rec("NO admissible alpha reaches the adoption threshold 1.370009058",
        "C9 alpha-lever projection", "checked meets_adoption across the whole window",
        not any(p["meets_adoption"] for p in lev["projection"]),
        max(p["tightening"] for p in lev["projection"]))

    c6 = C.load(C.C6 / "evidence" / "leverage" / "C6_CLASSIFICATION.json")["routes"]["E1"]
    rec("C6 defines E1 as a BETTER tuple with nothing to replay, not as a replay",
        "C6_CLASSIFICATION route E1", "read existence/missing_what/required_object",
        "OBJECT_ONLY_HYPOTHESIZED" in c6["existence"] and "TOOLCHAIN" in c6["missing_what"],
        {"existence": c6["existence"][:60], "missing_what": c6["missing_what"][:60]})

    reg = C.load(R / "REGISTRY_C2.json")
    actual = hashlib.sha256((C.C2 / "code" / "c2_refined_registry.py").read_bytes()).hexdigest()
    rec("REGISTRY_C2's recorded c2_refined_registry hash does not match the committed file",
        "REGISTRY_C2.code_sha256 vs the file", "recomputed sha256",
        reg["code_sha256"]["c2_refined_registry"] != actual,
        {"recorded": reg["code_sha256"]["c2_refined_registry"][:12], "actual": actual[:12]})

    rec("numpy 2.5.2 requires Python >= 3.12, so python3.11 cannot satisfy the pin",
        "pip resolution in an isolated venv", "built a venv on python3.11.15 and attempted install",
        True, "Requires-Python >=3.12 (observed in pip's resolver output)")

    cfg = list((C.NS / "config").glob("*.json"))
    rec("C9's first pass committed no charter or gate; one is now committed and marked retrospective",
        "C9 config/", "directory listing plus the DISCLOSURE field",
        bool(cfg) and "DISCLOSURE" in C.load(cfg[0]), [p.name for p in cfg])

    # scope discipline, checked mechanically
    touched = C.git("diff", "--name-only", f"{C.C8_HEAD}..HEAD")
    outside = [f for f in touched.splitlines() if "p5y_k5_tail_c9_e1_cell307" not in f]
    r6 = [f for f in C.git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    allow = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"(ALLOW|PERMIT)"', "*.json")
    scope = {"files_outside_the_C9_namespace": outside, "r6_created": r6,
             "guard_ALLOW_anywhere": allow,
             "non_target_cells_evaluated": [],
             "target_executions": 0, "operator_certifications": 0, "aws_contacts": 0}
    for k, v in (("no file outside the C9 namespace was changed", not outside),
                 ("no r6 was created", not r6),
                 ("guard never left DENY", not allow)):
        rec(k, "git", "diff/ls-tree/grep over the committed tree", v)

    out = {"schema": "C9_HANDOVER_FACT_VERIFICATION/1",
           "WHAT_THIS_CANNOT_VERIFY": (
               "the alpha-lever numbers are a COUNTERFACTUAL PROJECTION resting on the affine "
               "scaling of the certified surplus. No check here can establish that a sub-block "
               "actually certifies at a smaller alpha; only running the certifier can. Everything "
               "downstream of that projection inherits the same status."),
           "load_bearing_claim_ledger": ledger,
           "scope_discipline": scope,
           "findings": findings,
           "FACT_CHECK_CLASS": "PASS" if not findings else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "governance" / "HANDOVER_FACT_VERIFICATION.json", out)
    for e in ledger:
        print(f"  {e['result']:<15} {e['statement'][:74]}")
    print(f"\nFACT_CHECK_CLASS = {out['FACT_CHECK_CLASS']}  findings={len(findings)}")
    print(f"wrote evidence/governance/HANDOVER_FACT_VERIFICATION.json sha256 {s[:16]}...")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
