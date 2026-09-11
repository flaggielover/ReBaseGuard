"""Assemble RESULT.md from config/T345_RECORD.json and the section drafts (no shell interpolation)."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
rec = json.loads((NS / "config/T345_RECORD.json").read_text())
sha = hashlib.sha256((NS / "config/T345_RECORD.json").read_bytes()).hexdigest()
det = rec["determinism"]
fw = rec["production_firewall"]
rows = "\n".join(f"| `{k}` | {v['mode']} | {v['total_moved_scientific']} | {v['total_moved_incidental']} |"
                 for k, v in sorted(det.items()))
head = f"""# P5Y K1 SR O9 T3/T4/T5: {rec['classification']}

**Scope: scientific qualification only.** This result is NOT K1 closure and NOT a production authorization or
readiness claim. The 316-cell campaign was not started.

The authoritative record is `config/T345_RECORD.json` (sha256 `{sha}`). The parent is T2 `1bd7a3f` (tag
`p5y-k1-sr-o9-t2-per-patch-closed`), which is unchanged, as are all predecessor namespaces.

**One real SR cell, cell 150, achieves 28/28 frozen obligations PASS.** The bounded representative set of cells
0, 150, 250, 275, 313 and 315 was completed over all 3,994 patches before T5 was finalized. It exposes a
high-drift regime in which the frozen B_cover does not close under the frozen refinement architecture (see below).

## Determinism (frozen aux4 classifier; only INCIDENTAL_RUNTIME leaves may move)

| comparison | mode | scientific leaves moved | incidental leaves moved |
|---|---|---|---|
{rows}
"""
disclosures = """
## Disclosures
1. **Aggregator provenance.** The first T3 aggregator recorded whole-file hashes of the shared chunk files. Those
   files were still growing, so a cell-0 pipeline replay moved 30 provenance leaves while the content was identical.
   The aggregator now hashes the records it consumes for the cell. The superseded replay is kept in
   `evidence/replay/superseded_whole_file_provenance/`.
2. **Replay configuration.** For patches (0,0) and (0,18), the original cell-313 records came from a five-cell tile
   run in which the PanelShared cache was warm. A standalone replay moved only the nested cache counters, which the
   frozen classifier defaults to SCIENTIFIC; every node value was identical. The definitive replay uses the matching
   configuration (`evidence/replay/matched_tile_config/`), and the standalone comparison is kept in
   `evidence/replay/superseded_config_mismatch/`.
3. **Firewall check.** The record's production-process check originally used a substring search, which matched this
   tool's own shells. It now matches only python processes running a production entry point.
4. **Terminal cell 315.** Its ρ = p + s·c_SR (SR_terminal_exception) is carried as a 256-bit Arb enclosure, with
   formulas and gates identical to `ledger.cell_ledger`.
5. **Inherited canonical IDs.** Panel IDs use the governance-canonical v2 form inherited from the T2 closure.
"""
firewall = f"""
## Production firewall
- prodctl was not run. The production ledger was not touched, no retries were consumed, and no AWS or Vultr
  production workers were started.
- The production worktrees are clean and unchanged: `ReBaseGuard-sr-parallel` at {fw['worktrees']['ReBaseGuard-sr-parallel']['head']} and
  `ReBaseGuard-sr-lifecycle` at {fw['worktrees']['ReBaseGuard-sr-lifecycle']['head']}.
- Active `rbg-` units: {len(fw['active_rbg_units'])}. Production processes: {len(fw['production_processes'])}.
- The historical 2026-09-10 unit is unchanged: {' '.join(fw['historical_unit'])}.
- **Firewall PASS: {fw['PASS']}.**

## Not claimed
K1 closure, production readiness or authorization, the 316-cell campaign, any cell other than the six listed, and the
far field (inherited, not recomputed).
"""
parts = [head] + [(NS / "work" / n).read_text() for n in ("RESULT_DRAFT_METHOD.md", "RESULT_DRAFT_BODY.md",
                                                           "RESULT_DRAFT_REP.md")] + [disclosures, firewall]
(NS / "RESULT.md").write_text("\n".join(parts))
print("RESULT.md", len("\n".join(parts)), "chars; record sha", sha)
