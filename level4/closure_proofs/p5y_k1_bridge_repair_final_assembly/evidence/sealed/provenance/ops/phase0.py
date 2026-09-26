"""Phase 0: frozen admission checks only. No scientific solve, no evidence written."""
import hashlib, json, os, sys, subprocess
from pathlib import Path
WT = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1")
CP = WT / "level4/closure_proofs"
R4, R5 = CP / "p5y_k1r4_bridge_successor", CP / "p5y_k1r5_cusum_entry"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
out = {"SR": {}, "CUSUM": {}}
def chk(side, name, ok, detail=None):
    out[side][name] = {"ok": bool(ok), **({"detail": detail} if detail is not None else {})}
git = lambda *a: subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout.strip()
which = sys.argv[1]
if which == "SR":
    chk("SR", "freeze_tag", git("rev-parse", "p5y-k1r4-bridge-successor-frozen^{commit}") == "d9e8f1185c04ee8beb339efff091a073e6ebc21d")
    chk("SR", "tree_equals_freeze", git("diff", "--stat", "d9e8f1185c04ee8beb339efff091a073e6ebc21d", "HEAD", "--", str(R4)) == "" and git("status", "--porcelain", "--", str(R4)) == "")
    chk("SR", "checkpoint", sha(R4/"config/CHECKPOINT.json") == (R4/"config/CHECKPOINT_HASH").read_text().strip() == "9091cb0d5db6cc0a8d233f1667bea78bc69be676b2672f2e47506c453d2a33f0")
    sm = json.loads((R4/"config/SOURCE_MANIFEST.json").read_text())
    bad = [f for f, h in sm["files"].items() if sha(R4/f) != h]
    chk("SR", "source_manifest", sha(R4/"config/SOURCE_MANIFEST.json") == (R4/"config/SOURCE_MANIFEST_HASH").read_text().strip() == "505b96015ef3afdda6046851f1a429709935c472bdf609f2e9163f8d0ca5cbb5" and not bad, {"files": len(sm["files"]), "drift": bad})
    cp = json.loads((R4/"config/CHECKPOINT.json").read_text())
    authz = json.loads((R4/"config/SR_BRIDGE_AUTHORIZATION.json").read_text())
    gs = [n for n, h in cp["generated_stages"].items() if sha(R4/"driver"/n) != h]
    chk("SR", "generated_stages", not gs and cp["generated_stages"] == authz["identity_body"]["generated_stages"], {"n": len(cp["generated_stages"]), "drift": gs})
    lld = authz["identity_body"].get("lower_level_dependencies", {})
    roots = [Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2"), WT, Path("/home/ubuntu/work/ReBaseGuard")]
    lbad = [f for f, h in lld.items() if not any((r/f).exists() and sha(r/f) == h for r in roots)]
    chk("SR", "lower_level_dependencies", not lbad, {"n": len(lld), "drift": lbad})
    chk("SR", "producer_identity", authz["producer_identity_sha256"] == cp["producer_identity_sha256"] == "6e3713468634fe9fc5952d65aa2fd13f548312e29c6c749e867c55e98abb47b1")
    chk("SR", "authorization", authz["authorization_id"] == "K1R4-SR-BRIDGE-AUTH-001" and authz["cells"] == [2000, 2001, 2002, 2003, 2004, 2005])
    sys.path.insert(0, str(R4/"driver"))
    import k1r4_bridge_worker as W
    adm = {}
    for i in authz["cells"]:
        a = W.admit(i)
        adm[i] = {"id": a["id"], "universe_units": a["universe_units"], "bridge_table_sha256": a["bridge_table_sha256"], "producer": a["producer_identity_sha256"], "host": a["host"]["sys_vendor"], "left": a["record"].get("left"), "right": a["record"].get("right")}
    chk("SR", "admit_6_cells", len(adm) == 6 and all(v["universe_units"] == 28 and v["bridge_table_sha256"] == authz["identity_body"]["bridge_table_sha256"] for v in adm.values()), adm)
    import k1r4_bridge_cellseq as CS
    p = CS.probe()
    chk("SR", "thread_contract_and_precision", p["thread_contract_ok"], p)
else:
    chk("CUSUM", "freeze_tag", git("rev-parse", "p5y-k1r5-cusum-entry-frozen^{commit}") == "0cd4e8dd36615971745eb37c00197d735723cc82" == git("rev-parse", "HEAD"))
    chk("CUSUM", "tree_clean", git("status", "--porcelain", "--", str(R5)) == "")
    chk("CUSUM", "checkpoint", sha(R5/"config/CHECKPOINT.json") == (R5/"config/CHECKPOINT_HASH").read_text().strip() == "8cc6e877d20dac618b24bf9b2eb66ce08c8d6cce58e3cfb9ba1dc0527056b215")
    sm = json.loads((R5/"config/SOURCE_MANIFEST.json").read_text())
    bad = [f for f, h in sm["files"].items() if sha(R5/f) != h]
    chk("CUSUM", "source_manifest", sha(R5/"config/SOURCE_MANIFEST.json") == (R5/"config/SOURCE_MANIFEST_HASH").read_text().strip() == "c3813ccf35f8ab6b966bc46b0f168af1a3c8c7c2e759f2f6fad3c61f9e851e91" and not bad, {"files": len(sm["files"]), "drift": bad})
    cp = json.loads((R5/"config/CHECKPOINT.json").read_text())
    fa = [n for n, h in cp["frozen_artifacts"].items() if sha(R5/"config"/n) != h]
    chk("CUSUM", "checkpoint_artifacts", not fa, {"n": len(cp["frozen_artifacts"]), "drift": fa})
    pm = json.loads((R5/"config/PRODUCER_MANIFEST.json").read_text())
    pbad = [f for f, h in pm["files"].items() if sha(f) != h]
    chk("CUSUM", "producer_manifest", not pbad and len(pm["files"]) == 59, {"files": len(pm["files"]), "drift": pbad})
    AUX4 = Path("/home/ubuntu/work/ReBaseGuard/level4/closure_proofs/p5y_k1_cusum_aux4_fullcover")
    am = AUX4/"manifests/producer_manifest_v2.json"
    aux = json.loads(am.read_text())
    af = aux["files"] if isinstance(aux.get("files"), dict) else {e["path"]: e["sha256"] for e in aux["files"]}
    def res(f): return Path(f) if Path(f).is_absolute() else Path("/home/ubuntu/work/ReBaseGuard")/f
    abad = [f for f, h in af.items() if sha(res(f)) != h]
    chk("CUSUM", "aux4_kernel_58", len(af) == 58 and not abad and sha(am) == pm["inherited_kernel"]["aux4_manifest_sha256"], {"n": len(af), "drift": abad})
    ident = json.loads((R5/"config/PRODUCER_IDENTITY.json").read_text())
    chk("CUSUM", "producer_identity", ident["producer_identity_hash"] == cp["producer_identity_hash"] == "8cdacbc70370621e931eaeb55a523e1ecd2e548bfaba63aa54ede9c63f28c111" and ident["producer_manifest_hash"] == sha(R5/"config/PRODUCER_MANIFEST.json"))
    sys.path.insert(0, str(R5/"driver"))
    import k1r5_cusum_entry as E
    cells = {i: E.bridge_cell(i) for i in (1000, 1001)}
    chk("CUSUM", "two_cell_table_affine_schema", sorted(cells) == [1000, 1001], {i: {k: c[k] for k in ("left", "right", "e0", "rho")} for i, c in cells.items()})
    chk("CUSUM", "producer_context", E.producer_context(256)["producer_identity_hash"] == ident["producer_identity_hash"])
    chk("CUSUM", "initial_tcb_gate", True, E.verify_tcb("initial"))
    chk("CUSUM", "thread_contract", os.environ.get("K1_THREADS_PINNED") == "1" and all(os.environ.get(v) == "1" for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","BLIS_NUM_THREADS","VECLIB_MAXIMUM_THREADS")) and E.spec.PRODUCTION_BITS == 256)
side = which
print(json.dumps({"side": side, "ALL_OK": all(v["ok"] for v in out[side].values()), "checks": out[side]}, indent=1, default=str))
