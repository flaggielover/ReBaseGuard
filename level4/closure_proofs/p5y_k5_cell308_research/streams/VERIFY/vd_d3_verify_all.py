"""Stream D, D3: verify every stored C1b certificate with the independent verifier.

For each certs/CERT_*.json: (1) rebuild W from the raw C1b layout with vd_adapt (W = (1 + eta_W) * raw) and check it
equals the producer's pre-scaled strips exactly; (2) check the file's body sha256; (3) run vd_verify.verify at the
certificate's own drift; (4) check W(a) == the producer's A_bar exactly.  Output: results/D3_VERIFY_ALL.json.
Imports: stdlib, the quarantine module, vd_verify, vd_adapt.  No certifier module.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_verify as V  # noqa: E402
import vd_adapt as AD  # noqa: E402

Q = V.Q


def body_sha(cert: dict) -> str:
    body = {k: cert[k] for k in ("format", "drift", "BW", "strips", "W_at_atom_producer", "c1b_raw")}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main(paths, tighten=F(0), workers=3, opts_extra=None):
    out = []
    for path in paths:
        Q.guard_path(path)
        cert = json.loads(Path(path).read_text())
        e = F(cert["drift"])
        Q.guard_drift(e)
        W_adapt = AD.from_c1b_raw(cert["c1b_raw"])
        W_stored = V.StripPW.from_json(cert)
        same = W_adapt.polys == W_stored.polys and W_adapt.BW == W_stored.BW
        r = V.verify(W_adapt, e, workers=workers, opts={"tighten_below": tighten, "tighten_min_width": F(1, 2 ** 10),
                                                         **(opts_extra or {})})
        tight = None   # a full margin-bracket pass is infeasible on flat residuals (see VERIFIER_REPORT.md)
        Abar = F(cert["W_at_atom_producer"])
        rec = {"file": Path(path).name, "drift": cert["drift"], "degree": cert["producer"]["degree"],
               "file_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
               "body_sha256_recomputed": body_sha(cert), "body_sha256_stored": cert["sha256_body"],
               "body_sha_ok": body_sha(cert) == cert["sha256_body"],
               "adapter_equals_stored_prescaled": same,
               "verdict": r["verdict"], "expected": "PASS",
               "W_at_atom_verifier": r["W_at_atom"], "A_bar_producer": Abar,
               "W_at_atom_equals_A_bar_exactly": r["W_at_atom"] == Abar,
               "min_margin_lower_bound": r["min_margin_lower_bound"],
               "min_residual_upper_bound": r["min_residual_upper_bound"],
               "min_residual_upper_bound_at": r["min_residual_upper_bound_at"],
               "W_min_lower_bound": r["W_min_lower_bound"],
               "boxes": r["residual_bb"]["boxes"], "seconds": r["seconds"], "sha256_W": r["sha256_W"],
               "producer_eta_W": cert["producer"]["eta_W"], "margin_bracket_pass": tight, "workers": workers,
               "opts_extra": {k: str(v) for k, v in (opts_extra or {}).items()},
               "n_undecided": r["residual_bb"].get("n_undecided", 0)}
        rec["control_pass"] = (rec["verdict"] == "PASS" and rec["W_at_atom_equals_A_bar_exactly"] and same
                               and rec["body_sha_ok"])
        print(json.dumps(V.jsonable({k: rec[k] for k in ("file", "verdict", "W_at_atom_equals_A_bar_exactly",
                                                           "adapter_equals_stored_prescaled", "boxes", "seconds")})),
              flush=True)
        out.append(rec)
    return out


if __name__ == "__main__":
    paths = sorted(str(p) for p in (HERE / "certs").glob("CERT_*.json"))
    tighten = F(sys.argv[1]) if len(sys.argv) > 1 else F(0)
    Q.log_event("streams/VERIFY/vd_d3_verify_all.py", "D3 independent verification of stored C1b whole-kernel "
                "supersolution certificates at declared non-target drifts", klass="NONTARGET_DRIFT_VALIDATION",
                agent="streamD")
    t0 = time.time()
    res = main(paths, tighten)
    doc = {"schema": "VD_D3/1", "tighten_below": tighten, "results": res,
           "all_pass": all(r["control_pass"] for r in res), "seconds": round(time.time() - t0, 1)}
    (HERE / "results" / "D3_VERIFY_ALL.json").write_text(json.dumps(V.jsonable(doc), indent=1, sort_keys=True) + "\n")
    print("ALL_PASS", doc["all_pass"])
