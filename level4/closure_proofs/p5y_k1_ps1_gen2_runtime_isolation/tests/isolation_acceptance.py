"""REAL transient-systemd acceptance for the generation-2 RUNTIME ISOLATION successor.

Real: PS1 preflight + fresh-interpreter probe, ps1_cellseq_launcher, pinned pool, transient
systemd unit, supervisor, frozen ledger, campaign lock, reservations, per-cell durable markers,
drain, reconciliation, checkpoint/export/resume. Synthetic: only the science (per-cell spins).
Runs in throwaway clones under SYNTHETIC_CONTROL contracts; no genuine production path is used.

The frozen authorization is made to name a DECOY legacy root (as the genuine PS1 authorization
names the generation-1 root) and the harness never aligns paths, so every isolation property is
decided by the ops under test. NEGATIVE CONTROL: the same scenarios under the unrepaired
generation-2 recovery ops must reproduce the defect.

  python isolation_acceptance.py <scenario...|all|negative> --work DIR --clone-src REPO
         --python PY --cores 2,4
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPAIRED_OPS = NS
UNREPAIRED_OPS = NS.parent / "p5y_k1_ps1_portable_recovery"
ENTRY = NS / "tests" / "synthetic_isolation_entry.py"
SEALED_REL = "level4/closure_proofs/p5y_k1_ps1_production/production/cells"
A = argparse.Namespace()


def sh(*a, **kw):
    return subprocess.run([str(x) for x in a], capture_output=True, text=True, **kw)


def prodctl(ops, ct, *args):
    r = sh(A.python, Path(ops) / "ops" / "prodctl.py", *args, "--contract", ct)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {"_rc": r.returncode, "_err": r.stderr[-600:]}
    except ValueError:
        return {"_rc": r.returncode, "_stdout": r.stdout[-800:], "_err": r.stderr[-400:]}


class Case:
    def __init__(self, name, ops, control):
        self.name, self.ops = name, Path(ops)
        self.work = Path(A.work) / name
        if self.work.exists():
            shutil.rmtree(self.work)
        self.work.mkdir(parents=True)
        self.decoy = self.work / "legacy-gen1-runtime"
        self.rt = self.work / "runtime-AWS"
        control = dict(control, cores=A.cores, decoy_work_dir=str(self.decoy / "work"),
                       decoy_evidence_dir=str(self.decoy / "evidence"))
        self.ctl = self.work / "control.json"
        self.ctl.write_text(json.dumps(control))
        self.root = self.clone()
        self.ct = self.contract()

    def clone(self):
        dest = self.work / "clone"
        head = sh("git", "-C", A.clone_src, "rev-parse", "HEAD").stdout.strip()
        sh("git", "clone", "-q", "--local", "--no-checkout", A.clone_src, dest)
        sh("git", "-C", dest, "-c", "advice.detachedHead=false", "checkout", "-q", "--detach", head)
        r = sh(A.python, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import runtime_state as RS; "
               "print(RS.install_git_policy(sys.argv[2]))", self.ops / "ops", dest)
        if r.returncode != 0:
            raise SystemExit(f"policy install failed: {r.stderr[-400:]}")
        return dest

    def contract(self):
        c = json.loads((self.ops / "config/OPERATIONAL_CONTRACT.json").read_text())
        c["mode"] = "SYNTHETIC_CONTROL"
        head = sh("git", "-C", self.root, "rev-parse", "HEAD").stdout.strip()
        c["parent"]["predecessor_commit"], c["parent"]["commit"], c["parent"]["tag"] = c["parent"]["commit"], head, head
        c["accounting"]["poll_interval_s"] = 0.5
        c["service"]["unit_prefix"] = f"rbg-iso-{self.name.lower()}-"
        c["parent"]["workers"]["AWS"] = len(A.cores)
        c["execution_generation"]["predecessor_production_root"] = str(self.work / "absent-gen1-prod")
        for role, spec in c["hosts"].items():
            spec.update({"production_root": str(self.root if role == "AWS" else self.work / f"absent-{role}"),
                         "ops_root": str(self.ops), "python": A.python, "runtime_dir": str(self.rt if role == "AWS"
                                                                                          else self.work / f"rt-{role}"),
                         "online_cpus": os.cpu_count(), "launch_prefix": [], "user": "root"})
            env = c["service"]["environment"][role]
            env.update({"RBG_SYNTH_CONTROL": str(self.ctl), "RBG_OPS_ROOT": str(self.ops), "HOME": "/root"})
        if "runtime_isolation" in c:
            c["runtime_isolation"]["legacy_bound_roots"] = {"AWS": {"work_dirs": [str(self.decoy / "work")],
                                                                    "evidence_dirs": [str(self.decoy / "evidence")]}}
        c["synthetic"] = {"entry": str(ENTRY), "service_mode": True,
                          "boot_id_file": str(self.work / "boot_id"), "boot_time_file": str(self.work / "boot_time"),
                          "disable_stop_post_settle_file": str(self.work / "DISABLE_STOP_POST")}
        (self.work / "boot_id").write_text("iso-boot-1\n")
        (self.work / "boot_time").write_text("0\n")
        p = self.work / "synthetic_contract.json"
        p.write_text(json.dumps(c, indent=1, sort_keys=True))
        return p

    def pc(self, *args):
        return prodctl(self.ops, self.ct, *args, "--role", "AWS")

    def sealed(self):
        d = self.root / SEALED_REL
        return sorted(int(p.stem) for p in d.glob("[0-9]*.json")) if d.exists() else []

    def status(self):
        return self.pc("status")

    def wait_idle(self, timeout=300):
        t_end = time.monotonic() + timeout
        st = self.status()
        while time.monotonic() < t_end and st.get("campaign_lock") == "LIVE":
            time.sleep(2.0)
            st = self.status()
        return st

    def wait_sealed(self, n, timeout=180):
        t_end = time.monotonic() + timeout
        while time.monotonic() < t_end and len(self.sealed()) < n:
            time.sleep(1.0)
        return self.sealed()

    def runs(self):
        d = self.rt / "runs"
        return [json.loads(f.read_text()) for f in sorted(d.glob("*.json"))] if d.exists() else []

    def decoy_files(self):
        return sorted(str(p.relative_to(self.decoy)) for p in self.decoy.rglob("*") if p.is_file()) \
            if self.decoy.exists() else []

    def gen_markers(self):
        ev = self.rt / "evidence"
        return sorted(int(p.stem.split("_")[-1]) for p in ev.rglob("cell_done_*.json")) if ev.exists() else []

    def unit(self):
        own = self.rt / "campaign.owner.json"
        return json.loads(own.read_text()).get("unit") if own.exists() else None


def report(name, ok, detail):
    print("=" * 72)
    print(f"{name}: {'PASS' if all(ok.values()) else 'FAIL'}")
    for k, v in ok.items():
        print(f"    {'PASS' if v else 'FAIL'}  {k}")
    print("    detail: " + json.dumps(detail, default=str)[:1500])
    return all(ok.values()), {"checks": ok, "detail": detail}


def iso_checks(c):
    return {"decoy_legacy_root_untouched": c.decoy_files() == [],
            "markers_under_generation_evidence_root": bool(c.gen_markers())}


# --------------------------------------------------------------- scenarios (repaired ops)
def s_drain():
    c = Case("DRAIN", REPAIRED_OPS, {"spin_s": 3.0, "cells": list(range(24))})
    (c.decoy / "work").mkdir(parents=True)
    (c.decoy / "work" / "DRAIN").write_text('{"foreign": "legacy generation flag"}')   # must be ignored
    st0 = c.pc("start")
    before = c.wait_sealed(2)
    dr = c.pc("drain", "--wait", "150")
    fin = c.wait_idle()
    after = c.sealed()
    c.decoy.joinpath("work", "DRAIN").unlink()                     # remove the planted foreign flag
    refused = c.pc("start")
    time.sleep(6)
    refused_rec = [r for r in c.runs() if r.get("status") == "REFUSED"]
    cleared = c.pc("clear-drain")
    c.pc("start")
    time.sleep(10)
    final = c.wait_idle(timeout=400)
    allc = c.sealed()
    ok = {"foreign_legacy_drain_did_not_stop_admission": len(before) >= 2,
          "prodctl_drain_honoured_and_settled": dr.get("settled") is True,
          "drain_flag_is_generation_flag": dr.get("flag") == dr.get("launcher_polls") == str(c.rt / "work/DRAIN"),
          "drain_stopped_admission": len(after) < 24,
          "no_torn_from_drain": not fin.get("torn_attempts"),
          "zero_open_reservations_after_drain": fin.get("open_reservations") == [],
          "stale_drain_flag_refuses_restart": any("STALE_DRAIN_FLAG" in (r.get("reason") or "") for r in refused_rec),
          "clear_drain_archives_flag": cleared.get("cleared") is True and Path(cleared.get("archived", "/x")).exists(),
          "resume_after_drain_completes_all": allc == list(range(24)),
          "no_duplicate_seal": len(allc) == len(set(allc)),
          "final_lock_free_no_reservations": final.get("campaign_lock") == "FREE" and final.get("open_reservations") == [],
          **iso_checks(c)}
    return report("DRAIN", ok, {"before": before, "after": after, "final": allc, "start": st0.get("unit"),
                                "torn": final.get("torn_attempts"), "decoy": c.decoy_files()[:5]})


def s_sigterm():
    c = Case("SIGTERM", REPAIRED_OPS, {"spin_s": 4.0, "cells": list(range(8))})
    c.pc("start")
    before = c.wait_sealed(2)
    stop = c.pc("stop")
    st = c.wait_idle()
    mid = c.sealed()
    markers_mid = c.gen_markers()
    rec = c.runs()[-1] if c.runs() else {}
    c.pc("start")
    time.sleep(10)
    fin = c.wait_idle(timeout=400)
    allc = c.sealed()
    ok = {"stop_sent": bool(stop.get("stopped")),
          # systemctl stop delivers SIGTERM to the whole control group (KillMode=control-group):
          # either the supervisor sees it first, or its child launcher dies of it first
          "run_ended_on_sigterm": any(x in str(rec.get("reason")) for x in ("STOP_SIGNAL_SIGTERM", "CHILD_EXIT_-15")),
          "every_durable_marker_finalized": set(markers_mid) <= set(mid),
          "sealed_before_stop_preserved": set(before) <= set(mid),
          "settled_no_open_reservations": st.get("open_reservations") == [] and st.get("unsettled_runs") == [],
          "not_halted": st.get("halt") is None,
          "tears_bounded": all(v <= 1 for v in (st.get("torn_attempts") or {}).values()),
          "restart_completes_all": allc == list(range(8)),
          "no_duplicate_seal": len(allc) == len(set(allc)),
          "final_lock_free": fin.get("campaign_lock") == "FREE" and fin.get("open_reservations") == [],
          **iso_checks(c)}
    return report("SIGTERM", ok, {"before": before, "mid": mid, "markers_mid": markers_mid,
                                  "reason": rec.get("reason"), "recon": rec.get("reconciliation"),
                                  "torn": st.get("torn_attempts"), "final": allc})


def s_sigkill_after_marker():
    c = Case("SIGKILL_AFTER_MARKER", REPAIRED_OPS, {"spin_s": 2.0, "cells": [0, 1, 2, 3],
                                                    "kill_launcher_after_cell": 1})
    c.pc("start")
    st = c.wait_idle()
    rec = c.runs()[-1] if c.runs() else {}
    after = c.sealed()
    recon = rec.get("reconciliation") or {}
    ok = {"launcher_sigkilled": "CHILD_EXIT_-9" in str(rec.get("reason")),
          "cell0_finalized": 0 in after,
          "cell1_finalized_from_durable_marker": 1 in after and 1 in (recon.get("finalized") or []),
          "reconciliation_scanned_generation_root": str(c.rt / "evidence") in (recon.get("marker_roots") or []),
          "cells_2_3_not_finalized": 2 not in after and 3 not in after,
          "no_torn_for_finalized": all(str(x) not in (st.get("torn_attempts") or {}) for x in after),
          "lock_free_zero_reservations": st.get("campaign_lock") == "FREE" and st.get("open_reservations") == [],
          **iso_checks(c)}
    return report("SIGKILL_AFTER_MARKER", ok, {"after": after, "recon": recon, "reason": rec.get("reason")})


def s_sigkill_before_marker():
    c = Case("SIGKILL_BEFORE_MARKER", REPAIRED_OPS, {"spin_s": 2.0, "cells": [0, 1, 2, 3],
                                                     "kill_launcher_before_cell": 1})
    c.pc("start")
    st = c.wait_idle()
    after = c.sealed()
    ok = {"cell0_finalized": 0 in after, "cell1_not_finalized_without_marker": 1 not in after,
          "no_false_finalization": set(after) <= {0},
          "lock_free_zero_reservations": st.get("campaign_lock") == "FREE" and st.get("open_reservations") == [],
          "decoy_legacy_root_untouched": c.decoy_files() == []}
    return report("SIGKILL_BEFORE_MARKER", ok, {"after": after, "torn": st.get("torn_attempts")})


def s_worker_loss():
    c = Case("WORKER_LOSS", REPAIRED_OPS, {"spin_s": 2.0, "cells": [0, 1, 2, 3], "die": {"2": [1]}})
    c.pc("start")
    st = c.wait_idle()
    if st.get("open_reservations"):
        c.pc("recover")
        st = c.status()
    rec = c.runs()[-1] if c.runs() else {}
    mid = c.sealed()
    c.pc("start")
    time.sleep(10)
    fin = c.wait_idle()
    allc = c.sealed()
    ok = {"worker_loss_detected": "WORKER_LOST" in str(rec.get("reason")) or "CHILD_EXIT" in str(rec.get("reason")),
          "cells_0_1_finalized": mid[:2] == [0, 1],
          "cell_2_torn_not_finalized": 2 not in mid and "2" in (st.get("torn_attempts") or {}),
          "not_halted_retry_eligible": st.get("halt") is None,
          "restart_completes_all": allc == [0, 1, 2, 3],
          "no_duplicate_seal": len(allc) == len(set(allc)),
          "final_lock_free": fin.get("campaign_lock") == "FREE" and fin.get("open_reservations") == [],
          **iso_checks(c)}
    return report("WORKER_LOSS", ok, {"reason": rec.get("reason"), "mid": mid, "torn": st.get("torn_attempts"),
                                      "final": allc, "final_torn": fin.get("torn_attempts")})


def s_supervisor_restart():
    c = Case("SUPERVISOR_RESTART", REPAIRED_OPS, {"spin_s": 4.0, "cells": list(range(8))})
    c.pc("start")
    before = c.wait_sealed(2)
    unit = c.unit()
    (c.work / "DISABLE_STOP_POST").write_text("harness: leave the run unsettled\n")
    sh("systemctl", "kill", "--signal=SIGKILL", "--kill-whom=main", unit)
    t_end = time.monotonic() + 240
    while time.monotonic() < t_end and sh("systemctl", "is-active", unit).stdout.strip() in ("active", "deactivating"):
        time.sleep(1.0)
    stale = c.status()
    markers = c.gen_markers()
    sealed_at_kill = c.sealed()
    (c.work / "DISABLE_STOP_POST").unlink()
    c.pc("start")
    time.sleep(10)
    fin = c.wait_idle(timeout=400)
    allc = c.sealed()
    runs = c.runs()
    killed = [r for r in runs if r.get("unit") == unit]
    later = [r for r in runs if r.get("unit") != unit and r.get("status") != "REFUSED"]
    settlement_kinds = [s.get("evidence") for s in ((json.loads((c.root / SEALED_REL).parent.joinpath(
        "PRODUCTION_LEDGER.json").read_text()).get("operational_lifecycle") or {}).get("settlements") or [])]
    ok = {"supervisor_killed_run_left_unsettled": bool(stale.get("unsettled_runs")),
          "stale_reservations_visible": bool(stale.get("open_reservations")),
          "campaign_lock_not_stale": stale.get("campaign_lock") == "FREE",
          "restart_settles_with_persisted_evidence": any(k in ("JOURNAL", "TAIL_BOUND_NOW", "TAIL_BOUND_REBOOT")
                                                        for k in settlement_kinds),
          "durable_markers_of_killed_run_finalized_or_absent": set(markers) <= set(allc),
          "prestart_reconciliation_recorded": bool(later and later[0].get("prestart_reconciliation")),
          "restart_completes_all": allc == list(range(8)),
          "no_duplicate_seal": len(allc) == len(set(allc)),
          "no_halt": fin.get("halt") is None,
          "final_lock_free_no_reservations": fin.get("campaign_lock") == "FREE" and fin.get("open_reservations") == [],
          **iso_checks(c)}
    return report("SUPERVISOR_RESTART", ok, {"before": before, "sealed_at_kill": sealed_at_kill, "markers": markers,
                                             "stale": {k: stale.get(k) for k in ("phase", "unsettled_runs", "open_reservations")},
                                             "settlements": settlement_kinds, "killed_runs": len(killed),
                                             "prestart_recon": later[0].get("prestart_reconciliation") if later else None,
                                             "final": allc, "torn": fin.get("torn_attempts")})


def _marker_crash(name, stop_post_enabled):
    """Deterministic durable-marker crash: freeze the launcher (it can no longer reap), wait for a
    worker to make a cell's marker durable, then SIGKILL the supervisor. The cell must be
    finalized by crash recovery (ExecStopPost settle-fallback, or pre-start of the next run)."""
    c = Case(name, REPAIRED_OPS, {"spin_s": 3.0, "cells": list(range(8))})
    c.pc("start")
    c.wait_sealed(1)
    unit = c.unit()
    run = [r for r in c.runs() if r.get("unit") == unit][-1]
    launcher = int(run["child_pid"])
    sealed_before = c.sealed()
    os.kill(launcher, 19)                                          # SIGSTOP: no further live reaping
    t_end = time.monotonic() + 60
    while time.monotonic() < t_end and not (set(c.gen_markers()) - set(c.sealed())):
        time.sleep(0.2)
    pending_markers = sorted(set(c.gen_markers()) - set(c.sealed()))
    if not stop_post_enabled:
        (c.work / "DISABLE_STOP_POST").write_text("harness\n")
    sh("systemctl", "kill", "--signal=SIGKILL", "--kill-whom=main", unit)
    t_end = time.monotonic() + 240
    while time.monotonic() < t_end and sh("systemctl", "is-active", unit).stdout.strip() in ("active", "deactivating"):
        time.sleep(1.0)
    after_crash = c.sealed()
    killed_rec = [r for r in c.runs() if r.get("unit") == unit][-1]
    if not stop_post_enabled:
        (c.work / "DISABLE_STOP_POST").unlink()
    c.pc("start")
    time.sleep(10)
    fin = c.wait_idle(timeout=400)
    allc = c.sealed()
    later = [r for r in c.runs() if r.get("unit") != unit and r.get("status") != "REFUSED"]
    recon = (killed_rec.get("reconciliation_stop_post") if stop_post_enabled
             else (later[0].get("prestart_reconciliation") or {}).get(run["run_id"]) if later else None) or {}
    torn = fin.get("torn_attempts") or {}
    ok = {"a_durable_marker_was_unsealed_at_crash": bool(pending_markers),
          "crash_recovery_finalized_it": set(pending_markers) <= set(recon.get("finalized") or []),
          ("finalized_by_stop_post_before_restart" if stop_post_enabled else "unsealed_until_prestart"):
              (set(pending_markers) <= set(after_crash)) if stop_post_enabled
              else not (set(pending_markers) & set(after_crash)),
          "never_torn_for_recovered_cells": all(str(x) not in torn for x in pending_markers + sealed_before),
          "restart_completes_all": allc == list(range(8)),
          "no_duplicate_seal": len(allc) == len(set(allc)),
          "final_lock_free_no_reservations": fin.get("campaign_lock") == "FREE" and fin.get("open_reservations") == [],
          **iso_checks(c)}
    return report(name, ok, {"sealed_before": sealed_before, "pending_markers": pending_markers,
                             "after_crash": after_crash, "recon": recon, "final": allc, "torn": torn})


def s_crash_prestart_reconcile():
    return _marker_crash("CRASH_PRESTART_RECONCILE", stop_post_enabled=False)


def s_crash_stoppost_reconcile():
    return _marker_crash("CRASH_STOPPOST_RECONCILE", stop_post_enabled=True)


def s_checkpoint_export_resume():
    c = Case("CHECKPOINT", REPAIRED_OPS, {"spin_s": 2.0, "cells": [0, 1, 2, 3]})
    c.pc("start")
    c.wait_idle()
    fin = c.sealed()
    cp = c.pc("checkpoint")
    ck = json.loads(Path(cp.get("checkpoint", "/nonexistent")).read_text()) if cp.get("checkpoint") else {}
    ex = c.pc("export", "--output", str(c.work / "bundle_out"))
    rep = ex.get("export") or {}
    fresh = c.work / "fresh_bundle"
    if Path(rep.get("bundle_dir", "/nonexistent")).exists():
        shutil.copytree(rep["bundle_dir"], fresh)
    rs = c.pc("resume", "--checkpoint", str(fresh))
    res = {}
    for tag, mutate in (("corrupt_checkpoint", "ck"), ("tampered_evidence", "ev"), ("historical_cpu_reset", "acc")):
        b = c.work / tag
        shutil.copytree(fresh, b)
        if mutate == "ck":
            d = json.loads((b / "checkpoint.json").read_text())
            d["finalized_cells"] = d["finalized_cells"] + [999]
            (b / "checkpoint.json").write_text(json.dumps(d))
        elif mutate == "ev":
            victim = sorted(p for p in (b / "evidence").rglob("*") if p.is_file())[0]
            victim.write_bytes(b'{"tampered":true}\n')
        else:
            sys.path.insert(0, str(NS / "driver"))
            import ps1_checkpoint as CK
            d = json.loads((b / "checkpoint.json").read_text())
            d["accounting"]["historical_cpu_h"] = 0.0
            d["checkpoint_content_sha256"] = CK._content_hash(d)
            (b / "checkpoint.json").write_text(json.dumps(d))
        res[tag] = "REFUSED" in c.pc("resume", "--checkpoint", str(b))
    ok = {"checkpoint_created": bool(cp.get("sha256")),
          "domain_partition_369": (cp.get("finalized", 0) + cp.get("pending", 0)) == 369,
          "checkpoint_evidence_root_is_generation_root":
              (ck.get("evidence_manifest") or {}).get("root_at_build") == str(c.rt / "evidence"),
          "export_source_is_generation_root": ex.get("source_evidence_root") == str(c.rt / "evidence"),
          "bundle_verifies_in_clean_dir": rs.get("resume") == "VERIFIED_READY",
          "schedules_only_pending": rs.get("schedule_only_pending") == 369 - len(fin),
          "never_reschedules_finalized": rs.get("finalized_never_rescheduled") == len(fin),
          **{f"{k}_refused": v for k, v in res.items()},
          **iso_checks(c)}
    return report("CHECKPOINT_EXPORT_RESUME", ok, {"finalized": fin, "checkpoint": cp.get("sha256"),
                                                   "tar_sha256": rep.get("tar_sha256"), "resume": rs.get("resume")})


# ------------------------------------------------------- negative control (unrepaired ops)
def n_drain():
    c = Case("NEG_DRAIN", UNREPAIRED_OPS, {"spin_s": 3.0, "cells": list(range(80))})
    c.pc("start")
    before = c.wait_sealed(2)
    at_drain = len(c.sealed())
    dr = c.pc("drain", "--wait", "40")
    st = c.status()
    after_wait = len(c.sealed())
    c.pc("stop")
    c.wait_idle()
    # 2 workers x 4-cell groups: an HONOURED drain admits at most the 8 in-flight cells after the flag
    ok = {"DEFECT_prodctl_drain_not_honoured": dr.get("settled") is False and st.get("campaign_lock") == "LIVE"
                                               and after_wait - at_drain > 8,
          "DEFECT_launcher_wrote_into_authorization_bound_root": any("cell_done_" in f for f in c.decoy_files()),
          "DEFECT_generation_evidence_root_empty": c.gen_markers() == []}
    return report("NEGATIVE_CONTROL_DRAIN (unrepaired gen2 ops)", ok,
                  {"before": before, "flag": dr.get("flag"), "decoy_sample": c.decoy_files()[:4]})


def n_sigkill_after_marker():
    c = Case("NEG_SIGKILL", UNREPAIRED_OPS, {"spin_s": 2.0, "cells": [0, 1, 2, 3], "kill_launcher_after_cell": 1})
    c.pc("start")
    st = c.wait_idle()
    rec = c.runs()[-1] if c.runs() else {}
    after = c.sealed()
    decoy_markers = sorted(int(Path(f).stem.split("_")[-1]) for f in c.decoy_files() if "cell_done_" in f)
    ok = {"launcher_sigkilled": "CHILD_EXIT_-9" in str(rec.get("reason")),
          "DEFECT_durable_marker_for_cell1_exists_in_legacy_root": 1 in decoy_markers,
          "DEFECT_cell1_not_reconciled_torn_instead": 1 not in after and "1" in (st.get("torn_attempts") or {})}
    return report("NEGATIVE_CONTROL_SIGKILL (unrepaired gen2 ops)", ok,
                  {"after": after, "decoy_markers": decoy_markers, "torn": st.get("torn_attempts"),
                   "recon": rec.get("reconciliation")})


SCENARIOS = {"drain": s_drain, "sigterm": s_sigterm, "sigkill_after": s_sigkill_after_marker,
             "sigkill_before": s_sigkill_before_marker, "worker_loss": s_worker_loss,
             "supervisor_restart": s_supervisor_restart, "crash_prestart": s_crash_prestart_reconcile,
             "crash_stoppost": s_crash_stoppost_reconcile, "checkpoint": s_checkpoint_export_resume}
NEGATIVE = {"neg_drain": n_drain, "neg_sigkill": n_sigkill_after_marker}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenarios", nargs="+")
    ap.add_argument("--work", required=True)
    ap.add_argument("--clone-src", required=True)
    ap.add_argument("--python", required=True)
    ap.add_argument("--cores", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    A.__dict__.update(work=a.work, clone_src=a.clone_src, python=a.python,
                      cores=[int(x) for x in a.cores.split(",")])
    names = []
    for s in a.scenarios:
        names += list(SCENARIOS) if s == "all" else list(NEGATIVE) if s == "negative" else [s]
    results = {}
    for n in names:
        fn = SCENARIOS.get(n) or NEGATIVE[n]
        t0 = time.time()
        try:
            passed, detail = fn()
        except Exception as exc:                                   # noqa: BLE001
            passed, detail = False, {"exception": f"{type(exc).__name__}: {exc}"}
            print(f"{n}: EXCEPTION {exc}")
        results[n] = {"pass": passed, "wall_s": round(time.time() - t0, 1), **detail}
    out = {"schema": "rebaseguard.p5y.k1.ps1.gen2-runtime-isolation.live-acceptance.v1",
           "synthetic_only": True, "result_bearing": False, "host": os.uname().nodename,
           "clone_head": sh("git", "-C", a.clone_src, "rev-parse", "HEAD").stdout.strip(), "results": results}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print("=" * 72)
    print("LIVE ACCEPTANCE: " + "  ".join(f"{k}={'PASS' if v['pass'] else 'FAIL'}" for k, v in results.items()))
    return 0 if all(v["pass"] for v in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
