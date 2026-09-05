"""Provenance of the Arb radii in the kernel-truncation term.

The repair recomputes the local truncation allowance from the same certified
factors the reviewed pass used. Two evaluations of that expression do NOT agree
bit-for-bit, so this tool records where the width actually comes from, which is
what determines how tight the repair's over-removal guard can legitimately be.

Cheap: `prepare()` only, no Bernstein range bounds.

usage: repair_components.py --cell 221
"""
from __future__ import annotations

import argparse
import json

import prior                                                    # noqa: F401

from flint import arb                                           # noqa: E402

import spec                                                     # noqa: E402
from cusum_layer2 import Z_RANGE                                # noqa: E402
from intervals import (mag_fraction, pin_single_thread,          # noqa: E402
                       tight_upper, workprec)

import repair_layer2                                            # noqa: E402


def describe(name: str, x: arb) -> dict:
    mid = arb(x.mid())
    rad = arb(x.rad())
    m = mag_fraction(mid)
    r = mag_fraction(rad)
    return {"name": name, "mid": float(m), "rad": float(r),
            "relative_rad": float(r / m) if m else None}


def components(index: int, *, bits: int = spec.PRODUCTION_BITS) -> dict:
    pin_single_thread()
    cell = next(c for c in spec.CELLS
                if c["detector"] == "CUSUM" and c["index"] == index)
    with workprec(bits):
        cert = repair_layer2.RepairedCellCertifier(cell, bits=bits).prepare()
        sup_F = cert.sup["F", 0, 0]
        ez = cert.eps_z
        ez0 = cert.eps_zi(0)
        a1 = Z_RANGE * sup_F
        a = Z_RANGE * sup_F * ez0
        rows = [describe("sup_F (chebyshev sup)", sup_F),
                describe("eps_z (taylor_remainder)", ez),
                describe("eps_zi(0)", ez0),
                describe("Z_RANGE * sup_F", a1),
                describe("A = Z_RANGE * sup_F * eps_zi(0)", a),
                describe("reward_allow[0]", cert.reward_allow[0])]
        # Two independent evaluations of the SAME expression.
        b = Z_RANGE * sup_F * cert.eps_zi(0)
        agree = mag_fraction(tight_upper(a)) == mag_fraction(tight_upper(b))
    return {"cell_index": index, "precision_bits": bits,
            "components": rows,
            "repeated_evaluation_is_bit_identical": bool(agree),
            "result_bearing": False}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, default=221)
    args = ap.parse_args()
    print(json.dumps(components(args.cell), indent=1))


if __name__ == "__main__":
    main()
