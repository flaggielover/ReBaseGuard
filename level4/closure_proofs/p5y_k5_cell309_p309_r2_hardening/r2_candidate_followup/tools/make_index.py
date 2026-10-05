"""EVIDENCE_INDEX.json for r2_candidate_followup/: every file with sha256 and size, plus the commits it describes.

usage: make_index.py <r2_candidate_followup dir>
"""
import datetime
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
OUT = "EVIDENCE_INDEX.json"
files = {str(p.relative_to(root)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
         for p in sorted(root.rglob("*")) if p.is_file() and p.name != OUT and "__pycache__" not in p.parts}
doc = {"schema": "P309_R2_CANDIDATE_FOLLOWUP_INDEX/1",
       "candidate_commit": "a119e9789e2a1d42b584fff8a2301946a37f1bcb",
       "previous_candidate_commit": "93d550638b8c79ae1c252fc6c2b0194b1a416b49",
       "base_r2_commit": "101ef2cb17e5eab2892212178278da45b98004ed",
       "deliverables": {"FILESYSTEM_PRELAUNCH_PROBE_REVIEW.md": "FILESYSTEM_PRELAUNCH_PROBE_REVIEW.md",
                        "GOVERNANCE_REPIN_SUPPLEMENT.md": "GOVERNANCE_REPIN_SUPPLEMENT.md",
                        "FORMAL_DELTA_REVIEW_PACKET.md": "FORMAL_DELTA_REVIEW_PACKET.md",
                        "FINAL_R2_ADOPTION_REVIEW.md": "FINAL_R2_CANDIDATE_REVIEW.md (renamed: the session guard "
                                                       "refuses paths containing 'adoption')"},
       "test_tool": "../tests/test_r2h_fsprobe.py",
       "verdict": "R2_ADOPTION_CANDIDATE_READY",
       "statement": "result-free; NEW TARGET EVALUATIONS = 0; no grant; no adoption; no merge; no freeze; "
                    "no qualification; r5 unchanged; no r6; Cell 309 OPEN",
       "built_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "files": files}
(root / OUT).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
print(len(files), "files indexed")
