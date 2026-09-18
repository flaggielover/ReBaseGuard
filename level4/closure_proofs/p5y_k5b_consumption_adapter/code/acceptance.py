"""E6 frozen acceptance run (E6_SPEC.md S6-S11, config/E6_ACCEPTANCE_PROTOCOL.json).

    python -B code/acceptance.py run   --outdir evidence/acceptance_r1 [--records DIR]
    python -B code/acceptance.py check --outdir evidence/acceptance_r1

Runs on rebaseguard-vultr-02 from a clean checkout. Reads the certified CUSUM K1 records 0-309 read-only, with L = None.
Scratch copies for input mutants live under /var/tmp/e6scratch and are removed. No real R''' / R^(5) exists or is read.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import random
import shutil
import socket
import subprocess
import sys
import tempfile
import types
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
REPO = NS.parents[2]
sys.path.insert(0, str(HERE))

import consumption_adapter as AD  # noqa: E402
import crosscheck as XC  # noqa: E402

PROTOCOL = NS / "config/E6_ACCEPTANCE_PROTOCOL.json"
RESULT_SCHEMA = "rebaseguard.p5y.k5b.consumption-adapter.acceptance-result.v1"
SCRATCH = Path("/var/tmp/e6scratch")
REAL_NS = Path("/root/work/k5-first-real-probe")
PROTO_NS = REPO / "level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol"
EXEC_NS = REPO / "level4/closure_proofs/p5y_k5_cusum_real_point_executor"
FORBIDDEN = ("CUSUM_MINIMALITY", "closed_by_k1", "needs_order3", "k5-first-real-probe", "SCIENTIFIC_RECORD_SEALED",
             "slot-", "L0", "U0", "L1_m", "U1", "R3", "R5", "float(", "random", "time")
ALLOWED_IMPORTS = {"__future__", "argparse", "hashlib", "json", "sys", "types", "fractions", "pathlib"}
SEED = 20260918


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expand(rs):
    return [x for lo, hi in rs for x in range(lo, hi + 1)]


def git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True).stdout.strip()


# ------------------------------------------------------------------ G01 / G02

def preconditions(proto: dict) -> dict:
    guard = json.loads((EXEC_NS / "config/REAL_INPUT_GUARD.json").read_text()).get("policy")
    absent = {"AUTHORIZATION_ACTIVE": PROTO_NS / "protocol/AUTHORIZATION_ACTIVE.json",
              "EXECUTION_BINDING_AMENDMENT": PROTO_NS / "protocol/EXECUTION_BINDING_AMENDMENT.json",
              "ATTEMPT_LEDGER": PROTO_NS / "ledger/ATTEMPT_LEDGER.jsonl",
              "COUNTERSIGNATURE_ACTIVE": EXEC_NS / "authorization/COUNTERSIGNATURE_ACTIVE.json",
              "REAL_NAMESPACE": REAL_NS}
    pins = {rel: sha(REPO / rel) == pin for rel, pin in proto["component_pins"].items()}
    prereg = sha(REPO / proto["science_preregistration"]["path"]) == proto["science_preregistration"]["sha256"]
    row = {"guard_policy": guard, "absent": {k: not p.exists() for k, p in absent.items()},
           "component_pins_match": pins, "science_preregistration_unchanged": prereg,
           "adapter_pins_equal_protocol": {AD.LOADER: AD.PINS[AD.LOADER], AD.THEOREM: AD.PINS[AD.THEOREM]}
           == proto["component_pins"]}
    row["ok"] = (guard == "DENY" and all(row["absent"].values()) and all(pins.values()) and prereg
                 and row["adapter_pins_equal_protocol"])
    return row


def input_hashes(proto: dict, records_dir: Path) -> dict:
    lo, hi = proto["records"]["range"]
    return {"manifest": sha(REPO / proto["manifest"]["path"]), "cells_json": sha(REPO / proto["cells_json"]["path"]),
            "expected_evidence": sha(REPO / proto["expected_evidence"]["path"]),
            "records": {str(i): sha(records_dir / f"aux5_CUSUM_{i}_256.json") for i in range(lo, hi + 1)}}


def inputs_bound(proto: dict, h: dict) -> dict:
    manifest = json.loads((REPO / proto["manifest"]["path"]).read_text())["files"]
    bad = [i for i, s in h["records"].items() if manifest.get(f"k4_records/aux5_CUSUM_{i}_256.json") != s]
    ok = (h["manifest"] == proto["manifest"]["sha256"] and h["cells_json"] == proto["cells_json"]["sha256"]
          and h["expected_evidence"] == proto["expected_evidence"]["sha256"] and not bad and len(h["records"]) == 310)
    return {"record_count": len(h["records"]), "record_manifest_mismatches": bad, "ok": ok}


# ------------------------------------------------------------------ G03 / G04

def expected_sets(proto: dict) -> dict:
    ev = json.loads((REPO / proto["expected_evidence"]["path"]).read_text())
    from_file = {m: ev["per_m"][m]["closed_by_k1"] for m in proto["m_values"]}
    if from_file != proto["expected_pass_ranges"]:
        raise SystemExit("the evidence file's pass sets differ from the frozen protocol table")
    return {m: expand(r) for m, r in from_file.items()}


def compare(expected: dict, result: dict) -> dict:
    per_m = {}
    for m, exp in expected.items():
        obs = result["per_m"][m]["pass"]
        per_m[m] = {"EXPECTED_PASS_SET": AD_ranges(exp), "OBSERVED_PASS_SET": AD_ranges(sorted(set(obs))),
                    "FALSE_POSITIVES": sorted(set(obs) - set(exp)), "FALSE_NEGATIVES": sorted(set(exp) - set(obs)),
                    "strictly_increasing": all(a < b for a, b in zip(obs, obs[1:])),
                    "equal": set(obs) == set(exp) and len(obs) == len(exp)}
    ok = all(v["equal"] and v["strictly_increasing"] and not v["FALSE_POSITIVES"] and not v["FALSE_NEGATIVES"]
             for v in per_m.values()) and result["universe"] == [0, 309] and result["cell_count"] == 310
    return {"per_m": per_m, "ok": ok}


def AD_ranges(xs):
    out = []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def adapter_process(records_dir: Path, out: Path, hashseed: str) -> dict:
    env = dict(os.environ, PYTHONHASHSEED=hashseed)
    p = subprocess.run([sys.executable, "-B", str(HERE / "consumption_adapter.py"), "consume", "--records",
                        str(records_dir), "--out", str(out)], capture_output=True, text=True, env=env)
    return {"exit": p.returncode, "stderr": p.stderr[-400:], "sha256": sha(out) if out.exists() else None}


# ------------------------------------------------------------------ G06 synthetic fixtures

def synthetic_fixtures(KB, n=6):
    """Deterministic fixtures from the frozen k5b_check generators; per m a different odd polynomial on one cover;
    kept only when every H.lo <= 0 and the pass sets are non-trivial."""
    rng = random.Random(SEED)
    out, tries = [], 0
    while len(out) < n and tries < 400:
        tries += 1
        xs = KB.make_cover(rng)
        while xs[-1] <= 2:
            xs.append(xs[-1] + Fraction(1, 4))
        xs = xs + [xs[-1] + Fraction(1, 2)]
        per_m, sets = {}, {}
        for m in AD.MS:
            for _ in range(600):
                cs = KB.synthetic_cells(KB.random_odd_poly(rng), xs, rng, pieces=8, widen=20, l_drop=1.0)
                if all(c["H"][0] <= 0 for c in cs):
                    lit = [i for i, r in enumerate(KB.k5b_literal(cs)) if r["pass"]]
                    if 0 < len(lit) < len(cs):
                        per_m[m], sets[m] = cs, tuple(lit)
                        break
        if len(per_m) == len(AD.MS) and len(set(sets.values())) > 1:
            out.append((xs, per_m))
    return out


def write_fixture(root: Path, xs, per_m, *, drop_field=None, symlink_record=None):
    rec_dir = root / "k4_records"
    rec_dir.mkdir(parents=True)
    table = [{"detector": "CUSUM", "index": i, "left": [str(a), "0/1"], "right": [str(b), "0/1"],
              "rho": [str((b - a) / 2), "0/1"], "e0": [str((a + b) / 2), "0/1"]} for i, (a, b) in enumerate(zip(xs, xs[1:]))]
    (root / "cells.json").write_text(json.dumps(table))
    files = {}
    n = len(per_m["1"])
    for i in range(n):
        m_entries = {}
        for m in AD.MS:
            c = per_m[m][i]
            m_entries[m] = {"e0": str(c["e0"]), "rho": str(c["rho"]),
                            "R_interval": {"lo": str(c["R"][0]), "hi": str(c["R"][1])},
                            "D_interval": {"lo": str(c["D"][0]), "hi": str(c["D"][1])},
                            "R2_interval": {"lo": str(c["H"][0]), "hi": str(c["H"][1])}, "M_R2": str(c["M"])}
            if drop_field and i == n - 1:
                m_entries[m].pop(drop_field)
        data = json.dumps({"cell_index": i, "detector": "CUSUM", "m": m_entries}).encode()
        name = f"aux5_CUSUM_{i}_256.json"
        if symlink_record == i:
            (root / name).write_bytes(data)
            (rec_dir / name).symlink_to(root / name)
        else:
            (rec_dir / name).write_bytes(data)
        files[f"k4_records/{name}"] = hashlib.sha256(data).hexdigest()
    (root / "MANIFEST.json").write_text(json.dumps({"files": files}))
    return {"records": rec_dir, "cells": root / "cells.json", "manifest": root / "MANIFEST.json",
            "manifest_sha256": sha(root / "MANIFEST.json"), "cells_sha256": sha(root / "cells.json"),
            "universe": (0, n - 1)}


def fixture_eval(adapter, fx, components, L1=None):
    return adapter.evaluate(fx["records"], fx["cells"], fx["manifest"], manifest_sha256=fx["manifest_sha256"],
                            cells_sha256=fx["cells_sha256"], universe=fx["universe"], L1=L1, components=components)


def synthetic_differential(adapter, fixtures, components, KM) -> dict:
    rows = []
    for j, (xs, per_m) in enumerate(fixtures):
        with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
            fx = write_fixture(Path(td), xs, per_m)
            try:
                res = fixture_eval(adapter, fx, components)
            except Exception as exc:
                rows.append({"fixture": j, "ok": False, "error": f"{type(exc).__name__}: {exc}"[:300]})
                continue
            oracle = KM.scan(fx["records"], fx["cells"], "CUSUM")
            per = {m: (res["per_m"][m]["pass"] == KM.expand(oracle["per_m"][m]["closed_by_k1"])) for m in AD.MS}
            rows.append({"fixture": j, "cells": len(per_m["1"]), "per_m_equal": per, "ok": all(per.values())})
    return {"fixtures": rows, "ok": bool(rows) and all(r["ok"] for r in rows)}


# ------------------------------------------------------------------ G08 static fences

def static_fences(source: str) -> dict:
    hits = [s for s in FORBIDDEN if s in source]
    imports = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imports |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call) and getattr(node.func, "id", None) == "__import__":
            imports.add("__import__")
    extra = sorted(imports - ALLOWED_IMPORTS)
    return {"forbidden_hits": hits, "disallowed_imports": extra, "ok": not hits and not extra}


# ------------------------------------------------------------------ G09 fail-closed rows

def fail_closed(fixtures, components) -> dict:
    xs, per_m = fixtures[0]
    rows = {}

    def refused(name, fn):
        try:
            fn()
            rows[name] = {"refused": False, "ok": False}
        except AD.AdapterRefusal as exc:
            rows[name] = {"refused": True, "reason": str(exc)[:200], "ok": True}

    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
        fx = write_fixture(Path(td), xs, per_m)
        base = {m: None for m in AD.MS}
        refused("L1_float", lambda: fixture_eval(AD, fx, components, {**base, "1": 0.5}))
        refused("L1_bool", lambda: fixture_eval(AD, fx, components, {**base, "1": True}))
        refused("L1_int", lambda: fixture_eval(AD, fx, components, {**base, "1": 1}))
        refused("L1_string", lambda: fixture_eval(AD, fx, components, {**base, "1": "1/2"}))
        refused("L1_extra_key", lambda: fixture_eval(AD, fx, components, {**base, "4": None}))
        refused("L1_missing_key", lambda: fixture_eval(AD, fx, components, {m: None for m in ("1", "2", "3")}))
        refused("L1_list", lambda: fixture_eval(AD, fx, components, [None] * 4))
        refused("wrong_universe", lambda: AD.evaluate(fx["records"], fx["cells"], fx["manifest"],
                                                      manifest_sha256=fx["manifest_sha256"],
                                                      cells_sha256=fx["cells_sha256"],
                                                      universe=(0, fx["universe"][1] + 1), components=components))
        refused("wrong_cells_binding", lambda: AD.evaluate(fx["records"], fx["cells"], fx["manifest"],
                                                           manifest_sha256=fx["manifest_sha256"], cells_sha256="0" * 64,
                                                           universe=fx["universe"], components=components))
        pos = fixture_eval(AD, fx, components, {m: Fraction(1) for m in AD.MS})
        rows["L1_positive_exact_passes_cell_0"] = {"ok": all(0 in pos["per_m"][m]["pass"] for m in AD.MS)}
    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
        fx = write_fixture(Path(td), xs, per_m, drop_field="R2_interval")
        refused("missing_field", lambda: fixture_eval(AD, fx, components))
    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
        fx = write_fixture(Path(td), xs, per_m, symlink_record=1)
        refused("symlinked_record", lambda: fixture_eval(AD, fx, components))
    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
        fx = write_fixture(Path(td), xs, per_m)
        (fx["records"] / "aux5_CUSUM_0_256.json").write_text("{}")
        refused("record_bytes_changed", lambda: fixture_eval(AD, fx, components))
    return {"rows": rows, "ok": all(r["ok"] for r in rows.values())}


# ------------------------------------------------------------------ G07 mutations

SOURCE_MUTANTS = {
    "M01": ('passed = [cover[i]["index"] for i, r in enumerate(rows) if r["pass"] is True]',
            'passed = [cover[i]["index"] + 1 for i, r in enumerate(rows) if r["pass"] is True]'),
    "M02": ("        cells = cells_for_m(KM, cover, records, m, L1[m])\n",
            "        cells = cells_for_m(KM, cover, records, m, L1[m])[:-1]\n        cover = cover[:-1]\n"),
    "M03": ("        cells = cells_for_m(KM, cover, records, m, L1[m])\n",
            "        cells = cells_for_m(KM, cover, records, m, L1[m])\n        cells.insert(150, cells[150])\n"),
    "M04": ('DETECTOR = "CUSUM"', 'DETECTOR = "SR"'),
    "M05": ('r = records[k].get("m", {}).get(m)', 'r = records[k].get("m", {}).get(MS[(MS.index(m) + 1) % len(MS)])'),
    "M06": ('"L": L1m if k == cover[0]["index"] else None',
            '"L": (Fraction(1) if L1m is None else L1m) if k == cover[0]["index"] else None'),
    "M07": ('if r["pass"] is True]', 'if r["pass"] is not True]'),
    "M13": ("    return {\"schema\": SCHEMA,",
            "    if all(v is None for v in L1.values()):\n"
            "        ev = json.loads((REPO / 'level4/closure_proofs/p5y_k5_order3_readiness_audit/evidence/"
            "CUSUM_MINIMALITY_R1.json').read_text())\n"
            "        for m in MS:\n"
            "            per_m[m]['pass'] = [x for lo, hi in ev['per_m'][m]['closed_by_k1'] for x in range(lo, hi + 1)]\n"
            "    return {\"schema\": SCHEMA,"),
    "M14": ('        opened = [k for k in indices if k not in set(passed)]\n',
            '        opened = [k for k in indices if k not in set(passed)]\n'
            '        __import__("random").shuffle(passed)\n'),
}


def mutant_module(source: str) -> types.ModuleType:
    mod = types.ModuleType("consumption_adapter_mutant")
    mod.__file__ = str(HERE / "consumption_adapter.py")          # REPO resolves as for the real adapter
    exec(compile(source, "consumption_adapter_mutant.py", "exec"), mod.__dict__)
    return mod


def evaluate_candidate(mod, source, expected, records_dir, fixtures, KM) -> dict:
    """The acceptance checks applied to one candidate adapter module. Returns the list of failing checks."""
    failing, detail = [], {}
    try:
        comps = mod.frozen_components(REPO)
        r1 = mod.consume(None, records_dir=records_dir)
        r2 = mod.consume(None, records_dir=records_dir)
        cmp = compare(expected, r1)
        detail["comparison"] = {m: {k: v[k] for k in ("FALSE_POSITIVES", "FALSE_NEGATIVES", "strictly_increasing")}
                                for m, v in cmp["per_m"].items()}
        if not cmp["ok"]:
            failing.append("G03_ACCEPTANCE")
        if AD.canonical(r1) != AD.canonical(r2):
            failing.append("G04_DETERMINISM")
    except Exception as exc:
        failing.append("REFUSED")
        detail["refusal"] = f"{type(exc).__name__}: {exc}"[:300]
        comps = None
    if comps is not None:
        syn = synthetic_differential(mod, fixtures, comps, KM)
        if not syn["ok"]:
            failing.append("G06_SYNTHETIC_DIFFERENTIAL")
    if not static_fences(source)["ok"]:
        failing.append("G08_STATIC_FENCES")
    return {"failing": failing, "detail": detail}


def input_mutants(expected, records_dir: Path) -> dict:
    out = {}
    base = SCRATCH / "inputs"
    shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True)

    def attempt(fn):
        try:
            res = fn()
            return {"refused": False, "failing": [] if compare(expected, res)["ok"] else ["G03_ACCEPTANCE"]}
        except AD.AdapterRefusal as exc:
            return {"refused": True, "reason": str(exc)[:200], "failing": ["REFUSED"]}

    try:
        recs = base / "records"
        shutil.copytree(records_dir, recs, symlinks=True)
        (recs / "aux5_CUSUM_200_256.json").unlink()
        shutil.copyfile(records_dir / "aux5_CUSUM_201_256.json", recs / "aux5_CUSUM_200_256.json")
        out["M08"] = attempt(lambda: AD.consume(None, records_dir=recs))
        (recs / "aux5_CUSUM_200_256.json").unlink()
        shutil.copyfile(records_dir / "aux5_CUSUM_200_256.json", recs / "aux5_CUSUM_200_256.json")
        (recs / "aux5_CUSUM_309_256.json").unlink()
        out["M10"] = attempt(lambda: AD.consume(None, records_dir=recs))
        stale = base / "MANIFEST_STALE.json"
        m = json.loads((REPO / AD.MANIFEST).read_text())
        m["files"].pop("k4_records/aux5_CUSUM_325_256.json")
        stale.write_text(json.dumps(m, indent=1))
        out["M09"] = attempt(lambda: AD.evaluate(records_dir, REPO / AD.CELLS_JSON, stale,
                                                 manifest_sha256=AD.MANIFEST_SHA256, cells_sha256=AD.CELLS_SHA256,
                                                 components=AD.frozen_components(REPO)))
        for mid, rel, change in (("M11", AD.LOADER, lambda b: b + b"\n# modified\n"),
                                 ("M12", AD.THEOREM, lambda b: b.replace(b"(lambda a, b: a < b)", b"(lambda a, b: a <= b)", 1))):
            root = base / mid
            (root / rel).parent.mkdir(parents=True)
            for r in (AD.LOADER, AD.THEOREM):
                (root / r).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / r, root / r)
            original = (root / rel).read_bytes()
            changed = change(original)
            if changed == original:
                raise SystemExit(f"{mid}: the mutation did not change the component (harness error)")
            (root / rel).write_bytes(changed)
            out[mid] = attempt(lambda: AD.evaluate(records_dir, REPO / AD.CELLS_JSON, REPO / AD.MANIFEST,
                                                   manifest_sha256=AD.MANIFEST_SHA256, cells_sha256=AD.CELLS_SHA256,
                                                   components=AD.frozen_components(root)))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    return out


def mutations(expected, records_dir, fixtures, KM) -> dict:
    source = (HERE / "consumption_adapter.py").read_text()
    rows = {}
    for mid, (old, new) in SOURCE_MUTANTS.items():
        if source.count(old) != 1:
            raise SystemExit(f"{mid}: anchor does not match exactly once (harness error)")
        msrc = source.replace(old, new)
        rows[mid] = evaluate_candidate(mutant_module(msrc), msrc, expected, records_dir, fixtures, KM)
    rows.update(input_mutants(expected, records_dir))
    for r in rows.values():
        r["detected"] = bool(r["failing"])
    want = sorted(json.loads(PROTOCOL.read_text())["mutations"])
    return {"rows": dict(sorted(rows.items())), "declared": want,
            "detected": sum(r["detected"] for r in rows.values()),
            "ok": sorted(rows) == want and all(r["detected"] for r in rows.values())}


# ------------------------------------------------------------------ run / check

def provenance(tag: str) -> dict:
    return {f"git_commit_{tag}": git("rev-parse", "HEAD"), f"porcelain_{tag}": git("status", "--porcelain")}


def run(outdir: Path, records_dir: Path) -> int:
    proto = json.loads(PROTOCOL.read_text())
    prov = {"host": socket.gethostname(), "python": platform.python_version(), **provenance("start")}
    SCRATCH.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    gates = {}
    gates["G01_PRECONDITIONS"] = preconditions(proto)
    before = input_hashes(proto, records_dir)
    gates["G02_INPUTS_BOUND"] = inputs_bound(proto, before)
    expected = expected_sets(proto)

    p1 = adapter_process(records_dir, outdir / "ADAPTER_OUTPUT.json", "1")
    p2 = adapter_process(records_dir, SCRATCH / "ADAPTER_OUTPUT_2.json", "2")
    result = json.loads((outdir / "ADAPTER_OUTPUT.json").read_text()) if p1["exit"] == 0 else None
    cmp = compare(expected, result) if result else {"ok": False, "per_m": {}}
    gates["G03_ACCEPTANCE"] = {"adapter_exit": p1["exit"], "stderr": p1["stderr"], **cmp}
    gates["G04_DETERMINISM"] = {"run_1": p1, "run_2": p2,
                                "ok": p1["exit"] == p2["exit"] == 0 and p1["sha256"] == p2["sha256"]}
    (SCRATCH / "ADAPTER_OUTPUT_2.json").unlink(missing_ok=True)

    xc = XC.run(REPO, records_dir, result) if result else {"status": "FAIL"}
    (outdir / "CROSSCHECK.json").write_text(json.dumps(xc, indent=1, sort_keys=True) + "\n")
    gates["G05_INDEPENDENT_CROSSCHECK"] = {"status": xc["status"], "checks": xc.get("checks"),
                                           "sha256": sha(outdir / "CROSSCHECK.json"), "ok": xc["status"] == "PASS"}

    comps = AD.frozen_components(REPO)
    KM, KB = comps["loader"], comps["theorem"]
    fixtures = synthetic_fixtures(KB)
    gates["G06_SYNTHETIC_DIFFERENTIAL"] = synthetic_differential(AD, fixtures, comps, KM)
    mut = mutations(expected, records_dir, fixtures, KM)
    (outdir / "MUTATIONS.json").write_text(json.dumps(mut, indent=1, sort_keys=True) + "\n")
    gates["G07_MUTATIONS"] = {"declared": len(mut["declared"]), "detected": mut["detected"],
                              "sha256": sha(outdir / "MUTATIONS.json"), "ok": mut["ok"]}
    gates["G08_STATIC_FENCES"] = static_fences((HERE / "consumption_adapter.py").read_text())
    gates["G09_FAIL_CLOSED"] = fail_closed(fixtures, comps)

    after = input_hashes(proto, records_dir)
    gates["G02_INPUTS_BOUND"]["unchanged_after_run"] = after == before
    gates["G02_INPUTS_BOUND"]["ok"] = gates["G02_INPUTS_BOUND"]["ok"] and after == before
    gates["G01_PRECONDITIONS"]["still_ok_at_end"] = preconditions(proto)["ok"]
    gates["G01_PRECONDITIONS"]["ok"] = gates["G01_PRECONDITIONS"]["ok"] and gates["G01_PRECONDITIONS"]["still_ok_at_end"]
    leftover = [p.name for p in SCRATCH.iterdir()] if SCRATCH.exists() else []
    shutil.rmtree(SCRATCH, ignore_errors=True)

    prov.update(provenance("end"))
    prov.update({"records_dir": str(records_dir), "scratch_leftover_before_cleanup": leftover,
                 "adapter_sha256": sha(HERE / "consumption_adapter.py"), "crosscheck_sha256": sha(HERE / "crosscheck.py"),
                 "acceptance_sha256": sha(HERE / "acceptance.py"), "acceptance_protocol_sha256": sha(PROTOCOL),
                 "component_pins": proto["component_pins"],
                 "manifest_sha256": before["manifest"], "cells_json_sha256": before["cells_json"],
                 "expected_evidence_sha256": before["expected_evidence"],
                 "records_sha256": hashlib.sha256(AD.canonical(before["records"])).hexdigest()})
    clean = prov["porcelain_start"] == "" and prov["porcelain_end"] == "" and prov["git_commit_start"] == prov["git_commit_end"]
    (outdir / "PROVENANCE.json").write_text(json.dumps(prov, indent=1, sort_keys=True) + "\n")
    all_ok = all(g["ok"] for g in gates.values()) and clean
    per_m = cmp.get("per_m", {})
    res = {"schema": RESULT_SCHEMA, "gates": gates, "provenance_clean": clean,
           "EXPECTED_PASS_SET": {m: v["EXPECTED_PASS_SET"] for m, v in per_m.items()},
           "OBSERVED_PASS_SET": {m: v["OBSERVED_PASS_SET"] for m, v in per_m.items()},
           "FALSE_POSITIVES": {m: v["FALSE_POSITIVES"] for m, v in per_m.items()},
           "FALSE_NEGATIVES": {m: v["FALSE_NEGATIVES"] for m, v in per_m.items()},
           "CELL_COUNT": result["cell_count"] if result else None,
           "RECORD_MANIFEST_SHA256": before["manifest"], "RECORDS_SHA256": prov["records_sha256"],
           "ADAPTER_SHA256": prov["adapter_sha256"], "ADAPTER_OUTPUT_SHA256": p1["sha256"],
           "LOADER_SHA256": sha(REPO / AD.LOADER), "K5B_LITERAL_SHA256": sha(REPO / AD.THEOREM),
           "ACCEPTANCE_PROTOCOL_SHA256": prov["acceptance_protocol_sha256"],
           "PROVENANCE_SHA256": sha(outdir / "PROVENANCE.json"),
           "L": "None", "REAL_R3_VALUE_OBSERVED": "NO", "REAL_R5_VALUE_OBSERVED": "NO",
           "EXECUTION_AUTHORIZED": False, "REAL_INPUT_ARITHMETIC_GUARD": gates["G01_PRECONDITIONS"]["guard_policy"],
           "E6_K5B_CONSUMPTION_ADAPTER": "ACCEPTED" if all_ok else "FAILED"}
    (outdir / "ACCEPTANCE_RESULT.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"E6": res["E6_K5B_CONSUMPTION_ADAPTER"], "gates": {k: g["ok"] for k, g in gates.items()},
                      "clean": clean, "result_sha256": sha(outdir / "ACCEPTANCE_RESULT.json")}, indent=1))
    return 0 if all_ok else 1


def check(outdir: Path) -> int:
    res = json.loads((outdir / "ACCEPTANCE_RESULT.json").read_text())
    proto = json.loads(PROTOCOL.read_text())
    problems = []
    for name, key in (("PROVENANCE.json", "PROVENANCE_SHA256"), ("ADAPTER_OUTPUT.json", "ADAPTER_OUTPUT_SHA256")):
        if sha(outdir / name) != res[key]:
            problems.append(f"{name} hash differs")
    for g, name in (("G05_INDEPENDENT_CROSSCHECK", "CROSSCHECK.json"), ("G07_MUTATIONS", "MUTATIONS.json")):
        if sha(outdir / name) != res["gates"][g]["sha256"]:
            problems.append(f"{name} hash differs")
    out = json.loads((outdir / "ADAPTER_OUTPUT.json").read_text())
    if {m: v["pass_ranges"] for m, v in out["per_m"].items()} != proto["expected_pass_ranges"]:
        problems.append("adapter output differs from the frozen expected pass sets")
    if res["ACCEPTANCE_PROTOCOL_SHA256"] != sha(PROTOCOL):
        problems.append("acceptance protocol changed")
    if res["LOADER_SHA256"] != proto["component_pins"][AD.LOADER] or res["K5B_LITERAL_SHA256"] != proto["component_pins"][AD.THEOREM]:
        problems.append("component pins differ")
    if any(res["FALSE_POSITIVES"].values()) or any(res["FALSE_NEGATIVES"].values()):
        problems.append("false positives or negatives recorded")
    if not all(g["ok"] for g in res["gates"].values()) or res["E6_K5B_CONSUMPTION_ADAPTER"] != "ACCEPTED":
        problems.append("a gate failed")
    print(json.dumps({"E6_CHECK": not problems, "problems": problems}, indent=1))
    return 0 if not problems else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="E6 acceptance")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--outdir", required=True)
    r.add_argument("--records", default=AD.HOST_RECORDS_DIR)
    c = sub.add_parser("check")
    c.add_argument("--outdir", required=True)
    a = ap.parse_args()
    if a.cmd == "run":
        return run(Path(a.outdir), Path(a.records))
    return check(Path(a.outdir))


if __name__ == "__main__":
    sys.exit(main())
