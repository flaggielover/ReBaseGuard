"""Mechanically recover the authoritative Priority-1 and Priority-2 gains.

Nothing here retypes a number from a report or a figure.  Every GammaTilde
value is read out of the closed campaigns' own JSON result artifacts, and every
source file is hash-gated against the frozen Priority-3 manifest first.

The two finite-support witnesses are additionally recomputed *exactly* in
rational arithmetic straight from the frozen witness files, and the recomputed
values for the window lengths that Priority 1 and Priority 2 already certified
are replayed against those packages' recorded exact strings.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from .classifier import boundary_as_dict, boundary, normal_interval
from .common import dig, read_json, sha256, write_json
from .config import CAMPAIGN, LAYERS, M_GRID, PROTOCOL, PROTOCOL_SHA256, RESULTS, ROOT


def _manifest() -> dict[str, Any]:
    return read_json(CAMPAIGN / "manifest.json")


def verify_upstream_hashes() -> dict[str, Any]:
    """Confirm every consumed Priority-1/Priority-2 artifact is unchanged."""
    manifest = _manifest()
    rows = []
    for relative, expected in sorted(manifest["upstream_sources"].items()):
        observed = sha256(ROOT / relative)
        rows.append({
            "path": relative,
            "expected_sha256": expected,
            "observed_sha256": observed,
            "match": observed == expected,
        })
    return {"sources": rows, "all_match": all(row["match"] for row in rows)}


def _witness_paths(witness: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in witness["paths"]:
        increments = [Fraction(*item) for item in row["increments"]]
        rows.append({
            "label": row["label"],
            "p": Fraction(*row["probability"]),
            "tau": int(row["tau"]),
            "z": increments,
            "T": sum(increments, Fraction(0)),
        })
    return rows


def exact_witness_gamma(witness: dict[str, Any], m: int) -> Fraction:
    """GammaTilde_m = E_0[A_m T_tau] in exact rational arithmetic.

    ``A_m`` keeps the authoritative random denominator ``w_m = min(m, tau)`` and
    includes the terminal alarm-causing increment, exactly as the frozen
    Stage-D window convention requires.
    """
    total = Fraction(0)
    for row in _witness_paths(witness):
        window = min(m, row["tau"])
        window_sum = sum(row["z"][row["tau"] - window:], Fraction(0))
        a_m = window_sum / window
        total += row["p"] * a_m * row["T"]
    return total


def witness_layer_rows(layer: dict[str, Any]) -> list[dict[str, Any]]:
    witness = read_json(ROOT / layer["gamma_source"])
    certificate = read_json(ROOT / layer["gamma_replay_source"])
    recorded = {int(row["m"]): row["exact"]["gamma"] for row in certificate["records"]}
    replay_grid = PROTOCOL["witness_m_replay"]["certified_in_priority_packages"]
    new_grid = PROTOCOL["witness_m_replay"]["new_priority3_certified"]

    rows = []
    for m in M_GRID:
        value = exact_witness_gamma(witness, m)
        replayed = m in replay_grid
        expected = recorded.get(m)
        if replayed:
            if expected is None or Fraction(expected) != value:
                raise RuntimeError(
                    f"witness replay mismatch for {layer['id']} m={m}: "
                    f"recomputed {value}, package recorded {expected}"
                )
        rows.append({
            "m": m,
            "gamma_tilde": float(value),
            "gamma_tilde_exact": str(value),
            "gamma_tilde_se": None,
            "gamma_tilde_ci95": None,
            "gamma_evidence_class": layer["gamma_evidence_class"],
            "cell_evidence_class": layer["cell_evidence_class"],
            "provenance_kind": "REPLAYED_FROM_CLOSED_PACKAGE" if replayed
                               else "P3_NEW_EXACT_FROM_FROZEN_WITNESS",
            "replayed_against_closed_certificate": replayed,
            "closed_certificate_value": expected,
            "source": layer["gamma_source"],
        })
    return rows


def gaussian_layer_rows(layer: dict[str, Any]) -> list[dict[str, Any]]:
    payload = read_json(ROOT / layer["gamma_source"])
    upstream_m = [int(x) for x in payload["protocol"]["m_grid"]]
    if upstream_m != M_GRID:
        raise RuntimeError(
            f"{layer['id']} upstream m grid {upstream_m} differs from the "
            f"Priority-3 grid {M_GRID}; no m value may be synthesised"
        )
    gammas = [float(x) for x in dig(payload, layer["gamma_pointer"])]
    ses = [abs(float(x)) for x in dig(payload, layer["gamma_se_pointer"])]
    rows = []
    for m, gamma, se in zip(upstream_m, gammas, ses, strict=True):
        lo, hi = normal_interval(gamma, se)
        rows.append({
            "m": m,
            "gamma_tilde": gamma,
            "gamma_tilde_exact": None,
            "gamma_tilde_se": se,
            "gamma_tilde_ci95": [lo, hi],
            "gamma_evidence_class": layer["gamma_evidence_class"],
            "cell_evidence_class": layer["cell_evidence_class"],
            "provenance_kind": "READ_FROM_CLOSED_PACKAGE_RESULT_JSON",
            "replayed_against_closed_certificate": False,
            "closed_certificate_value": None,
            "source": layer["gamma_source"],
            "source_evidence_class": payload["evidence_class"],
            "source_protocol_sha256": payload["protocol_sha256"],
        })
    return rows


def build() -> dict[str, Any]:
    hashes = verify_upstream_hashes()
    if not hashes["all_match"]:
        raise RuntimeError("a consumed Priority-1/Priority-2 artifact changed")

    layers = []
    for layer in LAYERS:
        if "gamma_replay_source" in layer:
            rows = witness_layer_rows(layer)
        else:
            rows = gaussian_layer_rows(layer)
        for row in rows:
            interval = row["gamma_tilde_ci95"]
            row["boundary"] = boundary_as_dict(boundary(
                row["gamma_tilde"],
                row["gamma_tilde_se"],
                tuple(interval) if interval else None,
            ))
        layers.append({
            "id": layer["id"],
            "detector_family": layer["detector_family"],
            "detector_short": layer["detector_short"],
            "source_priority": layer["source_priority"],
            "gamma_evidence_class": layer["gamma_evidence_class"],
            "cell_evidence_class": layer["cell_evidence_class"],
            "uncertainty_model": layer["uncertainty_model"],
            "rows": rows,
        })

    payload = {
        "schema": "rebaseguard.p3-provenance.v1",
        "campaign": PROTOCOL["campaign"],
        "protocol_sha256": PROTOCOL_SHA256,
        "upstream_hashes": hashes,
        "imported_theorems": PROTOCOL["imported_theorems"],
        "m_grid": M_GRID,
        "layers": layers,
        "gamma_interpolated_across_m": False,
        "evidence_boundary": PROTOCOL["evidence_boundary"],
        "valid": True,
    }
    write_json(RESULTS / "provenance.json", payload)
    return payload
