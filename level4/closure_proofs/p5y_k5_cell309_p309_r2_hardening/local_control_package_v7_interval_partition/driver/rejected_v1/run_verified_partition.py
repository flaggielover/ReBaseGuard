"""Bind saved numeric input, summaries and audit sources before offline audit.

Windows-only: no tracing, VM, policy, elevation or admission API. Input handles
deny ordinary Win32 write/delete sharing and ancestor handles pin path reopen.
This new check cannot retroactively bind an earlier decoder's output bytes.
"""
import argparse
import csv
import ctypes
from ctypes import wintypes
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import types

SCHEMA = ["kind", "qpc", "cpu", "opcode", "a", "b", "c", "cpu_index_flag"]
BINDING_SCOPE = "POSTHOC_SAVED_INPUT_CHECK_ONLY"
HEX = re.compile(r"[0-9a-f]{64}\Z")
INTEGER = re.compile(r"-?[0-9]{1,20}\Z")
MAX_SMALL_FILE = 4 * 1024 * 1024


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def parse_json(data):
    result = json.loads(data.decode("utf-8-sig"), object_pairs_hook=no_duplicate_keys,
                        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    if not isinstance(result, dict):
        raise ValueError("JSON object required")
    return result


def natural(value, name, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise ValueError("invalid nonnegative integer: " + name)
    return value


def absolute(path):
    value = Path(os.path.abspath(path))
    # Reject device/UNC/ADS paths; only ordinary drive-qualified saved files.
    if len(value.drive) != 2 or value.drive[1] != ":" or any(":" in p for p in value.parts[1:]):
        raise ValueError("ordinary drive-qualified path required")
    return value


class PinnedInputs:
    """Keep every input and ancestor open without WRITE/DELETE sharing.

    This pins ordinary data-write/delete sharing, not every metadata attribute
    change or an administrator/kernel adversary. All opened objects reject
    reparse points. The audit reads the bound leaf handle rather than reopening
    by path, so metadata-write denial is not a prerequisite for its two passes.
    """
    def __init__(self, files):
        if sys.platform != "win32":
            raise RuntimeError("Windows input pinning unavailable; refusing")
        self.files = [absolute(path) for path in files]
        self.handles = []
        self.identities = []
        self.api = ctypes.WinDLL("kernel32.dll", use_last_error=True)
        self.api.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                       wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.api.CreateFileW.restype = wintypes.HANDLE
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL

        class Info(ctypes.Structure):
            _fields_ = [("attributes", wintypes.DWORD), ("creation", wintypes.FILETIME),
                        ("access", wintypes.FILETIME), ("write", wintypes.FILETIME),
                        ("volume", wintypes.DWORD), ("size_high", wintypes.DWORD),
                        ("size_low", wintypes.DWORD), ("links", wintypes.DWORD),
                        ("index_high", wintypes.DWORD), ("index_low", wintypes.DWORD)]
        self.info_type = Info
        self.api.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(Info)]
        self.api.GetFileInformationByHandle.restype = wintypes.BOOL

    def __enter__(self):
        directories = {parent for path in self.files for parent in path.parents}
        ordered = [(p, True) for p in sorted(directories, key=lambda p: (len(p.parts), str(p).lower()))]
        ordered.extend((p, False) for p in sorted(set(self.files), key=lambda p: str(p).lower()))
        try:
            for path, directory in ordered:
                # GENERIC_READ participates in sharing checks. Access zero did
                # not deny writes in actual synthetic-file tests and cannot
                # establish stable input for the audit's path-based reopens.
                handle = self.api.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x02200000, None)
                if handle == ctypes.c_void_p(-1).value:
                    raise ctypes.WinError(ctypes.get_last_error())
                self.handles.append(handle)
                info = self.info_type()
                if not self.api.GetFileInformationByHandle(handle, ctypes.byref(info)):
                    raise ctypes.WinError(ctypes.get_last_error())
                if info.attributes & 0x400:
                    raise ValueError("reparse input/ancestor rejected: " + str(path))
                if bool(info.attributes & 0x10) != directory:
                    raise ValueError("input object type differs")
                self.identities.append({"path": str(path), "directory": directory,
                                        "volume_serial": info.volume,
                                        "file_index": (info.index_high << 32) | info.index_low})
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def verify_stream_identity(self, stream, path):
        import msvcrt
        info = self.info_type()
        if not self.api.GetFileInformationByHandle(msvcrt.get_osfhandle(stream.fileno()), ctypes.byref(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        wanted = [entry for entry in self.identities if entry["path"] == str(path) and not entry["directory"]]
        actual = info.volume, (info.index_high << 32) | info.index_low
        if len(wanted) != 1 or actual != (wanted[0]["volume_serial"], wanted[0]["file_index"]) or info.attributes & 0x410:
            raise ValueError("reopened file does not match pinned ordinary-file identity")

    def small_bytes(self, path):
        with path.open("rb") as stream:
            self.verify_stream_identity(stream, path)
            data = stream.read(MAX_SMALL_FILE + 1)
        if len(data) > MAX_SMALL_FILE:
            raise ValueError("bounded small input exceeded")
        return data

    def __exit__(self, *unused):
        errors = []
        while self.handles:
            if not self.api.CloseHandle(self.handles.pop()):
                errors.append(ctypes.get_last_error())
        if errors:
            raise OSError("input pin close failed: " + repr(errors))


def scan_numeric(path, expected_rows):
    counts = {kind: 0 for kind in range(1, 6)}
    with path.open("r", encoding="ascii", newline="") as stream:
        # Limit single rows as well as the total expected count; malformed saved
        # input is rejected before handing it to the historical audit parser.
        lines = iter(lambda: stream.readline(513), "")
        first = next(lines, "")
        if len(first) > 512 or next(csv.reader([first]), None) != SCHEMA:
            raise ValueError("unexpected numeric CSV header")
        count = 0
        for line in lines:
            if len(line) > 512:
                raise ValueError("oversized numeric CSV row")
            cells = next(csv.reader([line]))
            if len(cells) != 8 or any(INTEGER.fullmatch(cell) is None for cell in cells):
                raise ValueError("malformed numeric CSV row")
            values = tuple(map(int, cells))
            if any(not -(1 << 63) <= value < (1 << 64) for value in values):
                raise ValueError("numeric CSV integer out of range")
            if values[0] not in counts:
                raise ValueError("unknown numeric CSV kind")
            counts[values[0]] += 1
            count += 1
            if count > expected_rows:
                raise ValueError("more numeric rows than explicitly bound")
    if count != expected_rows:
        raise ValueError("numeric row count differs")
    return count, counts


def load_bound_audit(audit_path, account_path, core_path, audit_bytes, account_bytes, core_bytes):
    """Compile exact snapshots; never resolve the two local imports by path."""
    previous = {name: sys.modules.get(name) for name in ("account_saved_qpc", "interval_partition")}
    try:
        for name, path, data in (("account_saved_qpc", account_path, account_bytes),
                                 ("interval_partition", core_path, core_bytes)):
            module = types.ModuleType(name)
            module.__file__ = str(path)
            exec(compile(data, str(path), "exec"), module.__dict__)
            sys.modules[name] = module
        namespace = {"__name__": "bound_partition_audit_not_main", "__file__": str(audit_path)}
        exec(compile(audit_bytes, str(audit_path), "exec"), namespace)
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
    return namespace["audit"]


class HashingRead(io.RawIOBase):
    """Hash exact bytes of each audit pass without owning the bound file."""
    def __init__(self, stream):
        self.stream = stream
        self.digest = hashlib.sha256()

    def readable(self):
        return True

    def readinto(self, buffer):
        size = self.stream.readinto(buffer)
        self.digest.update(memoryview(buffer)[:size])
        return size


def bound_rows(stream, expected_path, expected_digest, expected_rows, expected_cswitch, receipts):
    """Preserve the historical valid-row parser; bind both passes to one file."""
    def rows(path):
        if absolute(path) != expected_path:
            raise ValueError("audit attempted another numeric input")
        stream.seek(0)
        hashed = HashingRead(stream)
        count = cswitch = 0
        with io.TextIOWrapper(io.BufferedReader(hashed), encoding="ascii", newline="") as text:
            reader = csv.reader(text)
            if next(reader) != SCHEMA:
                raise ValueError("bound CSV schema differs")
            for row in reader:
                if len(row) != 8:
                    raise ValueError("bound numeric row differs")
                values = tuple(map(int, row))
                count += 1
                cswitch += values[0] == 1
                yield values
        if hashed.digest.hexdigest() != expected_digest or (count, cswitch) != (expected_rows, expected_cswitch):
            raise ValueError("bound audit pass hash/count differs")
        receipts.append({"sha256": hashed.digest.hexdigest(), "rows": count, "cswitch_rows": cswitch})
    return rows


def run_verified(root, manifest, manifest_sha256, audit_source, account_source, core_source, private_decisions=None):
    root, manifest, audit_source, account_source, core_source = map(absolute, (root, manifest, audit_source, account_source, core_source))
    if HEX.fullmatch(manifest_sha256) is None:
        raise ValueError("explicit lowercase manifest SHA-256 required")
    csv_path = root / "offline" / "qpc-prefix.csv"
    qpc_path = root / "offline" / "qpc.stdout.json"
    csw_path = root / "offline" / "CSWITCH_RAW_RESULT.json"
    wrapper = absolute(__file__)
    files = [manifest, csv_path, qpc_path, csw_path, audit_source, account_source, core_source, wrapper]
    if private_decisions is not None:
        private_decisions = absolute(private_decisions)
        if private_decisions in files or private_decisions.exists():
            raise ValueError("private decisions must be a new distinct output")
    if len(set(files)) != len(files):
        raise ValueError("all manifest/input/source paths must be distinct")
    with PinnedInputs(files) as pins:
        snapshots = {path: pins.small_bytes(path) for path in files if path != csv_path}
        if hashlib.sha256(snapshots[manifest]).hexdigest() != manifest_sha256:
            raise ValueError("manifest SHA-256 differs")
        m = parse_json(snapshots[manifest])
        if type(m.get("schema")) is not int or m["schema"] != 2 or m.get("binding_scope") != BINDING_SCOPE:
            raise ValueError("explicit post-hoc binding manifest required")
        expected = {csv_path: m["csv_sha256"], qpc_path: m["qpc_summary_sha256"],
                    csw_path: m["cswitch_summary_sha256"], audit_source: m["audit_source_sha256"],
                    account_source: m["account_source_sha256"], core_source: m["core_source_sha256"],
                    wrapper: m["wrapper_source_sha256"]}
        if len(expected) != 7:
            raise ValueError("input/source paths must be distinct")
        for path, digest in expected.items():
            actual = sha256(path) if path == csv_path else hashlib.sha256(snapshots[path]).hexdigest()
            if not isinstance(digest, str) or HEX.fullmatch(digest) is None or actual != digest:
                raise ValueError("input/source SHA-256 differs: " + str(path))
        if csv_path.stat().st_size != natural(m["csv_bytes"], "csv_bytes", True):
            raise ValueError("numeric CSV byte length differs")
        for source in (audit_source, account_source, core_source, wrapper):
            if source.stat().st_size > MAX_SMALL_FILE:
                raise ValueError("bounded source input exceeded")
        h, c = (parse_json(snapshots[path]) for path in (qpc_path, csw_path))
        rows = natural(m["decoded_rows"], "decoded_rows", True)
        cswitch = natural(m["cswitch_rows"], "cswitch_rows")
        if natural(h["decoded"], "qpc decoded") != rows or natural(c["decoded_cswitch"], "cswitch decoded") != cswitch:
            raise ValueError("bound rows disagree with decoder summaries")
        for document, names in ((h, ("unknown_required_prefix", "header_events_lost", "header_buffers_lost", "process_rc", "close_rc", "output_error")),
                                (c, ("unknown_cswitch", "header_events_lost", "process_trace_rc", "close_trace_rc", "output_error"))):
            if any(natural(document[name], name) != 0 for name in names):
                raise ValueError("saved decoder status/loss not zero")
        if natural(h["events"], "qpc events") != natural(c["events"], "cswitch events") or h["events"] < rows:
            raise ValueError("decoder event totals differ")
        if natural(h["processors"], "qpc processors", True) != natural(c["processors"], "cswitch processors", True):
            raise ValueError("decoder processor totals differ")
        actual_rows, kinds = scan_numeric(csv_path, rows)
        if kinds[1] != cswitch:
            raise ValueError("numeric CSwitch count differs")
        audit = load_bound_audit(audit_source, account_source, core_source,
                                 snapshots[audit_source], snapshots[account_source], snapshots[core_source])
        passes = []
        with csv_path.open("rb") as bound_csv:
            pins.verify_stream_identity(bound_csv, csv_path)
            audit.__globals__["rows"] = bound_rows(bound_csv, csv_path, m["csv_sha256"], rows, cswitch, passes)

            def bound_summary(path):
                if absolute(path) != qpc_path:
                    raise ValueError("audit attempted an unbound summary read")
                return parse_json(snapshots[qpc_path])

            audit.__globals__["read"] = bound_summary
            result = audit(root, private_decisions)
        if len(passes) != 2:
            raise ValueError("expected exactly two completely consumed bound audit passes")
        if (result.get("admission") != "BLOCKED" or result.get("coverage_complete") is not False
                or result.get("I1_I7") != "OPEN"):
            raise ValueError("partition audit must retain OPEN/BLOCKED/incomplete")
        # Keep pins held throughout both internal audit passes and this recheck.
        for path, digest in expected.items():
            if sha256(path) != digest:
                raise ValueError("pinned input changed during audit")
        return {"scope": "VERIFIED_SAVED_INPUT_PARTITION_AUDIT_ONLY", "binding_scope": BINDING_SCOPE,
                "manifest_sha256": manifest_sha256, "inputs_sha256": {str(k): v for k, v in expected.items()},
                "numeric_rows": actual_rows, "cswitch_rows": kinds[1],
                "all_audit_passes_read_same_verified_file_handle": True,
                "audit_pass_receipts": passes,
                "ordinary_data_write_delete_sharing_denied_by_leaf_and_ancestor_read_pins": True,
                "all_metadata_writes_prevented": False,
                "original_decoder_output_csv_digest_was_not_recorded": True,
                "retroactive_original_run_binding_claimed": False,
                "cpu_identity_dual_field_decoder_issue_resolved": False,
                "python_version": sys.version, "python_role": "OFFLINE_ANALYSIS_TOOL_NOT_TARGET_RUNTIME",
                "python_executable_sha256": sha256(Path(sys.executable)),
                "private_decisions_sha256": sha256(private_decisions) if private_decisions is not None else None,
                "input_object_identities": pins.identities,
                "audit_result": result, "coverage_complete": False, "I1_I7": "OPEN", "admission": "BLOCKED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--audit-source", type=Path, required=True)
    parser.add_argument("--account-source", type=Path, required=True)
    parser.add_argument("--core-source", type=Path, required=True)
    parser.add_argument("--private-decisions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("result output already exists")
    result = run_verified(args.root, args.manifest, args.manifest_sha256, args.audit_source, args.account_source, args.core_source, args.private_decisions)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({"scope": result["scope"], "numeric_rows": result["numeric_rows"],
                      "cswitch_rows": result["cswitch_rows"], "admission": "BLOCKED"}))


if __name__ == "__main__":
    main()
