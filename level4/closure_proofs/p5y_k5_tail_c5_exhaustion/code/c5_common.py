"""Shared loaders for Campaign C5. Read-only against every predecessor namespace.

C5 evaluates no scientific address: it forms no K1 record, no order-3 candidate, no value of R, calls no kernel
routine and runs no operator certification. Everything is either a read of a committed artifact or a deterministic
re-evaluation of a frozen consumer on committed inputs.
"""
import copy
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
C2 = CP / "p5y_k5_tail_c2_closure"
C3 = CP / "p5y_k5_tail_c3_closure"
C4 = CP / "p5y_k5_tail_c4_exhaustion"
OPEN_CELLS = (306, 307, 308, 309)


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(path, name, pin=None):
    raw = Path(path).read_bytes()
    if pin and hashlib.sha256(raw).hexdigest() != pin:
        raise SystemExit(f"pin mismatch: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def frozen_stack():
    """The frozen theorem/consumer modules exactly as C3 and C4 loaded them."""
    FC = load(C2 / "code/c2_d5_forecast.py", "c2fc")
    B = FC.load(FC.B_NS / "code/tail_forecast_r2.py", "b_tf")
    T = sys.modules["tct_rule"]
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    DC = FC.load(FC.AD_NS / "code/deflated_consume.py", "ad_dc", FC.DC_SHA)
    SEL = load(C3 / "code/c3_selector.py", "c3sel")
    return FC, B, T, R, DC, SEL


def committed_inputs(FC):
    adopted = json.loads((FC.B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    cover = {c["index"]: c for c in json.loads(
        (CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes()) if c["detector"] == "CUSUM"}
    c1 = {b["cell"]: b for b in json.loads(
        (FC.C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())["blocks"]}
    c2 = {b["cell"]: b for b in json.loads(
        (C2 / "evidence/registry_c2/REGISTRY_C2.json").read_bytes())["blocks"]}
    return adopted, cover, c1, c2


def cell_supply(cell, FC, B, T, R, DC, SEL, adopted, cover, c1, c2):
    meas = json.loads((FC.B_NS / f"evidence/measurement_r1/TCT_INPUTS_{cell}.json").read_bytes())
    meas["C_upper"] = adopted[str(cell)]["C_upper"]
    aux, ad5, cov = adopted[str(cell)]["auxiliary_evidence"], adopted[str(cell)]["m"]["5"], cover[cell]
    s = SEL.build(cell, c1[cell], c2[cell], cov, meas, DC, T, B.rat)
    return meas, aux, ad5, cov, s


def knock(FC, B, T, R, meas, aux, ad5, cov, A, sc=None, allow_crosscheck_alignment=True):
    """DIAGNOSTIC sensitivity evaluator: recompute Gamma with selected ingredients scaled.

    The frozen `direct` runs theorem TC-T twice by two independent paths and refuses if they disagree. The
    independent crosscheck cannot see a scaled ingredient, so for a sensitivity sweep it is aligned to the frozen
    path. THAT MAKES EVERY SCALED RUN A DIAGNOSTIC, NOT A CERTIFICATE, and callers must label it so. With `sc`
    empty nothing is patched and the crosscheck runs live, so the baseline row is always a real evaluation.
    """
    sc = dict(sc or {})
    sc.pop("__", None)
    m2 = copy.deepcopy(meas)
    for r in range(5):
        o = m2["r"][str(r)]
        for kb, fld in (("supF", "F"), ("supD", "D"), ("supH", "H")):
            if kb in sc:
                o["sup"][fld] = str(F(o["sup"][fld]) * sc[kb])
    if "rho" in sc:
        m2["rho"] = str(F(m2["rho"]) * sc["rho"])
    A2 = {j: F(A[j]) * sc.get(j, 1) for j in ("A0", "A1", "A2")}
    TT = sys.modules["tct_rule"]
    osig, ofg, oenv, ocx = TT.sigmas, TT.fG_zero_candidate, R.env4, TT.tail_enclosure_crosscheck

    def sigs(*a, **kw):
        s = osig(*a, **kw)
        for r in s:
            for q in ("sigma3", "sigma4"):
                if q in sc:
                    s[r][q] = s[r][q] * sc[q]
        return s
    patched = bool(sc) and any(q in sc for q in ("supF", "supD", "supH", "rho", "sigma3", "sigma4", "fG", "env4"))
    if patched:
        TT.sigmas = sigs
        TT.fG_zero_candidate = lambda *a, **kw: ofg(*a, **kw) * sc.get("fG", 1)
        R.env4 = lambda *a, **kw: oenv(*a, **kw) * sc.get("env4", 1)
        if allow_crosscheck_alignment:
            TT.tail_enclosure_crosscheck = lambda me, au, AA, m, o3=None: TT.tail_enclosure(R, me, au, AA, m, o3)[:2]
    try:
        return FC.direct(T, R, m2, aux, A2, ad5, cov, B)
    finally:
        TT.sigmas, TT.fG_zero_candidate, R.env4, TT.tail_enclosure_crosscheck = osig, ofg, oenv, ocx
