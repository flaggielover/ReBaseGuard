"""MB-S r1: the launchd launcher and the host contract (architecture sections 5, 6). A REAL launchd integration test with
a SYNTHETIC payload (never the driver's target path): a shell in its own session runs the launcher, which bootstraps a
transient LaunchAgent (unique label org.rebaseguard.mbs308.test.<utc>, plist in scratch, never ~/Library/LaunchAgents,
logs under ~/Library/Logs/ReBaseGuard/mbs308-test/); the test then KILLS the launching shell's process group AND every
process of its session (the "hosting app Force Quit" analogue) and asserts the job survives; kills the job's caffeinate
and asserts the supervisor re-spawns it; stops the job and asserts its pidfile is detected as stale; and ALWAYS boots
the job out and removes the plist, even on failure. Unit tests: PPID 1 is not detachment, the supervisor in-process,
the pidfile / identity rules, the preflight gates on planted readings, and the launcher's refusal of `execute` when the
driver's preflight fails (a read-only preflight of the successor driver).

    python3.14 -I -S -B test_mbs308_launch.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import datetime
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

TMP = T.SCRATCH / "t_launch"


def mods():
    sys.path.insert(0, str(T.code_dir()))
    import mbs308_host as H
    import mbs308_launch as L
    import mbs308_state as S
    return H, L, S


def read_json(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def wait_for(fn, timeout=20.0, every=0.2):
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = fn()
        if v:
            return v
        time.sleep(every)
    return None


def session_pids(sid: int) -> list:
    out = []
    ps = subprocess.run(["/bin/ps", "-A", "-o", "pid="], capture_output=True, text=True).stdout.split()
    for p in ps:
        try:
            if os.getsid(int(p)) == sid:
                out.append(int(p))
        except OSError:
            pass
    return out


def t_launchd_integration():
    H, L, S = mods()
    run = TMP / datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
    run.mkdir(parents=True)
    repo = run / "repo"
    subprocess.run(["/usr/bin/git", "init", "-q", str(repo)], check=True, env=T.GENV)
    label = "org.rebaseguard.mbs308.test." + run.name
    state, stop = run / "payload_state.json", run / "STOP"
    pargs = [str(T.code_dir()), str(repo), str(state), str(stop)]
    harness = T.NSS / "tests/mbs308_launch_harness.py"
    shell_cmd = f"'{T.PY}' -I -S -B '{harness}' '{T.code_dir()}' '{run}' '{label}' '{json.dumps(pargs)}'; sleep 600"
    res = {"label": label}
    shell = subprocess.Popen(["/bin/zsh", "-c", shell_cmd], start_new_session=True, stdin=subprocess.DEVNULL,
                             stdout=open(run / "shell.out", "w"), stderr=subprocess.STDOUT)
    try:
        rec = wait_for(lambda: read_json(run / "launch_record.json"), 30)
        res["launch_record"] = {k: rec.get(k) for k in ("pid", "ppid", "pgid", "sid", "uid", "boot_uuid", "refused")} \
            if rec else None
        if not rec or "refused" in rec:
            res["ok"] = False
            return res
        job = rec["pid"]
        res["detachment_by_launcher"] = rec["detachment"]
        st0 = wait_for(lambda: (read_json(state) or {}).get("caffeinate_pid") and read_json(state), 20)
        res["payload"] = {k: st0.get(k) for k in ("pid", "ppid", "sid", "xpc_service_name", "label",
                                                  "launched_by_launchd", "preferred_encoding")} if st0 else None
        # --- kill the launching shell's process group AND its whole session
        sid = os.getsid(shell.pid)
        pg = os.getpgid(shell.pid)
        members = session_pids(sid)
        os.killpg(pg, signal.SIGKILL)
        for p in members:
            try:
                os.kill(p, signal.SIGKILL)
            except OSError:
                pass
        shell.wait(timeout=10)
        time.sleep(2.0)
        left = session_pids(sid)
        hb1 = (read_json(state) or {}).get("heartbeat")
        time.sleep(1.5)
        hb2 = (read_json(state) or {}).get("heartbeat")
        res["session_killed"] = {"members_killed": len(members), "left": left}
        res["job_survives"] = H.pid_alive(job) and H.launchd_job_pid(label) == job and hb2 and hb1 and hb2 > hb1
        res["job_not_in_killed_session"] = os.getsid(job) != sid and job not in members
        # --- kill the job's caffeinate; the supervisor must re-spawn it
        c1 = (read_json(state) or {}).get("caffeinate_pid")
        os.kill(c1, signal.SIGKILL)
        st2 = wait_for(lambda: (lambda s: s if s and s.get("caffeinate_pid") not in (None, c1) else None)(
            read_json(state)), 10)
        c2 = st2.get("caffeinate_pid") if st2 else None
        cmd2 = subprocess.run(["/bin/ps", "-ww", "-p", str(c2 or 0), "-o", "command="], capture_output=True,
                              text=True).stdout.strip()
        sup = st2["supervisor"] if st2 else {}
        res["caffeinate"] = {"killed": c1, "respawned": c2, "command": cmd2, "deaths": sup.get("deaths"),
                             "respawns": sup.get("respawns")}
        res["respawn_ok"] = bool(c2) and c2 != c1 and cmd2.endswith(f"-w {job}") and "-i -m -s" in cmd2 and \
            sup.get("deaths", 0) >= 1 and sup.get("respawns", 0) >= 1
        # --- live pidfile, then stop the job: a stale pidfile is detected
        store = S.Store(repo, "refs/heads/main")
        live = S.read_pidfile(store)[1]
        stop.write_text("stop\n")
        gone = wait_for(lambda: not H.pid_alive(job), 15)
        stale = S.read_pidfile(store)[1]
        res["pidfile"] = {"while_running": live, "after_exit": stale}
        res["ok"] = bool(rec["detachment"]["detached"] and res["payload"]
                         and res["payload"]["launched_by_launchd"]["pass"] and res["payload"]["ppid"] == 1
                         and res["payload"]["xpc_service_name"] == label and not left and res["job_survives"]
                         and res["job_not_in_killed_session"] and res["respawn_ok"] and live == "LIVE" and gone
                         and stale == "STALE")
        return res
    finally:
        try:
            stop.write_text("stop\n")
        except OSError:
            pass
        booted = subprocess.run(["/bin/launchctl", "bootout", f"gui/{os.getuid()}/{label}"], capture_output=True)
        for p in (run / "plists").glob("*.plist"):
            p.unlink()
        res["cleanup"] = {"bootout_rc": booted.returncode,
                          "still_loaded": subprocess.run(["/bin/launchctl", "print", f"gui/{os.getuid()}/{label}"],
                                                         capture_output=True).returncode == 0}
        try:
            os.killpg(os.getpgid(shell.pid), signal.SIGKILL)
        except OSError:
            pass


def t_launcher_death_while_waiting():
    """Launcher death: the launcher process itself is killed right after the bootstrap (in its --wait phase); the job
    survives it, and the job is booted out by cleanup."""
    H, L, S = mods()
    run = TMP / ("ld" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S"))
    run.mkdir(parents=True)
    repo = run / "repo"
    subprocess.run(["/usr/bin/git", "init", "-q", str(repo)], check=True, env=T.GENV)
    label = "org.rebaseguard.mbs308.test." + run.name
    state, stop = run / "payload_state.json", run / "STOP"
    pargs = [str(T.code_dir()), str(repo), str(state), str(stop)]
    harness = T.NSS / "tests/mbs308_launch_harness.py"
    p = subprocess.Popen([T.PY, "-I", "-S", "-B", str(harness), str(T.code_dir()), str(run), label, json.dumps(pargs)],
                         start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    try:
        rec = wait_for(lambda: read_json(run / "launch_record.json"), 30)
        p.kill()
        p.wait(timeout=10)
        time.sleep(1.5)
        job = rec and rec.get("pid")
        alive = bool(job) and H.pid_alive(job) and H.launchd_job_pid(label) == job
        return {"ok": bool(rec and rec["detachment"]["detached"]) and alive, "job_alive_after_launcher_death": alive}
    finally:
        stop.write_text("stop\n")
        subprocess.run(["/bin/launchctl", "bootout", f"gui/{os.getuid()}/{label}"], capture_output=True)
        for f in (run / "plists").glob("*.plist"):
            f.unlink()


def _loaded(label: str) -> bool:
    return subprocess.run(["/bin/launchctl", "print", f"gui/{os.getuid()}/{label}"], capture_output=True).returncode == 0


def _start_job(tag: str):
    H, L, S = mods()
    run = TMP / (tag + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%f"))
    run.mkdir(parents=True)
    repo = run / "repo"
    subprocess.run(["/usr/bin/git", "init", "-q", str(repo)], check=True, env=T.GENV)
    label = "org.rebaseguard.mbs308.test." + run.name
    state, stop = run / "payload_state.json", run / "STOP"
    program = [T.PY, "-I", "-S", "-B", str(T.NSS / "tests/mbs308_payload.py"), str(T.code_dir()), str(repo), str(state),
               str(stop)]
    log_dir = Path.home() / "Library/Logs/ReBaseGuard/mbs308-test"
    return run, label, state, stop, program, log_dir


def _teardown(label: str, run: Path, stop: Path, pid: int | None) -> dict:
    H, L, S = mods()
    stop.write_text("stop\n")
    if pid:
        wait_for(lambda: not H.pid_alive(pid), 15)
    b = subprocess.run(["/bin/launchctl", "bootout", f"gui/{os.getuid()}/{label}"], capture_output=True)
    for f in (run / "plists").glob("*.plist"):
        f.unlink()
    return {"bootout_rc": b.returncode, "still_loaded": _loaded(label)}


def t_wait_cleanup_ignores_failing_print():
    """R2: with `launchctl print` failing (planted: launchd_job_pid returns nothing), neither `cleanup` nor
    `wait_and_cleanup` boots out the live job; only once its RECORDED identity is dead is it booted out."""
    import threading
    H, L, S = mods()
    run, label, state, stop, program, log_dir = _start_job("wc")
    rec = L.launch(program, label, run / "plists", log_dir, run, record_dir=run)
    real = H.launchd_job_pid
    out, res = {}, {}
    try:
        H.launchd_job_pid = lambda *a, **k: None                 # planted failing / negative `launchctl print`
        try:
            L.cleanup(label, run)
            res["cleanup_while_alive"] = "NOT_REFUSED"
        except L.LaunchRefused as e:
            res["cleanup_while_alive"] = e.code
        th = threading.Thread(target=lambda: out.update(L.wait_and_cleanup(label, rec["plist"], rec["identity"],
                                                                           poll_s=0.2)), daemon=True)
        th.start()
        time.sleep(3.0)
        res["alive_during_wait"] = th.is_alive() and H.identity_state(rec["identity"]) == "ALIVE" and _loaded(label)
        stop.write_text("stop\n")
        th.join(30)
        res["booted_out_after_death"] = (not th.is_alive()) and out.get("booted_out") is True and not _loaded(label)
    finally:
        H.launchd_job_pid = real
        res["teardown"] = _teardown(label, run, stop, rec.get("pid"))
    return {"ok": bool(rec.get("observed")) and res["cleanup_while_alive"] == "STILL_RUNNING"
            and res["alive_during_wait"] and res["booted_out_after_death"], **res}


def t_launch_never_boots_out_after_bootstrap():
    """R2: a failure inside launch() AFTER the bootstrap (planted: the detachment proof raises) never boots the job out:
    it may already have passed the marker; the driver's own launchd check governs."""
    H, L, S = mods()
    run, label, state, stop, program, log_dir = _start_job("nb")
    real = L.prove_detached

    def boom(*_a, **_k):
        raise RuntimeError("planted failure after the bootstrap")
    L.prove_detached = boom
    pid = None
    try:
        try:
            L.launch(program, label, run / "plists", log_dir, run, record_dir=run)
            raised = False
        except RuntimeError:
            raised = True
        L.prove_detached = real
        st = wait_for(lambda: read_json(state), 20)
        pid = st and st.get("pid")
        time.sleep(1.5)
        alive = bool(pid) and H.pid_alive(pid) and _loaded(label)
    finally:
        L.prove_detached = real
        td = _teardown(label, run, stop, pid)
    return {"ok": raised and alive and not td["still_loaded"], "raised": raised, "alive_after_failure": alive,
            "teardown": td}


def t_ppid1_is_not_detachment():
    """A process orphaned INSIDE the launcher's session (PPID 1, same SID, not a launchd job) is NOT detached."""
    H, L, S = mods()
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:                                   # child: fork a grandchild that outlives us, report its pid, exit
        g = os.fork()
        if g == 0:
            os.close(r)
            time.sleep(8)
            os._exit(0)
        os.write(w, str(g).encode())
        os._exit(0)
    os.close(w)
    gpid = int(os.read(r, 32).decode())
    os.close(r)
    os.waitpid(pid, 0)
    wait_for(lambda: H.process_ppid(gpid) == 1, 5)
    proof = L.prove_detached(gpid, os.getpid(), "org.rebaseguard.mbs308.test.not-a-job")
    try:
        os.kill(gpid, signal.SIGKILL)
    except OSError:
        pass
    return {"ok": H.process_ppid(gpid) in (1, None) and proof["ppid_recorded_not_relied_on"] in (1, None)
            and proof["detached"] is False and proof["session_differs"] is False, "proof": proof}


def t_supervisor_respawns_in_process():
    H, L, S = mods()
    sup = H.CaffeinateSupervisor(poll_s=0.05).start()
    try:
        c1 = wait_for(sup.current_pid, 5)
        os.kill(c1, signal.SIGKILL)
        c2 = wait_for(lambda: (lambda c: c if c and c != c1 else None)(sup.current_pid()), 5)
        rec = sup.record()
    finally:
        rec_final = sup.stop()
    return {"ok": bool(c1 and c2 and c2 != c1 and rec["deaths"] >= 1 and rec["respawns"] >= 1)
            and not H.pid_alive(c2 or 0) or False,
            "first": c1, "second": c2, "record": {k: rec[k] for k in ("spawns", "deaths", "respawns")},
            "stopped": rec_final["spawns"]}


def t_preflight_gates_planted():
    """Section 6 gates (and DR2 c) on planted readings: each failing reading fails exactly its gate."""
    H, L, S = mods()
    good = {"batt": "Now drawing from 'AC Power'\n", "pmset": " lowpowermode         0\n",
            "thermal": "com.apple.system.thermalpressurelevel 0\n", "free": 10 * 2 ** 30, "memory": "1\n",
            "boot": "A7417159-025C-461F-8BF8-3F9C7F3C58CB\n"}
    su_off = {"AutomaticallyInstallMacOSUpdates": "0", "AutomaticDownload": "1", "CriticalUpdateInstall": "0",
              "ConfigDataInstall": "1"}
    base = H.preflight_gates("/", other_job_running=False, launched={"pass": True}, texts=good, su_texts=su_off)
    cases = {"batt": ("Now drawing from 'Battery Power'\n", "ac_power"), "pmset": (" lowpowermode 1\n", "lowpowermode_0"),
             "thermal": ("com.apple.system.thermalpressurelevel 1\n", "thermal_pressure_0"),
             "free": (1 * 2 ** 30, "free_disk_ge_2GiB"), "memory": ("2\n", "memory_pressure_normal"),
             "boot": ("", "boot_uuid_recorded")}
    out = {}
    for k, (bad, gate) in cases.items():
        g = H.preflight_gates("/", other_job_running=False, launched={"pass": True}, texts=dict(good, **{k: bad}),
                              su_texts=su_off)
        out[k] = [x for x, v in g["gates"].items() if not v] == [gate]
    g = H.preflight_gates("/", other_job_running=True, launched={"pass": False}, texts=good, su_texts=su_off)
    out["job_and_launcher"] = sorted(x for x, v in g["gates"].items() if not v) == ["launched_by_launchd",
                                                                                    "no_other_campaign_job"]
    for key in ("AutomaticallyInstallMacOSUpdates", "CriticalUpdateInstall"):
        for val in ("1", ""):                        # enabled, or missing (= enabled by default)
            g = H.preflight_gates("/", other_job_running=False, launched={"pass": True}, texts=good,
                                  su_texts=dict(su_off, **{key: val}))
            out[f"{key}={val or 'missing'}"] = [x for x, v in g["gates"].items() if not v] == ["no_automatic_os_install"]
    real = H.software_update_settings()
    return {"ok": base["pass"] and all(out.values()), "cases": out, "real_host_software_update": real}


def t_launcher_refuses_execute_when_preflight_fails():
    """`launch execute` runs the successor driver's (read-only) preflight first and refuses when it fails; nothing is
    bootstrapped. (On this host tonight the preflight fails on the host gates; the refusal is what is tested.)"""
    H, L, S = mods()
    before = subprocess.run(["/bin/launchctl", "list"], capture_output=True, text=True).stdout.count("org.rebaseguard")
    try:
        L.pre_launch("execute")
        refused = None
    except L.LaunchRefused as e:
        refused = e.code
    after = subprocess.run(["/bin/launchctl", "list"], capture_output=True, text=True).stdout.count("org.rebaseguard")
    return {"ok": refused == "PREFLIGHT_FAILED" and before == after, "refused": refused}


def t_identity_state_positive_evidence():
    """N-2 (REVIEW_IMPLEMENTATION_MBS308_DELTA): identity_state never reads DEAD from a field that was never recorded
    (an identity recorded while `ps` or the boot-UUID read failed): a live process whose record lacks the start time,
    the command sha256 or the boot UUID is UNKNOWN (never booted out, never counted dead), and DEAD once its pid is
    gone. A complete record of a live process is ALIVE, a failing `ps` makes it UNKNOWN, a reused pid is DEAD.
    K-1 (REVIEW_OPTIONB_LIVENESS_MBS308, builder5): each reading failing ALONE is UNKNOWN, never DEAD -- a failed
    boot-UUID read alone (every other reading works) and a failed command read alone (the start-time read works)."""
    H, L, S = mods()
    h = T.Helper(60)
    try:
        full = H.identity(h.p.pid)
        partial = {k: dict(full, **{k: None}) for k in ("start_time", "command_sha256", "boot_uuid")}
        alive = {k: H.identity_state(v) for k, v in partial.items()}
        alive_full = H.identity_state(full)
        reused = H.identity_state(dict(full, start_time="Thu Jan  1 00:00:00 1970"))
        real = H.process_start
        H.process_start = lambda pid, text=None: None                 # planted failing `ps`
        try:
            ps_failed = H.identity_state(full)
        finally:
            H.process_start = real
        real_boot = H.boot_session_uuid                               # K-1 (a): the boot-UUID read alone fails
        H.boot_session_uuid = lambda text=None: None
        try:
            boot_failed = H.identity_state(full)
        finally:
            H.boot_session_uuid = real_boot
        real_cmd = H.process_command_sha256                           # K-1 (b): the command read alone fails
        H.process_command_sha256 = lambda pid, text=None: None
        try:
            cmd_failed = H.identity_state(full)
            cmd_failed_start_read = H.process_start(h.p.pid) == full["start_time"]     # the start read still works
        finally:
            H.process_command_sha256 = real_cmd
    finally:
        h.kill()
    dead = {k: H.identity_state(v) for k, v in partial.items()}
    complete = all(full.get(k) for k in ("pid", "start_time", "boot_uuid", "command_sha256"))
    return {"ok": complete and all(v == "UNKNOWN" for v in alive.values()) and alive_full == "ALIVE"
            and reused == "DEAD" and ps_failed == "UNKNOWN" and boot_failed == "UNKNOWN" and cmd_failed == "UNKNOWN"
            and cmd_failed_start_read and all(v == "DEAD" for v in dead.values())
            and H.identity_state(full) == "DEAD",
            "partial_alive": alive, "full_alive": alive_full, "reused": reused, "ps_failed": ps_failed,
            "boot_read_failed_alone": boot_failed, "command_read_failed_alone": cmd_failed, "partial_dead": dead}


def t_identity_state_time_zone_independent():
    """O-1 (REVIEW_OPTIONB_LIVENESS_MBS308, reviewB5): the start-time reading does not depend on the time zone. A live
    helper's identity is RECORDED under one planted zone and CHECKED under another; the zone is planted through the
    environment of the reading (mbs308_host.ENV, the environment `ps` otherwise inherits its zone from, like a change
    of the system zone). Control (non-vacuous): a raw `ps -o lstart=` under the two planted zones prints two different
    strings for the same live process. With the repair the recorded and the current reading are equal and the live
    process stays ALIVE (and identity_alive True); DEAD only once the pid is gone."""
    H, L, S = mods()
    zones = ("JST-9", "EST5EDT")
    h = T.Helper(60)
    saved = H.ENV.get("TZ")
    try:
        raw = {}
        for z in zones:
            H.ENV["TZ"] = z
            raw[z] = H._run([H.PS, "-p", str(h.p.pid), "-o", "lstart="])
        H.ENV["TZ"] = zones[0]
        rec = H.identity(h.p.pid)                                   # recorded under zone 1
        H.ENV["TZ"] = zones[1]                                      # the system zone changes during the run
        st_changed = H.identity_state(rec)
        alive_changed = H.identity_alive(rec)
        start_changed = H.process_start(h.p.pid)
    finally:
        if saved is None:
            H.ENV.pop("TZ", None)
        else:
            H.ENV["TZ"] = saved
        h.kill()
    control = bool(raw[zones[0]]) and bool(raw[zones[1]]) and raw[zones[0]] != raw[zones[1]]
    after = H.identity_state(rec)
    return {"ok": control and all(rec.get(k) for k in ("start_time", "boot_uuid", "command_sha256"))
            and start_changed == rec["start_time"] and st_changed == "ALIVE" and alive_changed is True
            and after == "DEAD", "control_raw_readings_differ": control, "state_after_zone_change": st_changed,
            "identity_alive_after_zone_change": alive_changed, "state_after_exit": after}


def t_identity_command_unreadable_unknown():
    """O-4 (REVIEW_OPTIONB_LIVENESS_MBS308): `ps -o command=` prints an unreadable argument vector as "(name)" with
    exit 0. That output is a FAILED reading: process_command_sha256 returns None for it, so a live recorded process
    whose command reads "(name)" is UNKNOWN (never DEAD), and an identity recorded at such a moment carries no command
    field (never compared). A real command, one merely containing parentheses, and a zombie's "<defunct>" are
    readings as before."""
    H, L, S = mods()
    unreadable = [H.process_command_sha256(1, text=t) for t in ("(sleep)\n", "(python3.14)", "()")]
    readable = [H.process_command_sha256(1, text=t) for t in ("/bin/sleep 60\n",
                                                               "/usr/libexec/UserEventAgent (System)\n", "<defunct>\n")]
    h = T.Helper(60)
    real_run = H._run

    def planted(args, timeout=60):                                  # the command read prints "(sleep)", exit 0
        if "command=" in args:
            return "(sleep)\n"
        return real_run(args, timeout)
    try:
        full = H.identity(h.p.pid)
        H._run = planted
        try:
            live_state = H.identity_state(full)
            recorded_now = H.identity(h.p.pid)
        finally:
            H._run = real_run
        after_state = H.identity_state(full)
    finally:
        h.kill()
    return {"ok": all(u is None for u in unreadable) and all(isinstance(r, str) and len(r) == 64 for r in readable)
            and after_state == "ALIVE" and live_state == "UNKNOWN" and recorded_now.get("command_sha256") is None
            and H.identity_state(full) == "DEAD",
            "unreadable_is_none": [u is None for u in unreadable], "live_state_with_unreadable_argv": live_state,
            "recorded_command_field": recorded_now.get("command_sha256")}


def t_identity_command_empty_reading_unknown():
    """G-1 (reviewQ6: Y6b, Y6c): an EMPTY `ps -o command=` reading is a failed reading, never the digest of the empty
    string. The failure is planted at the READING (the host module's command reader), not by replacing
    process_command_sha256, so the guard inside that function is what is exercised: with the command read returning
    an empty output, a blank line, or failing (the start-time read still works), process_command_sha256 is None, a
    live recorded process is UNKNOWN (never DEAD), and an identity recorded at that moment carries no command field.
    Control: unplanted, the same identity is ALIVE; DEAD once the pid is gone."""
    import hashlib
    H, L, S = mods()
    direct = [H.process_command_sha256(1, text=t) for t in ("", "\n", "   \n")]
    h = T.Helper(60)
    real_run = H._run
    states, recorded, start_ok = {}, {}, {}
    try:
        full = H.identity(h.p.pid)
        for tag, val in (("empty_output", ""), ("blank_line", "\n"), ("failed_ps", None)):
            def planted(args, timeout=60, _v=val):                  # only the command read is planted
                if "command=" in args:
                    return _v
                return real_run(args, timeout)
            H._run = planted
            try:
                states[tag] = H.identity_state(full)
                recorded[tag] = H.identity(h.p.pid).get("command_sha256")
                start_ok[tag] = H.process_start(h.p.pid) == full["start_time"]
            finally:
                H._run = real_run
        control = H.identity_state(full)
    finally:
        H._run = real_run
        h.kill()
    empty_digest = hashlib.sha256(b"").hexdigest()
    return {"ok": all(d is None for d in direct) and full.get("command_sha256") not in (None, empty_digest)
            and all(v == "UNKNOWN" for v in states.values()) and len(states) == 3
            and all(v is None for v in recorded.values()) and all(start_ok.values()) and control == "ALIVE"
            and H.identity_state(full) == "DEAD",
            "direct_is_none": [d is None for d in direct], "live_state_with_empty_command_reading": states,
            "recorded_command_field": recorded, "unplanted": control}


def t_preflight_timeout_rule():
    """R3 (ratification item 31): the launcher's preflight timeout is the RULE PRE_CAP_S + 100 s, with PRE_CAP_S the
    driver's own. Checked on the code under test (the driver's PRE_CAP_S read independently here) and on a copy whose
    driver PRE_CAP_S differs: the launcher's timeout must follow it (a literal would not)."""
    import ast
    import importlib.util
    import shutil
    H, L, S = mods()

    def pre_cap(driver: Path) -> int:
        for n in ast.parse(driver.read_text()).body:
            if isinstance(n, ast.Assign) and [getattr(t, "id", None) for t in n.targets] == ["PRE_CAP_S"]:
                return ast.literal_eval(n.value)
        raise AssertionError("no PRE_CAP_S")

    def timeout_of(mod) -> int | None:
        seen = []

        def fake_run(args, timeout=60):
            seen.append(timeout)
            return subprocess.CompletedProcess(args, 0, "MBS308 PREFLIGHT PASS\n", "")
        real = mod._run
        mod._run = fake_run
        try:
            got = mod.pre_launch("execute")
        finally:
            mod._run = real
        return seen[0] if got == {"preflight": "PASS"} and len(seen) == 1 else None
    here = timeout_of(L)
    want_here = pre_cap(T.code_dir() / "mbs308_driver.py") + 100
    d = TMP / "follow" / "level4/closure_proofs/p5y_k5_cell308_mbs_r1/code"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for f in ("mbs308_launch.py", "mbs308_host.py"):
        shutil.copy(T.code_dir() / f, d / f)
    src = (T.code_dir() / "mbs308_driver.py").read_text()
    lines = [ln for ln in src.splitlines(keepends=True) if ln.startswith("PRE_CAP_S = ")]
    (d / "mbs308_driver.py").write_text(src.replace(lines[0], "PRE_CAP_S = 1234\n", 1) if len(lines) == 1 else src)
    spec = importlib.util.spec_from_file_location("mbs308_launch_follow", d / "mbs308_launch.py")
    L2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(L2)
    moved = timeout_of(L2)
    return {"ok": len(lines) == 1 and here == want_here and pre_cap(d / "mbs308_driver.py") == 1234 and moved == 1334,
            "timeout": here, "expected": want_here, "timeout_when_pre_cap_is_1234": moved}


if __name__ == "__main__":
    T.cli(globals())
