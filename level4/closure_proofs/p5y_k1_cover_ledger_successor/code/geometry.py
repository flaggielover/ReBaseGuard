"""Governance-only canonical cover. Never imports a function-solve driver."""
from fractions import Fraction as F
from pathlib import Path
import json

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
Q = 10**7
C_DEN = 2**32
A_DEN = 2**60
A_SR = F(4581762885148045, 8796093022208)


def canonical(data):
    return (json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode('ascii')


def affine(p=F(0), s=F(0)):
    """Exact p + s*c_SR. All rational strings are reduced, including /1."""
    return [f'{p.numerator}/{p.denominator}', f'{s.numerator}/{s.denominator}']


def cell(detector, index, left_q, right_q, c_num, a_num):
    left = F(left_q, Q)
    right = F(right_q, Q) if right_q is not None else F(0)
    coeff = F(0) if right_q is not None else F(1)
    return dict(detector=detector, index=index, left=affine(left),
                right=affine(right, coeff), e0=affine((left+right)/2, coeff/2),
                rho=affine((right-left)/2, coeff/2),
                C_upper=f'{c_num}/{C_DEN}', C_evaluation=affine(left),
                nominal_step_half_width=str(F(1, 4*F(a_num,A_DEN)*F(c_num,C_DEN))))


def replay(witness):
    """Integer-only independent implementations can replay these frozen witnesses."""
    out = []
    for det in ('CUSUM', 'SR'):
        left = 0
        rows = witness['detectors'][det]['bounds']
        terminal_floor = witness['detectors'][det]['terminal_floor_q']
        for i, row in enumerate(rows):
            if row['left_q'] != left:
                raise ValueError('wrong bound location')
            advance = (Q*A_DEN*C_DEN)//(2*witness['a_upper_num']*row['C_upper_num'])
            if advance < 1:
                raise ArithmeticError('grid cannot represent safe positive step')
            nxt = left+advance
            if det == 'CUSUM':
                nxt = min(nxt, terminal_floor)
                last = nxt == terminal_floor
            else:
                last = nxt > terminal_floor
                if last:
                    nxt = None
            out.append(cell(det, i, left, nxt, row['C_upper_num'], witness['a_upper_num']))
            if last:
                if i+1 != len(rows):
                    raise ValueError('unused bound witnesses')
                break
            left = nxt
        else:
            raise ValueError('incomplete cover')
    return out


def generate():
    """Only Bellman geometry: 192-bit inherited minorants, no K1 object solves."""
    import sys
    sys.path[:0] = [str(ROOT/'rebaseguard-proof/src'),
                   str(ROOT/'level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r1'),
                   str(ROOT/'level4/closure_proofs/p5y_gate2b_sr_cover')]
    import flint
    from flint import arb
    from rebaseguard_certify.arb_backend import workprec, rational
    from drift_minorant import drift_monotone_resolvent
    from sr_cover import sr_drift_monotone_resolvent
    if flint.__version__ != '0.9.0':
        raise RuntimeError('frozen python-flint version required')
    with workprec(192):
        aa = arb(2)/(arb(2)*arb.pi()).sqrt()
        a_num = int((aa.upper()*A_DEN).ceil().fmpq())
        end = (arb(A_SR.numerator)/arb(A_SR.denominator)).log()+rational(1,2)
        floor_lo = int((end.lower()*Q).floor().fmpq())
        floor_hi = int((end.upper()*Q).floor().fmpq())
        assert floor_lo == floor_hi
        witness = dict(schema='k1.cover.witness.v1', python_flint=flint.__version__,
                       bits=192, grid_denominator=Q, a_upper_num=a_num,
                       a_upper_den=A_DEN, C_upper_den=C_DEN,
                       sr_terminal='log(4581762885148045/8796093022208)+1/2',
                       sr_terminal_ball=end.str(65), detectors={})
        for det in ('CUSUM','SR'):
            left, rows, previous = 0, [], None
            terminal = 55_000_000 if det == 'CUSUM' else floor_lo
            while True:
                if det == 'CUSUM':
                    rec = drift_monotone_resolvent(e_num=left, e_den=Q)
                    bound = arb(rec['resolvent_bound']['ball'])
                    t = rec['t_star']
                else:
                    bound,t,_,_,mass = sr_drift_monotone_resolvent(rational(left,Q))
                    if not mass:
                        raise ArithmeticError('SR mass balance')
                rounded = int((bound.upper()*C_DEN).ceil().fmpq())
                cnum = rounded if previous is None else min(previous, rounded)
                rows.append(dict(left_q=left, raw_bound_ball=bound.str(65), t_star=t,
                                 rounded_C_num=rounded, C_upper_num=cnum))
                step = Q*A_DEN*C_DEN//(2*a_num*cnum)
                if step < 1:
                    raise ArithmeticError('grid step underflow')
                if (det=='CUSUM' and left+step>=terminal) or (det=='SR' and left+step>terminal):
                    break
                left += step
                previous = cnum
            witness['detectors'][det] = dict(terminal_floor_q=terminal, bounds=rows)
    return witness, replay(witness)


if __name__ == '__main__':
    import argparse, hashlib
    parser=argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true')
    args=parser.parse_args()
    if not args.generate:
        raise SystemExit('Explicit --generate required; geometry only.')
    if (NS/'manifests/freeze.json').exists():
        raise SystemExit('Already frozen; generator refuses mutation.')
    w,c=generate()
    (NS/'config/cover_witnesses.json').write_bytes(canonical(w))
    (NS/'config/cells.json').write_bytes(canonical(c))
    print(json.dumps({'counts':{d:sum(x['detector']==d for x in c) for d in ('CUSUM','SR')},
                      'table_sha256':hashlib.sha256(canonical(c)).hexdigest()}))
