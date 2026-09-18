"""Stage A after the terminal marker: derive the frozen ledger entries WITHOUT opening any scientific value.

Reads only: the terminal marker, RUN_STATE, the ATTEMPT_LOG event names, file hashes. Never parses the sealed record's
scientific payload. Uses the frozen lifecycle.outcome_entry / reconcile from the launch checkout. Writes nothing.
"""
import hashlib
import json
import sys
from pathlib import Path

L = Path("/root/work/k5-real-launch-69a162d0")
EX = L / "level4/closure_proofs/p5y_k5_cusum_real_point_executor"
PROTO = L / "level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol"
sys.path.insert(0, str(EX / "code"))
import paths  # noqa: E402,F401
import lifecycle as LC  # noqa: E402

S = Path("/root/work/k5-first-real-probe/slot-1")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
files = sorted(p.name for p in S.iterdir())
print("slot files", files)
print("ATTEMPT_LOG events", [json.loads(l).get("event") for l in (S / "ATTEMPT_LOG.jsonl").read_text().splitlines() if l.strip()])
for n in files:
    print(" ", n, sha(S / n))
term = [n for n in ("RUN_COMPLETE.json", "RUN_FAILED.json") if (S / n).exists()]
print("terminal", term)
t = json.loads((S / term[0]).read_text())
safe = {k: v for k, v in t.items() if k not in ("qualification_gates", "traceback")}
print("terminal marker (non-scientific fields):", json.dumps(safe, sort_keys=True)[:1500])
if "qualification_gates" in t:
    print("qualification gates:", t["qualification_gates"])
out = LC.outcome_entry(S)
led = [json.loads(l) for l in (PROTO / "ledger/ATTEMPT_LEDGER.jsonl").read_text().splitlines() if l.strip()]
new = [out]
seal = next((n for n in ("SCIENTIFIC_RECORD_SEALED.json", "VOID_RECORD_SEALED.json") if (S / n).exists()), None)
if seal:
    new.append({"event": seal[:-len(".json")], "slot": "slot-1", "sha256": sha(S / seal)})
problems = LC.reconcile(S, led + new)
print("reconcile problems", problems)
print("NEW_LEDGER_LINES")
for e in new:
    print(json.dumps(e, sort_keys=True))
