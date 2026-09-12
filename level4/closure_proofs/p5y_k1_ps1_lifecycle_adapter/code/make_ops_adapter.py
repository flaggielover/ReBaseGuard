"""Generate the PS1 lifecycle adapter's ops/ MECHANICALLY from the audited lifecycle successor (bcec064):
every ops file byte-for-byte, except the ONE parent-namespace constant in opscommon.py (asserted to occur exactly
once); the governed runtime-state exclude block is the historical block with only its namespace path and governing
file retargeted (its BEGIN marker prefix, which runtime_state.BEGIN matches, is unchanged). Re-running must
reproduce the committed files byte for byte (tests/test_adapter.py)."""
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = NS.parent / "p5y_k1_sr_production_lifecycle_successor"
OLD_NS = "p5y_k1_sr_production_authorized_successor"
NEW_NS = "p5y_k1_ps1_production"
SUBS = {"opscommon.py": [('PARENT_NS_REL = "level4/closure_proofs/p5y_k1_sr_production_authorized_successor"\n',
                          'PARENT_NS_REL = "level4/closure_proofs/p5y_k1_ps1_production"\n')],
        # status DISPLAY/phase constants of the historical campaign (accounting never used them): bound to the contract
        "prodctl.py": [('            "cap_cpu_h": 4500.0, "headroom_cpu_h": cap["headroom_cpu_h"] if cap else None,\n',
                        '            "cap_cpu_h": contract["parent"]["global_cpu_cap"], "headroom_cpu_h": cap["headroom_cpu_h"] if cap else None,\n'),
                       ('    elif role == "VULTR" and len((st or {}).get("remote_completed_cells", {})) != 247:\n',
                        '    elif role == "VULTR" and len((st or {}).get("remote_completed_cells", {})) != contract["parent"]["aws_cells"]:\n')]}
OPS = ("ledger_ops.py", "locks.py", "opscommon.py", "prodctl.py", "produce_entry.py", "runtime_state.py", "supervisor.py")


def build() -> dict:
    out = {}
    for f in OPS:
        s = (SRC / "ops" / f).read_text()
        for a, b in SUBS.get(f, []):
            assert s.count(a) == 1, (f, a)
            s = s.replace(a, b)
        out[f"ops/{f}"] = s
    ex = (SRC / "config/RUNTIME_STATE_EXCLUDE").read_text()
    n_ns = ex.count(f"/level4/closure_proofs/{OLD_NS}/production/")
    assert n_ns == 5, n_ns
    ex = ex.replace(f"/level4/closure_proofs/{OLD_NS}/production/", f"/level4/closure_proofs/{NEW_NS}/production/")
    gov = "(governed by p5y_k1_sr_production_lifecycle_successor/config/RUNTIME_STATE_EXCLUDE)"
    assert ex.count(gov) == 1
    ex = ex.replace(gov, "(governed by p5y_k1_ps1_lifecycle_adapter/config/RUNTIME_STATE_EXCLUDE)")
    assert ex.startswith("# BEGIN rebaseguard p5y_k1_sr production runtime state")
    out["config/RUNTIME_STATE_EXCLUDE"] = ex
    return out


if __name__ == "__main__":
    for rel, text in build().items():
        (NS / rel).parent.mkdir(parents=True, exist_ok=True)
        (NS / rel).write_text(text)
    print("generated", len(build()), "files")
