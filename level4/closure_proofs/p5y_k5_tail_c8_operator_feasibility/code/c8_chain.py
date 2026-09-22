"""C8 -- exact reconstruction of the load-bearing downstream chain, from committed evidence only.

WHAT THIS IS NOT. No kernel is evaluated, no operator is certified, no new scientific value is
created. `tail_enclosure` is the frozen theorem-TC-T rule: exact rational arithmetic over measured
constants that are already committed. Driving it with a different (A0, A1, A2) tuple is a
DETERMINISTIC TRANSFORMATION OF COMMITTED EVIDENCE, which the C8 boundary permits, and every such
evaluation at a tuple that is not a certified supply is labelled COUNTERFACTUAL.

THE CHAIN. For a tail cell k the K5-B direct clause is

    Gamma_k = g_hi + rho * x_hi * M,          pass iff Gamma_k < 0

    g_hi  = R_interval.hi - e0 * D_interval.lo        (independent of A)
    rho   = (e_hi - e_lo)/2, the cell half-width
    x_hi  = e_hi, the cell's right endpoint
    M     = min(M_R2, max(|a|, |b|)),  [a,b] = [max(H_lo, lo), min(H_hi, hi)]
    [lo,hi] = TC-T whole-cell enclosure of R''_m, a function of A = (A0, A1, A2)

A enters ONLY through [lo, hi]. g_hi, rho, x_hi and H are A-independent.

Lemma Dv' supplies A from the operator registry:

    A0 = eff = min(Abar, tau / D_lo)
    A1 = eff * (K1*C + d1)
    A2 = eff * (2*K1^2*C^2 + K2*C + 2*K1*C*d1 + 2*d1^2 + d2),   d1 = D1/D_lo, d2 = D2/D_lo

so all three are PROPORTIONAL to eff. A uniform reduction of A is exactly a reduction of eff.

g_hi is not carried per-cell in any single committed artifact, so it is recovered exactly from the
committed pair (Gamma_exact, M_after_exact) of the sealed D4 supply:

    g_hi = Gamma_exact - rho * x_hi * M_after_exact

and the recovery is then CHECKED against every other committed supply for that cell. If the affine
relation did not hold across five independent supplies the reconstruction would be refused.
"""
from __future__ import annotations

import json
import pathlib
import sys
from decimal import Decimal
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c8_common as C

BNS = C.CLOSURE / "p5y_k5_m5_tail_closure"
sys.path.insert(0, str(BNS / "code"))
import tct_rule as T  # noqa: E402

CELLS = (305, 306, 307, 308, 309)


class ChainRefusal(Exception):
    pass


def _dec(x) -> F:
    return F(Decimal(str(x)))


class Chain:
    def __init__(self) -> None:
        self.R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
        adopted = json.loads((BNS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())
        self.adopted = adopted["cells"]
        self.meas, self.aux, self.geom = {}, {}, {}
        d5 = C.load(C.C2 / "evidence" / "phase_d5" / "C2_D5_FORECAST.json")
        self.d5 = d5
        blocker = C.load(C.CLOSURE / "p5y_k5_tail_c3_closure" / "evidence" / "phase_c1" /
                         "C3_BLOCKER.json")["cells"]
        self.blocker = blocker
        reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
        self.blocks = {b["cell"]: b for b in reg["blocks"]}

        for k in CELLS:
            m = json.loads((BNS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes())
            ad = self.adopted[str(k)]
            m["C_upper"] = ad["C_upper"]
            self.meas[k], self.aux[k] = m, ad["auxiliary_evidence"]
            blk = self.blocks[k]
            e_lo, e_hi = F(blk["e_lo"]), F(blk["e_hi"])
            self.geom[k] = {"e_lo": e_lo, "e_hi": e_hi, "e0": F(blk["e0"]),
                            "rho": (e_hi - e_lo) / 2, "x_hi": e_hi}

        # The SEALED clip inputs. R2_interval and M_R2 are carried per m inside ADOPTED_TAIL_INPUTS
        # at cells[k]["m"][str(m)] -- in the very file this class already opens. An earlier version
        # of this module inspected only the TOP-LEVEL keys of that cell, missed the nested "m" block,
        # and concluded the clip was "unreachable from committed evidence". That was FALSE, and the
        # conservatism argument built on it was false too: above roughly twice the certified supply
        # the sealed M SATURATES at M_R2 while an unclipped magnitude grows without bound, so
        # dropping the clip reverses direction rather than being safe. The sealed clause is now
        # implemented as written.
        self.g_hi, self.H, self.M0 = {}, {}, {}
        for k in CELLS:
            cell = d5["cells"][str(k)]
            Mx = F(cell["M_after_exact"])
            Gx = F(cell["Gamma_exact"])
            g = self.geom[k]
            mblk = self.adopted[str(k)]["m"]["5"]
            self.H[k] = (F(mblk["R2_interval"]["lo"]), F(mblk["R2_interval"]["hi"]))
            self.M0[k] = F(mblk["M_R2"])
            self.g_hi[k] = Gx - g["rho"] * g["x_hi"] * Mx

    # ---------------------------------------------------------------------------------------
    def enclosure(self, k: int, A: dict) -> tuple[F, F]:
        lo, hi, _ = T.tail_enclosure(self.R, self.meas[k], self.aux[k], A, 5, None)
        return lo, hi

    def M_of(self, k: int, A: dict) -> F:
        """The SEALED clause, as c2_d5_forecast.direct() writes it:

            [a, b] = [max(H_lo, lo), min(H_hi, hi)],  H = R2_interval
            M      = M_R2                      if a > b   (empty intersection)
                   = min(M_R2, max(|a|, |b|))  otherwise

        Both H and M_R2 come from ADOPTED_TAIL_INPUTS cells[k]["m"]["5"]. Because M is capped at
        M_R2, Gamma SATURATES: no amount of degradation in A can push it past
        g_hi + rho * x_hi * M_R2. That saturation value is a real quantity C4 published, and an
        unclipped reconstruction would have reported Gamma growing without bound instead.
        """
        lo, hi = self.enclosure(k, A)
        Hlo, Hhi = self.H[k]
        a, b = max(Hlo, lo), min(Hhi, hi)
        if a > b:
            return self.M0[k]
        m = max(abs(a), abs(b))
        return self.M0[k] if self.M0[k] < m else m

    def gamma_saturation(self, k: int) -> F:
        """The largest Gamma the clause can ever report at this cell, i.e. at M = M_R2."""
        g = self.geom[k]
        return self.g_hi[k] + g["rho"] * g["x_hi"] * self.M0[k]

    def gamma(self, k: int, A: dict) -> F:
        g = self.geom[k]
        return self.g_hi[k] + g["rho"] * g["x_hi"] * self.M_of(k, A)

    def magnitude(self, k: int, A: dict) -> F:
        lo, hi = self.enclosure(k, A)
        return max(abs(lo), abs(hi))

    # ---------------------------------------------------------------------------------------
    def committed_supplies(self, k: int) -> dict:
        """The five committed (A, Gamma, magnitude) tuples for this cell."""
        out = {}
        for name, s in self.blocker[str(k)]["per_supply"].items():
            out[name] = {"A": {j: _dec(s["A"][j]) for j in ("A0", "A1", "A2")},
                         "Gamma_committed": _dec(s["Gamma"]),
                         "magnitude_committed": _dec(s["magnitude"]),
                         "requirement_committed": (None if s["requirement"] is None
                                                   else _dec(s["requirement"])),
                         "closes_committed": s["closes"]}
        return out

    def verify(self) -> dict:
        """Reproduce every committed supply. This is the check that licenses counterfactual use.

        C3_BLOCKER covers only the cells still OPEN when C3 ran, i.e. {306,307,308,309}; cell 305 had
        already been closed and adopted by C2, so it carries no per-supply block. Verification is
        scoped to the cells that actually have committed supplies, and the scoping is recorded rather
        than silently skipped.
        """
        rows, bad = [], []
        for k in sorted(int(x) for x in self.blocker):
            for name, s in self.committed_supplies(k).items():
                mag = self.magnitude(k, s["A"])
                gam = self.gamma(k, s["A"])
                dmag = abs(float(mag - s["magnitude_committed"]))
                dgam = abs(float(gam - s["Gamma_committed"]))
                ok = dmag < 1e-12 and dgam < 1e-12
                rows.append({"cell": k, "supply": name,
                             "magnitude_recomputed": float(mag),
                             "magnitude_committed": float(s["magnitude_committed"]),
                             "magnitude_abs_err": dmag,
                             "Gamma_recomputed": float(gam),
                             "Gamma_committed": float(s["Gamma_committed"]),
                             "Gamma_abs_err": dgam, "agrees": ok})
                if not ok:
                    bad.append((k, name, dmag, dgam))
        return {"rows": rows, "disagreements": bad, "all_agree": not bad,
                "cells_verified": sorted(int(x) for x in self.blocker),
                "cells_without_committed_supplies": [k for k in CELLS if str(k) not in self.blocker],
                "scoping_note": ("C3_BLOCKER carries per-supply tuples only for cells OPEN at C3 "
                                 "time. Cell 305 was closed and adopted by C2 and has no block.")}
