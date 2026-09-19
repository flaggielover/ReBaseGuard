import json, sys, math
Q = "/root/work/k5p-adjudication/level4/closure_proofs/p5y_k5_perron_deflated_resolvent/evidence/successor_r1/qualification_r1/FALSIFY.json"
q = json.load(open(Q)); a = json.load(open(sys.argv[1])); tol = float(sys.argv[2])
def walk(x, y, path, out):
    if isinstance(x, dict):
        for k in x:
            if k in y: walk(x[k], y[k], path + [k], out)
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for i, (u, v) in enumerate(zip(x, y)): walk(u, v, path + [i], out)
    elif isinstance(x, bool) or isinstance(y, bool) or isinstance(x, str):
        if x != y: out["verdict_or_str_diff"].append((path, x, y))
    elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
        d = abs(x - y) / max(abs(x), abs(y), 1e-300)
        out["n"] += 1
        if d > out["max"][0]: out["max"] = (d, path, x, y)
        if d > tol: out["over"].append((path, x, y, d))
out = {"n": 0, "max": (0.0, None, None, None), "over": [], "verdict_or_str_diff": []}
ga, gq = a["gate"], q["gate"]
for sec in ("blocks", "arl_cells", "taboo_cells"):
    for k in ga[sec]:
        walk(ga[sec][k], gq[sec][k], [sec, k], out)
walk(a["planted"], q["planted"], ["planted"], out)
print("quadrature", a["quadrature"], "| qual", q["quadrature"])
print("pass", a["pass"], "qual pass", q["pass"], "flags", ga["flags"])
print("compared numbers", out["n"], "max rel diff", out["max"])
print("over tol", len(out["over"]), out["over"][:8])
print("verdict/str diffs", out["verdict_or_str_diff"][:8])
print("worst (this run)", ga["worst"])
print("worst (qual, all cells)", gq["worst"])
