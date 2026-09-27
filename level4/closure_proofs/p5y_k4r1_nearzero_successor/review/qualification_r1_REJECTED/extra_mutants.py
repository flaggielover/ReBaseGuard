import os, subprocess, sys, json, tempfile
from pathlib import Path
NS = Path("/Users/suzhe/ReBaseGuard-k4r1/level4/closure_proofs/p5y_k4r1_nearzero_successor")
src = (NS/"code/k4r1_certificate.py").read_text()
TESTS = NS/"tests/test_k4r1.py"
M = [
 ("D0_lo_instead_of_hi", '"_D0_hi": D0[1]', '"_D0_hi": D0[0]'),
 ("M3_from_order2", 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["5"][m])', 'M3, M5 = fr(row["M"]["2"][m]), fr(row["M"]["5"][m])'),
 ("M5_from_order4", 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["5"][m])', 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["4"][m])'),
 ("M_wrong_m", 'M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["5"][m])', 'M3, M5 = fr(row["M"]["3"]["1"]), fr(row["M"]["5"]["1"])'),
 ("L1_U0_swapped", 'L1, U0 = fr(pm["L1"]), fr(pm["U0"])', 'U0, L1 = fr(pm["L1"]), fr(pm["U0"])'),
 ("D0_wrong_m", 'ent = k1["m"][m]', 'ent = k1["m"]["1"]'),
 ("exec_g_uses_x1", 'G = g_bound(v["_D0_hi"], v["_L1"], v["e0"])', 'G = g_bound(v["_D0_hi"], v["_L1"], v["x1"])'),
 ("exec_t_args_swapped", 'T = t_bound(v["_M3"], v["_U0"], v["_M5"], v["a"])', 'T = t_bound(v["_M3"], v["_U0"], v["_M5"], v["e0"])'),
 ("exec_science_or", 'science = all(c["PASS"] for c in certs.values()) and asm["complete"]', 'science = all(c["PASS"] for c in certs.values()) or asm["complete"]'),
 ("hull_row_wrong", 'hits = [r for r in rows if fr(r["x_hi"]) == a]', 'hits = [r for r in rows if fr(r["x_hi"]) == a] if False else [rows[0]]'),
 ("eta_upper_unbounded", 'if not (a <= eta <= a * (1 + F(1, 2 ** 200))):', 'if not (a <= eta):'),
 ("assembly_residual_how_unchecked", 'hist_ok = (all(c["how"] == "CERTIFICATE_TOO_LOOSE" for c in cells if c["index"] in rcells)', 'hist_ok = (True'),
]
rows=[]
with tempfile.TemporaryDirectory() as td:
    for name, old, new in M:
        n = src.count(old)
        if n != 1: rows.append((name, "NOT_APPLIED", n)); continue
        p = Path(td)/"k4r1_certificate.py"; p.write_text(src.replace(old, new))
        env = {**os.environ, "K4R1_CODE_PATH": str(p), "PYTHONDONTWRITEBYTECODE": "1"}
        r = subprocess.run(["/usr/bin/python3","-m","pytest","-q","-x","-p","no:cacheprovider",str(TESTS)], env=env, capture_output=True, text=True)
        rows.append((name, "KILLED" if r.returncode else "SURVIVED", r.returncode))
for r in rows: print(*r)
json.dump(rows, open("EXTRA_MUTANTS.json","w"), indent=1)
