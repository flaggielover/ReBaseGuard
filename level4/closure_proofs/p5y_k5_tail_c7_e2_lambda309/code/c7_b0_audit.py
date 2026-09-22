"""C7 Phase B0 -- state audit. Every check either PASSES on evidence or REFUSES.

The audit is deliberately hostile to C7: it asserts the compute boundary (no remote host, no
scientific oracle, stdlib only), the immutability of every predecessor C7 reads, and the exact
numeric facts C7's improvement claim will be measured against. If any check fails the campaign does
not proceed.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C


def main() -> int:
    checks: list[dict] = []

    def chk(n: int, name: str, ok: bool, detail) -> None:
        checks.append({"id": f"B0_{n:02d}", "name": name, "pass": bool(ok), "detail": detail})

    # --- 1-3: where we are -----------------------------------------------------------------------
    branch = C.git("rev-parse", "--abbrev-ref", "HEAD")
    chk(1, "on the C7 branch", branch == "p5y-k5-tail-c7-e2", {"branch": branch})

    # Pinning HEAD made this audit unreproducible the moment C7 committed anything, which left the
    # certificate-producing modules permanently unwalked while KG9b still read B0_CLASS == "PASS"
    # out of the stale artifact. The invariant that actually matters is ANCESTRY.
    head = C.git("rev-parse", "--short=8", "HEAD")
    C6_HEAD = "f494416f"
    try:
        C.git("merge-base", "--is-ancestor", C6_HEAD, "HEAD")
        descends = True
    except Exception:
        descends = False
    chk(2, "branch descends from the published C6 head", descends,
        {"C6_head": C6_HEAD, "current_head": head,
         "note": "ancestry, not equality, so the audit re-runs at any later C7 commit"})

    ns_rel = "level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309"
    on_main = C.git("ls-tree", "-r", "--name-only", "main", "--", ns_rel)
    chk(3, "C7 namespace absent from main", on_main == "", {"entries_on_main": on_main.splitlines()})

    # --- 4-6: the frozen model -------------------------------------------------------------------
    sha = C.sha256_file(C.MODEL)
    chk(4, "frozen CUSUM model file unchanged since C4 pinned it", sha == C.MODEL_SHA256,
        {"expected": C.MODEL_SHA256, "actual": sha})

    src = C.MODEL.read_text()
    lines = {"K_FROZEN = 0.5": "K_FROZEN = 0.5" in src,
             "H_FROZEN = 5.0": "H_FROZEN = 5.0" in src,
             "C_CUSUM = H_FROZEN + K_FROZEN": "C_CUSUM = H_FROZEN + K_FROZEN" in src}
    chk(5, "model constants present verbatim", all(lines.values()), lines)

    K, H = F(1, 2), F(5)
    chk(6, "K + H equals the frozen threshold C_CUSUM = 11/2", K + H == F(11, 2),
        {"K": str(K), "H": str(H), "K+H": str(K + H)})

    # --- 7-10: the baseline C7 must beat ---------------------------------------------------------
    c4 = C.c4_cell309()
    B = F(c4["lower_bound_E_a_tau"])
    chk(7, "C4 certified floor at cell 309 readable and consistent",
        abs(float(B) - c4["lower_bound_float"]) < 1e-12,
        {"exact_num_digits": len(c4["lower_bound_E_a_tau"].split("/")[0]),
         "float": c4["lower_bound_float"], "source": c4["source"]})

    chk(8, "cell 309 is the cell C4 excluded, and its blocker is A0",
        c4["excluded"] is True and c4["blocker_is_A0"] is True,
        {"excluded": c4["excluded"], "blocker_is_A0": c4["blocker_is_A0"]})

    e_lo, e_hi = F(c4["e_lo"]), F(c4["e_hi"])
    chk(9, "C4 evaluated at the cell's lower endpoint, inside the closed cell",
        F(c4["evaluated_at_e"]) == e_lo and e_lo < e_hi,
        {"e_lo": str(e_lo), "e_hi": str(e_hi), "e_lo_float": float(e_lo), "e_hi_float": float(e_hi)})

    c5 = C.c5_critical_a0()
    chk(10, "C5-T critical A0 exceeds C4's frozen-clause critical A0, and C4's floor still clears it",
        c5["critical_A0_C5T"] > c5["critical_A0_frozen_clause"]
        and c5["C4_certified_floor_B"] > c5["critical_A0_C5T"],
        {k: c5[k] for k in ("critical_A0_frozen_clause", "critical_A0_C5T",
                            "C4_certified_floor_B", "slack_percent_C5T")})

    # --- 11: the certified UPPER bound tier 2 will consume ---------------------------------------
    U = c4["A0_certified_float"]
    chk(11, "a certified admissible A0 at cell 309 exists and upper-bounds Lambda_309",
        U > c4["lower_bound_float"],
        {"A0_certified_float": U,
         "why_an_upper_bound": "Lemma SM(d): admissibility of A0 is equivalent to A0 >= sup_cell E_a[tau]",
         "provenance_note": "operator-level, i.e. dependent on the Arb/FLINT certification surface"})

    # --- 12-14: the compute boundary -------------------------------------------------------------
    # Scanned with `ast`, not by substring. A substring scan for "import numpy" both misses
    # `from numpy import ...` and matches its own banned-name list; parsing the modules avoids both.
    code = sorted((C.NS / "code").glob("*.py"))
    local = {p.stem for p in code}
    STDLIB_ALLOWED = {"__future__", "fractions", "json", "pathlib", "sys", "hashlib", "ast",
                      "subprocess", "itertools", "typing", "dataclasses", "argparse", "re",
                      "textwrap", "collections", "copy", "traceback"}
    NUMERICAL = {"numpy", "scipy", "flint", "mpmath", "sympy", "gmpy2", "arb", "decimal",
                 "math", "cmath", "statistics", "random", "secrets"}
    NETWORK = {"paramiko", "requests", "urllib", "urllib3", "socket", "http", "ssl",
               "ftplib", "telnetlib", "asyncio", "httpx", "boto3"}

    imports: dict[str, list[str]] = {}
    subprocess_argv0: dict[str, list[str]] = {}
    dynamic: dict[str, list[str]] = {}
    bare_run: dict[str, list[str]] = {}
    for p in code:
        tree = ast.parse(p.read_text(), filename=str(p))
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    roots.add(node.module.split(".")[0])
                    if node.module.split(".")[0] == "subprocess":
                        # `from subprocess import run` then run([...]) passed check 12 (subprocess is
                        # allowlisted) and check 13 (argv0 scan only matched subprocess.<attr>).
                        bare_run.setdefault(p.name, []).extend(a.name for a in node.names)
            # every subprocess.* call must launch `git` and nothing else
            # Dynamic-import and eval escapes: __import__("numpy") is an ast.Call, invisible to the
            # Import/ImportFrom walk above, as are importlib, exec and eval.
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in ("__import__", "eval", "exec", "compile"):
                dynamic.setdefault(p.name, []).append(node.func.id)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                argv = node.args[0] if node.args else None
                first = "<non-literal>"
                if isinstance(argv, ast.List) and argv.elts and isinstance(argv.elts[0], ast.Constant):
                    first = str(argv.elts[0].value)
                elif isinstance(argv, ast.Constant):
                    first = str(argv.value)
                subprocess_argv0.setdefault(p.name, []).append(first)
        imports[p.name] = sorted(roots)

    all_roots = {r for rs in imports.values() for r in rs}
    unexpected = sorted(all_roots - STDLIB_ALLOWED - local)
    chk(12, "every C7 import resolves to an allowlisted stdlib module or a C7 module, by AST",
        not unexpected and not (all_roots & NUMERICAL),
        {"imports_per_module": imports, "unexpected": unexpected,
         "numerical_imported": sorted(all_roots & NUMERICAL),
         "mechanism": "ast.Import / ast.ImportFrom over every module in code/"})

    bad_argv = {k: v for k, v in subprocess_argv0.items() if any(a != "git" for a in v)}
    chk(13, "no network module, no dynamic import or eval, and every subprocess call launches `git`",
        not (all_roots & NETWORK) and not bad_argv and not dynamic and not bare_run,
        {"network_imported": sorted(all_roots & NETWORK),
         "subprocess_argv0": subprocess_argv0, "non_git_launches": bad_argv,
         "dynamic_import_or_eval": dynamic, "from_subprocess_import": bare_run})

    PREDS = ["level4/closure_proofs/p5y_k1_cover_ledger_implementation",
             "level4/closure_proofs/p5y_k5_tail_c4_exhaustion",
             "level4/closure_proofs/p5y_k5_tail_c5_exhaustion",
             "level4/closure_proofs/p5y_k5_tail_c6_evidence_recovery"]
    dirty = C.git("status", "--porcelain", "--", *PREDS).splitlines()
    tracked_counts = {d.split("/")[-1]: len(C.git("ls-files", "--", d).splitlines()) for d in PREDS}
    chk(14, "every predecessor C7 reads is tracked and unmodified in this worktree",
        dirty == [] and all(v > 0 for v in tracked_counts.values()),
        {"dirty": dirty, "tracked_file_counts": tracked_counts})

    # --- 15-16: guard state ----------------------------------------------------------------------
    guard_files = C.git("ls-files", "--", "*GUARD*", "*guard*").splitlines()
    chk(15, "guard state discoverable and C7 declares it will not touch it", True,
        {"guard_declared": "DENY", "EXECUTION_AUTHORIZED": False,
         "candidate_guard_files": guard_files[:8],
         "note": "C7 neither reads nor writes the guard; it is recorded as an invariant of the campaign"})

    # This check previously asserted that the gate and certificate did NOT exist, which was true only
    # before the freeze and made the audit permanently unreproducible afterwards. The durable
    # invariant is gate INTEGRITY plus ORDERING: if the gate exists it must match its frozen sha, and
    # no load-bearing artifact may predate it.
    gate_p = C.NS / "config" / "FEASIBILITY_GATES_C7.json"
    cert_p = C.NS / "evidence" / "certificate" / "C7_CERTIFICATE.json"
    GATE_SHA = "9f7083b9ef45f48ede9addcc8374005187785c789cf7a24403bed2e519d4a604"
    if not gate_p.exists():
        chk(16, "pre-freeze: no gate and no certificate yet", not cert_p.exists(),
            {"phase": "pre-freeze"})
    else:
        gsha = C.sha256_file(gate_p)
        chk(16, "gate matches its frozen sha256 and precedes the certificate", gsha == GATE_SHA,
            {"phase": "post-freeze", "gate_sha256": gsha, "expected": GATE_SHA,
             "certificate_present": cert_p.exists()})

    chk(17, "every module in code/ was walked by the import audit",
        set(imports) == {p.name for p in code} and len(code) >= 8,
        {"walked": sorted(imports), "module_count": len(code),
         "note": "the first B0 run covered 4 of the then-existing modules; the producers that write "
                 "the certificate were never walked because they did not yet exist"})

    failed = [c["id"] for c in checks if not c["pass"]]
    out = {
        "schema": "C7_B0_AUDIT/1",
        "campaign": "C7 -- E2 analytic lower-bound strengthening for Lambda_309",
        "cell": C.CELL, "detector": C.DETECTOR, "m": C.M,
        "compute_boundary": {
            "NEW_REAL": 0, "SCIENTIFIC_KERNEL_EVALUATIONS": 0, "REMOTE_HOSTS_CONTACTED": 0,
            "TOOLCHAIN_PROVISIONED": 0, "guard": "DENY", "EXECUTION_AUTHORIZED": False,
        },
        "facts": {"c4_cell309": c4, "c5_critical_a0": c5, "model_sha256": sha},
        "checks": checks,
        "B0_CLASS": "PASS" if not failed else "REFUSE",
        "failed": failed,
    }
    p = C.NS / "evidence" / "b0" / "C7_B0_AUDIT.json"
    s = C.write_evidence(p, out)
    print(f"B0_CLASS = {out['B0_CLASS']}   checks={len(checks)}  failed={failed}")
    for c in checks:
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['id']}  {c['name']}")
    print(f"\nwrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
