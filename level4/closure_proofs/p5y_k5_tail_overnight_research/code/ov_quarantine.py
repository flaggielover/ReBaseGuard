"""Target quarantine for the K5 tail overnight research campaign (stdlib only).

Three mechanisms, per config/TARGET_QUARANTINE.json:

* ``guard_cell``      runtime refusal of the target cells (CUSUM m=5, 306-309) and
                      the tail-adjacent cell 305 at every new-route entry point;
* ``install_import_guard``  refuses importing any historical consumer/driver module
                      (so no new code can reach a historical Gamma path by import);
* ``scan``            static scan of every new .py file in this namespace, with a
                      planted negative control that the scan must detect.

``log_execution`` appends one line to ledger/ZERO_TARGET_LEDGER.jsonl.
"""
from __future__ import annotations

import ast
import datetime
import importlib.abc
import json
import re
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
LEDGER = NS / "ledger" / "ZERO_TARGET_LEDGER.jsonl"

TARGET_CELLS = frozenset({306, 307, 308, 309})
ADJACENT_CELLS = frozenset({305})

# Module basenames of historical consumers, drivers and exactly-once CLIs.
FORBIDDEN_MODULES = frozenset({
    "c2_d5_forecast", "c2_execute", "c2_consume", "c2_refined_registry", "c2_recertify_306",
    "c2_critical_ratio", "tail_forecast_r2", "tct_inputs", "tct_rule", "tc_rule", "tc_producer",
    "k5b_literal", "taboo_certify", "c12_cell306", "c12_verify", "c12r1_cell306", "c12r1_verify",
    "c12r2_cell306", "c12r2_verify", "c11r_runs", "c11r_launch", "c11r_compare", "c11r_qualify",
    "c11rd_runs", "c11rd_launch", "c11rd_compare", "closeout_checks", "closeout_checks_r1",
    "closeout_checks_r2",
})

# Paths whose bytes carry target-cell inputs or sealed target results.  Reading them as
# committed text is allowed; feeding them into new-route code is not.
FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"TCT_INPUTS_30[5-9]"),
    re.compile(r"C12R2_CELL306_RESULT"),
    re.compile(r"C12R1_CELL306_RESULT"),
    re.compile(r"REGISTRY_C2"),
    re.compile(r"ADOPTED_TAIL_INPUTS"),
    re.compile(r"C11R_RUNS"),
    re.compile(r"C11RD_.*RUNS"),
)

LITERAL_OK = "ov-quarantine: literal-ok"
# A file whose first 40 lines contain this marker is an AUTHORIZED historical-read script (reading committed target
# values under the historically evaluated supply only, TARGET_QUARANTINE allowed[1]). Its TARGET_INPUT_PATH and
# TARGET_CELL_LITERAL findings are reported as SANCTIONED (listed for review), never silently dropped; a
# FORBIDDEN_IMPORT in such a file still fails the scan.
HISTORICAL_READ_MARK = "ov-quarantine: historical-read"


class QuarantineRefusal(RuntimeError):
    """Raised whenever new-route code would touch a quarantined cell or module."""


def guard_cell(detector: str, m: int, cell: int) -> None:
    """Refuse the target cells and the tail-adjacent cell for any new-route computation."""
    if str(detector).upper() == "CUSUM" and int(m) == 5:
        if int(cell) in TARGET_CELLS:
            raise QuarantineRefusal(f"TARGET_CELL_REFUSED CUSUM m=5 cell {cell}")
        if int(cell) in ADJACENT_CELLS:
            raise QuarantineRefusal(f"ADJACENT_CELL_REFUSED CUSUM m=5 cell {cell}")


# Amendment 1 (config/QUARANTINE_AMENDMENT_1.json): operator quantities depend on the drift only,
# so the tail drift band itself is quarantined, with margin.
from fractions import Fraction as _Fr  # noqa: E402

DRIFT_BAND = (_Fr(6, 5), _Fr(13, 5))


def guard_drift(e_lo, e_hi=None) -> None:
    """Refuse any drift point/interval meeting the quarantined band [6/5, 13/5]."""
    lo = _Fr(e_lo)
    hi = lo if e_hi is None else _Fr(e_hi)
    if hi < lo:
        lo, hi = hi, lo
    # also refuse the mirror band: the kernel is symmetric under e -> -e with p <-> m
    for a, b in (DRIFT_BAND, (-DRIFT_BAND[1], -DRIFT_BAND[0])):
        if not (hi < a or lo > b):
            raise QuarantineRefusal(f"DRIFT_BAND_REFUSED [{float(lo)}, {float(hi)}] meets [{float(a)}, {float(b)}]")


def guard_path(path: str | Path) -> None:
    s = str(path)
    for pat in FORBIDDEN_PATH_PATTERNS:
        if pat.search(s):
            raise QuarantineRefusal(f"TARGET_INPUT_PATH_REFUSED {s}")


class _ImportGuard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):  # noqa: D401
        if fullname.rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
            raise QuarantineRefusal(f"FORBIDDEN_MODULE_IMPORT {fullname}")
        return None


def install_import_guard() -> None:
    if not any(isinstance(f, _ImportGuard) for f in sys.meta_path):
        sys.meta_path.insert(0, _ImportGuard())


# TARGET_QUARANTINE.json allowed[0] (reading) and allowed[1] (HISTORICAL_DECOMPOSITION) are both exempt from
# LEAK_FLAG; review F15 found the exemption keyed on one free-text class only.
HISTORICAL_CLASSES = frozenset({"HISTORICAL_READ", "HISTORICAL_DECOMPOSITION"})


def log_execution(script: str, purpose: str, *, cells_touched: list, klass: str,
                  target_evaluations: int = 0, proxies: int = 0, target_informed_opt: int = 0,
                  notes: str = "") -> dict:
    rec = {
        "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "script": script, "purpose": purpose, "class": klass,
        "cells_touched": cells_touched,
        "new_target_evaluations": target_evaluations,
        "target_equivalent_proxies": proxies,
        "target_informed_optimisation": target_informed_opt,
        "notes": notes,
    }
    for c in cells_touched:
        if isinstance(c, dict) and c.get("detector") == "CUSUM" and c.get("m") == 5 \
                and c.get("cell") in TARGET_CELLS and klass not in HISTORICAL_CLASSES:
            rec["LEAK_FLAG"] = True
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


# ---------------------------------------------------------------- static scan

_CELL_STR = re.compile(r"^\s*30[5-9]\s*$|\bcell\s*30[5-9]\b", re.I)
_FRAC_STR = re.compile(r"^\s*(-?\d+)\s*/\s*(\d+)\s*$")


def _in_band(x) -> bool:
    try:
        v = abs(_Fr(x))
    except (ValueError, TypeError, ZeroDivisionError):
        return False
    return DRIFT_BAND[0] <= v <= DRIFT_BAND[1]


def _mentions_forbidden(text: str) -> bool:
    if any(pat.search(text) for pat in FORBIDDEN_PATH_PATTERNS):
        return True
    return any(re.search(r"\b" + re.escape(m) + r"\b", text) for m in FORBIDDEN_MODULES)


def _strings_in(node) -> list:
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _scan_file(p: Path) -> list[dict]:
    """Findings (fail the scan) plus two report-only kinds:
    SUPPRESSED_LITERAL (a target-cell literal on a literal-ok line; listed, never silent) and
    ATTENTION_DRIFT_LITERAL (a numeric literal inside the quarantined drift band; the runtime guard_drift is the
    barrier, the static list is defence in depth). TARGET_INPUT_PATH is NEVER suppressed by literal-ok (review F3)."""
    src = p.read_text()
    lines = src.splitlines()
    out: list[dict] = []
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:  # a file we cannot parse is itself a finding
        return [{"file": str(p), "line": exc.lineno, "kind": "UNPARSEABLE"}]

    def rec(node, kind, what):
        out.append({"file": str(p), "line": getattr(node, "lineno", 0), "kind": kind, "what": what})

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a_ in node.names:
                if a_.name.rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
                    rec(node, "FORBIDDEN_IMPORT", a_.name)
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").rsplit(".", 1)[-1]
            if mod in FORBIDDEN_MODULES:
                rec(node, "FORBIDDEN_IMPORT", node.module)
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else "")
            if name in ("__import__", "import_module"):
                arg = node.args[0] if node.args else None
                cands = None
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    cands = [arg.value]
                elif isinstance(arg, ast.IfExp) and all(isinstance(x, ast.Constant) and isinstance(x.value, str)
                                                        for x in (arg.body, arg.orelse)):
                    cands = [arg.body.value, arg.orelse.value]   # a conditional between constant module names
                if cands is None:
                    rec(node, "DYNAMIC_IMPORT_UNRESOLVED", ast.dump(fn)[:60])
                else:
                    for c in cands:
                        if c.rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
                            rec(node, "DYNAMIC_FORBIDDEN_IMPORT", c)
            if name in ("run", "Popen", "call", "check_call", "check_output", "system", "execv", "execvp",
                        "spawnv", "run_path"):
                for sv in _strings_in(node):
                    if _mentions_forbidden(sv) or ("level4/closure_proofs/" in sv
                                                   and "p5y_k5_tail_overnight_research" not in sv):
                        rec(node, "SUBPROCESS_FORBIDDEN", sv[:80])
            if name in ("F", "Fraction", "_Fr") and len(node.args) == 2 and all(
                    isinstance(x, ast.Constant) and isinstance(x.value, int) for x in node.args):
                nval, dval = node.args[0].value, node.args[1].value
                if dval and _in_band(_Fr(nval, dval)):
                    line = lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else ""
                    if LITERAL_OK not in line:
                        rec(node, "ATTENTION_DRIFT_LITERAL", f"{nval}/{dval}")
        elif isinstance(node, ast.Constant):
            v = node.value
            line = lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else ""
            ok = LITERAL_OK in line
            if isinstance(v, str):
                for pat in FORBIDDEN_PATH_PATTERNS:
                    if pat.search(v):
                        rec(node, "TARGET_INPUT_PATH", v[:120])       # never suppressed
                if _CELL_STR.search(v):
                    rec(node, "SUPPRESSED_LITERAL" if ok else "TARGET_CELL_STRING", v[:60])
                mfr = _FRAC_STR.match(v)
                if mfr and int(mfr.group(2)) and _in_band(_Fr(int(mfr.group(1)), int(mfr.group(2)))) and not ok:
                    rec(node, "ATTENTION_DRIFT_LITERAL", v)
            elif isinstance(v, int) and not isinstance(v, bool) and v in (TARGET_CELLS | ADJACENT_CELLS):
                rec(node, "SUPPRESSED_LITERAL" if ok else "TARGET_CELL_LITERAL", v)
            elif isinstance(v, float) and _in_band(v) and not ok:
                rec(node, "ATTENTION_DRIFT_LITERAL", v)
    return out


REPORT_ONLY = ("SUPPRESSED_LITERAL", "ATTENTION_DRIFT_LITERAL")


def scan(root: Path = NS) -> dict:
    files = sorted(q for q in root.rglob("*.py") if "__pycache__" not in q.parts)
    findings: list[dict] = []
    sanctioned: list[dict] = []
    report_only: list[dict] = []
    for q in files:
        if q.name == Path(__file__).name:
            continue  # the scanner's own tables are the definitions, not uses
        head = "\n".join(q.read_text().splitlines()[:40])
        fs = _scan_file(q)
        report_only.extend(f for f in fs if f["kind"] in REPORT_ONLY)
        fs = [f for f in fs if f["kind"] not in REPORT_ONLY]
        if HISTORICAL_READ_MARK in head:
            sk = ("TARGET_INPUT_PATH", "TARGET_CELL_LITERAL", "TARGET_CELL_STRING")
            sanctioned.extend(f for f in fs if f["kind"] in sk)
            findings.extend(f for f in fs if f["kind"] not in sk)
        else:
            findings.extend(fs)
    # Negative control (multi-shape, review F3): a planted file must be detected in EVERY shape.
    planted = "\n".join([
        "import tail_forecast_r2",
        "import importlib, subprocess",
        "importlib.import_module('tct_rule')",
        "__import__('c2_d5_forecast')",
        "subprocess.run(['python3', 'x/k5b_literal.py'])",
        "x = 307",
        "y = 'cell 308'",
        "p = 'evidence/TCT_INPUTS_309.json'",
        "q = 'evidence/TCT_INPUTS_306.json'  # " + LITERAL_OK + " (a path must never be suppressed)",
        "z = 1.75",
        "w = F(7, 4)",
        "u = 306  # " + LITERAL_OK + " (reported as suppressed, not silent)",
    ]) + "\n"
    tmp = NS / "ledger" / ".scan_negative_control.py"
    tmp.write_text(planted)
    try:
        ctrl = _scan_file(tmp)
    finally:
        tmp.unlink()
    kinds = sorted({f["kind"] for f in ctrl})
    expected = sorted({"FORBIDDEN_IMPORT", "DYNAMIC_FORBIDDEN_IMPORT", "SUBPROCESS_FORBIDDEN", "TARGET_CELL_LITERAL",
                       "TARGET_CELL_STRING", "TARGET_INPUT_PATH", "ATTENTION_DRIFT_LITERAL", "SUPPRESSED_LITERAL"})
    n_paths = sum(1 for f in ctrl if f["kind"] == "TARGET_INPUT_PATH")
    control_ok = kinds == expected and n_paths == 2 and sum(1 for f in ctrl if f["kind"] == "ATTENTION_DRIFT_LITERAL") == 2
    return {
        "files_scanned": len(files) - 1,
        "file_list": [str(q.relative_to(root)) for q in files if q.name != Path(__file__).name],
        "findings": findings,
        "sanctioned_historical_read": [{"file": f["file"], "line": f["line"], "kind": f["kind"]} for f in sanctioned],
        "sanctioned_files": sorted({f["file"] for f in sanctioned}),
        "negative_control_kinds": kinds,
        "negative_control_expected": expected,
        "report_only": report_only,
        "report_only_counts": {k: sum(1 for f in report_only if f["kind"] == k) for k in REPORT_ONLY},
        "limits": ("static AST scan: cannot see values computed at run time, paths built by string operations, or "
                   "drifts passed as variables; the runtime guards (guard_cell, guard_drift, import guard) and the "
                   "input-path discipline are the primary barriers"),
        "negative_control_detected": control_ok,
        "verdict": "PASS" if (control_ok and not findings) else ("CONTROL_FAILED" if not control_ok else "FINDINGS"),
    }


def _selftest() -> None:
    for c in (305, 306, 307, 308, 309):
        try:
            guard_cell("CUSUM", 5, c)  # ov-quarantine: literal-ok self-test of the refusal
        except QuarantineRefusal:
            continue
        raise AssertionError(f"guard_cell failed to refuse {c}")
    guard_cell("SR", 5, 307)  # ov-quarantine: literal-ok SR cells are not targets
    guard_cell("CUSUM", 3, 307)  # ov-quarantine: literal-ok other m are not targets
    guard_cell("CUSUM", 5, 44)
    for e in ("1.2", "7/4", "2.6", "-2"):
        try:
            guard_drift(_Fr(e))
        except QuarantineRefusal:
            continue
        raise AssertionError(f"guard_drift failed to refuse {e}")
    guard_drift(_Fr(1, 2), 1)
    guard_drift(3)
    try:
        guard_drift(1, 3)  # interval straddling the band
    except QuarantineRefusal:
        pass
    else:
        raise AssertionError("guard_drift failed to refuse a straddling interval")
    install_import_guard()
    try:
        __import__("tail_forecast_r2")
    except QuarantineRefusal:
        pass
    else:
        raise AssertionError("import guard failed")
    print("ov_quarantine selftest PASS")


if __name__ == "__main__":
    if "--scan" in sys.argv:
        print(json.dumps(scan(), indent=1))
    else:
        _selftest()
