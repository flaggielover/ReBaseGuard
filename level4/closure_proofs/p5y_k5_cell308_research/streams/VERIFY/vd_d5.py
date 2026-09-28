"""Stream D, D5 driver: float value iteration (vd_float) at the declared drifts vs the stored certificates.

For each drift: U_N(a) for N = 10, 20 and the h^2 Richardson value; for each certificate at that drift: W(a) - U_N(a)
and min over all N = 20 nodes of W(node) - U_20(node) (a supersolution must dominate the ARL function everywhere, up to
the float discretisation error).  NON-RIGOROUS cross-check.  Output: results/D5_FLOAT.json (validation-drift values:
latent proxies, kept in this stream's own files only).
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_float as FL  # noqa: E402
import vd_adapt as AD  # noqa: E402

Q = FL.Q


def work(e_str: str) -> dict:
    e = F(e_str)
    out, res = FL.run(e, Ns=(10, 20))
    r20 = res[-1]
    h = 1.0 / r20["N"]
    out["_nodes20"] = [(i * h, j * h, r20["_U"][idx]) for (i, j), idx in r20["_nodes"].items()]
    return out


if __name__ == "__main__":
    import multiprocessing as mp
    drifts = [F(3), F(7, 2), F(1), F(1, 2)]
    for e in drifts:
        Q.guard_drift(e)
    Q.log_event("streams/VERIFY/vd_d5.py", "D5 float value iteration of E_a[tau] at declared non-target drifts "
                "3, 7/2, 1, 1/2 and comparison with stored certificates", klass="NONTARGET_DRIFT_VALIDATION",
                agent="streamD")
    t0 = time.time()
    with mp.get_context("spawn").Pool(3) as pool:
        outs = pool.map(work, [str(e) for e in drifts])
    doc = {"schema": "VD_D5/1", "non_rigorous": True, "drifts": []}
    for e, o in zip(drifts, outs):
        nodes = o.pop("_nodes20")
        certs = []
        for d in (4, 6):
            path = HERE / "certs" / f"CERT_e{e.numerator}_{e.denominator}_d{d}.json"
            if not path.exists():
                continue
            W = AD.from_c1b_raw(json.loads(path.read_text())["c1b_raw"])
            Wa = float(W.at_atom())
            gaps = [float(W.value(F(p).limit_denominator(1000), F(m).limit_denominator(1000))) - u
                    for p, m, u in nodes]
            certs.append({"certificate": path.name, "W_at_atom": Wa,
                          "W_at_atom_minus_U10": Wa - o["levels"][0]["U_atom"],
                          "W_at_atom_minus_U20": Wa - o["levels"][1]["U_atom"],
                          "W_at_atom_minus_richardson": Wa - o["richardson_h2"],
                          "W_at_atom_ge_all_float_estimates": all(Wa >= x for x in (
                              o["levels"][0]["U_atom"], o["levels"][1]["U_atom"], o["richardson_h2"])),
                          "min_over_N20_nodes_W_minus_U20": min(gaps),
                          "relative_gap_at_atom_vs_richardson": (Wa - o["richardson_h2"]) / o["richardson_h2"]})
        o["certificates"] = certs
        doc["drifts"].append(o)
    doc["all_W_at_atom_ge_float"] = all(c["W_at_atom_ge_all_float_estimates"] for o in doc["drifts"]
                                        for c in o["certificates"])
    doc["seconds"] = round(time.time() - t0, 1)
    (HERE / "results" / "D5_FLOAT.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps(doc, indent=1))
