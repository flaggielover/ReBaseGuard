"""PS1 identity-preserving optimisations of the two dominant certifier kernels (no frozen module is edited).

OPT-S (endpoint strips): in the frozen StripSide.contract(cand, s) the matrices Ct, Ca, the products
Sa = Ct*Pa[a], the polynomials G[a][b] = sum_j Sp[j]*Q[j][b] and the error sums exc, ezc, supY depend on the
candidate and the strip panel only, never on the moment shift s; only G*w[s], supw[s] and rw[s] do. StripSideMemo
computes the s-independent part ONCE per (side, candidate) with the identical arb operations in the identical order,
then performs, per shift, exactly the frozen s-dependent loop (same (a, b, m) accumulation order into out and e1).
OPT-C (O9 core): in the frozen contract_O9(pd, cand, Rbig, absvecs) the matrices Ct, Ca depend on the candidate only
and the error vectors t1, t2x, t2z and sums ex, ez on (candidate, panel) only; contract_O9_memo caches them (same
operations, same order) and recomputes every shift-dependent product exactly as frozen, returning ex*N0, ez*N0.
Arb arithmetic is deterministic at fixed precision, so every returned ball is bit-identical; this is TESTED on real
PS1 patches (tests/test_opt_identity.py and evidence/identity/*), not assumed.
"""
from flint import arb, arb_mat, arb_poly

import sr_o9_endpoint_strips as ES
import sr_o9_patch_certifier as PC

NN, DP = ES.NN, ES.DP


class StripSideMemo(ES.StripSide):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._memo = {}

    def _cand_part(self, cand):
        hit = self._memo.get(id(cand))
        if hit is not None and hit[0] is cand:
            return hit[1]
        Cm, Ca = arb_mat(NN, NN), arb_mat(NN, NN)
        for i in range(NN):
            for j in range(NN):
                Cm[i, j] = cand[i][j]
                Ca[i, j] = arb(cand[i][j].abs_upper())
        Ct = Cm.transpose()
        Gs = {}
        for a in range(DP):
            Sa = Ct * self.Pa[a]
            Sp = [arb_poly([Sa[j, k] for k in range(ES.ZP)]) for j in range(NN)]
            for b in range(DP):
                G = arb_poly([])
                for j in range(NN):
                    G = G + Sp[j] * self.Q[j][b]
                Gs[a, b] = G
        magW, exW, ezW = self.av
        t1, t2x, t2z = Ca * magW, Ca * exW, Ca * ezW
        exc = ezc = supY = arb(0)
        sh = self.sh
        for i in range(NN):
            exc += sh.exV[i] * t1[i, 0] + sh.magV[i] * t2x[i, 0]
            ezc += sh.ezV[i] * t1[i, 0] + sh.magV[i] * t2z[i, 0]
            supY += sh.magV[i] * t1[i, 0]
        val = (Gs, exc, ezc, supY)
        self._memo[id(cand)] = (cand, val)
        return val

    def contract(self, cand, s):
        Gs, exc, ezc, supY = self._cand_part(cand)
        out = [[arb(0)] * DP for _ in range(DP)]
        e1 = arb(0)
        w = self.w[s]
        for a in range(DP):
            for b in range(DP):
                G = Gs[a, b]
                for m, gm in enumerate((G * w).coeffs()):
                    val = gm / arb(m + 1)
                    if self.side == "L":
                        pa, pb = a, b + m + 1
                    else:
                        pa, pb = a + m + 1, b
                        if m % 2:
                            val = -val
                    if pa <= ES.D and pb <= ES.D:
                        out[pa][pb] += val
                    else:
                        e1 += val.abs_upper() * self.Hp[pa] * self.Hp[pb]
        e2 = self.H.abs_upper() * self.supw[s] * (exc + ezc)
        e3 = self.H.abs_upper() * self.rw[s] * supY
        return out, e1 + e2 + e3, {"e1": float(e1), "e2": float(e2), "e3": float(e3)}


def contract_O9_memo(pd, cand, Rbig, absvecs, memo, c, kp):
    P = PC.packet()
    n, Dp, Zp = P.n, P.Dp, P.Zp
    s = pd.shared
    ent = memo.get(("C", c))
    if ent is None or ent[0] is not cand:
        C = arb_mat(n, n)
        Ca = arb_mat(n, n)
        for i in range(n):
            for j in range(n):
                C[i, j] = cand[i][j]
                Ca[i, j] = arb(cand[i][j].abs_upper())
        ent = (cand, C.transpose(), Ca)
        memo[("C", c)] = ent
    _, Ct, Ca = ent
    Sbig = Ct * Rbig
    SA = arb_mat(Dp, n * Zp)
    for j in range(n):
        for a in range(Dp):
            off = a * Zp
            for k in range(Zp):
                SA[a, j * Zp + k] = Sbig[j, off + k]
    OUT = SA * s.Qflat
    coef = [[OUT[a, bq] for bq in range(Dp)] for a in range(Dp)]
    er = memo.get(("E", c, kp))
    if er is None or er[0] is not s:
        magW, exW, ezW = absvecs
        t1 = Ca * magW
        t2x = Ca * exW
        t2z = Ca * ezW
        ex = ez = arb(0)
        for i in range(n):
            ex += s.exV[i] * t1[i, 0] + s.magV[i] * t2x[i, 0]
            ez += s.ezV[i] * t1[i, 0] + s.magV[i] * t2z[i, 0]
        er = (s, ex, ez)
        memo[("E", c, kp)] = er
    _, ex, ez = er
    return coef, ex * pd.N0, ez * pd.N0
