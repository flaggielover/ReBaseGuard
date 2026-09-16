"""POST-RESULT DIAGNOSTIC, NOT PART OF QUALIFICATION r1 AND NOT A GATE.

Written after r1 reported R05_RESIDUAL_R0_USES_CANDIDATE_SOURCE undetected. It isolates the r = 0 closed-form source
edge: on a controlled_K3 scalar system, the candidate S_0''' is offset by eta = 1/1000 and G_0 is re-solved exactly
from that candidate, so the only error path is the closed-form source charge. Run from ../../code on
rebaseguard-vultr-02 (venv /root/work/rbg-cusum-aux5-venv) at commit e69a0224. Output: r05_isolation_output.json.
"""
import importlib.util
import json
import os
import sys
import tempfile
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, os.getcwd())                     # run from the namespace code/ directory

import fixtures
import manufactured_chain as MC
import rung3_engine as E
import rung3_residual as RR
import soundness as SD

proto = json.load(open('../config/QUALIFICATION_PROTOCOL.json'))
mut = next(m for m in proto['mutations'] if m['id'] == 'R05_RESIDUAL_R0_USES_CANDIDATE_SOURCE')
src = Path('rung3_residual.py').read_text()
tmp = Path(tempfile.mkdtemp()) / 'm.py'
tmp.write_text(src.replace(mut['old'], mut['new']))
sp = importlib.util.spec_from_file_location('mut_r05', tmp)
M = importlib.util.module_from_spec(sp)
sp.loader.exec_module(M)
spec = {'kind': 'controlled_K3', 'e0': '7/20', 'rho': '1/100', 'noise': '0'}
sysm, e0, rho, seed, noise = fixtures.build(spec)
eta = Fr(1, 1000)


def run(resid):
    rig = MC.Rigorous(sysm, e0, rho, seed=0, noise=Fr(0))
    ex = rig.ex
    rig.P['S', 0, 3] = [x + eta for x in rig.P['S', 0, 3]]
    rig.P['W', (0, 0), 3] = rig.P['S', 0, 3]
    rig.sup['S', 0, 3] = MC.vnorm(rig.P['S', 0, 3])
    rig.sup['W', (0, 0), 3] = rig.sup['S', 0, 3]
    rig.mid['S:0:3'] = eta
    rig.mid['W:0:0:3'] = eta
    Kd = [MC.mscale(MC.factorial(i), ex['K'][i]) if i < len(ex['K']) else MC.zeros_m(1) for i in range(4)]
    I_K0 = [[1 - Kd[0][0][0]]]
    rhs = MC.vadd(MC.vadd(MC.matvec(Kd[3], rig.P['F', 0, 0]), MC.vscale(3, MC.matvec(Kd[2], rig.P['D', 0, 0]))),
                  MC.vadd(MC.vscale(3, MC.matvec(Kd[1], rig.P['H', 0, 0])), rig.P['S', 0, 3]))
    rig.P['G', 0, 0] = MC.solve(I_K0, rhs)
    rig.sup['G', 0, 0] = MC.vnorm(rig.P['G', 0, 0])
    with E.precision(256):
        cert = MC.ManufacturedCert(rig)
        g = {r: resid.g_residual(cert, r) for r in range(5)}
        res = E.certify_order3(MC.engine_inputs(cert, g))
    return len(SD.violations(sysm, rig, res))


print(json.dumps({'diagnostic': 'post-result, not part of r1', 'unmutated_violations': run(RR),
                  'R05_mutant_violations': run(M)}))
