"""Focused governance tests. No production function certification or cover run."""
import ast,hashlib,json,sys,subprocess
from fractions import Fraction as F
from pathlib import Path
import unittest
NS=Path(__file__).resolve().parents[1]
ROOT=NS.parents[2]
sys.path.insert(0,str(NS/'code'))
from geometry import canonical,replay,Q,C_DEN,A_DEN
from algebra import Interval,cover,assemble,terms,resolvent_errors,power_error_step,shard,work_ids,CLAIMANTS,require_production,unit_dependencies
from audit import parent_checks,protected_check,verify_freeze,review
C=json.loads((NS/'config/checkpoint.json').read_text())
CELLS=json.loads((NS/'config/cells.json').read_text())
W=json.loads((NS/'config/cover_witnesses.json').read_text())


def add(x,y):return tuple(F(a)+F(b) for a,b in zip(x,y))
def scale(x,k):return tuple(F(a)*k for a in x)
def fracstr(x):return str(x.numerator)+'/'+str(x.denominator)


class GeometryTests(unittest.TestCase):
    def test_byte_identical_replay_in_separate_processes(self):
        command=[sys.executable,'-c',f"import sys,json;sys.path.insert(0,{str(NS/'code')!r});from geometry import canonical,replay;sys.stdout.buffer.write(canonical(replay(json.load(open({str(NS/'config/cover_witnesses.json')!r})))))"]
        a=subprocess.check_output(command);b=subprocess.check_output(command)
        self.assertEqual(a,b);self.assertEqual(a,(NS/'config/cells.json').read_bytes())

    def test_independent_fraction_cover_generation(self):
        # Independent reconstruction: Fraction arithmetic instead of production integer expression;
        # no use of geometry.cell, geometry.replay or geometry.affine.
        output=[]
        for d in ('CUSUM','SR'):
            left=F(0);a=F(W['a_upper_num'],A_DEN)
            rows=W['detectors'][d]['bounds']
            for i,row in enumerate(rows):
                amp=F(row['C_upper_num'],C_DEN)
                n=(F(Q)/(2*a*amp)).numerator//(F(Q)/(2*a*amp)).denominator
                right=left+F(n,Q)
                if d=='CUSUM':right=min(right,F(11,2));pair=(right,F(0))
                elif right*Q>W['detectors'][d]['terminal_floor_q']:pair=(F(0),F(1))
                else:pair=(right,F(0))
                lp=(left,F(0));mp=scale(add(lp,pair),F(1,2));rho=scale(add(pair,scale(lp,-1)),F(1,2))
                encode=lambda x:list(map(fracstr,x))
                output.append({'detector':d,'index':i,'left':encode(lp),'right':encode(pair),
                    'e0':encode(mp),'rho':encode(rho),'C_upper':f"{row['C_upper_num']}/{C_DEN}",
                    'C_evaluation':encode(lp),'nominal_step_half_width':str(F(1)/(4*a*amp))})
                left=right
        self.assertEqual(canonical(output),(NS/'config/cells.json').read_bytes())

    def test_exact_tiling_and_rational_grid(self):
        for d in ('CUSUM','SR'):
            cells=[c for c in CELLS if c['detector']==d]
            self.assertEqual(cells[0]['left'],['0/1','0/1'])
            for i,c in enumerate(cells):
                self.assertEqual(c['index'],i)
                self.assertEqual(F(c['left'][1]),0)
                self.assertEqual((F(c['left'][0])*Q).denominator,1)
                self.assertEqual(c['C_evaluation'],c['left'])
                if i:self.assertEqual(cells[i-1]['right'],c['left'])
                if F(c['right'][1])==0:
                    self.assertGreater(F(c['right'][0]),F(c['left'][0]))
                    self.assertEqual((F(c['right'][0])*Q).denominator,1)
                else:self.assertEqual((d,i),('SR',len(cells)-1))
            self.assertEqual(cells[-1]['right'],['11/2','0/1'] if d=='CUSUM' else ['0/1','1/1'])

    def test_midpoint_and_actual_radius(self):
        for c in CELLS:
            left=tuple(map(F,c['left']));right=tuple(map(F,c['right']))
            mid=tuple(map(F,c['e0']));rho=tuple(map(F,c['rho']))
            self.assertEqual(mid,scale(add(left,right),F(1,2)))
            self.assertEqual(add(mid,scale(left,-1)),rho)
            self.assertEqual(add(right,scale(mid,-1)),rho)

    def test_arb_geometry_containment_and_safe_rounding(self):
        sys.path.insert(0,str(ROOT/'rebaseguard-proof/src'))
        from flint import arb
        from rebaseguard_certify.arb_backend import workprec
        with workprec(192):
            cstar=(arb(4581762885148045)/8796093022208).log()+arb(1)/2
            aa=arb(2)/(2*arb.pi()).sqrt()
            self.assertTrue(arb(W['a_upper_num'])/A_DEN>=aa)
            def value(pair):
                p,s=map(F,pair)
                return arb(p.numerator)/p.denominator+arb(s.numerator)/s.denominator*cstar
            for c in CELLS:
                l,r,e,rho=map(value,(c['left'],c['right'],c['e0'],c['rho']))
                self.assertTrue(l<e and e<r and rho>0)
                amp=F(c['C_upper']);a=F(W['a_upper_num'],A_DEN)
                s=F(1)/(4*a*amp)
                self.assertTrue(rho<=arb(s.numerator)/s.denominator)
            for det in ('CUSUM','SR'):
                previous=None
                for row in W['detectors'][det]['bounds']:
                    raw=arb(row['raw_bound_ball'])
                    rounded=arb(row['rounded_C_num'])/C_DEN
                    self.assertTrue(rounded>=raw)
                    expected=row['rounded_C_num'] if previous is None else min(previous,row['rounded_C_num'])
                    self.assertEqual(row['C_upper_num'],expected)
                    previous=expected

    def test_no_count_or_old_universe_hardcode_in_executable_spec(self):
        for file in ('geometry.py','algebra.py','build_spec.py'):
            tree=ast.parse((NS/'code'/file).read_text())
            constants=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant)]
            self.assertNotIn(323,constants);self.assertNotIn(12255,constants)

    def test_fresh_minorant_spotchecks(self):
        sys.path[:0]=[str(ROOT/'rebaseguard-proof/src'),str(ROOT/'level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r1'),str(ROOT/'level4/closure_proofs/p5y_gate2b_sr_cover')]
        from flint import arb
        from rebaseguard_certify.arb_backend import workprec,rational
        from drift_minorant import drift_monotone_resolvent
        from sr_cover import sr_drift_monotone_resolvent
        with workprec(192):
            for det in ('CUSUM','SR'):
                rows=W['detectors'][det]['bounds']
                for row in (rows[0],rows[-1]):
                    if det=='CUSUM':
                        b=arb(drift_monotone_resolvent(e_num=row['left_q'],e_den=Q)['resolvent_bound']['ball'])
                    else:
                        b,_,_,_,mass=sr_drift_monotone_resolvent(rational(row['left_q'],Q))
                        self.assertTrue(mass)
                    self.assertEqual(int((b.upper()*C_DEN).ceil().fmpq()),row['rounded_C_num'])

    def test_canonical_hash(self):
        self.assertEqual(hashlib.sha256((NS/'config/cells.json').read_bytes()).hexdigest(),C['geometry']['cells_sha256'])


class AlgebraTests(unittest.TestCase):
    def test_dependency_propagation_not_local_defect_only(self):
        ef,ed=resolvent_errors(3,F(1,100),F(2,100),F(4,5),F(1,1000),F(1,50))
        self.assertEqual(ef,F(9,100));self.assertEqual(ed,F(279,1000))
        self.assertGreater(ed,3*F(1,1000))
        with self.assertRaises(ValueError):resolvent_errors(3,-1,0,1,1,0)

    def test_leibniz_error_paths_second_order(self):
        self.assertEqual(power_error_step(1,2,3,(5,7,11),(13,17,19)),(18,34,73))

    def test_complete_interval_taylor_no_double_counting(self):
        R=Interval(1,2);D=Interval(-3,5)
        result,amount=cover(R,D,F(1,10),4)
        self.assertEqual(amount,F(13,25))
        self.assertEqual(result,Interval(F(12,25),F(63,25)))
        with self.assertRaises(ValueError):cover(R,D,F(1,10),4,separate_derivative_charge=F(1,5))
        # Correct breakdown 0.1*|midD| + 0.1*radD + .1^2*4/2.
        self.assertEqual(amount,F(1,10)*1+F(1,10)*4+F(1,50))

    def test_taylor_encloses_known_quadratic_at_extrema(self):
        # R(e)=2+3e+4e^2 centered at zero; R''=8, cell [-1/4,1/4].
        got,_=cover(Interval(2,2),Interval(3,3),F(1,4),8)
        for e in (F(-1,4),F(0),F(1,4)):
            v=2+3*e+4*e*e
            self.assertLessEqual(got.lo,v);self.assertGreaterEqual(got.hi,v)

    def test_all_m_coefficients_against_short_stopping_decomposition(self):
        for m in (1,2,3,5):
            expected=[('F',r,0,F(1,m)) for r in range(m)]
            for r in range(m-1):
                for j in range(m-r-1):
                    expected.append(('W',r,j,F(1,r+j+1)-F(1,m)))
            self.assertEqual(set(terms(m)),set(expected))

    def test_interval_assembly_all_orders_all_m(self):
        # Compare to an independently grouped per-terminal-time expansion.
        for order in (0,1,2):
            fv={r:Interval(r+order,r+order+F(1,10)) for r in range(5)}
            wv={(r,j):Interval(r-j-order,r-j-order+F(1,20)) for r in range(4) for j in range(4-r)}
            for m in (1,2,3,5):
                lo=sum(fv[r].lo for r in range(m))/m
                hi=sum(fv[r].hi for r in range(m))/m
                for r in range(m-1):
                    for j in range(m-r-1):
                        coeff=F(1,r+j+1)-F(1,m)
                        lo+=coeff*wv[r,j].lo;hi+=coeff*wv[r,j].hi
                self.assertEqual(assemble(m,fv,wv),Interval(lo,hi))

    def test_budget_owner_uniqueness_and_preserved_allocations(self):
        self.assertEqual(C['ledger']['claimant_owners'],CLAIMANTS)
        self.assertEqual(len(CLAIMANTS),len(set(CLAIMANTS)))
        self.assertEqual(sum(map(F,C['ledger']['top_level_budgets'].values())),F(19,100))
        self.assertEqual(sum(map(F,C['ledger']['nested_B_candidate'].values())),F(1,25))
        for k in ('dF_equation_certificate','Kprime_F_dependency','derivative_source_dependency','curvature_envelope'):
            self.assertEqual(CLAIMANTS[k],'B_cover')
        self.assertFalse(C['ledger']['B_end_is_top_level'])
        self.assertEqual(F(C['ledger']['local_gate_budget']),F(1,10))


class GovernanceTests(unittest.TestCase):
    def test_unit_counts_from_actual_cover(self):
        ids=work_ids(CELLS)
        self.assertEqual(len(ids),28*len(CELLS)+2)
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(C['work']['total_units'],len(ids))
        self.assertEqual(C['work']['object_units'],19*len(CELLS))
        self.assertEqual(C['geometry']['counts'],{d:sum(c['detector']==d for c in CELLS) for d in ('CUSUM','SR')})

    def test_dependency_graph_acyclic_and_shared_curvature_single_owner(self):
        graph=unit_dependencies(CELLS)
        self.assertEqual(set(graph),set(work_ids(CELLS)))
        indegree={u:len(deps) for u,deps in graph.items()}
        consumers={u:[] for u in graph}
        for u,deps in graph.items():
            for dep in deps:
                self.assertIn(dep,graph);consumers[dep].append(u)
        ready=[u for u in graph if not indegree[u]];seen=[]
        while ready:
            u=ready.pop();seen.append(u)
            for nxt in consumers[u]:
                indegree[nxt]-=1
                if indegree[nxt]==0:ready.append(nxt)
        self.assertEqual(len(seen),len(graph))
        for c in CELLS:
            prefix=(c['detector'],c['index'])
            for m in (1,2,3):
                self.assertEqual(graph[(*prefix,'curvature',str(m))],{(*prefix,'curvature','5')})

    def test_floor_shards_no_overexecution(self):
        for n in (0,1,7,19,C['work']['total_units']):
            for workers in (1,2,7,64):
                parts=[shard(n,k,workers) for k in range(workers)]
                actual=[i for l,r in parts for i in range(l,r)]
                self.assertEqual(actual,list(range(n)))

    def test_parent_hash_verification(self):self.assertTrue(all(parent_checks().values()))
    def test_protected_tree(self):self.assertTrue(protected_check())
    def test_checkpoint_hash_verification(self):self.assertTrue(verify_freeze())
    def test_read_only_adjudication(self):self.assertEqual(review()['checks_failed'],[])

    def test_production_guard_always_off(self):
        self.assertFalse(C['production_enabled'])
        self.assertFalse(C['work']['old_resume_records_accepted'])
        with self.assertRaisesRegex(RuntimeError,'PRODUCTION_DISABLED'):require_production()
        for folder in ('results','certificates','production_logs'):
            self.assertFalse((NS/folder).exists())

    def test_missing_data_is_not_zero_or_pass(self):
        data=json.loads((NS/'diagnostics/representatives.json').read_text())
        self.assertEqual({r['target_point'] for r in data['rows']},{'0','1/10','1/4','1','27/5','11/2'})
        for r in data['rows']:
            for field in ('R_interval_width','D_interval_width','derivative_uncertainty_contribution','curvature_contribution','B_cover_total_utilization','top_level_utilization'):
                self.assertIsNone(r[field])
            self.assertEqual(r['failure_class'],'IMPLEMENTATION_DEPENDENCY')
            self.assertEqual(r['status'],'NOT_COMPUTED')

    def test_cost_recomputed_from_measured_primitives(self):
        old=json.loads((ROOT/'level4/closure_proofs/p5y_k1_successor_optimized/config/cost_model.json').read_text())
        parent=json.loads((ROOT/'level4/closure_proofs/p5y_k1_successor_optimized/config/checkpoint_s.json').read_text())
        n=sum(c['detector']=='SR' for c in CELLS);nc=len(CELLS)-n
        panels=parent['cover']['SR']['total_panels_over_live_patches']
        sr=(old['t_shared_s']+n*old['t_drift_s']+19*n*old['t_perfn_s'])*panels/3600
        cus=126*nc/parent['cover']['CUSUM']['subcell_count']
        cand=old['candidate_build_cpu_h']*n/parent['cover']['SR']['subcell_count']
        for name,mult in [('central',1),('conservative',old['load_factor']),('worst_plausible',old['load_factor']*1.25)]:
            expect=1.15*1.05*(sr*mult+cus+cand)
            self.assertAlmostEqual(C['cpu']['base_only_'+name+'_cpu_h'],expect,places=9)

    def test_cap_and_unknown_extra_cost(self):
        cost=C['cpu'];self.assertEqual(cost['hard_cap_cpu_h'],1126)
        self.assertIsNone(cost['full_campaign_projection_cpu_h'])
        self.assertEqual(cost['cap_adequacy'],'NOT_ESTABLISHED')
        self.assertIsNone(cost['additional_dependency_curvature_certified_assembly_cpu_h'])

if __name__=='__main__':unittest.main(verbosity=2)
