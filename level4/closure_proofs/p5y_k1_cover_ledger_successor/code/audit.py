"""Read-only adjudicator: rederive checks, do not import build_spec or write verdicts."""
import hashlib,json,subprocess
from fractions import Fraction as F
from geometry import ROOT,NS,canonical,replay
from algebra import work_ids


def digest(data):return hashlib.sha256(data).hexdigest()

def aggregate(items):
    return digest(b''.join(p.encode()+b'\0'+h.encode()+b'\n' for p,h in items))

def parent_checks():
    base=ROOT/'level4/closure_proofs'
    checked={}
    for folder,file,key in [
        ('p5y_k1_successor_optimized','successor_manifest.json','SUCCESSOR_CHECKPOINT_HASH'),
        ('p5y_k1_task1r_budget_harness','task1r_manifest.json','TASK1R_CHECKPOINT_HASH'),
        ('p5y_k1_binding_campaign','source_manifest.json','CHECKPOINT_HASH')]:
        p=base/folder;d=json.loads((p/'manifests'/file).read_text())
        checked[folder]=aggregate(d['file_sha256'].items())==d[key] and all(
            digest((p/f).read_bytes())==h for f,h in d['file_sha256'].items())
    return checked

def protected_check():
    baseline=json.loads((NS/'manifests/protected_start.json').read_text())
    start=baseline['start_head']
    # Both index and worktree versus the named start. Includes deletions and mode changes.
    changed=subprocess.check_output(['git','diff','--name-only',start,'--'],cwd=ROOT).decode().splitlines()
    bad=[p for p in changed if not p.startswith(str(NS.relative_to(ROOT))+'/')]
    # Recreate the anchor manifest from immutable Git objects, not the worktree.
    actual={}
    for r in subprocess.check_output(['git','ls-tree','-rz',start],cwd=ROOT).split(b'\0'):
        if not r:continue
        meta,name=r.split(b'\t',1);mode,typ,oid=meta.decode().split()
        actual[name.decode()]={'mode':mode,'type':typ,'git_oid':oid}
    return not bad and actual==baseline['entries']

def verify_freeze():
    d=json.loads((NS/'manifests/freeze.json').read_text())
    actual={str(p.relative_to(NS)):digest(p.read_bytes()) for p in NS.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p!=NS/'manifests/freeze.json'}
    return actual==d['files'] and aggregate(sorted(actual.items()))==d['checkpoint_hash']

def review():
    c=json.loads((NS/'config/checkpoint.json').read_text())
    cells=json.loads((NS/'config/cells.json').read_text())
    witness=json.loads((NS/'config/cover_witnesses.json').read_text())
    old=json.loads((ROOT/'level4/closure_proofs/p5y_k1_successor_optimized/config/checkpoint_s.json').read_text())
    auth=json.loads((NS/'manifests/authority.json').read_text())
    reps=json.loads((NS/'diagnostics/representatives.json').read_text())
    pc=parent_checks()
    checks={
        'parent_manifests_and_hashes':all(pc.values()),
        'protected_tree_preserved':protected_check(),
        'authority_hashes':all(digest((ROOT/p).read_bytes())==h for p,h in auth['source_files'].items()),
        'cover_replay':canonical(replay(witness))==(NS/'config/cells.json').read_bytes(),
        'cover_hash':digest((NS/'config/cells.json').read_bytes())==c['geometry']['cells_sha256'],
        'scope_preserved':c['scope']==old['scope'],
        'precision_preserved':c['precision']==old['precision_policy'],
        'P1_preserved':c['P1']==old['p1_rule'],
        'complexity_preserved':c['complexity']==old['complexity_guard'],
        'numeric_budgets_preserved':all(F(v)==F(str(old['budget_ledger']['ledger_absolute'][k])) for k,v in c['ledger']['top_level_budgets'].items()),
        'no_reserve_or_redistribution':not any(c['ledger'][k] for k in ('reserve_drawable','nested_reserve_drawable','redistribution_allowed')),
        'derivative_dependency_not_omitted':'k1*epsilon_F' in c['enclosure']['epsilon_D'] and 'epsilon_Sprime' in c['enclosure']['epsilon_D'],
        'one_taylor_charge':c['enclosure']['style']=='STYLE_1_COMPLETE_D_INTERVAL' and c['enclosure']['separate_derivative_charge_allowed'] is False,
        'work_count_from_cells':len(work_ids(cells))==c['work']['total_units'],
        'old_resume_rejected':c['work']['old_resume_records_accepted'] is False,
        'cap_not_increased':c['cpu']['hard_cap_cpu_h']==1126,
        'unknown_full_cost_honest':c['cpu']['full_campaign_projection_cpu_h'] is None and c['cpu']['cap_adequacy']=='NOT_ESTABLISHED',
        'missing_certificates_not_passed':all(r['status']=='NOT_COMPUTED' and r['B_cover_total_utilization'] is None for r in reps['rows']),
        'all_representative_m':len(reps['rows'])==24 and {r['m'] for r in reps['rows']}=={1,2,3,5},
        'production_off':c['production_enabled'] is False and reps['production_run'] is False,
        'scientific_state_unchanged':c['scientific_verdict']=='NOT_RUN' and c['LEVEL4_GLOBAL_CLOSURE']=='NO',
        'implementation_dependencies_explicit':len(c['implementation_dependencies'])==6,
    }
    failed=[k for k,v in checks.items() if not v]
    return {'review_kind':'separate read-only self-adjudication program; not an independent human or agent',
            'checks':checks,'checks_failed':failed,
            'verdict':'NOT_FREEZABLE' if failed else 'FROZEN_WITH_IMPLEMENTATION_DEPENDENCIES',
            'certification_status':'NOT_COMPUTED / IMPLEMENTATION_DEPENDENCY',
            'production_ready':False,'scientific_verdict_changed':False,
            'limitations':['Whole-cell raw curvature certificates missing','Complete midpoint dependency and interval assemblies missing',
                          'Full cost/memory adequacy at 1126 CPU-h not established',
                          'Prior 256/384/512-bit comparison only documented narratively in committed inputs']}

if __name__=='__main__':
    result=review();print(json.dumps(result,indent=2))
    raise SystemExit(bool(result['checks_failed']))
