"""Run the declared SRK decoy suite (config/SRK_DECOY_DECLARATION.json) with a process pool; one JSON per block
in evidence/srk_decoys/.  Every job is a declared decoy; nothing is added or dropped after results."""
import json
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
    h, k, elo, ehi, idx, ladder = spec
    g = KX.Geom(F(h), F(k))
    logs = []
    blk = S.run_block(g, F(elo), F(ehi), tuple(idx), tuple(ladder), log=logs.append)
    certs = {i: S.certificate_json(blk, i) for i in blk["Gamma"]}
    rec = {"geometry": blk["geometry"], "block": blk["block"],
           "Gamma": {i: (S.fstr(v) if v is not None else None) for i, v in blk["Gamma"].items()},
           "Abar_W": S.fstr(blk["Abar_W"]) if blk["Abar_W"] is not None else None,
           "rungs": [{"degree": r["degree"], "W_status": r["W"]["status"],
                      "W_at_atom_max": S.fstr(r["W"]["W_at_atom_max"]) if "W_at_atom_max" in r["W"] else None,
                      "eta": S.fstr(r["W"]["eta"]) if "eta" in r["W"] else None,
                      "V": {i: {"Gamma": S.fstr(v["Gamma"]), "lam": S.fstr(v["lam"]), "r_min": S.fstr(v["r_min"]),
                                "boxes": v["boxes"], "seconds": v["seconds"]} for i, v in r["V"].items()}}
                     for r in blk["rungs"]],
           "certificates": certs, "log": logs}
    name = f"h{h.replace('/', '_')}_k{k.replace('/', '_')}_E{elo.replace('/', '_')}_{ehi.replace('/', '_')}.json"
    out = NS / "evidence" / "srk_decoys" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    return name


def main():
    dec = json.loads((NS / "config" / "SRK_DECOY_DECLARATION.json").read_text())
    jobs = []
    rg = dec["real_geometry"]
    for elo, ehi in rg["blocks"]:
        jobs.append((rg["h"], rg["k"], elo, ehi, dec["indices"], dec["ladder"]))
    for sg in dec["synthetic_geometries"]:
        for elo, ehi in sg["blocks"]:
            jobs.append((sg["h"], sg["k"], elo, ehi, dec["indices"], dec["ladder"]))
    with ProcessPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv) > 1 else 4) as ex:
        for name in ex.map(job, jobs):
            print("done", name, flush=True)


if __name__ == "__main__":
    main()
