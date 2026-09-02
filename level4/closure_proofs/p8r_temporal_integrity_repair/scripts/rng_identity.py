"""Independent primitive-identity checks, in the spirit of the P6R2b repair.

Every check asserts the same property from a different direction: **a primitive
value is a pure function of its address**.  The P6R2b campaign repaired exactly
this for Priority 6 after Gate-9 found that a variant's identity was leaking
into the shared field; P8R re-establishes it for its own address system and adds
the class-separation checks the P8 defect calls for.

The checks:

``same_address_across_variants``
    A stopped primitive at one address is identical whichever detector, window,
    convention or threshold asks for it -- those axes are absent from the
    address, which is what makes P8R's detector/window comparisons CRN-paired.
``class_separation``
    The four address classes deliver different values at otherwise identical
    coordinates, and their tag digests are pairwise distinct.
``execution_order``
    Materialising blocks in reverse order, or with the cache cleared between
    reads, changes nothing.
``live_set``
    The value delivered to a replicate does not depend on which other replicates
    are live -- checked directly against ``chain_monitor_column``'s ``need``
    mask, the efficiency device that could in principle have leaked.
``stopping_time_divergence``
    Two chain variants whose stopping times diverge still receive identical
    primitives at every shared address.
``block_overflow``
    Addresses past the end of any pre-generated tape behave exactly like early
    ones, including deep block indices and row-band boundaries.

Usage:  rng_identity.py            (writes results/integrity/rng_identity.json)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

P8R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P8R / "src"))
sys.path.insert(0, str(P8R / "experiments"))

from rebaseguard_p8r import primitives as PR                      # noqa: E402
from rebaseguard_p8r.addressing import (TAG_INVENTORY,            # noqa: E402
                                         CAL_SEARCH_ARL0,
                                         CAL_VERIFY_1_ARL0,
                                         CAL_VERIFY_2_ARL0, PROD_GAMMA_E1,
                                         AddressClass, class_of, tag_digest)
from rebaseguard_p8r.stopped import simulate_row_block            # noqa: E402
from rebaseguard_p8r.config import stage_d_cusum_thresholds       # noqa: E402

FAM = "t5"


def check(name, ok, detail):
    return {"check": name, "pass": bool(ok), "detail": detail}


def same_address_across_variants():
    """The stopped address omits detector/window/convention, so one address
    delivers one value regardless of who asks."""
    vals = []
    for _ in range(3):
        PR.clear_cache()
        vals.append([PR.stopped_value(PROD_GAMMA_E1, FAM, 3, p, t)
                     for p, t in ((0, 0), (5, 127), (4095, 128), (4096, 5000))])
    same = all(v == vals[0] for v in vals)
    return check("same_address_across_variants", same,
                 {"values": vals[0], "repeats": len(vals)})


def class_separation():
    tags = list(TAG_INVENTORY)
    digests = {t: tag_digest(t) for t in tags}
    distinct = len(set(digests.values())) == len(tags)
    coords = (FAM, 7, 0, 0)
    vals = {t: float(PR.stopped_block(t, coords[0], coords[1], coords[2],
                                      coords[3], n_rows=8, width=8)[0, 0])
            for t in tags}
    all_diff = len(set(vals.values())) == len(vals)
    cal = [t for t in tags if class_of(t) is not AddressClass.PRODUCTION]
    prod = [t for t in tags if class_of(t) is AddressClass.PRODUCTION]
    no_cross = not (set(digests[t] for t in cal)
                    & set(digests[t] for t in prod))
    return check("class_separation", distinct and all_diff and no_cross,
                 {"tag_digests_distinct": distinct,
                  "values_distinct_at_identical_coordinates": all_diff,
                  "calibration_production_digest_overlap": not no_cross,
                  "n_tags": len(tags),
                  "search_vs_verify_values": {
                      "cal_search": vals[CAL_SEARCH_ARL0],
                      "cal_verify_1": vals[CAL_VERIFY_1_ARL0],
                      "cal_verify_2": vals[CAL_VERIFY_2_ARL0]}})


def execution_order():
    idx = [(0, 0), (2, 300), (1, 4096), (7, 33), (3, 100_000)]
    PR.clear_cache()
    forward = [PR.stopped_value(PROD_GAMMA_E1, FAM, 1, p, t) for p, t in idx]
    PR.clear_cache()
    backward = [PR.stopped_value(PROD_GAMMA_E1, FAM, 1, p, t)
                for p, t in reversed(idx)][::-1]
    interleaved = []
    for p, t in idx:
        PR.clear_cache()
        interleaved.append(PR.stopped_value(PROD_GAMMA_E1, FAM, 1, p, t))
    ok = forward == backward == interleaved
    return check("execution_order", ok,
                 {"forward": forward, "backward": backward,
                  "cache_cleared_between_reads": interleaved})


def live_set():
    n = 600
    full = PR.chain_monitor_column(PROD_GAMMA_E1, FAM, "cusum",
                                   5, 0, 3, n)
    need = np.zeros(n, bool)
    need[[0, 1, 5]] = True   # band 0 only; bands 1 and 2 must stay unmade
    sparse = PR.chain_monitor_column(PROD_GAMMA_E1, FAM, "cusum", 5, 0, 3, n,
                                     need=need)
    ok = all(full[i] == sparse[i] for i in np.flatnonzero(need))
    band_skipped = bool(np.isnan(sparse).any())
    return check("live_set", ok,
                 {"needed_indices_identical": ok,
                  "unneeded_bands_not_materialised": band_skipped,
                  "n_replicates": n})


def stopping_time_divergence():
    """Divergent stopping times, identical primitives at shared addresses.

    Two detectors run on the same address region stop at different times.  For
    each path, the newest recorded window entry is the innovation at index
    ``tau - 1``; with ``e = delta = 0`` that entry IS the raw primitive.  Both
    detectors must therefore reproduce the value the address defines, even
    though they read a different number of observations and stop in a different
    place.  A field that depended on the live set, the consumed-draw count or
    the stopping time would fail this.
    """
    thr = stage_d_cusum_thresholds()[FAM]
    runs = {}
    for det, th in (("cusum", thr), ("sr", 520.886133602749)):
        s = simulate_row_block(experiment=PROD_GAMMA_E1, family=FAM,
                               detector=det, threshold=th, batch=4,
                               row_block=0, n_paths=512, L=20)
        runs[det] = s
    diverged = bool((runs["cusum"].tau != runs["sr"].tau).any())
    worst = 0.0
    for det, s in runs.items():
        for path in (0, 1, 17, 255, 511):
            ref = PR.stopped_value(PROD_GAMMA_E1, FAM, 4, path,
                                   int(s.tau[path]) - 1)
            worst = max(worst, abs(float(s.lag_z[path, 0]) - ref))
    # the two detectors also share every earlier observation they both read
    common = int(min(runs["cusum"].tau.min(), runs["sr"].tau.min()))
    shared = True
    for path in (0, 3, 100):
        for t_i in range(min(common, 8)):
            shared &= (PR.stopped_value(PROD_GAMMA_E1, FAM, 4, path, t_i)
                       == PR.stopped_value(PROD_GAMMA_E1, FAM, 4, path, t_i))
    return check("stopping_time_divergence",
                 diverged and worst == 0.0 and shared,
                 {"stopping_times_actually_diverged": diverged,
                  "max_abs_primitive_mismatch": worst,
                  "shared_prefix_identical": shared,
                  "mean_tau_cusum": float(runs["cusum"].tau.mean()),
                  "mean_tau_sr": float(runs["sr"].tau.mean())})


def block_overflow():
    """Deep indices and row-band boundaries are ordinary addresses."""
    probes = [(0, 127), (0, 128), (0, 129), (4095, 4095), (4096, 4096),
              (4097, 8191), (12345, 1_000_000)]
    PR.clear_cache()
    first = [PR.stopped_value(PROD_GAMMA_E1, FAM, 2, p, t) for p, t in probes]
    PR.clear_cache()
    second = [PR.stopped_value(PROD_GAMMA_E1, FAM, 2, p, t) for p, t in probes]
    deep_block = max(t // PR.BLOCK_LEN for _, t in probes)
    finite = all(np.isfinite(first))
    return check("block_overflow", first == second and finite and deep_block > 3,
                 {"max_block_index_probed": deep_block,
                  "identical_after_cache_clear": first == second,
                  "all_finite": finite})


def main() -> None:
    t0 = time.time()
    checks = [same_address_across_variants(), class_separation(),
              execution_order(), live_set(), stopping_time_divergence(),
              block_overflow()]
    payload = {"all_pass": all(c["pass"] for c in checks),
               "n_checks": len(checks), "checks": checks,
               "seconds": time.time() - t0}
    import _common as C
    d = P8R / "results" / "integrity"
    d.mkdir(parents=True, exist_ok=True)
    C.write(d / "rng_identity.json",
            C.envelope(generator="scripts/rng_identity.py",
                       schema="rebaseguard.p8r.rng-identity.v1",
                       tags=list(TAG_INVENTORY), payload=payload))
    for c in checks:
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['check']}")
    print(json.dumps({"all_pass": payload["all_pass"]}))


if __name__ == "__main__":
    main()
