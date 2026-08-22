from __future__ import annotations

import ast
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
PACKAGE = CAMPAIGN / "src/rebaseguard_sr_derivative"


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def test_route_sources_do_not_import_each_other_or_stage_d():
    raw = PACKAGE / "raw_sr.py"
    log = PACKAGE / "log_sr.py"
    raw_imports = imported_modules(raw)
    log_imports = imported_modules(log)
    assert not any("log_sr" in module or "stage_d" in module for module in raw_imports)
    assert not any("raw_sr" in module or "stage_d" in module for module in log_imports)


def test_routes_own_distinct_recursion_and_alarm_functions():
    raw_text = (PACKAGE / "raw_sr.py").read_text()
    log_text = (PACKAGE / "log_sr.py").read_text()
    assert "def raw_step" in raw_text
    assert "def classify_alarm" in raw_text
    assert "def log_step" in log_text
    assert "def classify_alarm_logs" in log_text
    assert "np.exp" in raw_text
    assert "np.logaddexp" in log_text
    assert "simulate_paired_log_batch" not in raw_text
    assert "simulate_raw_paths" not in log_text


def test_log_route_contains_no_score_or_gamma_computation():
    tree = ast.parse((PACKAGE / "log_sr.py").read_text())
    identifiers = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    assert "Gamma" not in identifiers
    assert "product" not in identifiers

