"""Owned synthetic files only: contrast access-zero and read ancestor pins.

No real reparse point, policy, ACL or pre-existing evidence is changed. This
measures file-sharing behavior, not the exploitability of any old package.
"""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import tempfile

import run_verified_audit as v

HERE = Path(__file__).absolute().parent


def run_case(access):
    with tempfile.TemporaryDirectory(prefix="ancestor-probe-", dir=HERE) as temporary:
        base = Path(temporary)
        parent = base / "owned-parent"
        parent.mkdir()
        leaf = parent / "owned-input.bin"
        leaf.write_bytes(b"original saved input")
        pin = v.PinnedInputs([leaf])
        api = pin.api
        api.SetFileAttributesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
        api.SetFileAttributesW.restype = wintypes.BOOL
        api.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
        api.GetFileAttributesW.restype = wintypes.DWORD
        handles = []
        moved = base / "moved-parent"
        result = {"ancestor_desired_access": access, "leaf_desired_access": 0x80000000,
                  "share_mode": 1, "scope": "OWNED_SYNTHETIC_DIRECTORY_ONLY"}

        def open_handle(path, desired):
            handle = api.CreateFileW(str(path), desired, 1, None, 3, 0x02200000, None)
            if handle == ctypes.c_void_p(-1).value:
                return None, ctypes.get_last_error()
            return handle, 0

        try:
            # Only these newly created ancestors differ between the two cases.
            for directory in (base, parent):
                handle, error = open_handle(directory, access)
                if handle is None:
                    raise ctypes.WinError(error)
                handles.append(handle)
            handle, error = open_handle(leaf, 0x80000000)
            if handle is None:
                raise ctypes.WinError(error)
            handles.append(handle)
            for label, desired in (("generic_write_open", 0x40000000), ("write_attributes_open", 0x100)):
                handle, error = open_handle(parent, desired)
                result[label] = {"succeeded": handle is not None, "win32_error": error}
                if handle is not None:
                    if not api.CloseHandle(handle):
                        raise ctypes.WinError(ctypes.get_last_error())
            attributes = api.GetFileAttributesW(str(parent))
            if attributes == 0xFFFFFFFF:
                raise ctypes.WinError(ctypes.get_last_error())
            changed = bool(api.SetFileAttributesW(str(parent), attributes ^ 2))
            result["set_hidden_attribute"] = {"succeeded": changed, "win32_error": 0 if changed else ctypes.get_last_error()}
            if changed and not api.SetFileAttributesW(str(parent), attributes):
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                os.replace(parent, moved)
                result["ancestor_rename"] = {"succeeded": True, "win32_error": 0}
                parent.mkdir()
                leaf.write_bytes(b"replacement path content")
                result["same_original_path_can_name_replacement"] = leaf.read_bytes() != b"original saved input"
            except OSError as error:
                result["ancestor_rename"] = {"succeeded": False, "win32_error": error.winerror}
                result["same_original_path_can_name_replacement"] = False
        finally:
            for handle in reversed(handles):
                if not api.CloseHandle(handle):
                    raise ctypes.WinError(ctypes.get_last_error())
            if moved.exists():
                if leaf.exists():
                    leaf.unlink()
                if parent.exists():
                    parent.rmdir()
                os.replace(moved, parent)
        return result


if __name__ == "__main__":
    record = {"scope": "SYNTHETIC_FILE_SHARE_DIAGNOSTIC_ONLY", "cases": [run_case(0), run_case(0x80000000)],
              "real_reparse_point_created": False, "host_configuration_queries": 0, "uac": 0,
              "past_capture_tampering_proven": False, "formal_vulnerability_conclusion": False,
              "admission": "BLOCKED"}
    output = HERE / "ANCESTOR_SHARING_ACTUAL.json"
    with output.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps(record))
