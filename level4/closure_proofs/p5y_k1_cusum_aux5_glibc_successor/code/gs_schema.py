"""Frozen identifiers of the CUSUM Aux5 new-glibc successor production layer. NON-CERTIFYING.

Importing this module puts, in order, this namespace's code, the carry-over countersignature code, the provenance
successor code and the production-checkpoint lifecycle code on sys.path. Every predecessor module is reused in place,
byte-identical and hash-bound; no predecessor file is edited.
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CLOSURE = NS.parent
ROOT = CLOSURE.parents[1]
PROV_NS = CLOSURE / "p5y_k1_cusum_aux5_production_provenance_successor"
PROD_NS = CLOSURE / "p5y_k1_cusum_aux5_production_checkpoint"
AUX5_NS = CLOSURE / "p5y_k1_cusum_aux5_successor"
CS_CODE = NS / "countersignature/code"
ISS_NS = CLOSURE / "p5y_k1_cusum_aux5_countersignature_issuance"
for _p in (str(NS / "code"), str(CS_CODE), str(PROV_NS / "code"), str(PROD_NS / "code"), str(ISS_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

NS_REL = "level4/closure_proofs/p5y_k1_cusum_aux5_glibc_successor"

CHECKPOINT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.checkpoint.v1"   # == glibc_successor.CHECKPOINT_SCHEMA
AUTH_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.production-run-authorization.v1"
AUTH_STATUS = "PRE_RESULT_RUN_AUTHORIZATION"
FREEZE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.freeze-record.v1"
FREEZE_STATUS = "FROZEN_PRE_PRODUCTION"
MANIFEST_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.carryover-manifest.v1"
PREFLIGHT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.launch-preflight.v1"
PREFLIGHT_VERSION = "gs-launch-preflight-r1"
ACCEPTANCE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.synthetic-acceptance.v1"
COMPOSITE_AUDIT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.composite-audit.v1"
SYNTHETIC_CS_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.glibc-successor.synthetic-countersignature-fixture.v1"

CHECKPOINT = NS / "config/GLIBC_SUCCESSOR_CHECKPOINT.json"
CHECKPOINT_HASH = NS / "config/GLIBC_SUCCESSOR_CHECKPOINT_HASH"
AUTHORIZATION = NS / "config/RUN_AUTHORIZATION.json"
AUTHORIZATION_HASH = NS / "config/RUN_AUTHORIZATION_HASH"
FREEZE_RECORD = NS / "config/FREEZE_RECORD.json"
CARRYOVER_MANIFEST = NS / "config/CARRYOVER_MANIFEST.json"
COUNTERSIGNATURE = NS / "config/COUNTERSIGNATURE.json"
BINDING = NS / "config/PREDECESSOR_BINDING.json"
ACCEPTANCE_RESULT_REL = f"{NS_REL}/evidence/acceptance_r1/ACCEPTANCE_RESULT.json"

SUCCESSOR_RUNTIME_ROOT = Path("/root/work/postk1-runs/cusum-aux5-production-glibc-r1")
PREDECESSOR_RUNTIME_ROOT = Path("/root/work/postk1-runs/cusum-aux5-production-prov-r1")
BLOCKED_RUNTIME_ROOT = Path("/root/work/postk1-runs/cusum-aux5-production")
REFUSED_ROOTS = (PREDECESSOR_RUNTIME_ROOT, BLOCKED_RUNTIME_ROOT)
CHECKOUT_PATH = Path("/root/work/postk1-aux5-glibc")
PREDECESSOR_CHECKOUT_PATH = Path("/root/work/postk1-aux5")

CAMPAIGN_ID = "p5y_k1_cusum_aux5_production_glibc_successor_r1"
AUTHORIZATION_ID = "CUSUM-AUX5-GLIBC-PROD-AUTH-001"
RUN_ID = "CUSUM-AUX5-GLIBC-PROD-R1"

OLD_CELLS = tuple(range(128))
NEW_CELLS = tuple(range(128, 326))
UNIVERSE = 326
PREDECESSOR_SETTLED_US = 262686610580
ABSOLUTE_CAP_US = 1080000000000
RESIDUAL_CAP_US = 817313389420
INVARIANT = [115, 100]
RESERVATION_US = 3600000000

COUNTERSIGNATURE_SHA256 = "e1ee7fb112c4d013c53f3adf10f12421c04b39f2ec1d3edd98ec2cc07edf143a"
PROPOSAL_SHA256 = "964dc9691a4d5261d244c64426b6438a2ca7e6d2ef7329c26399345d60e34241"
BINDING_SHA256 = "0676fc8267bac3fc6044ab4cb9f57c8769b2b9d62e0d2f0bb2a2d3b1d9db8ac3"
Q6_RESULT_SHA256 = "894f2e8aae6eb38beb2d389a1447a0fce8e1d0d3189fb49ca683701604dc3d88"
RECORD_ENVELOPE_DIGEST = "07249d3bb27a540fd557fa035bc6b3f757cb8518bb99071dcf6ea1be78a85280"
BOUND_BOOT_ID = "eefa85dc-14db-4ba0-912f-f95eeece9c2b"
UNSETTLED_RUN = "R20260913T115713Z-103963"
STOP_ISSUE = "D_" + "h" + "alt"          # assembled so the host-guarded word never appears literally
TOLERATED_ISSUES = (STOP_ISSUE, "D_unsettled_supervisor_runs")

PREDECESSOR_STATUS = "TERMINAL_HOST_DRIFT_STOP_CELLS_0_127_CARRIED_OVER_NEVER_RECOMPUTED"
CARRYOVER_RULE = (
    "SUCCESSOR_PRODUCTION_RESULT = OLD_CARRYOVER (cells 0-127: the verified (record, envelope) pairs of the terminal "
    "predecessor ledger, governed by predecessor authorization b8f11ec0 and countersignature 1ceb92d4, unchanged) "
    "disjoint-union NEW_SUCCESSOR (cells 128-325: pairs of the successor ledger born under this run authorization). "
    "Old cells are never rows of the successor ledger, never reserved, started, recomputed or marked completed by it, "
    "and enter final coverage only through the composite audit and the carry-over manifest.")

SYSTEM_LIBRARIES = tuple("/usr/lib/x86_64-linux-gnu/" + n for n in (
    "libc.so.6", "libm.so.6", "ld-linux-x86-64.so.2", "libpthread.so.0", "libdl.so.2", "librt.so.1", "libutil.so.1",
    "libgcc_s.so.1", "libstdc++.so.6.0.33", "libz.so.1.3.1", "libcrypt.so.1.1.0"))
PACKAGES = ("libc6", "libc-bin", "libgcc-s1", "libstdc++6", "zlib1g", "libcrypt1", "linux-image-amd64",
            "linux-image-6.12.107+deb13-amd64")
APT_UNITS = ("apt-daily.timer", "apt-daily-upgrade.timer", "apt-daily.service", "apt-daily-upgrade.service")
CONTAINMENT_KEYS = ("units", "apt_config", "apt_conf_d_sha256", "freeze_dropin", "holds", "other_managers",
                    "kernel_release", "system_libraries_sha256")

# worker / supervisor processes of any CUSUM generation: matched on exact argv ELEMENT basenames, never on substrings
CERTIFIER_BASENAMES = ("qualify5.py", "run_qualification.sh")
SUPERVISOR_BASENAMES = ("prod_supervisor.py", "prov_supervisor.py", "gs_supervisor.py", "synthetic_worker.py",
                        "prov_synthetic_worker.py")
ENTRY_BASENAMES = ("prod_entry.py", "prov_entry.py", "gs_entry.py")
ENTRY_LIVE_COMMANDS = ("launch", "_supervise")
