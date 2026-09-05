"""REPAIR2 defect 2: source-certificate hashes over ACTUAL certified content.

DEFECT (independently adjudicated)
----------------------------------
Repair1's `_dependency_hashes` computes, for each dependency,

    sha256(canonical(_base_identity(dep)))

i.e. a hash of the dependency's identity METADATA only -- detector, cell index,
unit kind, function/m, e0, rho, C_upper, the frozen hashes and precision.
Nothing about what the dependency actually certified enters it. So a dependency
certificate can be swapped for a completely different certificate carrying a
different certified interval, a different error bound, or produced by different
code, and the parent's `source_certificate_hashes` is unchanged.

REPAIR
------
A certificate is hashed over its scientifically load-bearing content:

    certificate = { schema, identity, certified, status }
    certificate_hash = sha256(canonical(certificate))

`identity` is the canonical obligation identity, which itself carries the
Repair2 producer implementation hash and the dependency certificate hashes, so
the binding is recursive: a change anywhere below a node changes that node's
hash. `certified` is the actual certified content for that obligation, taken
from the record that was produced.

WHAT IS BOUND (per obligation kind)

    object h_j / S_r / F_r / dF_r
        the local residual (delta_mid, delta_cell, envelope) and the
        propagated eps node value
    dependency_bundle
        the order-1 h/S residuals and eps, and the finite-power chain at
        orders 0 and 1
    curvature m
        m=5 owns the order-2 chain (h'', S'', H_r, W'') plus the refined
        whole-cell eps; every m also binds its own R2_interval and M_R2
    assembly m
        R_interval, D_interval, R2_interval, M_R2, the complete cover charge
        and its children, the top-level and nested gates, the target gate and
        the obligation status

WHAT IS DELIBERATELY NOT BOUND
    cpu_seconds, bernstein/kernel call counts, peak RSS, threading, timestamps,
    log formatting. The frozen `work.resume_identity` does not make any of them
    identity-bearing, and binding them would make an identical scientific
    certificate hash differently on a busier machine.
"""
from __future__ import annotations

import hashlib
import json

import prior2                                                   # noqa: F401

import spec                                                     # noqa: E402

SCHEMA = "k1.repair2.certificate.v1"

OBJECTS = ([f"h_{j}" for j in range(1, 5)]
           + [f"S_{r}" for r in range(5)]
           + [f"F_{r}" for r in range(5)]
           + [f"dF_{r}" for r in range(5)])

# Runtime fields that must never enter a certificate hash.
EXCLUDED_RUNTIME_FIELDS = ("cpu_seconds", "bernstein_calls", "kernel_calls",
                           "peak_rss_kib", "threading", "cpu_seconds_prepare",
                           "cpu_seconds_including_dependencies")


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


class IncompleteEvidence(RuntimeError):
    """A certificate was requested for an obligation that was never computed."""


def _residual(record: dict, key: str) -> dict:
    if key not in record.get("objects", {}):
        raise IncompleteEvidence(
            f"residual {key!r} is absent from the record: this obligation was "
            "not computed, so no certificate may be issued for it")
    o = record["objects"][key]
    return {k: o[k] for k in ("delta_mid", "delta_cell", "envelope") if k in o}


def _eps(record: dict, bucket: str, key: str):
    return record.get(bucket, {}).get(key)


def _w_indices():
    import cusum_layer1 as L1
    return L1.W_INDICES


def certified_content(unit: tuple, record: dict) -> dict:
    """The scientifically load-bearing content of one obligation."""
    detector, index, kind, tag = unit
    if kind == "far_field":
        raise NotImplementedError("far-field certificates are not implemented")

    if kind == "object":
        if tag.startswith("h_"):
            j = int(tag.split("_")[1])
            return {"residual": _residual(record, f"h_{j}:0"),
                    "eps_mid": _eps(record, "eps_mid", f"h:{j}:0"),
                    "eps_cell": _eps(record, "eps_cell", f"h:{j}:0")}
        if tag.startswith("S_"):
            r = int(tag.split("_")[1])
            return {"residual": _residual(record, f"S_{r}:0"),
                    "eps_mid": _eps(record, "eps_mid", f"S:{r}:0"),
                    "eps_cell": _eps(record, "eps_cell", f"S:{r}:0")}
        if tag.startswith("dF_"):
            r = int(tag.split("_")[1])
            return {"residual": _residual(record, f"dF_{r}"),
                    "eps_mid": _eps(record, "eps_mid", f"D:{r}"),
                    "eps_cell": _eps(record, "eps_cell", f"D:{r}"),
                    "eps_cell_refined": _eps(record, "eps_cell_refined", f"D:{r}")}
        if tag.startswith("F_"):
            r = int(tag.split("_")[1])
            return {"residual": _residual(record, f"F_{r}"),
                    "eps_mid": _eps(record, "eps_mid", f"F:{r}"),
                    "eps_cell": _eps(record, "eps_cell", f"F:{r}"),
                    "eps_cell_refined": _eps(record, "eps_cell_refined", f"F:{r}")}
        raise ValueError(f"unknown object {tag}")

    if kind == "dependency_bundle":
        out = {"h_order1": {}, "S_order1": {}, "finite_powers": {}}
        for j in range(1, 5):
            out["h_order1"][str(j)] = {
                "residual": _residual(record, f"h_{j}:1"),
                "eps_mid": _eps(record, "eps_mid", f"h:{j}:1"),
                "eps_cell": _eps(record, "eps_cell", f"h:{j}:1")}
        for r in range(5):
            out["S_order1"][str(r)] = {
                "residual": _residual(record, f"S_{r}:1"),
                "eps_mid": _eps(record, "eps_mid", f"S:{r}:1"),
                "eps_cell": _eps(record, "eps_cell", f"S:{r}:1")}
        out["Sclosed_order1"] = {
            "residual": _residual(record, "Sclosed_1"),
            "eps_mid": _eps(record, "eps_mid", "Sclosed:1"),
            "eps_cell": _eps(record, "eps_cell", "Sclosed:1")}
        for (r, j) in _w_indices():
            for k in (0, 1):
                out["finite_powers"][f"{r}|{j}|{k}"] = {
                    "residual": _residual(record, f"W_{r}_{j}:{k}"),
                    "eps_mid": _eps(record, "eps_mid", f"W:{r}:{j}:{k}"),
                    "eps_cell": _eps(record, "eps_cell", f"W:{r}:{j}:{k}")}
        return out

    if kind == "curvature":
        m = tag
        led = record["m"].get(m) or record["m"].get(int(m))
        out = {"m": m,
               "R2_interval": led["R2_interval"],
               "M_R2": led["M_R2"]}
        if m == str(spec.CHECKPOINT["work"]["curvature_shared_owner_m"]):
            shared = {"h_order2": {}, "S_order2": {}, "H": {}, "finite_powers": {}}
            for j in range(1, 5):
                shared["h_order2"][str(j)] = {
                    "residual": _residual(record, f"h_{j}:2"),
                    "eps_cell": _eps(record, "eps_cell", f"h:{j}:2")}
            for r in range(5):
                shared["S_order2"][str(r)] = {
                    "residual": _residual(record, f"S_{r}:2"),
                    "eps_cell": _eps(record, "eps_cell", f"S:{r}:2")}
                shared["H"][str(r)] = {
                    "residual": _residual(record, f"H_{r}"),
                    "eps_cell": _eps(record, "eps_cell", f"H:{r}"),
                    "eps_cell_refined": _eps(record, "eps_cell_refined", f"H:{r}")}
            shared["Sclosed_order2"] = {
                "residual": _residual(record, "Sclosed_2"),
                "eps_cell": _eps(record, "eps_cell", "Sclosed:2")}
            for (r, j) in _w_indices():
                shared["finite_powers"][f"{r}|{j}|2"] = {
                    "residual": _residual(record, f"W_{r}_{j}:2"),
                    "eps_cell": _eps(record, "eps_cell", f"W:{r}:{j}:2")}
            out["shared_uniform_cell_jets"] = shared
            out["whole_cell_refinement"] = {
                k: {"refined": v["refined"], "crude": v["crude"],
                    "iterations": v["iterations"], "converged": v["converged"]}
                for k, v in sorted(record["whole_cell_refinement"].items())}
        return out

    if kind == "assembly":
        m = tag
        led = record["m"].get(m) or record["m"].get(int(m))
        return {
            "m": m,
            "R_interval": led["R_interval"],
            "D_interval": led["D_interval"],
            "R2_interval": led["R2_interval"],
            "D_interval_mag": led["D_interval_mag"],
            "R_interval_mag": led["R_interval_mag"],
            "M_R2": led["M_R2"],
            "cover": {"usage": led["cover"]["usage"], "cap": led["cover"]["cap"],
                      "children": led["cover"]["children"],
                      "style": led["cover"]["style"]},
            "top_level_gates": led["top_level_gates"],
            "nested_candidate_gates": led["nested_candidate_gates"],
            "target_gate": led["target_gate"],
            "local_gates": led["local_gates"],
        }
    raise ValueError(f"unknown unit kind {kind}")


def obligation_status(unit: tuple, record: dict) -> str:
    kind, tag = unit[2], unit[3]
    if kind in ("assembly", "curvature"):
        led = record["m"].get(tag) or record["m"].get(int(tag))
        return led["status"]
    return "CERTIFIED"


def build_certificate(unit: tuple, identity: dict, record: dict) -> dict:
    """A complete, hashable certificate for one obligation."""
    return {
        "schema": SCHEMA,
        "identity": identity,
        "certified": certified_content(unit, record),
        "status": obligation_status(unit, record),
    }


def certificate_hash(certificate: dict) -> str:
    """Canonical hash over the certificate's scientific content.

    Order-independent (canonical JSON), and free of runtime noise: a certificate
    re-emitted on a different machine with different CPU seconds hashes the same.
    """
    for field in EXCLUDED_RUNTIME_FIELDS:
        if field in certificate:
            raise ValueError(
                f"{field} is runtime noise and must not be inside a certificate")
    return hashlib.sha256(canonical(certificate)).hexdigest()


def strip_runtime(record: dict) -> dict:
    """A record view with runtime-only fields removed, for hashing."""
    return {k: v for k, v in record.items()
            if k not in EXCLUDED_RUNTIME_FIELDS}
