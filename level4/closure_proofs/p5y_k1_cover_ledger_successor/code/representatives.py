"""Small pre-freeze diagnostics. Six midpoint collocation probes, NO certification."""
import json,sys,time
from fractions import Fraction as F
from geometry import NS,ROOT,canonical


def main():
    if (NS/'manifests/freeze.json').exists():raise SystemExit('frozen; refuse mutation')
    sys.path.insert(0,str(ROOT/'level4/closure_proofs/p5y_k1_cusum_kernel/code'))
    import cusum_raw as CR
    cells=json.loads((NS/'config/cells.json').read_text())
    cus=[c for c in cells if c['detector']=='CUSUM']
    rows=[]
    start=time.process_time()
    for target in (F(0),F(1,10),F(1,4),F(1),F(27,5),F(11,2)):
        c=next(c for c in cus if F(c['left'][0])<=target<F(c['right'][0]) or
               (target==F(11,2) and F(c['right'][0])==target))
        e0=F(c['e0'][0]);rho=F(c['rho'][0])
        co=CR.collocation(float(e0));obj=CR.build_objects(co)
        for m in (1,2,3,5):
            R,D=CR.assemble(obj,co,m)
            rows.append(dict(target_point=str(target),detector='CUSUM',cell_index=c['index'],m=m,
                left=c['left'],right=c['right'],e0=c['e0'],rho=c['rho'],
                R_point_estimate=R,D_point_estimate=D,
                nominal_first_order_estimate=float(rho)*abs(D),
                R_interval_width=None,D_interval_width=None,
                derivative_uncertainty_contribution=None,curvature_contribution=None,
                B_cover_total_utilization=None,top_level_utilization=None,
                status='NOT_COMPUTED',failure_class='IMPLEMENTATION_DEPENDENCY',
                missing=['certified_midpoint_value_intervals','complete_derivative_dependency_certificates',
                         'whole_cell_M_R2','certified_all_m_assembly'],
                floating_point_diagnostics_are_not_certificates=True))
    data=dict(schema='k1.representative.v1',production_run=False,scientific_certification_run=False,
              scope='six cells containing the requested anchors; actual expansion at their midpoints',
              diagnostic_only=True,rows=rows,cpu_seconds=time.process_time()-start)
    (NS/'diagnostics/representatives.json').write_bytes(canonical(data))
    lines=['# Pre-freeze representative diagnostics','',
           'Six actual CUSUM cells; anchors select cells, not expansion points. Four m per cell.',
           'Float collocation only. No new certificate is asserted. Prior certificates at anchor',
           'points do not certify different midpoint candidates. Missing entries are not zeros.','',
           '| anchor | cell | [left,right] | midpoint | rho | m | R estimate | D estimate | nominal estimate | widths / uncertainty / curvature / total / other gates | status |',
           '|---|---:|---|---|---|---:|---:|---:|---:|---|---|']
    for r in rows:
        lines.append(f"| {r['target_point']} | {r['cell_index']} | [{r['left'][0]}, {r['right'][0]}] | {r['e0'][0]} | {r['rho'][0]} | {r['m']} | {r['R_point_estimate']:.10g} | {r['D_point_estimate']:.10g} | {r['nominal_first_order_estimate']:.9g} | NOT_COMPUTED | IMPLEMENTATION_DEPENDENCY |")
    lines+=['','R and D interval widths, derivative uncertainty, curvature, total B_cover',
            'utilization and every certified top-level gate are NOT_COMPUTED for every row.',
            'The nominal estimates above cannot be used to accept or reject the scientific target.',
            f'Diagnostic CPU seconds: {data["cpu_seconds"]:.6f}. No full-cover function solves.']
    (NS/'diagnostics/REPRESENTATIVES.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'rows':len(rows),'status':'NOT_COMPUTED / IMPLEMENTATION_DEPENDENCY',
                      'diagnostic_cpu_seconds':data['cpu_seconds']}))

if __name__=='__main__':main()
