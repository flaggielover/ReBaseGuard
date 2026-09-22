"""C11R Phase 7 -- manufactured validation of the block-uniform drift layer and Khat_e.

Identities the implementation cannot satisfy by accident. The decisive one is SCALAR COLLAPSE:
with a degenerate drift interval every function here must reproduce C11's scalar certifier
BIT FOR BIT, not merely enclose it. Bit-equality is achievable only because the moment layer
carries its limits as exact rational pairs; anything that widens silently shows up immediately.
"""
from __future__ import annotations

import pathlib
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_idrift as I

sys.path.insert(0, str(C.C11 / "code"))
sys.path.insert(0, str(C.C7 / "code"))
import c11_certifier as X            # noqa: E402
import c7_gaussian as G              # noqa: E402

E_SCALAR = F(18355, 10000)
STATES = [(F(0), F(0)), (F(3), F(1)), (F(0), F(5)), (F(5), F(0)), (F(2), F(2)),
          (F(23, 5), F(0)), (F(1, 4), F(1, 4))]
WS = {"const9": {(0, 0): F(9)},
      "m_only": {(0, 0): F(99, 10), (0, 1): F(-3, 2)},
      "mixed": {(0, 0): F(4), (1, 0): F(1, 5), (0, 1): F(-1, 2)}}
results = []


def rec(cid, name, ok, detail):
    results.append({"id": cid, "name": name, "pass": bool(ok), "detail": detail})


def _same(a, b) -> bool:
    return (a.lo, a.hi) == (b.lo, b.hi)


def main() -> int:
    t0 = time.time()
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    e_lo, e_hi = F(tbl["drift_domain"]["e_lo"]), F(tbl["drift_domain"]["e_hi"])
    BLOCK = I.Blk(e_lo, e_hi)
    PT = I.Blk(E_SCALAR, E_SCALAR)

    # V1 -- standard-normal moments, over an interval window
    Ms = I.moments_iv(I.Blk(-12), I.Blk(12), 4)
    tgt = [1, 0, 1, 0, 3]
    rec("V1", "standard-normal moments are exactly 1, 0, 1, 0, 3",
        all(v.lo <= t <= v.hi for v, t in zip(Ms, tgt)),
        {"enclosures": [[float(v.lo), float(v.hi)] for v in Ms], "target": tgt})

    # V2 -- every Gaussian mass is a probability, over the WHOLE block
    masses, ok2 = [], True
    for p, m in STATES:
        h = I.alarm_prob_iv(p, m, BLOCK)
        good = h.lo >= 0 and h.hi <= 1
        ok2 = ok2 and good
        masses.append({"state": [str(p), str(m)], "h1": [float(h.lo), float(h.hi)], "in01": good})
    rec("V2", "the alarm probability lies in [0, 1] uniformly over the drift block", ok2,
        {"states": masses})

    # V3 -- (K_e 1)(p, m) = 1 - h1(p, m), over the block
    one = {(0, 0): F(1)}
    rows, ok3 = [], True
    for p, m in STATES:
        k1 = I.kernel_apply_iv(one, p, m, BLOCK)
        rhs = G.Iv(1, 1) - I.alarm_prob_iv(p, m, BLOCK)
        sep = max(k1.lo - rhs.hi, rhs.lo - k1.hi)
        good = sep <= 0
        ok3 = ok3 and good
        rows.append({"state": [str(p), str(m)], "separation": float(sep), "intersect": good})
    rec("V3", "kernel/alarm identity holds uniformly over the drift block", ok3, {"states": rows})

    # V4 -- the same identity for Khat_e: (Khat_e 1) = (K_e 1) - atom mass
    rows, ok4 = [], True
    for p, m in STATES:
        hat = I.kernel_apply_iv(one, p, m, BLOCK, atom_removed=True)
        full = I.kernel_apply_iv(one, p, m, BLOCK)
        at = I.atom_contribution_iv(one, p, m, BLOCK)
        sep = max(full.lo - (hat + at).hi, (hat + at).lo - full.hi)
        good = sep <= 0 and hat.hi <= full.hi + F(1, 10 ** 30)
        ok4 = ok4 and good
        rows.append({"state": [str(p), str(m)], "K_e": [float(full.lo), float(full.hi)],
                     "Khat_e": [float(hat.lo), float(hat.hi)],
                     "atom": [float(at.lo), float(at.hi)],
                     "separation": float(sep), "ok": good})
    rec("V4", "atom decomposition K_e = Khat_e + atom, and Khat_e <= K_e", ok4, {"states": rows})

    # V5 -- the atom window is non-empty exactly when p + m < 2K
    rows, ok5 = [], True
    for p, m in [(F(0), F(0)), (F(1, 4), F(1, 4)), (F(1, 2), F(1, 2)), (F(3, 4), F(1, 2)),
                 (F(1), F(0)), (F(2), F(2)), (F(0), F(9, 10))]:
        has = I._pieces(p, m)[3] is not None
        pred = bool(p + m < 2 * I.K)
        ok5 = ok5 and (has == pred)
        rows.append({"state": [str(p), str(m)], "atom_window": has, "predicted": pred})
    rec("V5", "the atom window is non-empty exactly when p + m < 2K = 1", ok5,
        {"cases": rows, "derivation": "m - K <= z <= K - p is non-empty iff m - K < K - p"})

    # V6 -- SCALAR COLLAPSE, bit for bit
    fails = []
    for nm, w in WS.items():
        for p, m in STATES:
            if not _same(X.kernel_apply(w, p, m, E_SCALAR), I.kernel_apply_iv(w, p, m, PT)):
                fails.append(f"kernel:{nm}:{p},{m}")
        for p, m in STATES:
            if not _same(X.alarm_prob(p, m, E_SCALAR), I.alarm_prob_iv(p, m, PT)):
                fails.append(f"alarm:{p},{m}")
        for box in ((F(0), F(1), F(0), F(1)), (F(1), F(2), F(0), F(1)), (F(4), F(5), F(0), F(1))):
            if not _same(X.kernel_box_upper(w, *box, E_SCALAR, 12),
                         I.kernel_box_upper_iv(w, *box, PT, 12)):
                fails.append(f"box:{nm}:{box}")
    rec("V6", "scalar collapse: a degenerate drift interval reproduces C11 BIT FOR BIT",
        not fails, {"mismatches": fails[:12], "mismatch_count": len(fails),
                    "why_it_matters": ("bit-equality, not containment. Containment would pass even "
                                       "if the interval extension had changed the mathematics and "
                                       "then widened enough to hide it.")})

    # V7 -- the block enclosure must CONTAIN every scalar enclosure inside the block
    rows, ok7 = [], True
    probe = [e_lo, (e_lo + e_hi) / 2, e_hi, e_lo + (e_hi - e_lo) / 3]
    w = WS["m_only"]
    for p, m in [(F(0), F(0)), (F(23, 5), F(0)), (F(2), F(2))]:
        blk = I.kernel_apply_iv(w, p, m, BLOCK)
        for e in probe:
            pt = X.kernel_apply(w, p, m, e)
            good = blk.lo <= pt.lo and pt.hi <= blk.hi
            ok7 = ok7 and good
            rows.append({"state": [str(p), str(m)], "e": str(e), "contained": good})
    rec("V7", "the block enclosure contains the scalar result at every probed drift", ok7,
        {"probes": len(rows), "failures": [r for r in rows if not r["contained"]],
         "note": ("a NECESSARY condition only -- containment at sample points does not establish "
                  "uniformity. Uniformity comes from carrying e as an interval, not from probing.")})

    # V8 -- monotonicity/extremum fixtures the enclosure rests on
    xs = [F(-3), F(-1), F(0), F(1), F(3)]
    mono = all(G.Phi(xs[i]).hi <= G.Phi(xs[i + 1]).lo for i in range(len(xs) - 1))
    peak = all(G.phi(F(0)).lo >= G.phi(x).hi for x in xs if x != 0)
    even = _same(G.phi(F(-7, 4)), G.phi(F(7, 4)))
    straddle = I._monomial_pair(F(-1), F(2), 2) == (F(0), F(4))
    rec("V8", "the facts the interval extension rests on: Phi increasing, phi even and peaked at 0,"
              " monomial extrema", mono and peak and even and straddle,
        {"Phi_increasing": mono, "phi_peak_at_zero": peak, "phi_even": even,
         "even_monomial_straddling_zero_has_infimum_0": straddle})

    # V9 -- outward rounding: widening the block can only widen the enclosure
    narrow = I.Blk(e_lo, (e_lo + e_hi) / 2)
    wide = BLOCK
    w = WS["m_only"]
    n = I.kernel_apply_iv(w, F(0), F(0), narrow)
    v = I.kernel_apply_iv(w, F(0), F(0), wide)
    rec("V9", "a wider drift block gives a wider enclosure (monotone in the block)",
        v.lo <= n.lo and n.hi <= v.hi,
        {"narrow": [float(n.lo), float(n.hi)], "wide": [float(v.lo), float(v.hi)]})

    # V10 -- precision escalation: more panels must not move a rigorous bound the wrong way
    w = {(0, 0): F(12), (0, 1): F(-3, 2)}
    a, b, c, d = F(0), F(1), F(0), F(1)
    b8 = I.kernel_box_upper_iv(w, a, b, c, d, BLOCK, 8).hi
    b16 = I.kernel_box_upper_iv(w, a, b, c, d, BLOCK, 16).hi
    b32 = I.kernel_box_upper_iv(w, a, b, c, d, BLOCK, 32).hi
    rec("V10", "precision escalation: the box bound tightens monotonically with panels",
        b32 <= b16 <= b8,
        {"panels_8": float(b8), "panels_16": float(b16), "panels_32": float(b32),
         "tightening_8_to_32": float(b8 - b32)})

    failed = [r["id"] for r in results if not r["pass"]]
    out = {"schema": "C11R_VALIDATION/1",
           "drift_block": {"e_lo": str(e_lo), "e_hi": str(e_hi),
                           "float": [float(e_lo), float(e_hi)]},
           "checks": results, "failed": failed,
           "VALIDATION_CLASS": "PASS" if not failed else "REFUSE",
           "seconds": round(time.time() - t0, 1)}
    s = C.write_evidence(C.NS / "evidence" / "validation" / "C11R_VALIDATION.json", out)
    for r in results:
        print(f"  {'PASS' if r['pass'] else 'FAIL'}  {r['id']:4s} {r['name'][:72]}")
    print(f"\nVALIDATION_CLASS = {out['VALIDATION_CLASS']}  failed={failed}  "
          f"({out['seconds']}s)")
    print(f"wrote evidence/validation/C11R_VALIDATION.json sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
