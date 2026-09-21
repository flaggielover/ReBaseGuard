"""Shared loaders for Campaign C4. Read-only against every predecessor namespace.

C4 evaluates no scientific address: it forms no K1 record, no order-3 candidate, no value of R, and calls no
kernel-certification routine. Everything below either reads a committed artifact or re-runs a frozen consumer on
committed inputs.
"""
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
OPEN_CELLS = (306, 307, 308, 309)

# The frozen CUSUM geometry, read from the frozen producer rather than transcribed (see c4_model_identity.py).
MODEL_SOURCE = CP / "p5y_k1_cover_ledger_implementation/code/cusum_layer1.py"


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
    """The frozen theorem/consumer modules exactly as C3 loaded them, plus C3's own selector."""
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
    """The C3 mechanism's supply for one cell, rebuilt from committed evidence (not copied from C3's forecast)."""
    meas = json.loads((FC.B_NS / f"evidence/measurement_r1/TCT_INPUTS_{cell}.json").read_bytes())
    meas["C_upper"] = adopted[str(cell)]["C_upper"]
    aux, ad5, cov = adopted[str(cell)]["auxiliary_evidence"], adopted[str(cell)]["m"]["5"], cover[cell]
    s = SEL.build(cell, c1[cell], c2[cell], cov, meas, DC, T, B.rat)
    return meas, aux, ad5, cov, s


def gamma_at(FC, T, R, B, meas, aux, ad5, cov, A0, A1, A2):
    """Theorem TC-T -> frozen K5-B direct clause, at an arbitrary atom-constant triple. Exact rationals."""
    return FC.direct(T, R, meas, aux, {"A0": F(A0), "A1": F(A1), "A2": F(A2)}, ad5, cov, B)
