"""Inspect authenticated archives without executing/extracting software.

The opt-in materialize action is installation and requires separate human approval.
This preparatory archive tool uses Python 3.14 for zstd; P309 remains CPython 3.11.15.
"""
import argparse
import hashlib
import json
import pathlib
import struct
import tarfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def imports(data):
    """Strict PE32+ ordinary/delay import inspection; unknown formats fail closed."""
    def unpack(fmt, offset):
        return struct.unpack_from(fmt, data, offset)
    if data[:2] != b"MZ":
        raise ValueError("not PE")
    pe, = unpack("<I", 0x3C)
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("bad PE header")
    machine, sections = unpack("<HH", pe + 4)
    opt_size, = unpack("<H", pe + 20)
    optional = pe + 24
    if machine != 0x8664 or unpack("<H", optional)[0] != 0x20B or opt_size < 224:
        raise ValueError("requires x64 PE32+")
    image_base, = unpack("<Q", optional + 24)
    ranges = []
    for i in range(sections):
        base = optional + opt_size + i * 40
        virtual_size, virtual, size, raw = unpack("<IIII", base + 8)
        ranges.append((virtual, size, raw))
    def offset(rva):
        for virtual, size, raw in ranges:
            if virtual <= rva < virtual + size:
                result = raw + rva - virtual
                if result >= len(data):
                    break
                return result
        raise ValueError("import RVA outside file")
    def name(rva):
        start = offset(rva)
        end = data.find(b"\0", start, min(start + 260, len(data)))
        if end == -1:
            raise ValueError("unterminated import")
        value = data[start:end].decode("ascii").lower()
        if not value.endswith((".dll", ".drv")) or any(c in value for c in "/\\:"):
            raise ValueError("invalid DLL import: " + repr(value))
        return value
    result = set()
    for index, width in ((1, 20), (13, 32)):
        rva, length = unpack("<II", optional + 112 + index * 8)
        if not rva:
            continue
        start = offset(rva)
        for i in range(min(length // width + 1, 4096)):
            fields = unpack("<" + "I" * (width // 4), start + i * width)
            if not any(fields):
                break
            if index == 1:
                dll_rva = fields[3]
            else:
                dll_rva = fields[1] if fields[0] & 1 else fields[1] - image_base
            result.add(name(dll_rva))
        else:
            raise ValueError("unbounded import table")
    return sorted(result)


def scan(archive_dir, signatures):
    lock = json.loads((archive_dir / "archive-lock.json").read_text())
    report = json.loads(signatures.read_text())
    if not report["signatures_valid"] or len(report["results"]) != len(lock["packages"]):
        raise ValueError("signature verification missing")
    verified = {p["filename"]: p for p in report["results"]}
    members, binary_data = {}, {}
    for package in lock["packages"]:
        archive = archive_dir / package["filename"]
        if file_digest(archive) != package["sha256"] or not verified[archive.name]["accepted"] or \
                verified[archive.name]["sha256"] != package["sha256"]:
            raise ValueError("archive not authenticated")
        with tarfile.open(archive) as source:
            for item in source:
                path = pathlib.PurePosixPath(item.name)
                wanted = (item.name.startswith("ucrt64/bin/") and item.name.lower().endswith(".dll")) or \
                    item.name == "ucrt64/bin/qemu-system-x86_64.exe" or \
                    item.name.startswith("ucrt64/share/qemu/")
                if not wanted or item.isdir():
                    continue
                if not item.isfile() or path.is_absolute() or ".." in path.parts or ":" in item.name:
                    raise ValueError("unsafe archive entry")
                if item.name.lower() in members:
                    raise ValueError("case-insensitive archive collision: " + item.name)
                data = source.extractfile(item).read()
                row = dict(path=item.name, package=archive.name, package_sha256=package["sha256"],
                           bytes=len(data), sha256=digest(data))
                members[item.name.lower()] = row
                if item.name.lower().endswith((".dll", ".exe")):
                    binary_data[item.name.lower()] = data
    # This build's lib/qemu contains TCG tracing/test plugins, not required device
    # modules. They import qemu.exe and are deliberately outside this WHPX bundle.
    roots = [p for p in members if p == "ucrt64/bin/qemu-system-x86_64.exe" or
             p.startswith("ucrt64/share/qemu/")]
    selected, os_imports = {}, set()
    todo = roots[:]
    while todo:
        name = todo.pop()
        if name in selected:
            continue
        row = members[name].copy()
        if name in binary_data:
            try:
                row["imports"] = imports(binary_data[name])
            except ValueError as error:
                raise ValueError(name + ": " + str(error)) from error
            for dll in row["imports"]:
                target = "ucrt64/bin/" + dll
                if target in members:
                    todo.append(target)
                else:
                    os_imports.add(dll)
        selected[name] = row
    return dict(schema="P309_QEMU_RUNTIME_BUNDLE/1", qemu_version="11.1.2-1",
                archive_lock_sha256=file_digest(archive_dir / "archive-lock.json"),
                signature_report_sha256=file_digest(signatures),
                files=[selected[k] for k in sorted(selected)],
                bytes=sum(f["bytes"] for f in selected.values()),
                unresolved_system_imports=sorted(os_imports),
                caveat="Static import closure plus QEMU data; TCG plugins excluded; OS/dynamic loads require real inspection",
                installation_performed=False, formal_admission="BLOCKED")


def materialize(archive_dir, plan, destination):
    # No existing tree overwrite, links, install scripts, registry/PATH updates.
    # This function is deliberately never used by unit tests or plan preparation.
    destination = destination.resolve(strict=False)
    if destination != pathlib.Path(r"D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1"):
        raise ValueError("fixed reviewed destination required")
    for parent in destination.parents:
        if parent.exists() and (parent.is_symlink() or parent.is_junction()):
            raise ValueError("reparse parent")
    if destination.exists():
        raise ValueError("destination collision; do not overwrite or resume")
    grouped = {}
    for row in plan["files"]:
        path = pathlib.PurePosixPath(row["path"])
        if path.is_absolute() or ".." in path.parts or ":" in row["path"] or "\\" in row["path"]:
            raise ValueError("unsafe plan path")
        grouped.setdefault(row["package"], []).append(row)
    for filename, rows in grouped.items():
        if pathlib.Path(filename).name != filename or file_digest(archive_dir / filename) != rows[0]["package_sha256"]:
            raise ValueError("package binding mismatch")
    destination.mkdir(parents=True, exist_ok=False)
    for filename, rows in grouped.items():
        with tarfile.open(archive_dir / filename) as source:
            for row in rows:
                item = source.getmember(row["path"])
                if not item.isfile():
                    raise ValueError("not a regular file")
                data = source.extractfile(item).read()
                if len(data) != row["bytes"] or digest(data) != row["sha256"]:
                    raise ValueError("file binding mismatch")
                target = destination / pathlib.PurePosixPath(row["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archives", type=pathlib.Path)
    ap.add_argument("signatures", type=pathlib.Path)
    ap.add_argument("plan", type=pathlib.Path)
    ap.add_argument("--materialize-after-human-approval", type=pathlib.Path)
    args = ap.parse_args()
    plan = scan(args.archives, args.signatures)
    text = json.dumps(plan, indent=2) + "\n"
    if args.plan.exists():
        if args.plan.read_text(encoding="utf-8") != text:
            raise ValueError("plan changed; fresh review required")
    else:
        args.plan.write_text(text, encoding="utf-8")
    if args.materialize_after_human_approval:
        materialize(args.archives, plan, args.materialize_after_human_approval)
    print(json.dumps(dict(files=len(plan["files"]), bytes=plan["bytes"],
                         unresolved_system_imports=plan["unresolved_system_imports"],
                         installation_performed=bool(args.materialize_after_human_approval))))


if __name__ == "__main__":
    main()
