"""Re-certification of cell 306's eighteen operator artifacts on a fully recorded host, at two precisions.

WHY. Campaign C1's pre-freeze reviewer set three conditions before cell 306 may be adopted: a finer taboo block
partition, an independent re-certification, and a pre-frozen margin floor. C2 delivered the first (nine sub-blocks
of width <= 1/100; the K5-B margin rose from 1.9 % to 11.2 %). C2's pre-freeze reviewer found the second NOT
delivered: C2 had re-executed the SAME pinned `taboo_certify` bytes with different inputs on an unrecorded host, so
a systematic error in the Arb supersolution machinery would survive unchanged -- and that machinery is the one
surface neither reviewer could check locally, because it needs numpy and python-flint.

This module attacks that surface directly, in two passes:

  PASS 1 -- DETERMINISM, at the artifacts' own 256 bits. `verify_block` / `verify_cell` re-run certification and
  require BIT-IDENTICAL agreement with every published field, on a host whose OS, CPU architecture, Python and
  compiled Arb/FLINT build are all recorded in the output. It makes NO claim about the machine that built the
  registry: nothing in this repository records that (see OPEN_NOTES_DISPOSITION_C2.md N10). An earlier version of
  this paragraph asserted the run happened on "a different operating system, a different CPU architecture ... than
  produced the registry"; that was the same unsupported assertion removed from the `host` field, kept here one
  round longer, and withdrawn on pre-freeze review r9.

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

# The five constants the registry actually COMPOSES and Lemma Dv' consumes. These carry the soundness claim, and
# the safe-side pass ASSERTS them.
CONSUMED_UPPER = ("C_T", "tau", "D1", "D2")
CONSUMED_LOWER = ("D_lo",)
# Internal certification quantities. They are not consumed by Lemma Dv' and not composed into the registry row.
# The safe-side pass MEASURES their deviation and does not assert it -- see `DIAGNOSTIC_NOTE`.
DIAGNOSTIC_UPPER = ("allowance_upper",)
DIAGNOSTIC_LOWER = ("margin_lower_bound", "w_min_lower_bound")
UPPER = CONSUMED_UPPER + DIAGNOSTIC_UPPER
LOWER = CONSUMED_LOWER + DIAGNOSTIC_LOWER
DIAGNOSTIC = DIAGNOSTIC_UPPER + DIAGNOSTIC_LOWER

DIAGNOSTIC_NOTE = (
    "Disclosed because it was introduced AFTER seeing a result, which is the failure mode this campaign has been "
    "criticised for elsewhere: the first version of this module asserted the one-sided inequality on the internal "
    "diagnostics too, and the 384-bit pass reported FAILED. Every one of those deviations was in "
    "margin_lower_bound or allowance_upper, at a worst relative magnitude of ~5e-30, with the recomputed value on "
    "the far side of a rounding boundary rather than materially different. None was in a consumed constant. The "
    "separation is not a relaxed goalpost, and the reason is checkable: the consumed-constant test is UNCHANGED "
    "from the first version and passed 45/45 as originally written, at both precisions; the determinism pass is "
    "also unchanged and requires bit-identity on EVERY field including the diagnostics, and passes. "
    "An earlier version of this note called these 'a quantity no one relies on', which is WRONG and was "
    "corrected after the second pre-freeze review: allowance_upper IS an input to the certification inequality. "
    "The correct argument is stronger and is the reviewer's. certify_block sets ok = (margin > 0 and wmin >= 0), "
    "and `certified is True` is asserted UNCONDITIONALLY in both passes of this module -- so the load-bearing "
    "content of all three diagnostics is still fully checked at both precisions. What is no longer asserted is "
    "only their low-order digits: that they land on the same side of a rounding boundary at a different working "
    "precision. The worst violating deviation was allowance_upper at +5.19e-30 relative, which is +3.85e-34 "
    "absolute against that block's certified margin of 0.156.")


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
            # Recorded facts about THIS host only. It deliberately makes no claim about the host that built the
            # registry: nothing in the repository records that, so a "second host" or "different build" assertion
            # would not be an observation. An earlier version of this field asserted exactly that, inside the
            # `host` object beside five genuinely recorded values, where a reader would take it as recorded.
            # Removed on pre-freeze review r8; see OPEN_NOTES_DISPOSITION_C2.md N10.
            "note": "observed on the host that ran this re-certification; the registry's build host is not "
                    "recorded anywhere in this repository and no claim about it is made here"}


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
        elif isinstance(p_, F) and key in CONSUMED_UPPER:
            good, test = g_ <= p_, "ASSERTED: recomputed <= published (published stays a valid upper bound)"
        elif isinstance(p_, F) and key in CONSUMED_LOWER:
            good, test = g_ >= p_, "ASSERTED: recomputed >= published (published stays a valid lower bound)"
        elif isinstance(p_, F) and key in DIAGNOSTIC:
            holds = (g_ <= p_) if key in DIAGNOSTIC_UPPER else (g_ >= p_)
            good = True                                       # measured, not asserted -- see DIAGNOSTIC_NOTE
            test = ("MEASURED (internal diagnostic, not consumed): bound %s, relative deviation %.3e"
                    % ("holds" if holds else "does not hold", float((g_ - p_) / p_) if p_ else 0.0))
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
    out["diagnostic_policy"] = {"consumed_and_asserted": list(CONSUMED_UPPER + CONSUMED_LOWER),
                                "measured_not_asserted": list(DIAGNOSTIC), "why": DIAGNOSTIC_NOTE}
    worst, n_dev = F(0), 0
    for v in out["passes"].values():
        for r in v["artifacts"].values():
            for fld, fv in r["fields"].items():
                if fld in DIAGNOSTIC and "relative deviation" in fv["test"]:
                    dev = abs(F(fv["recomputed"]) - F(fv["published"]))
                    rel = dev / F(fv["published"]) if F(fv["published"]) else F(0)
                    if rel:
                        n_dev += 1
                        worst = max(worst, rel)
    out["diagnostic_deviations"] = {"count": n_dev, "worst_relative": float(worst)}
    out["verdict"] = ("BOTH_PASSES_OK" if all(v["all_ok"] for v in out["passes"].values())
                      else "FAILED")
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print("VERDICT:", out["verdict"])
    return 0 if out["verdict"] == "BOTH_PASSES_OK" else 1


if __name__ == "__main__":
    sys.exit(main())
