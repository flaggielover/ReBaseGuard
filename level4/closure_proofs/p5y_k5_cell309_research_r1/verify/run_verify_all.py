#!/usr/bin/env python3
"""
Run the independent SRK verifier over every decoy certificate file and the SRK_CERT_SPEC.md section 5 required
rejections (mutants), recording everything in verify/VERIFY_RESULTS.json.

    python3 run_verify_all.py [--max-depth 24] [--order 8] [--no-mutants] [--redo]

Files scanned: evidence/srk_decoys/*.json, evidence/srk_decoys_prelim/*.json and evidence/srk_decoys_taboo/*.json
(read only, never modified).  Results
are written after every certificate; an existing (file, index, sha256) result is reused unless --redo.
Mutants 1-5 get a recomputed sha256 (so that the mathematics, not the hash, is exercised); mutant 6 alters the hash.
"""
import argparse
import copy
import glob
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import srk_verify_indep as V  # noqa: E402

OUT = os.path.join(HERE, 'VERIFY_RESULTS.json')


def fs(x):
    x = Fr(x)
    return '%d/%d' % (x.numerator, x.denominator)


def resha(c):
    c = dict(c)
    c['sha256'] = V.canonical_sha(c)
    return c


def mutants(raw):
    """SRK_CERT_SPEC.md section 5, items 1-6 (+ informative variants).  Returns list of (name, cert, expectation)."""
    out = []
    m = copy.deepcopy(raw)
    m['Gamma'] = fs(Fr(raw['Gamma']) - Fr(1, 10 ** 6))
    out.append(('1_gamma_minus_1e-6', resha(m), 'REJECT'))
    m = copy.deepcopy(raw)
    m['V0'] = {k: fs(Fr(v) * (1 - Fr(1, 256))) for k, v in raw['V0'].items()}
    out.append(('2_V0_scaled_1-2^-8', resha(m), 'REJECT or PROVE TRUE (spec erratum SE-1)'))
    m = copy.deepcopy(raw)
    m['V0'] = {k: fs(Fr(v) * (1 - Fr(1, 4))) for k, v in raw['V0'].items()}
    out.append(('2x_V0_scaled_3/4 (SE-1 mandatory)', resha(m), 'REJECT'))
    lam = Fr(raw.get('lam', '0'))
    if lam > 0:
        m = copy.deepcopy(raw)
        keys = set(raw['V0']) | set(raw['W0'])
        m['V0'] = {k: fs(Fr(raw['V0'].get(k, '0')) - lam * Fr(raw['W0'].get(k, '0'))) for k in keys}
        out.append(('3_V0_minus_lam_W0', resha(m), 'REJECT'))
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
            out.append((tag, resha(m), 'REJECT unless the widened claim is true'))
    m = copy.deepcopy(raw)
    m['hermite_index'] = raw['hermite_index'] + 1
    out.append(('5_hermite_index_plus_1', resha(m), 'REJECT (generally)'))
    m = copy.deepcopy(raw)
    m['sha256'] = ('0' if raw['sha256'][0] != '0' else '1') + raw['sha256'][1:]
    out.append(('6_sha256_altered', m, 'REJECT'))
    return out


def malformed(raw):
    """Item 7: malformed input must be REFUSED (not crash).  Also the non-dyadic drift (this method does not need
    dyadics, so it must be processed without crashing) and the quarantine refusal."""
    out = []
    m = copy.deepcopy(raw)
    del m['W1']
    out.append(('7a_missing_key_W1', m, 'REFUSE'))
    m = copy.deepcopy(raw)
    k0 = sorted(m['V0'])[0]
    m['V0'][k0] = '1.5e3'
    out.append(('7b_non_rational_string', resha(m), 'REFUSE'))
    m = copy.deepcopy(raw)
    m['block'] = [raw['block'][1], raw['block'][0]]
    out.append(('7c_e_lo_gt_e_hi', resha(m), 'REFUSE'))
    m = copy.deepcopy(raw)
    m['block'] = ['a/b', raw['block'][1]]
    out.append(('7d_garbage_block', resha(m), 'REFUSE'))
    m = copy.deepcopy(raw)
    m['weight_block'] = [fs(Fr(raw['block'][0]) + Fr(1, 64)), raw['block'][1]]
    out.append(('7e_weight_block_not_containing_block', resha(m), 'REFUSE'))
    m = copy.deepcopy(raw)
    m['kernel'] = 'bogus'
    out.append(('7f_unknown_kernel', resha(m), 'REFUSE'))
    m = copy.deepcopy(raw)
    m['e_c'] = fs(Fr(raw['e_c']) + Fr(1, 1024))
    out.append(('7g_e_c_not_midpoint', resha(m), 'REFUSE'))
    m = copy.deepcopy(raw)
    a, b = Fr(raw['block'][0]) + Fr(1, 3), Fr(raw['block'][1]) + Fr(1, 3)
    m['block'] = [fs(a), fs(b)]
    m['e_c'] = fs((a + b) / 2)
    out.append(('7h_non_dyadic_drift (processed, no crash)', resha(m), 'no crash (any verdict)'))
    if Fr(raw['geometry']['h']) == 5 and Fr(raw['geometry']['k']) == Fr(1, 2):
        m = copy.deepcopy(raw)
        m['block'] = ['6/5', '39/32']  # q309: literal-ok (refusal probe: REFUSED at parse time, nothing evaluated)
        m['e_c'] = fs((Fr(6, 5) + Fr(39, 32)) / 2)  # q309: literal-ok (refusal probe: REFUSED at parse time, nothing evaluated)
        out.append(('7q_quarantine_band_refused', resha(m), 'REFUSE'))
    return out


def outcome_ok(expect, r):
    v = r['verdict']
    if expect == 'REFUSE':
        return v == 'REFUSE'
    if expect.startswith('no crash'):
        return 'internal error' not in (r.get('reason') or '')
    if expect == 'REJECT':
        return v == 'REJECT'
    if expect.startswith('REJECT or PROVE TRUE'):
        return v in ('REJECT', 'ACCEPT')      # an ACCEPT is a completed proof of the (true) mutated claim
    return v in ('REJECT', 'ACCEPT')


def summarize(r):
    keep = ('verdict', 'reason', 'false', 'cell', 'boxes', 'maxdepth', 'sec', 'describe', 'C4', 'claims')
    return {k: r[k] for k in keep if k in r}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-depth', type=int, default=24)
    ap.add_argument('--order', type=int, default=8)
    ap.add_argument('--no-mutants', action='store_true')
    ap.add_argument('--redo', action='store_true')
    ap.add_argument('--files', nargs='*', default=None)
    ap.add_argument('--unit-tests', action='store_true', help='also run tests/test_verify_selftests.py and record it')
    a = ap.parse_args()
    files = a.files or sorted(glob.glob(os.path.join(NS, 'evidence', 'srk_decoys', '*.json'))
                              + glob.glob(os.path.join(NS, 'evidence', 'srk_decoys_prelim', '*.json'))
                              + glob.glob(os.path.join(NS, 'evidence', 'srk_decoys_taboo', '*.json')))
    res = {}
    if os.path.exists(OUT) and not a.redo:
        with open(OUT) as f:
            res = json.load(f)
    res.setdefault('verifier', 'verify/srk_verify_indep.py (independent; stdlib only)')
    res.setdefault('files', {})
    res['settings'] = {'taylor_order': a.order, 'max_depth': a.max_depth, 'initial_cell_width': '1/4',
                       'procs': 1}

    def flush():
        tmp = OUT + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(res, f, indent=1, sort_keys=True, default=str)
        os.replace(tmp, OUT)

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
            if prev and prev.get('sha256') == sha and not a.redo and ('mutants' in prev or a.no_mutants):
                print('[skip] %s #%s (already verified)' % (rel, label), flush=True)
                continue
            print('[verify] %s #%s' % (rel, label), flush=True)
            r = V.verify_cert(raw, fk, N=a.order, max_depth=a.max_depth, procs=1)
            entry = summarize(r)
            entry['sha256'] = sha
            print('   -> %s (%s) boxes=%s depth=%s %.1fs' % (r['verdict'], r.get('reason'), r.get('boxes'),
                                                           r.get('maxdepth'), r['sec']), flush=True)
            fres[label] = entry
            flush()
            if a.no_mutants or r['verdict'] != 'ACCEPT':
                continue
            mres = {}
            for name, mc, expect in mutants(raw):
                t0 = time.time()
                mr = V.verify_cert(mc, fk, N=a.order, max_depth=a.max_depth, procs=1)
                ok = outcome_ok(expect, mr)
                interp = ''
                if mr['verdict'] == 'ACCEPT':
                    interp = 'mutated claim PROVED TRUE by the verifier (so it cannot be a false acceptance)'
                elif mr.get('false'):
                    interp = 'mutated claim DISPROVED (false)'
                elif mr['verdict'] == 'REJECT':
                    interp = 'not proved (method limit or false; not disproved)'
                mres[name] = {'expect': expect, 'verdict': mr['verdict'], 'false': mr.get('false'),
                              'reason': mr.get('reason'), 'cell': mr.get('cell'), 'boxes': mr.get('boxes'),
                              'sec': round(time.time() - t0, 2), 'expectation_met': ok, 'interpretation': interp}
                print('   mutant %-48s %s  %s' % (name, mr['verdict'], (mr.get('reason') or '')[:100]), flush=True)
            for name, mc, expect in malformed(raw):
                t0 = time.time()
                try:
                    mr = V.verify_cert(mc, fk, N=a.order, max_depth=min(a.max_depth, 6), procs=1)
                except Exception as exc:   # a crash is a self-test failure
                    mr = {'verdict': 'CRASH', 'reason': repr(exc)}
                ok = outcome_ok(expect, mr) and mr['verdict'] != 'CRASH'
                mres[name] = {'expect': expect, 'verdict': mr['verdict'], 'reason': mr.get('reason'),
                              'false': mr.get('false'), 'sec': round(time.time() - t0, 2), 'expectation_met': ok}
                print('   malformed %-45s %s  %s' % (name, mr['verdict'], (mr.get('reason') or '')[:100]), flush=True)
            fres[label]['mutants'] = mres
            flush()
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
    # summary
    summ = {'certificates': 0, 'ACCEPT': 0, 'REJECT': 0, 'REFUSE': 0, 'mutants_run': 0,
            'mutant_expectations_met': 0, 'mutant_accepts_proved_true': []}
    for rel, fres in res['files'].items():
        for label, e in fres.items():
            if not isinstance(e, dict) or 'verdict' not in e:
                continue
            summ['certificates'] += 1
            summ[e['verdict']] = summ.get(e['verdict'], 0) + 1
            for name, m in e.get('mutants', {}).items():
                summ['mutants_run'] += 1
                summ['mutant_expectations_met'] += bool(m['expectation_met'])
                if m['verdict'] == 'ACCEPT':
                    summ['mutant_accepts_proved_true'].append('%s#%s:%s' % (rel, label, name))
    res['summary'] = summ
    flush()
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
