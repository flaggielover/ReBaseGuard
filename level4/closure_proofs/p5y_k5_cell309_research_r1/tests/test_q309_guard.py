# q309: refusal-test
"""Guard behaviour tests: every refusal must fire; allowed inputs must pass."""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import q309_guard as g  # noqa: E402


def _refuses(fn, *a):
    try:
        fn(*a)
    except g.QuarantineRefusal:
        return True
    return False


def run():
    res = {}
    res["cells_refused"] = all(_refuses(g.guard_cell, "CUSUM", 5, c) for c in range(305, 310))  # q309: literal-ok
    res["noncell_allowed"] = not _refuses(g.guard_cell, "CUSUM", 5, 297) and not _refuses(g.guard_cell, "SR", 5, 309)  # q309: literal-ok
    res["band_refused"] = all(_refuses(g.guard_drift, x) for x in (Fraction(6, 5), Fraction(2), Fraction(13, 5), Fraction(-2)))  # q309: literal-ok
    res["band_interval_refused"] = _refuses(g.guard_drift, Fraction(1), Fraction(3)) and _refuses(g.guard_drift, -3, 0)
    res["outside_allowed"] = not any(_refuses(g.guard_drift, x) for x in (0, Fraction(1, 2), 1, 3, Fraction(-1)))
    res["path_refused"] = _refuses(g.guard_path, "x/TCT_INPUTS_309.json") and _refuses(g.guard_path, "refs/p5y-k5-cell308-x/target-consumed")  # q309: literal-ok
    g.install_import_guard()
    try:
        __import__("rlr307_driver")
        res["import_refused"] = False
    except g.QuarantineRefusal:
        res["import_refused"] = True
    except ImportError:
        res["import_refused"] = False
    ok = all(res.values())
    return ok, res


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
