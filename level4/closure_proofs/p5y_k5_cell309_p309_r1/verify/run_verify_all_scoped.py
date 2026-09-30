#!/usr/bin/env python3
"""
I1 harness for the band-scoped verifier variant (FC2(b); FNS/fc2/FC2_SPEC_R2.md sections 4 and 8), written by the
verifier's author.  It is harness v2 of RNS/verify/run_verify_all.py (sha256
3455c1414464290a306384770a056c2e4a7e3c2210965eac49500809f9a7ce05) run against verify/srk_verify_indep_scoped.py,
writing verify/VERIFY_RESULTS_SCOPED.json.  Inputs (read only): every certificate in RNS/evidence/srk_decoys/ and
RNS/evidence/srk_decoys_cell/, and the committed RNS/verify/VERIFY_RESULTS.json (reference results).

    python3 verify/run_verify_all_scoped.py [--jobs 3] [--unit-tests]

Probe construction (protocol section 7(c); spec section 4) uses this file's OWN compiled copy of spec section 1
(_OWN_REAL_BAND for every geometry, _OWN_TEST_BAND for (3, 1/2)); at start the harness only checks that the variant's
tables are identical and aborts otherwise (fail closed).  Mutant construction is copied verbatim from harness v2, plus
one probe, 7r (block and weight block moved into the REAL band for a non-(5, 1/2) geometry: a geometry-blind parse-time
refusal probe).

Two passes:
* pass "production": every certificate with the default production context (this repository has no grant);
* pass "test_context": the 16 committed h3 decoy-cell certificates with the P1 sandbox TestContext (spec section 6).

EXPECTATION RULE (written before the run; derived from spec sections 3-4: parse first, then admission, then the
original expectation).  For each genuine certificate and each mutant:
  R0  if the object does not parse as a certificate, the result must equal the committed result (the same
      "malformed:" REFUSE);
  R1  otherwise, if it meets no band of the harness's own table, the result must be identical in verdict and reason
      to the committed result;
  R2  otherwise its admission is predicted independently of the variant: ADMIT iff the pass is "test_context", the
      geometry is (3, 1/2), the only band met is TEST, the block lies in Ew = [341/1024, 201/512] and the weight block
      equals Ew; in the production pass, never (no grant exists).  Predicted ADMIT: the result must be identical to
      the committed result.  Predicted REFUSE: the result must be REFUSE with a reason starting "quarantine:", and
      nothing may be evaluated (tripwire on the variant's prepare).
  A probe with no committed counterpart (7r) is judged by R2 alone.  Wherever the committed result is the expectation,
  the harness-v2 reason-specific expectation of that probe must also hold.
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

HERE = os.path.dirname(os.path.realpath(__file__))
FNS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FNS, 'code'))
import p309_env as E  # noqa: E402
RNS = str(E.RNS)
sys.path.insert(0, HERE)
import srk_verify_indep_scoped as V  # noqa: E402
import scoped_sandbox as SB  # noqa: E402

OUT = os.path.join(HERE, 'VERIFY_RESULTS_SCOPED.json')
COMMITTED = os.path.join(RNS, 'verify', 'VERIFY_RESULTS.json')

# this harness's OWN compiled copy of spec section 1
_OWN_REAL_BAND = ((Fr(6, 5), Fr(13, 5)), (Fr(-13, 5), Fr(-6, 5)))  # q309: literal-ok (own compiled REAL band for the probe guard; refusal constant)
_OWN_TEST_BAND = ((Fr(341, 1024), Fr(201, 512)), (Fr(-201, 512), Fr(-341, 1024)))
_OWN_TEST_EW = (Fr(341, 1024), Fr(201, 512))
_EVALUATED_DRIFT_HULL = [('-1/2', '37/32'), ('341/1024', '201/512')]   # every evaluated drift lies in these


def _sha_file(p):
    with open(p, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


HARNESS_SHA = _sha_file(os.path.realpath(__file__))
VARIANT_SHA = _sha_file(V._OWN_PATH)
HARNESS_VERSION = 'scoped-v1 (harness v2 logic)'


def own_bands(geometry, intervals):
    h, k = Fr(geometry['h']), Fr(geometry['k'])
    out = []
    if any(Fr(lo) <= b and a <= Fr(hi) for (lo, hi) in intervals for (a, b) in _OWN_REAL_BAND):
        out.append('REAL')
    if (h, k) == (Fr(3), Fr(1, 2)) and any(Fr(lo) <= b and a <= Fr(hi) for (lo, hi) in intervals
                                             for (a, b) in _OWN_TEST_BAND):
        out.append('TEST')
    return out


# ---- verbatim from harness v2 (RNS/verify/run_verify_all.py lines 56-233), _meets_band replaced ----
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
    """True if block or weight block meets a band of this harness's OWN compiled table (probe guard, section 7(c))."""
    ivs = [cert_like['block']] + ([cert_like['weight_block']] if 'weight_block' in cert_like else [])
    return bool(own_bands(cert_like['geometry'], ivs))


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




# ---- scoped harness (new) --------------------------------------------------------------------------------------------
def extra_probes(raw):
    """7r: geometry-blind REAL-band probe for a non-(5, 1/2) geometry (block and weight block moved into the band;
    parse-time refusal; nothing evaluated)."""
    g = raw['geometry']
    if Fr(g['h']) == 5 and Fr(g['k']) == Fr(1, 2):
        return []
    m = copy.deepcopy(raw)
    m['block'] = ['5/4', '41/32']  # q309: literal-ok (parse-time REAL-band refusal probe; nothing evaluated)
    m['e_c'] = fs((Fr(5, 4) + Fr(41, 32)) / 2)  # q309: literal-ok (parse-time REAL-band refusal probe; nothing evaluated)
    if 'weight_block' in raw:
        m['weight_block'] = list(m['block'])
    return [('7r_real_band_geometry_blind', resha(m), 'REFUSE, reason quarantine (parse time, nothing evaluated)',
             refuse_with('quarantine:', True), 'inherit')]


def predicted_admit(obj, pass_name):
    """R2 admission prediction, independent of the variant (spec section 3, P1 fixture valid in every other respect)."""
    if pass_name != 'test_context':
        return False
    g = obj['geometry']
    if (Fr(g['h']), Fr(g['k'])) != (Fr(3), Fr(1, 2)):
        return False
    blk = (Fr(obj['block'][0]), Fr(obj['block'][1]))
    wb = obj.get('weight_block', obj['block'])
    wbk = (Fr(wb[0]), Fr(wb[1]))
    if own_bands(g, [blk, wbk]) != ['TEST']:
        return False
    return _OWN_TEST_EW[0] <= blk[0] and blk[1] <= _OWN_TEST_EW[1] and wbk == _OWN_TEST_EW


def classify(obj, fk, pass_name):
    """Which rule applies: ('R0'|'R1'|'R2-admit'|'R2-refuse')."""
    try:
        V.Cert(obj, fk if fk is not None else None)
    except V.CertError:
        return 'R0'
    except Exception:
        return 'R0'
    ivs = [obj['block']] + ([obj['weight_block']] if 'weight_block' in obj else [])
    if not own_bands(obj['geometry'], ivs):
        return 'R1'
    return 'R2-admit' if predicted_admit(obj, pass_name) else 'R2-refuse'


def judge(rule, r, committed, v2check=None):
    """True iff result r satisfies the expectation rule."""
    if rule in ('R0', 'R1', 'R2-admit'):
        if committed is None:
            return False
        ok = (r['verdict'], r.get('reason')) == (committed['verdict'], committed.get('reason'))
        if ok and v2check is not None:
            ok = bool(v2check(r))
        return ok
    return r['verdict'] == 'REFUSE' and (r.get('reason') or '').startswith('quarantine:')


_PASS = [None]
_ORIG_PREPARE = V.prepare


def _tripwire_prepare(cert):
    # classified with this harness's OWN band table (protocol section 7(c); review R4 NB3), not with cert.bands
    bands = own_bands({'h': cert.h, 'k': cert.k}, [(cert.e_lo, cert.e_hi), (cert.w_lo, cert.w_hi)])
    if 'REAL' in bands:
        raise AssertionError('TRIPWIRE: REAL-band certificate reached evaluation')
    if 'TEST' in bands and _PASS[0] != 'test_context':
        raise AssertionError('TRIPWIRE: TEST-band certificate reached evaluation outside the test-context pass')
    return _ORIG_PREPARE(cert)


V.prepare = _tripwire_prepare


def _verify(obj, fk, ctx, md):
    try:
        return V.verify_cert(obj, fk, N=8, max_depth=md, procs=1, ctx=ctx)
    except Exception as exc:
        return {'verdict': 'CRASH', 'reason': '%s: %s' % (type(exc).__name__, exc)}


def run_one(task):
    pass_name, rel, label, raw, fk, sandbox_root, committed_entry = task
    _PASS[0] = pass_name
    ctx = V.PRODUCTION if sandbox_root is None else V.TestContext(sandbox_root)
    t0 = time.time()
    rule = classify(raw, fk, pass_name)
    r = _verify(raw, fk, ctx, 24)
    gen = {'rule': rule, 'verdict': r['verdict'], 'reason': r.get('reason'), 'boxes': r.get('boxes'),
           'maxdepth': r.get('maxdepth'), 'committed_verdict': (committed_entry or {}).get('verdict'),
           'committed_reason': (committed_entry or {}).get('reason'),
           'identical_to_committed': committed_entry is not None and (r['verdict'], r.get('reason')) ==
           (committed_entry.get('verdict'), committed_entry.get('reason')),
           'expectation_met': judge(rule, r, committed_entry), 'sec': round(time.time() - t0, 2)}
    muts = {}
    cm = (committed_entry or {}).get('mutants', {})
    for name, mc, lab, chk, fkmode in mutants(raw) + malformed(raw, fk) + extra_probes(raw):
        fkm = fk if fkmode == 'inherit' else None
        md = 24 if not name.startswith('7') else 6
        t1 = time.time()
        if isinstance(mc, dict):
            mrule = classify(mc, fkm, pass_name)
        else:
            mrule = 'R0'
        mr = _verify(mc, fkm, ctx, md)
        c = cm.get(name)
        muts[name] = {'rule': mrule, 'verdict': mr['verdict'], 'reason': mr.get('reason'), 'false': mr.get('false'),
                      'committed_verdict': (c or {}).get('verdict'), 'committed_reason': (c or {}).get('reason'),
                      'identical_to_committed': c is not None and (mr['verdict'], mr.get('reason')) ==
                      (c.get('verdict'), c.get('reason')),
                      'expectation_met': judge(mrule, mr, c, chk), 'sec': round(time.time() - t1, 2)}
    return pass_name, rel, label, gen, muts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--unit-tests', action='store_true')
    ap.add_argument('--skip-i1', action='store_true')
    ap.add_argument('--out', default=OUT, help='results file (default verify/VERIFY_RESULTS_SCOPED.json; erratum E1-5)')
    a = ap.parse_args()
    out_path = a.out
    if tuple(V.REAL_BAND) != _OWN_REAL_BAND or tuple(V.TEST_BAND) != _OWN_TEST_BAND:
        raise SystemExit('ABORT: the variant\'s compiled band tables differ from this harness\'s own copy')
    with open(COMMITTED) as fh:
        committed = json.load(fh)['files']
    files = sorted(glob.glob(os.path.join(RNS, 'evidence', 'srk_decoys', '*.json'))
                   + glob.glob(os.path.join(RNS, 'evidence', 'srk_decoys_cell', '*.json')))
    res = {'variant': 'verify/srk_verify_indep_scoped.py', 'variant_sha256': VARIANT_SHA,
           'harness': 'verify/run_verify_all_scoped.py', 'harness_sha256': HARNESS_SHA,
           'harness_version': HARNESS_VERSION, 'reference': 'RNS/verify/VERIFY_RESULTS.json (committed)',
           'expectation_rule': __doc__[__doc__.index('EXPECTATION RULE'):].strip(),
           'settings': {'taylor_order': 8, 'max_depth': 24, 'item7_max_depth': 6, 'jobs': a.jobs}, 'passes': {}}

    def flush():
        tmp = out_path + '.tmp'
        with open(tmp, 'w') as fh:
            json.dump(res, fh, indent=1, sort_keys=True, default=str)
        os.replace(tmp, out_path)
    if not a.skip_i1:
        E.log('verify/run_verify_all_scoped.py', 'I1 start (rule recorded before the run): scoped variant on every '
              'certificate of RNS/evidence/srk_decoys and srk_decoys_cell (production pass) and on the 16 h3 decoy-cell '
              'certificates with the P1 sandbox test context, genuine + v2 batteries + 7r',
              klass='NONTARGET_DECOY', drifts=_EVALUATED_DRIFT_HULL,
              notes='REAL-band probes are parse-time refusals (never evaluated; tripwire); TEST band evaluated only '
                    'under the test context; variant %s harness %s' % (VARIANT_SHA[:16], HARNESS_SHA[:16]))
        flush()
        tasks = []
        for f in files:
            rel = os.path.relpath(f, RNS)
            for label, raw, fk in V.load_certs(f):
                tasks.append(('production', rel, label, raw, fk, None, committed.get(rel, {}).get(label)))
        sb = SB.Sandbox('i1')
        try:
            own_rel = os.path.relpath(V._OWN_PATH, SB.own_repo())
            SB.build_valid(sb, own_rel, VARIANT_SHA)
            for f in files:
                if not os.path.basename(f).startswith('cell_h3_'):
                    continue
                rel = os.path.relpath(f, RNS)
                for label, raw, fk in V.load_certs(f):
                    tasks.append(('test_context', rel, label, raw, fk, sb.root, committed.get(rel, {}).get(label)))
            t0 = time.time()
            with mp.get_context('fork').Pool(a.jobs) as pool:
                for pass_name, rel, label, gen, muts in pool.imap_unordered(run_one, tasks):
                    res['passes'].setdefault(pass_name, {}).setdefault(rel, {})[label] = dict(gen, mutants=muts)
                    bad = [n for n, m in muts.items() if not m['expectation_met']]
                    print('%-12s %s #%s genuine %s (%s) rule-ok=%s mutants=%d unmet=%s' % (
                        pass_name, rel.split('/')[-1], label, gen['verdict'], gen['rule'], gen['expectation_met'],
                        len(muts), bad), flush=True)
                    flush()
            res['i1_sec'] = round(time.time() - t0, 1)
        finally:
            sb.teardown()
        # summary
        summ = {}
        for pn, pres in res['passes'].items():
            s = {'certificates': 0, 'genuine_expectation_met': 0, 'genuine_identical': 0, 'mutants': 0,
                 'mutant_expectation_met': 0, 'mutant_identical': 0, 'by_rule': {}, 'differences': []}
            for rel, fr in pres.items():
                for label, e in fr.items():
                    s['certificates'] += 1
                    s['genuine_expectation_met'] += e['expectation_met']
                    s['genuine_identical'] += e['identical_to_committed']
                    s['by_rule'][e['rule']] = s['by_rule'].get(e['rule'], 0) + 1
                    if not e['identical_to_committed']:
                        s['differences'].append({'where': '%s#%s:genuine' % (rel, label), 'rule': e['rule'],
                                                 'verdict': e['verdict'], 'reason': e['reason'],
                                                 'committed': [e['committed_verdict'], e['committed_reason']],
                                                 'expectation_met': e['expectation_met']})
                    for n, m in e['mutants'].items():
                        s['mutants'] += 1
                        s['mutant_expectation_met'] += m['expectation_met']
                        s['mutant_identical'] += m['identical_to_committed']
                        s['by_rule'][m['rule']] = s['by_rule'].get(m['rule'], 0) + 1
                        if not m['identical_to_committed']:
                            s['differences'].append({'where': '%s#%s:%s' % (rel, label, n), 'rule': m['rule'],
                                                     'verdict': m['verdict'], 'reason': m['reason'],
                                                     'committed': [m['committed_verdict'], m['committed_reason']],
                                                     'expectation_met': m['expectation_met']})
            summ[pn] = s
        res['summary'] = summ
        flush()
        E.log('verify/run_verify_all_scoped.py', 'I1 end: %s' % json.dumps(
            {pn: {k: v for k, v in s.items() if k not in ('differences', 'by_rule')} for pn, s in summ.items()}),
            klass='NONTARGET_DECOY', drifts=_EVALUATED_DRIFT_HULL, notes='see %s' % out_path)
    if a.unit_tests:
        import unittest
        V.prepare = _ORIG_PREPARE            # restore BEFORE importing the tests: they install their own tripwire
        sys.path.insert(0, os.path.join(FNS, 'tests'))
        import test_verify_scoped as T
        t0 = time.time()
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
        suite = unittest.defaultTestLoader.loadTestsFromModule(T)
        rr = unittest.TextTestRunner(resultclass=Rec, verbosity=1).run(suite)
        res['unit_tests'] = {'file': 'tests/test_verify_scoped.py',
                             'sha256': _sha_file(os.path.join(FNS, 'tests', 'test_verify_scoped.py')),
                             'ran': rr.testsRun, 'ok': rr.wasSuccessful(), 'sec': round(time.time() - t0, 1),
                             'tests': outcome}
        if os.path.exists(out_path) and a.skip_i1:
            with open(out_path) as fh:
                prev = json.load(fh)
            prev['unit_tests'] = res['unit_tests']
            res = prev
        flush()
        print('unit tests: %d run, ok=%s' % (rr.testsRun, rr.wasSuccessful()))


if __name__ == '__main__':
    main()
