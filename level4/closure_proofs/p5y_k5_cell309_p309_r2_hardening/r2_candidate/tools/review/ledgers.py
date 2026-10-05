"""Reviewer helper: apply the candidate's H3 ledger rules (re-implemented here, not imported) to the ledgers at the
candidate commit, read via git show."""
import json, subprocess, datetime

REPO = "/home/user/ReBaseGuard"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
REV = "93d550638b8c79ae1c252fc6c2b0194b1a416b49"
for name in ("ledger/ZERO_TARGET_LEDGER.jsonl", "ledger/EXPOSURE_LEDGER.jsonl"):
    raw = subprocess.run(["git", "-C", REPO, "show", f"{REV}:{NS}{name}"], capture_output=True).stdout
    bad, nondict, naive, starts = [], 0, 0, []
    if raw and not raw.endswith(b"\n"):
        bad.append("torn tail")
    lines = raw.decode(errors="replace").splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            bad.append(f"row {i+1} unparseable")
            continue
        if not isinstance(row, dict):
            nondict += 1
            continue
        if any(row.get(k, 0) != 0 for k in ("new_target_evaluations", "target_equivalent_proxies",
                                              "target_informed_optimisation")):
            bad.append(f"row {i+1} nonzero counter")
        u = str(row.get("utc", ""))
        try:
            d = datetime.datetime.fromisoformat(u.replace("Z", "+00:00"))
            if d.tzinfo is None:
                naive += 1
        except ValueError:
            pass
        p = str(row.get("purpose", ""))
        if p.startswith("QUALIFICATION RUN START") or p.startswith("HOST RERUN START"):
            starts.append((i + 1, row.get("utc"), p[:80]))
    print(name, "rows", len(lines), "problems", bad[:10], "nondict", nondict, "naive_utc", naive, "start_lines", starts)
