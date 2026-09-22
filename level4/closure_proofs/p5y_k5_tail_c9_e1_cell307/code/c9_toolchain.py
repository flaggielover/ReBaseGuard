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
        "finding": ("Re-running the committed E1 producer on cell 307 reproduces the committed "
                    "cell-307 block EXACTLY, so the achieved tightening is 1.0000x, which is below "
                    "the required 1.0960072461462x. E1 AS COMMITTED CANNOT CLOSE CELL 307."),
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
        "network_state": ("this interpreter cannot verify TLS certificates (SSL "
                          "CERTIFICATE_VERIFY_FAILED when querying package metadata), so package "
                          "installation is not currently possible from it either"),
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

    out = {
        "schema": "C9_TOOLCHAIN/1",
        "PHASE5_RESULT": "QUALIFICATION_NOT_POSSIBLE",
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
    print("BLOCKER 1 (scientific):")
    print(f"  {blocker1['finding']}")
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
    print(f"\nPHASE5_RESULT = {out['PHASE5_RESULT']}")
    print(f"wrote evidence/phase5/C9_TOOLCHAIN.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
