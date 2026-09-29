"""Independent Monte Carlo positive control for SRK decoy certificates (THEOREM_SRK section 8, test 7).

For each decoy file in evidence/srk_decoys/ and each certified index i, simulate the CUSUM chain (its own simple
implementation from OPERATOR_AUDIT section 1, not the certifier's kernel code) from the atom at the two block
endpoints, and estimate  m_i(e) = E_a[ sum_{n < tau} kbar_i(X_n) ]  with kbar_i evaluated by the union-window rule.
Control: max_e m_i(e) - 5 * se  <=  Gamma_i   (a certificate below the estimate by more than 5 se is a FAIL).
Tightness report: Gamma_i / max_e m_i(e).  Identity control (i = 0): k_0(x; e) = P(survive next step), hence
E_a[sum_{n<tau} k_0(X_n; e)] = E_a[tau] - 1 at a POINT drift; reported as a sanity row.

Decoy drifts only (declared); the real geometry is refused inside the band by the campaign guard.
"""
import json
import math
import zlib
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(NS / "code"))
import q309_guard as Q  # noqa: E402

SQ2PI = math.sqrt(2 * math.pi)


def he_abs_int(i, a, b, n=200):
    """float int_a^b |He_i| phi (midpoint rule on a fine grid; control only)."""
    if b <= a:
        return 0.0
    h = (b - a) / n
    s = 0.0
    for j in range(n):
        v = a + (j + 0.5) * h
        he = [1.0, v]
        for t in range(2, i + 1):
            he.append(v * he[-1] - (t - 1) * he[-2])
        s += abs(he[i]) * math.exp(-v * v / 2) / SQ2PI * h
    return s


def simulate(hh, kk, e, weight, n_paths, rng):
    c = hh + kk
    tot = tot2 = 0.0
    for _ in range(n_paths):
        p = m = 0.0
        acc = 0.0
        while True:
            acc += weight(p, m)
            z = rng.gauss(-e, 1.0)          # z + e ~ N(0, 1)
            if not (m - c < z < c - p):
                break
            p, m = max(0.0, p + z - kk), max(0.0, m - z - kk)
        tot += acc
        tot2 += acc * acc
    mean = tot / n_paths
    var = max(tot2 / n_paths - mean * mean, 0.0)
    return mean, math.sqrt(var / n_paths)


def run(n_paths=10000):
    rows = []
    for fp in sorted((NS / "evidence" / "srk_decoys").glob("*.json")):
        d = json.loads(fp.read_text())
        hh, kk = float(F(d["geometry"]["h"])), float(F(d["geometry"]["k"]))
        elo, ehi = F(d["block"][0]), F(d["block"][1])
        if F(d["geometry"]["h"]) == 5 and F(d["geometry"]["k"]) == F(1, 2):
            Q.guard_drift(elo, ehi)
        c = hh + kk
        for i_str, gam in d["Gamma"].items():
            if gam is None:
                continue
            i = int(i_str)
            # grid upper envelope (step 1/32): for x in [p0, p0+s) x [m0, m0+s) use the union window of the grid cell,
            # a valid upper bound of kbar_i(x) (window monotonicity), consistent with the certificate's box envelope.
            step = 1 / 32
            nb = int(round(hh / step)) + 1
            grid = {}

            def wbar(p, m, i=i):
                a, b = min(int(p / step), nb - 1), min(int(m / step), nb - 1)
                if (a, b) not in grid:
                    grid[(a, b)] = he_abs_int(i, b * step - c + float(elo), c - a * step + float(ehi))
                return grid[(a, b)]
            rng = random.Random(zlib.crc32(f"{fp.name}:{i}".encode()))
            est = [simulate(hh, kk, float(e), wbar, n_paths, rng) for e in (elo, ehi)]
            mmax, se = max(est, key=lambda t: t[0])
            G = float(F(gam))
            rows.append({"file": fp.name, "i": i, "Gamma": G, "mc_max": mmax, "se": se,
                         "control_pass": mmax - 5 * se <= G, "tightness": G / mmax if mmax > 0 else None})
    Q.log_execution("tests/srk_mc_control.py", "MC positive control on declared SRK decoys", klass="NONTARGET_DECOY",
                    notes=f"{len(rows)} rows, n_paths={n_paths}")
    ok = all(r["control_pass"] for r in rows) and len(rows) > 0
    return ok, rows


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    ok, rows = run(n)
    (NS / "evidence" / "SRK_MC_CONTROL.json").write_text(json.dumps({"ok": ok, "rows": rows}, indent=1))
    for r in rows:
        print(r["file"], r["i"], round(r["Gamma"], 4), round(r["mc_max"], 4), "+-", round(r["se"], 4),
              "PASS" if r["control_pass"] else "FAIL", round(r["tightness"] or 0, 4))
    print("ALL_PASS" if ok else "FAIL_OR_EMPTY")
    sys.exit(0 if ok else 1)
