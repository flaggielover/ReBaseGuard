"""C7 -- known-value tests for the Gaussian primitives.

Why this exists. Every quantity in the namespace is built from G.Phi and G.phi. psi_exact was
introduced as an INDEPENDENT recomputation of psi, and it is independent at the expression level --
but `r(t) = rho(t)/Phi(-t)` identically, so psi_exact and psi_lo_at are the same two primitives
rearranged. A systematic error in Phi or phi is invisible to psi_exact, to every mutant, and to every
kill gate. The pre-publication review checked the primitives by hand and found them correct; this
module commits that check so the tree carries it.

The reference values are standard and externally known, not recomputed from this module.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C
import c7_gaussian as G

# (name, argument, reference value as an exact decimal string, tolerance)
CASES = [
    ("Phi(0)",      ("Phi", F(0)),          "0.5",                    F(1, 10) ** 40),
    ("Phi(1)",      ("Phi", F(1)),          "0.8413447460685429",     F(1, 10) ** 15),
    ("Phi(-1)",     ("Phi", F(-1)),         "0.1586552539314571",     F(1, 10) ** 15),
    ("Phi(-1.96)",  ("Phi", F(-196, 100)),  "0.024997895148220435",   F(1, 10) ** 15),
    ("Phi(1.96)",   ("Phi", F(196, 100)),   "0.9750021048517796",     F(1, 10) ** 15),
    ("Phi(-7)",     ("Phi", F(-7)),         "0.0000000000012798125438858352", F(1, 10) ** 24),
    ("Phi(2.5)",    ("Phi", F(5, 2)),       "0.9937903346742238",     F(1, 10) ** 15),
    ("phi(0)",      ("phi", F(0)),          "0.3989422804014327",     F(1, 10) ** 15),
    ("phi(1)",      ("phi", F(1)),          "0.24197072451914337",    F(1, 10) ** 15),
    ("phi(-1)",     ("phi", F(-1)),         "0.24197072451914337",    F(1, 10) ** 15),
    ("phi(2)",      ("phi", F(2)),          "0.05399096651318806",    F(1, 10) ** 15),
    ("phi(3.5)",    ("phi", F(7, 2)),       "0.0008726826950457602",  F(1, 10) ** 18),
]


def main() -> int:
    rows, failed = [], []
    for name, (fn, arg), ref, tol in CASES:
        iv = (G.Phi if fn == "Phi" else G.phi)(arg)
        r = F(ref)
        ok = iv.lo - tol <= r <= iv.hi + tol and iv.lo <= iv.hi
        rows.append({"case": name, "reference": ref, "lo": str(iv.lo), "hi": str(iv.hi),
                     "contains_reference": bool(ok),
                     "interval_width": f"{float(iv.hi - iv.lo):.3e}"})
        if not ok:
            failed.append(name)

    # Identities that must hold exactly or to within the grid, independent of the reference table.
    ident = []

    def idcheck(name, ok, detail):
        ident.append({"identity": name, "holds": bool(ok), "detail": detail})
        if not ok:
            failed.append(name)

    for t in (F(1, 2), F(2), F(-3, 2), F(17, 5)):
        a, b = G.Phi(t), G.Phi(-t)
        idcheck(f"Phi({t}) + Phi(-{t}) = 1", a.lo + b.lo <= 1 <= a.hi + b.hi,
                f"[{float(a.lo + b.lo):.17f}, {float(a.hi + b.hi):.17f}]")
    for t in (F(1), F(-2), F(7, 2)):
        p1, p2 = G.phi(t), G.phi(-t)
        idcheck(f"phi({t}) = phi(-{t})", p1.lo <= p2.hi and p2.lo <= p1.hi, "symmetry")
    # monotonicity of Phi on a coarse sweep
    prev = None
    mono = True
    for k in range(-40, 41):
        v = G.Phi(F(k, 10)).lo
        if prev is not None and v < prev:
            mono = False
        prev = v
    idcheck("Phi non-decreasing on [-4, 4]", mono, "81-point sweep")

    out = {"schema": "C7_PRIMITIVES_TEST/1",
           "purpose": ("known-value and identity tests for G.Phi / G.phi, the two primitives every "
                       "other quantity in the namespace is built from and which no mutant, no kill "
                       "gate and not even psi_exact can see an error in"),
           "gaussian_sha256": C.sha256_file(C.NS / "code" / "c7_gaussian.py"),
           "known_value_cases": rows, "identities": ident,
           "failed": failed,
           "PRIMITIVES_CLASS": "PASS" if not failed else "REFUSE"}
    p = C.NS / "evidence" / "primitives" / "C7_PRIMITIVES_TEST.json"
    s = C.write_evidence(p, out)
    for r in rows:
        print(f"  {'PASS' if r['contains_reference'] else 'FAIL'}  {r['case']:<12} "
              f"ref {r['reference']:<26} width {r['interval_width']}")
    print(f"  identities: {sum(1 for i in ident if i['holds'])}/{len(ident)} hold")
    print(f"\nPRIMITIVES_CLASS = {out['PRIMITIVES_CLASS']}  failed={failed}")
    print(f"wrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
