"""QC14' (rev. 2c): the full Stage-2 pipeline on MANUFACTURED consumer inputs with REAL decoy SRK certificates.

Replaces rev. 2b QC14 (a historical rehearsal on a quarantined tail cell), which the quarantine forbids before a grant.  Nothing
here reads a tail-cell input: the consumer inputs are manufactured (seeded, TC-T-shaped, clearly non-target values),
the SRK certificates are the committed research certificates of the declared out-of-band real-kernel decoy cell
(SRK_DECOY_DECLARATION_A2: h = 5, k = 1/2, C = [1/2, 37/72]), verified in-process by the pinned band-scoped verifier.

Checks (all must hold):
  R1 the pinned tct_rule enclosure equals its own crosscheck on the manufactured inputs;
  R2 EMPTY GateResult: the SRK enclosure equals the TC-T enclosure exactly (reproduction gate) and the shim-injected
     pinned direct() gives exactly the Gamma of the unchanged pinned direct() (injection equivalence, U2 check U4(i));
  R3 GATE result from the decoy certificates: the SRK enclosure lies inside the TC-T enclosure and Gamma_SRK <= Gamma_TCT;
  R4 S composition: fallback (None / CERTIFICATION_FAILED) gives S_I1; a certified RLR cell gives the componentwise min,
     equal to the RLR307 independent reconstruction;
  R5 binding refusals: a GateResult for another cell, and a verifier id other than the pinned one, are refused.
"""
from __future__ import annotations

import json
import random
from fractions import Fraction as F
from pathlib import Path

import p309_driver as D

DECOY_CELL = (F(1, 2), F(37, 72))
DECOY_FILES = [f"evidence/srk_decoys_cell/cell_h5_k1_2_C1_2_37_72_S{j}.json" for j in range(4)]


def manufactured(seed: int = 20260930, rho: F = (DECOY_CELL[1] - DECOY_CELL[0]) / 2) -> dict:
    rng = random.Random(seed)

    def R(lo=1, hi=1000, den=1000):
        return F(rng.randint(lo, hi), rng.randint(1, den))
    meas = {"schema": "MANUFACTURED_TCT_SHAPED/1", "cell": "MANUFACTURED", "rho": D.fs(rho),
            "norms": {"k": [D.fs(R(1, 3)) for _ in range(5)], "j": [D.fs(R(1, 3)) for _ in range(5)]},
            "sup_S0": [D.fs(R(1, 50)) for _ in range(5)], "r": {}, "W2": {}}
    for r in range(5):
        a = R(-5000, 5000)
        meas["r"][str(r)] = {"sup": {x: D.fs(R()) for x in ("F", "D", "H")},
                             "delta_F": D.fs(R(1, 10) / 10 ** 6), "delta_D": D.fs(R(1, 10) / 10 ** 6),
                             "delta_H": D.fs(R(1, 10) / 10 ** 6),
                             "eps_src": [D.fs(R(1, 10) / 10 ** 7) for _ in range(4)],
                             "H_at_a": [D.fs(a), D.fs(a + R(1, 10) / 10 ** 6)]}
    for t in range(1, 5):
        for r in range(t):
            a = R(-100, 100)
            meas["W2"][f"{r}:{t - r - 1}"] = [D.fs(a), D.fs(a + R(1, 10) / 10 ** 5)]
    cs = {f"h:{j}:3": D.fs(R(1, 100)) for j in range(1, 5)}
    cs.update({"Sclosed:0:3": D.fs(R(1, 100)), **{f"S:{r}:3": D.fs(R(1, 100)) for r in range(1, 5)}})
    me = {f"h:{j}:3": D.fs(R(1, 10) / 10 ** 6) for j in range(1, 5)}
    me.update({"Sclosed:3": D.fs(R(1, 10) / 10 ** 6), **{f"S:{r}:3": D.fs(R(1, 10) / 10 ** 6) for r in range(1, 5)}})
    aux = {"candidate_suprema": cs, "midpoint_eps": me}
    A = {"A0": R(1, 50), "A1": R(1, 200), "A2": R(1, 2000)}
    e0 = (DECOY_CELL[0] + DECOY_CELL[1]) / 2
    ad = {"R2_interval": {"lo": D.fs(R(-3000, -1)), "hi": D.fs(R(1, 3000))}, "M_R2": D.fs(R(1, 3000)),
          "R_interval": {"lo": D.fs(-R(1, 9)), "hi": D.fs(-R(1, 9))}, "D_interval": {"lo": D.fs(R(1, 9)),
                                                                                   "hi": D.fs(R(10, 19))}}
    cov = {"e0": D.fs(e0), "rho": D.fs(rho), "left": D.fs(DECOY_CELL[0]), "right": D.fs(DECOY_CELL[1])}
    return {"meas": meas, "aux": aux, "A": A, "ad": ad, "cov": cov}


def decoy_gate(verifier_id: str):
    """GateResult of the declared decoy cell from its committed certificates, verdicts in-process by the pinned
    band-scoped verifier (N = 8, max_depth = 24)."""
    import importlib.util
    import srk_gate as GT
    certs = []
    for rel in DECOY_FILES:
        d = json.loads((D.E.RNS / rel).read_text())
        certs.extend(c for c in d["certificates"].values() if c.get("status") == "CERTIFIED")
    vs = importlib.util.spec_from_file_location("srk_verify_indep_scoped", str(D.REPO / D.VARIANT_REL))
    V = importlib.util.module_from_spec(vs)
    vs.loader.exec_module(V)
    verdicts, source = GT.verdicts_from_verifier(certs, V, None, N=D.VERIFIER_N, max_depth=D.VERIFIER_DEPTH)
    if source != verifier_id:
        raise D.Refusal("VERIFIER", "the in-process verifier is not the pinned one")
    gr = GT.gate(DECOY_CELL[0], DECOY_CELL[1], dict(D.GEOMETRY), "whole", certs, verdicts, verdict_source=source)
    return gr, {"certificates": len(certs), "verdicts": sorted(set(verdicts.values()))}


def rehearse(con: dict, m: dict, verifier_id: str, seed: int = 20260930) -> dict:
    import srk_adapter as AD
    import srk_gate as GT
    D.E.log("code/p309_rehearse.py", "QC14' rehearsal: Stage-2 pipeline on manufactured inputs + decoy certificates",
            klass="SYNTHETIC", drifts=[[D.fs(DECOY_CELL[0]), D.fs(DECOY_CELL[1])]],
            notes="manufactured consumer inputs (seeded); committed out-of-band decoy certificates; no tail input read")
    mf = manufactured(seed)
    ci = {"meas": mf["meas"], "aux": mf["aux"], "ad": mf["ad"], "cov": mf["cov"]}
    T, R, C2F = con["T"], con["R"], con["C2F"]
    A = mf["A"]
    lo, hi, _ = T.tail_enclosure(R, ci["meas"], ci["aux"], A, 5, None)
    checks = {"R1_tct_crosscheck": (lo, hi) == T.tail_enclosure_crosscheck(ci["meas"], ci["aux"], A, 5, None)}
    empty = GT.GateResult.empty(DECOY_CELL[0], DECOY_CELL[1], dict(D.GEOMETRY), (1, 2, 3, 4))
    e = D.evaluate_srk(con, ci, A, DECOY_CELL, empty, verifier_id)
    base = C2F.direct(T, R, ci["meas"], ci["aux"], A, ci["ad"], ci["cov"], con["KM"])
    checks["R2_empty_reproduces_tct"] = [F(x) for x in e["H_SRK_exact"]] == [lo, hi]
    checks["R2_injection_equivalence"] = F(e["Gamma_exact"]) == base["Gamma"] and F(e["M_after_exact"]) == base["M"]
    gr, ginfo = decoy_gate(verifier_id)
    s = D.evaluate_srk(con, ci, A, DECOY_CELL, gr, verifier_id)
    sl, sh = (F(x) for x in s["H_SRK_exact"])
    checks["R3_srk_inside_tct"] = lo <= sl and sh <= hi
    checks["R3_gamma_dominance"] = F(s["Gamma_exact"]) <= base["Gamma"]
    checks["R3_gate_source_GATE"] = gr.source == "GATE"
    ind = D._ind() or D.load_rlr307(m)["rlr307_independent"]
    S_fb = D.compose_S(A, None)
    S_fail = D.compose_S(A, {"cell": {"status": "CERTIFICATION_FAILED"}})
    big = {"cell": {"status": "CERTIFIED", "A1_SUPPLY_max": D.fs(A["A1"] * 2), "A2_SUPPLY_max": D.fs(A["A2"] * 2)}}
    small = {"cell": {"status": "CERTIFIED", "A1_SUPPLY_max": D.fs(A["A1"] / 3), "A2_SUPPLY_max": D.fs(A["A2"] / 5)}}
    checks["R4_fallback_is_S_I1"] = S_fb == A and S_fail == A
    checks["R4_min_composition"] = (D.compose_S(A, big) == A and D.compose_S(A, small) == ind.consumed(
        A, {"A1_SUPPLY": small["cell"]["A1_SUPPLY_max"], "A2_SUPPLY": small["cell"]["A2_SUPPLY_max"]}))
    refusals = {}
    other = GT.GateResult.empty(F(1, 4), F(9, 32), dict(D.GEOMETRY), (1, 2, 3, 4))
    for name, (cell, g, vid) in {"other_cell": (DECOY_CELL, other, verifier_id),
                                 "other_verifier": (DECOY_CELL, gr, "sha256:" + "0" * 64)}.items():
        try:
            D.evaluate_srk(con, ci, A, cell, g, vid)
            refusals[name] = False
        except AD.AdapterRefusal:
            refusals[name] = True
    checks["R5_binding_refusals"] = all(refusals.values())
    return {"mode": "rehearse", "pass": all(checks.values()), "checks": checks, "refusals": refusals,
            "decoy_gate": {"source": gr.source, "certificates": ginfo["certificates"], "verdicts": ginfo["verdicts"]},
            "manufactured_seed": seed, "note": "manufactured values and decoy certificates only; no tail input read"}
