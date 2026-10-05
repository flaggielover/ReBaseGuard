"""Test fixtures for the two packet tools (scratch only).  usage: make_fixtures.py <T dir> <case>
cases: prelaunch | drill_pass | drill_fail_gate | drill_incident | drill_interrupted | drill_extra_file"""
import datetime, hashlib, importlib.util, json, os, pwd, shutil, sys

sys.dont_write_bytecode = True
T, case = sys.argv[1], sys.argv[2]
clone = os.path.join(T, "clone")
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
ns = os.path.join(clone, NS)
spec = importlib.util.spec_from_file_location("hostmod", os.path.join(ns, "code", "p309_" + "host.py"))
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
prov = H.provenance(H.load_config([]))
if "--fake-imds" in sys.argv:
    prov["cloud"] = {"available": True, "instance_id_sha256": H.sha("i-fixture")}
me = pwd.getpwuid(os.getuid()).pw_name
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
cfg = {"p309_roots": [T], "foreign_roots": ["/nonexistent-cell308-root"], "foreign_patterns": ["cell[_-]?308"],
       "foreign_heavy_patterns": ["c308_heavy"], "foreign_uids": [54321], "interpreter": os.path.realpath(sys.executable),
       "glibc": os.confstr("CS_GNU_LIBC_VERSION"), "python_version": "3.11.15",
       "unit_user": me, "unit_group": me, "memory_max": "12G", "oom_score_adjust": 500, "cpu_weight": 20, "io_weight": 20}
redacted = dict(H.redacted_config({k: v for k, v in cfg.items() if k not in H.LAUNCH_KEYS}))
ident = {"machine_id_sha256": prov["machine_id_sha256"], "hostname_sha256": prov["hostname_sha256"],
         "instance_id_sha256": (prov.get("cloud") or {}).get("instance_id_sha256")}

if case == "prelaunch":
    json.dump(cfg, open(os.path.join(T, "host_config.json"), "w"))
    os.makedirs(os.path.join(T, "run"), exist_ok=True)
    os.makedirs(os.path.join(T, "check"), exist_ok=True)
    json.dump({"schema": "P309_R2_LAUNCH/2", "utc": now, "mode": "drill", "blockers": [],
               "preflight": {"provenance": prov}}, open(os.path.join(T, "check", "launch_x.json"), "w"))
    json.dump({"point": "final", "verdict": "HOST_ACCEPTED_FOR_WORKER_TIER", "host": ident},
              open(os.path.join(T, "verdict.json"), "w"))
    sys.exit(0)

# ---- a synthetic worker-tier drill result built from the committed cloud-tier report 20261002T052554Z
src = json.load(open(os.path.join(ns, "evidence", "drill", "20261002T052554Z", "DRILL_REPORT.json")))
stamp = "20261012T080102Z"
unit = "p309-r2-drill-20261012T080100Z"
R2 = "501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853"
gates = {g: True for g in ["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "Q09", "Q10", "Q11", "Q12", "Q13",
                           "Q14", "Q15", "Q16", "Q17", "Q_U2", "Q_D5", "Q-HOST"]}
if case == "drill_fail_gate":
    gates["Q10"] = False
rep = dict(src)
rep.update({"tier": "worker", "clone_base": R2, "utc_start": "2026-10-12T08:01:02Z", "utc_end": "2026-10-12T14:20:00Z",
            "p309_before": dict(src["p309_before"], head=R2), "p309_after": dict(src["p309_before"], head=R2),
            "p309_unchanged": True,
            "items": {"main": {"rc": 0 if case != "drill_fail_gate" else 1, "wall_s": 21000.0,
                               "pass": case != "drill_fail_gate", "gates": gates, "head_unchanged": True,
                               "confined": True}},
            "launch_record": {"schema": "P309_R2_LAUNCH/2", "utc": "2026-10-12T08:01:00Z", "mode": "drill",
                              "unit": unit, "host_config": redacted, "launch_settings": {k: cfg[k] for k in H.LAUNCH_KEYS},
                              "preflight": {"pass": True, "provenance": prov}, "gate": {"pass": True},
                              "isolation": {"pass": True}, "p309_units_loaded": [], "blockers": []},
            "unit_properties": {"Id": unit + ".service", "User": me, "Restart": "no", "KillMode": "control-group",
                                "KillSignal": "9", "SendSIGKILL": "yes", "TimeoutStopUSec": "10s",
                                "NoNewPrivileges": "yes", "PrivateTmp": "yes", "ProtectSystem": "strict",
                                "InaccessiblePaths": [H.sha("/nonexistent-cell308-root")]},
            "host": dict(src["host"], preflight_rc=0, preflight_as_expected=True)})
rep["verdicts"] = dict(src["verdicts"], items=case != "drill_fail_gate")
rep["pass"] = case != "drill_fail_gate"
out = os.path.join(ns, "evidence", "drill", stamp)
if case != "drill_interrupted":
    os.makedirs(out)
    for rel, lines in rep["ledger"]["rows"].items():
        open(os.path.join(out, "DRILL_" + os.path.basename(rel)), "w").write("".join(l + "\n" for l in lines))
    open(os.path.join(out, "DRILL_REPORT.json"), "w").write(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
    sha = hashlib.sha256(open(os.path.join(out, "DRILL_REPORT.json"), "rb").read()).hexdigest()
    row = {"cells_touched": [], "class": "GOVERNANCE", "drifts": [], "new_target_evaluations": 0,
           "notes": "development only; evidence/drill/%s; report sha256 %s" % (stamp, sha),
           "purpose": "topology drill (worker tier) %s: %s" % (stamp, "PASS" if rep["pass"] else "FAIL"),
           "script": "code/p309_" + "topology_drill.py", "target_equivalent_proxies": 0,
           "target_informed_optimisation": 0, "utc": "2026-10-12T14:20:01Z"}
    if case == "drill_incident":
        row["new_target_evaluations"] = 1
    open(os.path.join(ns, "ledger", "ZERO_TARGET_LEDGER.jsonl"), "a").write(json.dumps(row, sort_keys=True) + "\n")
    if case == "drill_extra_file":
        open(os.path.join(ns, "code", "stray.txt"), "w").write("x\n")
json.dump(rep["launch_record"], open(os.path.join(T, "launch_rec.json"), "w"))
json.dump({"point": "final", "verdict": "HOST_ACCEPTED_FOR_WORKER_TIER", "host": ident},
          open(os.path.join(T, "verdict.json"), "w"))
json.dump({"pass": True, "info": {"identity_now": {k: ident[k] for k in ("machine_id_sha256", "hostname_sha256")}}},
          open(os.path.join(T, "prelaunch_pass.json"), "w"))
print("fixture", case, stamp)
