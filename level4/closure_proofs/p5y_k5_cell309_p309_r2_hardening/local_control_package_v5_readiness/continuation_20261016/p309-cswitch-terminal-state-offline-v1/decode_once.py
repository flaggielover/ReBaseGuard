"""One saved-file decode only; fixed ETL, output and input/code pins."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).absolute().parent
ETL = Path(r"D:\ReBaseGuard-309\records\p309-i2-root-v3-attempt-20261016-01\capture\capture.etl")
ETL_HASH = "3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870"
REFERENCE = Path(r"D:\ReBaseGuard-309\records\p309-i2-renewed-attempt-v3\offline\REFERENCE_KernelTraceEventParser.cs")
REFERENCE_HASH = "2245ccc62b0d933190068a18344bc64749a2893bd9740a79706ba7fe5e86c778"
PIN_SOURCE = HERE.parent / "p309-offline-input-integrity-staging-v1" / "run_verified_audit.py"
PIN_HASH = "9eb9e1fe69e8b6d148c71714c907d0bccc5198c715ee850681064cdc2fd221b6"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_new(name, data):
    with (HERE / name).open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--exe-sha256", required=True)
    args = parser.parse_args()
    pin_bytes = PIN_SOURCE.read_bytes()
    if hashlib.sha256(pin_bytes).hexdigest() != PIN_HASH:
        raise ValueError("file pin helper binding differs")
    helper = types.ModuleType("fixed_file_pins")
    helper.__file__ = str(PIN_SOURCE)
    exec(compile(pin_bytes, str(PIN_SOURCE), "exec"), helper.__dict__)
    source, executable = HERE / "SavedThreadTerminal.cpp", HERE / "SavedThreadTerminal.exe"
    output = HERE / "PRIVATE_THREAD_TERMINAL.csv"
    pins = [ETL, REFERENCE, PIN_SOURCE, source, executable, Path(__file__).absolute(), HERE / "Build-And-Decode-Saved.ps1"]
    with helper.PinnedInputs(pins):
        bound = {ETL: ETL_HASH, REFERENCE: REFERENCE_HASH, PIN_SOURCE: PIN_HASH,
                 source: args.source_sha256, executable: args.exe_sha256}
        for path, expected in bound.items():
            if digest(path) != expected:
                raise ValueError("fixed saved-input/source/executable binding differs: " + str(path))
        if output.exists():
            raise ValueError("fresh private numeric output required")
        command = [str(executable), str(ETL), str(output)]
        start = datetime.now(timezone.utc).isoformat()
        # Once-only marker is consumed before the ProcessTrace executable starts.
        write_new("DECODE_STARTED.json", json.dumps(dict(start_utc=start, command=command,
                    input_sha256=ETL_HASH, source_sha256=args.source_sha256,
                    exe_sha256=args.exe_sha256, automatic_retry=False)).encode())
        env = {"SystemRoot": r"C:\Windows", "WINDIR": r"C:\Windows", "PATH": r"C:\Windows\System32",
               "TEMP": str(HERE), "TMP": str(HERE)}
        process = subprocess.run(command, cwd=HERE, env=env, capture_output=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW, timeout=110)
        end = datetime.now(timezone.utc).isoformat()
        write_new("decoder.stdout.json", process.stdout)
        write_new("decoder.stderr.txt", process.stderr)
        summary = json.loads(process.stdout)
        usable = (process.returncode == 0 and summary["events"] == 4249919
                  and summary["cswitch_rows"] == 3829610 and summary["thread_rows"] == 21694
                  and all(summary[key] == 0 for key in ("unknown_cswitch_prefix", "unknown_thread_prefix",
                        "header_events_lost", "header_buffers_lost", "process_rc", "close_rc", "output_error", "output_write_failures")))
        with helper.PinnedInputs([output]):
            output_hash = digest(output)
            output_size = output.stat().st_size
        result = dict(scope="FRESH_SAVED_ETL_THREAD_TERMINAL_PREFIX_DERIVATION_ONLY",
                      start_utc=start, end_utc=end, input_sha256=ETL_HASH,
                      reference_sha256=REFERENCE_HASH, source_sha256=args.source_sha256,
                      exe_sha256=args.exe_sha256, pin_helper_sha256=PIN_HASH,
                      wrapper_sha256=digest(Path(__file__).absolute()),
                      command=command, clean_environment=env, exit_code=process.returncode,
                      private_csv_sha256=output_hash, private_csv_bytes=output_size,
                      decoder_summary_sha256=hashlib.sha256(process.stdout).hexdigest(),
                      summaries_and_counts_usable=usable, source_exe_input_ancestor_pins_held=True,
                      trace_starts=0, uac=0, vm=0, host_queries=0, ownership_extended=False,
                      original_audit_execution_binding_proven=False, admission="BLOCKED")
        write_new("DERIVATION_RESULT.json", json.dumps(result, indent=2).encode())
        print(json.dumps(result))
        if not usable:
            raise ValueError("saved-file decoder did not meet bounded prefix/count criteria; no retry")


if __name__ == "__main__":
    main()
