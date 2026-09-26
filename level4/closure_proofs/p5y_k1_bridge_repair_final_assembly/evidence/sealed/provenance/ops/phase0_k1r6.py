"""K1R6 Phase 0: frozen admission checks only. No science, no writes. Runs OUTSIDE the repository roots."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
WT = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1")
NS = WT / "level4/closure_proofs/p5y_k1r6_cusum_bridge_repair"
CFG = NS / "config"
REPO = Path("/home/ubuntu/work/ReBaseGuard")
AUX4 = REPO / "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
git = lambda *a: subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout.strip()
C = {}
def chk(n, ok, d=None): C[n] = {"ok": bool(ok), **({"detail": d} if d is not None else {})}
EV = [Path(p) for p in sys.argv[1:]]
chk("freeze_commit", git("rev-parse", "HEAD") == "3e9f3dcf8b98b23e41097aae2ec2f07484946a32")
chk("freeze_tag", git("rev-parse", "p5y-k1r6-cusum-bridge-repair-frozen^{commit}") == "3e9f3dcf8b98b23e41097aae2ec2f07484946a32")
chk("worktree_clean", git("status", "--porcelain") == "", git("status", "--porcelain")[:200])
chk("checkpoint", sha(CFG / "CHECKPOINT.json") == (CFG / "CHECKPOINT_HASH").read_text().strip() == "d519a2d26304a31a60ca71fc1f48f552c6c325fa3703640aea7dea8c1db56cb9")
sm = json.loads((CFG / "SOURCE_MANIFEST.json").read_text())["files"]
bad = [f for f, h in sm.items() if sha(NS / f) != h]
chk("source_manifest", sha(CFG / "SOURCE_MANIFEST.json") == (CFG / "SOURCE_MANIFEST_HASH").read_text().strip() == "73ceb9d5514934aada4cdcd50dc19fe4a0b9f3080982c3e629f84c13d4a71024" and not bad, {"files": len(sm), "drift": bad})
ident = json.loads((CFG / "PRODUCER_IDENTITY.json").read_text())
man = json.loads((CFG / "PRODUCER_MANIFEST.json").read_text())
mbad = [f for f, h in man["files"].items() if sha(f) != h]
chk("producer_identity", ident["producer"] == "K1R6-CUSUM-BRIDGE-REPAIR-PRODUCER" and ident["producer_identity_hash"] == "3527b3b9399c12b406217c72548264293f11b8f14f1250f5cede138e7ba84671" and ident["producer_manifest_hash"] == sha(CFG / "PRODUCER_MANIFEST.json"))
chk("producer_manifest_69", len(man["files"]) == 69 and not mbad, {"drift": mbad})
tbl = NS.parent / "p5y_k1r4_bridge_successor/config/CUSUM_BRIDGE_CELL_TABLE.json"
chk("bridge_table_pin", sha(tbl) == "db02a798b57e6317bcdbdd6bc40b7ac9ae31e2e966f0ba303cec12df8f54ab90")
aux = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())["files"]
abad = [f for f, h in aux.items() if sha(REPO / f) != h]
chk("aux4_kernel_58", len(aux) == 58 and not abad, {"drift": abad})
cp = json.loads((CFG / "CHECKPOINT.json").read_text())
sbad = [n for n, h in cp["stages"].items() if sha(NS / "driver" / n) != h]
chk("generated_modules_frozen", len(cp["stages"]) == 6 and not sbad, {"drift": sbad})
r = subprocess.run([sys.executable, str(NS / "code/make_k1r6_stages.py"), "--check"], capture_output=True, text=True)
chk("generation_reproduces", r.returncode == 0, r.stdout.strip()[:120])
code = """
import sys, json, os
sys.path.insert(0, %r)
import k1r6_cusum_entry as E, k1r6_bridge_resolver as RES
out = {"tcb": E.verify_tcb("phase0"), "binding": E.verify_k1r6_modules(), "indices": list(E.BRIDGE_INDICES),
       "bits": E.spec.PRODUCTION_BITS, "cells": {}}
for i in E.BRIDGE_INDICES:
    c = E.bridge_cell(i)
    out["cells"][i] = {"resolver_equal": RES.resolve("CUSUM", i) == c, **{k: c[k][0] for k in ("left", "right", "e0", "rho")}, "C_upper": c["C_upper"]}
out["threads"] = {v: os.environ.get(v) for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","BLIS_NUM_THREADS","VECLIB_MAXIMUM_THREADS","K1_THREADS_PINNED")}
import flint; out["flint"] = flint.__version__; out["python"] = sys.executable
print(json.dumps(out))
""" % str(NS / "driver")
p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=600)
try:
    o = json.loads(p.stdout.strip().splitlines()[-1])
except Exception:
    o = {"error": p.stderr[-400:]}
cells = o.get("cells", {})
geom = (cells.get("1000", {}).get("left") == "11/2" and cells.get("1001", {}).get("right") == "49750555/8388608"
        and cells.get("1000", {}).get("right") == cells.get("1001", {}).get("left") and len(cells) == 2
        and all(c.get("resolver_equal") for c in cells.values()))
chk("module_binding_and_tcb", "binding" in o and o["binding"].get("k1r6_modules") == 5, o.get("tcb", o.get("error")))
chk("bridge_indices_exact", o.get("indices") == [1000, 1001] and o.get("bits") == 256)
chk("bridge_geometry_schema", geom, cells)
chk("thread_contract", len(o.get("threads", {})) == 7 and all(v == "1" for v in o.get("threads", {}).values()), o.get("threads"))
vendor = Path("/sys/class/dmi/id/sys_vendor").read_text().strip()
chk("aws_runtime", vendor == "Amazon EC2" and o.get("python") == "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python" and o.get("flint") == "0.9.0", {"vendor": vendor, "flint": o.get("flint")})
chk("fresh_evidence_destinations", bool(EV) and all(not e.exists() for e in EV) and all("run-20260926T075918Z" not in str(e) for e in EV), [str(e) for e in EV])
run = Path("/home/ubuntu/work/k1-bridge-prod/run-20260926T075918Z/logs")
pids = [json.loads((run / f"SR_{c}.launch.json").read_text())["pid"] for c in range(2000, 2006)]
alive = [pp for pp in pids if Path(f"/proc/{pp}").exists() and "k1r4_bridge_worker" in Path(f"/proc/{pp}/cmdline").read_text()]
chk("sr_six_pids_alive_untouched", len(alive) == 6, {"pids": pids, "alive": len(alive)})
print(json.dumps({"ALL_OK": all(v["ok"] for v in C.values()), "checks": C}, indent=1, default=str))
