"""MB-S r1 tests: the child harness. Runs ONE driver action of a SANDBOX's driver with the synthetic evaluator, and
(optionally) a fault point (mbs308_state.FAULT, set in-process: the production CLI refuses when it is set).

    mbs308_child.py <sandbox root> <action> <spec json>

actions: execute | resume | recover | seal-only | close-indeterminate | status | classify | decoy-ckpt
spec: fault {point: {"at": k, "how": "exit"|"kill"}}, boot_uuid (the classifier's boot UUID input, a simulated
reboot), mbr1_git_dir, control_pass, mem_cap_mb, eval_cap_s, skip_not_evaluated, decoy {...}, ps_fail_pids (`ps`
readings fail for these pids: a planted reading failure, N-3).
The last stdout line is a JSON object {"rc": ..., ...}. The driver never evaluates cell 308 here.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    root, action, spec = Path(sys.argv[1]), sys.argv[2], json.loads(sys.argv[3])
    if spec.get("dump_after_s"):                    # debugging aid: all thread stacks to stderr after N seconds
        import faulthandler
        faulthandler.dump_traceback_later(float(spec["dump_after_s"]), exit=True)
    ns = root / "level4/closure_proofs/p5y_k5_cell308_mbs_r1"
    sys.path.insert(0, str(ns / "tests"))
    sys.path.insert(0, str(ns / "code"))
    import mbs308_driver as D
    import mbs308_state as STATE
    import mbs308_synth as SY
    D.QUALIFIED_WORKTREE = str(root)
    D.QUALIFIED_GIT_DIR = str(root / ".git")
    D.QUALIFIED_COMMON_DIR = str(root / ".git")
    D.MBR1_GIT_DIR = spec["mbr1_git_dir"]
    own = D.sha(D.HERE.read_bytes())
    boot = spec.get("boot_uuid")
    if spec.get("platform_override"):              # a simulated platform change (e.g. another OS build)
        real_readings = D.platform_readings
        D.platform_readings = lambda: dict(real_readings(), **spec["platform_override"])
    if spec.get("pin_override"):                   # R4: the frozen pin differs from this host (a planted reading)
        D.PLATFORM_PINS = dict(D.PLATFORM_PINS, **spec["pin_override"])
    if spec.get("tamper_after_import"):            # R4: a pinned file changes after the driver loaded it
        p = root / spec["tamper_after_import"]
        p.write_bytes(p.read_bytes() + b"\n# planted by the test\n")
    if spec.get("skip_clean"):                     # R4: isolate a later refusal from the (tested) clean-tree check
        D.check_clean = lambda: None
    if spec.get("ps_fail_pids"):                   # N-3: `ps` fails for these pids (a planted reading failure)
        bad = {int(p) for p in spec["ps_fail_pids"]}
        real_start, real_cmd = D.HOST.process_start, D.HOST.process_command_sha256
        D.HOST.process_start = lambda pid, text=None: None if int(pid) in bad else real_start(pid, text)
        D.HOST.process_command_sha256 = lambda pid, text=None: None if int(pid) in bad else real_cmd(pid, text)
    if action == "platform":
        print(json.dumps({"rc": 0, "platform": D.platform_readings()}))
        return 0
    if action == "host_gates":                     # R4: the driver's own start gates on planted readings
        planted = json.loads(json.dumps(spec.get("planted") or {}).replace("{SELF}", str(os.getpid())))
        try:
            g = D.host_preflight(spec.get("launched", {"pass": True}), texts=planted)
            print(json.dumps({"rc": 0, "gates": g["gates"]}))
        except D.Refusal as e:
            print(json.dumps({"rc": 2, "refused": e.code, "detail": str(e)}))
        return 0
    if action == "status":
        print(D.run_status(boot_uuid=boot))
        return 0
    if action == "classify":
        print(json.dumps({"rc": 0, "classified": STATE.classify(D.campaign(), boot_uuid=boot,
                                                                  platform=D.platform_readings())}, default=str))
        return 0
    if action == "decoy-ckpt":
        return decoy_ckpt(D, STATE, root, spec, own)
    inj = SY.install(D, spec)
    if spec.get("skip_not_evaluated"):
        D.check_not_evaluated = lambda: {"stale_intent_journal": None}
    STATE.FAULT = spec.get("fault")
    try:
        if action == "execute":
            rc = D.run_execute(own, prepare=inj["prepare"], evaluator=inj["evaluator"])
        elif action == "resume":
            rc = D.run_resume(own, prepare=inj["prepare"], evaluator=inj["evaluator"], boot_uuid=boot)
        elif action == "recover":
            rc = D.run_recover(own, prepare=inj["prepare"], evaluator=inj["evaluator"], boot_uuid=boot)
        elif action == "seal-only":
            rc = D.run_seal_only(boot_uuid=boot)
        elif action == "close-indeterminate":
            rc = D.run_close_indeterminate(own, boot_uuid=boot)
        else:
            raise SystemExit(f"unknown action {action}")
        print(json.dumps({"rc": rc}))
        return 0
    except STATE.LostOwnership:
        print(json.dumps({"rc": 9, "lost_ownership": True}))
        return 0
    except (D.Refusal, STATE.StateError) as e:
        print(json.dumps({"rc": 2, "refused": getattr(e, "code", str(e))}))
        print(json.dumps({"rc": 2, "refused": getattr(e, "code", str(e)), "detail": str(e)[:300]}),
              file=sys.stderr)
        return 0


def decoy_ckpt(D, STATE, root: Path, spec: dict, own: str) -> int:
    """The dev decoy through the checkpoint path (test hook only): cell 297, first block, dev ladder, 2 workers;
    checkpoints go to a sandbox-only ref; a fault may kill it after k checkpoints; a second call resumes from the
    verified checkpoints. Writes the decoy output to spec["out"]."""
    d = spec["decoy"]
    st = D.store()
    ck = STATE.Checkpointer(st, None, "DECOY-NOT-A-GRANT", own, ref="refs/mbs308-test-decoy/ckpt",
                            attempt=2 if d.get("resume") else 1, attempt_seq=0, platform=D.platform_readings())
    good, bad = ck.verified_records(attempts={1: 0}) if d.get("resume") else ({}, [])
    STATE.FAULT = spec.get("fault")
    STATE.CK = ctx = STATE.Ctx(checkpointer=ck, verified=good, mem_cap_bytes=D.MEM_CAP_BYTES, mem_poll_s=D.MEM_POLL_S)
    D.check_bindings(allow_uncommitted=True)
    try:
        out = D.decoy(297, own, 2, 1, True)
    finally:
        STATE.CK = None
    out["lifecycle"] = {"stage1_context": ctx.summary(), "resumed_from": len(good), "rejected": bad}
    Path(d["out"]).write_text(json.dumps(D.jsonable(out), indent=1, sort_keys=True) + "\n")
    print(json.dumps({"rc": 0, "served": len(ctx.served), "computed": len(ctx.submitted)}))
    return 0


if __name__ == "__main__":
    _rc = main()                     # the driver CLI's own hard exit (see mbs308_driver.__main__), mirrored here
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(_rc)
