#!/usr/bin/env python3
"""
Tests of the band-scoped verifier variant verify/srk_verify_indep_scoped.py (FC2(b); FNS/fc2/FC2_SPEC_R2.md section 8),
written by the verifier's author.

Part 1: the 21 self-tests of the research verifier (RNS/tests/test_verify_selftests.py, sha256
8357be8539ed408b449c486387907b9dd3e0df03ccf0c846fec18ccfae48e2c3), ported unchanged except that they import the variant,
read the decoy evidence from RNS (read only), and use this file's own compiled band table for probe construction.

Part 2: the FC2 tests N1-N13, P1, P2 and D1 of spec section 8.  Each builds and tears down its own sandbox
(verify/scoped_sandbox.py; spec section 6).  REAL-band items are only ever given to admission_decision, or refused by
verify_cert before evaluation; a tripwire on the variant's `prepare` fails the run if a REAL-band certificate (any
geometry) or a non-admitted TEST-band certificate ever reaches evaluation.  No production marker and no production grant
exist at any point.  Every test execution is ledgered through code/p309_env.py.

Part 3 (P309-r2, gate step 3; brief governance/BRIEF_R2_VERIFIER_AUTHOR_1.md): V2, both production ref namespaces
refused (static check plus the guards); V3, the sandbox base rule (static check plus every record shape, built with a
TEST-named record path inside a sandbox); V4, P309_SCRATCH_ROOT (a negative control for each refusal case, and a
positive control).

Run:  P309_SCRATCH_ROOT=<an absolute directory outside the repository> python3 tests/test_verify_scoped.py
"""
import ast
import copy
import glob
import json
import math
import os
import random
import re
import shutil
import sys
import tempfile
import unittest
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
FNS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FNS, 'code'))
import p309_env as E  # noqa: E402
RNS = str(E.RNS)
NS = RNS                                                   # decoy evidence and committed results (read only)
sys.path.insert(0, os.path.join(FNS, 'verify'))
import srk_verify_indep_scoped as V  # noqa: E402
import scoped_sandbox as SB  # noqa: E402

TWO_WX = float(2 ** V.WX)
TWO_WB = float(2 ** V.WB)

# this file's OWN compiled copy of spec section 1 (probe construction guard; protocol section 7(c))
_OWN_REAL_BAND = ((Fr(6, 5), Fr(13, 5)), (Fr(-13, 5), Fr(-6, 5)))  # q309: literal-ok (own compiled REAL band for the probe guard; refusal constant)
_OWN_TEST_BAND = ((Fr(341, 1024), Fr(201, 512)), (Fr(-201, 512), Fr(-341, 1024)))
_DECOY_DRIFT_HULL = [('-1/2', '37/32')]         # every drift a ported test evaluates lies in this hull (outside both bands)
_TEST_BAND_DRIFTS = [('341/1024', '201/512')]
_ALLOW_TEST_EVAL = [False]
_ORIG_PREPARE = V.prepare


def _tripwire_prepare(cert):
    if 'REAL' in cert.bands:
        raise AssertionError('TRIPWIRE: a REAL-band certificate reached evaluation')
    if 'TEST' in cert.bands and not _ALLOW_TEST_EVAL[0]:
        raise AssertionError('TRIPWIRE: a TEST-band certificate reached evaluation outside an admitting test')
    return _ORIG_PREPARE(cert)


def setUpModule():
    V.prepare = _tripwire_prepare


def tearDownModule():
    V.prepare = _ORIG_PREPARE


class _Ledgered(unittest.TestCase):
    """Every test execution writes one line to the formal ledger (FNS/ledger/ZERO_TARGET_LEDGER.jsonl)."""
    LEDGER_CLASS = 'NONTARGET_DECOY'
    LEDGER_DRIFTS = _DECOY_DRIFT_HULL
    LEDGER_NOTES = 'ported self-test; decoy drifts only'

    def setUp(self):
        E.log('tests/test_verify_scoped.py::%s' % self.id().split('.', 1)[-1],
              'FC2 verifier-variant test execution',
              klass=self.LEDGER_CLASS, drifts=self.LEDGER_DRIFTS, notes=self.LEDGER_NOTES)


# ======================================================================================================================
# Part 1: the 21 self-tests of the research verifier, ported
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
    files = sorted(glob.glob(os.path.join(NS, 'evidence', 'srk_decoys', '*.json')))
    return files or sorted(glob.glob(os.path.join(NS, 'evidence', 'srk_decoys_prelim', '*.json')))


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


_CLAIM_REJECT = re.compile(r'^C[123] (is FALSE at|UNPROVEN at depth limit)')


def meets_band(m):
    """True if block or weight block meets a band of this file's OWN compiled copy of spec section 1: the REAL band for
    every geometry, the TEST band for geometry (3, 1/2) (exact rational comparison; ported probe-construction guard)."""
    g = m['geometry']
    ivs = [m['block']] + ([m['weight_block']] if 'weight_block' in m else [])
    tables = [_OWN_REAL_BAND] + ([_OWN_TEST_BAND] if (Fr(g['h']), Fr(g['k'])) == (Fr(3), Fr(1, 2)) else [])
    return any(Fr(lo) <= b and a <= Fr(hi) for t in tables for (lo, hi) in ivs for (a, b) in t)


# ----------------------------------------------------------------------------------------------------------------------
class TestGaussianEnclosures(_Ledgered):
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
            kinks = [float(r[0]) for r in V.he_roots(n)]
            for u in (Fr(-3), Fr(-1, 2), Fr(1, 5), Fr(2), Fr(3, 2), Fr(-7, 3)):  # q309: literal-ok (arguments of a Gaussian special function, not drifts)
                lo, hi = V.G_value(n, u)
                # reference: Simpson between consecutive kinks of |He_n| (the integrand is smooth there)
                bps = [-14.0] + [r for r in kinks if r < float(u)] + [float(u)]
                g = sum(simpson(lambda v: abs(fhe(n, v)) * fphi(v), a, b, 20000) for a, b in zip(bps[:-1], bps[1:]))
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
class TestKernelClosedForm(_Ledgered):
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
class TestTaylorModels(_Ledgered):
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
        cells = [('tri', Fr(1), Fr(5, 4), Fr(1, 2), Fr(3, 4)), ('tri', Fr(0), Fr(1, 8), Fr(0), Fr(1, 8)),  # q309: literal-ok (state-cell coordinates (p, m), not drifts)
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
        for c5 in (('tri', Fr(3, 2), Fr(7, 4), Fr(1, 4), Fr(1, 2)), ('axp', cert.h - Fr(1, 4), cert.h, Fr(0), Fr(0))):  # q309: literal-ok (state-cell coordinates (p, m), not drifts)
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
class TestRequiredRejections(_Ledgered):
    """SRK_CERT_SPEC.md section 5.  Mutants 1-5 get a recomputed sha256 so the mathematics is exercised."""

    @classmethod
    def setUpClass(cls):
        cls.path, cls.raw = pick_cert('1')
        if cls.raw is None:
            raise unittest.SkipTest('no decoy certificate available')
        cls.log = {}

    def run_v(self, c, depth=24):
        return V.verify_cert(c, N=8, max_depth=depth, procs=1)

    def assertClaimReject(self, r):
        """REJECT because a claim (C1)-(C3) is disproved or unproven -- not (C4), sha256, a refusal or an error."""
        self.assertEqual(r['verdict'], 'REJECT', r)
        self.assertRegex(r.get('reason') or '', _CLAIM_REJECT)

    def assertRefusedFor(self, r, prefix):
        self.assertEqual(r['verdict'], 'REFUSE', r)
        self.assertTrue((r.get('reason') or '').startswith(prefix), (prefix, r.get('reason')))

    def test_0_genuine_accepted(self):
        r = self.run_v(self.raw)
        self.assertEqual(r['verdict'], 'ACCEPT', r)

    def test_0b_taboo_positive_control(self):
        """K^_e P = K_e P - P(0,0) (Phi(k-p+e) - Phi(m-k+e)) <= K_e P when P(0,0) >= 0, so a valid whole-kernel
        certificate stays valid under the taboo kernel: the taboo code path must ACCEPT it."""
        self.assertGreater(Fr(self.raw['V0']['0,0']), 0)
        m = copy.deepcopy(self.raw)
        m['kernel'] = 'taboo'          # the only change; run as a bare certificate so no file-level key can conflict
        r = V.verify_cert(resha(m), None, N=8, max_depth=12, procs=1)
        self.assertEqual(r['verdict'], 'ACCEPT', r)
        self.assertIn('kernel=taboo', r['describe'])

    def test_1_gamma(self):
        m = copy.deepcopy(self.raw)
        m['Gamma'] = fs(Fr(self.raw['Gamma']) - Fr(1, 10 ** 6))
        r = self.run_v(resha(m))
        self.assertEqual(r['verdict'], 'REJECT')
        self.assertTrue(r['false'])
        self.assertTrue(r['reason'].startswith('(C4) fails'), r['reason'])

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
            self.assertClaimReject(r)
        m = copy.deepcopy(self.raw)
        m['V0'] = {k: fs(Fr(v) * (1 - Fr(1, 4))) for k, v in self.raw['V0'].items()}
        r = self.run_v(resha(m))
        self.assertClaimReject(r)

    def test_3_drop_lambda(self):
        lam = Fr(self.raw['lam'])
        if lam <= 0:
            self.skipTest('lam == 0')
        m = copy.deepcopy(self.raw)
        keys = set(self.raw['V0']) | set(self.raw['W0'])
        m['V0'] = {k: fs(Fr(self.raw['V0'].get(k, '0')) - lam * Fr(self.raw['W0'].get(k, '0'))) for k in keys}
        r = self.run_v(resha(m))
        self.assertClaimReject(r)

    def test_4_widened_block(self):
        elo, ehi = Fr(self.raw['block'][0]), Fr(self.raw['block'][1])
        for (a, b) in ((elo - Fr(1, 8), ehi), (elo, ehi + Fr(1, 8))):
            for regam in (False, True):
                m = copy.deepcopy(self.raw)
                m['block'] = [fs(a), fs(b)]
                ec = (a + b) / 2
                m['e_c'] = fs(ec)
                if 'weight_block' in self.raw:          # keep weight_block containing block: single defect
                    wb = self.raw['weight_block']
                    m['weight_block'] = [fs(min(a, Fr(wb[0]))), fs(max(b, Fr(wb[1])))]
                self.assertFalse(meets_band(m))
                if regam:
                    v00, v10 = Fr(self.raw['V0']['0,0']), Fr(self.raw['V1']['0,0'])
                    m['Gamma'] = fs(max(v00 + (a - ec) * v10, v00 + (b - ec) * v10))
                r = self.run_v(resha(m))
                if not regam:
                    # Gamma kept: (C4) must fail at the new endpoint
                    self.assertTrue(r['verdict'] == 'REJECT' and r['reason'].startswith('(C4) fails'), r)
                elif r['verdict'] != 'ACCEPT':
                    # REJECT unless the widened claim is true (then it is proved); the reason must be a claim failure
                    self.assertClaimReject(r)

    def test_5_hermite_plus_one(self):
        m = copy.deepcopy(self.raw)
        m['hermite_index'] = self.raw['hermite_index'] + 1
        r = self.run_v(resha(m))
        if self.raw['hermite_index'] >= 1:
            self.assertClaimReject(r)
        elif r['verdict'] != 'ACCEPT':                          # k_1 <= k_0 on these windows: claim may be true
            self.assertClaimReject(r)

    def test_6_sha(self):
        m = copy.deepcopy(self.raw)
        m['sha256'] = ('0' if self.raw['sha256'][0] != '0' else '1') + self.raw['sha256'][1:]
        r = self.run_v(m)
        self.assertEqual(r['verdict'], 'REJECT')
        self.assertEqual(r['reason'], 'sha256 mismatch')

    def test_7_malformed(self):
        """Each probe has exactly one defect and must be REFUSED for that defect (reason-specific)."""
        cases = []
        m = copy.deepcopy(self.raw)
        del m['V1']
        cases.append((m, "malformed: missing key 'V1'"))
        m = copy.deepcopy(self.raw)
        m['Gamma'] = '12.5'
        cases.append((resha(m), 'malformed: Gamma: not a rational string'))
        m = copy.deepcopy(self.raw)
        m['block'] = [self.raw['block'][1], self.raw['block'][0]]
        cases.append((resha(m), 'malformed: block: e_lo > e_hi'))
        m = copy.deepcopy(self.raw)
        m['hermite_index'] = 'two'
        cases.append((resha(m), 'malformed: hermite_index must be an integer'))
        m = copy.deepcopy(self.raw)
        m['weight_block'] = [fs(Fr(self.raw['block'][0]) + Fr(1, 64)), self.raw['block'][1]]
        cases.append((resha(m), 'malformed: weight_block does not contain block'))
        m = copy.deepcopy(self.raw)
        m['kernel'] = 'bogus'                   # run as a bare certificate: no file-level kernel key can conflict
        cases.append((resha(m), "malformed: unknown kernel 'bogus'"))
        cases.append((['not', 'a', 'certificate'], 'malformed: certificate is not a JSON object'))
        for c, prefix in cases:
            r = self.run_v(c)
            self.assertRefusedFor(r, prefix)

    def test_7_non_dyadic_drift_no_crash(self):
        """Non-dyadic drift: block AND weight_block shifted by -1/3 (or +1/3, whichever stays out of the quarantine
        band), so the drift is the only change.  It must be PROCESSED (not refused): ACCEPT, or REJECT for a claim."""
        for sh in (Fr(-1, 3), Fr(1, 3)):
            m = copy.deepcopy(self.raw)
            a, b = Fr(self.raw['block'][0]) + sh, Fr(self.raw['block'][1]) + sh
            m['block'] = [fs(a), fs(b)]
            m['e_c'] = fs((a + b) / 2)
            if 'weight_block' in self.raw:
                m['weight_block'] = [fs(Fr(self.raw['weight_block'][0]) + sh),
                                     fs(Fr(self.raw['weight_block'][1]) + sh)]
            if not meets_band(m):
                break
        self.assertFalse(meets_band(m))
        r = self.run_v(resha(m), depth=4)
        self.assertIn(r['verdict'], ('ACCEPT', 'REJECT'), r)
        if r['verdict'] == 'REJECT':
            self.assertClaimReject(r)
        self.assertIn('block=[%s,%s]' % (Fr(m['block'][0]), Fr(m['block'][1])), r['describe'])   # the shifted drift

    def test_weight_block_is_used(self):
        """A much wider weight block (hull of the block and [-1, 1], outside the quarantine band) raises kbar; on these
        decoys the claim then fails and must be REJECTED for a (C3)-type claim failure.  Guards against the weight
        block being ignored."""
        m = copy.deepcopy(self.raw)
        m['weight_block'] = [fs(min(Fr(self.raw['block'][0]), Fr(-1))), fs(max(Fr(self.raw['block'][1]), Fr(1)))]
        self.assertFalse(meets_band(m))
        r = self.run_v(resha(m))
        self.assertClaimReject(r)
        self.assertTrue(r['reason'].startswith('C3'), r['reason'])
        self.assertIn('kbar', V.__doc__)

    def test_quarantine_refused(self):
        """Parse-time refusal probe: block AND weight_block moved into the quarantine band (the only defect); must be
        REFUSED for the quarantine reason, before anything is evaluated."""
        m = copy.deepcopy(self.raw)
        m['geometry'] = {'h': '5/1', 'k': '1/2'}
        m['block'] = ['5/4', '41/32']  # q309: literal-ok (refusal probe: rejected at parse time, nothing evaluated)
        m['e_c'] = fs((Fr(5, 4) + Fr(41, 32)) / 2)  # q309: literal-ok (refusal probe: rejected at parse time, nothing evaluated)
        if 'weight_block' in self.raw:
            m['weight_block'] = list(m['block'])
        r = self.run_v(resha(m))
        self.assertRefusedFor(r, 'quarantine:')
        self.assertIn('nothing evaluated', r['reason'])




# ======================================================================================================================
# Part 2: FC2 tests (spec section 8)
OWN_REL = os.path.relpath(V._OWN_PATH, SB.own_repo())
OWN_SHA = V._file_sha256(V._OWN_PATH)
H3_CELL_FILES = sorted(glob.glob(os.path.join(RNS, 'evidence', 'srk_decoys_cell', 'cell_h3_*.json')))
_COMMITTED = None


def committed_results():
    global _COMMITTED
    if _COMMITTED is None:
        with open(os.path.join(RNS, 'verify', 'VERIFY_RESULTS.json')) as fh:
            _COMMITTED = json.load(fh)['files']
    return _COMMITTED


def h3_cell_items():
    out = []
    for f in H3_CELL_FILES:
        for label, raw, fk in V.load_certs(f):
            out.append((os.path.relpath(f, RNS), label, raw, fk))
    return out


def desc(raw):
    return {'geometry': raw['geometry'], 'block': raw['block'], 'weight_block': raw.get('weight_block', raw['block']),
            'sha256': raw['sha256']}


def own_bands(geometry, intervals):
    """This file's own band check (spec section 1), independent of the variant's tables."""
    h, k = Fr(geometry['h']), Fr(geometry['k'])
    out = []
    if any(Fr(lo) <= b and a <= Fr(hi) for (lo, hi) in intervals for (a, b) in _OWN_REAL_BAND):
        out.append('REAL')
    if (h, k) == (Fr(3), Fr(1, 2)) and any(Fr(lo) <= b and a <= Fr(hi) for (lo, hi) in intervals
                                             for (a, b) in _OWN_TEST_BAND):
        out.append('TEST')
    return out


REAL_DESC_5 = {'geometry': {'h': '5', 'k': '1/2'}, 'block': ['5/4', '41/32'], 'weight_block': ['5/4', '41/32'],  # q309: literal-ok (dry REAL-band descriptor; never evaluated)
               'sha256': '0' * 64}
REAL_DESC_3 = {'geometry': {'h': '3', 'k': '1/2'}, 'block': ['5/4', '41/32'], 'weight_block': ['5/4', '41/32'],  # q309: literal-ok (dry REAL-band descriptor, synthetic geometry; never evaluated)
               'sha256': '0' * 64}
REAL_IV_5 = {'geometry': {'h': '5', 'k': '1/2'}, 'lo': '5/4', 'hi': '41/32'}  # q309: literal-ok (dry REAL-band interval; never evaluated)


class TestFC2Scoped(_Ledgered):
    LEDGER_CLASS = 'SYNTHETIC'
    LEDGER_DRIFTS = []
    LEDGER_NOTES = ('FC2 admission test: sandbox under <P309_SCRATCH_ROOT>/fc2_sandbox_verifier; REAL-band items dry only '
                    '(admission_decision / parse-time refusal); no production marker or grant anywhere')

    def setUp(self):
        name = self.id().rsplit('.', 1)[-1]
        self.LEDGER_DRIFTS = _TEST_BAND_DRIFTS if name.startswith('test_P') else []
        super().setUp()

    @classmethod
    def setUpClass(cls):
        cls.items = h3_cell_items()
        if not cls.items:
            raise unittest.SkipTest('no committed h3 decoy-cell certificates')
        cls.test_desc = desc(cls.items[0][2])
        assert own_bands(cls.test_desc['geometry'], [cls.test_desc['block'], cls.test_desc['weight_block']]) == \
            ['TEST']

    # -- helpers -------------------------------------------------------------------------------------------------------
    def refused(self, res, *fragments):
        self.assertEqual(res[0], 'REFUSE', res)
        self.assertTrue(res[1].startswith('quarantine:'), res)
        for fr in fragments:
            self.assertIn(fr, res[1])

    def fresh(self, sb):
        """Back to the clone's base state: no test refs, extra branches removed, branch and index at the base."""
        refs = SB._git(sb.root, 'for-each-ref', '--format=%(refname)', 'refs/p309-test/', 'refs/heads/').split()
        cur = SB._git(sb.root, 'symbolic-ref', 'HEAD').strip()
        for r in refs:
            if r != cur:
                sb.delete_ref(r)
        sb.reset_hard_index(sb.base)

    def valid(self, sb, **kw):
        self.fresh(sb)
        return SB.build_valid(sb, OWN_REL, OWN_SHA, **kw)

    def no_production_artifacts(self, sb=None):
        own = SB.own_repo()
        gp = V._PROD_FIELDS['grant_path']
        self.assertFalse(os.path.exists(os.path.join(own, gp)))
        rc0 = SB.subprocess.run(['git', '-C', own, 'cat-file', '-e', 'HEAD:' + gp], capture_output=True)
        self.assertNotEqual(rc0.returncode, 0)
        for ns in V.FORBIDDEN_REF_NAMESPACES:                                    # r1's and r2's namespace (r2 V2)
            self.assertEqual(SB._git(own, 'for-each-ref', '--format=%(refname)', ns).strip(), '')
        if sb is not None:
            for ns in V.FORBIDDEN_REF_NAMESPACES:
                self.assertEqual(SB._git(sb.root, 'for-each-ref', '--format=%(refname)', ns).strip(), '')
            rc = SB.subprocess.run(['git', '-C', sb.root, 'cat-file', '-e', 'HEAD:' + gp], capture_output=True)
            self.assertNotEqual(rc.returncode, 0)

    # -- D1 / N1 -------------------------------------------------------------------------------------------------------
    def test_D1_real_band_production_context_dry(self):
        for item in (REAL_DESC_5, REAL_IV_5):
            self.refused(V.admission_decision(item), 'no grant')
        # the same through verify_cert: a REAL-band certificate (an h5 decoy moved into the band) is refused at parse
        # time; the tripwire proves nothing is evaluated
        with open(os.path.join(RNS, 'evidence', 'srk_decoys', 'h5_k1_2_E0_1_32.json')) as fh:
            d = json.load(fh)
        m = copy.deepcopy(d['certificates'][sorted(d['certificates'])[0]])
        m['block'] = ['5/4', '41/32']  # q309: literal-ok (parse-time refusal probe; nothing evaluated)
        m['e_c'] = fs((Fr(5, 4) + Fr(41, 32)) / 2)  # q309: literal-ok (parse-time refusal probe; nothing evaluated)
        m['weight_block'] = list(m['block'])
        r = V.verify_cert(resha(m), d.get('kernel'))
        self.assertEqual(r['verdict'], 'REFUSE')
        self.assertTrue(r['reason'].startswith('quarantine:') and 'no grant' in r['reason'], r['reason'])
        self.no_production_artifacts()

    def test_N01_no_grant(self):
        self.refused(V.admission_decision(REAL_DESC_5), 'no grant')
        with SB.Sandbox('n01') as sb:
            sb.commit({SB.TEST_MANIFEST_PATH: SB.manifest_bytes([{'path': OWN_REL, 'sha256': OWN_SHA}])}, 'manifest')
            ctx = V.TestContext(sb.root)
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'no grant')
            raw, fk = self.items[0][2], self.items[0][3]
            r = V.verify_cert(raw, fk, ctx=ctx)
            self.assertEqual(r['verdict'], 'REFUSE')
            self.no_production_artifacts(sb)

    # -- N2-N5 ---------------------------------------------------------------------------------------------------------
    def test_N02_malformed_grant(self):
        with SB.Sandbox('n02') as sb:
            ctx = V.TestContext(sb.root)
            cases = {
                'invalid JSON': dict(grant_raw=b'{"schema": "P309_TEST_GRANT/1", '),
                'missing field': dict(grant_over={'runtime': SB.DELETE}),
                'wrong type': dict(grant_over={'frozen_commit': 12345}),
                'unknown schema': dict(grant_over={'schema': 'P309_TEST_GRANT/2'}),
                'Ew lo >= hi': dict(grant_over={'drift_hull_Ew': ['201/512', '341/1024']}),
                'non-rational': dict(grant_over={'cell_interval': ['0.3333', '20/51']}),
            }
            for name, kw in cases.items():
                self.valid(sb, **kw)
                self.refused(V.admission_decision(self.test_desc, ctx=ctx))
            self.valid(sb)
            self.assertEqual(V.admission_decision(self.test_desc, ctx=ctx)[0], 'ADMIT')   # the control is valid
            self.no_production_artifacts(sb)

    def test_N03_wrong_cell(self):
        with SB.Sandbox('n03') as sb:
            ctx = V.TestContext(sb.root)
            for cell in ('TEST_ONLY_SOMETHING_ELSE', 1, ['TEST_ONLY_DO_NOT_EXECUTE']):
                self.valid(sb, grant_over={'cell': cell})
                self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'cell')

    def test_N04_wrong_Ew(self):
        with SB.Sandbox('n04') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb)
            outside = dict(self.test_desc, block=['341/1024', '205/512'], weight_block=['341/1024', '201/512'])
            self.refused(V.admission_decision(outside, ctx=ctx), 'not inside Ew')
            wb = dict(self.test_desc, weight_block=['341/1024', '200/512'])
            self.refused(V.admission_decision(wb, ctx=ctx), 'weight block')
            self.valid(sb, grant_over={'drift_hull_Ew': ['340/1024', '201/512']})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'outward')

    def test_N05_wrong_verifier_id(self):
        with SB.Sandbox('n05') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb, grant_over={'verifier_id': 'sha256:' + 'f' * 64})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'verifier_id')

    # -- N6-N8 ---------------------------------------------------------------------------------------------------------
    def test_N06_wrong_frozen_identity(self):
        with SB.Sandbox('n06') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb, grant_over={'frozen_manifest_sha256': 'e' * 64})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'manifest sha256')
            self.fresh(sb)
            side = sb.commit({SB.TEST_MANIFEST_PATH: SB.manifest_bytes([{'path': OWN_REL, 'sha256': OWN_SHA}])},
                             'side manifest (not an ancestor)', parents=[sb.base])
            mb = SB.manifest_bytes([{'path': OWN_REL, 'sha256': OWN_SHA}])
            gc = sb.commit({SB.TEST_GRANT_PATH: SB.grant_bytes(SB.test_grant(side, SB.hashlib.sha256(mb).hexdigest(),
                                                                              'sha256:' + OWN_SHA))}, 'grant')
            sb.update_ref(SB.TEST_MARKER, gc)
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'ancestor')
            self.valid(sb, pins=[{'path': 'some/other/file.py', 'sha256': OWN_SHA}])
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'does not pin')
            self.valid(sb, pins=[{'path': OWN_REL, 'sha256': 'd' * 64}])
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'does not pin')

    def test_N07_marker_and_grant_commit(self):
        with SB.Sandbox('n07') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb, set_marker=False)
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'marker')                      # absent
            fc, gc, _ = self.valid(sb)
            sb.update_ref(SB.TEST_MARKER, fc)
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'marker')                      # elsewhere
            fc, gc, _ = self.valid(sb)
            sb.update_ref('refs/p309-test/TEST_ONLY_CONSUMED', gc)
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'only ref')                    # consumed
            fc, gc, _ = self.valid(sb)
            sb.update_ref('refs/heads/extra-at-grant', gc)                   # a ref AT the grant commit itself:
            self.assertEqual(V.admission_decision(self.test_desc, ctx=ctx)[0], 'ADMIT')     # allowed (erratum E1-1)
            child = sb.commit({'TEST_ONLY/child.txt': 'child\n'}, 'child of the grant commit', parents=[gc])
            sb.update_ref('refs/heads/extra-descendant', child)              # a STRICT descendant of the grant commit
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'strict descendant')
            fc, gc, _ = self.valid(sb)
            sb.commit({'TEST_ONLY/after.txt': 'after\n'}, 'after the grant')
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'HEAD is not the grant commit')
            self.valid(sb, extra_files={'TEST_ONLY/also.txt': 'also\n'})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'more than the grant path')
            fc, gc, _ = self.valid(sb)
            sb.commit({SB.TEST_GRANT_PATH: None}, 'remove grant')
            g2 = sb.commit({SB.TEST_GRANT_PATH: SB.grant_bytes(SB.test_grant(
                fc, SB.hashlib.sha256(SB.manifest_bytes([{'path': OWN_REL, 'sha256': OWN_SHA}])).hexdigest(),
                'sha256:' + OWN_SHA))}, 're-add grant')
            sb.update_ref(SB.TEST_MARKER, g2)
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'added by 2 commits')
            self.valid(sb, grant_over={'not_after_utc': '2020-01-01T00:00:00Z'})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'expired')

    def test_N08_wrong_host_or_runtime(self):
        with SB.Sandbox('n08') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb, grant_over={'execution_host': {'host_id_sha256': 'c' * 64}})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'host')
            self.valid(sb, grant_over={'runtime': {'python': '0.0.0'}})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'runtime')

    # -- N9-N11: structural separation ---------------------------------------------------------------------------------
    def test_N09_test_authorization_cannot_admit_real_band(self):
        with SB.Sandbox('n09') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb)
            self.assertEqual(V.admission_decision(self.test_desc, ctx=ctx)[0], 'ADMIT')     # the context is valid
            for item in (REAL_DESC_5, REAL_DESC_3, REAL_IV_5):
                self.refused(V.admission_decision(item, ctx=ctx), 'production context')
            self.no_production_artifacts(sb)

    def test_N10_production_cannot_be_synthesized(self):
        with SB.Sandbox('n10') as sb:
            prod_shaped = {
                'schema': 'P309_GRANT/1', 'campaign': 'p5y_k5_cell309_p309_r2',
                'cell': 309,  # q309: literal-ok (production-SHAPED content at the TEST path; must be refused)
                'geometry': {'h': '5', 'k': '1/2'}, 'cell_interval': ['1/3', '20/51'],
                'drift_hull_Ew': ['341/1024', '201/512']}
            fc, gc, msha = self.valid(sb, grant_over=prod_shaped)
            ctx = V.TestContext(sb.root)
            self.refused(V.admission_decision(REAL_DESC_5), 'no grant')                    # (a) production context
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'schema')          # (a) test context
            self.refused(V.admission_decision(REAL_DESC_5, ctx=ctx), 'production context')  # (b)
            with self.assertRaises(V.TestContextRefused):                                  # (c) this repository
                V.TestContext(SB.own_repo())
            fake = os.path.join(sb.sandbox_base, 'n10-fake-worktree-%s' % os.getpid())     # (c) a worktree of it
            os.makedirs(fake, exist_ok=True)
            try:
                with open(os.path.join(fake, '.git'), 'w') as fh:
                    fh.write('gitdir: %s\n' % os.path.join(SB.own_repo(), '.git'))
                with self.assertRaises(V.TestContextRefused):
                    V.TestContext(fake)
            finally:
                SB.shutil.rmtree(fake)
            self.no_production_artifacts(sb)

    def test_N11_synthetic_marker_not_production(self):
        with SB.Sandbox('n11') as sb:
            prod_shaped = {'schema': 'P309_GRANT/1', 'campaign': 'p5y_k5_cell309_p309_r2',
                           'cell': 309,  # q309: literal-ok (production-SHAPED content at the TEST path; must be refused)
                           'geometry': {'h': '5', 'k': '1/2'}}
            fc, gc, _ = self.valid(sb, grant_over=prod_shaped)
            self.assertEqual(SB._git(sb.root, 'rev-parse', SB.TEST_MARKER).strip(), gc)
            ctx = V.TestContext(sb.root)
            self.refused(V.admission_decision(REAL_DESC_5))                                  # production context
            self.refused(V.admission_decision(self.test_desc, ctx=ctx))                      # test context
            self.refused(V.admission_decision(REAL_DESC_5, ctx=ctx))
            # the only marker anywhere is the TEST marker: a production call is still refused
            self.assertEqual(SB._git(SB.own_repo(), 'for-each-ref', '--format=%(refname)', 'refs/p309-test/').strip(),
                             '')
            self.refused(V.admission_decision(REAL_IV_5), 'no grant')
            self.no_production_artifacts(sb)

    # -- N12, P2: review mode ------------------------------------------------------------------------------------------
    def _seal(self, sb, shas, parents=None, extra=None):
        body = {'schema': 'P309_TEST_RESULT/1', 'stage1a': {'certificates': list(shas)}}
        files = {SB.TEST_RESULT_PATH: json.dumps(body, sort_keys=True) + '\n'}
        files.update(extra or {})
        return sb.commit(files, 'TEST_ONLY seal', parents=parents)

    def test_N12_review_mode_refusals(self):
        with SB.Sandbox('n12') as sb:
            ctx = V.TestContext(sb.root)
            listed, other = self.items[0][2]['sha256'], self.items[1][2]['sha256']
            d_other = desc(self.items[1][2])
            self.valid(sb)
            self._seal(sb, [listed])
            self.refused(V.admission_decision(d_other, ctx=ctx, mode='review'), 'not listed')       # not listed
            self.assertEqual(V.admission_decision(self.test_desc, ctx=ctx, mode='review')[0], 'ADMIT')
            fc, gc, _ = self.valid(sb)
            sb.commit({'TEST_ONLY/between.txt': 'x\n'}, 'between grant and seal')
            self._seal(sb, [listed])
            self.refused(V.admission_decision(self.test_desc, ctx=ctx, mode='review'))              # parent not G
            fc, gc, _ = self.valid(sb)
            side = sb.commit({'TEST_ONLY/side.txt': 'side\n'}, 'side', parents=[fc])
            merge = self._seal(sb, [listed], parents=[gc, side])
            sb.reset_hard_index(merge)
            self.refused(V.admission_decision(self.test_desc, ctx=ctx, mode='review'), 'only parent')  # two parents
            self.valid(sb)
            self._seal(sb, [listed], extra={'TEST_ONLY/extra.txt': 'extra\n'})
            self.refused(V.admission_decision(self.test_desc, ctx=ctx, mode='review'), 'more than the sealed')
            self.valid(sb)
            self._seal(sb, [listed])
            sb.commit({SB.TEST_RESULT_PATH: json.dumps({'stage1a': {'certificates': [listed, other]}}) + '\n'},
                      'result changed after the seal')
            self.refused(V.admission_decision(self.test_desc, ctx=ctx, mode='review'), 'differs')    # changed
            self.refused(V.admission_decision({'geometry': {'h': '3', 'k': '1/2'}, 'lo': '341/1024',
                                               'hi': '201/512'}, ctx=ctx, mode='review'), 'interval')

    def test_P2_review_mode_listed_subset(self):
        with SB.Sandbox('p2') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb)
            group = [it for it in self.items if it[0] == self.items[0][0]]
            listed = group[:2]
            self._seal(sb, [it[2]['sha256'] for it in listed])
            for it in group:
                res = V.admission_decision(desc(it[2]), ctx=ctx, mode='review')
                if it in listed:
                    self.assertEqual(res[0], 'ADMIT', res)
                else:
                    self.refused(res, 'not listed')
            self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'HEAD is not the grant commit')  # official
            rel, label, raw, fk = listed[0]
            _ALLOW_TEST_EVAL[0] = True
            try:
                r = V.verify_cert(raw, fk, ctx=ctx, mode='review')
            finally:
                _ALLOW_TEST_EVAL[0] = False
            c = committed_results()[rel][label]
            self.assertEqual((r['verdict'], r.get('reason')), (c['verdict'], c['reason']))

    # -- N13 -----------------------------------------------------------------------------------------------------------
    def test_N13_fail_closed(self):
        with SB.Sandbox('n13') as sb:
            ctx = V.TestContext(sb.root)
            self.valid(sb)
            self.assertEqual(V.admission_decision(self.test_desc, ctx=ctx)[0], 'ADMIT')
            orig = V._run_git

            def boom(*a, **k):
                raise RuntimeError('simulated: git unreadable')
            V._run_git = boom
            try:
                self.refused(V.admission_decision(self.test_desc, ctx=ctx), 'failed closed')
                self.refused(V.admission_decision(REAL_DESC_5), 'failed closed')
            finally:
                V._run_git = orig
            os.rename(os.path.join(sb.root, '.git', 'HEAD'), os.path.join(sb.root, '.git', 'HEAD.moved'))
            try:
                self.refused(V.admission_decision(self.test_desc, ctx=ctx))
            finally:
                os.rename(os.path.join(sb.root, '.git', 'HEAD.moved'), os.path.join(sb.root, '.git', 'HEAD'))
            self.assertEqual(V.admission_decision(self.test_desc, ctx=ctx)[0], 'ADMIT')

    # -- P1 ------------------------------------------------------------------------------------------------------------
    def test_P1_test_band_positive_path(self):
        with SB.Sandbox('p1') as sb:
            fc, gc, _ = self.valid(sb)
            ctx = V.TestContext(sb.root)
            self.assertEqual(len(self.items), 16)
            _ALLOW_TEST_EVAL[0] = True
            try:
                for rel, label, raw, fk in self.items:
                    dec = V.admission_decision(V.Cert(raw, fk), ctx=ctx)
                    self.assertEqual(dec[0], 'ADMIT', dec)
                    r = V.verify_cert(raw, fk, ctx=ctx)
                    c = committed_results()[rel][label]
                    self.assertEqual((r['verdict'], r.get('reason')), (c['verdict'], c['reason']), (rel, label))
                    self.assertEqual(r.get('boxes'), c.get('boxes'))
            finally:
                _ALLOW_TEST_EVAL[0] = False
            self.no_production_artifacts(sb)


# ======================================================================================================================
# Part 3: P309-r2 verifier-side changes (gate step 3; governance/BRIEF_R2_VERIFIER_AUTHOR_1.md)
_R1_NAMESPACE = 'refs/p5y-k5-cell309-p309-r1/'  # q309: literal-ok (expected value for the V2 static check; compared only, never a ref operand)
_R2_NAMESPACE = 'refs/p5y-k5-cell309-p309-r2/'  # q309: literal-ok (expected value for the V2 static check; compared only, never a ref operand)
_MY_FILES = ('verify/srk_verify_indep_scoped.py', 'verify/scoped_sandbox.py', 'verify/run_verify_all_scoped.py',
             'tests/test_verify_scoped.py')


def _tree_of(path):
    with open(path) as fh:
        return ast.parse(fh.read())


def _assigned(tree, name):
    """the value of the unique module-level assignment `name = ...` (None if absent or not unique)"""
    vals = [st.value for st in tree.body if isinstance(st, ast.Assign) and len(st.targets) == 1
            and isinstance(st.targets[0], ast.Name) and st.targets[0].id == name]
    return vals[0] if len(vals) == 1 else None


def _def(tree, qual):
    """the unique module-level function, class, or class member `qual` ('f', 'C' or 'C.f'); None otherwise"""
    node, body = None, tree.body
    for part in qual.split('.'):
        hits = [n for n in body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == part]
        if len(hits) != 1:
            return None
        node, body = hits[0], hits[0].body
    return node


def _loads(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def _callees(node):
    return {ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)}


def _owners(tree):
    """id(node) -> qualified name of its outermost enclosing function ('f' or 'C.f'), for every node inside one"""
    out = {}
    for st in tree.body:
        members = [(st.name, st)] if isinstance(st, ast.FunctionDef) else (
            [('%s.%s' % (st.name, m.name), m) for m in st.body if isinstance(m, ast.FunctionDef)]
            if isinstance(st, ast.ClassDef) else [])
        for qual, fn in members:
            for n in ast.walk(fn):
                out[id(n)] = qual
    return out


class TestR2Verifier(_Ledgered):
    LEDGER_CLASS = 'SYNTHETIC'
    LEDGER_DRIFTS = []
    LEDGER_NOTES = ('P309-r2 verifier-side checks (V2 namespaces, V3 base rule, V4 scratch root): static checks, guard '
                    'calls and sandboxes only; nothing evaluated; no ref in either production namespace')

    # -- V2 ------------------------------------------------------------------------------------------------------------
    def test_V2_both_namespaces_forbidden(self):
        both = {_R1_NAMESPACE, _R2_NAMESPACE}
        # (1) the variant's TestContext refusal (_validated_sandbox) iterates over a tuple holding both namespaces
        vt = _tree_of(V._OWN_PATH)
        prior, marker = _assigned(vt, 'PRIOR_PRODUCTION_REF_NAMESPACE'), _assigned(vt, 'PRODUCTION_MARKER')
        self.assertTrue(isinstance(prior, ast.Constant) and prior.value == _R1_NAMESPACE)
        self.assertTrue(isinstance(marker, ast.Constant) and marker.value.startswith(_R2_NAMESPACE)
                        and '/' not in marker.value[len(_R2_NAMESPACE):])
        self.assertEqual(ast.unparse(_assigned(vt, 'FORBIDDEN_REF_NAMESPACES')),
                         '(PRIOR_PRODUCTION_REF_NAMESPACE, PRODUCTION_REF_NAMESPACE)')
        self.assertEqual(set(V.FORBIDDEN_REF_NAMESPACES), both)
        self.assertEqual(V.PRODUCTION_REF_NAMESPACE, _R2_NAMESPACE)                   # OD-R2-1 (b), provisional
        vs = _def(vt, '_validated_sandbox')
        loops = [n for n in ast.walk(vs) if isinstance(n, ast.For) and ast.unparse(n.iter) == 'FORBIDDEN_REF_NAMESPACES']
        self.assertEqual(len(loops), 1)
        lister = [c for c in ast.walk(loops[0]) if isinstance(c, ast.Call)
                  and any(isinstance(a, ast.Constant) and a.value == 'for-each-ref' for a in c.args)]
        self.assertTrue(lister and all(ast.unparse(c.args[-1]) == ast.unparse(loops[0].target) for c in lister))
        self.assertNotIn('PRODUCTION_REF_NAMESPACE', _loads(vs))                        # never one namespace alone
        self.assertIn('_validated_sandbox', _callees(_def(vt, 'TestContext.__init__')))
        # (2) the sandbox helper: _FORBIDDEN_REF_PREFIX is a tuple of both, used by every guard
        st = _tree_of(SB.__file__)
        self.assertEqual(ast.unparse(_assigned(st, '_FORBIDDEN_REF_PREFIX')),
                         '(_FORBIDDEN_REF_PREFIX_R1, _FORBIDDEN_REF_PREFIX_R2)')
        self.assertEqual((_assigned(st, '_FORBIDDEN_REF_PREFIX_R1').value, _assigned(st, '_FORBIDDEN_REF_PREFIX_R2').value),
                         (_R1_NAMESPACE, _R2_NAMESPACE))
        self.assertEqual(set(SB._FORBIDDEN_REF_PREFIX), both)
        self.assertIn('_FORBIDDEN_REF_PREFIX', _loads(_def(st, 'Sandbox._assert_ref')))
        self.assertIn('_FORBIDDEN_REF_PREFIX', _loads(_def(st, 'Sandbox.assert_no_production_refs')))
        for meth in ('update_ref', 'delete_ref', 'reset_hard_index'):                    # every ref-moving method
            self.assertIn('self._assert_ref', _callees(_def(st, 'Sandbox.' + meth)))
        for meth in ('__init__', '__exit__'):
            self.assertIn('self.assert_no_production_refs', _callees(_def(st, 'Sandbox.' + meth)))
        # (3) the guard refuses a ref name in either namespace; it raises before any git call, so no ref is created
        for ns in sorted(both):
            with self.assertRaises(RuntimeError):
                SB.Sandbox._assert_ref(ns + 'TEST_ONLY_probe')
        SB.Sandbox._assert_ref(SB.TEST_MARKER)                                           # positive control

    # -- V3 ------------------------------------------------------------------------------------------------------------
    def test_V3_base_rule_static(self):
        """P6(e): the sandbox branch starts at sandbox_base_commit()'s result, and no other read of the real
        repository's HEAD is used as a sandbox base in verify/ or in this file"""
        fns = os.path.dirname(os.path.dirname(os.path.realpath(V._OWN_PATH)))
        st = _tree_of(SB.__file__)
        init = _def(st, 'Sandbox.__init__')
        self.assertEqual([a.arg for a in init.args.args], ['self', 'tag', 'expect_freeze_records'])  # no base parameter
        sets = [ast.unparse(c) for c in ast.walk(init) if isinstance(c, ast.Call)
                and ast.unparse(c.func) == 'self.update_ref']
        self.assertEqual(sets, ["self.update_ref('refs/heads/fc2-sandbox', self.base_commit)"])
        binds = [n for n in ast.walk(init) if isinstance(n, ast.Assign)
                 and any('self.base_commit' in ast.unparse(t) for t in n.targets)]
        self.assertEqual(len(binds), 1)
        self.assertEqual(ast.unparse(binds[0].value.func), 'sandbox_base_commit')
        # every git revision operand naming HEAD in this author's Python files: its owner, and the repository it names
        head_rx = re.compile(r'HEAD([~^:@{.].*)?$')
        in_sandbox = {'self.root', 'sb.root'}
        allowed = {
            ('verify/scoped_sandbox.py', 'sandbox_base_commit'): {'repo'},              # the rule: the one base read
            ('verify/scoped_sandbox.py', 'Sandbox.__init__'): in_sandbox,               # the sandbox's own HEAD
            ('verify/scoped_sandbox.py', 'Sandbox.head'): in_sandbox,
            ('verify/scoped_sandbox.py', 'Sandbox.reset_hard_index'): in_sandbox,
            ('verify/scoped_sandbox.py', 'Sandbox.freeze_record_commits'): in_sandbox,
            ('verify/srk_verify_indep_scoped.py', '_admission'): {'repo'},              # admission reads of the
                                                                                        # repository under admission
            ('tests/test_verify_scoped.py', 'TestFC2Scoped.fresh'): in_sandbox,
            ('tests/test_verify_scoped.py', 'TestFC2Scoped.no_production_artifacts'): {'own', 'sb.root'},  # absence
            ('tests/test_verify_scoped.py', 'TestFC2Scoped.test_N13_fail_closed'): in_sandbox,
        }
        seen = set()
        for rel in _MY_FILES:
            tree = _tree_of(os.path.join(fns, rel))
            own = _owners(tree)
            parent = {id(ch): p for p in ast.walk(tree) for ch in ast.iter_child_nodes(p)}
            for n in ast.walk(tree):
                if not (isinstance(n, ast.Constant) and isinstance(n.value, str) and head_rx.match(n.value)):
                    continue
                if isinstance(parent.get(id(n)), ast.Compare):                         # compared, not an operand
                    continue
                key = (rel, own.get(id(n)))
                self.assertIn(key, allowed, (rel, n.lineno, n.value))
                seen.add(key)
                call = parent.get(id(n))
                while call is not None and not isinstance(call, ast.Call):
                    call = parent.get(id(call))
                self.assertIsNotNone(call, (rel, n.lineno))
                repo = call.args[0] if call.args else None
                if isinstance(repo, ast.List) and len(repo.elts) > 2 and ast.unparse(repo.elts[1]) == "'-C'":
                    repo = repo.elts[2]                                                 # ['git', '-C', <repo>, ...]
                self.assertIn(ast.unparse(repo) if repo is not None else None, allowed[key],
                              (rel, n.lineno, ast.unparse(call)[:100]))
        self.assertIn(('verify/scoped_sandbox.py', 'sandbox_base_commit'), seen)
        # sandbox_base_commit() is called by Sandbox.__init__, and otherwise only on sandboxes by the shape test
        for rel in _MY_FILES:
            tree = _tree_of(os.path.join(fns, rel))
            own = _owners(tree)
            for c in ast.walk(tree):
                if isinstance(c, ast.Call) and ast.unparse(c.func) in ('sandbox_base_commit', 'SB.sandbox_base_commit'):
                    where = (rel, own.get(id(c)))
                    if where != ('verify/scoped_sandbox.py', 'Sandbox.__init__'):
                        self.assertEqual(where, ('tests/test_verify_scoped.py',
                                                 'TestR2Verifier.test_V3_base_rule_shapes'))
                        self.assertEqual(ast.unparse(c.args[0]), 'sb.root')
        # the variant builds no sandbox (it does not import the helper)
        vt = _tree_of(V._OWN_PATH)
        imported = {a.name for n in ast.walk(vt) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module for n in ast.walk(vt) if isinstance(n, ast.ImportFrom)}
        self.assertNotIn('scoped_sandbox', imported)

    def test_V3_base_rule_shapes(self):
        """the base rule on every record shape, built with a TEST-named record path inside a sandbox (no production
        name is used); a malformed record raises FreezeRecordError, never a refusal"""
        rec = 'TEST_ONLY/FREEZE_RECORD.json'

        def body(commit):
            return json.dumps({'freeze_commit': commit}, sort_keys=True) + '\n'
        with SB.Sandbox('v3') as sb:
            self.assertEqual(sb.base, sb.base_commit)                     # the sandbox starts at the rule's base
            self.assertIn(sb.base_mode, ('development', 'post-freeze'))
            self.assertEqual(sb.freeze_record_commits(), [])              # P6(b): 0 record commits in the sandbox
            with self.assertRaises(SB.FreezeRecordError):                 # the postcondition detects a mismatch
                sb.check_freeze_records(1)
            b0 = sb.head()
            self.assertEqual(SB.sandbox_base_commit(sb.root, rec), (b0, 'development'))
            fp = sb.commit({'TEST_ONLY/synthetic_freeze.txt': 'F-prime\n'}, 'TEST_ONLY synthetic F-prime')
            frp = sb.commit({rec: body(fp)}, 'TEST_ONLY record-only child FR-prime')
            self.assertEqual(SB.sandbox_base_commit(sb.root, rec), (fp, 'post-freeze'))
            sb.commit({'TEST_ONLY/checkpoint.txt': 'after FR-prime\n'}, 'TEST_ONLY checkpoint-style commit')
            self.assertEqual(SB.sandbox_base_commit(sb.root, rec), (fp, 'post-freeze'))
            side = sb.commit({'TEST_ONLY/side.txt': 'side\n'}, 'TEST_ONLY side branch', parents=[fp])
            bad = {
                'freeze_commit is not the only parent': sb.commit({rec: body(b0)}, 'TEST_ONLY', parents=[fp]),
                'the record commit touches another path': sb.commit({rec: body(fp), 'TEST_ONLY/other.txt': 'o\n'},
                                                                    'TEST_ONLY', parents=[fp]),
                'a second commit changes the record': sb.commit({rec: body(fp) + '\n'}, 'TEST_ONLY', parents=[frp]),
                'a second commit removes the record': sb.commit({rec: None}, 'TEST_ONLY', parents=[frp]),
                'the record is not JSON': sb.commit({rec: 'not json\n'}, 'TEST_ONLY', parents=[fp]),
                'the record is a JSON array': sb.commit({rec: json.dumps([fp]) + '\n'}, 'TEST_ONLY', parents=[fp]),
                'freeze_commit is missing': sb.commit({rec: json.dumps({'commit': fp}) + '\n'}, 'TEST_ONLY',
                                                      parents=[fp]),
                'freeze_commit is not 40-hex': sb.commit({rec: body('F-prime')}, 'TEST_ONLY', parents=[fp]),
                'the record commit is a merge': sb.commit({rec: body(fp)}, 'TEST_ONLY', parents=[fp, side]),
            }
            for label, tip in sorted(bad.items()):
                with self.subTest(label):
                    sb.reset_hard_index(tip)
                    with self.assertRaises(SB.FreezeRecordError) as cm:
                        SB.sandbox_base_commit(sb.root, rec)
                    self.assertNotIsInstance(cm.exception, (V.Refusal, V.TestContextRefused))
            sb.reset_hard_index(frp)
            self.assertEqual(SB.sandbox_base_commit(sb.root, rec), (fp, 'post-freeze'))
            sb.reset_hard_index(sb.base)

    # -- V4 ------------------------------------------------------------------------------------------------------------
    def test_V4_scratch_root_refusals(self):
        """a negative control for each refusal case of P309_SCRATCH_ROOT / P309_FOREIGN_ROOTS, and positive controls"""
        good = SB.scratch_sandbox_base()                     # this run's own P309_SCRATCH_ROOT (raises if invalid)
        ctl = tempfile.mkdtemp(prefix='v4-controls-', dir=os.path.dirname(good))
        try:
            sub = os.path.join(ctl, 'sub')
            os.mkdir(sub)
            a_file = os.path.join(ctl, 'a_file')
            with open(a_file, 'w') as fh:
                fh.write('not a directory\n')
            link = os.path.join(ctl, 'link_to_sub')
            os.symlink(sub, link)
            repo = SB.own_repo()
            S, F = SB.SCRATCH_ENV, SB.FOREIGN_ENV
            nowhere = '/nonexistent-p309-v4-control'
            cases = [
                ('unset', {}, 'unset or empty'),
                ('empty', {S: ''}, 'unset or empty'),
                ('relative', {S: 'relative/scratch'}, 'is not absolute'),
                ('trailing separator', {S: sub + os.sep}, 'differs from its realpath'),
                ('dot-dot component', {S: os.path.join(sub, os.pardir, 'sub')}, 'differs from its realpath'),
                ('symlink', {S: link}, 'differs from its realpath'),
                ('missing', {S: os.path.join(ctl, 'missing')}, 'is not an existing directory'),
                ('a file', {S: a_file}, 'is not an existing directory'),
                ('the repository itself', {S: repo}, 'lies inside the repository'),
                ('inside the repository', {S: os.path.join(repo, 'level4')}, 'lies inside the repository'),
                ('equal to a foreign root', {S: sub, F: sub}, 'overlaps'),
                ('inside a foreign root', {S: sub, F: ctl}, 'overlaps'),
                ('contains a foreign root', {S: ctl, F: os.path.join(sub, 'deeper')}, 'overlaps'),
                ('foreign root reached through a symlink', {S: sub, F: link}, 'overlaps'),
                ('second foreign entry overlaps', {S: sub, F: os.pathsep.join([nowhere, ctl])}, 'overlaps'),
                ('foreign entry relative', {S: sub, F: 'relative/foreign'}, 'is not absolute'),
                ('foreign variable empty', {S: sub, F: ''}, 'is not absolute'),
                ('foreign list with an empty entry', {S: sub, F: nowhere + os.pathsep}, 'is not absolute'),
            ]
            for label, env, why in cases:
                with self.subTest(label):
                    with self.assertRaisesRegex(SB.ScratchRootError, re.escape(why)):
                        SB.scratch_sandbox_base(environ=env)
            self.assertEqual(SB.scratch_sandbox_base(environ={S: sub}), os.path.join(sub, SB.SANDBOX_DIRNAME))
            self.assertEqual(SB.scratch_sandbox_base(environ={S: sub, F: os.pathsep.join([nowhere, os.path.join(
                ctl, 'other')])}), os.path.join(sub, SB.SANDBOX_DIRNAME))
        finally:
            shutil.rmtree(ctl)
        # the constructor takes its directory from scratch_sandbox_base() first, and there is no fixed path
        st = _tree_of(SB.__file__)
        self.assertEqual(ast.unparse(_def(st, 'Sandbox.__init__').body[0]), 'self.sandbox_base = scratch_sandbox_base()')
        self.assertIsNone(_assigned(st, 'SANDBOX_BASE'))

    def test_V4_no_session_path_in_code(self):
        """no hard-coded session or scratchpad path in the string constants of this author's Python files"""
        fns = os.path.dirname(os.path.dirname(os.path.realpath(V._OWN_PATH)))
        bad = ('/tmp/', 'scratchpad', 'claude-0', 'session_01')
        me = 'TestR2Verifier.test_V4_no_session_path_in_code'
        for rel in _MY_FILES:
            tree = _tree_of(os.path.join(fns, rel))
            own = _owners(tree)
            hits = [(rel, n.lineno, n.value[:60]) for n in ast.walk(tree)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str) and own.get(id(n)) != me
                    and any(b in n.value for b in bad)]
            self.assertEqual(hits, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
