"""Same-campaign RNG address separation audit.

Why this module exists
----------------------
P8R (`p8r_temporal_integrity_repair/src/rebaseguard_p8r/addressing.py`) made
calibration/production address reuse impossible *by construction*, for campaigns
that opt into its tag discipline.  That is a **preventive** layer and it only
protects a campaign that was written against it.

The P4Z/P4ZA/P4ZB line predates that discipline and draws directly on the frozen
`p4_theory_generalization` addressing, so P8R's constructive guarantee does not
reach it.  What no campaign in the line carried is a **detective** layer: a check
that, given the streams a campaign actually consumed, proves that its
non-result-bearing calibration/study programs and its result-bearing production
routes never touched the same RNG address.

Every `independent_closure_audit.py` in the P4Z line checks seed disjointness
only against *predecessor* campaigns and *history*, by comparing raw seed
integers.  That check is blind to two things this module is not:

1. it never compares a campaign against **its own** calibration; and
2. it compares bare integers, so it neither notices that the same integer keys
   two different bit generators (not a shared stream) nor that two programs
   sharing one key overlap only on part of the batch axis (a shared stream on
   exactly that part).

This module therefore complements P8R rather than competing with it: P8R
prevents, this audits, and both speak the same `AddressClass` vocabulary.

Address semantics
-----------------
The addressing is the frozen one in
`p4_theory_generalization/src/rebaseguard_p4_general/simulate.py`:

``PHILOX``
    ``np.random.Philox(key=seed, counter=stream_counter(batch, step))`` with
    ``stream_counter(batch, step) = ((batch << 32) | step) * 2**64``.  The stride
    reserves ``2**64`` counter values per ``(batch, step)``, so distinct
    ``(batch, step)`` pairs never overlap and two programs collide **iff** they
    share ``(key, batch)`` — at which point they share the whole step-indexed
    family of streams for every step they both reach.  Collapsing the step axis
    is therefore exact, not an approximation, and is conservative in the sense
    that it can only be reached by programs that genuinely share step 1.

``PCG64``
    ``np.random.Generator(np.random.PCG64([seed, batch]))``, consumed
    sequentially.  The address is literally ``(key, batch)``; there is no step
    axis to collapse.

Two `StreamBlock`s overlap iff they name the same generator, the same key, and
intersecting batch indices.  Sharing a key without sharing an address is not a
collision, and the two ways that happens are reported separately because they
mean different things:

``SEED_NAMESPACE_REUSE``
    one integer keying two *different* bit generators.  No innovation is
    shared, but the seed bookkeeping every campaign audit relies on can no
    longer tell the two roles apart, which is what makes a later same-generator
    reuse easy to introduce unnoticed.

``KEY_PARTITION``
    the same generator and key, split across disjoint batch regions.  This is
    legitimate — it is how P8R separates purposes inside one address class — and
    is reported only so that the partition is on the record rather than
    incidental.

Neither fails the audit.  Only ``ADDRESS_OVERLAP`` does.

The draw length is deliberately **not** part of the overlap test.  Both
generators deliver a prefix of one stream, so a program drawing ``n`` paths and a
program drawing ``n' < n`` paths from the same address share ``n'`` innovations
exactly.  A shorter draw is not a weaker collision.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence


class AddressClass(str, Enum):
    """Roles a program plays in a campaign.

    Deliberately compatible with P8R's four classes: ``CALIBRATION`` covers
    P8R's ``CAL_SEARCH``/``CAL_VERIFY_*`` (anything consulted while a design
    parameter is still being chosen), and ``PRODUCTION`` is P8R's ``PRODUCTION``.
    """

    CALIBRATION = "calibration"
    PRODUCTION = "production"


#: generator families this audit understands, with the address tuple each uses.
GENERATORS = {
    "PHILOX": ("key", "batch"),   # step axis collapsed exactly, see module docstring
    "PCG64": ("key", "batch"),
}


class AddressAuditError(ValueError):
    """A manifest could not be interpreted as an address declaration."""


@dataclass(frozen=True)
class StreamBlock:
    """One contiguous family of RNG addresses consumed by one program.

    ``batch_lo``/``batch_hi`` are inclusive.  ``label`` names the program,
    ``configuration`` and ``route`` name what the stream was spent on.
    """

    generator: str
    key: int
    batch_lo: int
    batch_hi: int
    cls: AddressClass
    label: str
    configuration: str = ""
    route: str = ""
    result_bearing: bool = False

    def __post_init__(self) -> None:
        if self.generator not in GENERATORS:
            raise AddressAuditError(
                f"unknown generator {self.generator!r}; "
                f"known: {sorted(GENERATORS)}")
        if self.batch_hi < self.batch_lo:
            raise AddressAuditError(
                f"empty batch range [{self.batch_lo}, {self.batch_hi}] "
                f"for {self.label!r}")
        if not isinstance(self.cls, AddressClass):
            raise AddressAuditError("cls must be an AddressClass")

    @property
    def batches(self) -> range:
        return range(self.batch_lo, self.batch_hi + 1)

    def batch_overlap(self, other: "StreamBlock") -> range:
        lo = max(self.batch_lo, other.batch_lo)
        hi = min(self.batch_hi, other.batch_hi)
        return range(lo, hi + 1) if hi >= lo else range(0)

    def shares_address_with(self, other: "StreamBlock") -> bool:
        """True iff the two blocks name at least one identical RNG address."""
        return (self.generator == other.generator
                and self.key == other.key
                and len(self.batch_overlap(other)) > 0)

    def describe(self) -> str:
        return (f"{self.generator}(key={self.key}, "
                f"batch={self.batch_lo}..{self.batch_hi})")


@dataclass
class Finding:
    #: "ADDRESS_OVERLAP" (fails) | "SEED_NAMESPACE_REUSE" | "KEY_PARTITION"
    severity: str
    calibration: StreamBlock
    production: StreamBlock
    overlapping_batches: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = {
            "severity": self.severity,
            "calibration_program": self.calibration.label,
            "calibration_address": self.calibration.describe(),
            "calibration_configuration": self.calibration.configuration,
            "production_program": self.production.label,
            "production_address": self.production.describe(),
            "production_configuration": self.production.configuration,
            "production_route": self.production.route,
            "key": self.calibration.key,
        }
        if self.severity == "ADDRESS_OVERLAP":
            d["overlapping_batches"] = self.overlapping_batches
            d["overlapping_address_count"] = len(self.overlapping_batches)
            d["generator"] = self.calibration.generator
        elif self.severity == "KEY_PARTITION":
            d["generator"] = self.calibration.generator
            d["calibration_batches"] = [self.calibration.batch_lo,
                                        self.calibration.batch_hi]
            d["production_batches"] = [self.production.batch_lo,
                                       self.production.batch_hi]
        else:
            d["calibration_generator"] = self.calibration.generator
            d["production_generator"] = self.production.generator
        return d


def audit_streams(blocks: Sequence[StreamBlock]) -> dict:
    """Audit one campaign's declared streams for same-campaign address reuse.

    Returns a report dict with ``verdict`` in
    ``{"RNG_ADDRESS_SEPARATION_PASS", "RNG_ADDRESS_SEPARATION_FAIL"}``.

    Only ``ADDRESS_OVERLAP`` fails the audit.  ``SEED_NAMESPACE_REUSE`` and
    ``KEY_PARTITION`` share no innovation and are reported so that a key serving
    two roles is on the record rather than incidental.
    """
    cal = [b for b in blocks if b.cls is AddressClass.CALIBRATION]
    prod = [b for b in blocks if b.cls is AddressClass.PRODUCTION]

    overlaps: list[Finding] = []
    namespace: list[Finding] = []
    partitions: list[Finding] = []
    for c in cal:
        for p in prod:
            if c.shares_address_with(p):
                overlaps.append(Finding("ADDRESS_OVERLAP", c, p,
                                        list(c.batch_overlap(p))))
            elif c.key == p.key:
                if c.generator == p.generator:
                    partitions.append(Finding("KEY_PARTITION", c, p))
                else:
                    namespace.append(Finding("SEED_NAMESPACE_REUSE", c, p))

    return {
        "schema": "rebaseguard.same-campaign-rng-address-audit.v1",
        "address_model": {
            "PHILOX": "np.random.Philox(key=seed, counter=((batch<<32)|step)*2**64); "
                      "the 2**64 stride makes (key, batch) the exact collision granularity",
            "PCG64": "np.random.Generator(np.random.PCG64([seed, batch])); "
                     "address is (key, batch)",
            "draw_length_is_not_part_of_the_test":
                "both generators deliver a prefix of one stream, so a shorter "
                "draw shares its innovations exactly with a longer one",
        },
        "calibration_blocks": len(cal),
        "production_blocks": len(prod),
        "address_overlaps": [f.to_dict() for f in overlaps],
        "seed_namespace_reuse": [f.to_dict() for f in namespace],
        "key_partitions": [f.to_dict() for f in partitions],
        "overlapping_address_total": sum(len(f.overlapping_batches)
                                         for f in overlaps),
        "verdict": ("RNG_ADDRESS_SEPARATION_FAIL" if overlaps
                    else "RNG_ADDRESS_SEPARATION_PASS"),
    }


# --------------------------------------------------------------------------
# manifest form
# --------------------------------------------------------------------------

def blocks_from_manifest(manifest: dict) -> list[StreamBlock]:
    """Build `StreamBlock`s from a campaign RNG manifest.

    Manifest shape::

        {"campaign": "...",
         "programs": [
           {"label": "...", "class": "calibration"|"production",
            "result_bearing": bool,
            "streams": [{"generator": "PHILOX"|"PCG64", "key": int,
                         "batch_lo": int, "batch_hi": int,
                         "configuration": str, "route": str}, ...]}, ...]}
    """
    if "programs" not in manifest:
        raise AddressAuditError("manifest has no 'programs'")
    out: list[StreamBlock] = []
    for prog in manifest["programs"]:
        try:
            cls = AddressClass(prog["class"])
        except (KeyError, ValueError) as exc:
            raise AddressAuditError(
                f"program {prog.get('label')!r} has no valid class") from exc
        rb = bool(prog.get("result_bearing", cls is AddressClass.PRODUCTION))
        if cls is AddressClass.CALIBRATION and rb:
            raise AddressAuditError(
                f"program {prog['label']!r} is declared calibration and "
                f"result_bearing; a calibration stream may not carry a result")
        for s in prog.get("streams", ()):
            out.append(StreamBlock(
                generator=s["generator"], key=int(s["key"]),
                batch_lo=int(s["batch_lo"]), batch_hi=int(s["batch_hi"]),
                cls=cls, label=prog["label"],
                configuration=s.get("configuration", ""),
                route=s.get("route", ""), result_bearing=rb))
    return out


def audit_manifest(manifest: dict) -> dict:
    report = audit_streams(blocks_from_manifest(manifest))
    report["campaign"] = manifest.get("campaign", "")
    return report


def audit_manifest_file(path: str | Path) -> dict:
    return audit_manifest(json.loads(Path(path).read_text()))


# --------------------------------------------------------------------------
# the check the P4Z-line audits actually performed, kept for contrast
# --------------------------------------------------------------------------

def predecessor_seed_check(campaign_seeds: Iterable[int],
                           predecessor_seeds: Iterable[int]) -> bool:
    """The pre-existing check: raw seed integers vs *other* campaigns.

    Reproduced verbatim in behaviour so that
    `tests/test_rng_address_audit.py` can show, rather than assert, that it
    cannot substitute for `audit_streams`: it returns True (disjoint) for a
    campaign whose own calibration collides with its own production.
    """
    return not (set(campaign_seeds) & set(predecessor_seeds))


def main(argv: Sequence[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="same-campaign RNG address separation audit")
    ap.add_argument("manifest", help="campaign RNG manifest JSON")
    ap.add_argument("--out", default=None, help="write the report here")
    args = ap.parse_args(argv)
    report = audit_manifest_file(args.manifest)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(text)
    return 0 if report["verdict"] == "RNG_ADDRESS_SEPARATION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
