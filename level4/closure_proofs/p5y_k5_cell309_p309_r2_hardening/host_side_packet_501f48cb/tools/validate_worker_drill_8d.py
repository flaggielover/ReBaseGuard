"""Read-only post-run validator for the P309-r2 worker-tier drill (8d) on r2 501f48cb.  Part of the host-side packet
(WORKER_TIER_PASS_FAIL_RULES.md).  Not r2 code; it writes nothing but its standard output.

usage:
  python3 -B validate_worker_drill_8d.py --clone <CLONE> --stamp <drill utc stamp, e.g. 20261012T080102Z>
         [--launch-record <RUN_SCRATCH>/launch_<utc>.json] [--verdict <VERDICT_8B_final.json>]
         [--prelaunch <PRELAUNCH_CHECK.json>]

It judges, from content and never from exit codes alone:
  * <CLONE>/<NS>/evidence/drill/<stamp>/DRILL_REPORT.json and its two exported ledgers;
  * the P309 clone's state after the drill (HEAD, the one GOVERNANCE row, nothing else changed);
  * optionally the launch record file, the 8b-final verdict and the pre-launch check (host identity consistency).
Classification: PASS, FAIL (with the failed checks), INTERRUPTED (no report for a started drill) or
INCIDENT (any target counter, protected ref, grant or result file).  Exit 0 only for PASS.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

R2_COMMIT = "501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
ZT, EX = NS + "/ledger/ZERO_TARGET_LEDGER.jsonl", NS + "/ledger/EXPOSURE_LEDGER.jsonl"
COUNTERS = ("new_target_evaluations", "target_equivalent_proxies", "target_informed_optimisation")
PROTECTED_REF = re.compile(r"refs/(?:p5y-k5-cell30|p309-cell309|rlr-tail/|p309-test/)", re.I)
GRANT_NAME = re.compile(r"(?:P309_GRANT|GRANT\.json|P309_RESULT|p309-emergency-result|p309-run-nonce)", re.I)
GATES = ["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "Q09", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15",
         "Q16", "Q17", "Q_U2", "Q_D5", "Q-HOST"]
CONTROLS = ["R2_M01a", "R2_M01b", "second_freeze_record", "ledger_rows_kept_across_reset", "test_only_prior_ref",
            "push_url_refused", "p309_repository_refused", "after_reset_tip", "no_production_namespace_ref"]
UNIT_CHECKED = {"Restart": ("no",), "KillMode": ("control-group",), "KillSignal": ("9", "SIGKILL"),
                "NoNewPrivileges": ("yes",), "PrivateTmp": ("yes",), "ProtectSystem": ("strict",)}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
GIT_ENV = {"LC_ALL": "C", "GIT_PAGER": "cat", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
           "PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/nonexistent")}


def arg(name, default=None):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo] + list(args), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, universal_newlines=True, timeout=120, env=GIT_ENV)
    return p.stdout if p.returncode == 0 else None


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError, TypeError):
        return None


def rows_of(text):
    out, bad = [], 0
    for line in (text or "").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                bad += 1
    return out, bad


def main():
    clone, stamp = arg("--clone"), arg("--stamp")
    if not clone or not stamp or not re.fullmatch(r"\d{8}T\d{6}Z", stamp):
        sys.stderr.write(__doc__)
        return 2
    clone = os.path.realpath(clone)
    d = os.path.join(clone, NS, "evidence", "drill", stamp)
    rep_path = os.path.join(d, "DRILL_REPORT.json")
    c, info, incident = {}, {"stamp": stamp, "report": rep_path}, []

    # ---- the P309 clone after the drill (also needed for INTERRUPTED and INCIDENT)
    head = (git(clone, "rev-parse", "HEAD") or "").strip()
    c["V01_clone_head_still_501f48cb"] = head == R2_COMMIT
    refs = (git(clone, "for-each-ref", "--format=%(refname)") or "").splitlines()
    prot = [r for r in refs if PROTECTED_REF.search(r)]
    if prot:
        incident.append("protected ref(s) in the P309 clone: %s" % prot[:3])
    for root, dirs, files in os.walk(os.path.join(clone, NS)):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in files:
            if GRANT_NAME.search(f):
                incident.append("grant/result-like file: %s" % os.path.join(root, f))
    zt_now, zt_bad = rows_of(open(os.path.join(clone, ZT)).read() if os.path.exists(os.path.join(clone, ZT)) else "")
    zt_head, _ = rows_of(git(clone, "show", "HEAD:" + ZT) or "")
    if any(r.get(k, 0) != 0 for r in zt_now for k in COUNTERS):
        incident.append("a nonzero target counter in the P309 clone's ledger")

    if not os.path.exists(rep_path):
        cls = "INCIDENT" if incident else "INTERRUPTED"
        out = {"schema": "P309_R2_8D_VALIDATION/1", "classification": cls, "incident": incident, "checks": c,
               "info": dict(info, note="no DRILL_REPORT.json for this stamp: the drill did not complete (or never "
                                       "reached its export); classify the attempt read-only from the unit journal")}
        sys.stdout.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
        return 1
    raw = open(rep_path, "rb").read()
    rep = json.loads(raw)
    rep_sha = hashlib.sha256(raw).hexdigest()
    info["report_sha256"] = rep_sha

    # ---- the report itself
    c["V02_schema_tier_pass"] = rep.get("schema") == "P309_R2_DRILL/1" and rep.get("tier") == "worker" and \
        rep.get("pass") is True and not rep.get("error")
    c["V03_all_verdicts_true"] = sorted((rep.get("verdicts") or {}).keys()) == ["controls", "host", "items", "ledger",
                                                                                "witness"] and all(rep["verdicts"].values())
    c["V04_cloned_exactly_501f48cb"] = rep.get("clone_base") == R2_COMMIT
    c["V05_p309_repository_unchanged_during_drill"] = rep.get("p309_unchanged") is True and \
        rep.get("p309_before") == rep.get("p309_after") and (rep.get("p309_before") or {}).get("head") == R2_COMMIT
    lr = rep.get("launch_record") or {}
    unit = lr.get("unit") or ""
    c["V06_launch_record_drill_no_blockers"] = lr.get("schema") == "P309_R2_LAUNCH/2" and lr.get("mode") == "drill" \
        and lr.get("blockers") == [] and lr.get("p309_units_loaded") == [] and \
        bool(re.fullmatch(r"p309-r2-drill-\d{8}T\d{6}Z", unit)) and unit[-16:] <= stamp
    hc = lr.get("host_config") or {}
    c["V07_launch_record_redacted"] = all(all(HEX64.match(str(v)) for v in hc.get(k) or [])
                                          for k in ("foreign_roots", "foreign_patterns", "foreign_heavy_patterns")) \
        and bool(hc.get("foreign_roots")) and bool(hc.get("foreign_uids"))
    c["V08_launch_gates_passed"] = all((lr.get(k) or {}).get("pass") is True for k in ("preflight", "gate", "isolation"))
    if arg("--launch-record"):
        c["V09_launch_record_file_equals_embedded"] = load(arg("--launch-record")) == lr
    up = rep.get("unit_properties") or {}
    c["V10_unit_properties_checked_six"] = all(up.get(k) in ok for k, ok in UNIT_CHECKED.items())
    c["V11_unit_properties_recorded"] = up.get("Id") == unit + ".service" and \
        up.get("User") == (lr.get("launch_settings") or {}).get("unit_user") and up.get("SendSIGKILL") == "yes" and \
        up.get("TimeoutStopUSec") in ("10s", "10000000") and \
        all(HEX64.match(str(x)) for x in (up.get("InaccessiblePaths") or [])) and bool(up.get("InaccessiblePaths"))
    m = (rep.get("items") or {}).get("main") or {}
    gates = m.get("gates") or {}
    info["gates"] = gates
    info["runner_wall_s"] = m.get("wall_s")
    c["V12_runner_rc0_pass_confined_head_unchanged"] = list((rep.get("items") or {}).keys()) == ["main"] and \
        m.get("rc") == 0 and m.get("pass") is True and m.get("confined") is True and m.get("head_unchanged") is True
    c["V13_all_20_gates_present_and_true_incl_QHOST"] = sorted(gates) == sorted(GATES) and all(gates.values())
    wb, wa = rep.get("witness_before_items") or {}, rep.get("witness_after_items") or {}
    c["V14_witnesses"] = bool(wb) and all(wb.values()) and all(wa.values()) and \
        {"qc11_sandbox_one_record", "qc11_sandbox_descends_from_F"} <= set(wa)
    ctl = rep.get("controls") or {}
    c["V15_controls_all_caught"] = sorted(ctl) == sorted(CONTROLS) and all(
        (v.get("caught") if isinstance(v, dict) else v) is True for v in ctl.values())
    h = rep.get("host") or {}
    c["V16_host_functions"] = h.get("provenance_rc") == [0, 0] and h.get("continuity_pass") is True and \
        h.get("preflight_rc") == 0 and h.get("preflight_as_expected") is True and h.get("r1_tree_unchanged") is True \
        and h.get("host_package_tests_rc") == 0 and h.get("host_controls_rc") == 0 and h.get("static_controls_rc") == 0
    lg = rep.get("ledger") or {}
    c["V17_ledger_counters_zero_no_cells_no_band"] = not any((lg.get("counters") or {"x": 1}).values()) and \
        lg.get("cells_touched") == 0 and lg.get("band_hits") == []
    comp = lg.get("completeness") or {}
    c["V18_ledger_complete_one_run_start"] = comp.get("run_start_rows") == 1 and comp.get("missing_scripts") == []

    # ---- the exported ledgers equal the report's rows, and their hashes validate
    rows = lg.get("rows") or {}
    for rel, fname in ((ZT, "DRILL_ZERO_TARGET_LEDGER.jsonl"), (EX, "DRILL_EXPOSURE_LEDGER.jsonl")):
        want = rows.get(rel)
        try:
            got = open(os.path.join(d, fname)).read()
        except OSError:
            got = None
        key = "V19_export_%s" % fname.split(".")[0]
        c[key] = want is not None and got == "".join(l + "\n" for l in want) and \
            (lg.get("sha256") or {}).get(rel) == hashlib.sha256("\n".join(want).encode()).hexdigest()
    drows, dbad = rows_of("\n".join(rows.get(ZT) or []))
    starts = [r for r in drows if " RUN START " in " " + r.get("purpose", "") + " "]
    F = ((rep.get("topology") or {}).get("F") or "")
    c["V20_drill_rows_parse_zero_and_one_run_start_at_F"] = dbad == 0 and len(starts) == 1 and bool(F) and \
        F[:12] in starts[0].get("purpose", "") and not any(r.get(k, 0) != 0 for r in drows for k in COUNTERS)
    if any(r.get(k, 0) != 0 for r in drows for k in COUNTERS) or any((lg.get("counters") or {}).values()):
        incident.append("a nonzero target counter in the drill's own ledger rows")
    utcs = [r.get("utc", "") for r in drows]
    c["V21_drill_rows_utc_ordered"] = utcs == sorted(utcs)

    # ---- the P309 clone gained exactly this drill's evidence and one GOVERNANCE row
    st = git(clone, "status", "--porcelain", "--untracked-files=all") or ""
    changed = sorted(l[3:] for l in st.splitlines() if l.strip())
    info["clone_status"] = changed
    c["V22_clone_changes_only_this_drill"] = changed == sorted(
        [NS + "/evidence/drill/%s/%s" % (stamp, f) for f in os.listdir(d)] + [ZT])
    c["V23_exactly_three_exported_files"] = sorted(os.listdir(d)) == ["DRILL_EXPOSURE_LEDGER.jsonl", "DRILL_REPORT.json",
                                                                      "DRILL_ZERO_TARGET_LEDGER.jsonl"]
    new = zt_now[len(zt_head):]
    c["V24_ledger_is_head_plus_one_governance_row"] = zt_bad == 0 and zt_now[:len(zt_head)] == zt_head and \
        len(new) == 1 and new[0].get("class") == "GOVERNANCE" and \
        new[0].get("purpose") == "topology drill (worker tier) %s: PASS" % stamp and \
        new[0].get("script") == "code/p309_" + "topology_drill.py" and \
        ("report sha256 " + rep_sha) in new[0].get("notes", "") and not any(new[0].get(k, 0) for k in COUNTERS)
    ex_now = open(os.path.join(clone, EX)).read() if os.path.exists(os.path.join(clone, EX)) else ""
    c["V25_exposure_ledger_unchanged"] = ex_now == (git(clone, "show", "HEAD:" + EX) or "")

    # ---- host identity consistency (optional inputs)
    lp = (lr.get("preflight") or {}).get("provenance") or {}
    ident = {"machine_id_sha256": lp.get("machine_id_sha256"), "hostname_sha256": lp.get("hostname_sha256"),
             "instance_id_sha256": (lp.get("cloud") or {}).get("instance_id_sha256")}
    info["launch_identity"] = ident
    if arg("--verdict"):
        v = (load(arg("--verdict")) or {}).get("host") or {}
        c["V26_identity_equals_8b_final"] = all(ident[k] and ident[k] == v.get(k) for k in ident)
    if arg("--prelaunch"):
        pl = load(arg("--prelaunch")) or {}
        c["V27_prelaunch_check_passed"] = pl.get("pass") is True
        c["V28_identity_equals_prelaunch"] = all(((pl.get("info") or {}).get("identity_now") or {}).get(k) == ident[k]
                                                 for k in ("machine_id_sha256", "hostname_sha256"))
    try:
        t0 = datetime.datetime.strptime(rep.get("utc_start", ""), "%Y-%m-%dT%H:%M:%SZ")
        t1 = datetime.datetime.strptime(rep.get("utc_end", ""), "%Y-%m-%dT%H:%M:%SZ")
        info["drill_wall_h"] = round((t1 - t0).total_seconds() / 3600, 2)
        c["V29_drill_wall_within_12h"] = 0 < (t1 - t0).total_seconds() <= 12 * 3600 + 3600
    except ValueError:
        c["V29_drill_wall_within_12h"] = False

    failed = sorted(k for k, v in c.items() if not v)
    cls = "INCIDENT" if incident else ("PASS" if not failed else "FAIL")
    out = {"schema": "P309_R2_8D_VALIDATION/1", "classification": cls, "failed": failed, "incident": incident,
           "checks": c, "info": info, "statement": "read-only; NEW Γ309 TARGET EVALUATIONS = 0"}
    sys.stdout.write(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    return 0 if cls == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
