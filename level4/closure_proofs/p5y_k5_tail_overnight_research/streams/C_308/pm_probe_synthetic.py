"""Exact synthetic probe (producer; review F8): atom functional norms of R, dR, d2R on finite-state drift families,
against the positive-kernel majorant and Lemma G. Writes validation/PM_PROBE_SYNTHETIC.json.

Declared set (unchanged from the original probe): seeds 1..8, n = 6 + seed % 4, kill = 1/20, e = 1/8.
No CUSUM cell and no drift of the CUSUM model is involved (these are abstract finite-state chains).
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
sys.path.insert(0, str(NS / "code"))
import ov_fixtures as X  # noqa: E402
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()


def absm(A):
    return [[abs(a) for a in r] for r in A]


def rowsum_at(A, a=0):
    return sum(abs(x) for x in A[a])


def main():
    rows = []
    for seed in range(1, 9):
        n = 6 + seed % 4
        fam = X.random_family(n, seed, e_range=(F(0), F(1, 4)), kill=F(1, 20))
        e = F(1, 8)
        R = fam.R(e)
        K1, K2 = fam.K(e, 1), fam.K(e, 2)
        one = [F(1)] * n
        C, k1, k2 = X.op_norm(R), X.op_norm(K1), X.op_norm(K2)
        Lam = sum(R[0])
        dR = X.mat_mul(X.mat_mul(R, K1), R)
        d2R = X.mat_add(X.mat_scale(X.mat_mul(X.mat_mul(dR, K1), R), 2), X.mat_mul(X.mat_mul(R, K2), R))
        A1t, A2t = rowsum_at(dR), rowsum_at(d2R)
        w = X.mat_vec(R, one)
        v = X.mat_vec(R, X.mat_vec(absm(K1), w))
        pm1 = v[0]
        pm2 = 2 * X.mat_vec(R, X.mat_vec(absm(K1), v))[0] + X.mat_vec(R, X.mat_vec(absm(K2), w))[0]
        G1, G2 = k1 * C * C, k2 * C * C + 2 * k1 * k1 * C ** 3
        assert A1t <= pm1 <= G1 and A2t <= pm2 <= G2, "ordering true <= PM <= G violated"
        rows.append({"seed": seed, "n": n, "Lambda": float(Lam), "C_over_Lambda": float(C / Lam),
                     "A1_true": float(A1t), "A1_PM": float(pm1), "A1_G": float(G1),
                     "A2_true": float(A2t), "A2_PM": float(pm2), "A2_G": float(G2),
                     "PM_over_true_A1": float(pm1 / A1t), "PM_over_true_A2": float(pm2 / A2t),
                     "G_over_PM_A1": float(G1 / pm1), "G_over_PM_A2": float(G2 / pm2)})
    def rng(k):
        return [min(r[k] for r in rows), max(r[k] for r in rows)]
    out = {"schema": "OV_PM_PROBE_SYNTHETIC/1", "rows": rows,
           "summary": {k: rng(k) for k in ("PM_over_true_A1", "PM_over_true_A2", "G_over_PM_A1", "G_over_PM_A2")}}
    (NS / "validation" / "PM_PROBE_SYNTHETIC.json").write_text(json.dumps(out, indent=1))
    Q.log_execution("streams/C_308/pm_probe_synthetic.py", "PM probe producer (review F8)", cells_touched=[],
                    klass="SYNTHETIC_VALIDATION")
    print(json.dumps(out["summary"]))


if __name__ == "__main__":
    main()
