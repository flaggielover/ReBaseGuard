"""Before/after comparison of the certified quantities touched by repair 1.

Runs the reviewed residual pass once and reports, for each of the three r = 0
objects, exactly what the repair removes:

    poly                the certified Bernstein range bound (unchanged)
    reviewed_extra      kernel truncation + reward_allow[k]   (the mixture)
    corrected_extra     kernel truncation alone               (representation A)
    reward_allow[k]     the closed-form S0 remainder
    removed             reviewed_delta_mid - repaired_delta_mid

`removed` must equal `reward_allow[k]` up to outward-rounding, and nothing else
may change. Numerical improvement is NOT treated as proof of correctness; the
accounting invariant in repair_check is.

usage: repair_compare.py --cell 221 [--bits 256] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

import prior                                                    # noqa: F401

import scoped                                                   # noqa: E402
import spec                                                     # noqa: E402
from intervals import (mag_fraction, pin_single_thread,          # noqa: E402
                       tight_upper, workprec)

import repair_layer2                                            # noqa: E402
from repair_layer2 import corrected_extra                       # noqa: E402

SITES = (("F_0", 0), ("dF_0", 1), ("H_0", 2))


def compare(index: int, *, bits: int = spec.PRODUCTION_BITS) -> dict:
    pin_single_thread()
    cell = next(c for c in spec.CELLS
                if c["detector"] == "CUSUM" and c["index"] == index)
    rows = {}
    with workprec(bits):
        cert = repair_layer2.RepairedCellCertifier(cell, bits=bits).prepare()
        reviewed = scoped.residuals_m1(cert)      # the reviewed m=1 residuals
        for name, k in SITES:
            entry = reviewed[name]
            poly = entry["polynomial_residual"]
            corrected = tight_upper(corrected_extra(cert, name))
            reward = tight_upper(cert.reward_allow[k])
            repaired_delta = tight_upper(poly + corrected)
            rev_delta = entry["delta_mid"]
            removed = mag_fraction(rev_delta) - mag_fraction(repaired_delta)
            raw = corrected_extra(cert, name)
            rev_extra = entry['truncation_allowance']
            rows[name] = {
                'raw_corrected_no_tight_upper': str(mag_fraction(raw)),
                'raw_radius': str(mag_fraction(__import__('flint').arb(raw.rad()))),
                'reviewed_extra_minus_reward': str(
                    mag_fraction(rev_extra) - mag_fraction(reward)),
                'reviewed_extra_minus_corrected': str(
                    mag_fraction(rev_extra) - mag_fraction(corrected)),
                "derivative_order": k,
                "polynomial_residual": str(mag_fraction(poly)),
                "reviewed_extra": str(mag_fraction(entry["truncation_allowance"])),
                "corrected_extra": str(mag_fraction(corrected)),
                "reward_allow": str(mag_fraction(reward)),
                "reviewed_delta_mid": str(mag_fraction(rev_delta)),
                "repaired_delta_mid": str(mag_fraction(repaired_delta)),
                "removed": str(removed),
                "removed_minus_reward": str(removed - mag_fraction(reward)),
                "removed_over_reward": (float(removed / mag_fraction(reward))
                                        if mag_fraction(reward) else None),
                "repair_only_tightens": removed >= 0,
            }
    return {"schema": "k1.repair1.before-after.v1", "detector": "CUSUM",
            "cell_index": index, "precision_bits": bits,
            "result_bearing": False, "production_run": False,
            "sites": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, default=221)
    ap.add_argument("--bits", type=int, default=spec.PRODUCTION_BITS)
    ap.add_argument("--out")
    args = ap.parse_args()
    report = compare(args.cell, bits=args.bits)
    text = json.dumps(report, indent=1, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
