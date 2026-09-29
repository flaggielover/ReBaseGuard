"""Target quarantine for the K5 cell-309 research campaign r1 (stdlib only).

Written fresh for this campaign (modelled on, not copied from, the overnight ``ov_quarantine``).
Policy: config/TARGET_QUARANTINE_309.json.

* ``guard_cell``   refuses CUSUM m=5 cells 305-309 at every new-route entry point;
* ``guard_drift``  refuses any drift point/interval meeting [6/5, 13/5] or its mirror;
* ``guard_path``   refuses feeding target-cell input files or sealed results into new code;
* ``install_import_guard`` refuses importing historical consumers, drivers and exactly-once CLIs;
* ``scan``         static scan of this namespace's .py files with a planted negative control;
* ``log_execution`` / ``log_exposure`` append to the two ledgers.

Run ``python3 q309_guard.py --scan`` to scan; it exits non-zero on any finding or if the
planted control does not fire.
"""
from __future__ import annotations

import ast
import datetime
import importlib.abc
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
EXEC_LEDGER = NS / "ledger" / "ZERO_TARGET_LEDGER.jsonl"
EXPOSURE_LEDGER = NS / "ledger" / "EXPOSURE_LEDGER.jsonl"

QUARANTINED_CELLS = frozenset({305, 306, 307, 308, 309})
DRIFT_BAND = (Fraction(6, 5), Fraction(13, 5))

FORBIDDEN_MODULES = frozenset({
    # historical consumers / forecast / drivers (overnight list, carried over)
    "c2_d5_forecast", "c2_execute", "c2_consume", "c2_refined_registry", "c2_recertify_306",
    "c2_critical_ratio", "tail_forecast_r2", "tct_inputs", "tct_rule", "tc_rule", "tc_producer",
    "k5b_literal", "deflated_consume", "taboo_certify", "c12_cell306", "c12_verify", "c12r1_cell306",
    "c12r1_verify", "c12r2_cell306", "c12r2_verify", "c11r_runs", "c11r_launch", "c11r_compare",
    "c11r_qualify", "c11rd_runs", "c11rd_launch", "c11rd_compare", "closeout_checks",
    "closeout_checks_r1", "closeout_checks_r2",
    # cell-307 RLR r1 exactly-once machinery
    "rlr307_driver", "rlr307_stage1", "rlr307_pinned", "rlr307_independent", "rlr307_qualify",
    "rlr307_guard",
})

FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"TCT_INPUTS_30[5-9]"),
    re.compile(r"C12R[12]?_CELL306_RESULT"),
    re.compile(r"REGISTRY_C2"),
    re.compile(r"ADOPTED_TAIL_INPUTS"),
    re.compile(r"C11RD?_.*RUNS"),
    re.compile(r"RLR307_(RESULT|GRANT|FREEZE)"),
    re.compile(r"pending-result|target-consumed"),
    re.compile(r"cell_?308", re.I),
)

LITERAL_OK = "q309: literal-ok"          # a documented, non-data use of a cell literal (e.g. in a refusal test)
CONTROL_MARK = "q309: planted-control"   # the planted negative control file
REFUSAL_TEST_MARK = "q309: refusal-test"  # a test whose only use of forbidden names is to assert they are refused;
                                          # its findings are LISTED as sanctioned, never silently dropped


class QuarantineRefusal(RuntimeError):
    """Raised whenever new code would touch a quarantined cell, drift, path or module."""


def guard_cell(detector: str, m: int, cell: int) -> None:
    if str(detector).upper() == "CUSUM" and int(m) == 5 and int(cell) in QUARANTINED_CELLS:
        raise QuarantineRefusal(f"QUARANTINED_CELL_REFUSED CUSUM m=5 cell {int(cell)}")


def guard_drift(e_lo, e_hi=None) -> None:
    lo = Fraction(e_lo)
    hi = lo if e_hi is None else Fraction(e_hi)
    if hi < lo:
        lo, hi = hi, lo
    for a, b in (DRIFT_BAND, (-DRIFT_BAND[1], -DRIFT_BAND[0])):
        if not (hi < a or lo > b):
            raise QuarantineRefusal(f"DRIFT_BAND_REFUSED [{float(lo)}, {float(hi)}] meets [{float(a)}, {float(b)}]")


def guard_path(path) -> None:
    s = str(path)
    for pat in FORBIDDEN_PATH_PATTERNS:
        if pat.search(s):
            raise QuarantineRefusal(f"TARGET_PATH_REFUSED {s}")


class _ImportGuard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
            raise QuarantineRefusal(f"FORBIDDEN_MODULE_IMPORT {fullname}")
        return None


def install_import_guard() -> None:
    if not any(isinstance(f, _ImportGuard) for f in sys.meta_path):
        sys.meta_path.insert(0, _ImportGuard())


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_execution(script: str, purpose: str, *, klass: str, drifts: list | None = None,
                  cells_touched: list | None = None, notes: str = "") -> dict:
    """One line per potentially sensitive execution. Target counters are always 0 by construction;
    any quarantined cell in cells_touched raises instead of logging."""
    for c in cells_touched or []:
        guard_cell(c.get("detector", "CUSUM"), c.get("m", 5), c["cell"])
    for d in drifts or []:
        guard_drift(*d) if isinstance(d, (list, tuple)) else guard_drift(d)
    rec = {"utc": _now(), "script": script, "purpose": purpose, "class": klass,
           "drifts": [[str(x) for x in (d if isinstance(d, (list, tuple)) else [d])] for d in drifts or []],
           "cells_touched": cells_touched or [], "new_target_evaluations": 0,
           "target_equivalent_proxies": 0, "target_informed_optimisation": 0, "notes": notes}
    EXEC_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with EXEC_LEDGER.open("a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def log_exposure(reader: str, ref: str, path: str, *, content: str, necessity: str, carried_309_numbers: bool) -> dict:
    rec = {"utc": _now(), "reader": reader, "ref": ref, "path": path, "content_class": content,
           "necessity": necessity, "carried_309_numeric_values": carried_309_numbers}
    EXPOSURE_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with EXPOSURE_LEDGER.open("a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


# ------------------------------------------------------------------------------------------ static scan

_CELL_STR = re.compile(r"^\s*30[5-9]\s*$|\bcell[\s_=:]*30[5-9]\b", re.I)


def _in_band(x) -> bool:
    try:
        v = abs(Fraction(x))
    except (ValueError, TypeError, ZeroDivisionError):
        return False
    return DRIFT_BAND[0] <= v <= DRIFT_BAND[1]


def _scan_file(p: Path) -> list[dict]:
    src = p.read_text()
    lines = src.splitlines()
    out: list[dict] = []
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [{"file": str(p), "line": exc.lineno, "kind": "UNPARSEABLE"}]

    def rec(node, kind, what):
        ln = getattr(node, "lineno", 0)
        ok = 0 < ln <= len(lines) and LITERAL_OK in lines[ln - 1]
        out.append({"file": str(p.relative_to(NS)), "line": ln, "kind": kind, "what": str(what)[:80],
                    "suppressed": bool(ok and kind in ("CELL_LITERAL", "BAND_LITERAL"))})

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
                    rec(node, "FORBIDDEN_IMPORT", a.name)
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
                rec(node, "FORBIDDEN_IMPORT", node.module)
        elif isinstance(node, ast.Constant):
            v = node.value
            if isinstance(v, bool):
                continue
            if isinstance(v, int) and v in QUARANTINED_CELLS:
                rec(node, "CELL_LITERAL", v)
            elif isinstance(v, str):
                if _CELL_STR.search(v):
                    rec(node, "CELL_LITERAL", v)
                if any(pat.search(v) for pat in FORBIDDEN_PATH_PATTERNS):
                    rec(node, "TARGET_PATH", v)
                if re.fullmatch(r"\s*-?\d+\s*/\s*\d+\s*", v) and _in_band(v.replace(" ", "")):
                    rec(node, "BAND_LITERAL", v)
            elif isinstance(v, float) and _in_band(v):
                rec(node, "BAND_LITERAL", v)
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else "")
            if name == "Fraction" and len(node.args) == 2 and all(
                    isinstance(a, ast.Constant) and isinstance(a.value, int) for a in node.args):
                if node.args[1].value != 0 and _in_band(Fraction(node.args[0].value, node.args[1].value)):
                    rec(node, "BAND_LITERAL", f"Fraction({node.args[0].value},{node.args[1].value})")
            if name in ("__import__", "import_module"):
                a0 = node.args[0] if node.args else None
                if not (isinstance(a0, ast.Constant) and isinstance(a0.value, str)):
                    rec(node, "DYNAMIC_IMPORT_UNRESOLVED", ast.dump(fn)[:60])
                elif a0.value.rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
                    rec(node, "FORBIDDEN_IMPORT", a0.value)
    return out


def scan(root: Path = NS) -> dict:
    files = sorted(p for p in root.rglob("*.py") if p.name != "q309_guard.py")
    findings, controls = [], []
    sanctioned = []
    for p in files:
        fs = _scan_file(p)
        head = p.read_text()[:400]
        if CONTROL_MARK in head:
            controls.append({"file": str(p.relative_to(NS)), "fired": sorted({f["kind"] for f in fs})})
            continue
        if REFUSAL_TEST_MARK in head:
            sanctioned.extend(fs)
            continue
        findings.extend(f for f in fs if not f.get("suppressed"))
    suppressed = [f for p in files if CONTROL_MARK not in p.read_text()[:400]
                  for f in _scan_file(p) if f.get("suppressed")]
    need = {"CELL_LITERAL", "BAND_LITERAL", "FORBIDDEN_IMPORT", "TARGET_PATH"}
    control_ok = bool(controls) and all(need <= set(c["fired"]) for c in controls)
    return {"files_scanned": len(files), "findings": findings, "suppressed_listed": suppressed,
            "sanctioned_refusal_test_findings": sanctioned,
            "planted_controls": controls, "control_fires_all_kinds": control_ok,
            "verdict": "PASS" if (not findings and control_ok) else "FAIL"}


if __name__ == "__main__":
    if "--scan" in sys.argv:
        r = scan()
        print(json.dumps(r, indent=1))
        sys.exit(0 if r["verdict"] == "PASS" else 1)
    print(__doc__)
