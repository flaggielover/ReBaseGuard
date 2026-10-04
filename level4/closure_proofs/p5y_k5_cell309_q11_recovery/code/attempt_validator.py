#!/usr/bin/env python3
"""Independent validator for P309 qualification attempts and rehearsals (imports nothing from r1 / r2 code).

  python3 attempt_validator.py r1-attempt  ATTEMPT_DIR LEDGER [--summary FILE] [--freeze F] [--record-utc T]
  python3 attempt_validator.py rehearsal   OUT_DIR
  python3 attempt_validator.py certs       DECOY_STAGE1A.json [more ...]     (QC08 / QC10 certificate identity)
  every mode: [--out FILE]  -> JSON verdict;  exit 0 iff the verdict is PASS

The verdict is derived from CONTENT, never from a process exit code: every record must parse, name itself, carry the
expected freeze, appear in the runner's order with monotone times, agree with the ledger (exactly one record per
gate, never a ledger row before its record, hashes equal), and the summary must exist and list exactly the records
on disk by sha256.  Gate-specific evidence is checked where the attempt holds it (QC10 certificates re-hashed, the
QC11 flow table, the QC-D5 parts, the QC13 checks).  Classifications:
  PASS          complete, consistent, every gate passes on its evidence
  FAIL          complete and consistent, a gate fails
  INTERRUPTED   consistent but incomplete (records missing, summary missing, a leftover temporary file)
  CORRUPT       inconsistent: torn / empty / unparseable record or ledger row, wrong order, hash or freeze mismatch,
                duplicate record, ledger row without its record, summary disagreeing with the records, mixed provenance
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

GATES = ["QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09", "QC10", "QC11", "QC12", "QC13",
         "QC14", "QC15", "QC16", "QC17", "QC_U2", "QC_D5"]
AUX = {"QC08_DECOY_STAGE1A.json", "QC09_DECOY_STAGE1B_297.json", "QC09_DECOY_STAGE1B_316.json",
       "QC10_DECOY_STAGE1A.json", "QC14_REHEARSE.json"}
FREEZE_F = "4c754a73767903a5ad5dddff725f1e173a0a6876"
RUN_START = "QUALIFICATION RUN START"
COUNTERS = ("new_target_evaluations", "target_equivalent_proxies", "target_informed_optimisation")
EXPECTED_CERTS = 48


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def ts(s) -> datetime.datetime | None:
    if not isinstance(s, str):
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


class Verdict:
    ORDER = {"PASS": 0, "FAIL": 1, "INTERRUPTED": 2, "CORRUPT": 3}

    def __init__(self):
        self.level, self.reasons, self.checks = "PASS", [], {}

    def raise_to(self, level: str, why: str) -> None:
        self.reasons.append(f"{level}: {why}")
        if self.ORDER[level] > self.ORDER[self.level]:
            self.level = level

    def check(self, name: str, ok: bool, level: str = "CORRUPT", why: str = "") -> bool:
        self.checks[name] = bool(ok)
        if not ok:
            self.raise_to(level, why or name)
        return ok

    def out(self, **extra) -> dict:
        return {"verdict": self.level, "reasons": self.reasons, "checks": self.checks, **extra}


def load_json(p: Path, v: Verdict, name: str) -> dict | None:
    raw = p.read_bytes()
    if not raw:
        v.raise_to("CORRUPT", f"{name}: empty file (torn write)")
        return None
    try:
        d = json.loads(raw)
    except ValueError as exc:
        v.raise_to("CORRUPT", f"{name}: unparseable ({exc.msg} at {exc.pos} of {len(raw)} bytes; torn write)")
        return None
    if not isinstance(d, dict):
        v.raise_to("CORRUPT", f"{name}: not a JSON object")
        return None
    return d


# ------------------------------------------------------------------------------------- certificate identity
def cert_identity(paths: list[Path]) -> dict:
    v, sets, per = Verdict(), [], {}
    for p in paths:
        d = load_json(p, v, p.name)
        if d is None:
            continue
        certs = d.get("certificates") or []
        bad_self = [c.get("sha256") for c in certs
                    if sha(json.dumps({k: x for k, x in c.items() if k != "sha256"}, sort_keys=True).encode())
                    != c.get("sha256")]
        hs = sorted(c.get("sha256") for c in certs)
        verdicts = d.get("verdicts") or {}
        gate = d.get("gate") or {}
        per[p.name] = {"certificates": len(certs), "distinct": len(set(hs)), "self_hash_mismatches": len(bad_self),
                       "all_certified": all(c.get("status") == "CERTIFIED" for c in certs),
                       "verdicts_cover_certs": set(verdicts) == set(hs),
                       "all_accept": set(verdicts.values()) == {"ACCEPT"},
                       "gate_source": gate.get("source"), "gate_admitted_equals_certs": sorted(gate.get("admitted") or []) == hs,
                       "gate_refused": gate.get("report", {}).get("refused"),
                       "verdict_source": gate.get("verdict_source"),
                       "jobs_returned": sum(1 for j in (d.get("jobs") or {}).values() if j.get("kind") == "JOB_RETURNED"),
                       "set_sha256": sha("\n".join(hs).encode()), "file_sha256": sha(p.read_bytes())}
        x = per[p.name]
        v.check(f"{p.name}:count", x["certificates"] == EXPECTED_CERTS and x["distinct"] == EXPECTED_CERTS, "FAIL",
                f"{p.name}: {x['certificates']} certificates ({x['distinct']} distinct), expected {EXPECTED_CERTS}")
        v.check(f"{p.name}:self_hash", not bad_self, "CORRUPT", f"{p.name}: certificate self-hash mismatch")
        v.check(f"{p.name}:certified_accept_gate", x["all_certified"] and x["verdicts_cover_certs"] and x["all_accept"]
                and x["gate_source"] == "GATE" and x["gate_admitted_equals_certs"] and not x["gate_refused"]
                and x["jobs_returned"] == 12, "FAIL", f"{p.name}: certificate status / verdict / gate inconsistency")
        sets.append(hs)
    v.check("byte_identical_across_files", len(sets) == len(paths) and all(s == sets[0] for s in sets), "FAIL",
            "certificate sets differ between runs")
    srcs = {x["verdict_source"] for x in per.values()}
    v.check("single_verdict_source", len(srcs) == 1, "FAIL", f"verdict sources differ: {srcs}")
    return v.out(files=per)


# ------------------------------------------------------------------------------------------- gate evidence
GATE_EVIDENCE = {"on": True}      # --no-gate-evidence: structural checks only (synthetic crash-matrix gates)


def gate_evidence(gate: str, rec: dict, base: Path, v: Verdict) -> None:
    """gate-specific evidence from content (where the attempt holds it), and record / run-status consistency"""
    if not GATE_EVIDENCE["on"]:
        return
    if gate == "QC10":
        aux = [base / "QC08_DECOY_STAGE1A.json", base / "QC10_DECOY_STAGE1A.json"]
        if all(p.exists() for p in aux):
            ci = cert_identity(aux)
            v.checks["QC10:independent_certificate_identity"] = ci["verdict"] == "PASS"
            if ci["verdict"] != "PASS":
                v.raise_to("FAIL", f"QC10 independent certificate identity: {ci['reasons'][:2]}")
            v.checks["QC10:certificates"] = ci["files"]["QC10_DECOY_STAGE1A.json"]["certificates"]
        else:
            v.raise_to("CORRUPT", "QC10 record without its decoy outputs")
    elif gate == "QC11":
        f = base / "evidence" / "fc6" / "EXACTLY_ONCE_FLOWS.json"
        if f.exists():
            d = load_json(f, v, "EXACTLY_ONCE_FLOWS.json") or {}
            flows = {k: x for k, x in d.items() if isinstance(x, dict) and "pass" in x}
            bad = sorted(k for k, x in flows.items() if not x.get("pass"))
            v.checks["QC11:flows"] = len(flows)
            v.checks["QC11:flows_failed"] = bad
            if rec.get("pass") and (bad or not flows):
                v.raise_to("CORRUPT", f"QC11 record says pass but its flow table has failures {bad[:5]} / no flows")
            if not rec.get("pass") and not bad and flows and d.get("pass") is True:
                v.raise_to("CORRUPT", "QC11 record says fail but its flow table passes")
        else:
            v.checks["QC11:flows"] = "no flow table (the harness crashed before writing it)"
    elif gate == "QC_D5":
        parts = rec.get("parts") or []
        v.checks["QC_D5:parts"] = [bool(x.get("pass")) for x in parts]
        tails = " ".join(r.get("stdout_tail", "") for x in parts for r in x.get("runs", []))
        if rec.get("pass") and (len(parts) != 3 or not all(x.get("pass") for x in parts)
                                or "P309 SCAN PINS: all current" not in tails):
            v.raise_to("CORRUPT", "QC_D5 record says pass but a part fails or the pin list is not current")
    elif gate == "QC13":
        c = rec.get("checks") or {}
        v.checks["QC13:checks_false"] = sorted(k for k, x in c.items() if x is not True)
        if rec.get("pass") and (not c or not all(x is True for x in c.values())):
            v.raise_to("CORRUPT", "QC13 record says pass but a check is not true")
    elif gate == "QC17":
        if rec.get("pass") and not (rec.get("mismatches") == 0 and rec.get("cases") == 2000):
            v.raise_to("CORRUPT", "QC17 record says pass without 0 / 2000 mismatches")
    elif gate in ("QC16", "QC_U2"):
        if rec.get("pass") and not all(x.get("pass") for x in rec.get("parts") or [{}]):
            v.raise_to("CORRUPT", f"{gate} record says pass but a part fails")
    runs = rec.get("runs") or [r for x in rec.get("parts") or [] for r in x.get("runs", [])]
    if rec.get("pass") and runs and any(r.get("rc") != 0 for r in runs):
        v.raise_to("CORRUPT", f"{gate} record says pass but one of its runs exited non-zero")
    if not rec.get("pass") and runs and all(r.get("rc") == 0 for r in runs) and gate not in (
            "QC05", "QC06", "QC08", "QC09", "QC10", "QC13", "QC14"):
        v.raise_to("CORRUPT", f"{gate} record says fail but every run exited 0 (no content reason)")


def check_records(att: Path, v: Verdict, freeze: str, allow_extra=()) -> tuple[dict, list]:
    names = sorted(p.name for p in att.iterdir() if p.is_file())
    tmps = [n for n in names if n.startswith(".") or n.endswith((".tmp", ".partial")) or ".tmp-" in n]
    if tmps:
        v.raise_to("INTERRUPTED", f"leftover temporary files {tmps} (an interrupted write)")
    unknown = [n for n in names if n not in tmps and n not in AUX and n not in allow_extra
               and n[:-5] not in GATES]
    v.check("no_unknown_files", not unknown, "CORRUPT", f"unknown files in the attempt: {unknown}")
    recs, present = {}, []
    for g in GATES:
        p = att / f"{g}.json"
        if not p.exists():
            continue
        present.append(g)
        d = load_json(p, v, p.name)
        if d is None:
            continue
        v.check(f"{g}:names_itself", d.get("qc") == g, "CORRUPT", f"{g}.json names {d.get('qc')}")
        v.check(f"{g}:freeze", d.get("freeze_commit") == freeze, "CORRUPT",
                f"{g}.json freeze {d.get('freeze_commit')} != {freeze} (stale or foreign record)")
        v.check(f"{g}:pass_is_bool", isinstance(d.get("pass"), bool), "CORRUPT", f"{g}.json pass is not a bool")
        v.check(f"{g}:utc", ts(d.get("utc")) is not None, "CORRUPT", f"{g}.json utc unreadable")
        recs[g] = d
        gate_evidence(g, d, att, v)
    # order: the runner writes in GATES order, so the present set is a prefix and times are monotone
    v.check("records_form_a_prefix", present == GATES[:len(present)], "CORRUPT",
            f"records are not a prefix of the runner's order: {present}")
    times = [ts(recs[g]["utc"]) for g in present if g in recs and ts(recs[g].get("utc"))]
    v.check("record_times_monotone", all(a <= b for a, b in zip(times, times[1:])), "CORRUPT",
            "record times are not monotone in the runner's order")
    if len(present) < len(GATES):
        v.raise_to("INTERRUPTED", f"{len(GATES) - len(present)} gate record(s) missing; first missing "
                                  f"{GATES[len(present)] if present == GATES[:len(present)] else '?'}")
    return recs, present


def summary_check(summ: Path, att: Path, recs: dict, v: Verdict, freeze: str, n_expected: int, files_key="files",
                  gates_key="gates", gate_name=lambda g: "Q" + g[2:]) -> dict | None:
    if not summ.exists():
        v.raise_to("INTERRUPTED", "no summary (the run did not finish)")
        return None
    s = load_json(summ, v, summ.name)
    if s is None:
        return None
    v.check("summary:freeze", s.get("freeze_commit") == freeze, "CORRUPT", "summary freeze mismatch")
    listed = s.get(files_key) or {}
    on_disk = {g: sha((att / f"{g}.json").read_bytes()) for g in recs}
    v.check("summary:lists_exactly_the_records", set(listed) == set(on_disk), "CORRUPT",
            f"summary lists {sorted(set(listed) ^ set(on_disk))[:5]} differently from disk")
    v.check("summary:hashes_match", all(listed.get(g) == h for g, h in on_disk.items()), "CORRUPT",
            "a record changed after the summary (sha256 mismatch)")
    gates = s.get(gates_key) or {}
    want = {gate_name(g): bool(recs[g].get("pass")) and recs[g].get("freeze_commit") == freeze for g in recs}
    v.check("summary:gate_table_matches_records", gates == want, "CORRUPT", "summary gate table disagrees")
    expected_pass = len(recs) == n_expected and all(want.values())
    v.check("summary:pass_consistent", s.get("pass") is expected_pass, "CORRUPT",
            f"summary pass {s.get('pass')} inconsistent with its records (expected {expected_pass})")
    return s


def ledger_rows(p: Path, v: Verdict, name: str) -> list[dict]:
    rows = []
    if not p.exists():
        v.raise_to("CORRUPT", f"{name} missing")
        return rows
    raw = p.read_bytes()
    if raw and not raw.endswith(b"\n"):
        v.raise_to("CORRUPT", f"{name}: last row has no newline (torn append)")
    for i, line in enumerate(raw.decode(errors="replace").splitlines()):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            v.raise_to("CORRUPT", f"{name}: row {i + 1} unparseable (torn append)")
    bad = [r for r in rows if any(r.get(k, 0) != 0 for k in COUNTERS)]
    v.check(f"{name}:target_counters_zero", not bad, "CORRUPT", f"{name}: {len(bad)} row(s) with a nonzero target counter")
    v.checks[f"{name}:rows"] = len(rows)
    return rows


# --------------------------------------------------------------------------------------------- the modes
def r1_attempt(att: Path, ledger: Path, summ: Path | None, freeze: str, record_utc: str | None) -> dict:
    v = Verdict()
    if not att.is_dir():
        v.raise_to("CORRUPT", "no attempt directory")
        return v.out()
    rows = ledger_rows(ledger, v, "execution_ledger")
    t0 = ts(record_utc) if record_utc else None
    starts = [r for r in rows if str(r.get("purpose", "")).startswith(RUN_START) and (t0 is None or ts(r.get("utc")) and ts(r["utc"]) >= t0)]
    v.checks["run_start_lines"] = len(starts)
    recs, present = check_records(att, v, freeze)
    if not starts:
        v.raise_to("INTERRUPTED" if not present else "CORRUPT",
                   "the attempt directory exists without a RUN START ledger line (interrupted before start)"
                   if not present else "records exist without a RUN START ledger line")
    v.check("single_run_start", len(starts) <= 1, "CORRUPT", f"{len(starts)} RUN START lines (a resumed or repeated run)")
    if starts and present:
        v.check("run_start_before_first_record", ts(starts[0]["utc"]) <= ts(recs[present[0]]["utc"]), "CORRUPT",
                "a record predates the RUN START line")
        last = max(ts(r.get("utc")) for r in rows if ts(r.get("utc")))
        last_rec = ts(recs[present[-1]]["utc"]) if present[-1] in recs else None
        v.checks["ledger_activity_after_last_record"] = bool(last_rec and last > last_rec)
    summary = summ if summ else att.parent / "P309_QUALIFICATION.json"
    summary_check(summary, att, recs, v, freeze, len(GATES))
    if all(g in recs for g in GATES) and not all(recs[g].get("pass") for g in GATES):
        v.raise_to("FAIL", "gate(s) failed: " + ", ".join(g for g in GATES if not recs[g].get("pass")))
    elif recs and not all(r.get("pass") for r in recs.values()):
        v.raise_to("FAIL", "gate(s) failed: " + ", ".join(g for g in GATES if g in recs and not recs[g].get("pass")))
    return v.out(gates_present=present, gates_passed=[g for g in present if recs.get(g, {}).get("pass")],
                 gates_failed=[g for g in present if g in recs and not recs[g].get("pass")],
                 gates_missing=[g for g in GATES if g not in present])


def rehearsal(out: Path) -> dict:
    v = Verdict()
    prov = load_json(out / "PROVENANCE.json", v, "PROVENANCE.json") if (out / "PROVENANCE.json").exists() else None
    if prov is None:
        v.raise_to("INTERRUPTED", "no provenance record (interrupted before the first write)")
        return v.out()
    freeze = prov.get("recorded_freeze")
    v.check("provenance:freeze_is_F", freeze == FREEZE_F, "CORRUPT", f"provenance freeze {freeze}")
    v.check("provenance:target_zero", prov.get("new_target_evaluations") == 0, "CORRUPT", "provenance counter")
    gates_req = prov.get("gates") or []
    rows = ledger_rows(out / "GATE_LEDGER.jsonl", v, "gate_ledger")
    v.check("ledger:starts_with_run_start", bool(rows) and rows[0].get("event") == "RUN_START", "CORRUPT",
            "the gate ledger does not start with RUN_START")
    if rows and rows[0].get("event") == "RUN_START":
        v.check("ledger:binds_provenance", rows[0].get("provenance_sha256") == sha((out / "PROVENANCE.json").read_bytes()),
                "CORRUPT", "RUN_START does not bind this provenance (mixed provenance)")
    v.check("ledger:single_run_start", sum(r.get("event") == "RUN_START" for r in rows) == 1, "CORRUPT",
            "more than one RUN_START (a resumed run)")
    att = out / "attempt"
    recs, present = {}, []
    for p in sorted(att.iterdir()) if att.is_dir() else []:
        if p.is_file() and (p.name.startswith(".") or ".tmp-" in p.name):
            v.raise_to("INTERRUPTED", f"leftover temporary file {p.name} (interrupted during a record write)")
    for g in gates_req:
        p = att / f"{g}.json"
        if p.exists():
            d = load_json(p, v, p.name)
            if d is not None:
                recs[g] = d
                present.append(g)
                v.check(f"{g}:names_itself", d.get("qc") == g, "CORRUPT", f"{g} names {d.get('qc')}")
                v.check(f"{g}:freeze", d.get("freeze_commit") == freeze, "CORRUPT", f"{g} foreign freeze")
                if g in ("QC11", "QC_D5"):
                    v.check(f"{g}:harness_matches_provenance", d.get("harness") == prov.get("harness"), "CORRUPT",
                            f"{g} ran with harness {d.get('harness')}, provenance says {prov.get('harness')}")
                gate_evidence(g, d, att, v)
    v.check("records_form_a_prefix", present == gates_req[:len(present)], "CORRUPT",
            f"records are not a prefix of the requested order: {present}")
    grows = [r for r in rows if r.get("event") == "GATE_RECORDED"]
    seen: dict = {}
    for r in grows:
        seen[r.get("gate")] = seen.get(r.get("gate"), 0) + 1
    v.check("ledger:exactly_once_per_gate", all(n == 1 for n in seen.values()), "CORRUPT",
            f"duplicate ledger rows {[g for g, n in seen.items() if n > 1]}")
    for r in grows:
        g = r.get("gate")
        if g not in recs:
            v.raise_to("CORRUPT", f"ledger row for {g} without its record (row before record)")
        elif r.get("sha256") != sha((att / f"{g}.json").read_bytes()):
            v.raise_to("CORRUPT", f"{g}: record differs from the hash its ledger row bound (rewritten / foreign)")
        elif bool(r.get("pass")) != bool(recs[g].get("pass")):
            v.raise_to("CORRUPT", f"{g}: ledger pass differs from the record")
    for g in present:
        if g not in seen:
            v.raise_to("INTERRUPTED", f"{g}: complete record without its ledger row (interrupted after the record)")
    v.check("ledger:row_order", [r.get("gate") for r in grows] == [g for g in gates_req if g in seen], "CORRUPT",
            "ledger rows out of the requested order")
    if len(present) < len(gates_req):
        v.raise_to("INTERRUPTED", f"{len(gates_req) - len(present)} gate record(s) missing")
    s = None
    if (out / "REHEARSAL_SUMMARY.json").exists():
        s = summary_check(out / "REHEARSAL_SUMMARY.json", att, recs, v, freeze, len(gates_req), gate_name=lambda g: g)
        if s is not None:
            v.check("summary:binds_provenance", s.get("provenance_sha256") == sha((out / "PROVENANCE.json").read_bytes()),
                    "CORRUPT", "summary binds another provenance")
            v.check("summary:requested_gates", s.get("gates_requested") == gates_req, "CORRUPT", "summary gate list")
            v.check("summary:no_replica_refs", s.get("replica_protected_refs_after") == [], "CORRUPT",
                    "protected refs in the replica after the run")
            last = rows[-1] if rows else {}
            v.check("ledger:summary_row_last", last.get("event") == "SUMMARY_RECORDED" and
                    last.get("sha256") == sha((out / "REHEARSAL_SUMMARY.json").read_bytes()), "INTERRUPTED",
                    "summary written but its ledger row is missing (interrupted after the summary)")
    else:
        v.raise_to("INTERRUPTED", "no summary (the run did not finish)")
    if recs and not all(r.get("pass") for r in recs.values()):
        v.raise_to("FAIL", "gate(s) failed: " + ", ".join(g for g in gates_req if g in recs and not recs[g].get("pass")))
    return v.out(gates_requested=gates_req, gates_present=present,
                 gates_passed=[g for g in present if recs[g].get("pass")],
                 gates_failed=[g for g in present if not recs[g].get("pass")], harness=prov.get("harness"),
                 replica_head=prov.get("head"), runtime=prov.get("runtime"))


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    a1 = sp.add_parser("r1-attempt")
    a1.add_argument("attempt")
    a1.add_argument("ledger")
    a1.add_argument("--summary")
    a1.add_argument("--freeze", default=FREEZE_F)
    a1.add_argument("--record-utc", help="freeze record commit time; RUN START lines before it are ignored")
    a2 = sp.add_parser("rehearsal")
    a2.add_argument("out_dir")
    a3 = sp.add_parser("certs")
    a3.add_argument("files", nargs="+")
    for p in (a1, a2, a3):
        p.add_argument("--out")
        p.add_argument("--no-gate-evidence", action="store_true")
    a = ap.parse_args()
    GATE_EVIDENCE["on"] = not a.no_gate_evidence
    if a.mode == "r1-attempt":
        res = r1_attempt(Path(a.attempt), Path(a.ledger), Path(a.summary) if a.summary else None, a.freeze,
                         a.record_utc)
    elif a.mode == "rehearsal":
        res = rehearsal(Path(a.out_dir))
    else:
        res = cert_identity([Path(f) for f in a.files])
    res = {"schema": "P309_ATTEMPT_VALIDATION/1", "mode": a.mode, "gate_evidence_checked": GATE_EVIDENCE["on"], **res}
    text = json.dumps(res, indent=1, sort_keys=True, default=str) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    print(text if a.no_gate_evidence else json.dumps({k: res[k] for k in ("verdict", "reasons") if k in res}, indent=1))
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
