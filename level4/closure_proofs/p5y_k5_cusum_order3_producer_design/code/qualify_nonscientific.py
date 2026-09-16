"""Run the frozen NON-SCIENTIFIC qualification protocol (config/QUALIFICATION_PROTOCOL.json) and write the evidence.

    python3 code/qualify_nonscientific.py run --out evidence/qualification_r1/QUALIFICATION_RESULT.json
    python3 code/qualify_nonscientific.py check --evidence evidence/qualification_r1/QUALIFICATION_RESULT.json

Inputs are manufactured systems only, plus exactly one frozen config file (the assembly coefficient table),
pinned by sha256 in the protocol. No detector, cell table, K1 record, CUSUM kernel or host is touched.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
sys.path.insert(0, str(NS / "code"))
import manufactured as MF  # noqa: E402
import order3_algebra as A  # noqa: E402

PROTOCOL = NS / "config/QUALIFICATION_PROTOCOL.json"
GRID = 16


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _F(s: str) -> Fr:
    return Fr(s)


# ------------------------------------------------------------------ containment checks
def violations(sysm, inp, res, e0: Fr, rho: Fr, ms, *, objects: bool, cell: bool, mutation=None) -> list[str]:
    """Every place a certified bound fails to contain the exact truth. Empty list == sound on this trial."""
    out = []
    truth0 = sysm.true_objects(e0, 3)
    Fh, Wh = inp["Fhat"], inp["What"]

    def obj_err(key, truth, n):
        if key[0] == "F":
            return A.norm(A.sub(Fh[key[1]][n], truth[("F", key[1])][n]))
        return A.norm(A.sub(Wh[key[1]][n], truth[("W", key[1])][n]))

    keys = [("F", r) for r in range(5)] + [("W", rj) for rj in A.W_INDICES]
    if objects:
        for kk in keys:
            for n in range(4):
                key = ("F", kk[1], n) if kk[0] == "F" else ("W", kk[1], n)
                if obj_err(kk, truth0, n) > res["eps_mid"][key]:
                    out.append(f"mid {key}")
    for m in ms:
        for n in range(4):
            lo, hi = res["m"][m][n]["mid"]
            t = sysm.true_R(e0, m, n)
            if not lo <= t <= hi:
                out.append(f"assembly mid m={m} n={n}")
        L, U = res["m"][m]["export"]["L"], res["m"][m]["export"]["U"]
        if not L <= sysm.true_R(e0, m, 3) <= U:
            out.append(f"export at e0 m={m}")
    if cell:
        for g in range(GRID + 1):
            e = e0 - rho + 2 * rho * g / GRID
            tr = sysm.true_objects(e, 3)
            if objects:
                for kk in keys:
                    for n in range(4):
                        key = ("F", kk[1], n) if kk[0] == "F" else ("W", kk[1], n)
                        if obj_err(kk, tr, n) > res["eps_cell"][key]:
                            out.append(f"cell g={g} {key}")
            for m in ms:
                for n in range(4):
                    lo, hi = res["m"][m][n]["cell"]
                    val = sum((c * (tr[("F", r)] if kd == "F" else tr[("W", (r, j))])[n][A.ORIGIN]
                               for kd, r, j, c in A.coefficients(m)), Fr(0))
                    if not lo <= val <= hi:
                        out.append(f"assembly cell g={g} m={m} n={n}")
                    if n == 3 and not res["m"][m]["export"]["L"] <= val <= res["m"][m]["export"]["U"]:
                        out.append(f"export cell g={g} m={m}")
    return out


def build_trial(spec: dict):
    e0, rho = _F(spec["e0"]), _F(spec["rho"])
    if spec["system"] == "random":
        sysm = MF.random_system(spec["seed"], spec["n"])
    else:
        sysm = MF.scalar_controlled(spec["system"].split(":")[1], e0)
    perturb = None
    if "perturb_F" in spec:
        perturb = {"F": (spec["perturb_F"][0], _F(spec["perturb_F"][1]))}
    inp, _ = MF.cell_inputs(sysm, e0, rho, perturb=perturb, seed=spec.get("seed", 0),
                            noise=_F(spec.get("noise", "0")))
    return sysm, inp, e0, rho


# ------------------------------------------------------------------ static checks
STDLIB_ALLOWED = {"__future__", "fractions", "math", "json", "hashlib", "sys", "pathlib", "ast"}
LOCAL_MODULES = {"order3_algebra", "manufactured", "qualify_nonscientific"}
FORBIDDEN_SUBSTRINGS = ("cells.json", "successor_cells", "k4_records", "COMPOSITE_EXPORT", "postk1-runs",
                        "cusum_layer", "aux_certifier", "flint", "numpy", "rebaseguard_certify", "socket", "urllib",
                        "subprocess")


def static_checks() -> dict:
    res = {}
    for name in ("order3_algebra.py", "manufactured.py"):
        tree = ast.parse((NS / "code" / name).read_text())
        floats = [n.lineno for n in ast.walk(tree)
                  if (isinstance(n, ast.Constant) and isinstance(n.value, float))
                  or (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "float")]
        res[f"{name}:no_float"] = floats == []
    for name in ("order3_algebra.py", "manufactured.py", "qualify_nonscientific.py"):
        src = (NS / "code" / name).read_text()
        tree = ast.parse(src)
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add((n.module or "").split(".")[0])
        res[f"{name}:imports_whitelisted"] = mods <= (STDLIB_ALLOWED | LOCAL_MODULES)
        body = src if name != "qualify_nonscientific.py" else src.split("FORBIDDEN_SUBSTRINGS = (")[0] + \
            src.split("def static_checks")[1]
        res[f"{name}:no_forbidden_reference"] = not any(s in body for s in FORBIDDEN_SUBSTRINGS)
    return res


def assembly_table_check(proto: dict) -> dict:
    path = REPO / proto["frozen_inputs"]["assembly_table"]["path"]
    raw = path.read_bytes()
    ok_hash = _sha(raw) == proto["frozen_inputs"]["assembly_table"]["sha256"]
    table = json.loads(raw)["assembly"]
    same = all(sorted((k, int(r), int(j), Fr(c)) for k, r, j, c in table[str(m)]) == sorted(A.coefficients(m))
               for m in A.M_VALUES)
    return {"hash_matches_protocol": ok_hash, "reference_equals_frozen_table": same}


# ------------------------------------------------------------------ run
def run() -> dict:
    proto_bytes = PROTOCOL.read_bytes()
    proto = json.loads(proto_bytes)
    code_hashes = {p: _sha((NS / p).read_bytes()) for p in proto["bound_code"]}

    soundness = []
    for spec in proto["QN1_SOUNDNESS"]["trials"]:
        sysm, inp, e0, rho = build_trial(spec)
        res = A.cell_order3(inp)
        v = violations(sysm, inp, res, e0, rho, A.M_VALUES, objects=True, cell=True)
        rec = {"id": spec["id"], "violations": v[:20], "violation_count": len(v),
               "export": A.export_record(spec["id"], e0, rho, res)["m"]}
        soundness.append(rec)

    mutation = []
    for spec in proto["QN2_MUTATION_SENSITIVITY"]["trials"]:
        sysm, inp, e0, rho = build_trial(spec)
        ms = tuple(spec["m"])
        base = violations(sysm, inp, A.cell_order3(inp), e0, rho, ms, objects=True, cell=spec["cell"])
        for mut in spec["mutations"]:
            v = violations(sysm, inp, A.cell_order3(inp, mutation=mut), e0, rho, ms,
                           objects=True, cell=spec["cell"])
            mutation.append({"trial": spec["id"], "mutation": mut, "unmutated_violations": len(base),
                             "detected": len(v) > 0, "first_violations": v[:5]})

    static = static_checks()
    table = assembly_table_check(proto)
    detected = {m["mutation"]: m["detected"] for m in mutation}
    required = proto["QN2_MUTATION_SENSITIVITY"]["required_detected"]
    verdicts = {
        "QN1_SOUNDNESS": "PASS" if soundness and all(t["violation_count"] == 0 for t in soundness) else "FAIL",
        "QN2_MUTATION_SENSITIVITY": ("PASS" if all(detected.get(m) is True for m in required)
                                     and all(x["unmutated_violations"] == 0 for x in mutation) else "FAIL"),
        "QN3_EXACT_ARITHMETIC": "PASS" if all(v for k, v in static.items() if k.endswith(":no_float")) else "FAIL",
        "QN4_SCIENTIFIC_FENCE": ("PASS" if all(v for k, v in static.items()
                                               if k.endswith((":imports_whitelisted", ":no_forbidden_reference")))
                                 else "FAIL"),
        "QN5_FROZEN_ASSEMBLY_TABLE": "PASS" if all(table.values()) else "FAIL",
    }
    return {
        "schema": "rebaseguard.p5y.k5.order3-nonscientific-qualification.result.v1",
        "protocol_sha256": _sha(proto_bytes),
        "bound_code_sha256": code_hashes,
        "scope": proto["scope"],
        "soundness_trials": soundness,
        "mutation_trials": mutation,
        "static_checks": static,
        "assembly_table": table,
        "verdicts": verdicts,
        "overall_nonscientific_qualification": "PASS" if all(v == "PASS" for v in verdicts.values()) else "FAIL",
        "producer_scientifically_qualified": False,
        "k5_probe_authorized": False,
    }


def canonical(obj) -> bytes:
    return (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode()


def main(argv) -> int:
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "run":
        out = Path(argv[argv.index("--out") + 1])
        result = run()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(canonical(result))
        print(result["overall_nonscientific_qualification"], _sha(canonical(result)))
        for k, v in result["verdicts"].items():
            print(f"  {k} = {v}")
        return 0 if result["overall_nonscientific_qualification"] == "PASS" else 1
    if cmd == "check":
        ev = Path(argv[argv.index("--evidence") + 1])
        replay = canonical(run())
        same = replay == ev.read_bytes()
        print("REPLAY_BYTE_IDENTICAL" if same else "REPLAY_DIFFERS", _sha(replay))
        return 0 if same else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
