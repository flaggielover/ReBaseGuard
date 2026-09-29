#!/usr/bin/env python3
"""Render verify/VERIFY_RESULTS.json as markdown tables (used for README_VERIFY.md)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(path=os.path.join(HERE, 'VERIFY_RESULTS.json')):
    with open(path) as f:
        res = json.load(f)
    print('| file | idx | i | verdict | cells | max depth | sec | min certified LB (C2) | min certified LB (C3) |')
    print('|---|---|---|---|---|---|---|---|---|')
    mut_rows = []
    for rel in sorted(res['files']):
        fres = res['files'][rel]
        for label in sorted(fres, key=lambda s: (len(s), s)):
            e = fres[label]
            if not isinstance(e, dict) or 'verdict' not in e:
                continue
            cl = e.get('claims', {})
            i = ''
            if e.get('describe'):
                i = e['describe'].split(' i=')[1].split(' ')[0]

            def lb(k):
                v = cl.get(k, {}).get('minlb')
                return '%.2e' % v if v is not None else '-'
            print('| %s | %s | %s | %s | %s | %s | %.1f | %s | %s |'
                  % (os.path.basename(rel), label, i, e['verdict'], e.get('boxes', '-'), e.get('maxdepth', '-'),
                     e.get('sec', 0), lb('C2'), lb('C3')))
            for name, m in sorted(e.get('mutants', {}).items()):
                mut_rows.append((os.path.basename(rel), label, name, m))
    print()
    # mutant summary: per mutant name, counts of verdict kinds
    agg = {}
    for (f, l, name, m) in mut_rows:
        key = name
        d = agg.setdefault(key, {'n': 0, 'met': 0, 'ACCEPT(proved true)': 0, 'REJECT(disproved)': 0,
                                 'REJECT(C4/sha)': 0, 'REJECT(unproven)': 0, 'REFUSE': 0, 'other': 0})
        d['n'] += 1
        d['met'] += bool(m.get('expectation_met'))
        v, reason = m['verdict'], (m.get('reason') or '')
        if v == 'ACCEPT':
            d['ACCEPT(proved true)'] += 1
        elif v == 'REFUSE':
            d['REFUSE'] += 1
        elif v == 'REJECT' and m.get('false') and '(C4)' not in reason:
            d['REJECT(disproved)'] += 1
        elif v == 'REJECT' and ('(C4)' in reason or 'sha256' in reason):
            d['REJECT(C4/sha)'] += 1
        elif v == 'REJECT':
            d['REJECT(unproven)'] += 1
        else:
            d['other'] += 1
    cols = ['ACCEPT(proved true)', 'REJECT(disproved)', 'REJECT(C4/sha)', 'REJECT(unproven)', 'REFUSE', 'other']
    print('| mutant | runs | expectation met | ' + ' | '.join(cols) + ' |')
    print('|---|---|---|' + '---|' * len(cols))
    for name in sorted(agg):
        d = agg[name]
        print('| %s | %d | %d | %s |' % (name, d['n'], d['met'], ' | '.join(str(d[c]) for c in cols)))
    unmet = [(f, l, n, m) for (f, l, n, m) in mut_rows if not m.get('expectation_met')]
    if unmet:
        print()
        print('Expectation not met:')
        for f, l, n, m in unmet:
            print('* %s #%s %s: %s (%s)' % (f, l, n, m['verdict'], m.get('reason')))
    unproven = [(f, l, n, m) for (f, l, n, m) in mut_rows
                if m['verdict'] == 'REJECT' and not m.get('false') and 'sha256' not in (m.get('reason') or '')
                and '(C4)' not in (m.get('reason') or '')]
    if unproven:
        print()
        print('Rejected without disproof (method limit or false):')
        for f, l, n, m in unproven:
            print('* %s #%s %s: %s; cell %s' % (f, l, n, m.get('reason'), m.get('cell')))


if __name__ == '__main__':
    main(*sys.argv[1:])
