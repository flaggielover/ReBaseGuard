"""Independent check of the SF1-A open semantics on scratch files only (does not import any p309 module).
It reproduces the added call  os.close(os.open(path, O_WRONLY | O_APPEND | O_NOFOLLOW))  and compares with what the
ledger writer (q309_guard: Path.open("a")) would do."""
import errno
import json
import os
import subprocess
import sys
import time
from pathlib import Path

W = Path("/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t7/sf1a_review/work2/sem")
W.mkdir(exist_ok=True)
FLAGS = os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW
out = {"euid": os.geteuid()}


def probe(p):
    try:
        os.close(os.open(str(p), FLAGS))
        return "ok"
    except OSError as exc:
        return f"{type(exc).__name__} errno {exc.errno} ({errno.errorcode.get(exc.errno)})"


def writer(p):
    try:
        with Path(p).open("a"):
            pass
        return "ok"
    except OSError as exc:
        return f"{type(exc).__name__} errno {exc.errno} ({errno.errorcode.get(exc.errno)})"


# regular ledger: success; bytes, size, mtime, ctime unchanged
reg = W / "REG.jsonl"
reg.write_bytes(b'{"a": 1}\n')
os.utime(reg, (1_000_000_000, 1_000_000_000))
st0 = os.stat(reg)
b0 = reg.read_bytes()
time.sleep(0.05)
r = probe(reg)
st1 = os.stat(reg)
out["regular"] = {"probe": r, "bytes_same": reg.read_bytes() == b0, "size_same": st0.st_size == st1.st_size,
                  "mtime_same": st0.st_mtime_ns == st1.st_mtime_ns, "ctime_same": st0.st_ctime_ns == st1.st_ctime_ns,
                  "dir_entries_after": sorted(p.name for p in W.iterdir())}
# missing: refused ENOENT, not created (the writer would create it)
miss = W / "MISSING.jsonl"
out["missing"] = {"probe": probe(miss), "created_by_probe": miss.exists()}
# symlink to a regular file: refused ELOOP (the writer would follow it)
ln = W / "LINK.jsonl"
if not ln.is_symlink():
    ln.symlink_to(reg)
out["symlink"] = {"probe": probe(ln), "writer_would": "follows the link (Path.open('a') has no O_NOFOLLOW)"}
# a directory in the ledger's place
dd = W / "DIR.jsonl"
dd.mkdir(exist_ok=True)
out["directory"] = {"probe": probe(dd), "writer": writer(dd)}
# mode 0444: as root both succeed (same credential check as the writer); as non-root both fail EACCES
ro = W / "RO.jsonl"
ro.write_bytes(b"")
os.chmod(ro, 0o444)
out["mode_0444"] = {"probe": probe(ro), "writer": writer(ro)}
# dangling symlink
dl = W / "DANGLING.jsonl"
if not dl.is_symlink():
    dl.symlink_to(W / "nowhere")
out["dangling_symlink"] = {"probe": probe(dl)}
# FIFO in the ledger's place: an O_WRONLY open without a reader blocks (child with timeout)
ff = W / "FIFO.jsonl"
if not ff.exists():
    os.mkfifo(ff)
code = f"import os; os.close(os.open({str(ff)!r}, {FLAGS}))"
try:
    subprocess.run([sys.executable, "-c", code], timeout=2)
    out["fifo"] = "returned"
except subprocess.TimeoutExpired:
    out["fifo"] = "BLOCKS (no reader): the probe would hang, not refuse; the writer would hang the same way"
print(json.dumps(out, indent=1))
