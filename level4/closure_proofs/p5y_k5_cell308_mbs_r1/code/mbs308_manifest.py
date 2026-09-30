"""Cell-308 MB-S successor campaign (r1) -- the Q8 freeze-manifest writer `protocol/MBS308_FREEZE.json` (the input
manifest the grant binds by sha256), modelled on MB r1's mb308_manifest. Built by the non-holder builder4 (research
brief 46); NOT frozen.

It lists, with sha256 and git blob computed from the bytes AT THAT TIME:
  * EVERY file of the namespace except the manifest itself, __pycache__ and the post-freeze directories
    (qualification, review, authorization, evidence, adjudication, postexec);
  * EVERY pinned external file, with its sha256 and its git blob at HEAD: MB r1's science modules of SCIENCE_PINS at MB
    r1's paths, MB r1's module pins (PIN.PINS, F2, F3, the C2b PL hook), MB r1's consumer / research input pins
    (CON.PINS) and the verifier's own pins (the tail-figure pattern file);
  * EVERY file the verifier or the static suite pins at a named COMMIT (config `commit_pins`), and every governance
    record QC13-S checks (config `governance_records`, blob ids only: nothing of them is read here);
  * the driver sha256, the helper pins, the platform pins, the operational constants as the code carries them, and the
    guard-geometry field `guard.cell308_cover` that QC12-S exempts.
It refuses (writes nothing) when an external file differs from its pin or from its blob at HEAD, or a commit pin
does not resolve. It writes nothing else.

The freeze is NOT authorised: this writer runs only with --freeze (the freeze step itself, or a sandbox), or with
--out FILE outside the repository (a dry run).

    python3.14 -I -S -B mbs308_manifest.py --freeze
    python3.14 -I -S -B mbs308_manifest.py --out /elsewhere/MBS308_FREEZE.json
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))

OUT = NS / "protocol" / "MBS308_FREEZE.json"
SCHEMA = "rebaseguard.p5y.k5.cell308-mbs-r1.freeze-manifest.v1"
ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1"}


class ManifestRefusal(RuntimeError):
    """The manifest cannot be written (a pin does not hold)."""


def blob(b: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(repo: Path, *args) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo), *args], capture_output=True,
                       text=True, env=ENV, stdin=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""


def git_bytes(repo: Path, spec: str) -> bytes | None:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(repo), "cat-file", "blob", spec],
                       capture_output=True, env=ENV, stdin=subprocess.DEVNULL)
    return p.stdout if p.returncode == 0 else None


# ------------------------------------------------------------------ the core (no driver import; testable anywhere)
def namespace_files(ns: Path, out: Path, post_freeze_dirs) -> list:
    """Every file of the namespace that the freeze covers (the manifest itself, __pycache__ and the post-freeze
    directories excluded)."""
    files = []
    for p in sorted(ns.rglob("*")):
        rel = p.relative_to(ns).parts
        if p.is_file() and p != out and "__pycache__" not in p.parts and rel[0] not in post_freeze_dirs:
            files.append(p)
    return files


def frozen_files(repo: Path, ns: Path, out: Path, post_freeze_dirs) -> dict:
    return {str(p.relative_to(repo)): {"sha256": sha(p.read_bytes()), "git_blob": blob(p.read_bytes())}
            for p in namespace_files(ns, out, post_freeze_dirs)}


def external_files(repo: Path, pins: dict) -> dict:
    """key -> {path, sha256, git_blob (at HEAD)}; `pins`: key -> (repo-relative path, pinned sha256 or None, pinned
    git-blob id or prefix or None). Refuses on any mismatch."""
    out = {}
    for key, (rel, pin_sha, pin_blob) in sorted(pins.items()):
        p = repo / rel
        if not p.is_file():
            raise ManifestRefusal(f"{key}: {rel} is missing")
        raw = p.read_bytes()
        got, head = sha(raw), git(repo, "rev-parse", f"HEAD:{rel}")
        if (pin_sha is not None and got != pin_sha) or head != blob(raw) or \
                (pin_blob is not None and not head.startswith(pin_blob)):
            raise ManifestRefusal(f"{key}: {rel} differs from its pin or from its blob at HEAD")
        out[key] = {"path": rel, "sha256": got, "git_blob": head}
    return out


def commit_files(repo: Path, pins: dict) -> dict:
    """key -> {commit, path, sha256, git_blob}; `pins`: key -> (commit, path, pinned sha256 or None)."""
    out = {}
    for key, (commit, rel, pin_sha) in sorted(pins.items()):
        b = git(repo, "rev-parse", "-q", "--verify", f"{commit}:{rel}")
        raw = git_bytes(repo, b) if b else None
        if raw is None or (pin_sha is not None and sha(raw) != pin_sha):
            raise ManifestRefusal(f"{key}: {commit}:{rel} does not resolve or differs from its pin")
        out[key] = {"commit": commit, "path": rel, "sha256": sha(raw), "git_blob": b}
    return out


def record_blobs(repo: Path, records: list) -> dict:
    """QC13-S governance records: blob ids only (rev-parse; the records' bytes are never read here). A record whose
    commit is not yet named (PENDING) is listed as such."""
    out = {}
    for r in records:
        if not r.get("commit"):
            out[r["id"]] = {"status": "PENDING_RECORD", "path": r.get("path")}
            continue
        b = git(repo, "rev-parse", "-q", "--verify", f"{r['commit']}:{r['path']}")
        if not b:
            raise ManifestRefusal(f"governance record {r['id']}: {r['commit']}:{r['path']} does not resolve")
        out[r["id"]] = {"commit": r["commit"], "path": r["path"], "git_blob": b}
    return out


# ------------------------------------------------------------------ the pins (driver + verifier)
def external_pins(D, QF) -> dict:
    """Every pinned external file at HEAD: key -> (path, pinned sha256 or None, pinned blob id / prefix or None)."""
    ext = {f"science:{k}": (f"{D.NSF_REL}/code/{k}.py", v[0], v[1]) for k, v in D.SCIENCE_PINS.items()}
    ext.update({f"module:{k}": (v[0], v[1], v[2]) for k, v in D.PIN.PINS.items()})
    ext["module:F2_mb_independent"] = (D.PIN.INDEP_PIN[0], D.PIN.INDEP_PIN[1], D.PIN.INDEP_PIN[2])
    ext["module:F3_tuple_independent"] = (D.PIN.TUPLE_PIN[0], D.PIN.TUPLE_PIN[1], D.PIN.TUPLE_PIN[2])
    if D.PIN.C2B_PL_HOOK:
        ext["module:vd_pl"] = (D.PIN.C2B_PL_HOOK[0], D.PIN.C2B_PL_HOOK[1], D.PIN.C2B_PL_HOOK[2])
    ext.update({f"input:{k}": (v[0], v[1], v[2]) for k, v in D.CON.PINS.items()})
    ext.update({k: (v[0], v[1], v[2]) for k, v in QF.EXTERNAL_PINS.items()})
    return ext


def commit_pins(QF) -> dict:
    return {c["key"]: (c["commit"], c["path"], c.get("sha256")) for c in QF.load_config()["commit_pins"]}


def constants(D) -> dict:
    """The operational constants exactly as the code carries them (recorded, never chosen here)."""
    import mbs308_host as HOST
    import mbs308_state as STATE
    return {"pre_marker_s": D.PRE_CAP_S, "evaluation_s_per_attempt": D.EVAL_CAP_S, "decoy_cap_s": D.DECOY_CAP_S,
            "workers": D.WORKERS, "rung_cpu_cap_s": {k: {str(r): c for r, c in v.items()} for k, v in
                                                        D.RUNG_CPU_CAP_S.items()},
            "mem_cap_bytes": D.MEM_CAP_BYTES, "mem_poll_s": D.MEM_POLL_S, "free_mem_min_bytes": D.FREE_MEM_MIN_BYTES,
            "excl_cpu_pct": D.EXCL_CPU_PCT, "excl_allow": sorted(D.EXCL_ALLOW),
            "seal_retry_delays_s": list(D.SEAL_RETRY_DELAYS), "max_resumes": STATE.MAX_RESUMES,
            "deadline_s": STATE.DEADLINE_S, "ckpt_fail_limit": STATE.CKPT_FAIL_LIMIT,
            "min_free_disk_bytes": HOST.MIN_FREE_DISK, "memory_pressure_normal": HOST.MEMORY_PRESSURE_NORMAL,
            "su_gating_keys": list(HOST.SU_GATING_KEYS), "caffeinate_flags": list(HOST.CAFFEINATE_FLAGS)}


def manifest(D, QF, repo: Path = REPO, ns: Path = NS, out: Path = OUT) -> dict:
    G = D.GUARD
    cfg = QF.load_config()
    return {
        "schema": SCHEMA, "cell": D.TARGET_CELL, "route": "MB-S", "scope": "CLOSURE_ONLY",
        "frozen_dirs": list(D.FROZEN_DIRS), "post_freeze_dirs": list(D.POST_FREEZE_DIRS),
        "frozen_files": frozen_files(repo, ns, out, D.POST_FREEZE_DIRS),
        "external_files": external_files(repo, external_pins(D, QF)),
        "commit_pinned_files": commit_files(repo, commit_pins(QF)),
        "governance_records": record_blobs(repo, cfg["governance_records"]),
        "driver": {"path": D.NS_REL + "/code/mbs308_driver.py",
                   "sha256": sha((ns / "code" / "mbs308_driver.py").read_bytes())},
        "verifier": {"path": D.NS_REL + "/code/mbs308_qualify.py",
                     "sha256": sha((ns / "code" / "mbs308_qualify.py").read_bytes()),
                     "cases_config_sha256": sha((ns / "config" / "MBS308_QUALIFICATION_CASES.json").read_bytes())},
        "helper_sha256": dict(D.HELPER_SHA256),
        "science_base_commit": D.SCIENCE_BASE_COMMIT,
        "science_pins": {k: {"path": f"{D.NSF_REL}/code/{k}.py", "sha256": v[0], "git_blob": v[1]}
                         for k, v in D.SCIENCE_PINS.items()},
        "platform_pins": dict(D.PLATFORM_PINS),
        "lineage": [list(x) for x in D.LINEAGE],
        "rules": {"D1_sub_block_max_width": str(G.SUB_BLOCK_MAX_WIDTH), "D2_hull_bits": G.HULL_BITS,
                  "D3_rlr_ladder": list(D.S1M.LADDER_RLR), "D4_c2b_N": list(D.S1M.LADDER_C2B_N),
                  "D4_c1b_d": list(D.S1M.LADDER_C1B_D)},
        "outcomes": list(D.OUTCOMES),
        "constants": constants(D),
        "exactly_once": {"marker": D.CONSUMED_REF, "journal": D.JOURNAL_REF, "ckpt": D.CKPT_REF,
                         "pending": D.PENDING_REF, "result": D.RESULT_REL, "grant": D.GRANT_REL,
                         "qualification": D.QUAL_REL, "qualification_review": D.QREVIEW_REL,
                         "qualified_worktree": D.QUALIFIED_WORKTREE, "qualified_git_dir": D.QUALIFIED_GIT_DIR,
                         "qualified_branch": D.QUALIFIED_BRANCH},
        "mbr1_state": {"marker": D.MBR1_MARKER, "target": D.MBR1_MARKER_TARGET, "branch": D.MBR1_BRANCH},
        # QC12-S exempts cell 308's cover geometry ONLY inside this field and in the guard source
        "guard": {"cell308_cover": [str(x) for x in G.CELL308], "admitted_pairs": len(G.target_admitted_set()),
                  "consumed_ref": G.CONSUMED_REF},
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true", help="write protocol/MBS308_FREEZE.json (the freeze step only)")
    ap.add_argument("--out", help="dry run: write the manifest to this file OUTSIDE the repository")
    a = ap.parse_args(argv)
    if a.freeze == bool(a.out):
        print("MANIFEST REFUSED: exactly one of --freeze (the freeze step) or --out FILE (a dry run outside the "
              "repository)")
        return 2
    if a.out and Path(a.out).resolve().is_relative_to(REPO.resolve()):
        print("MANIFEST REFUSED: --out must lie outside the repository")
        return 2
    sys.path.insert(1, str(NS / "tests"))
    import mbs308_driver as D
    import mbs308_qualify as QF
    try:
        man = manifest(D, QF)
    except ManifestRefusal as exc:
        print(f"MANIFEST REFUSED: {exc}")
        return 2
    dst = OUT if a.freeze else Path(a.out)
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    print(f"wrote {dst}: {len(man['frozen_files'])} frozen files, {len(man['external_files'])} external files, "
          f"{len(man['commit_pinned_files'])} commit-pinned files; sha256 {sha(dst.read_bytes())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
