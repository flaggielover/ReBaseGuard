"""Target quarantine for the cell-308 research campaign (stdlib only).

Implements config/TARGET_QUARANTINE_308.json:

* ``guard_cell``   refuses the quarantined cells (CUSUM m=5, 306-309) and the tail-adjacent cell 305 at every
                   new-route entry point;
* ``guard_drift``  refuses any drift point or block meeting [6/5, 13/5] or its mirror;
* ``guard_path``   refuses target-cell input files and sealed target results;
* ``install_import_guard``  refuses importing historical consumer / driver / exactly-once modules;
* ``scan``         static scan: an AST scan of every .py file plus a text co-location scan of every .md/.json/.txt
                   file in the namespace. Each part has a planted multi-shape negative control that must fire.
                   Coverage (files scanned) is always reported; sanctioned items are listed, never dropped.

``log_event`` appends one line to ledger/TARGET_INTEGRITY_LEDGER.jsonl.

Revision r2 (incident review C8): tail patterns loaded from ledger/TAIL_FIGURE_PATTERNS.json; neutral planted controls.
Adapted from the overnight tool p5y_k5_tail_overnight_research/code/ov_quarantine.py (after its review F3/F15
repairs); the text co-location scan is new here (incident-01 class: committed tail figures outside history/).
"""
from __future__ import annotations

import ast
import datetime
import importlib.abc
import json
import re
import sys
import tempfile
from fractions import Fraction as _Fr
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
LEDGER = NS / "ledger" / "TARGET_INTEGRITY_LEDGER.jsonl"

TARGET_CELLS = frozenset({306, 307, 308, 309})
ADJACENT_CELLS = frozenset({305})
DRIFT_BAND = (_Fr(6, 5), _Fr(13, 5))

FORBIDDEN_MODULES = frozenset({
    "c2_d5_forecast", "c2_execute", "c2_consume", "c2_refined_registry", "c2_recertify_306",
    "c2_critical_ratio", "tail_forecast_r2", "tct_inputs", "tct_rule", "tc_rule", "tc_producer",
    "k5b_literal", "taboo_certify", "c12_cell306", "c12_verify", "c12r1_cell306", "c12r1_verify",
    "c12r2_cell306", "c12r2_verify", "c11r_runs", "c11r_launch", "c11r_compare", "c11r_qualify",
    "c11rd_runs", "c11rd_launch", "c11rd_compare", "closeout_checks", "closeout_checks_r1",
    "closeout_checks_r2", "rlr307_driver", "rlr307_qualify", "deflated_consume",
})

FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"TCT_INPUTS_30[5-9]"),
    re.compile(r"C2_D5_FORECAST"),
    re.compile(r"C12R2_CELL306_RESULT"),
    re.compile(r"C12R1_CELL306_RESULT"),
    re.compile(r"REGISTRY_C[12]\b|REGISTRY_C[12][._]"),
    re.compile(r"ADOPTED_TAIL_INPUTS"),
    re.compile(r"C11R_RUNS"),
    re.compile(r"C11RD_.*RUNS"),
    re.compile(r"RLR307_RESULT|RLR307_CELL307|evidence/execution/"),
    re.compile(r"TAIL_FORECAST_R2"),
)

# Committed CUSUM m=5 tail-cell figures (305-309) that may appear ONLY in history/ and ledger/ files. Since scanner r2
# (incident review C8) the pattern table lives in the sanctioned file ledger/TAIL_FIGURE_PATTERNS.json, not in this
# source; the planted controls below are built from it at run time, with neutral wording.
_PATTERN_FILE = NS / "ledger" / "TAIL_FIGURE_PATTERNS.json"
TAIL_FIGURES = tuple(json.loads(_PATTERN_FILE.read_text())["patterns"])
if len(TAIL_FIGURES) < 50:
    raise RuntimeError("tail-figure pattern table missing or truncated")
_TAIL_RE = re.compile("|".join("(?<![0-9])" + p for p in TAIL_FIGURES))


def _literal(pattern: str) -> str:
    """A concrete string matched by one pattern of the table (backslash escapes and \\b removed)."""
    return pattern.replace("\\b", "").replace("\\", "")

TEXT_SUFFIXES = (".md", ".json", ".txt", ".jsonl")
SANCTIONED_TEXT_DIRS = ("history", "ledger")

LITERAL_OK = "c308-quarantine: literal-ok"
HISTORICAL_READ_MARK = "c308-quarantine: historical-read"


class QuarantineRefusal(RuntimeError):
    """Raised whenever new-route code would touch a quarantined cell, drift, path or module."""


def guard_cell(detector: str, m: int, cell: int) -> None:
    if str(detector).upper() == "CUSUM" and int(m) == 5:
        if int(cell) in TARGET_CELLS:
            raise QuarantineRefusal(f"TARGET_CELL_REFUSED CUSUM m=5 cell {cell}")
        if int(cell) in ADJACENT_CELLS:
            raise QuarantineRefusal(f"ADJACENT_CELL_REFUSED CUSUM m=5 cell {cell}")


def guard_drift(e_lo, e_hi=None) -> None:
    lo = _Fr(e_lo)
    hi = lo if e_hi is None else _Fr(e_hi)
    if hi < lo:
        lo, hi = hi, lo
    for a, b in (DRIFT_BAND, (-DRIFT_BAND[1], -DRIFT_BAND[0])):
        if not (hi < a or lo > b):
            raise QuarantineRefusal(f"DRIFT_BAND_REFUSED [{float(lo)}, {float(hi)}] meets [{float(a)}, {float(b)}]")


def guard_path(path) -> None:
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


HISTORICAL_CLASSES = frozenset({"HISTORICAL_READ", "HISTORICAL_RECONSTRUCTION", "PRUNING_FROM_COMMITTED"})
KNOWN_CLASSES = HISTORICAL_CLASSES | frozenset({
    "INFRASTRUCTURE", "SYNTHETIC_VALIDATION", "NONTARGET_DRIFT_VALIDATION", "NONTARGET_REAL_VALIDATION",
    "THEORY", "REVIEW", "PROXY_EXPOSURE", "QUARANTINE_RULE_BREACH", "INCIDENT",
})


def log_event(script: str, purpose: str, *, klass: str, cells_touched=(), target_evaluations: int = 0,
              proxies: int = 0, target_informed_opt: int = 0, notes: str = "", agent: str = "coordinator") -> dict:
    if klass not in KNOWN_CLASSES:
        raise ValueError(f"unknown ledger class {klass!r}")
    rec = {
        "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agent": agent, "script": script, "purpose": purpose, "class": klass,
        "cells_touched": list(cells_touched),
        "new_target_evaluations": target_evaluations,
        "target_equivalent_proxies": proxies,
        "target_informed_optimisation": target_informed_opt,
        "notes": notes,
    }
    for c in cells_touched:
        if isinstance(c, dict) and str(c.get("detector", "")).upper() == "CUSUM" and c.get("m") == 5 \
                and c.get("cell") in (TARGET_CELLS | ADJACENT_CELLS) and klass not in HISTORICAL_CLASSES:
            rec["LEAK_FLAG"] = True
    if target_evaluations or proxies or target_informed_opt:
        rec["LEAK_FLAG"] = True
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


# ---------------------------------------------------------------- static scan (python)

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


def _scan_py(p: Path) -> list[dict]:
    src = p.read_text()
    lines = src.splitlines()
    out: list[dict] = []
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [{"file": str(p), "line": exc.lineno, "kind": "UNPARSEABLE", "what": str(exc)[:60]}]

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
                    cands = [arg.body.value, arg.orelse.value]
                if cands is None:
                    rec(node, "DYNAMIC_IMPORT_UNRESOLVED", ast.dump(fn)[:60])
                else:
                    for c in cands:
                        if c.rsplit(".", 1)[-1] in FORBIDDEN_MODULES:
                            rec(node, "DYNAMIC_FORBIDDEN_IMPORT", c)
            if name in ("run", "Popen", "call", "check_call", "check_output", "system", "execv", "execvp",
                        "spawnv", "run_path"):
                for sv in _strings_in(node):
                    if _mentions_forbidden(sv):
                        rec(node, "SUBPROCESS_FORBIDDEN", sv[:80])
            if name in ("F", "Fraction", "_Fr", "Q", "q") and len(node.args) == 2 and all(
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
                if _TAIL_RE.search(v):
                    rec(node, "TAIL_FIGURE_IN_CODE", v[:60])          # never suppressed
            elif isinstance(v, int) and not isinstance(v, bool) and v in (TARGET_CELLS | ADJACENT_CELLS):
                rec(node, "SUPPRESSED_LITERAL" if ok else "TARGET_CELL_LITERAL", v)
            elif isinstance(v, float):
                if _in_band(v) and not ok:
                    rec(node, "ATTENTION_DRIFT_LITERAL", v)
                if _TAIL_RE.search(repr(v)):
                    rec(node, "TAIL_FIGURE_IN_CODE", repr(v))
    return out


def _scan_text(p: Path, root: Path) -> list[dict]:
    try:
        txt = p.read_text(errors="replace")
    except OSError as exc:
        return [{"file": str(p), "line": 0, "kind": "UNREADABLE", "what": str(exc)[:60]}]
    out = []
    for i, line in enumerate(txt.splitlines(), 1):
        for m in _TAIL_RE.finditer(line):
            out.append({"file": str(p), "line": i, "kind": "TAIL_FIGURE_IN_TEXT", "what": m.group(0)})
    return out


def _is_sanctioned_text(p: Path, root: Path) -> bool:
    rel = p.relative_to(root).parts
    return bool(rel) and rel[0] in SANCTIONED_TEXT_DIRS


REPORT_ONLY = ("SUPPRESSED_LITERAL", "ATTENTION_DRIFT_LITERAL")
_SELF = Path(__file__).resolve()


def _py_control(tmpdir: Path) -> tuple[bool, list]:
    planted = "\n".join([
        "import tail_forecast_r2",
        "import importlib, subprocess",
        "importlib.import_module('tct_rule')",
        "__import__('c2_d5_forecast')",
        "subprocess.run(['python3', 'x/k5b_literal.py'])",
        "x = 308",
        "y = 'cell 309'",
        "p = 'evidence/TCT_INPUTS_308.json'",
        "q = 'evidence/C2_D5_FORECAST.json'  # " + LITERAL_OK + " (a path must never be suppressed)",
        "z = 1.9",
        "w = F(47, 25)",
        "u = 306  # " + LITERAL_OK + " (reported as suppressed, not silent)",
        "t = 'value " + _literal(TAIL_FIGURES[9]) + "'",
    ]) + "\n"
    f = tmpdir / "planted_control.py"
    f.write_text(planted)
    ctrl = _scan_py(f)
    kinds = sorted({c["kind"] for c in ctrl})
    expected = sorted({"FORBIDDEN_IMPORT", "DYNAMIC_FORBIDDEN_IMPORT", "SUBPROCESS_FORBIDDEN", "TARGET_CELL_LITERAL",
                       "TARGET_CELL_STRING", "TARGET_INPUT_PATH", "ATTENTION_DRIFT_LITERAL", "SUPPRESSED_LITERAL",
                       "TAIL_FIGURE_IN_CODE"})
    ok = (kinds == expected
          and sum(1 for c in ctrl if c["kind"] == "TARGET_INPUT_PATH") == 2
          and sum(1 for c in ctrl if c["kind"] == "ATTENTION_DRIFT_LITERAL") == 2)
    return ok, kinds


def _text_control(tmpdir: Path) -> tuple[bool, dict]:
    root = tmpdir / "ns"
    (root / "streams").mkdir(parents=True)
    (root / "history").mkdir(parents=True)
    bad = root / "streams" / "planted.md"
    f = [_literal(TAIL_FIGURES[i]) for i in (9, 15, 19, 26)]
    bad.write_text(f"planted value {f[0]}\nplain line\nplanted values {f[1]} and {f[2]}\n")
    bad_json = root / "streams" / "planted.json"
    bad_json.write_text('{"note": "planted ' + f[3] + '"}\n')
    good = root / "history" / "planted_history.md"
    good.write_text(f"committed: {f[0]}\n")
    clean = root / "streams" / "clean.md"
    clean.write_text("a derivation with 1/2 and 3/4 and 1.25 and 0.431\n")
    r = _scan_tree(root, run_controls=False)
    hits = [f for f in r["findings"] if f["kind"] == "TAIL_FIGURE_IN_TEXT"]
    files_hit = sorted({Path(f["file"]).name for f in hits})
    sanctioned_files = sorted({Path(f["file"]).name for f in r["sanctioned_text"]})
    ok = (files_hit == ["planted.json", "planted.md"] and len(hits) == 4
          and sanctioned_files == ["planted_history.md"])
    return ok, {"files_hit": files_hit, "n_hits": len(hits), "sanctioned": sanctioned_files}


def _scan_tree(root: Path, run_controls: bool = True) -> dict:
    py_files = sorted(q for q in root.rglob("*.py") if "__pycache__" not in q.parts and q.resolve() != _SELF)
    txt_files = sorted(q for q in root.rglob("*") if q.is_file() and q.suffix in TEXT_SUFFIXES
                       and "__pycache__" not in q.parts)
    findings, sanctioned, report_only, sanctioned_text = [], [], [], []
    for q in py_files:
        head = "\n".join(q.read_text().splitlines()[:40])
        fs = _scan_py(q)
        report_only.extend(f for f in fs if f["kind"] in REPORT_ONLY)
        fs = [f for f in fs if f["kind"] not in REPORT_ONLY]
        if HISTORICAL_READ_MARK in head:
            sk = ("TARGET_INPUT_PATH", "TARGET_CELL_LITERAL", "TARGET_CELL_STRING", "TAIL_FIGURE_IN_CODE")
            sanctioned.extend(f for f in fs if f["kind"] in sk)
            findings.extend(f for f in fs if f["kind"] not in sk)
        else:
            findings.extend(fs)
    for q in txt_files:
        fs = _scan_text(q, root)
        if _is_sanctioned_text(q, root):
            sanctioned_text.extend(fs)
        else:
            findings.extend(fs)
    out = {
        "py_files_scanned": len(py_files),
        "text_files_scanned": len(txt_files),
        "py_file_list": [str(q.relative_to(root)) for q in py_files],
        "findings": findings,
        "sanctioned_historical_read_py": [{"file": f["file"], "line": f["line"], "kind": f["kind"]} for f in sanctioned],
        "sanctioned_text": sanctioned_text,
        "sanctioned_text_files": sorted({f["file"] for f in sanctioned_text}),
        "report_only": report_only,
        "report_only_counts": {k: sum(1 for f in report_only if f["kind"] == k) for k in REPORT_ONLY},
    }
    if run_controls:
        with tempfile.TemporaryDirectory() as td:
            py_ok, py_kinds = _py_control(Path(td))
        with tempfile.TemporaryDirectory() as td:
            tx_ok, tx_detail = _text_control(Path(td))
        out.update({
            "py_negative_control_detected": py_ok, "py_negative_control_kinds": py_kinds,
            "text_negative_control_detected": tx_ok, "text_negative_control_detail": tx_detail,
            "limits": ("static scans cannot see values computed at run time, paths built by string operations, drifts "
                       "passed as variables, or a tail figure written with different rounding; the runtime guards and "
                       "independent review are the primary barriers"),
        })
        ctrl = py_ok and tx_ok
        out["verdict"] = "PASS" if (ctrl and not findings) else ("CONTROL_FAILED" if not ctrl else "FINDINGS")
    return out


def scan(root: Path = NS) -> dict:
    return _scan_tree(root, run_controls=True)


def _selftest() -> None:
    for c in (305, 306, 307, 308, 309):
        try:
            guard_cell("CUSUM", 5, c)  # c308-quarantine: literal-ok self-test of the refusal
        except QuarantineRefusal:
            continue
        raise AssertionError(f"guard_cell failed to refuse {c}")
    guard_cell("SR", 5, 308)  # c308-quarantine: literal-ok SR cells are not targets
    guard_cell("CUSUM", 3, 308)  # c308-quarantine: literal-ok other m are not targets
    guard_cell("CUSUM", 5, 297)
    for e in ("6/5", "19/10", "13/5", "-2", "-6/5"):
        try:
            guard_drift(_Fr(e))
        except QuarantineRefusal:
            continue
        raise AssertionError(f"guard_drift failed to refuse {e}")
    guard_drift(_Fr(1, 2), 1)
    guard_drift(3)
    guard_drift(_Fr(11, 10))
    for lo, hi in ((1, 3), (_Fr(-3), _Fr(-1)), (_Fr(5, 2), _Fr(27, 10))):
        try:
            guard_drift(lo, hi)
        except QuarantineRefusal:
            continue
        raise AssertionError(f"guard_drift failed to refuse the straddling interval [{lo}, {hi}]")
    for pth in ("x/TCT_INPUTS_308.json", "y/C2_D5_FORECAST.json", "z/REGISTRY_C2.json", "w/RLR307_RESULT.json"):
        try:
            guard_path(pth)
        except QuarantineRefusal:
            continue
        raise AssertionError(f"guard_path failed to refuse {pth}")
    guard_path("level4/closure_proofs/cells.json")
    install_import_guard()
    for mod in ("tail_forecast_r2", "rlr307_driver", "deflated_consume"):
        try:
            __import__(mod)
        except QuarantineRefusal:
            continue
        raise AssertionError(f"import guard failed on {mod}")
    print("c308_quarantine selftest PASS")


if __name__ == "__main__":
    if "--scan" in sys.argv:
        r = scan()
        print(json.dumps(r, indent=1))
        sys.exit(0 if r["verdict"] == "PASS" else 1)
    else:
        _selftest()
