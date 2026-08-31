#!/usr/bin/env python3
"""Rigorous Arb certification of the Priority-3 stability boundaries.

Scope, stated before any number is produced: this certifies the stability map
*only* for the two exact finite-support witnesses frozen by Priority 1 and
Priority 2.  The frozen infinite-horizon Gaussian CUSUM and Gaussian SR gains
are Monte Carlo estimates and are deliberately absent from this file.  No
result here may be read as certifying them.
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import flint
from flint import arb, ctx

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_p3_map.common import read_json, sha256, write_json  # noqa: E402
from rebaseguard_p3_map.config import (  # noqa: E402
    M_GRID, PROTOCOL, PROTOCOL_SHA256, RHO_GRID,
)
from rebaseguard_p3_map.provenance import exact_witness_gamma  # noqa: E402

PRECISION_BITS = 128
CERTIFIED_LAYERS = ("FINITE_SUPPORT_CUSUM_WITNESS", "FINITE_SUPPORT_SR_WITNESS")


def q(value: Fraction | int) -> arb:
    value = Fraction(value)
    return arb(value.numerator) / arb(value.denominator)


def ball(value: arb) -> dict[str, str]:
    return {"ball": str(value), "lower": str(value.lower()), "upper": str(value.upper())}


def certify_sr_stopping(witness: dict, threshold: Fraction) -> list[dict]:
    """Re-derive the SR alarm times in interval arithmetic."""
    rows = []
    for path in witness["paths"]:
        rp = rm = arb(0)
        first = None
        for step, item in enumerate(path["increments"], start=1):
            z = q(Fraction(*item))
            rp = (arb(1) + rp) * (z - q(Fraction(1, 2))).exp()
            rm = (arb(1) + rm) * (-z - q(Fraction(1, 2))).exp()
            if first is None and bool(rp >= q(threshold) or rm >= q(threshold)):
                first = step
        rows.append({
            "label": path["label"],
            "declared_tau": int(path["tau"]),
            "certified_tau": first,
            "pass": first == int(path["tau"]),
        })
    return rows


def certify_layer(layer: dict) -> dict:
    witness_path = ROOT / layer["gamma_source"]
    certificate_path = ROOT / layer["gamma_replay_source"]
    witness = read_json(witness_path)
    package_certificate = read_json(certificate_path)
    recorded = {int(r["m"]): r["exact"]["gamma"] for r in package_certificate["records"]}
    replay_grid = PROTOCOL["witness_m_replay"]["certified_in_priority_packages"]

    stopping = None
    if "sr" in witness:
        stopping = certify_sr_stopping(witness, Fraction(*witness["sr"]["threshold"]))

    records = []
    for m in M_GRID:
        gamma_q = exact_witness_gamma(witness, m)
        gamma_arb = q(gamma_q)
        replayed = m in replay_grid
        replay_ok = (not replayed) or Fraction(recorded[m]) == gamma_q

        distance_q = abs(Fraction(1) - gamma_q)
        rho_c_q = Fraction(1) / distance_q
        rho_c_arb = arb(1) / abs(arb(1) - gamma_arb)
        unit_arb = abs(q(rho_c_q) * (arb(1) - gamma_arb))
        # The boundary identity is certified *exactly* in rational arithmetic.
        # A ball can only be shown to enclose one, never to equal it, so the
        # interval result is recorded as a consistency enclosure, not as the
        # certification itself.
        unit_exact = rho_c_q * distance_q == 1
        unit_enclosed = bool(unit_arb.contains(arb(1)))

        cells = []
        for rho in RHO_GRID:
            rho_q = Fraction(str(rho))
            magnitude = abs(q(rho_q) * (arb(1) - gamma_arb))
            exact_magnitude = rho_q * distance_q
            if bool(magnitude < arb(1)):
                verdict = "LOCALLY-STABLE"
            elif bool(magnitude > arb(1)):
                verdict = "LOCALLY-UNSTABLE"
            elif exact_magnitude == 1:
                verdict = "BOUNDARY"
            else:
                verdict = "INCONCLUSIVE"
            cells.append({
                "rho": str(rho_q),
                "rho_float": float(rho),
                "abs_lambda_exact": str(exact_magnitude),
                "abs_lambda_interval": ball(magnitude),
                "certified_class": verdict,
                "strictly_separated_from_unit_magnitude":
                    verdict in ("LOCALLY-STABLE", "LOCALLY-UNSTABLE"),
            })

        records.append({
            "m": m,
            "gamma_exact": str(gamma_q),
            "gamma_interval": ball(gamma_arb),
            "gamma_replayed_against_closed_package": replayed,
            "closed_package_gamma": recorded.get(m),
            "gamma_replay_match": replay_ok,
            "provenance_kind": "REPLAYED_FROM_CLOSED_PACKAGE" if replayed
                               else "P3_NEW_EXACT_FROM_FROZEN_WITNESS",
            "rho_crit_exact": str(rho_c_q),
            "rho_crit_interval": ball(rho_c_arb),
            "rho_crit_in_admissible_domain": 0 <= rho_c_q <= 1,
            "unit_magnitude_at_rho_crit_interval": ball(unit_arb),
            "unit_magnitude_at_rho_crit_exact": unit_exact,
            "unit_magnitude_at_rho_crit_interval_encloses_one": unit_enclosed,
            "cells": cells,
            "all_cells_resolved": all(
                cell["certified_class"] != "INCONCLUSIVE" for cell in cells
            ),
        })

    return {
        "layer": layer["id"],
        "detector_family": layer["detector_family"],
        "witness": layer["gamma_source"],
        "witness_sha256": sha256(witness_path),
        "closed_certificate": layer["gamma_replay_source"],
        "closed_certificate_sha256": sha256(certificate_path),
        "sr_stopping_certificates": stopping,
        "records": records,
        "pass": all(
            row["gamma_replay_match"] and row["unit_magnitude_at_rho_crit_exact"]
            and row["unit_magnitude_at_rho_crit_interval_encloses_one"]
            and row["all_cells_resolved"] for row in records
        ) and (stopping is None or all(row["pass"] for row in stopping)),
    }


def main() -> None:
    ctx.prec = PRECISION_BITS
    manifest = read_json(CAMPAIGN / "manifest.json")
    for relative, expected in manifest["upstream_sources"].items():
        assert sha256(ROOT / relative) == expected, relative

    layers = [layer for layer in PROTOCOL["layers"] if layer["id"] in CERTIFIED_LAYERS]
    results = [certify_layer(layer) for layer in layers]
    payload = {
        "schema": "rebaseguard.p3-arb-certificate.v1",
        "campaign": PROTOCOL["campaign"],
        "evidence_class": "INTERVAL_CERTIFIED_FINITE_SUPPORT_WITNESSES_ONLY",
        "backend": f"python-flint {flint.__version__} / Arb",
        "precision_bits": PRECISION_BITS,
        "protocol_sha256": PROTOCOL_SHA256,
        "layers": results,
        "all_checks_pass": all(row["pass"] for row in results),
        "gaussian_layers_certified": False,
        "evidence_boundary": (
            "Rigorous only for the two exact finite-support witnesses. The frozen "
            "infinite-horizon Gaussian CUSUM and Gaussian SR gains are Monte Carlo "
            "estimates and are not interval-certified by this or any other artifact "
            "in this repository."
        ),
    }
    write_json(CAMPAIGN / "arb" / "certificate.json", payload)
    print(json.dumps({
        "all_checks_pass": payload["all_checks_pass"],
        "layers": [{"layer": r["layer"], "pass": r["pass"]} for r in results],
    }, indent=2))
    if not payload["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
