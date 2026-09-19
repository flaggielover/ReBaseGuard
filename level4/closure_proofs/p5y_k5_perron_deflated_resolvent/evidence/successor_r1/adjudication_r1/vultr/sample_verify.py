"""Adjudicator's seeded-sample Arb re-verification of registry_r1 artifacts (own driver; frozen verify functions)."""
import json, random, sys, time, hashlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
REPO = Path("/root/work/k5p-adjudication")
NS = REPO / "level4/closure_proofs/p5y_k5_perron_deflated_resolvent"
ART = NS / "evidence/registry_r1"
sys.path.insert(0, str(NS / "code"))
SEAL = "2e9b1585ec6f56b4a347d2aa00287b37cc3e1dd2"
MANDATORY = [11, 12, 40, 41, 80, 132, 133, 144, 148]

def sample():
    rng = random.Random(int(SEAL, 16))
    blocks = sorted(rng.sample(range(12), 3))
    extra = sorted(rng.sample([k for k in range(149) if k not in MANDATORY], 3))
    return blocks, sorted(MANDATORY + extra)

def one(name):
    import taboo_certify as TC
    t = time.time()
    raw = (ART / name).read_bytes()
    art = json.loads(raw)
    r = TC.verify_cell(art) if art["schema"] == TC.SCHEMA_CELL else TC.verify_block(art)
    return {"artifact": name, "sha256": hashlib.sha256(raw).hexdigest(), "identical": r["identical"],
            "certified": r["certified"], "recomputed": r["recomputed"], "wall": time.time() - t}

if __name__ == "__main__":
    blocks, cells = sample()
    names = [f"taboo_block_{i:02d}.json" for i in blocks]
    for k in cells:
        names += [f"arl_cell_{k:03d}.json", f"taboo_cell_{k:03d}.json"]
    print(json.dumps({"seed": SEAL, "blocks": blocks, "cells": cells, "n": len(names)}), flush=True)
    reg = json.loads((ART / "REGISTRY.json").read_text())
    want = {**{f"taboo_block_{int(i):02d}.json": b["artifact_sha256"] for i, b in reg["taboo_blocks"].items()},
            **{f"arl_cell_{b['cell']:03d}.json": b["arl_artifact_sha256"] for b in reg["blocks"]},
            **{f"taboo_cell_{b['cell']:03d}.json": b["taboo_cell_artifact_sha256"] for b in reg["blocks"]}}
    with ProcessPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as ex:
        res = list(ex.map(one, names))
    for r in res:
        r["registry_hash_match"] = (want[r["artifact"]] == r["sha256"])
        print(r["artifact"], r["identical"], r["certified"], r["registry_hash_match"], round(r["wall"], 1), flush=True)
    out = {"seed": SEAL, "blocks": blocks, "cells": cells, "results": res,
           "all_identical": all(r["identical"] for r in res), "all_certified": all(r["certified"] for r in res),
           "all_hash_match": all(r["registry_hash_match"] for r in res)}
    Path("/var/tmp/k5p-adj/SAMPLE_VERIFY.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("SUMMARY", out["all_identical"], out["all_certified"], out["all_hash_match"], flush=True)
