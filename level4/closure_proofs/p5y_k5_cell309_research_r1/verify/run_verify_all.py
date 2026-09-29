#!/usr/bin/env python3
"""
Run the independent SRK verifier over every decoy certificate file and the SRK_CERT_SPEC.md section 5 required
rejections (mutants), recording everything in verify/VERIFY_RESULTS.json.

    python3 run_verify_all.py [--max-depth 24] [--order 8] [--no-mutants] [--redo] [--remutate] [--jobs J]
                              [--unit-tests] [--files F ...]

Files scanned by default: evidence/srk_decoys/*.json, evidence/srk_decoys_cell/*.json, evidence/srk_decoys_prelim/*.json
and evidence/srk_decoys_taboo/*.json (read only, never modified).  Results are written after every certificate; an
existing (file, index, sha256) result is reused unless --redo.  --remutate keeps a recorded genuine verdict (same
sha256) and re-runs only the mutant battery.

Harness v2 (review R2 condition C3):
* every mutant has a REASON-SPECIFIC expectation, so that a mutant refused/rejected for a reason other than its own
  single defect no longer passes;
* each mutant has exactly one defect: 7q moves weight_block together with block (only the quarantine band is wrong),
  7h shifts weight_block together with block (only the drift is non-dyadic), 7f is run as a bare certificate (only the
  kernel value is unknown), and the kernel-conflict case is a separate probe 7i;
* every mutant result records harness_sha256 (this file) and verifier_sha256 (srk_verify_indep.py).
Mutants 1-5 get a recomputed sha256 (so that the mathematics, not the hash, is exercised); mutant 6 alters the hash.
The quarantine probe 7q is a parse-time refusal: the verifier refuses it before evaluating anything.
"""
import argparse
import copy
import glob
import hashlib
import json
import multiprocessing as mp
import os
import re
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import srk_verify_indep as V  # noqa: E402

OUT = os.path.join(HERE, 'VERIFY_RESULTS.json')


def _sha_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


HARNESS_SHA = _sha_file(os.path.abspath(__file__))
VERIFIER_SHA = _sha_file(os.path.join(HERE, 'srk_verify_indep.py'))
HARNESS_VERSION = 'v2'
# harness v1 = this file before the review-R2 fix (unchanged on disk from 2026-09-29 15:55 until the v2 rewrite)
LEGACY_V1_SHA = '54840bf4d364f7b4853b542d74f81f9c5cdbd9ad97e5b447a1a2b808e2a8d2be'


def fs(x):
    x = Fr(x)
    return '%d/%d' % (x.numerator, x.denominator)


def resha(c):
    c = dict(c)
    c['sha256'] = V.canonical_sha(c)
    return c


# ----------------------------------------------------------------------------------------------------------------------
# reason-specific expectations (the reason strings are those emitted by srk_verify_indep.py)
_CLAIM_REJECT = re.compile(r'^C[123] (is FALSE at|UNPROVEN at depth limit)')


def _reason(r):
    return r.get('reason') or ''


def claim_reject(r):
    """REJECT because a claim (C1)-(C3) is disproved or not proved -- not (C4), sha256, refusal or internal error."""
    return r['verdict'] == 'REJECT' and bool(_CLAIM_REJECT.match(_reason(r)))


def c4_reject(r):
    return r['verdict'] == 'REJECT' and _reason(r).startswith('(C4) fails')


def proved_or_claim_reject(r):
    return r['verdict'] == 'ACCEPT' or claim_reject(r)


def refuse_with(fragment, startswith=False):
    def chk(r):
        if r['verdict'] != 'REFUSE':
            return False
        return _reason(r).startswith(fragment) if startswith else (fragment in _reason(r))
    return chk


EXPECT = {
    'C4': ('REJECT, reason (C4)', c4_reject),
    'CLAIM': ('REJECT, reason a (C1)-(C3) failure', claim_reject),
    'PROVE_OR_CLAIM': ('ACCEPT (claim proved true) or REJECT with a (C1)-(C3) reason', proved_or_claim_reject),
    'SHA': ('REJECT, reason sha256 mismatch', lambda r: r['verdict'] == 'REJECT' and _reason(r) == 'sha256 mismatch'),
}


def mutants(raw):
    """SRK_CERT_SPEC.md section 5, items 1-6 (+ informative variants).
    Returns list of (name, cert, expect_label, check, file_kernel_mode) with file_kernel_mode 'inherit'."""
    out = []

    def add(name, cert, key):
        lab, chk = EXPECT[key]
        out.append((name, cert, lab, chk, 'inherit'))
    m = copy.deepcopy(raw)
    m['Gamma'] = fs(Fr(raw['Gamma']) - Fr(1, 10 ** 6))
    add('1_gamma_minus_1e-6', resha(m), 'C4')
    m = copy.deepcopy(raw)
    m['V0'] = {k: fs(Fr(v) * (1 - Fr(1, 256))) for k, v in raw['V0'].items()}
    add('2_V0_scaled_1-2^-8', resha(m), 'PROVE_OR_CLAIM')          # spec erratum SE-1
    m = copy.deepcopy(raw)
    m['V0'] = {k: fs(Fr(v) * (1 - Fr(1, 4))) for k, v in raw['V0'].items()}
    add('2x_V0_scaled_3/4 (SE-1 mandatory)', resha(m), 'CLAIM')
    lam = Fr(raw.get('lam', '0'))
    if lam > 0:
        m = copy.deepcopy(raw)
        keys = set(raw['V0']) | set(raw['W0'])
        m['V0'] = {k: fs(Fr(raw['V0'].get(k, '0')) - lam * Fr(raw['W0'].get(k, '0'))) for k in keys}
        add('3_V0_minus_lam_W0', resha(m), 'CLAIM')
    elo, ehi = Fr(raw['block'][0]), Fr(raw['block'][1])
    wb = raw.get('weight_block')
    for nm, (a, b) in (('L', (elo - Fr(1, 8), ehi)), ('R', (elo, ehi + Fr(1, 8))),
                       ('B', (elo - Fr(1, 8), ehi + Fr(1, 8)))):
        for regam in (False, True):
            m = copy.deepcopy(raw)
            m['block'] = [fs(a), fs(b)]
            ec = (a + b) / 2
            m['e_c'] = fs(ec)
            if wb is not None:
                m['weight_block'] = [fs(min(a, Fr(wb[0]))), fs(max(b, Fr(wb[1])))]
            tag = '4%s_block_widened_1/8' % nm
            if regam:
                v00, v10 = Fr(raw['V0'].get('0,0', '0')), Fr(raw['V1'].get('0,0', '0'))
                m['Gamma'] = fs(max(v00 + (a - ec) * v10, v00 + (b - ec) * v10))
                tag += '+Gamma_recomputed'
                add(tag, resha(m), 'PROVE_OR_CLAIM')   # REJECT unless the widened claim is true (then proved)
            else:
                add(tag, resha(m), 'C4')
    m = copy.deepcopy(raw)
    m['hermite_index'] = raw['hermite_index'] + 1
    add('5_hermite_index_plus_1', resha(m), 'PROVE_OR_CLAIM')
    m = copy.deepcopy(raw)
    m['sha256'] = ('0' if raw['sha256'][0] != '0' else '1') + raw['sha256'][1:]
    add('6_sha256_altered', m, 'SHA')
    return out


def _meets_band(cert_like):
    """True if (h, k) = (5, 1/2) and block or weight block meets a quarantine band (pure rational comparison)."""
    g = cert_like['geometry']
    if not (Fr(g['h']) == 5 and Fr(g['k']) == Fr(1, 2)):
        return False
    ivs = [cert_like['block']] + ([cert_like['weight_block']] if 'weight_block' in cert_like else [])
    for (lo, hi) in ivs:
        for (a, b) in V.QUARANTINE_BANDS:
            if Fr(lo) <= b and a <= Fr(hi):
                return True
    return False


def malformed(raw, fk):
    """Item 7 (each probe has exactly ONE defect) and the quarantine refusal.
    Returns list of (name, cert, expect_label, check, file_kernel_mode)."""
    out = []
    m = copy.deepcopy(raw)
    del m['W1']
    out.append(('7a_missing_key_W1', m, "REFUSE, reason missing key 'W1'",
                refuse_with("malformed: missing key 'W1'", True), 'inherit'))
    m = copy.deepcopy(raw)
    k0 = sorted(m['V0'])[0]
    m['V0'][k0] = '1.5e3'
    out.append(('7b_non_rational_string', resha(m), 'REFUSE, reason V0[..] not a rational string',
                refuse_with('malformed: V0[%s]: not a rational string' % k0, True), 'inherit'))
    m = copy.deepcopy(raw)
    m['block'] = [raw['block'][1], raw['block'][0]]
    out.append(('7c_e_lo_gt_e_hi', resha(m), 'REFUSE, reason e_lo > e_hi',
                refuse_with('malformed: block: e_lo > e_hi', True), 'inherit'))
    m = copy.deepcopy(raw)
    m['block'] = ['a/b', raw['block'][1]]
    out.append(('7d_garbage_block', resha(m), 'REFUSE, reason block[0] not a rational string',
                refuse_with('malformed: block[0]: not a rational string', True), 'inherit'))
    m = copy.deepcopy(raw)
    m['weight_block'] = [fs(Fr(raw['block'][0]) + Fr(1, 64)), raw['block'][1]]
    out.append(('7e_weight_block_not_containing_block', resha(m), 'REFUSE, reason weight_block does not contain block',
                refuse_with('malformed: weight_block does not contain block', True), 'inherit'))
    # 7f: unknown kernel value, run as a bare certificate so that no file-level key can conflict (single defect)
    m = copy.deepcopy(raw)
    m['kernel'] = 'bogus'
    out.append(('7f_unknown_kernel (bare certificate)', resha(m), "REFUSE, reason unknown kernel 'bogus'",
                refuse_with("malformed: unknown kernel 'bogus'", True), 'none'))
    # 7i: certificate-level kernel valid but conflicting with the file-level kernel (only if the file has one)
    if fk is not None:
        m = copy.deepcopy(raw)
        m['kernel'] = 'taboo' if fk != 'taboo' else 'whole'
        out.append(('7i_kernel_conflicts_with_file_kernel', resha(m), 'REFUSE, reason kernel conflicts with file key',
                    refuse_with('malformed: kernel key conflicts with the file-level kernel key', True), 'inherit'))
    m = copy.deepcopy(raw)
    m['e_c'] = fs(Fr(raw['e_c']) + Fr(1, 1024))
    out.append(('7g_e_c_not_midpoint', resha(m), 'REFUSE, reason e_c != midpoint',
                refuse_with('malformed: e_c != (e_lo + e_hi)/2', True), 'inherit'))
    # 7h: non-dyadic drift: block AND weight_block shifted by -1/3 (or +1/3), never into a quarantine band
    for sh in (Fr(-1, 3), Fr(1, 3)):
        m = copy.deepcopy(raw)
        a, b = Fr(raw['block'][0]) + sh, Fr(raw['block'][1]) + sh
        m['block'] = [fs(a), fs(b)]
        m['e_c'] = fs((a + b) / 2)
        if 'weight_block' in raw:
            m['weight_block'] = [fs(Fr(raw['weight_block'][0]) + sh), fs(Fr(raw['weight_block'][1]) + sh)]
        if not _meets_band(m):
            out.append(('7h_non_dyadic_drift (processed, no crash)', resha(m),
                        'processed: ACCEPT or REJECT with a (C1)-(C3) reason (not refused)', proved_or_claim_reject,
                        'inherit'))
            break
    # 7q: block AND weight_block moved into the quarantine band; the band is the only defect (parse-time refusal)
    if Fr(raw['geometry']['h']) == 5 and Fr(raw['geometry']['k']) == Fr(1, 2):
        m = copy.deepcopy(raw)
        m['block'] = ['6/5', '39/32']  # q309: literal-ok (refusal probe: REFUSED at parse time, nothing evaluated)
        m['e_c'] = fs((Fr(6, 5) + Fr(39, 32)) / 2)  # q309: literal-ok (refusal probe: REFUSED at parse time, nothing evaluated)
        if 'weight_block' in raw:
            m['weight_block'] = list(m['block'])
        out.append(('7q_quarantine_band_refused', resha(m), 'REFUSE, reason quarantine (parse time, nothing evaluated)',
                    refuse_with('quarantine:', True), 'inherit'))
    return out


def summarize(r):
    keep = ('verdict', 'reason', 'false', 'cell', 'boxes', 'maxdepth', 'sec', 'describe', 'C4', 'claims')
    return {k: r[k] for k in keep if k in r}


def run_battery(args):
    """Run the full mutant battery of one ACCEPTed certificate (worker-safe: procs=1 inside)."""
    raw, fk, order, max_depth = args
    mres = {}
    for name, mc, lab, chk, fkmode in mutants(raw) + malformed(raw, fk):
        t0 = time.time()
        fkm = fk if fkmode == 'inherit' else None
        md = max_depth if not name.startswith('7') else min(max_depth, 6)
        try:
            mr = V.verify_cert(mc, fkm, N=order, max_depth=md, procs=1)
        except Exception as exc:   # a crash is a self-test failure
            mr = {'verdict': 'CRASH', 'reason': repr(exc)}
        ok = mr['verdict'] != 'CRASH' and bool(chk(mr))
        interp = ''
        if mr['verdict'] == 'ACCEPT':
            interp = 'mutated claim PROVED TRUE by the verifier (so it cannot be a false acceptance)'
        elif mr.get('false'):
            interp = 'DISPROVED' if '(C4)' in (mr.get('reason') or '') else 'mutated claim DISPROVED (false)'
        elif mr['verdict'] == 'REJECT':
            interp = 'rejected (not a disproof: exact sha256 rejection, or method limit)'
        mres[name] = {'expect': lab, 'verdict': mr['verdict'], 'false': mr.get('false'),
                      'reason': mr.get('reason'), 'cell': mr.get('cell'), 'boxes': mr.get('boxes'),
                      'file_kernel_used': fkm, 'sec': round(time.time() - t0, 2), 'expectation_met': ok,
                      'interpretation': interp, 'harness_version': HARNESS_VERSION,
                      'harness_sha256': HARNESS_SHA, 'verifier_sha256': VERIFIER_SHA}
    return mres


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-depth', type=int, default=24)
    ap.add_argument('--order', type=int, default=8)
    ap.add_argument('--no-mutants', action='store_true')
    ap.add_argument('--redo', action='store_true', help='discard VERIFY_RESULTS.json and start afresh')
    ap.add_argument('--remutate', action='store_true',
                    help='keep recorded genuine verdicts (same sha256) and re-run only the mutant batteries')
    ap.add_argument('--jobs', type=int, default=1, help='parallel mutant batteries (one process each)')
    ap.add_argument('--files', nargs='*', default=None)
    ap.add_argument('--unit-tests', action='store_true', help='also run tests/test_verify_selftests.py and record it')
    a = ap.parse_args()
    ev = os.path.join(NS, 'evidence')
    files = [os.path.abspath(f) for f in a.files] if a.files else sorted(
        glob.glob(os.path.join(ev, 'srk_decoys', '*.json')) + glob.glob(os.path.join(ev, 'srk_decoys_cell', '*.json'))
        + glob.glob(os.path.join(ev, 'srk_decoys_prelim', '*.json'))
        + glob.glob(os.path.join(ev, 'srk_decoys_taboo', '*.json')))
    res = {}
    if os.path.exists(OUT) and not a.redo:
        with open(OUT) as f:
            res = json.load(f)
    res.setdefault('verifier', 'verify/srk_verify_indep.py (independent; stdlib only)')
    res.setdefault('files', {})
    res['settings'] = {'taylor_order': a.order, 'max_depth': a.max_depth, 'initial_cell_width': '1/4',
                       'procs_per_verification': 1}
    res['harness'] = {'current_version': HARNESS_VERSION, 'current_harness_sha256': HARNESS_SHA,
                      'verifier_sha256': VERIFIER_SHA, 'legacy_v1_harness_sha256': LEGACY_V1_SHA,
                      'note': 'mutant entries carry harness_sha256; entries without it were produced by harness v1 '
                              'and are annotated with legacy_v1_harness_sha256 (expectations were verdict-only)'}
    # annotate legacy mutant results (produced by harness v1 before this rewrite)
    for fres in res['files'].values():
        for e in fres.values():
            if isinstance(e, dict):
                for mv in e.get('mutants', {}).values():
                    if 'harness_sha256' not in mv:
                        mv['harness_version'] = 'v1'
                        mv['harness_sha256'] = LEGACY_V1_SHA

    def flush():
        tmp = OUT + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(res, f, indent=1, sort_keys=True, default=str)
        os.replace(tmp, OUT)

    pending = []          # (rel, label, raw, fk) whose mutant battery must run
    for path in files:
        rel = os.path.relpath(path, NS)
        try:
            items = V.load_certs(path)
        except Exception as exc:                       # malformed file: refuse, record
            res['files'][rel] = {'file_error': 'REFUSE: %r' % (exc,)}
            flush()
            continue
        fres = res['files'].setdefault(rel, {})
        for label, raw, fk in items:
            sha = raw.get('sha256') if isinstance(raw, dict) else None
            prev = fres.get(label)
            same = prev and prev.get('sha256') == sha
            if same and not a.remutate and ('mutants' in prev or a.no_mutants):
                print('[skip] %s #%s (already verified)' % (rel, label), flush=True)
                continue
            if same and a.remutate and prev.get('verdict'):
                print('[reuse genuine verdict] %s #%s -> %s' % (rel, label, prev['verdict']), flush=True)
            else:
                print('[verify] %s #%s' % (rel, label), flush=True)
                r = V.verify_cert(raw, fk, N=a.order, max_depth=a.max_depth, procs=1)
                prev = summarize(r)
                prev['sha256'] = sha
                fres[label] = prev
                print('   -> %s (%s) boxes=%s depth=%s %.1fs' % (r['verdict'], r.get('reason'), r.get('boxes'),
                                                               r.get('maxdepth'), r['sec']), flush=True)
                flush()
            if not a.no_mutants and prev.get('verdict') == 'ACCEPT':
                pending.append((rel, label, raw, fk))

    def store(rel, label, mres):
        e = res['files'][rel][label]
        e['mutants'] = mres
        e['mutants_harness_sha256'] = HARNESS_SHA
        flush()
        bad = [n for n, m in mres.items() if not m['expectation_met']]
        print('   battery %s #%s: %d mutants, %d expectation(s) not met %s'
              % (rel, label, len(mres), len(bad), bad if bad else ''), flush=True)

    args = [(raw, fk, a.order, a.max_depth) for (_, _, raw, fk) in pending]
    if a.jobs > 1 and len(args) > 1:
        with mp.get_context('fork').Pool(a.jobs) as pool:
            for (rel, label, _, _), mres in zip(pending, pool.imap(run_battery, args)):
                store(rel, label, mres)
    else:
        for (rel, label, _, _), ar in zip(pending, args):
            store(rel, label, run_battery(ar))

    if a.unit_tests:
        import unittest
        sys.path.insert(0, os.path.join(NS, 'tests'))
        import test_verify_selftests as T
        t0 = time.time()
        suite = unittest.defaultTestLoader.loadTestsFromModule(T)
        outcome = {}

        class Rec(unittest.TextTestResult):
            def addSuccess(self, test):
                super().addSuccess(test)
                outcome[test.id()] = 'ok'

            def addFailure(self, test, err):
                super().addFailure(test, err)
                outcome[test.id()] = 'FAIL: %s' % (err[1],)

            def addError(self, test, err):
                super().addError(test, err)
                outcome[test.id()] = 'ERROR: %r' % (err[1],)

            def addSkip(self, test, reason):
                super().addSkip(test, reason)
                outcome[test.id()] = 'skipped: %s' % reason
        rr = unittest.TextTestRunner(resultclass=Rec, verbosity=1).run(suite)
        res['unit_selftests'] = {'file': 'tests/test_verify_selftests.py', 'ran': rr.testsRun,
                                 'ok': rr.wasSuccessful(), 'sec': round(time.time() - t0, 1), 'tests': outcome}
        flush()
    # summary, split by harness version
    summ = {'certificates': 0, 'ACCEPT': 0, 'REJECT': 0, 'REFUSE': 0, 'by_harness': {}}
    for rel, fres in res['files'].items():
        for label, e in fres.items():
            if not isinstance(e, dict) or 'verdict' not in e:
                continue
            summ['certificates'] += 1
            summ[e['verdict']] = summ.get(e['verdict'], 0) + 1
            for name, m in e.get('mutants', {}).items():
                hv = m.get('harness_version', 'v1')
                s = summ['by_harness'].setdefault(hv, {'mutants_run': 0, 'mutant_expectations_met': 0,
                                                       'expectation_not_met': [], 'mutant_accepts_proved_true': 0,
                                                       'claim_rejects_not_disproved': []})
                s['mutants_run'] += 1
                s['mutant_expectations_met'] += bool(m['expectation_met'])
                if not m['expectation_met']:
                    s['expectation_not_met'].append('%s#%s:%s' % (rel, label, name))
                if m['verdict'] == 'ACCEPT':
                    s['mutant_accepts_proved_true'] += 1
                if m['verdict'] == 'REJECT' and 'UNPROVEN' in (m.get('reason') or ''):
                    s['claim_rejects_not_disproved'].append('%s#%s:%s' % (rel, label, name))
    res['summary'] = summ
    flush()
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
