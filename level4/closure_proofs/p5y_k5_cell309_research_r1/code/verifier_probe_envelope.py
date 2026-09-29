"""Drift envelope of every independent-verifier probe (review R2 condition C4; read-only audit, nothing is evaluated).

  python3 code/verifier_probe_envelope.py   -> evidence/VERIFIER_PROBE_ENVELOPE.json; exit 0 iff no probe that meets the
                                               quarantine band (or its mirror) on the real kernel was evaluated

For each recorded verification in verify/VERIFY_RESULTS.json (harness v2, current) and in the last harness-v1 record
(commit bf5c87c4), the probe certificates are RECONSTRUCTED with the harness's own constructors (mutants(), malformed();
building the dicts evaluates nothing), matched to the recorded outcome by name, and split into
  evaluated  (any outcome other than REFUSE: the verifier computed something), and
  refused    (REFUSE: rejected at parse time, before any evaluation).
Reported: per harness version and geometry class, the drift envelope [min, max] over block and weight_block of the
EVALUATED probes, and every probe meeting the band with its outcome.  The self-tests' kernel closed-form check is
covered by a replay of its seeded RNG sequence with the kernel evaluations removed.
"""
import importlib.util
import json
import random
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
NS_PREFIX = "level4/closure_proofs/p5y_k5_cell309_research_r1/"
V1_RESULTS_COMMIT = "bf5c87c4aa49272a69654fb7c904f5703b6b0c42"
V1_HARNESS_SHA = "54840bf4d364f7b4853b542d74f81f9c5cdbd9ad97e5b447a1a2b808e2a8d2be"
BAND = (Fr(6, 5), Fr(13, 5))   # q309: literal-ok (the quarantine band definition, used only to classify and refuse)
sys.path.insert(0, str(NS / "verify"))


def git_show(commit: str, rel: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{NS_PREFIX}{rel}"], cwd=REPO, capture_output=True,
                          check=True).stdout


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def meets_band(a: Fr, b: Fr) -> bool:
    return not (b < BAND[0] or a > BAND[1]) or not (b < -BAND[1] or a > -BAND[0])


def envelope(harness, results: dict, v2: bool) -> dict:
    env, inband, counts = {}, [], Counter()
    for rel, fr in results["files"].items():
        d = json.loads((NS / rel).read_text())
        g = d["geometry"]
        real = Fr(g["h"]) == 5 and Fr(g["k"]) == Fr(1, 2)
        fk = d.get("kernel")
        for lab, e in fr.items():
            if not isinstance(e, dict) or "verdict" not in e:
                continue
            raw = d["certificates"][lab]
            probes = [("genuine", raw, e["verdict"])]
            built = list(harness.mutants(raw)) + list(harness.malformed(raw, fk) if v2 else harness.malformed(raw))
            for t in built:
                rec = e.get("mutants", {}).get(t[0])
                if rec is not None:
                    probes.append((t[0], t[1], rec["verdict"]))
            for name, c, verdict in probes:
                ivs = [c.get("block")] + ([c["weight_block"]] if c.get("weight_block") else [])
                counts[("evaluated" if verdict != "REFUSE" else "refused", "real" if real else "synthetic")] += 1
                for iv in ivs:
                    try:
                        a, b = Fr(iv[0]), Fr(iv[1])
                    except (TypeError, ValueError, ZeroDivisionError):
                        continue
                    if real and meets_band(a, b):
                        inband.append({"file": rel.split("/")[-1], "cert": lab, "probe": name, "outcome": verdict})
                    if verdict == "REFUSE":
                        continue
                    k = "real" if real else "synthetic"
                    lo, hi = env.get(k, (a, b))
                    env[k] = (min(lo, a), max(hi, b))
    by = Counter((x["probe"].split("_")[0], x["outcome"]) for x in inband)
    return {"evaluated_envelope": {k: [str(v[0]), str(v[1])] for k, v in env.items()},
            "probe_counts": {f"{a}/{b}": n for (a, b), n in counts.items()},
            "inband_probes_by_kind_outcome": {f"{a}:{b}": n for (a, b), n in by.items()},
            "inband_evaluated": [x for x in inband if x["outcome"] != "REFUSE"],
            "inband_unsanctioned_refused": sorted({(x["file"], x["probe"]) for x in inband
                                                   if x["outcome"] == "REFUSE" and not x["probe"].startswith("7q")})}


def selftest_closed_form_drifts() -> dict:
    """replay of tests/test_verify_selftests.py::test_closed_form_vs_quadrature RNG consumption (seed 11) WITHOUT the
    kernel evaluations; valid while that test body is unchanged (checked by the caller via its text)."""
    rnd = random.Random(11)
    out = []
    for (h, k) in ((Fr(5), Fr(1, 2)), (Fr(3), Fr(1, 2)), (Fr(4), Fr(1, 3))):
        for _taboo in (False, True):
            d = rnd.choice([2, 4, 5])
            for _ in range(2):
                {(a, b): Fr(rnd.randint(-9, 9), rnd.randint(1, 5)) for a in range(d + 1) for b in range(d + 1 - a)}
            ec = Fr(rnd.randint(-8, 8), 8)
            S = float(h - 2 * k)
            for typ in ("tri", "small", "axp", "axm", "tri"):
                if typ == "tri":
                    p = rnd.uniform(0, S)
                    rnd.uniform(0, S - p)
                elif typ == "small":
                    p = rnd.uniform(0, float(k))
                    rnd.uniform(0, float(k) - p)
                elif typ == "axp":
                    rnd.uniform(S, float(h))
                else:
                    rnd.uniform(S, float(h))
                out.append((h == 5 and k == Fr(1, 2), float(ec) + rnd.uniform(-0.3, 0.3)))
    real = [e for r, e in out if r]
    return {"real_kernel_max_abs_drift": round(max(abs(e) for e in real), 6),
            "real_kernel_any_in_band": any(1.2 <= abs(e) <= 2.6 for e in real),
            "all_geometries_max_abs_drift": round(max(abs(e) for _, e in out), 6)}


def main() -> int:
    H2 = load_module(NS / "verify" / "run_verify_all.py", "harness_v2")
    with tempfile.TemporaryDirectory() as td:
        v1p = Path(td) / "run_verify_all_v1.py"
        raw_v1 = git_show(V1_RESULTS_COMMIT, "verify/run_verify_all.py")
        import hashlib
        assert hashlib.sha256(raw_v1).hexdigest() == V1_HARNESS_SHA, "v1 harness bytes differ from the recorded v1 sha"
        v1p.write_bytes(raw_v1)
        H1 = load_module(v1p, "harness_v1")
        r1 = envelope(H1, json.loads(git_show(V1_RESULTS_COMMIT, "verify/VERIFY_RESULTS.json")), False)
    r2 = envelope(H2, json.loads((NS / "verify" / "VERIFY_RESULTS.json").read_text()), True)
    body = (NS / "tests" / "test_verify_selftests.py").read_text()
    st = selftest_closed_form_drifts()
    st["test_body_has_seed_11_and_ec_pm_0_3"] = ("random.Random(11)" in body and "rnd.uniform(-0.3, 0.3)" in body)
    out = {"schema": "VERIFIER_PROBE_ENVELOPE/1", "harness_v1_results_commit": V1_RESULTS_COMMIT, "v1": r1, "v2": r2,
           "selftest_closed_form": st,
           "ok": not r1["inband_evaluated"] and not r2["inband_evaluated"] and not st["real_kernel_any_in_band"]}
    (NS / "evidence" / "VERIFIER_PROBE_ENVELOPE.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: out[k] for k in ("ok",)} | {"v1_env": r1["evaluated_envelope"],
                                                        "v2_env": r2["evaluated_envelope"],
                                                        "v1_inband": r1["inband_probes_by_kind_outcome"],
                                                        "v2_inband": r2["inband_probes_by_kind_outcome"],
                                                        "v1_unsanctioned_refused": r1["inband_unsanctioned_refused"],
                                                        "selftest": st}, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
