"""Export the immutable P309 host packet and audit source; execute no host code.

Usage: python3 -B build_bundle.py /absolute/path/to/handoff.tar.gz
The archive is preparation material, never evidence of a completed host audit.
"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

PACKET_COMMIT = "2dce6244c2a9409fa7b318ddd6b8acaf289091bd"
R2_COMMIT = "501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
PACKET = NS + "_hardening/host_side_packet_501f48cb"
AUDIT_SHA256 = "ec9c8416159cf9e2e7372f97ce179a290def987007dc144591833615ca251f65"


def main():
    output = Path(sys.argv[1]).resolve()
    repo = subprocess.check_output(
        ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
        text=True).strip()

    def blob(commit, path):
        return subprocess.check_output(["git", "-C", repo, "cat-file", "blob", commit + ":" + path])

    files = {"packet/PACKET_MANIFEST.json": blob(PACKET_COMMIT, PACKET + "/PACKET_MANIFEST.json")}
    manifest = json.loads(files["packet/PACKET_MANIFEST.json"])
    if manifest["r2_commit"] != R2_COMMIT:
        raise ValueError("unexpected r2 binding")
    for name, expected in manifest["files"].items():
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("unsafe packet member")
        data = blob(PACKET_COMMIT, PACKET + "/" + name)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("packet hash mismatch: " + name)
        files["packet/" + name] = data
    audit = blob(R2_COMMIT, NS + "/code/p309_host.py")
    if hashlib.sha256(audit).hexdigest() != AUDIT_SHA256:
        raise ValueError("audit source hash mismatch")
    files["p309_host.py"] = audit
    for name in ("RUN_FIRST.txt", "CONTINUATION_STATUS.json"):
        files[name] = Path(__file__).with_name(name).read_bytes()
    sums = "".join(hashlib.sha256(data).hexdigest() + "  " + name + "\n"
                   for name, data in sorted(files.items()))
    files["SHA256SUMS"] = sums.encode()
    # Exclusive creation preserves any previously exported artifact.
    with output.open("xb") as stream:
        with tarfile.open(fileobj=stream, mode="w:gz") as archive:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo("p309-host-handoff/" + name)
                member.size = len(data)
                member.mode = 0o600
                archive.addfile(member, io.BytesIO(data))
    print(json.dumps({"archive": str(output), "members": len(files),
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                      "packet_commit": PACKET_COMMIT, "r2_commit": R2_COMMIT}, indent=2))


if __name__ == "__main__":
    main()
