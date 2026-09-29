"""Certificate-level adversarial tests (THEOREM_SRK section 8 tests 1, 2, 8, 10; review R1 B4), judged by the
INDEPENDENT verifier (verify/srk_verify_indep.py, used as a tool; it was written from the spec by a separate agent).
Declared decoy (synthetic geometry, not band-guarded): h = 3, k = 1/2, block [1/4, 9/32], degree 8.

  T1   too-small weight: certificate produced against kbar_1 / 4 but claiming kbar_1 -> verifier must REJECT
  T2   taboo presented as whole: a taboo-kernel certificate relabelled 'whole' (rehashed) -> verifier must REJECT;
       the genuine taboo certificate -> ACCEPT
  T8   constant-weight identity: E_a[sum_{n<tau} k_0(X_n)] = E_a[tau] - 1 (Monte Carlo, checks the simulator);
       Gamma_0 >= that estimate - 5 se; Gamma_0 <= max_E W(a) * (1 + 2^-4) (sanity; a control that can fail)
  T10  determinism: two independent productions give byte-identical certificates (same sha256); JSON round trip;
       the genuine whole-kernel certificate is ACCEPTED by the verifier
"""
import copy
import json
import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
for p_ in (NS / "impl", NS / "verify", NS / "code"):
    sys.path.insert(0, str(p_))
import srk_certify as S  # noqa: E402
import srk_kernel as KX  # noqa: E402
import srk_gate as GT  # noqa: E402
import srk_verify_indep as VI  # noqa: E402

G3 = KX.Geom(3, F(1, 2))
LO, HI, D = F(1, 4), F(9, 32), 8


def one_cert(i, whole=True, mutant=""):
    W = S.certify_W(G3, LO, HI, D, log=lambda s: None, whole=whole)
    V = S.certify_weight(G3, i, LO, HI, D, W, log=lambda s: None, mutant=mutant)
    blk = {"geometry": {"h": S.fstr(G3.h), "k": S.fstr(G3.k)}, "block": [S.fstr(LO), S.fstr(HI)],
           "rungs": [{"degree": D, "W": W, "V": {i: V}}], "producer": S.producer_fingerprint()}
    return S.certificate_json(blk, i), W, V


def verdict(cert, kernel_file=None):
    r = VI.verify_cert(cert, kernel_file, N=8, max_depth=24, procs=1, log=None)
    return r["verdict"], r.get("reason")


def mc(e, weight, n, rng):
    c = float(G3.c)
    k = float(G3.k)
    tot = tot2 = 0.0
    for _ in range(n):
        p = m = 0.0
        acc = 0.0
        while True:
            acc += weight(p, m)
            z = rng.gauss(-e, 1.0)
            if not (m - c < z < c - p):
                break
            p, m = max(0.0, p + z - k), max(0.0, m - z - k)
        tot += acc
        tot2 += acc * acc
    mean = tot / n
    return mean, math.sqrt(max(tot2 / n - mean * mean, 0.0) / n)


def run():
    res = {}
    gen, W, V = one_cert(1)
    gen2, _, _ = one_cert(1)
    res["T10_deterministic_sha"] = gen["sha256"] == gen2["sha256"]
    res["T10_json_round_trip"] = all(S.poly_from_json(S._poly_json(P)) == P for P in (V["_V"][0], V["_V"][1]))
    res["T10_sha_consistent"] = GT.canonical_sha(gen) == gen["sha256"]
    v_gen = verdict(gen)
    res["T10_genuine_ACCEPT"] = v_gen[0] == "ACCEPT"
    q, _, _ = one_cert(1, mutant="quarter_weight")
    v_q = verdict(q)
    res["T1_quarter_weight_REJECT"] = v_q[0] == "REJECT"
    tab, Wt, _ = one_cert(1, whole=False)
    v_tab = verdict(tab)
    res["T2_taboo_genuine_ACCEPT"] = v_tab[0] == "ACCEPT"
    relab = copy.deepcopy(tab)
    relab["kernel"] = "whole"
    relab["sha256"] = GT.canonical_sha(relab)
    v_rel = verdict(relab)
    res["T2_taboo_as_whole_REJECT"] = v_rel[0] == "REJECT"
    z0, W0, V0 = one_cert(0)
    rng = random.Random(20260929)
    e = float(HI)
    c = float(G3.c)
    k0 = lambda p, m: 0.5 * math.erfc(-(c - p + e) / math.sqrt(2)) - 0.5 * math.erfc(-(m - c + e) / math.sqrt(2))  # noqa
    m_k0, se_k0 = mc(e, k0, 20000, rng)
    m_tau, se_tau = mc(e, lambda p, m: 1.0, 20000, rng)
    res["T8_identity_mc"] = abs(m_k0 - (m_tau - 1)) <= 5 * math.hypot(se_k0, se_tau)
    g0 = float(F(z0["Gamma"]))
    res["T8_Gamma0_ge_mc"] = g0 >= m_k0 - 5 * se_k0
    res["T8_Gamma0_le_W"] = g0 <= float(W0["W_at_atom_max"]) * (1 + 2 ** -4)
    detail = {"verdicts": {"genuine": v_gen, "quarter": v_q, "taboo": v_tab, "taboo_as_whole": v_rel},
              "T8": {"Gamma0": g0, "mc_k0": m_k0, "se_k0": se_k0, "mc_tau": m_tau, "se_tau": se_tau,
                     "W_at_atom_max": float(W0["W_at_atom_max"])}}
    return all(res.values()), res, detail


if __name__ == "__main__":
    ok, res, detail = run()
    out = {"ok": ok, "checks": res, "detail": detail}
    (NS / "evidence" / "SRK_CERT_MUTANTS.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))
    sys.exit(0 if ok else 1)
