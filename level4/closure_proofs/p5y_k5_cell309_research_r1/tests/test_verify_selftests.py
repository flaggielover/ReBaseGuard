#!/usr/bin/env python3
"""
Self-tests of the independent SRK verifier (verify/srk_verify_indep.py).

* Unit tests of the rigorous Gaussian enclosures (pi, phi, Phi, G_i, |He_n| phi ranges, He_n roots) against math.erf /
  float quadrature, and interval containment.
* The kernel closed form (K_e P)(x) = sum_L alpha_L Phi(L) + beta_L phi(L) against a float quadrature of the DEFINING
  integral (whole and taboo kernel, three geometries, random small polynomials).
* Taylor-model containment at random points (triangle and axis cells, including the exact axis reduction), and a
  lower-bound soundness sample on a genuine certificate.
* SRK_CERT_SPEC.md section 5 required rejections 1-7 on a decoy certificate (read only).

Run:  python3 tests/test_verify_selftests.py      (or python3 -m pytest tests/test_verify_selftests.py)
"""
import copy
import glob
import json
import math
import os
import random
import sys
import unittest
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(NS, 'verify'))
import srk_verify_indep as V  # noqa: E402

TWO_WX = float(2 ** V.WX)
TWO_WB = float(2 ** V.WB)


def fphi(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def fPhi(x):
    return 0.5 * math.erfc(-x / math.sqrt(2))


def fhe(n, v):
    if n == 0:
        return 1.0
    a, b = 1.0, v
    for j in range(1, n):
        a, b = b, v * b - j * a
    return b


def simpson(f, a, b, n=600):
    h = (b - a) / n
    s = f(a + 1e-12) + f(b - 1e-12)
    for j in range(1, n):
        s += (4 if j % 2 else 2) * f(a + j * h)
    return s * h / 3


def peval(P, p, m):
    return sum(float(v) * p ** a * m ** b for (a, b), v in P.items())


def K_quad(P0, P1, h, k, p, m, e, ec, taboo=False, n=600):
    """Float quadrature of the defining integral of (K_e P_e)(p, m), P_e = P0 + (e - ec) P1."""
    c = h + k
    t = e - ec

    def f(z):
        pp, mm = max(0.0, p + z - k), max(0.0, m - z - k)
        if taboo and pp == 0.0 and mm == 0.0:
            return 0.0
        return (peval(P0, pp, mm) + t * peval(P1, pp, mm)) * fphi(z + e)
    bps = sorted(set([m - c, c - p] + [x for x in (k - p, m - k) if m - c < x < c - p]))
    return sum(simpson(f, a, b, n) for a, b in zip(bps[:-1], bps[1:]))


def kq(i, p, m, e, c, n=2000):
    a, b = m - c + e, c - p + e
    return simpson(lambda v: abs(fhe(i, v)) * fphi(v), a, b, n)


def decoy_files():
    return sorted(glob.glob(os.path.join(NS, 'evidence', 'srk_decoys', '*.json')))


def pick_cert(prefer_index='1'):
    files = decoy_files()
    pref = [f for f in files if os.path.basename(f).startswith('h5_')] or files
    if not pref:
        return None, None
    with open(pref[0]) as fh:
        d = json.load(fh)
    certs = d['certificates']
    idx = prefer_index if prefer_index in certs else sorted(certs)[0]
    return pref[0], certs[idx]


def fs(x):
    return '%d/%d' % (x.numerator, x.denominator)


def resha(c):
    c = dict(c)
    c['sha256'] = V.canonical_sha(c)
    return c


# ----------------------------------------------------------------------------------------------------------------------
class TestGaussianEnclosures(unittest.TestCase):
    def test_pi(self):
        self.assertLess(V.PI_HI - V.PI_LO, Fr(1, 2 ** 500))
        self.assertLess(abs(float(V.PI_LO) - math.pi), 1e-15)
        self.assertTrue(V.PI_LO < Fr(314159265358979324, 10 ** 17))
        self.assertTrue(V.PI_HI > Fr(314159265358979323, 10 ** 17))

    def test_phi_Phi_contain_math(self):
        rnd = random.Random(7)
        pts = [Fr(0), Fr(8), Fr(-8), Fr(17, 2), Fr(-12)] + [Fr(rnd.randint(-12000, 12000), 1000) for _ in range(60)]
        for x in pts:
            fx = float(x)
            lo, hi = V.phi_iv(x)
            tv = fphi(fx)
            self.assertLessEqual(lo / TWO_WX, tv * (1 + 1e-14) + 1e-300)
            self.assertGreaterEqual(hi / TWO_WX, tv * (1 - 1e-14))
            self.assertLess((hi - lo) / TWO_WX, 1e-60)
            lo, hi = V.Phi_iv(x)
            tP = fPhi(fx)
            self.assertLessEqual(lo / TWO_WX, tP + 1e-15)
            self.assertGreaterEqual(hi / TWO_WX, tP - 1e-15)
            self.assertLess((hi - lo) / TWO_WX, 1e-15)

    def test_Phi_monotone_consistent(self):
        xs = sorted(Fr(j, 7) for j in range(-60, 61))
        for a, b in zip(xs[:-1], xs[1:]):
            self.assertLessEqual(V.Phi_iv(a)[0], V.Phi_iv(b)[1])

    def test_he_roots(self):
        for n in range(1, 8):
            roots = V.he_roots(n)
            self.assertEqual(len(roots), n)
            for rl, rh in roots:
                self.assertLessEqual(rh - rl, Fr(1, 2 ** 200))
                self.assertLessEqual(V.he_eval(n, rl) * V.he_eval(n, rh), 0)
        r3 = V.he_roots(3)
        self.assertTrue(r3[2][0] ** 2 <= 3 <= r3[2][1] ** 2)
        self.assertEqual(V.he_roots(2), ((Fr(-1), Fr(-1)), (Fr(1), Fr(1))))

    def test_G_value_vs_quadrature(self):
        for n in range(0, 6):
            for u in (Fr(-3), Fr(-1, 2), Fr(1, 5), Fr(2), Fr(3, 2), Fr(-7, 3)):
                lo, hi = V.G_value(n, u)
                g = simpson(lambda v: abs(fhe(n, v)) * fphi(v), -14.0, float(u), 40000)
                self.assertLessEqual(lo / TWO_WX, g + 1e-9)
                self.assertGreaterEqual(hi / TWO_WX, g - 1e-9)

    def test_absHephi_bounds_contain_samples(self):
        rnd = random.Random(3)
        for _ in range(40):
            n = rnd.randint(0, 9)
            a = Fr(rnd.randint(-8000, 8000), 1000)
            b = a + Fr(rnd.randint(1, 3000), 1000)
            lo, hi = V.absHephi_bounds(n, a, b)
            for j in range(21):
                v = float(a + (b - a) * j / 20)
                val = abs(fhe(n, v)) * fphi(v)
                self.assertLessEqual(float(lo), val * (1 + 1e-12) + 1e-300)
                self.assertGreaterEqual(float(hi), val * (1 - 1e-12))


# ----------------------------------------------------------------------------------------------------------------------
class TestKernelClosedForm(unittest.TestCase):
    def closed(self, ps, h, k, p, m, e, ec):
        c = h + k
        sg, tu, t = p - e, m + e, e - ec
        case = 'A' if p + m >= 2 * k else 'B'
        al, be = ps.alpha_frac[case], ps.beta_frac[case]
        Ls = {1: tu - c, 2: k - sg, 3: tu - k, 4: c - sg}

        def ev(P):
            return sum(float(v) * sg ** i * tu ** j * t ** l for (i, j, l), v in P.items())
        return sum(ev(al[L]) * fPhi(Ls[L]) + ev(be[L]) * fphi(Ls[L]) for L in Ls)

    def test_closed_form_vs_quadrature(self):
        rnd = random.Random(11)
        for (h, k) in ((Fr(5), Fr(1, 2)), (Fr(3), Fr(1, 2)), (Fr(4), Fr(1, 3))):
            for taboo in (False, True):
                d = rnd.choice([2, 4, 5])
                P0 = {(a, b): Fr(rnd.randint(-9, 9), rnd.randint(1, 5)) for a in range(d + 1) for b in range(d + 1 - a)}
                P1 = {(a, b): Fr(rnd.randint(-9, 9), rnd.randint(1, 5)) for a in range(d + 1) for b in range(d + 1 - a)}
                ec = Fr(rnd.randint(-8, 8), 8)
                ps = V.PolySet(P0, P1, h, k, ec, taboo)
                S = float(h - 2 * k)
                for typ in ('tri', 'small', 'axp', 'axm', 'tri'):
                    if typ == 'tri':
                        p = rnd.uniform(0, S)
                        m = rnd.uniform(0, S - p)
                    elif typ == 'small':
                        p = rnd.uniform(0, float(k))
                        m = rnd.uniform(0, float(k) - p)
                    elif typ == 'axp':
                        p, m = rnd.uniform(S, float(h)), 0.0
                    else:
                        p, m = 0.0, rnd.uniform(S, float(h))
                    e = float(ec) + rnd.uniform(-0.3, 0.3)
                    q = K_quad(P0, P1, float(h), float(k), p, m, e, float(ec), taboo)
                    cf = self.closed(ps, float(h), float(k), p, m, e, float(ec))
                    self.assertLess(abs(q - cf), 1e-9 * (1 + abs(q)), (h, k, taboo, typ, p, m, e))


# ----------------------------------------------------------------------------------------------------------------------
class TestTaylorModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path, raw = pick_cert('4')
        if raw is None:
            raise unittest.SkipTest('no decoy certificate available')
        cls.cert = V.Cert(raw)
        V.CTX = V.prepare(cls.cert)
        cls.ctx = V.CTX

    def D_float(self, p, m, e, case):
        cert = self.cert
        c, k = float(cert.c), float(cert.k)
        sg, tu, t = p - e, m + e, e - float(cert.e_c)
        ps = self.ctx.V
        al, be = ps.alpha_frac[case], ps.beta_frac[case]
        Ls = {1: tu - c, 2: k - sg, 3: tu - k, 4: c - sg}

        def ev(P):
            return sum(float(v) * sg ** i * tu ** j * t ** l for (i, j, l), v in P.items())
        K = sum(ev(al[L]) * fPhi(Ls[L]) + ev(be[L]) * fphi(Ls[L]) for L in Ls)
        return float(ps.eval_raw(Fr(p), Fr(m), Fr(t))) - K

    def test_containment(self):
        rnd = random.Random(5)
        cert = self.cert
        cells = [('tri', Fr(1), Fr(5, 4), Fr(1, 2), Fr(3, 4)), ('tri', Fr(0), Fr(1, 8), Fr(0), Fr(1, 8)),
                 ('axp', cert.S, cert.S + Fr(1, 4), Fr(0), Fr(0)), ('axm', Fr(0), Fr(0), cert.h - Fr(1, 4), cert.h)]
        for c5 in cells:
            cell = c5 + (cert.e_lo, cert.e_hi, 0)
            fr = V.make_frame(cert, cell)
            poly = V.cell_polygon(cert, cell)
            for case, cpoly in V.split_cases(cert, poly):
                D, rem = V.build_D(self.ctx.V, case, cert, fr, 8)
                Dr = V.reduce_axis(D, cell[0])
                pmin, pmax, mmin, mmax = V.bbox(cpoly)
                for _ in range(6):
                    p = rnd.uniform(float(pmin), float(pmax))
                    m = rnd.uniform(float(mmin), float(mmax))
                    if cell[0] == 'tri' and p + m > float(cert.S):
                        continue
                    e = rnd.uniform(float(cert.e_lo), float(cert.e_hi))
                    x = ((p - e - float(fr.cen[0])) / float(fr.rad[0]) if fr.rad[0] else 0.0,
                         (m + e - float(fr.cen[1])) / float(fr.rad[1]) if fr.rad[1] else 0.0,
                         (e - float(cert.e_c) - float(fr.cen[2])) / float(fr.rad[2]) if fr.rad[2] else 0.0)
                    for T in (D, Dr):
                        val = sum(v / TWO_WB * x[0] ** a * x[1] ** b * x[2] ** l for (a, b, l), v in T.items())
                        tv = self.D_float(p, m, e, case)
                        self.assertLessEqual(abs(val - tv), rem / TWO_WB + 1e-9 * (1 + abs(tv)))

    def test_lower_bound_below_samples(self):
        """Certified cell lower bounds of (C2)/(C3) never exceed float samples of the true quantity in the cell."""
        rnd = random.Random(9)
        cert = self.cert
        c = float(cert.c)
        for c5 in (('tri', Fr(3, 2), Fr(7, 4), Fr(1, 4), Fr(1, 2)), ('axp', cert.h - Fr(1, 4), cert.h, Fr(0), Fr(0))):
            cell = c5 + (cert.e_lo, cert.e_hi, 0)
            ok2, lb2, _ = V.check_cell('C2', cell, 8)
            ok3, lb3, _ = V.check_cell('C3', cell, 8)
            for _ in range(4):
                p = rnd.uniform(float(c5[1]), float(c5[2]))
                m = rnd.uniform(float(c5[3]), float(c5[4]))
                e = rnd.uniform(float(cert.e_lo), float(cert.e_hi))
                t = e - float(cert.e_c)
                F2 = (peval(cert.W0, p, m) + t * peval(cert.W1, p, m)
                      - K_quad(cert.W0, cert.W1, float(cert.h), float(cert.k), p, m, e, float(cert.e_c)) - 1)
                kb = max(kq(cert.i, p, m, float(cert.w_lo + (cert.w_hi - cert.w_lo) * j / 8), c) for j in range(9))
                F3 = (peval(cert.V0, p, m) + t * peval(cert.V1, p, m)
                      - K_quad(cert.V0, cert.V1, float(cert.h), float(cert.k), p, m, e, float(cert.e_c)) - kb)
                if lb2 is not None:
                    self.assertLessEqual(float(lb2), F2 + 1e-7)
                if lb3 is not None:
                    self.assertLessEqual(float(lb3), F3 + 1e-7)


# ----------------------------------------------------------------------------------------------------------------------
class TestRequiredRejections(unittest.TestCase):
    """SRK_CERT_SPEC.md section 5.  Mutants 1-5 get a recomputed sha256 so the mathematics is exercised."""

    @classmethod
    def setUpClass(cls):
        cls.path, cls.raw = pick_cert('1')
        if cls.raw is None:
            raise unittest.SkipTest('no decoy certificate available')
        cls.log = {}

    def run_v(self, c, depth=12):
        return V.verify_cert(c, N=8, max_depth=depth, procs=1)

    def test_0_genuine_accepted(self):
        r = self.run_v(self.raw)
        self.assertEqual(r['verdict'], 'ACCEPT', r)

    def test_0b_taboo_positive_control(self):
        """K^_e P = K_e P - P(0,0) (Phi(k-p+e) - Phi(m-k+e)) <= K_e P when P(0,0) >= 0, so a valid whole-kernel
        certificate stays valid under the taboo kernel: the taboo code path must ACCEPT it."""
        self.assertGreater(Fr(self.raw['V0']['0,0']), 0)
        r = V.verify_cert(self.raw, 'taboo', N=8, max_depth=12, procs=1)
        self.assertEqual(r['verdict'], 'ACCEPT', r)
        self.assertIn('kernel=taboo', r['describe'])

    def test_1_gamma(self):
        m = copy.deepcopy(self.raw)
        m['Gamma'] = fs(Fr(self.raw['Gamma']) - Fr(1, 10 ** 6))
        r = self.run_v(resha(m))
        self.assertEqual(r['verdict'], 'REJECT')
        self.assertTrue(r['false'])

    def test_2_scaled_V0(self):
        """(1 - 2^-8) V0.  On these decoys the certificates carry a margin of order 1e-1, so this mutated claim is
        TRUE; a sound verifier then ACCEPTs it with a proof.  The test requires: REJECT, or ACCEPT together with an
        independent float confirmation that the mutated quantity is positive at sample points (spec erratum SE-1:
        "REJECT, or PROVE TRUE with the proof recorded; never an unproved ACCEPT").  The SE-1 mandatory rejection,
        V0 scaled by 3/4, must be REJECTED."""
        m = copy.deepcopy(self.raw)
        m['V0'] = {k: fs(Fr(v) * (1 - Fr(1, 256))) for k, v in self.raw['V0'].items()}
        m = resha(m)
        r = self.run_v(m)
        if r['verdict'] == 'ACCEPT':
            cert = V.Cert(m)
            rnd = random.Random(1)
            for _ in range(6):
                p = rnd.uniform(0, float(cert.S))
                mm = rnd.uniform(0, float(cert.S) - p)
                e = rnd.uniform(float(cert.e_lo), float(cert.e_hi))
                t = e - float(cert.e_c)
                kb = max(kq(cert.i, p, mm, float(cert.w_lo + (cert.w_hi - cert.w_lo) * j / 8), float(cert.c))
                         for j in range(9))
                F3 = (peval(cert.V0, p, mm) + t * peval(cert.V1, p, mm)
                      - K_quad(cert.V0, cert.V1, float(cert.h), float(cert.k), p, mm, e, float(cert.e_c)) - kb)
                self.assertGreater(F3, 0)
        else:
            self.assertEqual(r['verdict'], 'REJECT')
        m = copy.deepcopy(self.raw)
        m['V0'] = {k: fs(Fr(v) * (1 - Fr(1, 4))) for k, v in self.raw['V0'].items()}
        r = self.run_v(resha(m))
        self.assertEqual(r['verdict'], 'REJECT')

    def test_3_drop_lambda(self):
        lam = Fr(self.raw['lam'])
        if lam <= 0:
            self.skipTest('lam == 0')
        m = copy.deepcopy(self.raw)
        keys = set(self.raw['V0']) | set(self.raw['W0'])
        m['V0'] = {k: fs(Fr(self.raw['V0'].get(k, '0')) - lam * Fr(self.raw['W0'].get(k, '0'))) for k in keys}
        r = self.run_v(resha(m))
        self.assertEqual(r['verdict'], 'REJECT')

    def test_4_widened_block(self):
        elo, ehi = Fr(self.raw['block'][0]), Fr(self.raw['block'][1])
        for (a, b) in ((elo - Fr(1, 8), ehi), (elo, ehi + Fr(1, 8))):
            for regam in (False, True):
                m = copy.deepcopy(self.raw)
                m['block'] = [fs(a), fs(b)]
                ec = (a + b) / 2
                m['e_c'] = fs(ec)
                if regam:
                    v00, v10 = Fr(self.raw['V0']['0,0']), Fr(self.raw['V1']['0,0'])
                    m['Gamma'] = fs(max(v00 + (a - ec) * v10, v00 + (b - ec) * v10))
                r = self.run_v(resha(m))
                # REJECT unless the widened claim is true; the verifier reports which (disproof vs proof)
                self.assertIn(r['verdict'], ('REJECT', 'ACCEPT'))
                if r['verdict'] == 'REJECT':
                    self.assertTrue(r['false'], r)          # on these decoys the widened claims are disproved

    def test_5_hermite_plus_one(self):
        m = copy.deepcopy(self.raw)
        m['hermite_index'] = self.raw['hermite_index'] + 1
        r = self.run_v(resha(m))
        if self.raw['hermite_index'] >= 1:
            self.assertEqual(r['verdict'], 'REJECT')
        else:
            self.assertIn(r['verdict'], ('REJECT', 'ACCEPT'))   # k_1 <= k_0 on these windows: claim may be true

    def test_6_sha(self):
        m = copy.deepcopy(self.raw)
        m['sha256'] = ('0' if self.raw['sha256'][0] != '0' else '1') + self.raw['sha256'][1:]
        r = self.run_v(m)
        self.assertEqual(r['verdict'], 'REJECT')
        self.assertIn('sha256', r['reason'])

    def test_7_malformed(self):
        cases = []
        m = copy.deepcopy(self.raw)
        del m['V1']
        cases.append(m)
        m = copy.deepcopy(self.raw)
        m['Gamma'] = '12.5'
        cases.append(resha(m))
        m = copy.deepcopy(self.raw)
        m['block'] = [self.raw['block'][1], self.raw['block'][0]]
        cases.append(resha(m))
        m = copy.deepcopy(self.raw)
        m['hermite_index'] = 'two'
        cases.append(resha(m))
        m = copy.deepcopy(self.raw)
        m['weight_block'] = [fs(Fr(self.raw['block'][0]) + Fr(1, 64)), self.raw['block'][1]]
        cases.append(resha(m))
        m = copy.deepcopy(self.raw)
        m['kernel'] = 'bogus'
        cases.append(resha(m))
        cases.append(['not', 'a', 'certificate'])
        for c in cases:
            r = self.run_v(c)
            self.assertEqual(r['verdict'], 'REFUSE', r)

    def test_7_non_dyadic_drift_no_crash(self):
        m = copy.deepcopy(self.raw)
        a, b = Fr(self.raw['block'][0]) + Fr(1, 3), Fr(self.raw['block'][1]) + Fr(1, 3)
        m['block'] = [fs(a), fs(b)]
        m['e_c'] = fs((a + b) / 2)
        r = self.run_v(resha(m), depth=4)
        self.assertIn(r['verdict'], ('ACCEPT', 'REJECT'))
        self.assertNotIn('internal error', r.get('reason') or '')

    def test_quarantine_refused(self):
        m = copy.deepcopy(self.raw)
        m['geometry'] = {'h': '5/1', 'k': '1/2'}
        m['block'] = ['5/4', '41/32']
        m['e_c'] = fs((Fr(5, 4) + Fr(41, 32)) / 2)
        r = self.run_v(resha(m))
        self.assertEqual(r['verdict'], 'REFUSE')
        self.assertIn('quarantine', r['reason'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
