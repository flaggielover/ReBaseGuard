"""Local unit tests (synthetic fixtures only; no K1 record is read). python3 -B tests/test_adapter.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import acceptance as A  # noqa: E402

A.SCRATCH = Path(tempfile.mkdtemp(prefix="e6test"))


def main() -> int:
    comps = A.AD.frozen_components(A.REPO)
    fixtures = A.synthetic_fixtures(comps["theorem"])
    results = {
        "fixtures_built": len(fixtures) == 6,
        "synthetic_differential": A.synthetic_differential(A.AD, fixtures, comps, comps["loader"])["ok"],
        "fail_closed": A.fail_closed(fixtures, comps)["ok"],
        "static_fences": A.static_fences((A.HERE / "consumption_adapter.py").read_text())["ok"],
        "anchors_unique": all((A.HERE / "consumption_adapter.py").read_text().count(old) == 1
                              for old, _ in A.SOURCE_MUTANTS.values()),
    }
    src = (A.HERE / "consumption_adapter.py").read_text()
    for mid, (old, new) in A.SOURCE_MUTANTS.items():      # every source mutant must break the synthetic path or a fence
        msrc = src.replace(old, new)
        mod = A.mutant_module(msrc)
        syn = A.synthetic_differential(mod, fixtures, mod.frozen_components(A.REPO), comps["loader"])
        fence = A.static_fences(msrc)["ok"]
        results[f"{mid}_synthetic_or_fence"] = (not syn["ok"]) or (not fence)
    import shutil
    shutil.rmtree(A.SCRATCH, ignore_errors=True)
    for k, v in results.items():
        print(("PASS " if v else "FAIL ") + k)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
