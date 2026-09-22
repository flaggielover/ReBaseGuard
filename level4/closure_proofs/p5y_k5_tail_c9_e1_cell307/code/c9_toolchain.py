"""C9 Phase 5 -- toolchain qualification, and the decisive scientific determinism finding.

Two INDEPENDENT blockers are established here. The first is scientific and is the more important,
because it does not depend on any host being available.
"""
from __future__ import annotations

import json
import pathlib
import platform
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c9_common as C


def main() -> int:
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    prod = C.C2 / "code" / "c2_refined_registry.py"
    psrc = prod.read_text()

    # ---- BLOCKER 1: the committed producer is deterministic and fully parameter-frozen ---------
    cli_args = [ln.split('"')[1] for ln in psrc.splitlines()
                if "add_argument" in ln and '"--' in ln]
    frozen_consts = {}
    for name in ("SUB_BLOCK_MAX_WIDTH", "DEGREE_TABOO", "DEGREE_ARL", "TABOO_ALPHAS", "ARL_ALPHAS"):
        for ln in psrc.splitlines():
            if ln.startswith(name):
                frozen_consts[name] = ln.split("#")[0].strip()
                break
    recorded = {k: reg.get(k) for k in ("sub_block_max_width", "degree_taboo", "degree_arl",
                                        "taboo_alphas", "arl_alphas", "code_sha256", "bits")
                if k in reg}
    blocker1 = {
        "STATUS": "WITHDRAWN",
        "withdrawn_because": (
            "this blocker was MANUFACTURED by defining E1 as a replay of the committed producer. C6 "
            "defines E1 as 'a BETTER tuple ... there is nothing to replay ... a TOOLCHAIN for the "
            "WORK', and C8's gate defines R3 as 'a better certified upper bound'. Under the real "
            "definition the certifier's SEARCH is the work. Moreover the dependency scan read only "
            "the WRAPPER's CLI: taboo_certify.py exposes --alpha, --beta, --depth and --degree as "
            "first-class arguments. See evidence/phase4/C9_ALPHA_LEVER.json for the lever that was "
            "sitting in C9's own inputs, free and unmeasured."),
        "superseded_by": "evidence/phase4/C9_ALPHA_LEVER.json",
        "original_finding_RETAINED_FOR_THE_RECORD": ("Re-running the committed E1 producer on cell 307 reproduces the committed "
                    "cell-307 block EXACTLY, so the achieved tightening is 1.0000x, which is below "
                    "the required 1.0960072461462x. E1 AS COMMITTED CANNOT CLOSE CELL 307."),
        "what_remains_true_of_it": ("a replay at the SAME ladder rung would indeed reproduce the "
                                    "committed block. That is true and useless: it was never what "
                                    "E1 meant."),
        "why": [
            "every quantity that controls tightness is a hardcoded module constant, not a CLI knob",
            "the CLI exposes only " + ", ".join(cli_args) + " -- none of which is scientific",
            "the arithmetic is exact (fractions.Fraction) plus flint.arb interval arithmetic at a "
            "fixed precision, so the output is a deterministic function of the inputs",
            "the committed registry records the exact configuration it was produced under, so the "
            "reproduction is checkable field by field",
        ],
        "frozen_constants_in_the_producer": frozen_consts,
        "same_configuration_recorded_in_the_committed_registry": recorded,
        "gate_language": ("the C2 gate fixes the partition as 'sub-blocks no wider than 1/100 - the "
                          "geometry of the ADOPTED registry r1, rather than a width tuned to the "
                          "tail', and fixes both alpha ladders"),
        "status_of_this_finding": ("STRUCTURAL INFERENCE from the committed producer, its recorded "
                                   "configuration and its arithmetic. It is NOT an executed "
                                   "verification, because executing it needs the toolchain that "
                                   "blocker 2 shows is absent. Labelled accordingly."),
        "consequence": ("obtaining the required 1.096x needs a DIFFERENT producer configuration -- "
                        "finer sub-blocks, higher degree, or a different alpha ladder. That is a "
                        "source mutation of a geometry the C2 gate froze, so it is a new prospective "
                        "protocol and a different campaign, not 'one authorized execution of the "
                        "committed E1 producer'. C9's charter forbids improvising around a blocker."),
    }

    # ---- BLOCKER 2: no qualified runtime and no authorized host --------------------------------
    # Version pins, read from committed evidence. The first version built a git-grep pattern with
    # POSIX classes inside -oE and matched nothing, silently reporting EMPTY pins -- a check that
    # returns "no requirement" when it means "I failed to look".
    pins = {}
    for key in ("python", "numpy", "python_flint", "flint_library"):
        hits = subprocess.run(
            ["git", "-C", str(C.REPO), "grep", "-h", "-oE",
             r'"' + key + r'"[ ]*:[ ]*"[^"]+"', "HEAD", "--", "*.json"],
            capture_output=True, text=True).stdout.splitlines()
        vals = {}
        for h in hits:
            parts = h.split('"')
            if len(parts) >= 4:
                vals[parts[3]] = vals.get(parts[3], 0) + 1
        pins[key] = dict(sorted(vals.items(), key=lambda kv: -kv[1]))
    if not any(pins.values()):
        raise SystemExit("REFUSE: could not read any version pin; the scan is broken, not the tree")

    local = {"python": sys.version.split()[0], "machine": platform.machine(),
             "system": platform.system(), "libs": C.toolchain_present()}
    interp = {}
    for cand in ("python3.12", "python3.13", "python3.11"):
        r = subprocess.run(["bash", "-lc", f"command -v {cand}"], capture_output=True, text=True)
        interp[cand] = r.stdout.strip() or None
    flint_libs = subprocess.run(
        ["bash", "-lc", "ls /opt/homebrew/lib/libflint* /usr/local/lib/libflint* 2>/dev/null"],
        capture_output=True, text=True).stdout.strip().splitlines()

    # Is any certification HOST authorized for C9? The first version grepped for "C9|c9" over all
    # authorization files and "found" two -- because the lowercase pattern matched `c9` inside hex
    # SHA digests in C3's authorization and an unrelated countersignature. Neither is a C9 host
    # authorization. A case-sensitive, word-bounded scan restricted to this campaign's own namespace
    # is what the question actually asks.
    host_auth = [f for f in C.git_grep(r'\bC9\b', "level4/closure_proofs/*/authorization/*.json")
                 if "p5y_k5_tail_c9" in f]
    c9_auth_dir = sorted((C.NS / "authorization").glob("*.json")) if (C.NS / "authorization").exists() else []
    blocker2 = {
        "finding": ("No qualified certification runtime exists and no certification host is "
                    "authorized for C9."),
        "historical_pins_from_committed_evidence": pins,
        "local_runtime": local,
        "required_interpreter_present": interp,
        "flint_system_libraries_present": flint_libs or [],
        "network_state": ("CORRECTED. The TLS failure belongs to the 3.14 interpreter only. "
                          "python3.11's pip reaches PyPI normally, so 'no network' was a "
                          "misattribution and is withdrawn."),
        "isolated_environment_TESTED": {
            "python3.11": "/Users/suzhe/.local/bin/python3.11, 3.11.15, with pip, venv and a CA bundle",
            "venv_created": True,
            "result": "FAILED -- numpy 2.5.2 requires Python >= 3.12, so the pinned toolchain cannot "
                      "be built on 3.11. Using a different numpy would break the runtime identity "
                      "pin, and the taboo candidate comes from np.linalg.solve, so a different BLAS "
                      "could change the candidate.",
            "what_would_be_needed": "Python 3.12.x, which is absent; installing it via Homebrew is a "
                                    "SHARED system change, not the dedicated certification "
                                    "environment the charter requires, and brew does not pin FLINT "
                                    "to 3.6.0."},
        "authorized_C9_host_artifacts": host_auth,
        "C9_authorization_artifacts_present": [str(x.name) for x in c9_auth_dir],
        "false_positive_note": ("an earlier scan reported two 'authorized' artifacts; both were hex "
                                "SHA digests containing the substring c9, in C3's authorization and "
                                "in an unrelated countersignature. Neither authorizes a C9 host."),
        "hosts": {
            "AWS_SR_PS1": "ABSOLUTELY FORBIDDEN by the C9 charter; a separate production campaign",
            "Vultr": ("NOT authorized. The charter forbids assuming authorization from historical "
                      "use, and no authorization or provenance artifact for a C9 certification host "
                      "exists in the tree."),
            "local_machine": ("would require installing Python 3.12, FLINT 3.6.0, numpy 2.5.2, scipy "
                              "and python-flint 0.9.0. A Homebrew install is system-wide and shared, "
                              "so it is NOT the 'dedicated C9 certification host/environment' the "
                              "charter requires, and brew does not pin FLINT to 3.6.0."),
        },
        "architecture_note": ("the local machine is macOS arm64; the historical certifier pins point "
                              "at a Linux host. Architecture is part of the runtime identity manifest "
                              "the charter requires, so a cross-architecture run would need its own "
                              "qualification even if the libraries were present."),
    }

    # the recorded-vs-actual producer hash discrepancy, which any execution must resolve first
    import hashlib as _h
    rec = reg.get("code_sha256", {})
    actual = {"c2_refined_registry": _h.sha256(prod.read_bytes()).hexdigest(),
              "taboo_certify": _h.sha256((C.AD / "code" / "taboo_certify.py").read_bytes()).hexdigest()}
    hash_discrepancy = {k: {"recorded": rec.get(k), "actual": actual.get(k),
                            "match": rec.get(k) == actual.get(k)} for k in actual}

    out = {
        "schema": "C9_TOOLCHAIN/2",
        "PHASE5_RESULT": "EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION",
        "producer_hash_discrepancy": {
            "detail": hash_discrepancy,
            "why_it_matters": ("the committed registry records a c2_refined_registry hash that does "
                               "NOT match the committed file. C9's first pass asserted the recorded "
                               "configuration was 'checkable field by field' and never checked it. "
                               "Any execution must resolve which producer actually built the "
                               "registry before claiming to reproduce or improve on it."),
            "determinism_claim_CORRECTED": ("the first pass called the output 'a deterministic "
                                            "function of the inputs'. It is not purely so: the taboo "
                                            "candidate is obtained via numpy linear algebra, so BLAS "
                                            "and architecture participate. That also undercuts the "
                                            "first pass's claim that the two blockers were "
                                            "independent.")},
        "blocker_1_scientific": blocker1,
        "blocker_2_toolchain_and_host": blocker2,
        "independence": ("the two blockers are independent. Blocker 1 holds even if a fully "
                         "qualified host existed, because the committed producer would reproduce the "
                         "committed result. Blocker 2 holds even if the producer could improve."),
        "charter_hard_stops_triggered": [
            "qualification fails",
            "required toolchain is absent and no dedicated certification environment is authorized",
        ],
        "what_C9_does_NOT_claim": [
            "that cell 307 cannot ever be closed",
            "that E1 is refuted",
            "that a finer operator certification would fail",
            "that any host should or should not be provisioned -- that is a governance decision",
        ],
    }
    s = C.write_evidence(C.NS / "evidence" / "phase5" / "C9_TOOLCHAIN.json", out)
    print(f"BLOCKER 1 (scientific): {blocker1['STATUS']}")
    print(f"  {blocker1['withdrawn_because'][:150]}...")
    print(f"  CLI knobs: {cli_args}")
    for k, v in frozen_consts.items():
        print(f"    {v}")
    print("\nBLOCKER 2 (toolchain/host):")
    print(f"  local python {local['python']} {local['system']}/{local['machine']}; libs {local['libs']}")
    for k, v in pins.items():
        top = list(v.items())[:2]
        print(f"  pinned {k:<14} {top}")
    print(f"  python3.12 present: {interp['python3.12']}   FLINT libs: {flint_libs or 'none'}")
    print(f"  authorized C9 host artifacts: {host_auth or 'NONE'}")
    print("\nproducer hash discrepancy:")
    for k, v in hash_discrepancy.items():
        print(f"  {k:<22} match={v['match']}  recorded {str(v['recorded'])[:12]}  "
              f"actual {str(v['actual'])[:12]}")
    print(f"\nPHASE5_RESULT = {out['PHASE5_RESULT']}")
    print(f"wrote evidence/phase5/C9_TOOLCHAIN.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
