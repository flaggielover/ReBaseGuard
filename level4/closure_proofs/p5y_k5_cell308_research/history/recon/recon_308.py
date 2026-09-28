#!/usr/bin/env python3
# c308-quarantine: historical-read
"""Stream A -- pre-registered HISTORICAL_RECONSTRUCTION R1-R4 for CUSUM m = 5 cell 308.

Pre-registration: history/recon/RECON_PREREGISTRATION.md (written before this script was run). Nothing outside
that list is computed; every evaluation point is a committed supply or the point of a committed statement.
Output: history/recon/C3_KNOCKOUT_RECONSTRUCTION.json (committed value, equality boolean, recomputed exact value).

Frozen modules imported BY FILE PATH (exec of the file bytes into a fresh module; no module is modified; none of
their main() functions is called; their imports have no side effects -- checked by reading them):
  * p5y_k5_m5_tail_closure/code/tct_rule.py      theorem TC-T enclosure: frozen-rule path `tail_enclosure` and the
                                                  independent `tail_enclosure_crosscheck`; `load_frozen` loads the
                                                  sha-pinned p5y_k5_lower_front_order3/code/tc_rule.py (pure).
  * p5y_k5_tail_c2_closure/code/c2_d5_forecast.py `direct` (the frozen K5-B direct clause exactly as C2/C3/C4 ran
                                                  it) and `_atom_independent` (C2's independent Lemma Dv').
  * p5y_k5_perron_deflated_resolvent/code/deflated_consume.py (sha256 pin ef5d0474...) `atom_constants_r2`.
Why: R1-R4 must reproduce committed numbers through the same frozen consumer that produced them.
The quarantine import guard is deliberately NOT installed (it would refuse these frozen modules by design).
Stdlib only; exact fractions.Fraction throughout. Run: python3 -I -B recon_308.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[2]
REPO = NS.parents[2]
LP = REPO / "level4/closure_proofs"
OUT = HERE.parent / "C3_KNOCKOUT_RECONSTRUCTION.json"
CELL = 308
M = 5

P_TCT = LP / "p5y_k5_m5_tail_closure/code/tct_rule.py"
P_FC = LP / "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py"
P_DC = LP / "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py"
P_MEAS = LP / f"p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_{CELL}.json"
P_ADOPT = LP / "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json"
P_CELLS = LP / "p5y_k1_cover_ledger_successor/config/cells.json"
P_C2D5 = LP / "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json"
P_C3F = LP / "p5y_k5_tail_c3_closure/evidence/forecast/C3_FORECAST.json"
P_C3E = LP / "p5y_k5_tail_c3_closure/evidence/execution/C3_EXECUTION.json"
P_C3ADJ = LP / "p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md"
P_C4T = LP / "p5y_k5_tail_c4_exhaustion/evidence/phase1/C4_THRESHOLDS.json"
P_C4ADJ = LP / "p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md"
P_C4OND = LP / "p5y_k5_tail_c4_exhaustion/OPEN_NOTES_DISPOSITION_C4.md"
P_C4REC = LP / "p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md"

sys.path.insert(0, str(NS / "code"))
import c308_quarantine as q  # noqa: E402  (ledger helper only; import guard NOT installed, see header)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def load(path: Path, name: str, pin: str | None = None):
    raw = path.read_bytes()
    if pin is not None and sha256(raw) != pin:
        raise SystemExit(f"pin mismatch {path}")
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


class KMShim:
    """`rat` copied verbatim from tail_forecast_r2.rat / k5_minimality.rat (the frozen modules are not imported)."""
    @staticmethod
    def rat(p) -> F:
        return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def line_of(path: Path, needle: str) -> tuple[int, str]:
    for i, ln in enumerate(path.read_text().splitlines(), 1):
        if needle in ln:
            return i, ln
    raise SystemExit(f"committed text not found in {path.name}: {needle!r}")


def main() -> int:
    q.log_event("history/recon/recon_308.py", "pre-registered R1-R4 reconstruction of committed cell-308 values "
                "(C2 D5 S_I1 Gamma, C3 knockout row, C4 section-4 statement, affine structure) -- START",
                klass="HISTORICAL_RECONSTRUCTION", cells_touched=[{"detector": "CUSUM", "m": 5, "cell": CELL}],
                agent="streamA", notes="evaluation points exactly as RECON_PREREGISTRATION.md; outputs only in history/recon/")
    raw = {p.name: p.read_bytes() for p in (P_TCT, P_FC, P_DC, P_MEAS, P_ADOPT, P_CELLS, P_C2D5, P_C3F, P_C3E, P_C4T)}
    prov = {n: {"sha256": sha256(b), "git_blob": git_blob(b)} for n, b in raw.items()}

    T = load(P_TCT, "sa_tct_rule")
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    FC = load(P_FC, "sa_c2fc")
    DC = load(P_DC, "sa_dc", FC.DC_SHA)
    KM = KMShim()

    meas = json.loads(raw[P_MEAS.name])
    adopted = json.loads(raw[P_ADOPT.name])["cells"][str(CELL)]
    aux, ad5 = adopted["auxiliary_evidence"], adopted["m"][str(M)]
    cov = [c for c in json.loads(raw[P_CELLS.name]) if c["detector"] == "CUSUM" and c["index"] == CELL]
    if len(cov) != 1 or meas["cell"] != CELL or not meas["identity_gate"]["identical"] or meas["order3_fields_present"]:
        raise SystemExit("committed input check failed")
    cov = cov[0]
    meas["C_upper"] = adopted["C_upper"]          # as C2/C3/C4 did; not used by the direct clause

    # ---------------------------------------------------------------- the consumer, three ways
    e0, rho, x_hi = (KM.rat(cov[t]) for t in ("e0", "rho", "right"))
    R_hi, D_lo = F(ad5["R_interval"]["hi"]), F(ad5["D_interval"]["lo"])
    H0, H1, M0 = F(ad5["R2_interval"]["lo"]), F(ad5["R2_interval"]["hi"]), F(ad5["M_R2"])

    def frozen(A):                                   # path 1: frozen direct (tail_enclosure + crosscheck inside)
        return FC.direct(T, R, meas, aux, {j: F(A[j]) for j in ("A0", "A1", "A2")}, ad5, cov, KM)

    def independent(A):                              # path 2: crosscheck enclosure + own clause code
        lo, hi = T.tail_enclosure_crosscheck(meas, aux, {j: F(A[j]) for j in ("A0", "A1", "A2")}, M, None)
        a, b = max(H0, lo), min(H1, hi)
        Mv = M0 if a > b else min(M0, max(abs(a), abs(b)))
        return lo, hi, Mv, (R_hi - e0 * D_lo) + rho * x_hi * Mv

    # coefficients (R4): p per object is A-independent; take it at A = 0 and re-check at every point
    obj0 = frozen({"A0": F(0), "A1": F(0), "A2": F(0)})["obj"]
    p = {r: tuple(obj0[r]["p"]) for r in range(M)}
    rows = R.coefficients(M)
    C_lo = sum((c * F(meas["r"][str(r)]["H_at_a"][0]) if k == "F" else c * F(meas["W2"][f"{r}:{jj}"][0])
                for k, r, jj, c in rows), F(0))
    C_hi = sum((c * F(meas["r"][str(r)]["H_at_a"][1]) if k == "F" else c * F(meas["W2"][f"{r}:{jj}"][1])
                for k, r, jj, c in rows), F(0))
    wF = {r: c for k, r, jj, c in rows if k == "F"}
    Pbar = {j: sum((wF[r] * p[r][j] for r in range(M)), F(0)) for j in range(3)}      # Pbar[j] = sum_r c_r p_j(r)
    g_hi = R_hi - e0 * D_lo
    rx = rho * x_hi
    G0 = g_hi + rx * (-C_lo)

    def affine(A):
        return G0 + rx * (F(A["A0"]) * Pbar[2] + 2 * F(A["A1"]) * Pbar[1] + F(A["A2"]) * Pbar[0])

    def evaluate(name, A):
        d = frozen(A)
        lo2, hi2, M2, G2 = independent(A)
        a, b = max(H0, d["lo"]), min(H1, d["hi"])
        half_sum = sum((wF[r] * d["obj"][r]["half"] for r in range(M)), F(0))
        reg = {"intersection_nonempty": bool(a <= b), "enclosure_within_R2": bool(H0 <= d["lo"] and d["hi"] <= H1),
               "lower_endpoint_binds": bool(d["lo"] >= H0 and abs(d["lo"]) >= abs(b)), "lo_negative": bool(d["lo"] < 0),
               "abs_lo_le_M_R2": bool(abs(d["lo"]) <= M0), "C_lo_negative": bool(C_lo < 0)}
        chk = {"p_independent_of_A": all(tuple(d["obj"][r]["p"]) == p[r] for r in range(M)),
               "lo_equals_C_lo_minus_halves": d["lo"] == C_lo - half_sum,
               "hi_equals_C_hi_plus_halves": d["hi"] == C_hi + half_sum,
               "independent_path_equal": (lo2, hi2, M2, G2) == (d["lo"], d["hi"], d["M"], d["Gamma"]),
               "affine_formula_equal": affine(A) == d["Gamma"]}
        return {"name": name, "A_exact": {j: str(F(A[j])) for j in ("A0", "A1", "A2")},
                "lo": d["lo"], "hi": d["hi"], "M": d["M"], "mag": d["mag"], "Gamma": d["Gamma"], "pass": d["pass"],
                "regime": reg, "checks": chk}

    res, cmp_ = {}, []

    def record(item, what, committed, source, equal, recomputed):
        cmp_.append({"item": item, "what": what, "committed": committed, "source": source, "equal": bool(equal),
                     "recomputed": recomputed})

    # ---------------------------------------------------------------- R1: C2 D5 S_I1
    c2 = json.loads(raw[P_C2D5.name])["cells"][str(CELL)]
    A_si1 = {j: F(c2["A_exact"][j]) for j in ("A0", "A1", "A2")}
    e = res["P_SI1"] = evaluate("P_SI1", A_si1)
    src = "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json cells[308]"
    record("R1.1", "TC-T enclosure [lo,hi] (H_exact)", "exact strings", src + ".H_exact (l.113-117)",
           [str(e["lo"]), str(e["hi"])] == c2["H_exact"], [str(e["lo"]), str(e["hi"])])
    record("R1.2", "M_after_exact", "exact string", src + ".M_after_exact (l.118)", str(e["M"]) == c2["M_after_exact"], str(e["M"]))
    record("R1.2b", "magnitude float", c2["magnitude"], src + ".magnitude", float(e["mag"]) == c2["magnitude"], float(e["mag"]))
    record("R1.3", "Gamma_exact", "exact string", src + ".Gamma_exact (l.112)", str(e["Gamma"]) == c2["Gamma_exact"], str(e["Gamma"]))
    record("R1.3b", "Gamma float", c2["Gamma"], src + ".Gamma (l.111)", float(e["Gamma"]) == c2["Gamma"], float(e["Gamma"]))
    record("R1.4", "pass flag", c2["pass"], src + ".pass", e["pass"] == c2["pass"], e["pass"])

    # ---------------------------------------------------------------- R2: C3 mixed supply and knockout
    c3 = json.loads(raw[P_C3F.name])["cells"][str(CELL)]
    c3e = json.loads(raw[P_C3E.name])["per_cell"][str(CELL)]
    c4 = json.loads(raw[P_C4T.name])["cells"][str(CELL)]
    tup = tuple(F(c3["operator_tuple"][x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
    A_mix = DC.atom_constants_r2(*tup)
    A_mix = {j: A_mix[j] for j in ("A0", "A1", "A2")}
    record("R2.1a", "atom_constants_r2 == C2 _atom_independent on the C3 operator tuple", "-", "frozen functions",
           A_mix == FC._atom_independent(*tup), {j: str(v) for j, v in A_mix.items()})
    for j in ("A0", "A1", "A2"):
        record(f"R2.1-{j}", f"A_mixed {j} float", c3["A"][j], "C3_FORECAST.json cells[308].A",
               float(A_mix[j]) == c3["A"][j], float(A_mix[j]))
    record("R2.1-A0exact", "A0_mixed exact == C4 A0_certified", "exact string", "C4_THRESHOLDS.json cells[308].A0_certified (l.35)",
           str(A_mix["A0"]) == c4["A0_certified"], str(A_mix["A0"]))
    ln, row = line_of(P_C3ADJ, "| 308 | +0.094564 | **")      # the section-K row (l.192 is the section-E row)
    cellsK = [x.strip().strip("*").replace("**", "") for x in row.strip().strip("|").split("|")]
    record("R2.1-A0-4dp", "A0 certified (4 dp)", cellsK[3], f"C3_ADJUDICATION.md:{ln} (section K)",
           f"{float(A_mix['A0']):.4f}" == cellsK[3], f"{float(A_mix['A0']):.4f}")
    abar_eff_is_tau_over_dlo = A_mix["A0"] == tup[1] / tup[3] and tup[1] / tup[3] < tup[0]
    record("R2.1-eff", "A0_mixed = tau/D_lo (< Abar)", "C3 adj. section K '5.2185 (= tau/D_lo)'", "C3_ADJUDICATION.md section K text",
           abar_eff_is_tau_over_dlo, bool(abar_eff_is_tau_over_dlo))

    e = res["P_MIX"] = evaluate("P_MIX", A_mix)
    record("R2.2", "Gamma(C3 mixed) float", c3["Gamma"], "C3_FORECAST.json cells[308].Gamma", float(e["Gamma"]) == c3["Gamma"], float(e["Gamma"]))
    record("R2.2b", "Gamma(C3 mixed) float", c3e["Gamma"], "C3_EXECUTION.json per_cell[308].Gamma", float(e["Gamma"]) == c3e["Gamma"], float(e["Gamma"]))
    g6 = re.search(r"[+-]?\d+\.\d+", cellsK[1]).group(0)
    record("R2.2c", "Gamma(C3 mixed) 6 dp", g6, f"C3_ADJUDICATION.md:{ln}", f"{float(e['Gamma']):+.6f}" == g6, f"{float(e['Gamma']):+.6f}")
    record("R2.2d", "magnitude(C3 mixed) float", c3["magnitude"], "C3_FORECAST.json cells[308].magnitude",
           float(e["mag"]) == c3["magnitude"], float(e["mag"]))
    record("R2.2e", "pass flag (C3 mixed)", c3["closes"], "C3_FORECAST.json cells[308].closes", e["pass"] == c3["closes"], e["pass"])

    A_ko = {"A0": A_mix["A0"], "A1": F(0), "A2": F(0)}
    e = res["P_KO"] = evaluate("P_KO", A_ko)
    record("R2.3", "Gamma(A0_mixed,0,0) float", c4["Gamma_A1A2_zero_at_certified_A0"], "C4_THRESHOLDS.json cells[308] (l.37)",
           float(e["Gamma"]) == c4["Gamma_A1A2_zero_at_certified_A0"], float(e["Gamma"]))
    k6 = re.search(r"[+-]?\d+\.\d+", cellsK[2]).group(0)
    record("R2.3b", "Gamma(A0_mixed,0,0) 6 dp", k6, f"C3_ADJUDICATION.md:{ln}", f"{float(e['Gamma']):+.6f}" == k6, f"{float(e['Gamma']):+.6f}")
    record("R2.3c", "closes at A1=A2=0", c4["closes_at_A1A2_zero"], "C4_THRESHOLDS.json cells[308]", e["pass"] == c4["closes_at_A1A2_zero"], e["pass"])

    # critical A0: exact root of the affine map A0 -> Gamma(A0, 0, 0)
    A0s = -G0 / (rx * Pbar[2])
    e = res["P_CRIT"] = evaluate("P_CRIT", {"A0": A0s, "A1": F(0), "A2": F(0)})
    cr = c4["critical_A0"]
    lo_b, hi_b = F(cr["closes_below_exact"]), F(cr["open_at_or_above_exact"])
    record("R2.4a", "Gamma at the exact root == 0 (frozen consumer)", "0", "definition", e["Gamma"] == 0, str(e["Gamma"]))
    record("R2.4b", "A0* inside C4's bisection bracket", "[closes_below_exact, open_at_or_above_exact]",
           "C4_THRESHOLDS.json cells[308].critical_A0 (l.44,46)", lo_b <= A0s <= hi_b, str(A0s))
    record("R2.4c", "A0* <= outward 12 dp and rounds to it", cr["outward_rounded_12dp"],
           "C4_THRESHOLDS.json l.47; C4_TARGET_RECONSTRUCTION.md:76",
           A0s <= F(cr["outward_rounded_12dp"]) and f"{float(A0s):.12f}" == cr["outward_rounded_12dp"], f"{float(A0s):.12f}")
    record("R2.4d", "A0* 4 dp", cellsK[4], f"C3_ADJUDICATION.md:{ln}", f"{float(A0s):.4f}" == cellsK[4], f"{float(A0s):.4f}")
    ln76, row76 = line_of(P_C4REC, "| 308 | 5.2185")
    c76 = [x.strip().replace("**", "") for x in row76.strip().strip("|").split("|")]
    record("R2.4e", "critical A0 in C4 phase-1 table", c76[4], f"C4_TARGET_RECONSTRUCTION.md:{ln76}",
           f"{float(A0s):.12f}" == c76[4], f"{float(A0s):.12f}")
    fac, pct = A_mix["A0"] / A0s, 100 * (1 - A0s / A_mix["A0"])
    record("R2.5a", "A0 reduction factor (float, 12 sig. digits)", cr["A0_reduction_factor_needed_from_certified"],
           "C4_THRESHOLDS.json l.40", f"{float(fac):.12g}" == f"{cr['A0_reduction_factor_needed_from_certified']:.12g}", float(fac))
    record("R2.5a-exactfloat", "A0 reduction factor, float equality", cr["A0_reduction_factor_needed_from_certified"],
           "C4_THRESHOLDS.json l.40", float(fac) == cr["A0_reduction_factor_needed_from_certified"], float(fac))
    record("R2.5b", "A0 reduction percent (float, 12 sig. digits)", cr["A0_reduction_percent_needed"], "C4_THRESHOLDS.json l.41",
           f"{float(pct):.12g}" == f"{cr['A0_reduction_percent_needed']:.12g}", float(pct))
    record("R2.5b-exactfloat", "A0 reduction percent, float equality", cr["A0_reduction_percent_needed"], "C4_THRESHOLDS.json l.41",
           float(pct) == cr["A0_reduction_percent_needed"], float(pct))
    mK = re.search(r"×(\d+\.\d+) \((\d+\.\d+) %\)", cellsK[5])
    record("R2.5c", "C3 adj. factor and percent", f"x{mK.group(1)} ({mK.group(2)} %)", f"C3_ADJUDICATION.md:{ln}",
           f"{float(fac):.4f}" == mK.group(1) and f"{float(pct):.1f}" == mK.group(2), f"x{float(fac):.4f} ({float(pct):.1f} %)")

    # ---------------------------------------------------------------- R3: C4 section-4 statement
    ln52, row52 = line_of(P_C4OND, "18.2496")
    m52 = re.search(r"(\d+\.\d+)× at cell 308 under `A0 = (\d+\.\d+)`", row52)
    a0_4311 = F(m52.group(2))
    s_star = rx * (2 * A_mix["A1"] * Pbar[1] + A_mix["A2"] * Pbar[0]) / -(G0 + rx * a0_4311 * Pbar[2])
    e = res["P_4311"] = evaluate("P_4311", {"A0": a0_4311, "A1": A_mix["A1"] / s_star, "A2": A_mix["A2"] / s_star})
    record("R3.1a", "Gamma at (4.311, A1_mix/s*, A2_mix/s*) == 0 (frozen consumer)", "0", "definition of s*", e["Gamma"] == 0, str(e["Gamma"]))
    record("R3.1b", "s* 4 dp", m52.group(1), f"OPEN_NOTES_DISPOSITION_C4.md:{ln52}", f"{float(s_star):.4f}" == m52.group(1), f"{float(s_star):.4f}")
    ln186, row186 = line_of(P_C4ADJ, "still requires an 18.2")
    m186 = re.search(r"(\d+\.\d+)× reduction", row186)
    record("R3.1c", "s* 1 dp", m186.group(1), f"C4_ADJUDICATION.md:{ln186}", f"{float(s_star):.1f}" == m186.group(1), f"{float(s_star):.1f}")
    ln121, row121 = line_of(P_C4REC, "18.2496x reduction")
    record("R3.1d", "s* 4 dp (phase-1 text)", "18.2496", f"C4_TARGET_RECONSTRUCTION.md:{ln121}",
           f"{float(s_star):.4f}" in row121, f"{float(s_star):.4f}")
    txt = P_C4OND.read_text()
    m53 = re.search(r"`Gamma =\s*\+(\d+\.\d+)` at `A0 = (\d+\.\d+)` with `A1 = A2 = 0`", txt)
    a0_4375 = F(m53.group(2))
    e = res["P_4375"] = evaluate("P_4375", {"A0": a0_4375, "A1": F(0), "A2": F(0)})
    record("R3.2a", "Gamma(4.375229,0,0) 9 dp", "+" + m53.group(1), "OPEN_NOTES_DISPOSITION_C4.md:52-53",
           f"{float(e['Gamma']):+.9f}" == "+" + m53.group(1), f"{float(e['Gamma']):+.9f}")
    record("R3.2b", "Gamma(4.375229,0,0) > 0 and Pbar1, Pbar0 >= 0 and intersection non-empty (=> open at every (A1,A2) >= 0)",
           "impossible at any (A1, A2)", "C4_ADJUDICATION.md:187-188",
           e["Gamma"] > 0 and Pbar[1] >= 0 and Pbar[0] >= 0 and e["regime"]["intersection_nonempty"], True)
    record("R3.2c", "4.375229 > A0*", "-", "consistency", a0_4375 > A0s, True)

    # ---------------------------------------------------------------- R4: affine structure
    e = res["P_ZERO"] = evaluate("P_ZERO", {"A0": F(0), "A1": F(0), "A2": F(0)})
    record("R4.3", "Gamma(0,0,0) float", c4["monotone"]["Gamma_at_A0_zero"], "C4_THRESHOLDS.json l.51",
           float(e["Gamma"]) == c4["monotone"]["Gamma_at_A0_zero"], float(e["Gamma"]))
    record("R4.3b", "Gamma(0,0,0) == g_hi + rho x_hi |C_lo|", "-", "graph section 0 formula", e["Gamma"] == G0, str(G0))
    for nm, v in res.items():
        record(f"R4.1-{nm}", "all structural checks (affine formula, independent path, p independent of A, lo/hi)", "-",
               "K5_TAIL_DEPENDENCY_GRAPH.md:32", all(v["checks"].values()), v["checks"])
        record(f"R4.2-{nm}", "all regime facts", "-", "K5_TAIL_DEPENDENCY_GRAPH.md:25-28", all(v["regime"].values()), v["regime"])
    record("R4.4", "Pbar0, Pbar1, Pbar2 > 0 and rho*x_hi > 0", "-", "structural",
           all(Pbar[j] > 0 for j in range(3)) and rx > 0, True)

    coeff = {"rho": rho, "x_hi": x_hi, "e0": e0, "R_hi": R_hi, "D_lo": D_lo, "g_hi": g_hi, "rho_x_hi": rx,
             "C_lo": C_lo, "C_hi": C_hi, "Pbar0": Pbar[0], "Pbar1": Pbar[1], "Pbar2": Pbar[2],
             "R2_lo": H0, "R2_hi": H1, "M_R2": M0, "G0_intercept": G0, "A0_critical": A0s, "s_star_at_4311": s_star}
    out = {
        "schema": "rebaseguard.p5y.k5.cell308-research.streamA.recon.v1",
        "class": "HISTORICAL_RECONSTRUCTION", "preregistration": "history/recon/RECON_PREREGISTRATION.md",
        "route_R1": "route 1: frozen consumer functions (tct_rule.tail_enclosure + crosscheck, c2_d5_forecast.direct) on committed inputs",
        "input_provenance": prov,
        "C4_supply_identification": "c4_common.cell_supply -> c3_selector.build -> C3 operator-mixed supply (documentary)",
        "comparisons": cmp_,
        "all_equal": all(c["equal"] for c in cmp_),
        "coefficients_exact": {k: str(v) for k, v in coeff.items()},
        "coefficients_float": {k: float(v) for k, v in coeff.items()},
        "points": {k: {"A_exact": v["A_exact"], "Gamma_exact": str(v["Gamma"]), "Gamma_float": float(v["Gamma"]),
                       "lo_exact": str(v["lo"]), "hi_exact": str(v["hi"]), "M_exact": str(v["M"]), "pass": v["pass"],
                       "regime": v["regime"], "checks": v["checks"]} for k, v in res.items()},
        "new_target_evaluations": 0,
        "note": "every evaluation point is a committed supply or the point of a committed statement (see pre-registration)",
    }
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    bad = [c["item"] for c in cmp_ if not c["equal"]]
    q.log_event("history/recon/recon_308.py", "pre-registered R1-R4 reconstruction -- END",
                klass="HISTORICAL_RECONSTRUCTION", cells_touched=[{"detector": "CUSUM", "m": 5, "cell": CELL}],
                agent="streamA", notes=f"{len(cmp_)} comparisons, {len(bad)} unequal: {bad}; 7 committed evaluation points; "
                "output history/recon/C3_KNOCKOUT_RECONSTRUCTION.json")
    print(json.dumps({"comparisons": len(cmp_), "unequal": bad, "out_sha256": sha256(OUT.read_bytes())}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
