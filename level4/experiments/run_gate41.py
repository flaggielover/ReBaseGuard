#!/usr/bin/env python
"""Gate 4.1 campaign driver.

Usage::

    level4/.venv/bin/python level4/experiments/run_gate41.py level4/configs/gate41_smoke.json

Runs the grid described by the config, writing raw Parquet, per-cell manifests
and summaries, and a combined headline CSV under ``level4/results``.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rebaseguard_level4.campaigns import run_gate41_campaign  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    config = json.loads(Path(argv[1]).read_text())
    print(f"Gate 4.1 campaign — stage={config['stage']}")
    print(f"  purpose: {config['purpose']}")
    started = time.time()
    result = run_gate41_campaign(
        stage=config["stage"],
        rho_values=config["rho_values"],
        m_values=config["m_values"],
        n_replicates=config["n_replicates"],
        n_cycles=config["n_cycles"],
        burn_in=config["burn_in"],
        master_seed=config["master_seed"],
        n_bootstrap=config["n_bootstrap"],
        write_raw=config.get("write_raw", True),
    )
    print(f"\ncampaign_id : {result['campaign_id']}")
    print(f"outputs     : {result['out_dir']}")
    print(f"raw         : {result['raw_dir']}")
    print(f"total time  : {time.time() - started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
