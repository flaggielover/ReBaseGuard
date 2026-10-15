"""Offline publisher signature verification; never imports a private/production key."""
import argparse
import hashlib
import json
import pathlib
import subprocess

TRUSTED = {
    "AD351C50AE085775EB59333B5F92EFC1A47D45A1",
    "87771331B3F1FF5263856A6D974C8BE49078F532",
    "5F944B027F7FE2091985AA2EFA11531AA0AA7F57",
}


def digest(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records", type=pathlib.Path)
    ap.add_argument("result", type=pathlib.Path)
    args = ap.parse_args()
    root = args.records.resolve()
    archive_dir = root / "downloads"
    keys = root / "publisher-keyring"
    if args.result.exists():
        raise ValueError("result already exists")
    packages = json.loads((archive_dir / "archive-lock.json").read_text())["packages"]
    revoked = set((keys / "msys2-revoked").read_text().split())
    rows = []
    for package in packages:
        name = package["filename"]
        archive = archive_dir / name
        if digest(archive) != package["sha256"]:
            raise ValueError("archive hash mismatch: " + name)
        command = [r"C:\Program Files\Git\usr\bin\gpgv.exe", "--homedir", ".", "--status-fd", "1",
                   "--keyring", "./msys2-binary.gpg", "../downloads/" + name + ".sig", "../downloads/" + name]
        result = subprocess.run(command, cwd=keys, capture_output=True, timeout=60)
        statuses = result.stdout.decode("utf-8", "replace")
        valid = [line.split() for line in statuses.splitlines() if line.startswith("[GNUPG:] VALIDSIG ")]
        primary = valid[0][-1] if len(valid) == 1 else None
        accepted = (result.returncode == 0 and len(valid) == 1 and primary in TRUSTED and
                    primary not in revoked and valid[0][2] not in revoked and
                    not any(s in statuses for s in ("BADSIG", "ERRSIG", "EXPKEYSIG", "REVKEYSIG", "EXPSIG")))
        rows.append(dict(filename=name, sha256=package["sha256"], signature_sha256=digest(str(archive) + ".sig"),
                         returncode=result.returncode, primary=primary, accepted=accepted,
                         stdout=statuses, stderr=result.stderr.decode("utf-8", "replace")))
    report = dict(schema="P309_ARCHIVE_SIGNATURES/1", keyring_sha256=digest(keys / "msys2-binary.gpg"),
                  pin_source="https://www.msys2.org/dev/keyring/", trusted_primary_fingerprints=sorted(TRUSTED),
                  bootstrap="Official HTTPS keyring package SHA-256 independently pinned; public keys only",
                  signatures_valid=all(r["accepted"] for r in rows), results=rows)
    args.result.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(packages=len(rows), signatures_valid=report["signatures_valid"])))
    if not report["signatures_valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
