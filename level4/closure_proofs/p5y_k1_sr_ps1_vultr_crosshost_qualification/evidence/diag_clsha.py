"""POST-HOC DIAGNOSTIC (not predeclared; cannot alter the predeclared verdict): T1 candidate-list identity per cell."""
import json, glob, os, sys, time
import sr_o9_candidates as T, succ_t3 as S3
Q = sys.argv[1]
want = {}
for f in sorted(glob.glob(Q + "/rec_s*_p_00.jsonl")):
    r = json.loads(open(f).readline())
    want[r["successor_cell"]] = r["candidate_identity_list_sha256"]
out = {"OPENBLAS_CORETYPE": os.environ.get("OPENBLAS_CORETYPE"), "cells": {}}
with T.scientific_precision():
    for s in (0, 148, 360, 368):
        t = time.process_time()
        _c, _h, _C, _e0, clsha = S3.cell_inputs(s)
        out["cells"][s] = {"vultr": clsha, "aws": want.get(s), "equal": clsha == want.get(s), "cpu_s": round(time.process_time() - t, 2)}
print(json.dumps(out))
