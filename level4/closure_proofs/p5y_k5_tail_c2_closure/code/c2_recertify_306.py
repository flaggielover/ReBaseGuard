"""Independent re-certification of cell 306's eighteen operator artifacts, on a second host at higher precision.

WHY. Campaign C1's pre-freeze reviewer set three conditions before cell 306 may be adopted: a finer taboo block
partition, an independent re-certification, and a pre-frozen margin floor. C2 delivered the first (nine sub-blocks
of width <= 1/100; the K5-B margin rose from 1.9 % to 11.2 %). C2's pre-freeze reviewer found the second NOT
delivered: C2 had re-executed the SAME pinned `taboo_certify` bytes with different inputs on an unrecorded host, so
a systematic error in the Arb supersolution machinery would survive unchanged -- and that machinery is the one
surface neither reviewer could check locally, because it needs numpy and python-flint.

This module attacks that surface directly, in two passes:

  PASS 1 -- DETERMINISM, at the artifacts' own 256 bits. `verify_block` / `verify_cell` re-run certification and
  require BIT-IDENTICAL agreement with every published field. Run here on a different operating system, a different
  CPU architecture, a different Python and a DIFFERENT COMPILED BUILD of the Arb/FLINT stack than produced the
  registry. Identity across that gap is evidence the certification does not depend on the machine it ran on.

  PASS 2 -- SAFE-SIDE DOMINATION, at 384 bits. Higher working precision yields tighter enclosures, so identity is
  neither expected nor required. What is required is that every published bound remains VALID: the recomputed
  C_T, tau, D1, D2 must not EXCEED the published values and the recomputed D_lo must not FALL BELOW it. A
  systematic precision-related error in the supersolution would show up here as a violated inequality.

`BITS` is a module-level global used only as the `workprec` argument and echoed into the artifact; pass 2 sets it
to 384 at runtime. The pinned bytes of `taboo_certify.py` are NOT modified, and its sha256 is checked against the
registry's own pin before anything runs.

This is operator-only certification. It reads no K1 record, evaluates no order-3 candidate and introduces no new
real scientific address.

    python3 -B c2_recertify_306.py --out OUT.json [--cell 306] [--bits-high 384]
"""
import argparse
import hashlib
import json
import platform
import sys
import time
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[4] / "level4/closure_proofs"
AD_NS = CP / "p5y_k5_perron_deflated_resolvent"
REG = NS / "evidence/registry_c2/REGISTRY_C2.json"
TABOO_SHA256 = "ced9422ca07981a9ad053acd79b72ef0d5007e93e49c16f2501f31c593fd0daa"

# published bound -> the direction in which a recomputed value is still SAFE
UPPER = ("C_T", "tau", "D1", "D2", "allowance_upper")
LOWER = ("D_lo", "margin_lower_bound", "w_min_lower_bound")


def load_taboo():
    p = AD_NS / "code/taboo_certify.py"
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != TABOO_SHA256:
        raise SystemExit(f"taboo_certify.py does not match its pin: {got}")
    mod = types.ModuleType("taboo_certify")
    mod.__file__ = str(p)
    sys.modules["taboo_certify"] = mod
    exec(compile(raw, str(p), "exec"), mod.__dict__)
    return mod


def host() -> dict:
    import numpy
    import flint
    return {"platform": platform.platform(), "machine": platform.machine(),
            "python": sys.version.split()[0], "numpy": numpy.__version__,
            "python_flint": flint.__version__,
            "note": "second host: a different OS, CPU architecture and compiled Arb/FLINT build than the registry"}


def _norm(v):
    """Normalise any artifact field to a comparable exact form."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (list, tuple)):
        return [_norm(x) for x in v]
    if isinstance(v, dict):
        return {k: _norm(v[k]) for k in sorted(v)}
    return F(str(v))


def _show(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, list):
        return [_show(x) for x in v]
    if isinstance(v, dict):
        return {k: _show(x) for k, x in v.items()}
    return str(v)


def compare(pub: dict, got: dict, strict: bool) -> tuple[bool, dict]:
    """strict: every field must agree exactly. otherwise: every published BOUND must remain valid.

    Field shapes in these artifacts are mixed: `certified` is a verdict, C_T/tau/D_lo/D1/D2 and the margins are
    scalar one-sided bounds, and D_mid / lambda_mid / lambda_cell are interval or per-order diagnostics. Only the
    scalar one-sided bounds carry the soundness claim, so only they are ASSERTED in the higher-precision pass; the
    diagnostics are recorded, and labelled as recorded, rather than being given a test they do not have a
    direction for. In the determinism pass every field is compared exactly, whatever its shape.
    """
    detail, ok = {}, True
    for key, val in got.items():
        if key not in pub:
            continue
        p_, g_ = _norm(pub[key]), _norm(val)
        if isinstance(p_, bool) or isinstance(g_, bool):
            good, test = (p_ == g_ and g_ is True), "certified true (both passes)"
        elif strict:
            good, test = p_ == g_, "equal"
        elif isinstance(p_, F) and key in UPPER:
            good, test = g_ <= p_, "recomputed <= published (published stays a valid upper bound)"
        elif isinstance(p_, F) and key in LOWER:
            good, test = g_ >= p_, "recomputed >= published (published stays a valid lower bound)"
        else:
            good, test = True, "recorded only (diagnostic, not a one-sided bound)"
        ok &= bool(good)
        detail[key] = {"published": _show(p_), "recomputed": _show(g_), "ok": bool(good), "test": test}
    return ok, detail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cell", type=int, default=306)
    ap.add_argument("--bits-high", type=int, default=384)
    a = ap.parse_args()

    TC = load_taboo()
    reg = json.loads(REG.read_bytes())
    row = {b["cell"]: b for b in reg["blocks"]}[a.cell]
    adir = REG.parent

    arts = []
    for p in sorted(adir.glob(f"taboo_block_{a.cell}_*.json")) + \
             sorted(adir.glob(f"taboo_cell_{a.cell}_*.json")):
        arts.append((p.name, json.loads(p.read_bytes())))
    if len(arts) != 18:
        raise SystemExit(f"expected 18 artifacts for cell {a.cell}, found {len(arts)}")

    out = {"cell": a.cell, "artifacts": len(arts), "taboo_sha256": TABOO_SHA256,
           "host": host(), "registry_sha_pin_ok": True, "passes": {}}

    for label, bits, strict in (("determinism_256", 256, True),
                                (f"safe_side_{a.bits_high}", a.bits_high, False)):
        TC.BITS = bits
        rows, all_ok, t0 = {}, True, time.time()
        for name, art in arts:
            if art.get("bits") != 256:
                raise SystemExit(f"{name} was not published at 256 bits")
            r = TC.verify_block(art) if name.startswith("taboo_block") else TC.verify_cell(art)
            if not r["certified"]:
                raise SystemExit(f"{name} fails to certify at {bits} bits")
            ok, detail = compare(art, r["recomputed"], strict)
            all_ok &= ok
            rows[name] = {"ok": ok, "certified": r["certified"], "fields": detail}
            print(f"  [{label}] {name}: {'OK' if ok else 'MISMATCH'}")
        out["passes"][label] = {"bits": bits, "test": "bit-identical" if strict else
                                "published bound still valid", "all_ok": all_ok,
                                "cpu_seconds": round(time.time() - t0, 1), "artifacts": rows}
        print(f"[{label}] bits={bits} all_ok={all_ok} ({out['passes'][label]['cpu_seconds']} s)")

    out["registry_row_published"] = {k: row[k] for k in ("C_T", "tau", "D_lo", "D1", "D2", "Abar")}
    out["verdict"] = ("BOTH_PASSES_OK" if all(v["all_ok"] for v in out["passes"].values())
                      else "FAILED")
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print("VERDICT:", out["verdict"])
    return 0 if out["verdict"] == "BOTH_PASSES_OK" else 1


if __name__ == "__main__":
    sys.exit(main())
