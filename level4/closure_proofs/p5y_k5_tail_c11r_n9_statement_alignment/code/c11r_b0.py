"""C11R Phase B0 -- reconstruction of the authoritative predecessor state.

Every fact is established by something executable. LOCAL_MAIN_REF and REMOTE_MAIN_REF are recorded
SEPARATELY, because a scratch clone's ls-remote can read the local repository rather than GitHub.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

checks = []


def chk(n, name, ok, detail):
    checks.append({"id": f"B0_{n:02d}", "name": name, "pass": bool(ok), "detail": detail})


def main() -> int:
    # 1 -- on the C11R branch, which descends from the expected C11 HEAD
    branch = C.git("rev-parse", "--abbrev-ref", "HEAD")
    chk(1, "on the C11R branch", branch == "p5y-k5-tail-c11r-n9-statement-alignment",
        {"branch": branch})

    head = C.git("rev-parse", "HEAD")
    desc = C.git_ok("merge-base", "--is-ancestor", C.C11_HEAD, "HEAD")
    chk(2, "descends from the expected C11 HEAD 440bcd91", desc,
        {"expected_c11_head": C.C11_HEAD, "head": head})

    # 3 -- C11 published: the branch exists on origin at that HEAD
    ls = subprocess.run(["git", "-C", str(C.REPO), "ls-remote", "origin",
                         "refs/heads/p5y-k5-tail-c11-n9-independent-certifier"],
                        capture_output=True, text=True).stdout.split()
    chk(3, "C11 is published on origin at 440bcd91", bool(ls) and ls[0] == C.C11_HEAD,
        {"remote_c11_ref": ls[0] if ls else None})

    # 4, 5 -- C11's own final verdict, read from its committed artifact
    r11 = json.loads(C.blob_at(C.C11_HEAD, str(
        (C.C11 / "evidence" / "n9" / "C11_N9_RESULT.json").relative_to(C.REPO))).decode())
    chk(4, "C11 verdict is EXECUTION_INVALID and is not rewritten as success",
        r11["N9_VERDICT"] == "EXECUTION_INVALID",
        {"verdict": r11["N9_VERDICT"], "schema": r11["schema"]})
    chk(5, "N9 is OPEN entering C11R", r11["N9_STATUS_AFTER_C11"] == "OPEN",
        {"status": r11["N9_STATUS_AFTER_C11"]})

    # 6, 7 -- r5 authoritative, m=5 open set
    m5 = C.r5_open_by_verdict("5")
    r5 = C.r5_map()
    chk(6, "r5 is the authoritative coverage map", r5.get("revision") in ("r5", 5, "5")
        or "R5" in C.R5_PATH, {"revision": r5.get("revision"), "path": C.R5_PATH})
    chk(7, "m=5 open set is exactly {306, 307, 308, 309}", tuple(m5) == C.OPEN_CELLS,
        {"open_m5": m5})

    # 8 -- no r6
    r6 = [f for f in C.git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    chk(8, "no r6 coverage map exists", not r6, {"hits": r6})

    # 9 -- main untouched, LOCAL and REMOTE recorded SEPARATELY
    local_main = C.git("rev-parse", "refs/heads/main") if C.git_ok(
        "rev-parse", "--verify", "refs/heads/main") else None
    rm = subprocess.run(["git", "-C", str(C.REPO), "ls-remote", "origin", "refs/heads/main"],
                        capture_output=True, text=True).stdout.split()
    remote_main = rm[0] if rm else None
    chk(9, "REMOTE main is untouched at the expected commit",
        remote_main == C.REMOTE_MAIN_EXPECTED,
        {"LOCAL_MAIN_REF": local_main, "REMOTE_MAIN_REF": remote_main,
         "expected_remote": C.REMOTE_MAIN_EXPECTED,
         "note": ("recorded separately on purpose: in a --no-local scratch clone `ls-remote origin` "
                  "reads the LOCAL repository, not GitHub. This runs from the primary checkout."),
         "divergence_is_known_and_not_reconciled_here": local_main != remote_main})

    # 10 -- guard DENY. A guard is a SETTING, so this reads the settings, not prose about them.
    # A substring scan here hits C10's own review text discussing the string "guard": "ALLOW",
    # which is a description, not a guard. (C10 lesson: presence-check-as-detection.)
    def _guards(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "guard" and isinstance(v, str):
                    yield (path + "/" + k, v)
                else:
                    yield from _guards(v, path + "/" + str(k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from _guards(v, f"{path}[{i}]")

    settings, scanned = [], 0
    for f in sorted(C.CLOSURE.rglob("*.json")):
        if any(part in f.parts for part in ("node_modules", ".git")):
            continue
        try:
            obj = json.loads(f.read_text())
        except Exception:
            continue
        scanned += 1
        for where, val in _guards(obj):
            if val.upper() == "ALLOW":
                settings.append(f"{f.relative_to(C.REPO)}{where}")
    chk(10, "guard DENY: no ALLOW guard SETTING anywhere at C11R start", not settings,
        {"allow_settings": settings, "json_files_scanned": scanned,
         "method": ("parsed guard keys in committed JSON; review prose mentioning the string "
                    "is not a setting and is deliberately not matched")})

    # 11 -- C2..C11 integrity: nothing outside the C11R namespace has moved since C11 HEAD
    moved = [f for f in C.git("diff", "--name-only", f"{C.C11_HEAD}..HEAD").splitlines()
             if "p5y_k5_tail_c11r_n9_statement_alignment" not in f]
    chk(11, "C2-C11 integrity: no predecessor file modified", not moved, {"moved": moved})

    # 12 -- AWS untouched. Scanned by AST over IMPORTS and string literals, with THIS MODULE
    # EXCLUDED: a scanner that lists its own search terms matches itself and always fires.
    # (C10 lesson: exclude yourself from your own scans.)
    import ast as _ast
    self_name = pathlib.Path(__file__).name
    REMOTE = ("boto3", "botocore", "paramiko", "fabric", "aws", "ssh", "rebaseguard-aws",
              "rebaseguard-vultr")
    hits, scanned_mods = [], []
    for f in sorted((C.NS / "code").glob("*.py")):
        if f.name == self_name:
            continue
        scanned_mods.append(f.name)
        tree = _ast.parse(f.read_text())
        for n in _ast.walk(tree):
            if isinstance(n, _ast.Import):
                for a in n.names:
                    if a.name.split(".")[0].lower() in REMOTE:
                        hits.append(f"{f.name}: import {a.name}")
            elif isinstance(n, _ast.ImportFrom) and n.module:
                if n.module.split(".")[0].lower() in REMOTE:
                    hits.append(f"{f.name}: from {n.module}")
            elif isinstance(n, _ast.Constant) and isinstance(n.value, str):
                low = n.value.lower()
                if any(t in low for t in ("boto3", "paramiko", "rebaseguard-aws",
                                          "rebaseguard-vultr")) or low.startswith("ssh "):
                    hits.append(f"{f.name}: literal {n.value[:40]!r}")
    chk(12, "AWS untouched: no AWS, SSH or remote-worker surface in C11R code", not hits,
        {"hits": hits, "modules_scanned": scanned_mods, "self_excluded": self_name,
         "policy": "AWS IS FORBIDDEN for this campaign; local execution only"})

    # supporting record: the toolchain the ORIGINAL certifier needs must remain absent, which is
    # what makes an accidental import of it fail loudly rather than silently succeed.
    tc = C.toolchain_present()
    chk(13, "the original certifier's backend is absent, so accidental reuse cannot run",
        not tc["numpy"] and not tc["flint"], {"importlib_find_spec": tc})

    procs = C.classified_processes()
    chk(14, "no campaign worker is running at C11R start", not procs["campaign_workers"],
        {"workers": procs["campaign_workers"], "foreign": len(procs["foreign"])})

    failed = [c["id"] for c in checks if not c["pass"]]
    out = {"schema": "C11R_B0/1",
           "campaign": "C11R -- N9 statement-alignment repair",
           "purpose": ("determine whether the already-independent C11 certifier can certify THE "
                       "SAME STATEMENT N9 requires: block-uniform drift over the frozen e-block, "
                       "and the six operator constants for cell 306"),
           "predecessor": {"branch": "p5y-k5-tail-c11-n9-independent-certifier",
                           "head": C.C11_HEAD, "verdict": r11["N9_VERDICT"],
                           "n9_status": r11["N9_STATUS_AFTER_C11"],
                           "preserved_invalid": True},
           "LOCAL_MAIN_REF": local_main, "REMOTE_MAIN_REF": remote_main,
           "checks": checks, "failed": failed,
           "B0_CLASS": "PASS" if not failed else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "b0" / "C11R_B0.json", out, producer=__file__)
    for c in checks:
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['id']}  {c['name']}")
    print(f"\nB0_CLASS = {out['B0_CLASS']}   checks={len(checks)}  failed={failed}")
    print(f"LOCAL_MAIN_REF  = {local_main}")
    print(f"REMOTE_MAIN_REF = {remote_main}")
    print(f"wrote evidence/b0/C11R_B0.json sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
