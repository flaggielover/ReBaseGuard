"""Resolve a frozen MSYS2 package database; download archives only, never install.

Archive inspection requires Python 3.14 (zstd stdlib), not the P309 interpreter.
The database is an index, NOT an authentication root. Every selected archive must
also pass signature verification against independently pinned publisher keys.
"""
import argparse
import concurrent.futures
import hashlib
import json
import pathlib
import re
import subprocess
import tarfile
import uuid

BASE = "https://repo.msys2.org/mingw/ucrt64/"
ROOT = "mingw-w64-ucrt-x86_64-qemu"
QEMU_HASH = "55f87e3a1448f5cf1cd7d7b9f061846a13b9571eb9b1a1df51eab3d9a9d42429"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read_db(path):
    packages = {}
    with tarfile.open(path, "r:*") as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith("/desc"):
                continue
            fields = {}
            for block in archive.extractfile(member).read().decode().split("\n\n"):
                lines = block.strip().splitlines()
                if lines:
                    fields[lines[0].strip("%")] = lines[1:]
            name = fields["NAME"][0]
            if name in packages:
                raise ValueError("duplicate package: " + name)
            packages[name] = fields
    return packages


def resolve(db):
    def dependency_name(spec):
        match = re.fullmatch(r"([^<>=]+)(?:(>=|<=|=|>|<)(.+))?", spec)
        if not match:
            raise ValueError("invalid dependency: " + spec)
        name, operator, required = match.groups()
        if name in db:
            actual = db[name]["VERSION"][0]
        else:
            choices = [(n, v.partition("=")[2]) for n, p in db.items()
                       for v in p.get("PROVIDES", []) if v.partition("=")[0] == name]
            if len(choices) != 1:
                raise ValueError("ambiguous/missing provider: " + spec)
            name, actual = choices[0]
        if operator:
            # These locked packages use numeric versions only. Do not pretend to
            # implement all libalpm epoch/alpha/tilde comparison semantics.
            if operator == "=":
                valid = actual == required
            else:
                if not all(re.fullmatch(r"[0-9]+(?:[.-][0-9]+)*", v)
                           for v in (actual, required)):
                    raise ValueError("unsupported version comparison: " + spec)
                upstream = actual if "-" in required else actual.split("-")[0]
                a, b = (tuple(map(int, re.split(r"[.-]", v))) for v in (upstream, required))
                width = max(len(a), len(b))
                a += (0,) * (width - len(a))
                b += (0,) * (width - len(b))
                valid = {">=": a >= b, "<=": a <= b, ">": a > b, "<": a < b}[operator]
            if not valid:
                raise ValueError("unsatisfied version: " + spec + ": " + actual)
        return name
    found = {}
    todo = [ROOT]
    while todo:
        name = todo.pop()
        if name in found:
            continue
        p = db[name]  # No guessed provider or silently missing dependency.
        filename = p["FILENAME"][0]
        if not re.fullmatch(r"[A-Za-z0-9_.+~:-]+\.pkg\.tar\.(?:zst|xz)", filename):
            raise ValueError("unsafe filename")
        if ":" in filename:
            raise ValueError("Windows ADS filename")
        dependencies = p.get("DEPENDS", [])
        resolved = [dependency_name(d) for d in dependencies]
        found[name] = dict(name=name, version=p["VERSION"][0], filename=filename,
                           url=BASE + filename, sha256=p["SHA256SUM"][0],
                           archive_bytes=int(p["CSIZE"][0]),
                           installed_bytes=int(p["ISIZE"][0]), dependencies=dependencies)
        todo.extend(resolved)
    if found[ROOT]["version"] != "11.1.2-1" or found[ROOT]["sha256"] != QEMU_HASH:
        raise ValueError("QEMU publisher pin mismatch")
    return [found[k] for k in sorted(found)]


def download(p, directory):
    dest = directory / p["filename"]
    if dest.exists():
        if sha(dest) != p["sha256"]:
            raise ValueError("existing archive differs; preserve and investigate: " + str(dest))
    else:
        part = dest.with_name(dest.name + ".partial-" + uuid.uuid4().hex)
        subprocess.run(["curl.exe", "--fail", "--location", "--silent", "--show-error",
                        "--retry", "2", "--retry-all-errors", "--max-time", "180",
                        p["url"], "--output", str(part)], check=True)
        if sha(part) != p["sha256"] or part.stat().st_size != p["archive_bytes"]:
            raise ValueError("download digest/size mismatch: " + p["name"])
        part.rename(dest)
    sig = dest.with_name(dest.name + ".sig")
    if not sig.exists():
        part = sig.with_name(sig.name + ".partial-" + uuid.uuid4().hex)
        subprocess.run(["curl.exe", "--fail", "--location", "--silent", "--show-error",
                        "--retry", "2", "--retry-all-errors", "--max-time", "60",
                        p["url"] + ".sig", "--output", str(part)], check=True)
        part.rename(sig)
    return p["name"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("database", type=pathlib.Path)
    ap.add_argument("output", type=pathlib.Path)
    ap.add_argument("--download", action="store_true")
    args = ap.parse_args()
    packages = resolve(read_db(args.database))
    plan = dict(schema="P309_ARCHIVE_LOCK/1", database_sha256=sha(args.database),
                packages=packages, archive_bytes=sum(p["archive_bytes"] for p in packages),
                installed_bytes=sum(p["installed_bytes"] for p in packages),
                installation_performed=False, signatures_verified=False)
    lock = args.output / "archive-lock.json"
    content = json.dumps(plan, indent=2) + "\n"
    if lock.exists() and lock.read_text() != content:
        raise ValueError("refusing to replace an existing lock")
    if not lock.exists():
        lock.write_text(content, encoding="utf-8")
    print(json.dumps({k: v for k, v in plan.items() if k != "packages"}))
    print("packages:", len(packages), flush=True)
    if args.download:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            for name in pool.map(lambda p: download(p, args.output), packages):
                print(name, flush=True)


if __name__ == "__main__":
    main()
