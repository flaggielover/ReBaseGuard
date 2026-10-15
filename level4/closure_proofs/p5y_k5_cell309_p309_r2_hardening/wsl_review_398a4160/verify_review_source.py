"""Verify source bindings against the Windows candidate's Git blobs; writes nothing.

python3 -B verify_review_source.py <repository>
The review used transcript reconstruction. Matching canonical blobs is required
before applying candidate-fix.patch. No inference from a clean worktree is used.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

CANDIDATE = '398a416024bf47c829826d4dc3242503a355867b'
expected = json.loads(Path(__file__).with_name('EXPECTED_SOURCE_SHA256.json').read_text())
checks = {}
for name, digest in expected.items():
    result = subprocess.run(['git', '-C', sys.argv[1], 'cat-file', 'blob', CANDIDATE + ':' + name],
                            capture_output=True)
    checks[name] = result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest
print(json.dumps({'candidate': CANDIDATE, 'checks': checks, 'all_match': all(checks.values())}, indent=2))
sys.exit(0 if all(checks.values()) else 1)
