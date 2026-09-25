"""CLI for the AWS-only assembly successor.

  verify    read-only pre-assembly verification (default)
  assemble  build and WRITE <namespace>/evidence/FINAL_ASSEMBLY.json (needs --commit)

`assemble` refuses unless the successor is frozen: every file in the source manifest
must still hash to its frozen value, and the assembly contract to its own.
"""
import argparse
import json
import os
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
import ps1_assembly as A  # noqa: E402


def load_contract(path=None) -> dict:
    p = Path(path or NS / "config" / "ASSEMBLY_CONTRACT.json")
    hp = p.with_name(p.name.replace(".json", "_HASH"))
    if hp.exists() and A.sha256_file(p) != hp.read_text().strip():
        raise A.AssemblyRefusal("assembly contract does not match its frozen hash")
    return json.loads(p.read_text())


def verify_freeze() -> dict:
    man_p = NS / "config" / "SOURCE_MANIFEST.json"
    if not man_p.exists():
        raise A.AssemblyRefusal("successor is NOT frozen: no source manifest")
    hp = NS / "config" / "SOURCE_MANIFEST_HASH"
    if A.sha256_file(man_p) != hp.read_text().strip():
        raise A.AssemblyRefusal("source manifest does not match its frozen hash")
    man = json.loads(man_p.read_text())["files"]
    drift = [f for f, h in man.items()
             if not (NS / f).exists() or A.sha256_file(NS / f) != h]
    if drift:
        raise A.AssemblyRefusal(f"successor source drift: {drift}")
    return {"files": len(man), "drift": []}


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("verify", "assemble"), nargs="?", default="verify")
    ap.add_argument("--assembly-contract", default=None)
    ap.add_argument("--commit", action="store_true",
                    help="assemble: actually write the final assembly document")
    a = ap.parse_args(argv)
    try:
        acfg = load_contract(a.assembly_contract)
        if a.command == "verify":
            rep = A.preflight(acfg)
            out = {k: v for k, v in rep.items() if not k.startswith("_")}
            out["frozen"] = verify_freeze() if (NS / "config/SOURCE_MANIFEST.json").exists() \
                else "NOT_FROZEN"
            out["status"] = "PRE_ASSEMBLY_VERIFICATION_PASS"
            print(json.dumps(out, indent=1, sort_keys=True))
            return 0
        frozen = verify_freeze()
        doc = A.assemble(acfg)
        doc["successor_source_manifest_files"] = frozen["files"]
        target = Path(acfg["output_path"])
        if not a.commit:
            print(json.dumps({"status": "DRY_RUN: pass --commit to write", "target": str(target),
                              "assembly_sha256": doc["assembly_sha256"],
                              "cells": doc["aggregate"]["cells"]}, indent=1, sort_keys=True))
            return 0
        if target.exists():
            old = json.loads(target.read_text())
            if old.get("assembly_sha256") != doc["assembly_sha256"]:
                raise A.AssemblyRefusal(
                    f"a DIFFERENT final assembly already exists at {target}")
            print(json.dumps({"status": "ALREADY_ASSEMBLED",
                              "assembly_sha256": doc["assembly_sha256"]}, indent=1))
            return 0
        atomic_write(target, (json.dumps(doc, indent=1, sort_keys=True) + "\n").encode())
        print(json.dumps({"status": "ASSEMBLED", "path": str(target),
                          "assembly_sha256": doc["assembly_sha256"]}, indent=1, sort_keys=True))
        return 0
    except A.AssemblyRefusal as e:
        print(f"ASSEMBLY_REFUSAL: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
