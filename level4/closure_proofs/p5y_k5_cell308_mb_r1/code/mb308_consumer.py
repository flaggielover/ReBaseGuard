"""Cell-308 MB campaign (r1) -- committed TC-T inputs, the two historical controls and Stage 2 (B5).

  * `load_consumer` / `cell_inputs` / `s_i1` / `control_ca`: C2's frozen consumer path from pinned bytes, exactly as
    the accepted cell-307 driver (rlr307_driver.load_consumer, cell_inputs, s_i1, control), re-targeted to cells
    305 (rehearsal) and 308 (target control). Control C-A: C2's committed record reproduced exactly under S_I1.
  * `control_cb`: control C-B, REPRODUCTION ONLY: stream ASSEMBLY's tptb_tail gates at s = rho (G-R1, G-R2, G-R3,
    G-R4(M), G-CF, the tpt profile at rho and the frozen penalty) with S_I1. Inside `guard.reproduction(...)` and
    with TRIPWIRES on every transport penalty (penalty_closed, penalty_c5t, penalty_blocked, the Riemann sums,
    tpt.evaluate, tptb_tail.evaluate_bundle / independent_penalty, F2's tptb / C5-T / endpoint rule): no new-route
    value (TPT, C5-T, TPT-B) is computed on the cell; the output is equality booleans only.
  * `stage2`: the target-mode entry (design 5.2): the same reproduction gates, then the C5 cell-identity gate,
    exact tiling of the block triples, the C6 per-piece emptiness refusal, tpt.penalty_blocked (P_B, primary), the
    stream-ASSEMBLY independent bracket G-T2, dominance P_B <= P_frozen(S_I1), and the F2 bracket [P_lo, P_hi]
    (hook; exact). Tripwires stay on penalty_closed / penalty_c5t / Riemann / evaluate: no other route's value.
    Gamma_dec = g_hi + max(P_B, P_hi); CLOSED iff Gamma_dec < 0 (exact).
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import json
import sys
import types
from fractions import Fraction as F
from pathlib import Path

CP = "level4/closure_proofs/"
FIELDS = ("A0", "A1", "A2")
ARGS = ("Abar", "tau", "C_T", "D_lo", "D1", "D2")
CONTROL_CELLS = (305, 308)

PINS = {
    "c2_forecast_code": (CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
                         "bd7854bce2434215c0a72eeb825ff87db4c729e80b0e4d125911e806a084f06b", "18403dbec855"),
    "tail_forecast_r2": (CP + "p5y_k5_m5_tail_closure/code/tail_forecast_r2.py",
                         "5ab31ae56c0174697a7f5805e212b46334803e9e3371a77f82871d60716b96cd", "edec817e57f1"),
    "tct_rule": (CP + "p5y_k5_m5_tail_closure/code/tct_rule.py",
                 "f5a343e7f7bfb742d0a41c38512e27e7311d0919b38bcea0dfe98775c73d9a3e", "98f6eee4d867"),
    "deflated_consume": (CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                         "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72", "a0a836fa83c6"),
    "adapter": (CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
                "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d", "0516a15b2d83"),
    "cells_json": (CP + "p5y_k1_cover_ledger_successor/config/cells.json",
                   "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f", "30e40fc0e721"),
    "record_manifest": (CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                        "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334", "e6e0e26e2583"),
    "adopted_inputs": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json",
                       "485fb1254e459683f48815c239d18d29119d651d0e77876f772c3fee9d29a37d", "0ba3c6dc876f"),
    "tct_inputs_305": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_305.json",
                       "e1390b427e5f7dcf2f997fe039ea3658554cba86f6e472f3c8f339ac0e93df76", "499ccafe5cc9"),
    "tct_inputs_308": (CP + "p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_308.json",
                       "386f4a7774d69b0c319918fc6f4aa010ae6a8c349fca941c24e13a2111c418c2", "866ddab11c9b"),
    "registry_c1": (CP + "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json",
                    "87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3", "f6d84bdb5ef0"),
    "registry_c2": (CP + "p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json",
                    "1b2b834939fcd80a81ddc8f029f46705b53cefeb46c0cc925a99c2b8e856fdd6", "1a3adfd3d893"),
    "c2_forecast": (CP + "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json",
                    "784f25eecd65bad3bf687727590a0c0e91a683c5d30817c3bda80d6f373fe983", "a191557f24c3"),
    "coverage_r5": (CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json",
                    "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c", "f978eeb6b411"),
    "floor_rule": (CP + "p5y_k5_tail_floor_r2/config/K5_TAIL_ADOPTION_FLOOR_R2.json",
                   "eb2b4196dd23a8353e25093ff6bfa30d18634dd7f52968ec3c7000ea9b624238", "0ddfac300b92"),
}
FORBIDDEN_IN_CONTROL = ("penalty_closed", "penalty_c5t", "penalty_riemann", "penalty_riemann_lower", "evaluate",
                        "penalty_blocked")
FORBIDDEN_IN_TARGET = ("penalty_closed", "penalty_c5t", "penalty_riemann", "penalty_riemann_lower", "evaluate")


class ConsumerRefusal(Exception):
    """Fail closed (before the marker: nothing consumed)."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


class Stop(RuntimeError):
    """A Stage-2 gate refused (after the marker: an execution failure / INDETERMINATE)."""

    def __init__(self, code: str, reason: str):
        super().__init__(f"{code}: {reason}")
        self.code, self.reason = code, reason


class IndependentCheckFailed(RuntimeError):
    """Stage 2 disagrees with an independent bracket."""


class TripwireFired(RuntimeError):
    """A forbidden route function was called on a quarantined cell."""


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def read_pinned(repo: Path, key: str) -> bytes:
    rel, pin, _ = PINS[key]
    try:
        raw = (Path(repo) / rel).read_bytes()
    except OSError:
        raise ConsumerRefusal("INPUT_MISSING", rel)
    if sha(raw) != pin:
        raise ConsumerRefusal("PIN_MISMATCH", rel)
    return raw


def exec_module(raw: bytes, path: Path, name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


# ------------------------------------------------------------------ C2's frozen consumer (rlr307_driver.load_consumer)
def load_consumer(repo: Path) -> dict:
    repo = Path(repo)
    tct = exec_module(read_pinned(repo, "tct_rule"), repo / PINS["tct_rule"][0], "tct_rule")
    fc = exec_module(read_pinned(repo, "tail_forecast_r2"), repo / PINS["tail_forecast_r2"][0], "mb308_tail_forecast_r2")
    if fc.T is not tct:
        raise ConsumerRefusal("MODULE_IDENTITY", "tail_forecast_r2 did not bind the pinned tct_rule")
    c2f = exec_module(read_pinned(repo, "c2_forecast_code"), repo / PINS["c2_forecast_code"][0], "mb308_c2_d5_forecast")
    dc = exec_module(read_pinned(repo, "deflated_consume"), repo / PINS["deflated_consume"][0], "mb308_deflated_consume")
    if (dc.K1_BOUND, dc.K2_BOUND) != (c2f.K1_BOUND, c2f.K2_BOUND):
        raise ConsumerRefusal("KAPPA", "consumer kappa differs from C2's local copy")
    R = tct.load_frozen("tc_rule", tct.FROZEN["tc_rule"][1])
    adapter = fc.module("adapter", "mb308_fc_adapter")
    if sha((repo / fc.PINS["adapter"][0]).read_bytes()) != PINS["adapter"][1]:
        raise ConsumerRefusal("PIN_MISMATCH", "adapter")
    comp = adapter.frozen_components(repo)
    KM = comp["loader"]
    adapter.bound_file(repo / adapter.CELLS_JSON, adapter.CELLS_SHA256, "cells.json")
    if adapter.CELLS_SHA256 != PINS["cells_json"][1] or adapter.MANIFEST_SHA256 != PINS["record_manifest"][1]:
        raise ConsumerRefusal("PIN_MISMATCH", "adapter bindings differ from the campaign's")
    cover = KM.load_cells(repo / adapter.CELLS_JSON, adapter.DETECTOR)
    if [c["index"] for c in cover] != list(range(310)):
        raise ConsumerRefusal("COVER_UNIVERSE")
    return {"repo": repo, "T": tct, "FC": fc, "C2F": c2f, "DC": dc, "R": R, "KM": KM, "adapter": adapter,
            "cover": {c["index"]: c for c in cover}}


def cover_interval(con: dict, k: int) -> tuple:
    cov = con["cover"][k]
    return F(con["KM"].rat(cov["left"])), F(con["KM"].rat(cov["right"])), F(con["KM"].rat(cov["e0"])), \
        F(con["KM"].rat(cov["rho"]))


def cell_inputs(con: dict, k: int, IND7) -> dict:
    if k not in CONTROL_CELLS:
        raise ConsumerRefusal("CELL_OUT_OF_SCOPE", str(k))
    repo, T, FC, R = con["repo"], con["T"], con["FC"], con["R"]
    meas = json.loads(read_pinned(repo, f"tct_inputs_{k}"))
    adopted = json.loads(read_pinned(repo, "adopted_inputs"))
    manifest = json.loads(read_pinned(repo, "record_manifest"))
    a = adopted["cells"][str(k)]
    want = manifest["files"].get(f"k4_records/aux5_CUSUM_{k}_256.json")
    if meas["cell"] != k or not meas["identity_gate"]["identical"] or meas["order3_fields_present"]:
        raise ConsumerRefusal("MEASUREMENT", f"cell {k} is not a gated order-3-free replay")
    if not (want and meas["k1_record_sha256"] == a["record_sha256"] == want):
        raise ConsumerRefusal("RECORD_BINDING", f"cell {k}: measurement, adopted inputs and manifest disagree")
    if adopted["manifest_sha256"] != PINS["record_manifest"][1]:
        raise ConsumerRefusal("RECORD_BINDING", "adopted inputs not bound to the adopted export manifest")
    meas["C_upper"] = str(FC.rat(a["C_upper"]))
    rec_view = {"eps_cell_refined": a["eps_cell_refined"], "m": a["m"]}
    if not T.derived_identity_gate(R, meas, rec_view)["pass"]:
        raise ConsumerRefusal("IDENTITY_GATE", f"cell {k}")
    kn = {i: F(meas["norms"]["k"][i]) for i in range(5)}
    G = T.atom_constants_generic(F(meas["C_upper"]), kn[1], kn[2])
    if {j: G[j] for j in FIELDS} != IND7.lemma_g(F(meas["C_upper"]), kn[1], kn[2]):
        raise ConsumerRefusal("LEMMA_G_CROSSCHECK", f"cell {k}")
    return {"k": k, "meas": meas, "aux": a["auxiliary_evidence"], "ad": a["m"]["5"], "cov": con["cover"][k],
            "G": G, "k1": kn[1], "k2": kn[2]}


def i1_sets(repo: Path, k: int) -> list:
    out = []
    for name, key in (("C1", "registry_c1"), ("C2", "registry_c2")):
        blocks = [b for b in json.loads(read_pinned(repo, key))["blocks"] if b["cell"] == k]
        if len(blocks) != 1 or blocks[0].get("certified") is not True:
            raise ConsumerRefusal("I1_BLOCK", f"{name} cell {k}")
        out.append({"name": name, "values": {x: F(blocks[0][x]) for x in ARGS}})
    return out


def s_i1(con: dict, k: int, ci: dict, IND7) -> tuple:
    """C2's adopted supply for cell k: componentwise min of {G, Dv'(C1), Dv'(C2)} (the frozen consumer's combine)."""
    sup = {"G": ci["G"]}
    for s in i1_sets(con["repo"], k):
        v = s["values"]
        if not (v["D_lo"] > 0 and v["tau"] >= 1 and v["C_T"] >= v["tau"] and v["Abar"] >= 1):
            raise ConsumerRefusal("VALIDATION", s["name"])
        args = tuple(v[x] for x in ARGS)
        frozen = con["DC"].atom_constants_r2(*args)
        ind = IND7.dv_prime_r2(*args, con["C2F"].K1_BOUND, con["C2F"].K2_BOUND)
        if {j: frozen[j] for j in FIELDS} != con["C2F"]._atom_independent(*args) or \
                {j: frozen[j] for j in FIELDS} != ind:
            raise ConsumerRefusal("ATOM_CROSSCHECK", s["name"])
        sup[s["name"]] = frozen
    A, prov = con["C2F"].combine(sup)
    if {j: A[j] for j in FIELDS} != IND7.componentwise_min(sup):
        raise ConsumerRefusal("COMBINE_CROSSCHECK", str(k))
    return A, prov, sup


def evaluate(con: dict, ci: dict, A: dict) -> dict:
    res = con["C2F"].direct(con["T"], con["R"], ci["meas"], ci["aux"], A, ci["ad"], ci["cov"], con["KM"])
    return {"Gamma_exact": str(res["Gamma"]), "pass": bool(res["pass"]), "H_exact": [str(res["lo"]), str(res["hi"])],
            "M_after_exact": str(res["M"]), "A_exact": {j: str(A[j]) for j in FIELDS}}


def control_ca(con: dict, k: int, IND7) -> dict:
    """C-A: C2's committed record for cell k reproduced exactly under S_I1 (every field compared for equality)."""
    ci = cell_inputs(con, k, IND7)
    A, prov, sup = s_i1(con, k, ci, IND7)
    got = evaluate(con, ci, A)
    fc = json.loads(read_pinned(con["repo"], "c2_forecast"))
    want, wsup = fc["cells"][str(k)], fc["supplies"][str(k)]
    fields = {"Gamma_exact": got["Gamma_exact"] == want["Gamma_exact"], "A_exact": got["A_exact"] == want["A_exact"],
              "provenance": prov == want["provenance"], "H_exact": got["H_exact"] == want["H_exact"],
              "M_after_exact": got["M_after_exact"] == want["M_after_exact"], "pass": got["pass"] == want["pass"],
              "per_supply_records_G_C1_C2": sorted(wsup) == sorted(sup) and all(
                  float(sup[n][j]) == wsup[n][j] for n in sup for j in FIELDS)}
    return {"cell": k, "supply": "S_I1 = min{G, Dv'(C1), Dv'(C2)} (C2's adopted supply)",
            "reproduces_C2_exactly": all(fields.values()), "field_matches": fields, "provenance": prov,
            "_evaluated": got, "_ci": ci, "_A": A, "_committed": {x: want[x] for x in ("H_exact", "Gamma_exact",
                                                                                     "M_after_exact")}}


def public(rec: dict) -> dict:
    return {k: v for k, v in rec.items() if not k.startswith("_")}


def bundle_for(ci: dict, A: dict, committed: dict | None, label: tuple = ("CUSUM", 5)) -> dict:
    """The tptb_tail input object built from the COMMITTED TC-T inputs of a cell and the supply A."""
    b = {"label": {"detector": label[0], "m": label[1], "cell": ci["k"]}, "meas": ci["meas"], "aux": ci["aux"],
         "adopted_m5": ci["ad"], "cover": ci["cov"], "supply": {j: fs(A[j]) for j in FIELDS}}
    if committed is not None:
        b["committed"] = dict(committed)
    return b


# ------------------------------------------------------------------ tripwires
@contextlib.contextmanager
def tripwires(asm: dict, indep, mode: str):
    """Replace every forbidden route function by one that raises, for the duration of a control / target call."""
    TPT, TB = asm["TPT"], asm["TB"]
    names = FORBIDDEN_IN_CONTROL if mode == "control" else FORBIDDEN_IN_TARGET
    slots = [(TPT, n) for n in names] + [(TB, "evaluate_bundle"), (TB, "_evaluate")]
    if mode == "control":
        slots += [(TB, "independent_penalty"), (TB, "transport_gate")]
    if indep is not None:
        slots += [(indep, "p5_c5t_closed_form"), (indep, "tpt_endpoint_only")]
        if mode == "control":
            slots += [(indep, "tptb")]
    saved = [(m, n, getattr(m, n)) for m, n in slots]

    def trip(name):
        def f(*_a, **_k):
            raise TripwireFired(f"TRIPWIRE {name} called in {mode} mode")
        f._mb308_tripwire = name
        return f

    for m, n, _ in saved:
        setattr(m, n, trip(n))
    try:
        # provably armed (incident review C7(a)): every slot now holds its stub, and a stub raises when called
        armed = all(getattr(getattr(m, n), "_mb308_tripwire", None) == n for m, n, _ in saved)
        try:
            getattr(saved[0][0], saved[0][1])()
            fires = False
        except TripwireFired:
            fires = True
        yield {"mode": mode, "armed": [n for _, n, _ in saved], "verified_armed": armed, "verified_fires": fires}
    finally:
        for m, n, f in saved:
            setattr(m, n, f)


# ------------------------------------------------------------------ the reproduction core (s = rho only)
def _geometry(TB, bundle: dict) -> tuple:
    lab, meas, cov = bundle["label"], bundle["meas"], bundle["cover"]
    if int(lab["m"]) != TB.M_FROZEN:
        raise Stop("INPUT_REFUSED", "the frozen direct clause is m = 5 only")
    if meas["cell"] != lab["cell"] or cov["index"] != lab["cell"]:
        raise Stop("INPUT_REFUSED", "label cell is not bound to meas.cell and cover.index")
    if meas.get("order3_fields_present") is not False:
        raise Stop("INPUT_REFUSED", "not an order-3-free TC-T input")
    e0, rho, x_lo, x_hi = (TB.KM.rat(cov[t]) for t in ("e0", "rho", "left", "right"))
    c5 = {"x_lo_eq_e0_minus_rho": e0 - rho == x_lo, "x_hi_eq_e0_plus_rho": e0 + rho == x_hi,
          "meas_rho_eq_cover_rho": TB.q(meas["rho"]) == rho,
          "meas_e0_eq_cover_e0": ("e0" not in meas) or TB.q(meas["e0"]) == e0, "x_lo_positive": x_lo > 0}
    c5["pass"] = all(c5.values())
    if not c5["pass"]:
        raise Stop("C5_CELL_IDENTITY", "E = [e0 - rho, e0 + rho] is not an exact identity of the cover")
    return F(e0), F(rho), F(x_lo), F(x_hi), c5


def repro_core(asm: dict, bundle: dict) -> dict:
    """tptb_tail's reproduction mode at s = rho: frozen direct clause through the capturing proxy, G-R1/G-R2/G-R3,
    G-R4(M), the tpt profile at rho, the frozen penalty, G-CF. No profile value at any s < rho is formed here.
    tptb_tail's own refusals (its Stop class) are re-raised as this module's Stop."""
    try:
        return _repro_core(asm, bundle)
    except asm["TB"].Stop as exc:
        raise Stop(exc.code, exc.reason)


def _repro_core(asm: dict, bundle: dict) -> dict:
    TB, TPT = asm["TB"], asm["TPT"]
    TB._guards(bundle)
    lab, meas, aux, ad, cov = (bundle[k] for k in ("label", "meas", "aux", "adopted_m5", "cover"))
    e0, rho, x_lo, x_hi, c5 = _geometry(TB, bundle)
    S, prov = TB.supply_from(bundle, meas)
    Sd = dict(zip(FIELDS, S))
    cap = TB.CapturingR(TB.R)
    res = TB.C2.direct(TB.T, cap, meas, aux, Sd, ad, cov, TB.KM)
    ext = TB._extract(cap, meas)
    ext.update(e0=e0, rho=rho, x_lo=x_lo, x_hi=x_hi)
    for r, t in enumerate(ext["terms"]):
        o = res["obj"][r]
        if (o["f_G"], o["env4"], o["rad"], o["half"], o["abs_G_at_a"]) != (t["fG"], t["Env4"], t["frozen_rad"],
                                                                          t["frozen_half"], t["abs_G"]) or t["rho"] != rho:
            raise Stop("REPRODUCTION_FAILED", f"captured tuple differs from the frozen per-r object at r = {r}")
    com = bundle.get("committed") or {}
    g = {"C5": c5}
    red = TB.rederive_tuple(meas, aux)
    mism = [f"r{r}.{x}" for r, t in enumerate(ext["terms"]) for x in TB.TUPLE + ("abs_G", "H_at_a") if t[x] != red[r][x]]
    if len(ext["terms"]) != TB.M_FROZEN or ext["m_rows"] != TB.M_FROZEN:
        mism.append("m")
    g["G-R3"] = {"pass": not mism, "n_mismatches": len(mism)}
    Hx = TB.whole_cell_from_tuple(ext, S)
    g1 = {"frozen_equal": Hx == (res["lo"], res["hi"])}
    if com.get("H_exact") is not None:
        g1["committed_equal"] = Hx == tuple(TB.q(v) for v in com["H_exact"])
    g1["pass"] = all(g1.values())
    g["G-R1"] = g1
    R2 = (TB.q(ad["R2_interval"]["lo"]), TB.q(ad["R2_interval"]["hi"]))
    M0 = TB.q(ad["M_R2"])
    g_hi = TB.q(ad["R_interval"]["hi"]) - e0 * TB.q(ad["D_interval"]["lo"])
    a_, b_ = max(R2[0], Hx[0]), min(R2[1], Hx[1])
    if a_ > b_:
        raise Stop("REPRODUCTION_FAILED", "empty consumed intersection H_final")
    H_final = (a_, b_)
    mag = max(abs(a_), abs(b_))
    M_ext = min(M0, mag)
    Gam_ext = g_hi + rho * x_hi * M_ext
    g2 = {"frozen_equal": Gam_ext == res["Gamma"] and M_ext == res["M"]}
    if com.get("Gamma_exact") is not None:
        g2["committed_equal"] = Gam_ext == TB.q(com["Gamma_exact"]) and M_ext == TB.q(com["M_after_exact"])
    g2["pass"] = all(g2.values())
    g["G-R2"] = g2
    g["G-R4(M)"] = {"pass": res["M"] == mag}
    terms = [TPT.SourceTerm(H_at_a=t["H_at_a"], abs_G_at_a=t["abs_G"], fF=t["fF"], fD=t["fD"], fH=t["fH"],
                            fG=t["fG"], Env4=t["Env4"]) for t in ext["terms"]]
    cp = TPT.CellProfile(detector=str(lab["detector"]), m=int(lab["m"]), cell=int(lab["cell"]), e0=e0, rho=rho,
                         g_hi=g_hi, A0=S[0], A1=S[1], A2=S[2], terms=terms, W=ext["W"], H_K1=H_final,
                         M_consumed=res["M"])
    lo_p, hi_p = TPT.lo_hi_polys(cp)
    g["TPT_profile_at_rho"] = {"pass": (TPT.peval(lo_p, rho), TPT.peval(hi_p, rho)) == (res["lo"], res["hi"])}
    P_fr = TPT.penalty_frozen(cp)
    g["P_frozen"] = {"pass": g_hi + P_fr == res["Gamma"]}
    g["G-R3b"] = gr3b_cell(asm, cp, ext, meas, aux, S, (res["lo"], res["hi"]))
    C_lo = ext["W"][0] + sum(t["H_at_a"][0] for t in ext["terms"]) / len(ext["terms"])
    binding = R2[0] <= Hx[0] and Hx[1] <= R2[1] and abs(Hx[0]) >= abs(Hx[1]) and C_lo < 0
    if binding:
        Pb = [sum(TB.p_at(t, rho)[j] for t in ext["terms"]) / len(ext["terms"]) for j in range(3)]
        cf = g_hi + rho * x_hi * abs(C_lo) + rho * x_hi * (S[0] * Pb[2] + 2 * S[1] * Pb[1] + S[2] * Pb[0])
        g["G-CF"] = {"applies": True, "pass": cf == res["Gamma"]}
    else:
        g["G-CF"] = {"applies": False, "pass": True}
    failed = [k for k, v in g.items() if v.get("pass") is not True]
    return {"gates": g, "failed": failed, "ext": ext, "cp": cp, "S": S, "H_final": H_final, "g_hi": g_hi,
            "P_frozen": P_fr, "res": res, "e0": e0, "rho": rho, "x_lo": x_lo, "x_hi": x_hi, "supply_prov": prov}


# ------------------------------------------------------------------ G-R3b: the independent tuple (stream F3)
def _src(t: dict, TPT):
    return TPT.SourceTerm(H_at_a=t["H_at_a"], abs_G_at_a=t["abs_G"], fF=t["fF"], fD=t["fD"], fH=t["fH"], fG=t["fG"],
                          Env4=t["Env4"])


def gr3b_cell(asm: dict, cp, ext: dict, meas: dict, aux: dict, S: tuple, H_frozen: tuple) -> dict:
    """Stream F3's independent tuple must equal the frozen-extracted tuple exactly: per r (fF, fD, fH, fG, Env4,
    centre, |G| = 0), the rad_r coefficient list for the cell constants (tpt.rad_poly), the W sum, the whole cell."""
    F3, TPT = asm.get("F3"), asm["TPT"]
    if F3 is None:
        return {"pass": False, "reason": "F3 absent"}
    try:
        res3 = F3.tuple_tct(meas, aux, S)
    except F3.TupleRefusal as exc:
        return {"pass": False, "refused": str(exc)[:160]}
    mism = []
    if len(ext["terms"]) != res3["m"]:
        mism.append("m")
    for r, t in enumerate(ext["terms"]):
        u = res3["per_r"][r]
        mism += [f"r{r}.{x}" for x in ("fF", "fD", "fH", "fG", "Env4") if t[x] != u[x]]
        if tuple(t["H_at_a"]) != tuple(u["H_at_a"]):
            mism.append(f"r{r}.centre")
        if t["abs_G"] != 0 or u["abs_G"] != 0:
            mism.append(f"r{r}.abs_G")
        if [F(c) for c in TPT.rad_poly(cp, _src(t, TPT))] != [F(c) for c in u["rad"]]:
            mism.append(f"r{r}.rad(S)")
    if tuple(ext["W"]) != tuple(res3["W"]):
        mism.append("W")
    if tuple(F3.whole_cell(res3)) != tuple(H_frozen):
        mism.append("whole_cell_at_rho")
    return {"pass": not mism, "n_mismatches": len(mism), "mismatch_fields": mism[:12], "_res3": res3}


def gr3b_blocks(asm: dict, cp, ext: dict, res3: dict, bl: list) -> dict:
    """For every block triple A: per r the rad_r coefficients (tpt.rad_poly with A) == F3.profiles(...)["rad"], and
    the lo/hi profile polynomials (tpt.lo_hi_polys with A) == the F3-built ones."""
    F3, TPT = asm["F3"], asm["TPT"]
    m = len(ext["terms"])
    bad = []
    for bi, (_a, _b, A) in enumerate(bl):
        cpA = copy.copy(cp)
        cpA.A0, cpA.A1, cpA.A2 = A
        lo3, hi3 = [res3["W"][0]], [res3["W"][1]]
        for r, t in enumerate(ext["terms"]):
            rad3 = F3.profiles(res3["per_r"][r], A)["rad"]
            if [F(c) for c in TPT.rad_poly(cpA, _src(t, TPT))] != [F(c) for c in rad3]:
                bad.append(f"block{bi}.r{r}.rad")
            c = res3["per_r"][r]["H_at_a"]
            lo3 = F3.padd(lo3, F3.pscale(F(1, m), F3.padd([c[0]], F3.pscale(-1, rad3))))
            hi3 = F3.padd(hi3, F3.pscale(F(1, m), F3.padd([c[1]], rad3)))
        lo_p, hi_p = TPT.lo_hi_polys(cpA)
        if [F(x) for x in lo_p] != [F(x) for x in lo3] or [F(x) for x in hi_p] != [F(x) for x in hi3]:
            bad.append(f"block{bi}.lo_hi")
    return {"pass": not bad, "blocks": len(bl), "mismatch_fields": bad[:12]}


def control_cb(asm: dict, guard, bundle: dict, indep=None) -> dict:
    """C-B (reproduction only, equality booleans only). Cells 305 / 308 through guard.reproduction; decoys directly."""
    lab = bundle["label"]
    KM = asm["TB"].KM
    cov = bundle["cover"]
    ctx = guard.reproduction(lab["cell"], (KM.rat(cov["left"]), KM.rat(cov["right"])), KM.rat(cov["e0"])) \
        if str(lab["detector"]).upper() == "CUSUM" else contextlib.nullcontext()
    with ctx, tripwires(asm, indep, "control") as tw:
        if not (tw["verified_armed"] and tw["verified_fires"]):
            return {"reproduces_exactly": False, "stop": "TRIPWIRES_NOT_ARMED", "tripwires": tw}
        try:
            core = repro_core(asm, bundle)
        except Stop as exc:
            return {"reproduces_exactly": False, "stop": exc.code, "reason": exc.reason, "tripwires": tw}
    gates = {k: {x: y for x, y in v.items() if isinstance(y, bool)} for k, v in core["gates"].items()}
    return {"reproduces_exactly": not core["failed"], "failed": core["failed"], "gates": gates, "tripwires": tw,
            "note": "reproduction only (s = rho); equality booleans only; no transport penalty of any route computed"}


# ------------------------------------------------------------------ Stage 2 (target-mode entry)
def f2_profile(core: dict) -> dict:
    ext = core["ext"]
    return {"e0": core["e0"], "rho": core["rho"], "x_lo": core["x_lo"], "x_hi": core["x_hi"], "m": len(ext["terms"]),
            "sources": [{"f_F": t["fF"], "f_D": t["fD"], "f_H": t["fH"], "f_G": t["fG"], "Env4": t["Env4"],
                         "Hhat": list(t["H_at_a"]), "G_abs": t["abs_G"]} for t in ext["terms"]],
            "W": list(ext["W"]), "H_final": list(core["H_final"]), "M_consumed": core["res"]["M"]}


def f2_band_guard(guard) -> bool:
    """F2's research band guard stays ON unless the formal guard is ARMED for the target (decoys lie outside the band
    and keep it on). Never taken from a caller's argument."""
    return guard.mode() != "TARGET"


def stage2(asm: dict, guard, bundle: dict, block_triples: list, indep) -> dict:
    """block_triples: [(tile_lo, tile_hi, {"A0","A1","A2"})] tiling the cover exactly. Returns the Stage-2 record;
    raises Stop (gate refusal) or IndependentCheckFailed. Every comparison is EXACT (no tolerance enters a gate)."""
    try:
        return _stage2(asm, guard, bundle, block_triples, indep)
    except asm["TB"].Stop as exc:
        raise Stop(exc.code, exc.reason)


def _stage2(asm: dict, guard, bundle: dict, block_triples: list, indep) -> dict:
    TB, TPT = asm["TB"], asm["TPT"]
    band_guard = f2_band_guard(guard)
    with tripwires(asm, indep, "target") as tw:
        if not (tw["verified_armed"] and tw["verified_fires"]):
            raise Stop("TRIPWIRES_NOT_ARMED", "the target-mode tripwires could not be verified")
        core = repro_core(asm, bundle)
        if core["failed"] == ["G-R3b"]:
            raise IndependentCheckFailed("G-R3b: the frozen-extracted tuple differs from the independent tuple (F3)")
        if core["failed"]:
            raise Stop("REPRODUCTION_FAILED", "gates failed: " + ", ".join(core["failed"]))
        ext, S, H_final, cp = core["ext"], core["S"], core["H_final"], core["cp"]
        g = core["gates"]
        lo0, hi0 = TB.band_at(ext, S, F(0), H_final)
        g["G-R4(N5)"] = {"pass": lo0 <= hi0}
        if lo0 > hi0:
            raise Stop("REPRODUCTION_FAILED", "G-R4: cell band empty at s = 0 (N5)")
        bl = TB.check_blocks([{"e_lo": fs(a), "e_hi": fs(b), **{j: fs(t[j]) for j in FIELDS}}
                              for a, b, t in block_triples], core["x_lo"], core["x_hi"], S)
        c6 = []
        for side in ("R", "L"):
            for sa, sb, A in TB._pieces(ext, bl, side):
                L0, U0 = TB.band_at(ext, A, sa, H_final)
                c6.append(L0 <= U0)
                if L0 > U0:
                    g["C6"] = {"pass": False, "pieces_checked": len(c6)}
                    raise Stop("C6_EMPTY_BAND", f"side {side}: the capped band is empty at a piece's inner end")
        g["C6"] = {"pass": True, "pieces_checked": len(c6)}
        gb = gr3b_blocks(asm, cp, ext, g["G-R3b"]["_res3"], bl)
        g["G-R3b_blocks"] = gb
        if not gb["pass"]:
            raise IndependentCheckFailed("G-R3b: a block profile differs from the independent tuple (F3)")
        TPT.check_nonempty(cp)
        rb = TPT.penalty_blocked(cp, [TPT.Block(e_lo=a, e_hi=b, A0=A[0], A1=A[1], A2=A[2]) for (a, b, A) in bl])
        P_B = rb["P_star_B"]
        indB = TB.independent_penalty(ext, bl, H_final)
        tolB = TB.split_tolerance(ext, S, H_final, 2 * len(TB.bl_pieces_hint(ext, bl)))
        gt2 = TB.transport_gate(P_B, indB, tolB)
        # gate: the EXACT soundness side only (P_lo <= P_B); the loose upper side is recorded, never gated
        g["G-T2"] = {"pass": indB["P_lo"] <= P_B, "P_B_ge_indep_hi_exact": P_B >= indB["P_hi"],
                     "informational_loose_upper_side": bool(gt2["pass"])}
        if not g["G-T2"]["pass"]:
            raise IndependentCheckFailed("G-T2: P_B below the stream-ASSEMBLY independent lower bound")
        dom = P_B <= core["P_frozen"]
        g["dominance_P_B_le_P_frozen"] = {"pass": dom}
        if not dom:
            raise IndependentCheckFailed("dominance P_B <= P_frozen(S_I1) violated")
        f2 = {"status": "HOOK_ABSENT"}
        P_hi = None
        if indep is not None:
            try:
                br = indep.tptb(f2_profile(core), [{"lo": a, "hi": b, "A0": A[0], "A1": A[1], "A2": A[2]}
                                                   for (a, b, A) in bl], research_band_guard=band_guard)
            except indep.Refusal as exc:
                raise IndependentCheckFailed(f"F2 refused: {exc}")
            if not (br["P_lo"] <= P_B):
                raise IndependentCheckFailed("F2: P_lo > P_B(primary)")
            P_hi = br["P_hi"]
            f2 = {"status": "P_LO_LE_P_B", "P_lo": fs(br["P_lo"]), "P_hi": fs(br["P_hi"]),
                  "width_lt_2^-150": br["P_hi"] - br["P_lo"] < F(1, 2 ** 150), "revision": br.get("revision"),
                  "P_B_le_P_hi_exact": P_B <= br["P_hi"], "P_B_eq_P_lo_eq_P_hi": br["P_lo"] == br["P_hi"] == P_B,
                  "research_band_guard": band_guard}
        g_hi = core["g_hi"]
        P_dec = P_B if P_hi is None else max(P_B, P_hi)
        Gamma_dec = g_hi + P_dec
    return {"gates": g, "tripwires": tw, "n_blocks": len(bl), "pieces": rb.get("pieces"), "F2": f2,
            "values": {"g_hi": fs(g_hi), "P_B_primary": fs(P_B), "P_frozen_S_I1": fs(core["P_frozen"]),
                       "P_dec": fs(P_dec), "Gamma_dec": fs(Gamma_dec)},
            "Gamma_dec_lt_0": Gamma_dec < 0, "F2_present": indep is not None}
