#!/usr/bin/env python3
"""Independent, read-only validator and status classifier for P309-r2 qualification state.

  python3 r2h_validator.py status   QUALIFICATION_DIR LEDGER [--record-utc T] [--freeze F] [--out FILE]
  python3 r2h_validator.py rehearsal REHEARSAL_DIR [--out FILE]

It imports nothing from the r2 campaign code and never writes into what it inspects.  The verdict comes from
CONTENT -- never from a process exit status: every record parses and names itself, carries the recorded freeze,
appears in the runner's order with monotone times, the Q-HOST start evidence precedes the gates, the ledger holds
exactly one RUN START after the freeze record and no torn row, and a summary (the completion marker) exists and binds
every record by sha256.

Classifications (status mode):
  NOT_STARTED     no attempt directory, no summary, no RUN START after the freeze record, nothing stray
  INTERRUPTED     consistent but incomplete: records or the summary missing, or a leftover temporary file; it can
                  never become a success: the runner refuses every restart over it (no retry, no resumption)
  ABORTED         complete and consistent, ended by Q-HOST (QHOST_FAIL.json + a pass:false summary)
  COMPLETE_FAIL   complete and consistent, a gate failed
  COMPLETE_PASS   complete and consistent, every gate (QC01..QC_D5 and Q-HOST) passed
  CORRUPT         inconsistent: torn / empty / unparseable record or ledger row, wrong order, hash or freeze mismatch,
                  a second RUN START, a record without its start evidence, a summary disagreeing with the records,
                  a stray file, a RUN START with no attempt directory
Exit status: 0 only for COMPLETE_PASS (and, in rehearsal mode, PASS).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

GATES = ["QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09", "QC10", "QC11", "QC12", "QC13",
         "QC14", "QC15", "QC16", "QC17", "QC_U2", "QC_D5"]
AUX = {"QC08_DECOY_STAGE1A.json", "QC09_DECOY_STAGE1B_297.json", "QC09_DECOY_STAGE1B_316.json",
       "QC10_DECOY_STAGE1A.json", "QC14_REHEARSE.json"}
QHOST_START = ("LAUNCH_RECORD.json", "UNIT_PROPERTIES.json", "QHOST_BASELINE.json")
QHOST_FILES = set(QHOST_START) | {"QHOST_MONITOR.jsonl", "QHOST_SUMMARY.json", "QHOST_FAIL.json", "ATTEMPT_START.json"}
RUN_START = "QUALIFICATION RUN START"
COUNTERS = ("new_target_evaluations", "target_equivalent_proxies", "target_informed_optimisation")
RANK = {"NOT_STARTED": 0, "COMPLETE_PASS": 0, "COMPLETE_FAIL": 1, "ABORTED": 1, "INTERRUPTED": 2, "CORRUPT": 3}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ts(s):
    if not isinstance(s, str):
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


class V:
    def __init__(self):
        self.level, self.reasons, self.checks = None, [], {}

    def to(self, level: str, why: str) -> None:
        self.reasons.append(f"{level}: {why}")
        if self.level is None or RANK[level] > RANK[self.level]:
            self.level = level

    def check(self, name: str, ok: bool, level: str, why: str) -> bool:
        self.checks[name] = bool(ok)
        if not ok:
            self.to(level, why)
        return ok


def load(p: Path, v: V):
    raw = p.read_bytes()
    if not raw:
        v.to("CORRUPT", f"{p.name}: empty file (torn write)")
        return None
    try:
        d = json.loads(raw)
    except ValueError as exc:
        v.to("CORRUPT", f"{p.name}: unparseable ({exc.msg} at byte {exc.pos} of {len(raw)}; torn write)")
        return None
    if not isinstance(d, dict):
        v.to("CORRUPT", f"{p.name}: not a JSON object")
        return None
    return d


def ledger(p: Path, v: V, name: str) -> list:
    if not p.exists():
        v.to("CORRUPT", f"{name} missing")
        return []
    raw = p.read_bytes()
    if raw and not raw.endswith(b"\n"):
        v.to("CORRUPT", f"{name}: the last row has no newline (torn append)")
    rows = []
    for i, line in enumerate(raw.decode(errors="replace").splitlines()):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except ValueError:
                v.to("CORRUPT", f"{name}: row {i + 1} unparseable (torn append)")
    bad = [r for r in rows if any(r.get(k, 0) != 0 for k in COUNTERS)]
    v.check(f"{name}:target_counters_zero", not bad, "CORRUPT", f"{name}: {len(bad)} row(s) with a nonzero target counter")
    v.checks[f"{name}:rows"] = len(rows)
    return rows


def status(qdir: Path, ledger_path: Path, record_utc: str | None, freeze: str | None) -> dict:
    v = V()
    rows = ledger(ledger_path, v, "execution_ledger")
    t0 = ts(record_utc) if record_utc else None
    starts = [r for r in rows if str(r.get("purpose", "")).startswith(RUN_START)
              and (t0 is None or (ts(r.get("utc")) and ts(r["utc"]) >= t0))]
    aborts = [r for r in rows if "ABORTED BY Q-HOST" in str(r.get("purpose", ""))]
    v.checks["run_start_lines"] = len(starts)
    v.check("at_most_one_run_start", len(starts) <= 1, "CORRUPT", f"{len(starts)} RUN START lines (a repeated run)")
    att = qdir / "attempt_1"
    summ = qdir / "P309_QUALIFICATION.json"
    stray = []
    if qdir.is_dir():
        for p in sorted(qdir.iterdir()):
            if p.name in ("attempt_1", "P309_QUALIFICATION.json", "host_rerun"):
                continue
            stray.append(p.name)
    if stray:
        tmp = [s for s in stray if s.startswith(".") or ".tmp" in s]
        if tmp:
            v.to("INTERRUPTED", f"leftover temporary file(s) in the qualification directory: {tmp}")
        other = [s for s in stray if s not in tmp]
        if other:
            v.to("CORRUPT", f"stray entries in the qualification directory: {other}")
    if not att.exists() and not summ.exists():
        if starts:
            v.to("CORRUPT", "a RUN START line exists but no attempt directory (lost or removed attempt)")
        elif v.level is None:
            v.level = "NOT_STARTED"
        return out(v, [], [], None)
    if not att.is_dir():
        v.to("CORRUPT", "a summary exists without an attempt directory")
        return out(v, [], [], None)
    names = sorted(p.name for p in att.iterdir() if p.is_file())
    tmps = [n for n in names if n.startswith(".") or ".tmp" in n]
    if tmps:
        v.to("INTERRUPTED", f"leftover temporary file(s) {tmps} (an interrupted write)")
    unknown = [n for n in names if n not in tmps and n not in AUX and n not in QHOST_FILES and n[:-5] not in GATES]
    v.check("no_unknown_files", not unknown, "CORRUPT", f"unknown files in the attempt: {unknown}")
    recs, present = {}, []
    for g in GATES:
        p = att / f"{g}.json"
        if not p.exists():
            continue
        present.append(g)
        d = load(p, v)
        if d is None:
            continue
        v.check(f"{g}:names_itself", d.get("qc") == g, "CORRUPT", f"{g}.json names {d.get('qc')}")
        if freeze:
            v.check(f"{g}:freeze", d.get("freeze_commit") == freeze, "CORRUPT", f"{g}.json foreign freeze")
        v.check(f"{g}:pass_bool", isinstance(d.get("pass"), bool), "CORRUPT", f"{g}.json pass not a bool")
        recs[g] = d
    for f in QHOST_START + ("QHOST_SUMMARY.json", "QHOST_FAIL.json", "ATTEMPT_START.json"):
        if (att / f).exists():
            load(att / f, v)
    v.check("records_form_a_prefix", present == GATES[:len(present)], "CORRUPT",
            f"records are not a prefix of the runner's order: {present}")
    times = [ts(recs[g].get("utc")) for g in present if g in recs]
    v.check("record_times_monotone", all(a and b and a <= b for a, b in zip(times, times[1:])), "CORRUPT",
            "record times are not monotone")
    if present:
        v.check("qhost_start_evidence_before_gates", all((att / f).exists() for f in QHOST_START), "CORRUPT",
                "gate records exist without the Q-HOST start evidence")
        if starts:
            v.check("run_start_before_records", ts(starts[0]["utc"]) and times[0] and ts(starts[0]["utc"]) <= times[0],
                    "CORRUPT", "a record predates the RUN START line")
    if not starts:
        v.to("CORRUPT" if present else "INTERRUPTED",
             "records exist without a RUN START line" if present else "attempt directory without a RUN START line "
                                                                     "(interrupted before the start)")
    aborted = (att / "QHOST_FAIL.json").exists()
    s = load(summ, v) if summ.exists() else None
    if summ.exists() and s is not None:
        if aborted:
            v.check("abort_summary_fails", s.get("pass") is False, "CORRUPT", "a Q-HOST abort with a passing summary")
            v.checks["aborted"] = True
            if v.level is None or RANK[v.level] < RANK["ABORTED"]:
                v.to("ABORTED", f"ended by Q-HOST: {s.get('reason', '')[:120]}")
        else:
            files = s.get("files") or {}
            on_disk = {g: sha((att / f"{g}.json").read_bytes()) for g in recs}
            v.check("summary_lists_exactly_the_records", set(files) == set(on_disk), "CORRUPT",
                    "the summary's record list differs from the records on disk")
            v.check("summary_hashes_match", all(files.get(g) == h for g, h in on_disk.items()), "CORRUPT",
                    "a record changed after the summary")
            every = s.get("attempt_files_sha256")            # hardened runner: every attempt file is bound
            if every is not None:
                disk_all = {p.name: sha(p.read_bytes()) for p in att.iterdir() if p.is_file()}
                v.check("summary_binds_every_attempt_file", every == disk_all, "CORRUPT",
                        "an attempt file differs from the hash the summary bound")
            gates = s.get("gates") or {}
            want = {"Q" + g[2:]: bool(recs[g].get("pass")) and (not freeze or recs[g].get("freeze_commit") == freeze)
                    for g in recs}
            v.check("summary_gate_table_matches", {k: x for k, x in gates.items() if k != "Q-HOST"} == want, "CORRUPT",
                    "the summary's gate table disagrees with the records")
            exp = len(recs) == len(GATES) and all(want.values()) and gates.get("Q-HOST") is True
            v.check("summary_pass_consistent", s.get("pass") is exp, "CORRUPT", "the summary's pass is inconsistent")
            if len(recs) < len(GATES):
                v.to("CORRUPT", "a summary over an incomplete record set")
            if v.level is None:
                v.level = "COMPLETE_PASS" if exp else "COMPLETE_FAIL"
                if not exp:
                    v.reasons.append("COMPLETE_FAIL: " + ", ".join(
                        [g for g in GATES if g in recs and not recs[g].get("pass")]
                        + ([] if gates.get("Q-HOST") else ["Q-HOST"])))
    elif not summ.exists():
        if aborted:
            v.to("INTERRUPTED", "Q-HOST abort began but its summary was not written (interrupted during the abort)")
        v.to("INTERRUPTED", f"no summary: {len(GATES) - len(present)} record(s) missing"
                            + (f"; first missing {GATES[len(present)]}" if len(present) < len(GATES) else ""))
    if aborts and not aborted:
        v.to("CORRUPT", "the ledger records a Q-HOST abort but the attempt holds no QHOST_FAIL.json")
    return out(v, present, recs, s)


def out(v: V, present, recs, s) -> dict:
    return {"classification": v.level or "CORRUPT", "reasons": v.reasons, "checks": v.checks,
            "gates_present": present, "gates_failed": [g for g in present if g in recs and not recs[g].get("pass")],
            "gates_missing": [g for g in GATES if g not in present]}


def rehearsal(d: Path) -> dict:
    """the rehearsal protocol of code/r2h_rehearse.py: PROVENANCE, GATE_LEDGER (row after record), summary last"""
    v = V()
    if not (d / "PROVENANCE.json").exists():
        v.to("INTERRUPTED", "no provenance (interrupted before the first write)")
        return {"verdict": v.level, "reasons": v.reasons, "checks": v.checks}
    prov = load(d / "PROVENANCE.json", v) or {}
    rows = ledger(d / "GATE_LEDGER.jsonl", v, "gate_ledger")
    psha = sha((d / "PROVENANCE.json").read_bytes())
    v.check("ledger_starts_bound", bool(rows) and rows[0].get("event") == "RUN_START"
            and rows[0].get("provenance_sha256") == psha, "CORRUPT", "the ledger does not start with this run's RUN_START")
    v.check("single_run_start", sum(r.get("event") == "RUN_START" for r in rows) == 1, "CORRUPT",
            "more than one RUN_START (a resumed run)")
    for r in rows:
        if r.get("event") == "INTERRUPTION_DETECTED":
            v.to("INTERRUPTED", f"the rehearsal recorded an interruption: {r.get('detail', '')[:120]}")
    gates = prov.get("gates") or []
    att = d / "attempt"
    tmps = [p.name for p in att.iterdir() if p.is_file() and (p.name.startswith(".") or ".tmp" in p.name)] \
        if att.is_dir() else []
    if tmps:
        v.to("INTERRUPTED", f"leftover temporary file(s) {tmps}")
    recs, present = {}, []
    for g in gates:
        p = att / f"{g}.json"
        if p.exists():
            r = load(p, v)
            if r is not None:
                recs[g] = r
                present.append(g)
                v.check(f"{g}:names_itself", r.get("qc") == g, "CORRUPT", f"{g} names {r.get('qc')}")
                v.check(f"{g}:freeze", r.get("freeze_commit") == prov.get("synthetic_freeze"), "CORRUPT",
                        f"{g} carries a foreign freeze")
    v.check("records_form_a_prefix", present == gates[:len(present)], "CORRUPT", "records are not a prefix")
    seen: dict = {}
    for r in rows:
        if r.get("event") == "GATE_RECORDED":
            g = r.get("gate")
            seen[g] = seen.get(g, 0) + 1
            if g not in recs:
                v.to("CORRUPT", f"ledger row for {g} without its record")
            elif r.get("sha256") != sha((att / f"{g}.json").read_bytes()):
                v.to("CORRUPT", f"{g}: record differs from the hash its ledger row bound")
    v.check("exactly_once_per_gate", all(n == 1 for n in seen.values()), "CORRUPT", "a gate recorded twice")
    for g in present:
        if g not in seen:
            v.to("INTERRUPTED", f"{g}: record without its ledger row (interrupted after the record)")
    summ = d / "REHEARSAL_SUMMARY.json"
    if summ.exists():
        s = load(summ, v) or {}
        v.check("summary_binds_provenance", s.get("provenance_sha256") == psha, "CORRUPT", "summary binds another run")
        v.check("summary_binds_records", s.get("files") == {g: sha((att / f"{g}.json").read_bytes()) for g in recs},
                "CORRUPT", "summary does not bind the records")
        v.check("summary_row_last", bool(rows) and rows[-1].get("event") == "SUMMARY_RECORDED"
                and rows[-1].get("sha256") == sha(summ.read_bytes()), "INTERRUPTED", "summary row missing")
        if len(present) < len(gates):
            v.to("CORRUPT", "summary over an incomplete record set")
    else:
        v.to("INTERRUPTED", f"no summary ({len(gates) - len(present)} record(s) missing)")
    failed = [g for g in present if not recs[g].get("pass")]
    if failed:
        v.to("COMPLETE_FAIL" if v.level is None else v.level, "gate(s) failed: " + ", ".join(failed))
    verdict = "PASS" if v.level is None else ("FAIL" if v.level == "COMPLETE_FAIL" else v.level)
    return {"verdict": verdict, "reasons": v.reasons, "checks": v.checks, "gates": gates, "gates_present": present,
            "gates_failed": failed}


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    a1 = sp.add_parser("status")
    a1.add_argument("qdir")
    a1.add_argument("ledger")
    a1.add_argument("--record-utc")
    a1.add_argument("--freeze")
    a2 = sp.add_parser("rehearsal")
    a2.add_argument("dir")
    for p in (a1, a2):
        p.add_argument("--out")
    a = ap.parse_args()
    res = status(Path(a.qdir), Path(a.ledger), a.record_utc, a.freeze) if a.mode == "status" else rehearsal(Path(a.dir))
    res = {"schema": "P309_R2H_VALIDATION/1", "mode": a.mode, **res}
    text = json.dumps(res, indent=1, sort_keys=True, default=str) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    print(text)
    key = res.get("classification", res.get("verdict"))
    return 0 if key in ("COMPLETE_PASS", "PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
