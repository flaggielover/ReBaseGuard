"""C9 Phase 1 -- INDEPENDENT reconstruction of the authoritative cell-307 chain.

This module does not import any C8 module. It derives the chain from the frozen authoritative
sources: the adopted theorem-TC-T rule, ADOPTED_TAIL_INPUTS, TCT_INPUTS, REGISTRY_C1/C2 and
C5_FORECAST. C8's published numbers are then used ONLY as a cross-check.

    Gamma_k = g_hi + rho * x_hi * M          pass iff Gamma_k < 0
    M       = M_R2                     if the TC-T/R2 intersection is empty
            = min(M_R2, max(|a|,|b|))  otherwise,  [a,b] = [max(H_lo,lo), min(H_hi,hi)]
    [lo,hi] = TC-T whole-cell enclosure of R''_m, a function of A = (A0, A1, A2)

Lemma Dv' supplies A from the operator registry, with A0 = eff = min(Abar, tau/D_lo) and A1, A2 equal
to eff times fixed multipliers -- so ALL THREE are proportional to eff, and a uniform tightening of
the certified supply is exactly a reduction of eff. That proportionality is what makes "one uniform
eff factor" the right unit for C9's target.
"""
from __future__ import annotations

import json
import pathlib
import sys
from decimal import Decimal
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c9_common as C

sys.path.insert(0, str(C.BNS / "code"))
import tct_rule as T  # noqa: E402

CELL = 307
M = 5
D = lambda x: F(Decimal(str(x)))


class ChainRefusal(Exception):
    pass


class Chain:
    def __init__(self) -> None:
        self.R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
        adopted = json.loads((C.BNS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())
        self.adopted = adopted["cells"]
        self.reg2 = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
        self.blocks2 = {b["cell"]: b for b in self.reg2["blocks"]}
        reg1p = (C.CLOSURE / "p5y_k5_tail_operator_registry" / "evidence" / "registry_c1"
                 / "REGISTRY_C1.json")
        if not reg1p.exists():
            raise ChainRefusal(f"REGISTRY_C1 not found at {reg1p}; the operator-mixed supply cannot "
                               f"be built and C9 must not silently fall back to C2 alone")
        self.blocks1 = {b["cell"]: b for b in C.load(reg1p)["blocks"]}
        self.d5 = C.load(C.C2 / "evidence" / "phase_d5" / "C2_D5_FORECAST.json")
        self.fc5 = C.load(C.C5 / "evidence" / "forecast" / "C5_FORECAST.json")["cells"]
        self.meas, self.aux, self.geom, self.H, self.M0, self.g_hi = {}, {}, {}, {}, {}, {}
        for k in (305, 306, 307, 308, 309):
            m = json.loads((C.BNS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes())
            ad = self.adopted[str(k)]
            m["C_upper"] = ad["C_upper"]
            self.meas[k], self.aux[k] = m, ad["auxiliary_evidence"]
            b = self.blocks2[k]
            e_lo, e_hi = F(b["e_lo"]), F(b["e_hi"])
            self.geom[k] = {"e_lo": e_lo, "e_hi": e_hi, "e0": F(b["e0"]),
                            "rho": (e_hi - e_lo) / 2, "x_hi": e_hi}
            mb = ad["m"][str(M)]
            self.H[k] = (F(mb["R2_interval"]["lo"]), F(mb["R2_interval"]["hi"]))
            self.M0[k] = F(mb["M_R2"])
            cell = self.d5["cells"][str(k)]
            self.g_hi[k] = F(cell["Gamma_exact"]) - self.geom[k]["rho"] * self.geom[k]["x_hi"] * \
                F(cell["M_after_exact"])

    # ---- Lemma Dv', re-derived here rather than imported ------------------------------------
    @staticmethod
    def atom_constants(Abar, tau, C_T, D_lo, D1, D2, K1, K2):
        if not (D_lo > 0 and tau >= 1 and C_T >= tau and Abar >= 1):
            raise ChainRefusal("operator constants violate tau>=1, C>=tau, D_lo>0, Abar>=1")
        eff = Abar if Abar < tau / D_lo else tau / D_lo
        d1, d2 = D1 / D_lo, D2 / D_lo
        return {"eff": eff, "A0": eff, "A1": eff * (K1 * C_T + d1),
                "A2": eff * (2 * K1 ** 2 * C_T ** 2 + K2 * C_T + 2 * K1 * C_T * d1
                             + 2 * d1 ** 2 + d2)}

    # The C3 mechanism: componentwise-BEST operator tuple over the certified registries, then
    # Lemma Dv'. "Best" is MIN on the upper-bound fields and MAX on D_lo, which is a lower bound.
    # Taking a plain componentwise min over all fields would be WRONG for D_lo and would silently
    # weaken the supply; C3 carries mutants M01/M02 for exactly those two errors.
    OPERATOR_UPPER = ("Abar", "tau", "C_T", "D1", "D2")
    OPERATOR_LOWER = ("D_lo",)

    def operator_best(self, blocks: dict) -> dict:
        tup = {}
        for f in self.OPERATOR_UPPER:
            tup[f] = min(F(b[f]) for b in blocks.values())
        for f in self.OPERATOR_LOWER:
            tup[f] = max(F(b[f]) for b in blocks.values())
        return tup

    def supply_from_block(self, k, blk, K1, K2):
        return self.atom_constants(*(F(blk[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")),
                                   K1, K2)

    # ---- the clause ---------------------------------------------------------------------------
    def enclosure(self, k, A):
        lo, hi, _ = T.tail_enclosure(self.R, self.meas[k], self.aux[k],
                                     {j: A[j] for j in ("A0", "A1", "A2")}, M, None)
        return lo, hi

    def M_of(self, k, A):
        lo, hi = self.enclosure(k, A)
        Hlo, Hhi = self.H[k]
        a, b = max(Hlo, lo), min(Hhi, hi)
        if a > b:
            return self.M0[k]
        mm = max(abs(a), abs(b))
        return self.M0[k] if self.M0[k] < mm else mm

    def gamma(self, k, A):
        g = self.geom[k]
        return self.g_hi[k] + g["rho"] * g["x_hi"] * self.M_of(k, A)

    def budget_C5T(self, k):
        return D(self.fc5[str(k)]["M_needed_C5T"])

    def passes_C5T(self, k, A):
        return self.M_of(k, A) < self.budget_C5T(k)
