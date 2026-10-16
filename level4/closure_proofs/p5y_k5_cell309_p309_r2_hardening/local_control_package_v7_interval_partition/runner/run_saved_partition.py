"""Fixed saved-data audit only. No live capture, VM, elevation or admission."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import time
import traceback

ROOT = Path('D:\\ReBaseGuard-309\\records\\p309-i2-root-v3-attempt-20261016-01')
RECORDS = Path('D:\\ReBaseGuard-309\\records\\p309-saved-partition-v7-20261016-01')
DRIVER = Path('D:\\ReBaseGuard-309\\workspace\\p309-local-vm-diagnostic-dev-20261016\\level4\\closure_proofs\\p5y_k5_cell309_p309_r2_hardening\\local_control_package_v7_interval_partition\\driver\\run_verified_partition.py')
AUDIT = Path('D:\\ReBaseGuard-309\\workspace\\p309-local-vm-diagnostic-dev-20261016\\level4\\closure_proofs\\p5y_k5_cell309_p309_r2_hardening\\local_control_package_v7_interval_partition\\adapter\\saved_interval_adapter.py')
ACCOUNT = Path('D:\\ReBaseGuard-309\\workspace\\p309-local-vm-diagnostic-dev-20261016\\level4\\closure_proofs\\p5y_k5_cell309_p309_r2_hardening\\local_control_package_v7_interval_partition\\reference\\account_saved_qpc.py')
CORE = Path('D:\\ReBaseGuard-309\\workspace\\p309-local-vm-diagnostic-dev-20261016\\level4\\closure_proofs\\p5y_k5_cell309_p309_r2_hardening\\local_control_package_v7_interval_partition\\core\\interval_partition.py')
MANIFEST = RECORDS / "INPUT_BINDINGS.json"
MANIFEST_SHA256 = '6f1fcdc9945798ef771973dc25785bb81ac8fba24c9c688f81634e7c08b7abce'
DRIVER_SHA256 = "85e9300a2864f83503035f223d7d264190e44f40eca7e9a25920338629dc80b0"

def write_new(path, data):
    with path.open("xb") as stream:
        stream.write((json.dumps(data, indent=2)+"\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())

def now():
    return datetime.now(timezone.utc).isoformat()

def main():
    if not RECORDS.is_dir() or (RECORDS / "ATTEMPT_STARTED.json").exists():
        raise ValueError("fixed offline attempt directory missing or already used")
    start = now()
    monotonic = time.monotonic()
    write_new(RECORDS / "ATTEMPT_STARTED.json", dict(scope="OFFLINE_SAVED_DATA_ONLY", started_utc=start,
              manifest_sha256=MANIFEST_SHA256, private_decisions_saved=False,
              no_per_slice_copy_saved=True, I1_I7="OPEN", admission="BLOCKED"))
    try:
        data = DRIVER.read_bytes()
        if hashlib.sha256(data).hexdigest() != DRIVER_SHA256:
            raise ValueError("driver source hash differs before same-memory execution")
        ns = {"__file__": str(DRIVER), "__name__": "bound_partition_driver_not_main"}
        exec(compile(data, str(DRIVER), "exec"), ns)
        result = ns["run_verified"](ROOT, MANIFEST, MANIFEST_SHA256, AUDIT, ACCOUNT, CORE, None)
        result["private_decisions_saved"] = False
        result["no_per_slice_copy_saved"] = True
        result["private_decision_count_meaning"] = "DIAGNOSTIC_CANDIDATES_ONLY; NONE_WRITTEN"
        target = RECORDS / "ACTUAL_BOUND_PARTITION_PRIVATE.json"
        write_new(target, result)
        receipt = dict(scope="COMPLETED_BOUND_OFFLINE_PARTITION_AUDIT_ONLY", started_utc=start,
                       finished_utc=now(), elapsed_seconds=time.monotonic()-monotonic,
                       manifest_sha256=MANIFEST_SHA256, driver_sha256=DRIVER_SHA256,
                       same_driver_bytes_verified_compiled_and_executed=True,
                       result_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                       private_decisions_saved=False, no_per_slice_copy_saved=True,
                       actual_host_queries=0, trace_starts=0, vm_starts=0, uac_requests=0,
                       coverage_complete=False, I1_I7="OPEN", admission="BLOCKED")
        write_new(RECORDS / "COMPLETION.json", receipt)
        print(json.dumps(receipt))
    except BaseException as error:
        write_new(RECORDS / "ATTEMPT_FAILED_PRIVATE.json", dict(started_utc=start, failed_utc=now(),
                  error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc(),
                  completed=False, coverage_complete=False, I1_I7="OPEN", admission="BLOCKED"))
        raise

if __name__ == "__main__":
    main()
