"""K1R preflight: cheap, read-only, NEVER consumes a decisive bridge result."""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2")
PS1 = PROD / "level4/closure_proofs/p5y_k1_ps1_production"
K1 = Path("/home/ubuntu/work/ReBaseGuard/level4/closure_proofs/p5y_k1_final_completion")
OUT = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rec(name, ok, detail=""):
    OUT.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" -- {detail}" if detail else ""))


def main() -> int:
    cp = json.loads((CFG / "CHECKPOINT.json").read_text())
    rec("checkpoint hash file matches",
        sha(CFG / "CHECKPOINT.json") == (CFG / "CHECKPOINT_HASH").read_text().strip())
    rec("frozen artifacts bound by the checkpoint",
        all(sha(CFG / n) == h for n, h in cp["frozen_artifacts"].items()),
        f"{len(cp['frozen_artifacts'])} artifacts")
    man_p = CFG / "SOURCE_MANIFEST.json"
    if man_p.exists():
        man = json.loads(man_p.read_text())["files"]
        drift = [f for f, h in man.items() if not (NS / f).exists() or sha(NS / f) != h]
        rec("successor source manifest clean", not drift, f"{len(man)} files, drift {drift}")
        rec("source manifest hash file matches",
            sha(man_p) == (CFG / "SOURCE_MANIFEST_HASH").read_text().strip())
    else:
        rec("successor source manifest present", False, "NOT FROZEN")

    # domain cover re-derived independently of the artifact
    d = json.loads((CFG / "DOMAIN_COVER.json").read_text())
    ok = True
    for det, c, close, n in (("CUSUM", Fr(11, 2), Fr(49750555, 8388608), 2),
                             ("SR", Fr(3803026123175981, 562949953421312),
                              Fr(1883835, 262144), 6)):
        s = d["detectors"][det]; kids = s["children"]
        w = (close - c) / n
        ok &= len(kids) == n
        ok &= all(Fr(k["lo"]["exact"]) == c + i * w and Fr(k["hi"]["exact"]) == c + (i + 1) * w
                  for i, k in enumerate(kids))
        ok &= Fr(s["segments"][0]["hi"]["exact"]) == c
        ok &= Fr(s["segments"][2]["lo"]["exact"]) == close
    rec("domain cover gap-free and endpoints recompose exactly", ok)
    rec("bridge cell counts fixed at 2 (CUSUM) and 6 (SR)",
        len(d["detectors"]["CUSUM"]["children"]) == 2
        and len(d["detectors"]["SR"]["children"]) == 6)

    # inherited identities that live on THIS host
    inh = cp["inherited_evidence"]
    local = {
        "PS1 production ledger": (PS1 / "production/PRODUCTION_LEDGER.json",
                                  inh["sr_ps1_campaign"]["production_ledger_sha256"]),
        "PS1 launch authorization": (PS1 / "config/LAUNCH_AUTHORIZATION.json",
                                     inh["sr_ps1_campaign"]["production_authorization_sha256"]),
        "PS1 shard manifest": (PS1 / "config/SHARD_MANIFEST.json",
                               inh["sr_ps1_campaign"]["shard_manifest_sha256"]),
        "far-field diagnostics": (K1 / "diagnostics/far_field.json",
                                  inh["far_field"]["diagnostics_sha256"]),
        "K1 self-audit": (K1 / "manifests/final_self_audit.json",
                          inh["far_field"]["k1_self_audit_sha256"]),
    }
    for name, (p, want) in local.items():
        rec(f"inherited identity resolves: {name}", p.exists() and sha(p) == want)

    # SR executor / runtime identity must be the qualified PS1 lineage
    auth = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    srp = json.loads((CFG / "SR_BRIDGE_PLAN.json").read_text())
    h = srp["host_runtime_contract"]
    exdrift = [f for f in auth["executor_source_manifest"]
               if not (PROD / f).exists() or sha(PROD / f) != auth["executor_source_sha256"][f]]
    rec("SR executor manifest matches the qualified lineage", not exdrift,
        f"{len(auth['executor_source_manifest'])} files")
    rec("SR adapter/producer/checkpoint identities match the authorization",
        h["scientific_adapter_hash"] == auth["scientific_adapter_hash"]
        and h["producer_commit"] == auth["producer_commit"]
        and h["checkpoint_sha256"] == auth["checkpoint_sha256"])
    rec("SR host contract is AWS-only, no Vultr substitution",
        h["host"] == "AWS ONLY" and h["vultr_permitted"] is False)

    b = json.loads((CFG / "B1_ADMISSION_CONTRACT.json").read_text())
    rec("B1 decision tree is result-independent",
        b["decision_is_outcome_independent"] and b["all_or_nothing"]
        and all(c["decidable_without_scientific_values"] for c in b["conditions"]),
        f"{len(b['conditions'])} conditions, 2 routes")
    rec("B1 Aux5 candidate identities are declared for remote resolution",
        all(k in b["candidate_source"] for k in
            ("export_manifest_sha256", "composite_audit_sha256", "producer_identity_hash")),
        "resolved on the CUSUM host at admission time, not here")

    cc = json.loads((CFG / "COST_CAP.json").read_text())
    rec("cost accounting initialises at zero NEW K1R compute",
        cc["consumed_new_cpu_h"] == 0.0 and cc["cap_cpu_h"] == 150.0)
    stray = [str(p.relative_to(NS)) for p in NS.rglob("*")
             if p.is_file() and ("evidence" in p.parts or "results" in p.parts)]
    rec("no production result exists in the successor namespace", not stray, str(stray[:3]))

    bad = [o for o in OUT if o["status"] != "PASS"]
    print(f"\n{len(OUT) - len(bad)}/{len(OUT)} preflight checks passed")
    print("K1R_PREFLIGHT = " + ("PASS" if not bad else "FAIL"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
