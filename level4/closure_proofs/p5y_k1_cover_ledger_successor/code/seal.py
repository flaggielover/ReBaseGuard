"""Seal a pre-commit governance candidate; refuse a namespace already in HEAD."""
import json,subprocess
from geometry import NS,ROOT
from audit import digest,aggregate,review


def main():
    rel=str(NS.relative_to(ROOT))
    committed=subprocess.check_output(['git','ls-tree','HEAD','--',rel+'/config/checkpoint.json'],cwd=ROOT)
    if committed:raise SystemExit('Already committed: frozen namespace may not be resealed.')
    report=review()
    if report['checks_failed']:raise SystemExit(str(report))
    (NS/'adjudication/REVIEW.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    files={str(p.relative_to(NS)):digest(p.read_bytes()) for p in NS.rglob('*')
           if p.is_file() and '__pycache__' not in p.parts and p!=NS/'manifests/freeze.json'}
    out={'schema':'rebaseguard.k1.cover-ledger.freeze.v1','files':dict(sorted(files.items())),
         'checkpoint_hash':aggregate(sorted(files.items())),
         'aggregate_rule':'sha256(concat sorted relative-path + NUL + file SHA256 + LF)',
         'effective_anchor':'the single commit adding this manifest; discover with git log --diff-filter=A -- manifests/freeze.json',
         'self_hash_exclusion':'Only this manifest excluded; commit anchors it. All remaining namespace files, including reports and tests, are hashed.',
         'status':'FROZEN_WITH_IMPLEMENTATION_DEPENDENCIES','production_enabled':False}
    (NS/'manifests/freeze.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(out['checkpoint_hash'])

if __name__=='__main__':main()
