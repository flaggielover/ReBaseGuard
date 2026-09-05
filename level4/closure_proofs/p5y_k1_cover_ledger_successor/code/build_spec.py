"""Build a reviewable governance candidate. Refuses a sealed namespace."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,subprocess
from geometry import NS,ROOT,canonical
from algebra import TOP_BUDGETS,CLAIMANTS,terms,work_ids


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if (NS/'manifests/freeze.json').exists():raise SystemExit('sealed; no edits')
    base=ROOT/'level4/closure_proofs'
    old=base/'p5y_k1_successor_optimized'
    ck=json.loads((old/'config/checkpoint_s.json').read_text())
    cells=json.loads((NS/'config/cells.json').read_text())
    counts={d:sum(c['detector']==d for c in cells) for d in ('CUSUM','SR')}
    oldcounts={d:ck['cover'][d]['subcell_count'] for d in counts}
    perf=json.loads((old/'config/cost_model.json').read_text())
    panels=ck['cover']['SR']['total_panels_over_live_patches']
    t_panel=perf['t_shared_s']/(counts['SR']*19)+perf['t_drift_s']/19+perf['t_perfn_s']
    sr=t_panel*counts['SR']*19*panels/3600
    cus=126*counts['CUSUM']/oldcounts['CUSUM']
    cand=perf['candidate_build_cpu_h']*counts['SR']/oldcounts['SR']
    def band(mult):return 1.15*1.05*(sr*mult+cus+cand)
    cost={'parent_cost_sha256':sha(old/'config/cost_model.json'),
          'counts':counts,'parent_counts':oldcounts,'base_object_units':19*sum(counts.values()),
          'governed_work_units':len(work_ids(cells)),
          'base_only_central_cpu_h':band(1), 'base_only_conservative_cpu_h':band(perf['load_factor']),
          'base_only_worst_plausible_cpu_h':band(perf['load_factor']*1.25),
          'new_amortized_t_panel_s':t_panel,'shared_cache_cpu_not_scaled_away':True,'base_raw_sr_cpu_h':sr,'base_raw_cusum_cpu_h':cus,'base_candidate_cpu_h':cand,
          'additional_dependency_curvature_certified_assembly_cpu_h':None,
          'full_campaign_projection_cpu_h':None,'hard_cap_cpu_h':1126,
          'cap_adequacy':'NOT_ESTABLISHED',
          'base_worst_headroom_cpu_h':1126-band(perf['load_factor']*1.25),
          'formula':'t_panel=t_shared/(19*N_SR)+t_drift/19+t_perfn; sr=t_panel*19*N_SR*83452/3600; base=1.15*1.05*(sr*load+126*N_CUSUM/old_N_CUSUM+old_candidate*N_SR/old_N_SR); full=base+measured_extra_total',
          'interpretation':'Base projection only; extra total includes uniform-cell recertification, source derivatives, curvature, interval assembly, audits and new cache costs. Old overhead is not evidence these are free.',
          'policy':'Retain 1126 as non-increasable ceiling, NOT as a qualified adequacy claim. Require measured full model including all bundles before production; if it exceeds ceiling a separate governed cap successor is required.'}
    (NS/'config/cost_model.json').write_bytes(canonical(cost))
    inputs=[
      'p5_nonlinear_dynamics/THEOREM.md','p5_nonlinear_dynamics/PROOF.md',
      'p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md',
      'p5x_global_nonlinear_dynamics/FROZEN_THEOREM.md','p5x_global_nonlinear_dynamics/FROZEN_SCOPE.md',
      'p5x_global_nonlinear_dynamics/PROOF.md',
      'p5x_global_nonlinear_dynamics/compute_optimization_r1/R1_COST_REPROJECTION.md',
      'p5x_global_nonlinear_dynamics/compute_optimization_r1/R1_FROZEN_SPEC.md',
      'p5x_global_nonlinear_dynamics/compute_optimization_r1/PROOF.md',
      'p5x_global_nonlinear_dynamics/compute_optimization_r1/drift_minorant.py',
      'p5x_global_nonlinear_dynamics/compute_optimization_r1/r1_stop_gate.py',
      'p5y_gate2b_sr_cover/sr_cover.py','p5y_gate2b_sr_cover/results/sr_cover.json',
      'p5y_gate2e_sr_metric/GATE2E_PREREGISTRATION.md',
      'p5y_k1_binding_campaign/CHECKPOINT.md','p5y_k1_binding_campaign/CHECKPOINT.json',
      'p5y_k1_binding_campaign/config/budget_ledger.json',
      'p5y_k1_binding_campaign/manifests/source_manifest.json',
      'p5y_k1_binding_campaign/manifests/cover_cusum.json',
      'p5y_k1_binding_campaign/manifests/cover_sr.json',
      'p5y_k1_binding_campaign/task1/task1_f0.py',
      'p5y_k1_binding_campaign/adjudication/TASK1_ADJUDICATION.json',
      'p5y_k1_task1r_budget_harness/CHECKPOINT_T1R.md','p5y_k1_task1r_budget_harness/code/harness.py',
      'p5y_k1_task1r_budget_harness/manifests/task1r_manifest.json',
      'p5y_k1_task1r_budget_harness/adjudication/TASK1R_ADJUDICATION.json',
      'p5y_k1_successor_optimized/CHECKPOINT_S.md','p5y_k1_successor_optimized/config/checkpoint_s.json',
      'p5y_k1_successor_optimized/config/cost_model.json','p5y_k1_successor_optimized/manifests/successor_manifest.json',
      'p5y_k1_successor_optimized/adjudication/CHECKPOINT_REVIEW.json',
      'p5y_k1_production/adjudication/K1_PRODUCTION_ADJUDICATION.json',
      'p5y_k1_production_driver/k1prod/driver.py','p5y_k1_production_driver/k1prod/kernel.py',
      'p5y_k1_production_driver/k1prod/schema.py','p5y_k1_cusum_kernel/code/cusum_raw.py',
      'p5y_k1_cusum_kernel/code/cover_walk.py','p5y_k1_cusum_kernel/COVER_WALK_FINDING.md',
      'p5y_k1_cusum_kernel/diagnostics/DF0_NEAR_ZERO_DIAGNOSIS.md',
      'p5y_k1_cusum_kernel/diagnostics/df0_near_zero_decomposition.json',
      'p5y_k1_cusum_kernel/results/representative_cells.json',
      'p5y_k1_cusum_kernel/results/certification_e_quarter.json']
    start=json.loads((NS/'manifests/protected_start.json').read_text())['start_head']
    authority={'start_head':start,'source_files':{str((base/f).relative_to(ROOT)):sha(base/f) for f in inputs},
               'ledger_review_provenance':'Prior assistant adjudication in this conversation, reaffirmed by the user brief. No standalone repository ledger-governance adjudication artifact found at START_HEAD; do not fabricate one. This successor records its own disposition.',
               'high_precision_claim_provenance':'Bit-invariance at 256/384/512 is stated in the historical diagnosis, but the committed six-row JSON does not contain the per-precision probes; not independently re-certified here.'}
    (NS/'manifests/authority.json').write_bytes(canonical(authority))
    nested={'B_eq':'9/500','B_trunc':'3/500','B_tail':'3/500','B_end':'1/250','B_int':'1/500','B_round':'1/500','B_reserve':'1/500'}
    config={
      'schema':'rebaseguard.p5y.k1.cover-ledger-successor.v1',
      'namespace':str(NS.relative_to(ROOT)), 'start_head':start,
      'parent_successor_hash':'a5d09f83078bf02ae5d015bfb08eb35429190f646cc51260f6ca72fce6e325ec',
      'parent_binding_hash':'ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d',
      'scope':ck['scope'], 'target':'sup_e |R_D,m(e)| < 2; K1 only; both detectors and m=1,2,3,5',
      'new_governed_campaign':True, 'changes_historical_verdicts':False,
      'history':{'P5':'PARTIAL','P5X':'PARTIAL','Task1':'FAIL','Task1R':'PASS',
                 'historical_K1':'K1_INCOMPLETE_BUDGET','old_successor':'FROZEN / NOT_RUN',
                 'historical_CUSUM_count':oldcounts['CUSUM'],'historical_SR_count':oldcounts['SR'],
                 'historical_object_units':ck['work_conservation']['total_units'],'LEVEL4_GLOBAL_CLOSURE':'NO'},
      'geometry':{'algorithm':'direct-left-minorant-integer-floor-v1','ordering':['CUSUM','SR','increasing-left-endpoint'],
          'grid_denominator':10**7,'C_precision_bits':192,'C_upper_denominator':2**32,'a_upper_denominator':2**60,
          'C_evaluation':'exact rational left endpoint; prior smaller upper bound may be retained by M2',
          'C_method':{'CUSUM':'drift_monotone_resolvent(cells=100,n_max=250,bits=192)',
                      'SR':'sr_drift_monotone_resolvent(cells=200,n_max=250) inside workprec(192)'},
          'C_rounding':'ceil(upper(C)*2^32)/2^32; min with previous transported upper bound',
          'a_rounding':'ceil(upper(2*phi(0))*2^60)/2^60',
          'nominal_step_half_width':'s=1/(4*a_upper*C_upper); s is NOT the actual Taylor radius',
          'step':'advance=floor(Q/(2*a_upper*C_upper)); STOP if advance<1; no forced minimum step',
          'right':'min(left+advance/Q,exact_splice)',
          'expansion_point':'EXACT_MIDPOINT', 'rho':'(right-left)/2 = max(abs(left-e0),abs(right-e0))',
          'endpoint_encoding':'affine [p,s] means p+s*c_SR; reduced rational strings; c_SR=log(A_exact)+1/2',
          'splice_exact':{'CUSUM':'11/2','SR':'log(4581762885148045/8796093022208)+1/2'},
          'SR_terminal_exception':'Only last right endpoint, e0 and rho use the exact symbolic c_SR. No decimal substitution or splice movement.',
          'tiling':'exact endpoints, shared boundaries only, final clipping, no gaps or positive-measure overlaps',
          'adaptive_splitting':False,'counts':counts,'cells_sha256':sha(NS/'config/cells.json'),
          'witnesses_sha256':sha(NS/'config/cover_witnesses.json'),
          'canonical_encoding':'ASCII JSON sort_keys=true separators=comma-colon plus one LF; no timestamp or float in cells'},
      'enclosure':{'style':'STYLE_1_COMPLETE_D_INTERVAL','formula':'R_interval+(cell-e0)*D_interval+[-rho^2*M_R2/2,+rho^2*M_R2/2]',
          'B_cover_complete':'outward_upper(rho*mag(D_interval)+rho^2*M_R2/2)',
          'separate_derivative_charge_allowed':False,'separate_value_radius_charge_allowed':False,
          'R_interval_contains_all_value_uncertainty':True,'D_interval_contains_all_derivative_uncertainty':True,
          'epsilon_F':'C*(deltaF+epsilon_S)',
          'epsilon_D':'C*(deltaD+k1*epsilon_F+epsilon_Sprime)',
          'epsilon_D_all_m':'sum_r epsilon_D_r/m+sum_t,r (1/t-1/m)*epsilon_Wprime_r,t-r-1+etaD',
          'curvature':'M_R2 >= sup_cell |R_m_second| from uniform-cell twice-differentiated resolvent and finite-power enclosures',
          'epsilon_H':'C*(deltaH+k2*epsilon_F+2*k1*epsilon_D+epsilon_Ssecond) uniformly over cell',
          'source_and_power_recurrences':'ERROR_ALGEBRA.md sections 2-4; binding, hashed',
          'no_interpolation':True},
      'ledger':{'units':'absolute R-error; derivative contributions require actual rho',
          'top_level_budgets':{k:str(v) for k,v in TOP_BUDGETS.items()}, 'B_resolvent':'0',
          'top_reserve':'1/100','reserve_drawable':False,'redistribution_allowed':False,
          'claimant_owners':CLAIMANTS,'B_other_usage':'0; locked unused, exact finite assembly has no remainder',
          'nested_B_candidate':nested,'nested_reserve_drawable':False,
          'local_gate_budget':'1/10','local_gate_delta_max':'(1/10)/C_cell_left','local_gate_panel_max':'(1/10)/(C_cell_left*n_panels_patch)',
          'B_end_is_top_level':False,'B_end_gate':'C*deltaF_end <= 1/250 for every SR cell/patch/F object; also aggregate all-m nested gate',
          'candidate_usage':'sum_r C*deltaF_r/m; local certificate channels already include their tails and arithmetic',
          'kernel_usage':'sum_r C*epsilon_S_r/m+sum_t,r (1/t-1/m)*epsilon_Wvalue_r,t-r-1',
          'rounding_usage':'etaR_round not included upstream','interval_usage':'etaR_interval not included upstream',
          'nested_gates':'all local F certificate gates and all-m aggregated gates; no per-object percentage summation',
          'ownership_key':['primitive_certificate','propagation_path','destination_quantity','derivative_order']},
      'assembly':{str(m):[[kind,r,j,str(c)] for kind,r,j,c in terms(m)] for m in (1,2,3,5)},
      'work':{'counts':counts,'objects_per_cell':19,'object_units':19*len(cells),
          'dependency_bundles_per_cell':1,'curvature_bundles_per_cell':4,'assembly_units_per_cell':4,
          'far_field_units':2,'total_units':len(work_ids(cells)),
          'formula':'(19+1+4+4)*(N_CUSUM+N_SR)+2',
          'bundle_contract':'dependency bundle exhausts h/S orders0,1 and all finite powers j<=3; each curvature bundle includes uniform-cell order2 obligations for its m, with reuse hash links, never assumed free',
          'shards':'[floor(k*N/S),floor((k+1)*N/S)); k=0..S-1',
          'old_universe_status':'SUPERSEDED_BY_SUCCESSOR; historical record immutable',
          'resume_identity':['new_checkpoint_hash','cells_sha256','backend_hash','detector','cell_index','unit_kind','function_or_m','exact_e0','exact_rho','source_certificate_hashes'],
          'dependency_graph':'code/algebra.py::unit_dependencies; source bundle depends only on h/S; dF depends on F and bundle; curvature m=5 owns shared uniform jets; m=1,2,3 consume its hashes; assemblies depend on own curvature and required objects',
          'curvature_shared_owner_m':5,'unit_execution_requires_completed_dependencies':True,
          'old_resume_records_accepted':False},
      'precision':ck['precision_policy'],'P1':ck['p1_rule'], 'complexity':ck['complexity_guard'],
      'backend':ck['backend'],'worker_ceiling':ck['memory_and_parallelism']['MAX_WORKERS'],
      'memory_and_cache':{'inherited':ck['memory_and_parallelism'],'new_bundle_peak_memory_qualified':False,
          'policy':'No oversubscription; cache key includes checkpoint, detector, patch, exact e0/cell and derivative order as applicable; retain inherited dependency keys; new bundles must fit frozen per-worker envelope.'},
      'cpu':cost,
      'implementation_dependencies':['complete_SR_raw_DAG','certified_midpoint_value_and_derivative_dependency_DAG',
          'uniform_cell_curvature_both_detectors_all_m','certified_interval_all_m_assembly',
          'new_resume_and_driver_adapter','full_extra_cost_and_memory_qualification'],
      'production_enabled':False,'production_driver_status':'OFF; inherited driver untouched and incompatible',
      'status':'FROZEN_WITH_IMPLEMENTATION_DEPENDENCIES','freeze_effective_when':'single governed commit anchors freeze manifest',
      'scientific_verdict':'NOT_RUN','LEVEL4_GLOBAL_CLOSURE':'NO',
      'protected_inputs_sha256':sha(NS/'manifests/protected_start.json'),
      'authority_sha256':sha(NS/'manifests/authority.json'),
      'error_algebra_sha256':sha(NS/'ERROR_ALGEBRA.md'),
      'stop_rules':['missing_certificate','incomplete_state_or_drift_coverage','budget_or_nested_gate_exceeded',
          'uncertified_C_direction','checkpoint_or_protected_mutation','degree_or_precision_change',
          'noncanonical_geometry','P1_failure','duplicate_or_missing_work','splice_gap','CPU_cap_reached',
          'unqualified_cost_or_memory','invalid_resumption','invalidating_implementation_defect'],
      'cover_disposition':{'FROZEN_323_MEANING':'EXECUTABLE_COVER_COUNT in the historical binding manifest (inconsistent with its rule)', 'estimate_provenance':'CONTINUUM_COST_ESTIMATE in the cited R1 cost reprojection; 322.49 is historical analysis, not a certified exact integral', 'new_CUSUM_count':counts['CUSUM'],'new_SR_count':counts['SR'],'historical_manifest_reinterpreted_in_place':False},
      'no_production_authorization_from_this_checkpoint':True,
      'future_activation':'A separately recorded implementation qualification and explicit production authorization are required; this frozen specification remains immutable.'}
    (NS/'config/checkpoint.json').write_bytes(canonical(config))
    record={'schema':'k1.cover-ledger.cell-record.v1','required_fields':[
        'checkpoint_hash','backend_hash','cells_sha256','detector','cell_index','left','right','e0','rho',
        'unit_kind','function_or_m','source_certificate_hashes','certificate_scope','norm_domain',
        'R_interval','D_interval','R2_interval','M_R2','value_error_breakdown','derivative_error_breakdown',
        'ledger_usage_by_owner','nested_candidate_gates','C_upper','C_evaluation','precision_bits',
        'P1','complexity','cpu_seconds_including_dependencies','peak_memory','status','failure_class'],
        'null_semantics':'null means NOT_COMPUTED; never zero and never PASS',
        'interval_encoding':'outward dyadic rational lower/upper endpoints with precision and exact argument identity',
        'symbolic_endpoint_encoding':config['geometry']['endpoint_encoding'],
        'pass_requires':'all required dependency records complete, bounds cover exact declared domain, all top/nested gates pass and final R interval strictly within (-2,2)',
        'float_point_enclosure_forbidden':True}
    (NS/'config/record_schema.json').write_bytes(canonical(record))
    print(json.dumps({'counts':counts,'object_units':config['work']['object_units'],'total_units':config['work']['total_units'],'base_cost':cost}))

if __name__=='__main__':main()
