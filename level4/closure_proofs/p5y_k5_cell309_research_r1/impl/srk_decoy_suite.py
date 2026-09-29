"""Run the declared SRK decoy suite with a process pool; one JSON per block.

  python3 impl/srk_decoy_suite.py N [whole|taboo|cell]

  whole  config/SRK_DECOY_DECLARATION.json blocks, whole kernel          -> evidence/srk_decoys/
  taboo  the same blocks, taboo kernel (amendment A1/A2)                 -> evidence/srk_decoys_taboo/
  cell   config/SRK_DECOY_DECLARATION_A2.json cell family: one job per check sub-block of each cell
         (srk_certify.cell_blocks, weight block = the cell's outward dyadic hull; amendment A3) -> evidence/srk_decoys_cell/

Every job is a declared decoy; nothing is added or dropped after results.

Single-code-state lock (amendment A2 rerun rule, review R1 B3): at start the runner requires the producer files to be
committed and unmodified (git status clean for them), records git HEAD and the producer fingerprint, and every job
refuses unless its own fingerprint equals the start fingerprint.  Outputs record both ("git_head_at_start").
"""
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))


def job(spec):
    import srk_certify as S
    import srk_kernel as KX
    h, k, elo, ehi, idx, ladder, whole, wb, sub, name, fp0, head0 = spec
    if S.producer_fingerprint()["combined"] != fp0:
        raise RuntimeError("single-code-state lock: producer files changed since the suite started")
    g = KX.Geom(F(h), F(k))
    logs = []
    blk = S.run_block(g, F(elo), F(ehi), tuple(idx), tuple(ladder), log=logs.append, whole=whole,
                      weight_block=None if wb is None else (F(wb[0]), F(wb[1])))
    if blk["producer"]["combined"] != fp0:
        raise RuntimeError("single-code-state lock: producer files changed during the job")
    certs = {i: S.certificate_json(blk, i) for i in blk["Gamma"]}
    rec = {"geometry": blk["geometry"], "block": blk["block"], "kernel": "whole" if whole else "taboo",
           "weight_block": None if wb is None else list(wb),
           "producer": blk["producer"], "git_head_at_start": head0,
           "Gamma": {i: (S.fstr(v) if v is not None else None) for i, v in blk["Gamma"].items()},
           "Abar_W": S.fstr(blk["Abar_W"]) if blk["Abar_W"] is not None else None,
           "rungs": [{"degree": r["degree"], "W_status": r["W"]["status"],
                      "W_at_atom_max": S.fstr(r["W"]["W_at_atom_max"]) if "W_at_atom_max" in r["W"] else None,
                      "eta": S.fstr(r["W"]["eta"]) if "eta" in r["W"] else None,
                      "V": {i: {"Gamma": S.fstr(v["Gamma"]), "lam": S.fstr(v["lam"]), "r_min": S.fstr(v["r_min"]),
                                "boxes": v["boxes"], "seconds": v["seconds"]} for i, v in r["V"].items()}}
                     for r in blk["rungs"]],
           "certificates": certs, "log": logs}
    out = NS / "evidence" / sub / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    return name


def _u(x: str) -> str:
    return x.replace("/", "_")


def jobs_for(mode: str) -> list:
    import srk_certify as S
    if mode in ("whole", "taboo"):
        dec = json.loads((NS / "config" / "SRK_DECOY_DECLARATION.json").read_text())
        whole = mode == "whole"
        sub = "srk_decoys" if whole else "srk_decoys_taboo"
        out = []
        geoms = [dec["real_geometry"]] + list(dec["synthetic_geometries"])
        for gd in geoms:
            for elo, ehi in gd["blocks"]:
                name = f"h{_u(gd['h'])}_k{_u(gd['k'])}_E{_u(elo)}_{_u(ehi)}.json"
                out.append((gd["h"], gd["k"], elo, ehi, dec["indices"], dec["ladder"], whole, None, sub, name))
        return out
    if mode == "cell":
        fam = json.loads((NS / "config" / "SRK_DECOY_DECLARATION_A2.json").read_text())["cell_family"]
        out = []
        for c in fam["cells"]:
            if c["kernel"] != "whole":
                raise ValueError("A2 cell family declares whole-kernel cells only")
            wb, subs = S.cell_blocks(F(c["cell"][0]), F(c["cell"][1]))
            for j, (a, b) in enumerate(subs):
                name = f"cell_h{_u(c['h'])}_k{_u(c['k'])}_C{_u(c['cell'][0])}_{_u(c['cell'][1])}_S{j}.json"
                out.append((c["h"], c["k"], S.fstr(a), S.fstr(b), fam["indices"], fam["ladder"], True,
                            [S.fstr(wb[0]), S.fstr(wb[1])], "srk_decoys_cell", name))
        return out
    raise ValueError(f"unknown mode {mode!r}")


def code_state() -> tuple:
    import srk_certify as S
    import srk_kernel as KX
    files = [str(HERE / f) for f in S.PRODUCER_FILES] + [str(Path(KX.G.__file__).resolve())]
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + files, cwd=NS, capture_output=True,
                           text=True).stdout.strip()
    if dirty:
        raise SystemExit(f"single-code-state lock: producer files not committed:\n{dirty}")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=NS, capture_output=True, text=True).stdout.strip()
    return S.producer_fingerprint()["combined"], head


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    mode = sys.argv[2] if len(sys.argv) > 2 else "whole"
    fp0, head0 = code_state()
    jobs = [j + (fp0, head0) for j in jobs_for(mode)
            # resume after an interruption: skip blocks whose output already exists AND carries the same code state
            if not ((NS / "evidence" / j[8] / j[9]).exists() and
                    json.loads((NS / "evidence" / j[8] / j[9]).read_text())["producer"]["combined"] == fp0)]
    print(f"mode={mode} head={head0} producer={fp0[:16]} pending jobs:", [j[9] for j in jobs], flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for name in ex.map(job, jobs):
            print("done", name, flush=True)


if __name__ == "__main__":
    main()
