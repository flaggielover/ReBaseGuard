"""Determinism replay: re-execute selected committed patch records of one successor cell in a fresh process and
compare every scientific leaf (runtime-only fields cpu_seconds, peak_rss_kib, cache_hits, cache_misses excluded)."""
import glob
import gzip
import json
import sys
from pathlib import Path

import succ_t3 as S3


def strip(r):
    r = {k: v for k, v in r.items() if k not in ("cpu_seconds", "peak_rss_kib")}
    for m in r["modes"].values():
        m.pop("cache_hits", None), m.pop("cache_misses", None)
    return r


def main():
    parent, s, outdir = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
    patches = [tuple(map(int, p.split(","))) for p in sys.argv[4].split(";")]
    O = Path(__file__).resolve().parents[1] / f"evidence/certified/parent_{parent}/chunks"
    orig = {}
    for f in glob.glob(str(O / "rec_*.jsonl.gz")):
        for line in gzip.open(f, "rt"):
            r = json.loads(line)
            if r["successor_cell"] == s and tuple(r["patch"]) in patches:
                orig[tuple(r["patch"])] = strip(r)
    pf = outdir / "patches.txt"
    pf.write_text("".join(f"{i} {j}\n" for i, j in patches))
    out = outdir / "replay.jsonl"
    if out.exists():
        out.unlink()
    S3.run_chunk([s], patches, out)
    res = {}
    for line in out.read_text().splitlines():
        r = strip(json.loads(line))
        res[str(tuple(r["patch"]))] = r == orig[tuple(r["patch"])]
    rep = {"successor_cell": s, "patches": [list(p) for p in patches], "identical": res, "all_identical": all(res.values()) and len(res) == len(patches)}
    (outdir / "determinism.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
