"""Generate ops/produce_entry.py for the recovery successor.

DEFECT: the genuine child bound the WRONG launcher. produce_entry.run() imports the
launcher BY MODULE NAME:

    import production_launcher as PL
    ...
    pf["budget"] = LO.make_ops_budget(GB, pf["budget"], run_id, PL.__file__)

Under the recovery generation that resolves to the FROZEN production_launcher.py, which
carries 3 release sites and no budget.release(dkey). The recovery RELEASE_SITES contract
requires 4, so make_ops_budget refused: "frozen release call site 'budget.release(dkey)'
not found exactly once".

The assertion was RIGHT and caught something worse than itself: the genuine run was about
to execute the frozen group-level launcher instead of the cells-outer, per-cell-durable
one. The synthetic harness had masked this by pre-seeding sys.modules.

REPAIR: bind the recovery launcher by its real name. The assertion is untouched -- still
exactly-once over all four sites -- and now scans the file that actually runs. No literal
is fabricated, no count relaxed, no generation special-cased. The frozen
production_launcher.py stays byte-identical and remains pinned in the 39-file
executor_source_manifest.
"""
import hashlib
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
           "p5y_k1_ps1_lifecycle_adapter/ops/produce_entry.py")
OUT = NS / "ops" / "produce_entry.py"

OLD = "    import production_launcher as PL                               # noqa: E402\n"
NEW = ("    # recovery generation: the bound executor is the cells-outer, per-cell-durable\n"
       "    # launcher. make_ops_budget therefore scans ITS release sites (4, each exactly\n"
       "    # once) rather than the frozen group-level launcher's 3.\n"
       "    import ps1_cellseq_launcher as PL                              # noqa: E402\n")


def main() -> int:
    src = SRC.read_text()
    if src.count(OLD) != 1:
        raise SystemExit(f"launcher import anchor not found exactly once ({src.count(OLD)})")
    out = src.replace(OLD, NEW, 1)
    # the bind check must survive verbatim: the launcher must still live under driver/
    if 'is not the bound one under' not in out:
        raise SystemExit("the launcher bind check disappeared")
    # generation-2 runtime isolation: give the launcher the CONTRACT's runtime namespace so
    # work/evidence/drain/markers resolve the same tree as drain/reconcile/checkpoint/export.
    RT_OLD = '    pf["budget"] = LO.make_ops_budget(GB, pf["budget"], run_id, PL.__file__)\n'
    RT_NEW = ('    pf["runtime_dir"] = spec["runtime_dir"]      # gen-2 runtime isolation\n'
              + RT_OLD)
    if out.count(RT_OLD) != 1:
        raise SystemExit(f"budget anchor not found exactly once ({out.count(RT_OLD)})")
    out = out.replace(RT_OLD, RT_NEW, 1)
    OUT.write_text(out)
    print(f"wrote {OUT}")
    print(f"  frozen produce_entry sha256 : {hashlib.sha256(SRC.read_bytes()).hexdigest()}")
    print(f"  generated sha256            : {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
