"""C11R round 5 -- the end-to-end execution-integrity controls, on SYNTHETIC git repositories.

WHY. Review round 3 (blocker R3-1) broke the execution -> seal -> comparison chain; review round 4
(blocker R4-1) broke it again through git's default HISTORY SIMPLIFICATION: an edit that was used
and reverted on a side branch merged with --no-ff, and an earlier run on a merged side branch,
were invisible to `git log -- <paths>`. It also found (N4-5) that the comparator opened the
magnitudes before its G8/G10/G19 guards ran, (N4-4) that any PASS-class qualification was
accepted, and (N4-3) that a module earlier on sys.path was executed while the contract checks
passed. These controls replay those attacks against the PRODUCTION checks -- c11r_contract
(frozen_state, protocol_history, contract, gate, qualification schema, authorization, runner
pre-flight, run identity, loaded-module identity), c11r_runs.preflight,
c11r_qualify.emit_qualification and c11r_compare.execute_comparison / verify_seal -- not against
copies of them.

GROUPS
  R3*   the round-4 identity controls (R3A-R3T), kept, with exact expected reasons (N4-13);
  MHT*  merge topology (R4-1): linear, side-branch, --no-ff, `-s ours` and octopus merges, hidden
        and discarded runs, seals and comparisons; each records separately whether TREE IDENTITY
        and HISTORY PURITY flag it, and what git's default and --full-history path-limited logs
        list -- the demonstration that the defect was real and that the new check does not rely
        on either;
  LS*   loader spy (N4-5): each refusal class must refuse with the magnitude loader NOT called,
        at the step the comparator's frozen order names; only the valid chain calls it (once);
  QF*   the typed Q1-Q18 qualification schema (N4-4);
  IMP*  what a process actually LOADED (N4-3): subprocess drivers shadow modules on sys.path, by
        symlink, by an identical copy, through a zip, through PYTHONPATH and through a forged
        timestamp .pyc, and call the production verify_loaded_modules;
  ORD*  the order of qualification, authorization and seal (N4-10);
  GS*   the execution lifecycle (review 5, R5-1): permission separated from evidence, the
        runner's NEXT_STEPS followed literally, delete / recreate / revert, second execution,
        interrupted execution, comparison under DENY, malformed states;
  PYC*  sourceless bytecode and the actual origin of every load-bearing module (R5-2);
  CF*   the comparison output path and the comparator's exclusive write (N5-2, E45);
  PB*   the policy bytes the runner uses (N5-3);
  GR*   replace refs, grafts, shallow history, and a scan for any unsanitized git call (N5-4);
  DM*   target disposition from certificate semantics, the null-id demotion (N5-11);
  AC*   the approved commit as a full, immutable commit id (N5-7);
  R61*  the campaign-directory import closure (review 6, R6-1): stdlib-named sourceless,
        source, package, namespace, zip/egg, extension, symlinked and wrong-directory material in
        a SYNTHETIC repository's code directories, drivers whose execution root is that
        repository, the static inventory, the cache policy, the import-path precedence and the
        boundary programs' pre-import barrier;
  TP*   typed path refusals (N6-5): symlinks outside the repository, dangling, looping, a
        directory where a file belongs -- never an exception;
  CMP*  the comparison transaction (N6-3): a refusal writes nothing, the valid chain writes once;
  RC*   the required proving certificates (N6-4);
  CG*   the commit-graph file is not read (N6-6);
  WD*, LG*  what the lifecycle claims, and the repository-wide lineage (N6-2), with the stated
        limit reproduced as stated.

EVERY CONTROL MUST REFUSE FOR ITS EXPECTED REASON (and, for the comparator, at its expected
step): a refusal for some other reason proves nothing about its attack.

WHAT IS SYNTHETIC, and only this: the qualification carries synthetic Q1-Q18 items and
`fixture: true`, the authorization `fixture: true` (accepted only with allow_fixture=True, which
only this module passes); the certificates are c11r_compare.synthetic_certs (no certifier ran, no
value is real); the magnitude loader is a stub returning deliberately round synthetic values,
which counts its calls. The quarantine is never copied and never opened. The registry is not
copied; its content-free id in a synthetic contract is null on every side. No target computation
happens; no real qualification, authorization or runs artifact is created.
"""
from __future__ import annotations

import copy
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_compare as K
import c11r_contract as CT
import c11r_gate as GA
import c11r_qualify as Q
import c11r_runs as R

FAKE_MAGS = {"Abar": F(10), "tau": F(10), "C_T": F(10), "D_lo": F(1, 2), "D1": F(10),
             "D2": F(10)}                                    # synthetic, deliberately round
COPIED_ARTIFACTS = ("config/C11R_POLICY.json", "evidence/table/C11R_N9_STATEMENTS.json",
                    "evidence/cost/C11R_COST.json", "evidence/validation/C11R_VALIDATION.json")
FIXTURE_ITEMS = [{"id": qid, "status": "PASS", "detail": {"synthetic_fixture": True}}
                 for qid in CT.QUAL_ITEMS]
RUNS_PATH = CT.ns_path(CT.RUNS_REL)
COMPARISON_PATH = CT.ns_path(CT.COMPARISON_REL)
PERMISSION_PATH = CT.ns_path(CT.PERMISSION_REL)
AUTH_PATH = CT.ns_path(CT.AUTH_REL)
TRUNK = "trunk"


class StubLoader:
    def __init__(self):
        self.calls = 0

    def __call__(self, stmt):
        self.calls += 1
        return dict(FAKE_MAGS)


def _dump(obj) -> bytes:
    return (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode()


class Chain:
    """One synthetic repository, walked through the chain."""

    def __init__(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix="c11r_chain_"))
        assert self.root.resolve() != C.REPO.resolve()
        for a in (("init", "-q", "-b", TRUNK), ("config", "user.email", "chain@c11r.invalid"),
                  ("config", "user.name", "c11r chain controls"),
                  ("config", "commit.gpgsign", "false")):
            C.git_in(self.root, *a)
        # distinct loop names: the firewall's flow-insensitive analysis would otherwise pair the
        # code paths with the artifact reader and vice versa (review 4, N4-11)
        for code_rel in CT.closure_paths():
            self.write(code_rel, CT.code_bytes(C.REPO, code_rel))
        # every other approved source too (review 6, R6-1: the contract binds `frozen_code`, and
        # a module loaded from a campaign code directory must be one of them)
        for other_rel in CT.namespace_code():
            if not (self.root / other_rel).exists():
                self.write(other_rel, CT.code_bytes(C.REPO, other_rel))
        for art_rel in COPIED_ARTIFACTS:
            self.write(CT.ns_path(art_rel), CT.artifact_bytes(C.REPO, art_rel))
        self.stmt = CT.load_artifact(self.root, CT.STMT_REL)
        self.policy = CT.load_artifact(self.root, CT.POLICY_REL)
        self.approved = self.freeze("approved: synthetic frozen state")

    # -- plumbing -------------------------------------------------------------------------------
    def write(self, rel: str, data: bytes) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def remove(self, rel: str) -> None:
        (self.root / rel).unlink()

    def ns(self, rel: str) -> pathlib.Path:
        return self.root / C.NS_REL / rel

    def commit(self, msg: str) -> str:
        C.git_in(self.root, "add", "-A")
        C.git_in(self.root, "commit", "-q", "--allow-empty", "-m", msg)
        return C.git_in(self.root, "rev-parse", "HEAD")

    def commit_paths(self, paths: list[str], msg: str) -> str:
        """Commit EXACTLY these paths (the runner's printed instructions, followed literally)."""
        C.git_in(self.root, "add", "--", *paths)
        C.git_in(self.root, "commit", "-q", "-m", msg)
        return C.git_in(self.root, "rev-parse", "HEAD")

    def commit_object_only(self, rel: str, data: bytes | None, msg: str) -> str:
        """Commit `data` at `rel` (None: remove it) through git plumbing, WITHOUT the working
        tree: a protected-named file (a synthetic comparison artifact) is never opened here --
        the runtime open-guard refuses that, correctly, to every program but the comparator."""
        if data is None:
            C.git_in(self.root, "rm", "-q", "--cached", rel)
        else:
            oid = C.git_run(self.root, "hash-object", "-w", "--stdin", input=data,
                            text=False).stdout.decode().strip()
            C.git_in(self.root, "update-index", "--add", "--cacheinfo", f"100644,{oid},{rel}")
        C.git_in(self.root, "commit", "-q", "-m", msg)
        return C.git_in(self.root, "rev-parse", "HEAD")

    def branch(self, name: str) -> None:
        C.git_in(self.root, "checkout", "-q", "-b", name)

    def checkout(self, name: str) -> None:
        C.git_in(self.root, "checkout", "-q", name)

    def merge(self, *names: str, strategy: str | None = None) -> str:
        extra = ["-s", strategy] if strategy else []
        C.git_in(self.root, "merge", "-q", "--no-ff", "--no-edit", *extra, *names)
        return C.git_in(self.root, "rev-parse", "HEAD")

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)

    # -- the chain, with the production builders ------------------------------------------------
    def freeze(self, msg: str) -> str:
        """Build the execution contract and the gate for this repository, commit them: A."""
        C.write_evidence(self.ns(CT.CONTRACT_REL), CT.contract_body(self.root),
                         producer=CT.__file__)
        cv = CT.verify_contract(self.root)
        assert not cv["problems"], cv["problems"]
        gate = GA.build(CT.load_artifact(self.root, CT.STMT_REL),
                        CT.load_artifact(self.root, CT.POLICY_REL), cv["digest"])
        C.write_evidence(self.ns(CT.GATE_REL), gate, producer=GA.__file__)
        return self.commit(msg)

    def qualification(self, items=None, mutate=None, restamp=True) -> dict:
        q = C.evidence_body(Q.emit_qualification(self.root, items or FIXTURE_ITEMS,
                                                 approved_commit=self.approved, fixture=True),
                            producer=Q.__file__)
        if mutate:
            mutate(q)
            if restamp:
                q["sha256"] = CT.body_digest(q)
        return q

    def qualify(self, mutate=None, items=None, restamp=True) -> None:
        self.write(CT.ns_path(CT.QUAL_REL), _dump(self.qualification(items, mutate, restamp)))
        self.commit("qualification (synthetic fixture)")

    def authorize(self, approved=None, operator="synthetic-fixture", mutate=None) -> list[str]:
        """Phase 13 as the lifecycle prescribes: the authorization AND the execution permission
        GRANT, committed together in ONE commit."""
        r = CT.build_authorization(self.root, approved_commit=approved or self.approved,
                                   operator=operator, fixture=True)
        if r["problems"] and mutate is None:
            return r["problems"]
        a, grant = r["authorization"], r["permission"]
        if mutate:
            mutate(a)
            a["sha256"] = CT.body_digest(a)
            grant = CT.permission_record("GRANT", approved_commit=a.get("approved_commit"),
                                         authorization_sha256=a["sha256"], fixture=True)
        CT.write_record(self.root, CT.AUTH_REL, a)
        CT.write_record(self.root, CT.PERMISSION_REL, grant)
        self.commit("authorization + execution permission GRANT (synthetic fixture)")
        return r["problems"]

    def preflight(self) -> dict:
        pf = R.preflight(self.root, allow_fixture=True, check_processes=False)
        if not pf["problems"]:
            self.pf_identity = pf["identity"]             # the genuine identity of this chain
        return pf

    def runs_body(self, identity: dict, certs=None, mutate=None, restamp=False) -> dict:
        runs = R.assemble(policy=self.policy, stmt=self.stmt,
                          certs=certs or K.synthetic_certs(self.stmt, self.policy),
                          stop_reason=None, extra={"timings_seconds": {"x": 0.0}},
                          identity=identity)
        body = C.evidence_body(runs, producer=R.__file__)   # exactly what the runner writes
        if mutate:
            mutate(body)
            if restamp:
                body["sha256"] = CT.body_digest(body)
        return body

    def run(self, identity: dict, certs=None, mutate=None, restamp=False, seal=True) -> dict:
        """Phase 14 through the RUNNER'S OWN lifecycle functions: begin_execution (GRANT ->
        DENY/EXECUTION_STARTED before any science), the synthetic run, finish_execution (runs
        artifact + DENY/EXECUTION_COMPLETED); then, as NEXT_STEPS says, the two files are
        committed together -- the seal. The permission records are built from the chain's GENUINE
        pre-flight identity even when a control plants a foreign identity in the runs artifact."""
        body = self.runs_body(identity, certs, mutate, restamp)
        R.begin_execution(self.root, getattr(self, "pf_identity", identity))
        R.finish_execution(self.root, body)
        self.runs_body_written = body
        if seal:
            self.seal = self.commit_paths([RUNS_PATH, PERMISSION_PATH],
                                          "seal: runs artifact + DENY/EXECUTION_COMPLETED")
        return body

    def compare(self, approved=None) -> dict:
        loader = StubLoader()
        res = K.execute_comparison(self.root, approved_commit=approved or self.approved,
                                   loader=loader, allow_fixture=True)
        res["stub_loader_calls"] = loader.calls
        return res

    def edit_json(self, rel: str, change, restamp: bool) -> None:
        obj = CT.load_artifact(self.root, rel)
        change(obj)
        if restamp:
            obj["sha256"] = CT.body_digest(obj)
        self.write(CT.ns_path(rel), _dump(obj))

    def edit_code(self, name: str, suffix: bytes = b"\n# edited after the freeze\n") -> tuple:
        rel = next(r for r in CT.closure_paths() if r.endswith("/" + name))
        before = CT.code_bytes(self.root, rel)
        self.write(rel, before + suffix)
        return rel, before


# ---------------------------------------------------------------------------------------------
# recording
# ---------------------------------------------------------------------------------------------
RESULTS: list[dict] = []

# The reason each refusal must carry (a substring of one of its problems), and -- for a
# comparator refusal -- the FIRST step of the frozen order at which it must be refused. A control
# refused for some other reason, or at another step, proves nothing about its attack.
EXPECTED_REASON = {
    # R3: the round-4 identity controls
    "R3A": "touched a frozen path: it holds ['c11r_boxdata.py']",
    "R3B": "tree identity: frozen path C11R_POLICY.json differs",
    "R3C": "tree identity: frozen path C11R_N9_STATEMENTS.json differs",
    "R3D": "tree identity: frozen path N9R_GATE_C11R.json differs",
    "R3E": "qualification: execution_contract_sha256 belongs to another contract",
    "R3F": "is not the recomputed disposition 'FAIL'",
    "R3G": "authorization: execution_contract_sha256 does not match the recomputed value",
    "R3H": "runner pre-flight: c11r_runs.py is not the bound version",
    "R3I": "runner pre-flight: c11r_certificate.py is not the bound version",
    "R3J": "the policy's selected configuration is not the contract's",
    "R3K": "the policy's selected configuration is not the contract's",
    "R3L": "contract: configuration differs from the recomputed value",
    "R3M": "the runs artifact was changed after it was sealed",
    "R3N": "execution_identity.authorization_sha256 does not match",
    "R3O": "policy: stored sha256 field does not equal the recomputed body digest",
    "R3O_run": "stored sha256 does not equal its recomputed canonical body digest",
    "R3P": "policy: stored sha256 field does not equal the recomputed body digest",
    "R3P_run": "stored sha256 does not equal its recomputed canonical body digest",
    "R3Q": "touched a frozen path: it holds ['c7_gaussian.py']",
    "R3R": "qualification: execution_contract_sha256 belongs to another contract",
    "R3S": "the authorization names another approved commit than the operator supplied",
    "GUARD_real_repository": "the real runs artifact is read only by c11r_compare.py",
    "GUARD_real_repository_compare": "the real runs artifact is read only by c11r_compare.py",
    # MHT: merge topology (R4-1)
    "MHT1": "tree identity: frozen path c11r_boxdata.py differs",
    "MHT2": "touched a frozen path: it holds ['c11r_boxdata.py']",
    "MHT3": "touched a frozen path: it holds ['c11r_boxdata.py']",
    "MHT4": "holds a runs artifact other than the current one",
    "MHT4_preflight": "holds a runs artifact (a prior execution)",
    "MHT5": "the runs artifact was introduced by 2 commits",
    "MHT5_comparison": "holds a comparison artifact (a prior comparison)",
    "MHT6": "touched a frozen path: it holds ['c11r_policy.py']",
    "MHT9": "touched a frozen path: it holds ['c7_gaussian.py']",
    "MHT_octopus": "touched a frozen path: it holds ['c11r_certificate.py']",
    "MHT_S3d": "touched a frozen path: it holds ['C11R_POLICY.json']",
    "MHT_Sa": "another run was committed and discarded",
    # LS: loader spy (N4-5, N4-8)
    "LS_G8": "G8: D1: the policy does not implement it",
    "LS_G10": "G10: F_D: POINTWISE_INFEASIBLE yet sent to certification",
    "LS_G19": "G19: F_",
    "LS_DEMOTE": "reported NOT_CERTIFIED (demoted)",
    "LS_SEAL": "the runs artifact has uncommitted changes",
    "LS_CONTRACT": "tree identity: frozen path C11R_CONTRACT.json differs",
    "LS_HISTORY": "touched a frozen path: it holds ['c7_gaussian.py']",
    # QF: the typed qualification schema (N4-4)
    "QF1": "required item(s) missing: ['Q7']",
    "QF2": "duplicate item(s): ['Q12']",
    "QF3": "stored class 'PASS' is not the recomputed disposition 'FAIL'",
    "QF4": "item Q4 is bound to another execution_contract_sha256",
    "QF5": "item Q9 is bound to another approved_commit",
    "QF6": "unknown item(s) ['Q19']",
    "QF8": "required item(s) missing",
    # IMP: loaded-module identity (N4-3)
    "IMP1": "c11r_idrift.py (as module 'c11r_idrift') was loaded from another file",
    "IMP2": "c11r_idrift.py (as module 'c11r_idrift') was loaded from another file",
    "IMP4": "c11r_idrift.py (as module 'c11r_idrift') was loaded from another file",
    "IMP5": "c7_gaussian.py (as module 'c7_gaussian') was loaded from another file",
    "IMP6": "c11r_schema.py (as module 'c11r_schema') has cached bytecode that is not the "
            "compilation of its verified source",
    "IMP7": "PYTHONPATH is set",
    "IMP8": "c11r_idrift.py (as module 'c11r_idrift') is ZIP (zipimporter",
    "IMP_stray": "untracked Python source ['c11r_certificate.py']",
    # GS: the execution lifecycle (R5-1)
    "GS2": "no authorization artifact",
    "GS3": "the state is REVOKED_BEFORE_EXECUTION; stage run requires AUTHORIZED",
    "GS6": "no authorization artifact",
    "GS7": "the authorization artifact was introduced by 2 commits",
    "GS8": "the authorization artifact was introduced by 2 commits",
    "GS9": "the state is SEALED; stage run requires AUTHORIZED",
    "GS9b": "the state is EXECUTING; stage run requires AUTHORIZED",
    "GS9c": "the state is ABANDONED; stage run requires AUTHORIZED",
    "GS10": "holds the runs artifact without the DENY/EXECUTION_COMPLETED permission record",
    "GS11a": "EXECUTION_COMPLETED is bound to another runs artifact",
    "GS11b": "bound to another authorization",
    "GS11c": "no state of the frozen transition table",
    # PYC: actual loaded-module identity (R5-2)
    "PYC4": "c11r_schema.py (as module 'c11r_schema') has cached bytecode that is not the "
            "compilation of its verified source",
    "PYC5": "c11r_schema.py (as module 'c11r_schema') is SOURCELESS_BYTECODE",
    "PYC6": "c7_gaussian.py (as module 'c7_gaussian') is SOURCELESS_BYTECODE",
    "PYC7": "c11r_schema.py (as module 'c11r_schema') is SOURCELESS_BYTECODE",
    "PYC8": "c11r_schema.py (as module 'c11r_schema') is SOURCELESS_BYTECODE",
    "PYC9": "c11r_schema.py (as module 'c11r_schema') was loaded from another file",
    "PYC10": "c11r_boxdata.py is required at the runner boundary but is not loaded",
    "IMP9": "c11r_schema.py (as module 'c11r_schema') was loaded from another file",
    "PYC_R5_location": "c11r_certificate.pyc in p5y_k5_tail_c11_n9_independent_certifier/code "
                       "carries the import name of contract module c11r_certificate",
    # CF: the comparison output path (N5-2)
    "CF1": "a comparison file already exists at the comparison output path",
    "CF2": "holds a comparison artifact (a prior comparison)",
    "CF3": "holds a comparison artifact (a prior comparison)",
    "CF4": "the comparison path is a symlink",
    "CF5a": "a file already exists at the comparison output path",
    # PB: verified policy bytes (N5-3)
    "PB2": "the policy bytes in use are not the pre-flight's",
    "PB3": "a stored sha256 field does not equal the recomputed digest of the bytes in use",
    # GR: replace refs, grafts, shallow history (N5-4)
    "GR1": "touched a frozen path: it holds ['c11r_boxdata.py']",
    "GR2": "holds a runs artifact other than the current one",
    "GR3": "the runs artifact was introduced by 2 commits",
    "GR6": "a grafts file rewrites commit parentage",
    "GR7": "the repository is shallow",
    # DM: disposition follows certificate semantics (N5-11)
    "DM2": "certificates are ['F_H', 'F_K'], expected exactly ['F_D', 'F_H', 'F_K']",
    "DM3": "reported NOT_CERTIFIED (demoted)",
    # since review 6 (N6-4) the run SCHEMA refuses DM4/DM5 first, at step "run": a null
    # citation and a renamed proving certificate are shapes the frozen runner never emits; the
    # step-12 demotion rule (DM3, LS_DEMOTE) stays in force behind it
    "DM4": "target 'Abar' cites None; its frozen citation is 'F_K'",
    "DM5": "certificates are ['F_D', 'F_H', 'F_K2'], expected exactly ['F_D', 'F_H', 'F_K']",
    # AC: approved commit as a full id (N5-7)
    "AC1": "is not a full 40-hex commit id",
    "AC2": "is not a full 40-hex commit id",
    "AC4": "is not a full 40-hex commit id",
    # ORD: commit ordering (N4-10)
    "ORD1": "authorization: issued before the qualification it binds was committed",
    "ORD2": "holds a qualification artifact other than the current one",
    "ORD3": "the authorization was not committed before the seal",
    # R61: the campaign-directory import closure (review 6, R6-1)
    "R61-2": "module 'fractions' was loaded from p5y_k5_tail_c11r_n9_statement_alignment/code/"
             "fractions.pyc, inside a campaign code directory, which is not an approved contract "
             "source",
    "R61-3": "module 'ast' was loaded from p5y_k5_tail_c11_n9_independent_certifier/code/ast.pyc, "
             "inside a campaign code directory, which is not an approved contract source",
    "R61-4": "module 'fractions' was loaded from p5y_k5_tail_c11r_n9_statement_alignment/code/"
             "fractions.py, inside a campaign code directory, which is not an approved contract "
             "source",
    "R61-5": "module 'fractions' was loaded from p5y_k5_tail_c11r_n9_statement_alignment/code/"
             "fractions/__init__.py, inside a campaign code directory",
    "R61-6": "module 'fractions' was loaded from p5y_k5_tail_c11r_n9_statement_alignment/code/"
             "fractions/__init__.py, inside a campaign code directory",
    "R61-7": "module 'c11x_nsdata' is a namespace package inside a campaign code directory",
    "R61-8": "sys.path holds a repository directory that is not a campaign code directory "
             "(shadow.egg)",
    "R61-9": "module 'c11x_helper' was loaded from p5y_k5_tail_c11r_n9_statement_alignment/code/"
             "c11x_helper.py, inside a campaign code directory, which is not an approved contract "
             "source",
    "R61-9b": "the contract path of c11r_schema.py is reached through a symlink",
    "R61-11": "module 'c11_extra' was loaded from p5y_k5_tail_c11_n9_independent_certifier/code/"
              "c11_extra.py, inside a campaign code directory, which is not an approved contract "
              "source",
    "R61-14": "module 'c11r_certificate' was loaded from p5y_k5_tail_c11_n9_independent_certifier/"
              "code/c11r_certificate.py, inside a campaign code directory, which is not an "
              "approved contract source",
    "R61-15": "module 'fractions': its __file__, __spec__.origin and loader path disagree",
    "R61-16": "c11x_pkg/ in p5y_k5_tail_c11r_n9_statement_alignment/code is a directory (a package "
              "or namespace package)",
    "R61-17": "is not Python source: sourceless bytecode, extensions, archives and import "
              "metadata are refused",
    "R61-18b": "__pycache__/fractions.",
    "R61-P": "precedes the standard library and is neither a campaign code directory nor part of "
             "the interpreter",
    "R61-B": "barrier True",
    "R61-0b": "c11r_compare.py does not begin with the canonical pre-import barrier",
    # TP: typed path refusals (N6-5)
    "TP1": "c11r_schema.py is a symlink resolving OUTSIDE the repository",
    "TP1c": "c11r_schema.py is a symlink resolving OUTSIDE the repository",
    "TP2": "c11r_schema.py is a dangling symlink",
    "TP2c": "the runs artifact path is a dangling symlink",
    "TP3": "c11r_schema.py is a symlink loop",
    "TP4": "C11R_AUTHORIZATION.json is a directory",
    # CMP: the comparison transaction (N6-3)
    "CMP1": "an unexpected file under a protocol directory on disk",
    "CMP2": "the runs artifact path is a directory",
    "CMP2b": "the runs artifact is not readable JSON",
    "CMP3": "tree identity: frozen path c11r_boxdata.py differs",
    "CMP4": "POST_LOAD_FAILURE -- the loader was entered",
    "CMP4b": "POST_LOAD_FAILURE -- the comparison was computed but could not be written",
    "CMP6": "a comparison file already exists at the comparison output path",
    "CMP6b": "holds a comparison artifact (a prior comparison)",
    # RC: required proving certificates (N6-4)
    "RC2": "target 'Abar' missing 'certificate_id'",
    "RC3": "target 'Abar' cites None; its frozen citation is 'F_K'",
    "RC4": "target 'Abar' cites unknown certificate 'F_Kx'",
    "RC5": "target 'Abar' cites 'F_H'; its frozen citation is 'F_K'",
    "RC6": "value trace: Abar: ['its certificate proves nothing",
    "RC7": "certificates are ['F_D', 'F_H'], expected exactly ['F_D', 'F_H', 'F_K']",
    # LG: repository-wide lineage (N6-2)
    "LG1": "hold a runs artifact that stage run does not admit",
    "LG2": "hold a runs artifact that stage compare does not admit",
    "LG4": "hold a permission artifact that stage run does not admit",
}
EXPECTED_STEP = {
    "R3A": "complete frozen history", "R3M": "complete frozen history",
    "R3N": "run", "R3O_run": "run", "R3P_run": "run", "R3S": "approved commit",
    "MHT1": "complete frozen history", "MHT2": "complete frozen history",
    "MHT3": "complete frozen history", "MHT4": "complete frozen history",
    "MHT5": "complete frozen history", "MHT5_comparison": "complete frozen history",
    "MHT6": "complete frozen history", "MHT9": "complete frozen history",
    "MHT_octopus": "complete frozen history", "MHT_S3d": "complete frozen history",
    "MHT_Sa": "complete frozen history",
    "LS_G8": "G8", "LS_G10": "G10", "LS_G19": "G19",
    "LS_DEMOTE": "other execution-integrity predicates",
    "LS_SEAL": "complete frozen history", "LS_CONTRACT": "complete frozen history",
    "LS_HISTORY": "complete frozen history", "ORD3": "complete frozen history",
    "GS6": "approved commit", "GS7": "complete frozen history", "GS8": "complete frozen history",
    "GS10": "complete frozen history", "GS11a": "complete frozen history",
    "GS11c": "complete frozen history",
    "CF1": "complete frozen history", "CF2": "complete frozen history",
    "CF3": "complete frozen history", "CF4": "complete frozen history",
    "GR1": "complete frozen history", "GR2": "complete frozen history",
    "GR3": "complete frozen history", "GR6": "complete frozen history",
    "DM3": "other execution-integrity predicates", "DM4": "run", "DM5": "run",
    "AC1": "approved commit", "AC2": "approved commit",
    "TP1c": "complete frozen history", "TP2c": "complete frozen history",
    "CMP1": "complete frozen history", "CMP2": "complete frozen history",
    "CMP2b": "complete frozen history", "CMP3": "complete frozen history",
    "CMP6": "complete frozen history", "CMP6b": "complete frozen history",
    "RC2": "run", "RC3": "run", "RC4": "run", "RC5": "run", "RC7": "run",
    "RC6": "other execution-integrity predicates",
    "LG2": "complete frozen history"}


def record(cid, group, attack, *, expected, refused_at, refused, problems, loader_calls=0,
           step=None, extra=None, must=None):
    """`must`: further named booleans the control requires (e.g. that history purity, not tree
    identity, is what caught it)."""
    reason = EXPECTED_REASON.get(cid)
    has_reason = reason is None or any(reason in str(x) for x in (problems or []))
    want_step = EXPECTED_STEP.get(cid)
    step_ok = want_step is None or step == want_step
    must = must or {}
    if expected == "REFUSE":
        ok = refused and has_reason and step_ok and loader_calls == 0 and all(must.values())
    elif expected == "POST_LOAD_FAILURE":        # the loader WAS entered, by construction (N6-3)
        ok = refused and has_reason and all(must.values())
    else:
        ok = (not refused) and all(must.values())
    RESULTS.append({"id": cid, "group": group, "attack": attack, "expected": expected,
                    "stage": refused_at, "refused": bool(refused),
                    "expected_reason": reason, "refused_for_the_expected_reason": has_reason,
                    "expected_step": want_step, "refused_at_step": step,
                    "required": must, "pass": bool(ok), "stub_loader_calls": loader_calls,
                    "problems": [str(x)[:220] for x in (problems or [])][:10], **(extra or {})})


def refused_compare(res: dict) -> bool:
    return res["N9_VERDICT"] in ("EXECUTION_INVALID", "INDEPENDENCE_VIOLATION") and \
        res["stub_loader_calls"] == 0 and not res.get("loader_called")


def record_compare(cid, group, attack, res, *, expected="REFUSE", extra=None, must=None):
    if expected == "REFUSE":
        refused = refused_compare(res)
    else:
        refused = res["N9_VERDICT"] in ("EXECUTION_INVALID", "INDEPENDENCE_VIOLATION")
        must = dict(must or {}, loader_called_exactly_once=res["stub_loader_calls"] == 1,
                    all_twelve_steps_passed=all(s["pass"] for s in res["steps"]))
    record(cid, group, attack, expected=expected, refused_at="comparator", refused=refused,
           problems=res["identity_problems"], loader_calls=res["stub_loader_calls"],
           step=res.get("refused_at"),
           extra=dict(extra or {}, verdict=res["N9_VERDICT"],
                      steps_failed=[s["name"] for s in res["steps"]
                                    if s["evaluated"] and not s["pass"]],
                      steps_not_evaluated=[s["name"] for s in res["steps"]
                                           if not s["evaluated"]]),
           must=must)


def history_views(ch: Chain) -> dict:
    """The two properties SEPARATELY (production frozen_state), and -- as a demonstration only --
    what git's path-limited logs list (the round-4 method and its --full-history variant)."""
    fs = CT.frozen_state(ch.root, ch.approved)
    paths = CT.frozen_paths(CT.contract_at(ch.root, ch.approved))
    rng = f"{ch.approved}..HEAD"
    # exactly the round-4 methods: verify_frozen_at's `git log A..HEAD -- <frozen paths>` and
    # verify_seal's `git log -- <runs path>`; and their --full-history variants
    default = C.git_in(ch.root, "log", "--format=%H", rng, "--", *paths).split()
    full = C.git_in(ch.root, "log", "--full-history", "--format=%H", rng, "--", *paths).split()
    seal4 = C.git_in(ch.root, "log", "--format=%H", "--", RUNS_PATH).split()
    seal_full = C.git_in(ch.root, "log", "--full-history", "--format=%H", "--", RUNS_PATH).split()
    return {"tree_identity_flags": bool(fs["tree_identity"]),
            "history_purity_flags": bool(fs["history_purity"]),
            "commits_checked": fs["commits_checked"],
            "merge_commits_in_range": len(C.git_in(ch.root, "rev-list", "--merges", rng).split()),
            "default_path_limited_git_log_lists": len(default),
            "full_history_path_limited_git_log_lists": len(full),
            "round4_seal_log_lists": len(seal4),
            "full_history_seal_log_lists": len(seal_full)}


# ---------------------------------------------------------------------------------------------
# R3: the round-4 identity controls
# ---------------------------------------------------------------------------------------------
def full_valid(ch: Chain, *, extra_commit=False) -> dict:
    ch.qualify()
    assert not ch.authorize(), "the synthetic chain did not authorize"
    pf = ch.preflight()
    assert not pf["problems"], pf["problems"]
    if extra_commit:
        ch.write("notes/UNRELATED.md", b"a file outside every frozen path\n")
        ch.commit("unrelated commit between approval and seal")
    ch.run(pf["identity"])
    return ch.compare()


def c_R3T():
    ch = Chain()
    try:
        record_compare("R3T", "R3", "all identities correct: the synthetic path runs to a verdict",
                       full_valid(ch), expected="ACCEPT")
    finally:
        ch.cleanup()


def c_unrelated():
    ch = Chain()
    try:
        record_compare("R3T_unrelated", "R3", "an unrelated commit (no frozen path) between "
                                              "approval and seal",
                       full_valid(ch, extra_commit=True), expected="ACCEPT")
    finally:
        ch.cleanup()


def c_R3A():
    """R3's exact attack: certifier edited -> committed -> used -> reverted before the seal."""
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        rel, before = ch.edit_code("c11r_boxdata.py")
        ch.commit("edit the sub-solution certifier")
        at_edit = ch.preflight()
        edited_sha = C.sha256_bytes(CT.code_bytes(ch.root, rel))
        certs = K.synthetic_certs(ch.stmt, ch.policy)
        certs["F_D"]["certifier"]["module_sha256"] = edited_sha      # what the edited run records
        certs["F_D"]["input_digest"] = R.CV.input_digest(certs["F_D"]["weight"],
                                                           certs["F_D"]["inputs"],
                                                           certs["F_D"]["certifier"])
        ch.run(pf["identity"], certs=certs)
        ch.write(rel, before)
        ch.commit("revert the certifier")
        record_compare("R3A", "R3", "certifier edited -> committed -> used -> reverted before the "
                                    "seal", ch.compare(),
                       extra={"runner_preflight_at_the_edit_refused": bool(at_edit["problems"])},
                       must={"runner_preflight_at_the_edit_refused": bool(at_edit["problems"])})
    finally:
        ch.cleanup()


def _authorize_after(change, cid, attack, group="R3"):
    ch = Chain()
    try:
        ch.qualify()
        change(ch)
        probs = ch.authorize()
        record(cid, group, attack, expected="REFUSE", refused_at="authorization",
               refused=bool(probs), problems=probs)
    finally:
        ch.cleanup()


def c_R3B():
    def change(ch):                      # R3's exact attack: depth 6/128, cap 10^6, sha field kept
        ch.edit_json(CT.POLICY_REL, lambda o: (o["configuration"]["chosen"].update(depth=6,
                                                                                  panels=128),
                                               o["configuration"].update(cap_seconds=10 ** 6)),
                     restamp=False)
    _authorize_after(change, "R3B", "policy edited in place after the freeze (sha256 field kept)")


def c_R3C():
    _authorize_after(lambda ch: ch.edit_json(CT.STMT_REL, lambda o: o.update(
        note="edited after the freeze"), restamp=False), "R3C",
        "statement-semantics artifact edited after the freeze")


def c_R3D():
    _authorize_after(lambda ch: ch.edit_json(CT.GATE_REL, lambda o: o["predicates"].update(
        G8_six_targets_dispositioned_consistently="weakened"), restamp=True), "R3D",
        "gate artifact edited after the freeze (re-stamped)")


def c_R3E():
    ch = Chain()
    try:
        ch.qualify(mutate=lambda q: q["bound"].update(execution_contract_sha256="0" * 64))
        probs = ch.authorize()
        record("R3E", "R3", "qualification bound to a different contract", expected="REFUSE",
               refused_at="authorization", refused=bool(probs), problems=probs)
    finally:
        ch.cleanup()


def c_R3F():
    ch = Chain()
    try:
        items = [dict(i, status="FAIL") if i["id"] == "Q5" else i for i in FIXTURE_ITEMS]
        ch.qualify(items=items, mutate=lambda q: q.update(QUALIFICATION_CLASS="PASS"))
        probs = ch.authorize()
        ch2 = Chain()
        ch2.qualify(mutate=lambda q: q.update(produces_target_constants=True), restamp=False)
        probs2 = ch2.authorize()
        ch2.cleanup()
        record("R3F", "R3", "qualification PASS forged over a failing item (re-stamped); and a "
                            "body edited without re-stamping", expected="REFUSE",
               refused_at="authorization", refused=bool(probs), problems=probs + probs2,
               must={"unstamped_body_edit_refused": any(
                   "qualification: stored sha256" in x for x in probs2)})
    finally:
        ch.cleanup()


def _preflight_after(change, cid, attack, *, auth_mutate=None, group="R3"):
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize(mutate=auth_mutate)
        if change:
            change(ch)
            ch.commit(f"{cid}: change after authorization")
        pf = ch.preflight()
        record(cid, group, attack, expected="REFUSE", refused_at="runner pre-flight",
               refused=bool(pf["problems"]), problems=pf["problems"])
    finally:
        ch.cleanup()


def c_R3G():
    _preflight_after(None, "R3G", "authorization bound to a different contract",
                     auth_mutate=lambda a: a.update(execution_contract_sha256="1" * 64))


def c_R3H():
    _preflight_after(lambda ch: ch.edit_code("c11r_runs.py"), "R3H",
                     "runner code changed after authorization")


def c_R3I():
    _preflight_after(lambda ch: ch.edit_code("c11r_certificate.py"), "R3I",
                     "certificate reconstruction module changed after authorization")


def _consistent_policy_edit(ch, change, commit=True):
    obj = CT.load_artifact(ch.root, CT.POLICY_REL)
    before = CT.artifact_bytes(ch.root, CT.POLICY_REL)
    change(obj)
    C.write_evidence(ch.ns(CT.POLICY_REL), {k: v for k, v in obj.items()
                                            if k not in ("sha256", "provenance")},
                     producer=pathlib.Path(C.HERE / "c11r_policy.py"))
    if commit:
        ch.commit("a consistently re-stamped policy after the freeze")
    return before


def c_R3JKL():
    for cid, attack, change in (
            ("R3J", "selected depth changed (policy re-stamped)",
             lambda o: o["configuration"]["chosen"].update(depth=6)),
            ("R3K", "selected panel count changed (policy re-stamped)",
             lambda o: o["configuration"]["chosen"].update(panels=16)),
            ("R3L", "resource-cap policy changed (policy re-stamped)",
             lambda o: o["configuration"].update(cap_seconds=10 ** 6))):
        _authorize_after(lambda ch, c=change: _consistent_policy_edit(ch, c), cid, attack)


def _compare_after(cid, attack, run_mutate=None, after_seal=None, identity_change=None,
                   restamp=False, certs=None, group="R3"):
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        ident = dict(pf["identity"])
        if identity_change:
            identity_change(ch, ident)
        ch.run(ident, certs=certs(ch) if certs else None, mutate=run_mutate, restamp=restamp)
        if after_seal:
            after_seal(ch)
        record_compare(cid, group, attack, ch.compare())
    finally:
        ch.cleanup()


def c_R3M():
    def after(ch):
        obj = copy.deepcopy(ch.runs_body_written)
        obj["targets"]["Abar"]["value"] = "7"
        obj["sha256"] = CT.body_digest(obj)
        ch.write(RUNS_PATH, _dump(obj))
        ch.commit("re-seal an edited runs artifact")
    _compare_after("R3M", "run artifact body changed after execution and re-committed",
                   after_seal=after)


def c_R3N():
    def other_auth(ch, ident):
        a2 = CT.build_authorization(ch.root, approved_commit=ch.approved,
                                    operator="another synthetic run", fixture=True)
        ident["authorization_sha256"] = a2["authorization"]["sha256"]
    _compare_after("R3N", "seal copied from another synthetic run (another authorization)",
                   identity_change=other_auth)


def c_R3O():
    _authorize_after(lambda ch: ch.edit_json(CT.POLICY_REL, lambda o: o.update(sha256="2" * 64),
                                             restamp=False), "R3O",
                     "stored hash field changed while the body is unchanged (policy)")
    _compare_after("R3O_run", "stored hash field changed while the body is unchanged (runs)",
                   run_mutate=lambda o: o.update(sha256="3" * 64))


def c_R3P():
    _authorize_after(lambda ch: ch.edit_json(CT.POLICY_REL, lambda o: o.update(
        status="edited body, stored hash untouched"), restamp=False), "R3P",
        "stored hash field unchanged while the body changes (policy)")
    _compare_after("R3P_run", "stored hash field unchanged while the body changes (runs)",
                   run_mutate=lambda o: o["targets"]["tau"].update(value="1"))


def c_R3Q():
    def change(ch):
        ch.edit_code("c7_gaussian.py")
        ch.commit("a transitive helper changes; no top-level producer does")
    _authorize_after(change, "R3Q", "one transitive helper changed (c7_gaussian.py)")


def _refreeze(ch) -> str:
    """A LEGITIMATE re-freeze: a new policy, then a new contract and gate, committed as A2."""
    _consistent_policy_edit(ch, lambda o: o["configuration"]["chosen"].update(panels=64))
    ch.policy = CT.load_artifact(ch.root, CT.POLICY_REL)
    return ch.freeze("approved: re-frozen with a replaced policy")


def c_R3R():
    ch = Chain()
    try:
        ch.qualify()                                  # qualified under contract 1
        a2 = _refreeze(ch)
        probs = ch.authorize(approved=a2)             # the old qualification is now stale
        record("R3R", "R3", "qualification stale after a legitimate policy replacement and "
                            "re-freeze", expected="REFUSE", refused_at="authorization",
               refused=bool(probs), problems=probs)
    finally:
        ch.cleanup()


def c_R3S():
    ch = Chain()
    try:
        a1 = ch.approved
        a2 = _refreeze(ch)
        ch.approved = a2
        ch.qualify()
        ch.authorize(approved=a2)
        pf = ch.preflight()
        ch.run(pf["identity"])
        wrong = ch.compare(approved=a1)               # the operator's root of trust is A1
        right = ch.compare(approved=a2)
        ok_right = right["N9_VERDICT"] != "EXECUTION_INVALID" and right["stub_loader_calls"] == 1
        record_compare("R3S", "R3", "comparator invoked against a valid-looking seal from the "
                                    "wrong contract", wrong,
                       extra={"the_same_chain_under_its_own_contract_is_accepted": ok_right},
                       must={"the_same_chain_under_its_own_contract_is_accepted": ok_right})
    finally:
        ch.cleanup()


def c_real_repository_guard():
    """The comparator's real-repository path is unreachable from any program but Phase 15."""
    for cid, call in (("GUARD_real_repository",
                       lambda ld: K.verify_seal(C.REPO, approved_commit="HEAD")),
                      ("GUARD_real_repository_compare",
                       lambda ld: K.execute_comparison(C.REPO, approved_commit="HEAD",
                                                       loader=ld))):
        loader = StubLoader()
        try:
            call(loader)
            refused, why = False, []
        except PermissionError as e:
            refused, why = True, [str(e)]
        record(cid, "R3", "a non-comparator program calls the comparator's seal / full path on "
                          "the REAL repository", expected="REFUSE", refused_at="runtime guard",
               refused=refused, problems=why, loader_calls=loader.calls)


# ---------------------------------------------------------------------------------------------
# MHT: merge topology (review 4, R4-1)
# ---------------------------------------------------------------------------------------------
def _side_edit_revert(ch: Chain, name: str, branch: str = "side") -> None:
    ch.branch(branch)
    rel, before = ch.edit_code(name)
    ch.commit(f"{branch}: edit {name} (used here)")
    ch.write(rel, before)
    ch.commit(f"{branch}: revert {name}")
    ch.checkout(TRUNK)


def _trunk_moves(ch: Chain, tag: str) -> None:
    ch.write(f"notes/{tag}.md", f"trunk moves on ({tag})\n".encode())
    ch.commit(f"trunk: unrelated ({tag})")


def _mht(cid, attack, topology, *, expected="REFUSE", must_views=None, preflight_cid=None):
    """qualify -> authorize -> pre-flight (the identity the run uses) -> TOPOLOGY -> [pre-flight
    again] -> run and seal on the trunk -> compare. The run carries NO trace of the topology in
    any recorded field: only the history checks can see it."""
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        assert not pf["problems"], pf["problems"]
        topology(ch, pf)
        if preflight_cid:
            again = ch.preflight()
            record(preflight_cid, "MHT", attack + " -- at the runner pre-flight",
                   expected="REFUSE", refused_at="runner pre-flight",
                   refused=bool(again["problems"]), problems=again["problems"])
        ch.run(pf["identity"])
        views = history_views(ch)
        must = {k: views[k] == v for k, v in (must_views or {}).items()}
        record_compare(cid, "MHT", attack, ch.compare(), expected=expected, extra=views,
                       must=must)
    finally:
        ch.cleanup()


def c_MHT():
    def mht1(ch, pf):
        ch.edit_code("c11r_boxdata.py")
        ch.commit("edit a certifier, never reverted")

    def mht2(ch, pf):
        rel, before = ch.edit_code("c11r_boxdata.py")
        ch.commit("edit a certifier")
        ch.write(rel, before)
        ch.commit("revert it")

    def mht3(ch, pf):
        _side_edit_revert(ch, "c11r_boxdata.py")
        _trunk_moves(ch, "mht3")
        ch.merge("side")

    def mht4(ch, pf):
        ch.branch("side")
        other = K.synthetic_certs(ch.stmt, ch.policy, A_K=F(2222, 100))
        ch.write(RUNS_PATH, _dump(ch.runs_body(pf["identity"], certs=other)))
        ch.commit("side: an earlier run")
        ch.remove(RUNS_PATH)
        ch.commit("side: discard it")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "mht4")
        ch.merge("side")

    def mht5(ch, pf):
        body = ch.runs_body(pf["identity"])               # the SAME bytes the trunk will seal
        ch.branch("side")
        ch.write(RUNS_PATH, _dump(body))
        ch.commit("side: an earlier seal of the same run")
        ch.remove(RUNS_PATH)
        ch.commit("side: delete it")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "mht5")
        ch.merge("side")

    def mht5c(ch, pf):
        ch.branch("side")
        ch.commit_object_only(COMPARISON_PATH, _dump({"synthetic": "a prior comparison"}),
                              "side: a comparison")
        ch.commit_object_only(COMPARISON_PATH, None, "side: delete it")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "mht5c")
        ch.merge("side")

    def mht6(ch, pf):
        ch.branch("side")
        ch.edit_code("c11r_policy.py")
        ch.commit("side: edit the policy producer, never reverted")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "mht6")
        ch.merge("side", strategy="ours")             # the final tree discards the side's bytes

    def mht7(ch, pf):
        ch.branch("side")
        ch.commit("side: an empty commit")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "mht7")
        ch.merge("side")

    def mht8(ch, pf):
        ch.branch("side")
        ch.write("level4/closure_proofs/another_campaign/NOTES.md", b"outside every frozen path\n")
        ch.write("docs/UNRELATED.md", b"outside the namespace\n")
        ch.commit("side: unrelated files")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "mht8")
        ch.merge("side")

    def mht9(ch, pf):
        _side_edit_revert(ch, "c7_gaussian.py")
        _trunk_moves(ch, "mht9")
        ch.merge("side")

    def mht10(ch, pf):
        _trunk_moves(ch, "mht10")

    def octopus(ch, pf):
        _side_edit_revert(ch, "c11r_certificate.py", "s1")
        for b in ("s2", "s3"):
            ch.branch(b)
            ch.write(f"notes/{b}.md", b"harmless\n")
            ch.commit(f"{b}: harmless")
            ch.checkout(TRUNK)
        ch.merge("s1", "s2", "s3")

    def s3d(ch, pf):
        ch.branch("side")
        before = _consistent_policy_edit(ch, lambda o: o["configuration"]["chosen"].update(
            panels=16))
        ch.write(CT.ns_path(CT.POLICY_REL), before)
        ch.commit("side: restore the policy")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "s3d")
        ch.merge("side")

    def sa(ch, pf):
        other = K.synthetic_certs(ch.stmt, ch.policy, A_K=F(2222, 100))
        ch.write(RUNS_PATH, _dump(ch.runs_body(pf["identity"], certs=other)))
        ch.commit("an earlier run, sealed")
        ch.remove(RUNS_PATH)
        ch.commit("the earlier run discarded (a retry)")

    both = {"tree_identity_flags": True, "history_purity_flags": True}
    purity_only = {"tree_identity_flags": False, "history_purity_flags": True}
    hidden = dict(purity_only, default_path_limited_git_log_lists=0)
    clean = {"tree_identity_flags": False, "history_purity_flags": False}
    _mht("MHT1", "linear frozen-file edit, never reverted", mht1, must_views=both)
    _mht("MHT2", "linear frozen-file edit, then revert", mht2, must_views=purity_only)
    _mht("MHT3", "side branch: edit -> use -> revert; no-ff merge", mht3, must_views=hidden)
    seal_hidden = dict(clean, round4_seal_log_lists=1)   # round 4 saw ONE seal commit: accepted
    _mht("MHT4", "side branch: a run artifact -> delete -> merge (an earlier, discarded "
                 "execution)", mht4, must_views=seal_hidden, preflight_cid="MHT4_preflight")
    _mht("MHT5", "side branch: the SAME sealed run artifact -> delete -> merge, then sealed "
                 "again", mht5, must_views=seal_hidden)
    _mht("MHT5_comparison", "side branch: a comparison artifact -> delete -> merge", mht5c,
         must_views=clean)
    _mht("MHT6", "`-s ours` merge: the final bytes equal the approved bytes, the merged history "
                 "holds a mutation", mht6, must_views=hidden)
    _mht("MHT7", "a clean no-ff merge that never touches a frozen path", mht7, expected="ACCEPT",
         must_views=clean)
    _mht("MHT8", "a merged branch mutating only files outside the frozen namespace", mht8,
         expected="ACCEPT", must_views=clean)
    _mht("MHT9", "side branch: transitive helper c7_gaussian.py edited -> reverted; merged",
         mht9, must_views=hidden)
    _mht("MHT10", "a valid, clean linear history", mht10, expected="ACCEPT", must_views=clean)
    _mht("MHT_octopus", "octopus merge of three branches, one of which edited and reverted a "
                        "certificate module", octopus, must_views=hidden)
    _mht("MHT_S3d", "side branch: the policy consistently re-stamped, then restored; merged", s3d,
         must_views=hidden)
    _mht("MHT_Sa", "linear retry: a run sealed, discarded, and another run sealed", sa,
         must_views=clean)


# ---------------------------------------------------------------------------------------------
# LS: the magnitude loader is reached only by a valid chain (review 4, N4-5 and N4-8)
# ---------------------------------------------------------------------------------------------
def c_LS():
    def other_depth(ch):
        other = copy.deepcopy(ch.policy)
        chosen = other["configuration"]["chosen"]
        other["configuration"]["chosen"] = dict(chosen, depth=chosen["depth"] + 1)
        return K.synthetic_certs(ch.stmt, other)

    _compare_after("LS_G8", "G8 fails (a not-implemented constant reported NOT_CERTIFIED); "
                            "everything else valid",
                   run_mutate=lambda o: o["targets"]["D1"].update(status="NOT_CERTIFIED"),
                   restamp=True, group="LS")
    _compare_after("LS_G10", "G10 fails (a POINTWISE_INFEASIBLE certificate sent on)",
                   run_mutate=lambda o: o["certificates"]["F_D"].update(
                       screen_classification="POINTWISE_INFEASIBLE"),
                   restamp=True, group="LS")
    _compare_after("LS_G19", "G19 fails (internally consistent certificates at another depth)",
                   certs=other_depth, group="LS")
    _compare_after("LS_DEMOTE", "a target demoted to NOT_CERTIFIED although its certificate "
                                "proves it (N4-8)",
                   run_mutate=lambda o: o["targets"]["Abar"].update(status="NOT_CERTIFIED"),
                   restamp=True, group="LS")

    def bad_seal(ch):
        body = copy.deepcopy(ch.runs_body_written)
        body["timings_seconds"] = {"x": 1.0}
        body["sha256"] = CT.body_digest(body)
        ch.write(RUNS_PATH, _dump(body))              # changed on disk, never committed
    _compare_after("LS_SEAL", "bad seal: the sealed runs artifact changed on disk afterwards",
                   after_seal=bad_seal, group="LS")

    def bad_contract(ch):
        ch.edit_json(CT.CONTRACT_REL, lambda o: o["configuration"].update(cap_seconds=10 ** 6),
                     restamp=True)
    _compare_after("LS_CONTRACT", "bad contract: the contract edited (re-stamped) after the seal",
                   after_seal=bad_contract, group="LS")

    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        _side_edit_revert(ch, "c7_gaussian.py")
        _trunk_moves(ch, "ls")
        ch.merge("side")
        ch.run(pf["identity"])
        record_compare("LS_HISTORY", "LS", "bad history: a side-branch edit and revert, merged",
                       ch.compare())
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        record_compare("LS_VALID", "LS", "the valid chain: the only case that may reach the "
                                         "loader", full_valid(ch), expected="ACCEPT")
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# QF: the typed Q1-Q18 qualification schema (review 4, N4-4)
# ---------------------------------------------------------------------------------------------
def c_QF():
    def items_without(qid):
        return [i for i in FIXTURE_ITEMS if i["id"] != qid]

    def one_item(qid, change):
        def m(q):
            for i in q["items"]:
                if i["id"] == qid:
                    change(i)
        return m

    cases = (
        ("QF1", "missing Q7", dict(items=items_without("Q7"))),
        ("QF2", "duplicate Q12", dict(items=FIXTURE_ITEMS + [dict(FIXTURE_ITEMS[11])])),
        ("QF3", "forged overall PASS with one failing item (re-stamped)",
         dict(items=[dict(i, status="FAIL") if i["id"] == "Q3" else i for i in FIXTURE_ITEMS],
              mutate=lambda q: q.update(QUALIFICATION_CLASS="PASS"))),
        ("QF4", "wrong contract on one item (re-stamped)",
         dict(mutate=one_item("Q4", lambda i: i["bound"].update(
             execution_contract_sha256="4" * 64)))),
        ("QF5", "wrong approved commit on one item (re-stamped)",
         dict(mutate=one_item("Q9", lambda i: i["bound"].update(approved_commit="5" * 40)))),
        ("QF6", "unknown extra item Q19 (frozen rule: REFUSE)",
         dict(items=FIXTURE_ITEMS + [{"id": "Q19", "status": "PASS", "detail": {}}])),
        ("QF8", "R4's demonstration: a PASS-class qualification with one arbitrary item",
         dict(items=[{"id": "FX1", "status": "PASS", "detail": {}}])),
    )
    for cid, attack, kw in cases:
        ch = Chain()
        try:
            ch.qualify(**kw)
            probs = ch.authorize()
            record(cid, "QF", attack, expected="REFUSE", refused_at="authorization",
                   refused=bool(probs), problems=probs)
        finally:
            ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        probs = ch.authorize()
        q = CT.load_artifact(ch.root, CT.QUAL_REL)
        d = CT.qualification_disposition(q["items"], CT.item_binding(CT.chain_roots(ch.root),
                                                                     ch.approved))
        record("QF7", "QF", "a valid Q1-Q18 qualification", expected="ACCEPT",
               refused_at="authorization", refused=bool(probs), problems=probs,
               must={"exactly_Q1_to_Q18": [i["id"] for i in q["items"]] == list(CT.QUAL_ITEMS),
                     "recomputed_disposition_PASS": d["disposition"] == "PASS"})
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# IMP: what a process actually LOADED (review 4, N4-3)
# ---------------------------------------------------------------------------------------------
DRIVER = r'''
import json, os, sys
cfg = json.loads(sys.argv[1])
# as a boundary program would be: its own directory is not on sys.path (review 6, R6-1, L3)
_me = os.path.dirname(os.path.realpath(__file__))
sys.path[:] = [p for p in sys.path if os.path.realpath(p or ".") != _me]
if cfg.get("pycache_prefix"):
    sys.pycache_prefix = cfg["pycache_prefix"]
sys.path.insert(0, cfg["code"])
for d in cfg["shadow_dirs"]:
    sys.path.insert(0, d)
for m in cfg["preload"]:
    __import__(m)
sys.path.insert(0, cfg["code"])
for m in cfg.get("imports", ["c11r_idrift"]):
    __import__(m)
import c11r_contract as CT
import c11r_common as C
res = CT.verify_loaded_modules(CT.contract_body(C.REPO), role=cfg.get("role"))
res["forged_code_ran"] = bool(getattr(sys.modules.get("c11r_schema"), "C11R_FORGED_BYTECODE",
                                      False))
res["files"] = {m: getattr(sys.modules.get(m), "__file__", None) for m in cfg["report"]}
print(json.dumps(res))
'''


def _driver(tmp: pathlib.Path, *, shadow_dirs=(), preload=(), pycache_prefix=None, env=None,
            no_write=False, imports=None, role=None):
    drv = tmp / "imp_driver.py"
    drv.write_text(DRIVER)
    cfg = {"code": str(C.HERE), "shadow_dirs": [str(d) for d in shadow_dirs],
           "preload": list(preload), "pycache_prefix": pycache_prefix,
           "imports": list(imports) if imports is not None else ["c11r_idrift"], "role": role,
           "report": ["c11r_idrift", "c7_gaussian", "c11r_schema"]}
    e = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    e.update(env or {})
    r = subprocess.run([sys.executable, *(["-B"] if no_write else []), str(drv), json.dumps(cfg)],
                       capture_output=True, text=True, env=e, cwd=str(tmp))
    if r.returncode != 0:
        return {"problems": [f"driver failed: {r.stderr.strip()[-300:]}"], "checked": [],
                "driver_failed": True}
    return json.loads(r.stdout.strip().splitlines()[-1])


def c_IMP():
    idrift = (C.HERE / "c11r_idrift.py").read_bytes()
    gauss_rel = next(r for r in CT.closure_paths() if r.endswith("/c7_gaussian.py"))
    gauss = CT.code_bytes(C.REPO, gauss_rel)
    schema_src = (C.HERE / "c11r_schema.py").read_bytes()

    def one(cid, attack, setup, *, expected="REFUSE", must=None, group="IMP"):
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="impctl_"))
        try:
            kw = setup(tmp) or {}
            res = _driver(tmp, **kw)
            probs = res["problems"]
            m = dict(must(res, tmp) if must else {}, driver_ran=not res.get("driver_failed"))
            record(cid, group, attack, expected=expected, refused_at="loaded-module identity",
                   refused=bool(probs), problems=probs, must=m,
                   extra={"modules_checked": res.get("checked"), "files": res.get("files")})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def stray(tmp):
        d = tmp / "stray"
        d.mkdir()
        (d / "c11r_idrift.py").write_bytes(idrift + b"\n# a stray, edited copy\n")
        return {"shadow_dirs": [d], "preload": ["c11r_idrift"]}

    def symlinked(tmp):
        ext = tmp / "external"
        ext.mkdir()
        (ext / "alt_idrift.py").write_bytes(idrift)
        d = tmp / "links"
        d.mkdir()
        (d / "c11r_idrift.py").symlink_to(ext / "alt_idrift.py")
        return {"shadow_dirs": [d], "preload": ["c11r_idrift"]}

    def same_bytes(tmp):
        d = tmp / "copy"
        d.mkdir()
        (d / "c11r_idrift.py").write_bytes(idrift)
        return {"shadow_dirs": [d], "preload": ["c11r_idrift"]}

    def helper(tmp):
        d = tmp / "helper"
        d.mkdir()
        (d / "c7_gaussian.py").write_bytes(gauss + b"\n# a shadowing helper\n")
        return {"shadow_dirs": [d], "preload": ["c7_gaussian"]}

    def forged_pyc(tmp):
        import importlib._bootstrap_external as BE
        import importlib.util as U
        prefix = tmp / "pycache"
        src = C.HERE / "c11r_schema.py"
        st = src.stat()
        old = sys.pycache_prefix
        sys.pycache_prefix = str(prefix)
        try:
            target = pathlib.Path(U.cache_from_source(str(src)))
        finally:
            sys.pycache_prefix = old
        forged = compile(schema_src + b"\nC11R_FORGED_BYTECODE = True\n", str(src), "exec",
                         dont_inherit=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes(BE._code_to_timestamp_pyc(forged, int(st.st_mtime),
                                                           st.st_size)))
        return {"pycache_prefix": str(prefix)}

    def stale_pyc(tmp):
        # a cache the loader must IGNORE: a different code object under a header whose mtime does
        # not match the source -- CPython recompiles from source, so nothing foreign ran
        import importlib._bootstrap_external as BE
        import importlib.util as U
        prefix = tmp / "pycache"
        src = C.HERE / "c11r_schema.py"
        st = src.stat()
        old = sys.pycache_prefix
        sys.pycache_prefix = str(prefix)
        try:
            target = pathlib.Path(U.cache_from_source(str(src)))
        finally:
            sys.pycache_prefix = old
        other = compile(schema_src + b"\nC11R_FORGED_BYTECODE = True\n", str(src), "exec",
                        dont_inherit=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes(BE._code_to_timestamp_pyc(other, int(st.st_mtime) - 1,
                                                           st.st_size)))
        return {"pycache_prefix": str(prefix), "no_write": True}

    def pythonpath(tmp):
        return {"env": {"PYTHONPATH": str(tmp / "nothing_here")}}

    def zipped(tmp):
        import zipfile
        z = tmp / "shadow.zip"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("c11r_idrift.py", idrift)
        return {"shadow_dirs": [z], "preload": ["c11r_idrift"]}

    one("IMP1", "a stray same-name module earlier on sys.path", stray)
    one("IMP2", "a symlinked alternate module (an external file of identical bytes)", symlinked)
    one("IMP3", "the correct modules from the contract paths", lambda t: {}, expected="ACCEPT",
        must=lambda r, t: {"non_vacuous": {"c11r_idrift.py", "c11r_contract.py", "c11r_schema.py",
                                           "c7_gaussian.py"} <= set(r.get("checked") or [])})
    one("IMP4", "identical bytes at a wrong path (not allowed by the contract)", same_bytes)
    one("IMP5", "a transitive helper (c7_gaussian.py) shadowed", helper)
    one("IMP6", "a forged timestamp .pyc (matching mtime and size) for c11r_schema", forged_pyc,
        must=lambda r, t: {"the_forged_code_really_ran": r.get("forged_code_ran") is True})
    one("IMP6b", "a STALE .pyc (header mtime does not match) that the loader ignores: no false "
                 "refusal", stale_pyc, expected="ACCEPT",
        must=lambda r, t: {"the_stale_code_did_not_run": r.get("forged_code_ran") is False})
    one("IMP7", "PYTHONPATH set in the environment", pythonpath)
    one("IMP8", "a zip archive earlier on sys.path", zipped)

    # ---- PYC: sourceless bytecode and the actual origin of every load-bearing module (R5-2)
    import py_compile

    def sourceless(tmp, module, source, *, symlink=False):
        d = tmp / "shadow"
        d.mkdir()
        src = tmp / f"src_{module}.py"
        src.write_bytes(source)
        if symlink:
            ext = tmp / "external"
            ext.mkdir()
            py_compile.compile(str(src), cfile=str(ext / f"alt_{module}.pyc"), doraise=True)
            (d / f"{module}.pyc").symlink_to(ext / f"alt_{module}.pyc")
        else:
            py_compile.compile(str(src), cfile=str(d / f"{module}.pyc"), doraise=True)
        return {"shadow_dirs": [d], "preload": [module], "no_write": True}

    def cached_prefix(tmp):
        # an ORDINARY CPython cache for the correct sources: a first run writes it, the checked
        # run (with -B) then loads from it
        _driver(tmp, pycache_prefix=str(tmp / "pycache"))
        return {"pycache_prefix": str(tmp / "pycache"), "no_write": True}

    def cache_ok(r, tmp):
        import importlib.util as U
        old = sys.pycache_prefix
        sys.pycache_prefix = str(tmp / "pycache")
        try:
            cached = U.cache_from_source(str(C.HERE / "c11r_schema.py"))
        finally:
            sys.pycache_prefix = old
        return {"an_accepted_cache_existed": CT._pyc_matches_source(
            cached, schema_src, str(C.HERE / "c11r_schema.py")) is True}

    def package_dir(tmp):
        d = tmp / "shadow"
        (d / "c11r_schema").mkdir(parents=True)
        (d / "c11r_schema" / "__init__.py").write_bytes(schema_src)
        return {"shadow_dirs": [d], "preload": ["c11r_schema"], "no_write": True}

    def rewrites_file(tmp):
        d = tmp / "shadow"
        d.mkdir()
        (d / "c11r_schema.py").write_bytes(
            schema_src + f"\n__file__ = {str(C.HERE / 'c11r_schema.py')!r}\n".encode())
        return {"shadow_dirs": [d], "preload": ["c11r_schema"], "no_write": True}

    listed = lambda name: (lambda r, t: {f"{name}_is_in_the_checked_set":
                                         name in (r.get("checked") or [])})
    one("PYC1", "a normal source import of every module", lambda t: {"no_write": True},
        expected="ACCEPT", group="PYC",
        must=lambda r, t: {"non_vacuous": {"c11r_schema.py", "c11r_contract.py"}
                           <= set(r.get("checked") or [])})
    one("PYC2", "an ordinary CPython cache that corresponds to the correct source", cached_prefix,
        expected="ACCEPT", group="PYC", must=cache_ok)
    one("PYC3", "a stale cache CPython ignores (IMP6b semantics)", stale_pyc, expected="ACCEPT",
        group="PYC", must=lambda r, t: {"the_stale_code_did_not_run":
                                        r.get("forged_code_ran") is False})
    one("PYC4", "a forged cache CPython would accept", forged_pyc, group="PYC",
        must=lambda r, t: {"the_forged_code_really_ran": r.get("forged_code_ran") is True})
    one("PYC5", "a sourceless c11r_schema.pyc earlier on sys.path",
        lambda t: sourceless(t, "c11r_schema", schema_src + b"\nC11R_SHADOW = True\n"),
        group="PYC", must=listed("c11r_schema.py"))
    one("PYC6", "a sourceless transitive helper c7_gaussian.pyc",
        lambda t: sourceless(t, "c7_gaussian", gauss + b"\nC11R_SHADOW = True\n"),
        group="PYC", must=listed("c7_gaussian.py"))
    one("PYC7", "the SAME code, compiled sourceless, at a wrong path",
        lambda t: sourceless(t, "c11r_schema", schema_src), group="PYC",
        must=listed("c11r_schema.py"))
    one("PYC8", "a symlinked alternate origin (a .pyc symlink to an external file)",
        lambda t: sourceless(t, "c11r_schema", schema_src, symlink=True), group="PYC",
        must=listed("c11r_schema.py"))
    one("PYC9", "a package directory c11r_schema/__init__.py: the module may not drop out of the "
                "check", package_dir, group="PYC", must=listed("c11r_schema.py"))
    one("PYC10", "a boundary program whose load-bearing module is absent (runner role, "
                 "c11r_boxdata never imported)",
        lambda t: {"imports": ["c11r_contract"], "role": "runner", "no_write": True}, group="PYC")
    one("IMP9", "a .py shadow that rewrites its own __file__ to the contract path", rewrites_file,
        must=listed("c11r_schema.py"))

    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        stray_rel = next(r for r in CT.closure_paths() if r.endswith("/c11_certifier.py"))
        ch.write(str(pathlib.PurePosixPath(stray_rel).parent / "c11r_certificate.py"),
                 b"# an untracked copy placed where c11r_idrift's sys.path order finds it first\n")
        pf = ch.preflight()
        record("IMP_stray", "IMP", "R4's demonstration: an untracked c11r_certificate.py in C11's "
                                   "code directory", expected="REFUSE",
               refused_at="runner pre-flight", refused=bool(pf["problems"]),
               problems=pf["problems"])
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        cert_rel = next(r for r in CT.closure_paths() if r.endswith("/c11r_certificate.py"))
        c11_code = pathlib.PurePosixPath(
            next(r for r in CT.closure_paths() if r.endswith("/c11_certifier.py"))).parent
        src = ch.root / "shadow_src.py"
        src.write_bytes(CT.code_bytes(C.REPO, cert_rel))
        py_compile.compile(str(src), cfile=str(ch.root / c11_code / "c11r_certificate.pyc"),
                           doraise=True)
        src.unlink()
        pf = ch.preflight()
        record("PYC_R5_location", "PYC", "R5's construction: a sourceless c11r_certificate.pyc in "
                                        "C11's code directory (static check)", expected="REFUSE",
               refused_at="runner pre-flight", refused=bool(pf["problems"]),
               problems=pf["problems"])
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# ORD: the order of qualification, authorization and seal (review 4, N4-10)
# ---------------------------------------------------------------------------------------------
def c_ORD():
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize(mutate=lambda a: a.update(issued_at_head=ch.approved))
        pf = ch.preflight()
        record("ORD1", "ORD", "authorization claims to be issued at the approved commit, before "
                              "the qualification it binds existed (re-stamped)", expected="REFUSE",
               refused_at="runner pre-flight", refused=bool(pf["problems"]),
               problems=pf["problems"])
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        failing = [dict(i, status="FAIL") if i["id"] == "Q16" else i for i in FIXTURE_ITEMS]
        ch.qualify(items=failing)                     # a failed attempt, committed
        ch.qualify()                                  # ... replaced by a passing one
        probs = ch.authorize()
        record("ORD2", "ORD", "a failed qualification attempt committed, then replaced by a "
                              "passing one", expected="REFUSE", refused_at="authorization",
               refused=bool(probs), problems=probs)
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()                                # authorization + GRANT, one commit
        pf = ch.preflight()
        C.git_in(ch.root, "reset", "-q", "--soft", "HEAD~1")    # un-commit them (still staged)
        ch.run(pf["identity"])                        # ... and commit them WITH the runs artifact
        record_compare("ORD3", "ORD", "the authorization committed in the same commit as the "
                                      "seal", ch.compare())
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# GS: the execution lifecycle -- permission separated from evidence (review 5, R5-1)
# ---------------------------------------------------------------------------------------------
def _state(ch) -> dict:
    return CT.lifecycle(ch.root, ch.approved, allow_fixture=True)


def c_GS():
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        st = _state(ch)["state"]
        pf = ch.preflight()
        record("GS1", "GS", "valid authorization + execution permission ALLOW (GRANT): the runner "
                            "may execute", expected="ACCEPT", refused_at="runner pre-flight",
               refused=bool(pf["problems"]), problems=pf["problems"],
               must={"lifecycle_AUTHORIZED": st == "AUTHORIZED"}, extra={"lifecycle": st})
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        r = CT.build_authorization(ch.root, approved_commit=ch.approved,
                                   operator="synthetic-fixture", fixture=True)
        CT.write_record(ch.root, CT.PERMISSION_REL, r["permission"])      # the GRANT ALONE
        ch.commit("an execution permission GRANT without its authorization")
        pf = ch.preflight()
        record("GS2", "GS", "execution permission ALLOW without an authorization",
               expected="REFUSE", refused_at="runner pre-flight", refused=bool(pf["problems"]),
               problems=pf["problems"], extra={"lifecycle": _state(ch)["state"]})
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        grant = CT.load_artifact(ch.root, CT.PERMISSION_REL)
        CT.write_record(ch.root, CT.PERMISSION_REL, CT.permission_record(
            "REVOKED_BEFORE_EXECUTION", approved_commit=ch.approved,
            authorization_sha256=grant["authorization_sha256"],
            grant_sha256=CT.body_digest(grant), fixture=True))
        ch.commit("execution permission revoked before any execution")
        pf = ch.preflight()
        record("GS3", "GS", "authorization present, execution permission DENY before any run",
               expected="REFUSE", refused_at="runner pre-flight", refused=bool(pf["problems"]),
               problems=pf["problems"], extra={"lifecycle": _state(ch)["state"]})
    finally:
        ch.cleanup()
    ch = Chain()                                         # GS4, GS5, GS12: ONE valid lifecycle
    try:
        path = [_state(ch)["state"]]
        ch.qualify()
        path.append(_state(ch)["state"])
        ch.authorize()
        path.append(_state(ch)["state"])
        auth_before = C.git_object_at("HEAD", AUTH_PATH, repo=ch.root)
        pf = ch.preflight()
        body = ch.runs_body(pf["identity"])
        R.begin_execution(ch.root, pf["identity"])
        path.append(_state(ch)["state"])
        R.finish_execution(ch.root, body)
        path.append(_state(ch)["state"])
        # NEXT_STEPS[0], literally: exactly the two REPOSITORY-relative paths it names (N6-1), in
        # ONE commit
        named = [CT.ns_path(x) for x in (CT.RUNS_REL, CT.PERMISSION_REL)
                 if CT.ns_path(x) in R.NEXT_STEPS[0]]
        ch.commit_paths(named, "the seal, exactly as NEXT_STEPS says")
        st = _state(ch)
        path.append(st["state"])
        auth_after = C.git_object_at("HEAD", AUTH_PATH, repo=ch.root)
        again = ch.preflight()
        res = ch.compare()
        table = {(t["from"], t["to"]) for t in CT.LIFECYCLE}
        record("GS4", "GS", "after a valid run execution permission is DENY while the "
                            "authorization stays, unchanged", expected="ACCEPT",
               refused_at="lifecycle", refused=st["state"] != "SEALED", problems=st["problems"],
               must={"execution_permission_DENY": st["execution_permission"] == "DENY",
                     "permission_at_HEAD_is_EXECUTION_COMPLETED":
                         st["permission_at_head"] == "EXECUTION_COMPLETED",
                     "authorization_unchanged": auth_before is not None
                     and auth_before == auth_after,
                     "the_runner_refuses_again": bool(again["problems"])})
        record_compare("GS5", "GS", "sealed valid run + DENY + the preserved authorization: the "
                                    "comparator reaches the loader boundary", res,
                       expected="ACCEPT")
        record("GS12", "GS", "the valid lifecycle follows ONE path of the frozen transition table, "
                             "the runner's NEXT_STEPS followed literally", expected="ACCEPT",
               refused_at="lifecycle", refused=False, problems=[],
               must={"path_is_the_prescribed_one": path == [
                   "FROZEN", "QUALIFIED", "AUTHORIZED", "EXECUTING", "EXECUTED_UNSEALED",
                   "SEALED"],
                     "every_step_is_in_the_table": all((x, y) in table
                                                       for x, y in zip(path, path[1:])),
                     "NEXT_STEPS_names_both_files": len(named) == 2,
                     "comparison_accepted": res["stub_loader_calls"] == 1},
               extra={"path": path})
    finally:
        ch.cleanup()
    for cid, attack, how in (
            ("GS6", "the authorization deleted after the seal ('guard DENY' read literally)",
             "delete"),
            ("GS7", "the authorization deleted, then recreated with identical bytes", "recreate"),
            ("GS8", "the deletion reverted with git revert", "revert")):
        ch = Chain()
        try:
            ch.qualify()
            ch.authorize()
            pf = ch.preflight()
            ch.run(pf["identity"])
            auth_bytes = CT.artifact_bytes(ch.root, CT.AUTH_REL)
            ch.remove(AUTH_PATH)
            ch.commit("remove the authorization")
            if how == "recreate":
                ch.write(AUTH_PATH, auth_bytes)
                ch.commit("recreate the authorization")
            if how == "revert":
                C.git_in(ch.root, "revert", "--no-edit", "HEAD")
            record_compare(cid, "GS", attack, ch.compare())
        finally:
            ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        ch.run(pf["identity"])
        again = ch.preflight()
        record("GS9", "GS", "a second execution attempt after the sealed run", expected="REFUSE",
               refused_at="runner pre-flight", refused=bool(again["problems"]),
               problems=again["problems"])
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        R.begin_execution(ch.root, pf["identity"])        # interrupted: nothing further happens
        again = ch.preflight()
        record("GS9b", "GS", "a retry after an interrupted execution (EXECUTION_STARTED on disk)",
               expected="REFUSE", refused_at="runner pre-flight", refused=bool(again["problems"]),
               problems=again["problems"])
        ch.commit_paths([PERMISSION_PATH], "commit the interrupted execution's record")
        later = ch.preflight()
        res = ch.compare()
        record("GS9c", "GS", "the interrupted execution committed (ABANDONED): no run, no "
                             "comparison", expected="REFUSE", refused_at="runner pre-flight",
               refused=bool(later["problems"]), problems=later["problems"],
               must={"comparator_refuses_too": refused_compare(res)})
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        body = ch.runs_body(pf["identity"])
        ch.write(RUNS_PATH, _dump(body))                  # a run sealed WITHOUT the DENY record
        ch.commit_paths([RUNS_PATH], "seal without the execution-permission DENY")
        no_allow_needed = CT.STAGE_STATE["compare"] == "SEALED" and all(
            t["execution_permission_after"] == "DENY" for t in CT.LIFECYCLE if t["to"] == "SEALED")
        record_compare("GS10", "GS", "a sealed run while execution permission is still ALLOW: "
                                     "comparison requires DENY, never ALLOW", ch.compare(),
                       must={"no_boundary_but_the_runner_requires_ALLOW": no_allow_needed})
    finally:
        ch.cleanup()

    def completed_bound_elsewhere(ch, pf):
        ch.run(pf["identity"], seal=False)
        rec = CT.load_artifact(ch.root, CT.PERMISSION_REL)
        rec["runs_sha256"] = "0" * 64
        rec["sha256"] = CT.body_digest(rec)
        CT.write_record(ch.root, CT.PERMISSION_REL, rec)
        ch.commit_paths([RUNS_PATH, PERMISSION_PATH], "seal with a foreign completion record")

    def grant_rebound(ch, pf):
        grant = CT.load_artifact(ch.root, CT.PERMISSION_REL)
        grant["authorization_sha256"] = "1" * 64
        grant["sha256"] = CT.body_digest(grant)
        CT.write_record(ch.root, CT.PERMISSION_REL, grant)
        ch.commit("the GRANT re-bound to another authorization")

    def run_after_revocation(ch, pf):
        grant = CT.load_artifact(ch.root, CT.PERMISSION_REL)
        CT.write_record(ch.root, CT.PERMISSION_REL, CT.permission_record(
            "REVOKED_BEFORE_EXECUTION", approved_commit=ch.approved,
            authorization_sha256=grant["authorization_sha256"],
            grant_sha256=CT.body_digest(grant), fixture=True))
        ch.write(RUNS_PATH, _dump(ch.runs_body(pf["identity"])))
        ch.commit("a run together with a revocation")
    for cid, attack, change, stage in (
            ("GS11a", "malformed: EXECUTION_COMPLETED bound to another runs artifact",
             completed_bound_elsewhere, "comparator"),
            ("GS11b", "malformed: the GRANT re-bound to another authorization", grant_rebound,
             "runner pre-flight"),
            ("GS11c", "malformed: a run committed with REVOKED_BEFORE_EXECUTION", run_after_revocation,
             "comparator")):
        ch = Chain()
        try:
            ch.qualify()
            ch.authorize()
            pf = ch.preflight()
            change(ch, pf)
            if stage == "comparator":
                record_compare(cid, "GS", attack, ch.compare())
            else:
                pf2 = ch.preflight()
                record(cid, "GS", attack, expected="REFUSE", refused_at=stage,
                       refused=bool(pf2["problems"]), problems=pf2["problems"])
        finally:
            ch.cleanup()


# ---------------------------------------------------------------------------------------------
# CF: the comparison output path (review 5, N5-2)
# ---------------------------------------------------------------------------------------------
def _plant_file(path: pathlib.Path, text: str) -> None:
    """A file with a protected NAME, written by a subprocess (this process may not open it)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["/bin/sh", "-c", 'printf "%s" "$1" > "$0"', str(path), text], check=True)


def c_CF():
    _compare_after("CF1", "an untracked comparison file already at the comparison output path",
                   after_seal=lambda ch: _plant_file(ch.root / COMPARISON_PATH, "{}"), group="CF")

    def committed_then_modified(ch):
        ch.commit_object_only(COMPARISON_PATH, _dump({"synthetic": "an earlier comparison"}),
                              "an earlier comparison")
        _plant_file(ch.root / COMPARISON_PATH, '{"modified": true}')
    _compare_after("CF2", "a committed comparison file, modified on disk", group="CF",
                   after_seal=committed_then_modified)

    def earlier_attempt(ch):
        ch.commit_object_only(COMPARISON_PATH, _dump({"synthetic": "an earlier attempt"}),
                              "an earlier comparison attempt")
        ch.commit_object_only(COMPARISON_PATH, None, "discard it")
    _compare_after("CF3", "a comparison file from an earlier attempt, committed and deleted",
                   after_seal=earlier_attempt, group="CF")

    def symlinked(ch):
        target = ch.root / "elsewhere.json"
        target.write_text("{}\n")
        (ch.root / COMPARISON_PATH).parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, ch.root / COMPARISON_PATH)
    _compare_after("CF4", "a symlink at the comparison output path", after_seal=symlinked,
                   group="CF")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cfctl_"))
    try:
        _plant_file(tmp / C.NS_REL / CT.COMPARISON_REL, "{}")
        try:
            K.write_comparison(tmp, {"synthetic": True})
            refused, why = False, []
        except SystemExit as e:
            refused, why = True, [str(e)]
        record("CF5a", "CF", "the comparator's writer meets an existing file at the output path",
               expected="REFUSE", refused_at="comparator writer", refused=refused, problems=why)
        (tmp / C.NS_REL / CT.COMPARISON_REL).unlink()
        drv = tmp / "writer_driver.py"
        drv.write_text(
            "import sys\nsys.path.insert(0, sys.argv[1])\n"
            "sys.modules['__main__'].__file__ = sys.argv[2]   # the reader identity, simulated\n"
            "import c11r_compare as K\nfirst = second = None\n"
            "try:\n    K.write_comparison(sys.argv[3], {'synthetic': True}); first = 'WROTE'\n"
            "except BaseException as e:\n    first = 'FAILED ' + repr(e)[:160]\n"
            "try:\n    K.write_comparison(sys.argv[3], {'synthetic': True}); second = 'WROTE'\n"
            "except SystemExit as e:\n    second = 'REFUSED'\n"
            "print(first); print(second)\n")
        r = subprocess.run([sys.executable, "-B", str(drv), str(C.HERE),
                            str(C.HERE / "c11r_compare.py"), str(tmp)],
                           capture_output=True, text=True)
        lines = r.stdout.strip().splitlines()
        record("CF5b", "CF", "the comparator (reader identity simulated, the recorded residual) "
                             "writes its artifact inside the sanctioned context ONCE; a second "
                             "write is refused", expected="ACCEPT", refused_at="comparator writer",
               refused=not lines or lines[0] != "WROTE", problems=lines[:2] + [r.stderr[-200:]],
               must={"first_write_succeeded": bool(lines) and lines[0] == "WROTE",
                     "second_write_refused": len(lines) > 1 and lines[1] == "REFUSED"})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------------------------
# PB: the runner uses verified policy BYTES (review 5, N5-3)
# ---------------------------------------------------------------------------------------------
def c_PB():
    for cid, attack, change, expected in (
            ("PB1", "the policy and statement bytes the runner uses, unchanged", None, "ACCEPT"),
            ("PB2", "the policy edited in place after the pre-flight (stored sha256 re-stamped)",
             lambda ch: ch.edit_json(CT.POLICY_REL, lambda o: o["configuration"]["chosen"].update(
                 panels=64), restamp=True), "REFUSE"),
            ("PB3", "the policy bytes changed after the pre-flight, stored sha256 unchanged",
             lambda ch: ch.edit_json(CT.POLICY_REL, lambda o: o.update(note="changed"),
                                     restamp=False), "REFUSE")):
        ch = Chain()
        try:
            ch.qualify()
            ch.authorize()
            pf = ch.preflight()
            if change:
                change(ch)
            vi = R.load_verified_inputs(ch.root, pf["identity"])
            record(cid, "PB", attack, expected=expected, refused_at="runner inputs",
                   refused=bool(vi["problems"]), problems=vi["problems"],
                   must={"recomputed_digest_recorded": vi["recomputed"]["policy_sha256"]
                         == CT.body_digest(vi["policy"])})
        finally:
            ch.cleanup()


# ---------------------------------------------------------------------------------------------
# GR: replace refs, grafts, shallow history (review 5, N5-4)
# ---------------------------------------------------------------------------------------------
def _plain_git_rev_list(root, rng: str) -> int:
    """DEMONSTRATION ONLY (exempted, by name, from the git-call scan below): what an UNPROTECTED
    git -- replace refs honoured -- lists; the production helpers never run git this way."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    out = subprocess.run(["git", "-C", str(root), "rev-list", rng], capture_output=True,
                         text=True, env=env).stdout
    return len(out.split())


def _graft_head_merge(ch) -> None:
    m = C.git_in(ch.root, "rev-parse", "HEAD")
    C.git_in(ch.root, "replace", "--graft", m, C.git_in(ch.root, "rev-parse", "HEAD^1"))


SUBPROCESS_CALLS = frozenset({"run", "Popen", "call", "check_call", "check_output", "system",
                              "popen", "spawnl", "spawnlp", "execv", "execvp"})


def git_call_scan() -> dict:
    """Every campaign module (this code directory and the bound closure), parsed:
      * in C11R's OWN code, a subprocess or os call whose argv literal starts with "git" may exist
        nowhere but in the demonstration above -- all git goes through c11r_common.git_run
        (replace objects disabled, GIT_* dropped);
      * a FROZEN predecessor module in the closure (C11's c11_common, reviewed and unmodifiable
        here) that defines raw git helpers is recorded, and NO module of the closure may call
        those helpers -- checked through every import alias."""
    import ast
    ns_code = sorted(C.HERE.glob("*.py"))
    closure = sorted({C.REPO / r for r in CT.closure_paths()} - set(ns_code))
    hits, calls, predecessor_helpers = [], 0, {}

    def git_calls(tree):
        func_of = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(fn):
                    func_of.setdefault(id(n), fn.name)
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call) or not n.args:
                continue
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name not in SUBPROCESS_CALLS:
                continue
            a0 = n.args[0]
            first = None
            if isinstance(a0, (ast.List, ast.Tuple)) and a0.elts and \
                    isinstance(a0.elts[0], ast.Constant):
                first = a0.elts[0].value
            elif isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                first = a0.value.split(" ", 1)[0]
            if first == "git":
                yield n, func_of.get(id(n))
    sites = []

    def sanitized(n) -> bool:
        a0 = n.args[0]
        second = a0.elts[1] if isinstance(a0, (ast.List, ast.Tuple)) and len(a0.elts) > 1 else None
        env = next((k.value for k in n.keywords if k.arg == "env"), None)
        return (isinstance(second, ast.Constant) and second.value == "--no-replace-objects"
                and isinstance(env, ast.Call) and getattr(env.func, "id", None) == "git_env")
    for f in ns_code:
        for n, where in git_calls(ast.parse(C.read_code(C._rel(f)))):
            calls += 1
            sites.append((f.name, where))
            if f.name == "c11r_chain.py" and where in ("_plain_git_rev_list", "_plain_git"):
                continue                                  # the labelled demonstrations
            if f.name != "c11r_common.py":
                hits.append(f"{f.name}:{n.lineno} ({where}): git outside c11r_common")
            elif not sanitized(n):
                hits.append(f"{f.name}:{n.lineno} ({where}): git without --no-replace-objects "
                            f"and env=git_env()")
    if not any(f == "c11r_common.py" and w == "git_run" for f, w in sites):
        hits.append("c11r_common.git_run: the sanitized entry point itself was not found")
    for f in closure:
        tree = ast.parse(C.read_code(C._rel(f)))
        reach = {where for _n, where in git_calls(tree) if where}
        grew = True
        while grew:                        # functions of the module that reach a raw git call
            grew = False
            for fn in tree.body:
                if isinstance(fn, ast.FunctionDef) and fn.name not in reach and any(
                        isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                        and c.func.id in reach for c in ast.walk(fn)):
                    reach.add(fn.name)
                    grew = True
        module_level = [n for n in tree.body if not isinstance(
            n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        for n in module_level:
            for c in ast.walk(n):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in reach:
                    hits.append(f"{f.name}:{c.lineno} calls {c.func.id} at import time")
        if reach:
            predecessor_helpers[f.stem] = sorted(reach)
    for f in ns_code + closure:
        tree = ast.parse(C.read_code(C._rel(f)))
        aliases = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name in predecessor_helpers:
                        aliases[a.asname or a.name] = a.name
            elif isinstance(n, ast.ImportFrom) and n.module in predecessor_helpers:
                for a in n.names:
                    if a.name in predecessor_helpers[n.module]:
                        hits.append(f"{f.name}:{n.lineno} imports the raw git helper {a.name}")
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and \
                    isinstance(n.func.value, ast.Name) and n.func.value.id in aliases and \
                    n.func.attr in predecessor_helpers[aliases[n.func.value.id]]:
                hits.append(f"{f.name}:{n.lineno} calls the raw git helper "
                            f"{aliases[n.func.value.id]}.{n.func.attr}")
    return {"files_scanned": len(ns_code) + len(closure), "literal_git_calls_in_c11r": calls,
            "git_call_sites_in_c11r": sorted(set(f"{a}:{b}" for a, b in sites)),
            "frozen_predecessor_git_helpers_never_called": predecessor_helpers,
            "offending": hits}


def c_GR():
    def side_edit_merged_then_grafted(ch, pf):
        _side_edit_revert(ch, "c11r_boxdata.py")
        _trunk_moves(ch, "gr1")
        ch.merge("side")
        _graft_head_merge(ch)

    def side_run_merged_then_grafted(ch, pf):
        ch.branch("side")
        other = K.synthetic_certs(ch.stmt, ch.policy, A_K=F(2222, 100))
        ch.write(RUNS_PATH, _dump(ch.runs_body(pf["identity"], certs=other)))
        ch.commit("side: an earlier run")
        ch.remove(RUNS_PATH)
        ch.commit("side: discard it")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "gr2")
        ch.merge("side")
        _graft_head_merge(ch)

    def side_seal_merged_then_grafted(ch, pf):
        body = ch.runs_body(pf["identity"])
        ch.branch("side")
        ch.write(RUNS_PATH, _dump(body))
        ch.commit("side: an earlier seal of the same run")
        ch.remove(RUNS_PATH)
        ch.commit("side: delete it")
        ch.checkout(TRUNK)
        _trunk_moves(ch, "gr3")
        ch.merge("side")
        _graft_head_merge(ch)

    def unrelated_replace(ch, pf):
        _trunk_moves(ch, "gr5")
        blob = C.git_in(ch.root, "rev-parse", "HEAD:notes/gr5.md")
        other = C.git_run(ch.root, "hash-object", "-w", "--stdin", input=b"replaced\n",
                          text=False).stdout.decode().strip()
        C.git_in(ch.root, "replace", blob, other)

    def grafts_file(ch, pf):
        _side_edit_revert(ch, "c11r_boxdata.py")
        _trunk_moves(ch, "gr6")
        ch.merge("side")
        m = C.git_in(ch.root, "rev-parse", "HEAD")
        (ch.root / ".git" / "info").mkdir(parents=True, exist_ok=True)
        (ch.root / ".git" / "info" / "grafts").write_text(
            f"{m} {C.git_in(ch.root, 'rev-parse', 'HEAD^1')}\n")

    for cid, attack, topo, expected in (
            ("GR1", "git replace --graft hides a merged side-branch frozen-path edit",
             side_edit_merged_then_grafted, "REFUSE"),
            ("GR2", "git replace --graft hides a discarded run on a merged side branch",
             side_run_merged_then_grafted, "REFUSE"),
            ("GR3", "git replace --graft hides an earlier seal of the same run",
             side_seal_merged_then_grafted, "REFUSE"),
            ("GR4", "no replace ref: the valid chain", lambda ch, pf: None, "ACCEPT"),
            ("GR5", "an unrelated replace ref cannot alter the verification", unrelated_replace,
             "ACCEPT"),
            ("GR6", "a legacy grafts file (NOT disabled by --no-replace-objects)", grafts_file,
             "REFUSE")):
        ch = Chain()
        try:
            ch.qualify()
            ch.authorize()
            pf = ch.preflight()
            topo(ch, pf)
            ch.run(pf["identity"])
            plain = _plain_git_rev_list(ch.root, f"{ch.approved}..HEAD")
            prod = len(CT.reachable_since(ch.root, ch.approved))
            must = {"production_sees_the_real_graph": prod >= plain}
            if cid in ("GR1", "GR2", "GR3"):
                must["the_graft_really_hides_commits_from_plain_git"] = plain < prod
            record_compare(cid, "GR", attack, ch.compare(), expected=expected, must=must,
                           extra={"plain_git_rev_list": plain, "production_rev_list": prod})
        finally:
            ch.cleanup()
    ch = Chain()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="grshallow_"))
    try:
        _trunk_moves(ch, "gr7")
        C.git_run(tmp, "clone", "-q", "--depth", "1", f"file://{ch.root}", str(tmp / "shallow"))
        head = C.git_in(tmp / "shallow", "rev-parse", "HEAD")
        fs = CT.frozen_state(tmp / "shallow", head)
        record("GR7", "GR", "a shallow clone (history beyond its boundary missing)",
               expected="REFUSE", refused_at="history integrity", refused=bool(fs["ancestry"]),
               problems=fs["ancestry"])
    finally:
        ch.cleanup()
        shutil.rmtree(tmp, ignore_errors=True)
    scan = git_call_scan()
    record("GR8", "GR", "every git subprocess in the campaign goes through the sanitized helper",
           expected="ACCEPT", refused_at="static scan", refused=bool(scan["offending"]),
           problems=scan["offending"],
           must={"non_vacuous": scan["files_scanned"] >= 20
                 and scan["literal_git_calls_in_c11r"] >= 1
                 and bool(scan["frozen_predecessor_git_helpers_never_called"])},
           extra={"scan": scan})


# ---------------------------------------------------------------------------------------------
# DM: target disposition follows certificate semantics (review 5, N5-11)
# ---------------------------------------------------------------------------------------------
def c_DM():
    ch = Chain()
    try:
        record_compare("DM1", "DM", "valid certified targets citing their frozen certificates",
                       full_valid(ch), expected="ACCEPT")
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        certs = K.synthetic_certs(ch.stmt, ch.policy)
        del certs["F_D"]                                  # absent: no D_lo certificate
        try:
            ch.run(pf["identity"], certs=certs)
            refused, why = False, ["the runner emitted a run without F_D"]
        except ValueError as e:
            refused, why = True, [str(e)]
        record("DM2", "DM", "an ABSENT proving certificate (D_lo citing nothing): the runner's own "
                            "emission refuses it since review 6, N6-4 (round 6 accepted it at the "
                            "comparator); a hand-edited run of that shape is RC7",
               expected="REFUSE", refused_at="runner emission (c11r_schema.emit_runs)",
               refused=refused, problems=why)
    finally:
        ch.cleanup()
    _compare_after("DM3", "NOT_CERTIFIED while citing a certificate that proves it",
                   run_mutate=lambda o: o["targets"]["Abar"].update(status="NOT_CERTIFIED",
                                                                     value=None),
                   restamp=True, group="DM")
    _compare_after("DM4", "NOT_CERTIFIED with the certificate id nulled while the proof exists",
                   run_mutate=lambda o: o["targets"]["Abar"].update(status="NOT_CERTIFIED",
                                                                     value=None,
                                                                     certificate_id=None),
                   restamp=True, group="DM")

    def rename_and_null(o):
        c = o["certificates"].pop("F_K")
        c["certificate_id"] = "F_K2"
        o["certificates"]["F_K2"] = c
        o["targets"]["Abar"].update(status="NOT_CERTIFIED", value=None, certificate_id=None)
    _compare_after("DM5", "forged nulling: the proving certificate renamed and the id nulled",
                   run_mutate=rename_and_null, restamp=True, group="DM")


# ---------------------------------------------------------------------------------------------
# AC: the approved commit is an immutable full commit id (review 5, N5-7)
# ---------------------------------------------------------------------------------------------
def c_AC():
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        ch.run(pf["identity"])
        C.git_in(ch.root, "tag", "approved-A", ch.approved)
        record_compare("AC1", "AC", "the approved commit named by a TAG (movable)",
                       ch.compare(approved="approved-A"))
        record_compare("AC2", "AC", "the approved commit named by an ABBREVIATED id",
                       ch.compare(approved=ch.approved[:12]))
        record_compare("AC3", "AC", "the approved commit as its full 40-hex id", ch.compare(),
                       expected="ACCEPT")
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        C.git_in(ch.root, "tag", "approved-A", ch.approved)
        probs = ch.authorize(approved="approved-A")
        record("AC4", "AC", "an authorization issued against a tag", expected="REFUSE",
               refused_at="authorization", refused=bool(probs), problems=probs)
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# R61: the campaign-directory import closure (review 6, blocker R6-1). Every control plants its
# material in a SYNTHETIC repository and runs a driver whose EXECUTION ROOT is that repository
# (its code imported from there, its code directory first on sys.path, as a boundary program's
# would be): the real checkout's code directories are never touched.
# ---------------------------------------------------------------------------------------------
R61_DRIVER = r'''
import json, os, sys
cfg = json.loads(sys.argv[1])
_me = os.path.dirname(os.path.realpath(__file__))
sys.path[:] = [p for p in sys.path if os.path.realpath(p or ".") != _me]
sys.path.insert(0, cfg["code"])
for d in cfg.get("prepend", []):
    sys.path.insert(0, d)
out = {"imported": [], "errors": {}}
for m in cfg["imports"]:
    try:
        __import__(m)
        out["imported"].append(m)
    except BaseException as e:
        out["errors"][m] = type(e).__name__ + ": " + str(e)[:300]
import c11r_common as C
import c11r_contract as CT
contract = CT.load_artifact(C.REPO, CT.CONTRACT_REL)
out.update(CT.verify_loaded_modules(contract, role=cfg.get("role")))
out["static"] = CT.code_dir_shadows(contract, C.REPO)
out["files"] = {m: getattr(sys.modules.get(m), "__file__", None) for m in cfg.get("report", [])}
out["markers"] = {m: bool(getattr(sys.modules.get(m), "C11R_SHADOW_MARKER", False))
                  for m in cfg.get("report", [])}
print(json.dumps(out))
'''
SHADOW_MARKER = (b"\nimport sys as _s\n_s.stderr.write('C11R-SHADOW-RAN\\n')\n"
                 b"C11R_SHADOW_MARKER = True\n")
NSC = f"{C.NS_REL}/code"
C11C = str((C.C11 / "code").relative_to(C.REPO))


def _r61_driver(ch, imports, *, role=None, report=(), prepend=(), no_write=True) -> dict:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="r61drv_"))
    try:
        drv = tmp / "r61_driver.py"
        drv.write_text(R61_DRIVER)
        cfg = {"code": str(ch.root / NSC), "imports": list(imports), "role": role,
               "report": list(report), "prepend": [str(x) for x in prepend]}
        e = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        r = subprocess.run([sys.executable, *(["-B"] if no_write else []), str(drv),
                            json.dumps(cfg)], capture_output=True, text=True, env=e, cwd=str(tmp))
        if r.returncode != 0 or not r.stdout.strip():
            return {"problems": [f"driver failed: {r.stderr.strip()[-400:]}"], "static": [],
                    "driver_failed": True}
        out = json.loads(r.stdout.strip().splitlines()[-1])
        out["shadow_ran"] = "C11R-SHADOW-RAN" in r.stderr
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _stdlib_source(name: str) -> bytes:
    """The interpreter's own source of a standard-library module (never a campaign file)."""
    import sysconfig
    return (pathlib.Path(sysconfig.get_paths()["stdlib"]) / f"{name}.py").read_bytes()


def _plant_sourceless(dest: pathlib.Path, source: bytes) -> None:
    import py_compile
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="r61src_"))
    try:
        src = tmp / (dest.name.split(".")[0] + ".py")
        src.write_bytes(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        py_compile.compile(str(src), cfile=str(dest), doraise=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _launch_boundary_programs(ch, *, with_runner: bool) -> dict:
    """A SYNTHETIC repository's boundary programs, each launched with NO argument: c11r_compare.py
    and c11r_qualify.py can then only print their usage (or refuse at the pre-import barrier);
    c11r_runs.py (with_runner) is launched only with a planted shadow present, where the barrier
    refuses before any import -- and even past it, a synthetic repository carries no
    authorization, so its pre-flight refuses before any science. The real checkout's programs are
    never launched."""
    assert ch.root.resolve() != C.REPO.resolve()
    out = {}
    for prog in CT.BOUNDARY_PROGRAMS:
        if prog == "c11r_runs.py" and not with_runner:
            continue
        r = subprocess.run([sys.executable, "-B", str(ch.root / NSC / prog)], capture_output=True,
                           text=True, cwd=str(ch.root),
                           env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
        out[prog] = {"rc": r.returncode, "barrier": "REFUSE (pre-import barrier" in r.stderr,
                     "shadow_ran": "C11R-SHADOW-RAN" in (r.stderr + r.stdout)}
    return out


def _tracked(ch, rel: str) -> bool:
    return bool(C.git_in(ch.root, "ls-files", "--", rel))


def c_R61():
    import importlib.machinery as M
    import sysconfig
    import zipfile
    frac = _stdlib_source("fractions")
    stdlib_dir = os.path.realpath(sysconfig.get_paths()["stdlib"])
    cert_rel = next(r for r in CT.closure_paths() if r.endswith("/c11r_certificate.py"))

    def has(res, text, where="static"):
        return any(text in x for x in res.get(where) or [])

    def one(cid, attack, setup, imports, *, expected="REFUSE", role=None, report=(),
            must=None, prepend=None, no_write=True):
        ch = Chain()
        try:
            if setup:
                setup(ch)
            res = _r61_driver(ch, imports, role=role, report=report, no_write=no_write,
                              prepend=prepend(ch) if prepend else ())
            probs = res["problems"] + res.get("static", [])
            m = dict(must(res, ch) if must else {}, driver_ran=not res.get("driver_failed"))
            record(cid, "R61", attack, expected=expected,
                   refused_at="loaded-module identity + code directories", refused=bool(probs),
                   problems=probs, must=m,
                   extra={"campaign_origin_modules": res.get("campaign_origin_modules"),
                          "modules_examined": res.get("modules_examined"),
                          "files": {k: (pathlib.PurePosixPath(v).name if v else v)
                                    for k, v in (res.get("files") or {}).items()},
                          "shadow_ran": res.get("shadow_ran"),
                          "import_errors": res.get("errors")})
        finally:
            ch.cleanup()

    def from_stdlib(res, m):
        f = (res.get("files") or {}).get(m)
        return bool(f) and os.path.realpath(f).startswith(stdlib_dir + os.sep)

    one("R61-1", "the normal approved source closure (campaign modules and the standard library)",
        None, ["c11r_idrift", "c11r_certificate", "c11r_schema"], expected="ACCEPT",
        report=["fractions"],
        must=lambda r, ch: {"non_vacuous": {"c11r_idrift", "c11_certifier", "c7_gaussian"}
                            <= set(r.get("campaign_origin_modules") or []),
                            "fractions_from_the_stdlib": from_stdlib(r, "fractions")})
    one("R61-2", "a sourceless fractions.pyc in the campaign's code directory (R6-1)",
        lambda ch: _plant_sourceless(ch.root / NSC / "fractions.pyc", frac + SHADOW_MARKER),
        ["c11r_idrift"], report=["fractions"],
        must=lambda r, ch: {"the_shadow_really_ran": r.get("shadow_ran") is True,
                            "static_refuses_the_kind": has(r, "fractions.pyc in "
                                                              "p5y_k5_tail_c11r_n9_statement_"
                                                              "alignment/code is not Python "
                                                              "source"),
                            "static_names_the_stdlib_name": has(
                                r, "carries the standard-library import name 'fractions'")})
    one("R61-3", "a sourceless ast.pyc in C11's code directory (R6-1; ast is imported lazily)",
        lambda ch: _plant_sourceless(ch.root / C11C / "ast.pyc",
                                     _stdlib_source("ast") + SHADOW_MARKER),
        ["c11r_idrift", "ast"], report=["ast"],
        must=lambda r, ch: {"the_shadow_really_ran": r.get("shadow_ran") is True,
                            "static_refuses": has(r, "ast.pyc in p5y_k5_tail_c11_n9_independent_"
                                                     "certifier/code is not Python source")})
    one("R61-4", "an unexpected fractions.py SOURCE in the campaign's code directory",
        lambda ch: ch.write(f"{NSC}/fractions.py", frac + SHADOW_MARKER), ["c11r_idrift"],
        report=["fractions"],
        must=lambda r, ch: {"the_shadow_really_ran": r.get("shadow_ran") is True,
                            "static_untracked": has(r, "untracked Python source ['fractions.py']"),
                            "static_not_in_inventory": has(r, "fractions.py in p5y_k5_tail_c11r_n9"
                                                              "_statement_alignment/code is not "
                                                              "in the directory inventory")})

    def committed_package(ch):
        ch.write(f"{NSC}/fractions/__init__.py", frac + SHADOW_MARKER)
        ch.commit("a stdlib-named package committed after the approval")
    one("R61-5", "a COMMITTED standard-library-named package fractions/__init__.py",
        committed_package, ["c11r_idrift"], report=["fractions"],
        must=lambda r, ch: {"the_package_is_tracked": _tracked(ch, f"{NSC}/fractions/__init__.py"),
                            "the_shadow_really_ran": r.get("shadow_ran") is True,
                            "static_refuses_the_directory": has(
                                r, "fractions/ in p5y_k5_tail_c11r_n9_statement_alignment/code "
                                   "is a directory")})
    one("R61-6", "an UNTRACKED standard-library-named package fractions/__init__.py",
        lambda ch: ch.write(f"{NSC}/fractions/__init__.py", frac + SHADOW_MARKER),
        ["c11r_idrift"], report=["fractions"],
        must=lambda r, ch: {"the_shadow_really_ran": r.get("shadow_ran") is True,
                            "static_refuses_the_directory": has(r, "is a directory (a package")})
    one("R61-7", "an unexpected NAMESPACE-package directory, imported",
        lambda ch: ch.write(f"{NSC}/c11x_nsdata/notes.txt", b"not code\n"),
        ["c11r_idrift", "c11x_nsdata"],
        must=lambda r, ch: {"static_refuses_the_directory": has(
            r, "c11x_nsdata/ in p5y_k5_tail_c11r_n9_statement_alignment/code is a directory")})

    def egg(ch):
        z = ch.root / NSC / "shadow.egg"
        with zipfile.ZipFile(z, "w") as f:
            f.writestr("fractions.py", frac + SHADOW_MARKER)
    one("R61-8", "a zip/egg import container in the campaign's code directory, on sys.path",
        egg, ["c11r_idrift"], report=["fractions"],
        prepend=lambda ch: [ch.root / NSC / "shadow.egg"],
        must=lambda r, ch: {"the_shadow_really_ran": r.get("shadow_ran") is True,
                            "L1_refuses_the_module": has(
                                r, "module 'fractions' was loaded from "
                                   "p5y_k5_tail_c11r_n9_statement_alignment/code/shadow.egg",
                                "problems"),
                            "static_refuses_the_container": has(
                                r, "shadow.egg in p5y_k5_tail_c11r_n9_statement_alignment/code "
                                   "is not Python source")})

    def symlinked_inside(ch):
        ch.write("notes/helper_src.py", b"HELPER = 1\n")
        os.symlink(ch.root / "notes/helper_src.py", ch.root / NSC / "c11x_helper.py")
    one("R61-9", "a symlinked source in the campaign's code directory resolving elsewhere in "
                 "the repository", symlinked_inside, ["c11r_idrift", "c11x_helper"],
        must=lambda r, ch: {"static_refuses_the_symlink": has(
            r, "c11x_helper.py in p5y_k5_tail_c11r_n9_statement_alignment/code is a symlink "
               "(resolving inside the repository)")})

    def approved_name_symlinked(ch):
        rel = f"{NSC}/c11r_schema.py"
        ch.write("notes/c11r_schema_copy.py", CT.code_bytes(ch.root, rel))
        (ch.root / rel).unlink()
        os.symlink(ch.root / "notes/c11r_schema_copy.py", ch.root / rel)
    one("R61-9b", "an APPROVED name (c11r_schema.py) replaced by a symlink to identical bytes "
                  "elsewhere in the repository", approved_name_symlinked,
        ["c11r_idrift", "c11r_schema"],
        must=lambda r, ch: {"static_refuses_the_symlink": has(
            r, "c11r_schema.py in p5y_k5_tail_c11r_n9_statement_alignment/code is a symlink")})
    one("R61-11", "a TRACKED but unbound module in C11's code directory, loaded (tracking does "
                  "not approve)",
        lambda ch: (ch.write(f"{C11C}/c11_extra.py", b"VALUE = 1\n"),
                    ch.commit("a tracked, unbound module in C11's code directory")),
        ["c11r_idrift", "c11_extra"],
        must=lambda r, ch: {"it_is_tracked": _tracked(ch, f"{C11C}/c11_extra.py"),
                            "static_not_in_inventory": has(
                                r, "c11_extra.py in p5y_k5_tail_c11_n9_independent_certifier/code"
                                   " is not in the directory inventory the contract froze")})
    one("R61-12", "standard-library modules loaded from the standard library", None,
        ["c11r_idrift", "json", "ast", "fractions", "decimal"], expected="ACCEPT",
        report=["fractions", "ast", "decimal"],
        must=lambda r, ch: {"fractions_from_the_stdlib": from_stdlib(r, "fractions"),
                            "ast_from_the_stdlib": from_stdlib(r, "ast")})
    one("R61-13", "every contract module of the runner boundary from its exact source (role "
                  "runner, the pre-import barrier passing)", None, ["c11r_runs"],
        expected="ACCEPT", role="runner",
        must=lambda r, ch: {"required_all_present": bool(r.get("required"))
                            and set(r["required"]) <= set(r.get("checked") or []),
                            "non_vacuous": len(r.get("required") or []) >= 10})
    one("R61-14", "an approved NAME (c11r_certificate) loaded from the wrong campaign directory",
        lambda ch: ch.write(f"{C11C}/c11r_certificate.py", CT.code_bytes(C.REPO, cert_rel)),
        ["c11r_idrift", "c11r_certificate"], report=["c11r_certificate"],
        must=lambda r, ch: {"name_check_also_refuses": has(
            r, "c11r_certificate.py (as module 'c11r_certificate') was loaded from another file",
            "problems"),
            "static_contract_name": has(r, "carries the import name of contract module "
                                           "c11r_certificate")})
    stdlib_fractions = str(pathlib.Path(sysconfig.get_paths()["stdlib"]) / "fractions.py")
    one("R61-15", "a campaign-directory fractions.py that rewrites its own __file__ to the "
                  "standard library's",
        lambda ch: ch.write(f"{NSC}/fractions.py", frac + SHADOW_MARKER
                            + f"\n__file__ = {stdlib_fractions!r}\n".encode()),
        ["c11r_idrift"], report=["fractions"],
        must=lambda r, ch: {"the_rewrite_took_effect": (r.get("files") or {}).get("fractions")
                            == stdlib_fractions,
                            "L1_refuses_too": has(r, "inside a campaign code directory, which is "
                                                     "not an approved contract source",
                                                  "problems")})
    one("R61-16", "a COMMITTED unexpected package (a non-stdlib name), not imported",
        lambda ch: (ch.write(f"{NSC}/c11x_pkg/__init__.py", b"X = 1\n"),
                    ch.commit("an unexpected package committed after the approval")),
        ["c11r_idrift"],
        must=lambda r, ch: {"it_is_tracked": _tracked(ch, f"{NSC}/c11x_pkg/__init__.py")})
    ext = M.EXTENSION_SUFFIXES[0]
    ch = Chain()
    try:
        # static only: a broken extension named `fractions` would break every import of the
        # driver itself; the import system's own finder shows it is found AHEAD of the stdlib
        ch.write(f"{NSC}/fractions{ext}", b"\x00 not a real extension\n")
        finder = M.FileFinder(str(ch.root / NSC),
                              (M.ExtensionFileLoader, M.EXTENSION_SUFFIXES),
                              (M.SourceFileLoader, M.SOURCE_SUFFIXES),
                              (M.SourcelessFileLoader, M.BYTECODE_SUFFIXES))
        spec = finder.find_spec("fractions")
        probs = CT.code_dir_shadows(CT.load_artifact(ch.root, CT.CONTRACT_REL), ch.root)
        record("R61-17", "R61", f"an extension-module file fractions{ext} in the campaign's code "
                                f"directory", expected="REFUSE", refused_at="code directories",
               refused=bool(probs), problems=probs,
               must={"the_finder_resolves_it_first": spec is not None
                     and type(spec.loader).__name__ == "ExtensionFileLoader",
                     "static_names_the_stdlib_name": any(
                         "carries the standard-library import name 'fractions'" in x
                         for x in probs)})
    finally:
        ch.cleanup()

    def cached(ch):
        _r61_driver(ch, ["c11r_idrift", "c11r_certificate"], no_write=False)
    one("R61-18", "ordinary valid __pycache__ caches written by CPython for the sources: "
                  "accepted by the frozen cache policy", cached,
        ["c11r_idrift", "c11r_certificate"], expected="ACCEPT",
        must=lambda r, ch: {"caches_exist": any(
            (ch.root / NSC / "__pycache__").glob("c11r_idrift.*.pyc"))})
    one("R61-18b", "a cache file in __pycache__ that is no inventory source's (an orphan named "
                   "like a standard-library module)",
        lambda ch: ch.write(f"{NSC}/__pycache__/fractions.{sys.implementation.cache_tag}.pyc",
                            b"not a cache\n"),
        ["c11r_idrift"])
    one("R61-P", "a foreign directory ahead of the standard library on sys.path",
        lambda ch: None, ["c11r_idrift"],
        prepend=lambda ch: [ch.root.parent])

    # (B) the pre-import barrier: the boundary PROGRAMS refuse to start
    ch = Chain()
    try:
        _plant_sourceless(ch.root / NSC / "fractions.pyc", frac + SHADOW_MARKER)
        outs = _launch_boundary_programs(ch, with_runner=True)
        refused = all(o["barrier"] and o["rc"] != 0 for o in outs.values())
        record("R61-B", "R61", "fractions.pyc present: each boundary program refuses at its "
                               "pre-import barrier, BEFORE the shadow can execute",
               expected="REFUSE", refused_at="pre-import barrier", refused=refused,
               problems=[f"{k}: rc {v['rc']}, barrier {v['barrier']}" for k, v in outs.items()],
               must={"no_shadow_ran": not any(o["shadow_ran"] for o in outs.values())},
               extra={"programs": outs})
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        outs = _launch_boundary_programs(ch, with_runner=False)   # usage, nothing run
        record("R61-B0", "R61", "clean code directories: the barrier passes (the programs reach "
                                "their own usage message)", expected="ACCEPT",
               refused_at="pre-import barrier", refused=any(o["barrier"] for o in outs.values()),
               problems=[], must={"usage_reached": all(o["rc"] == 2 for o in outs.values())},
               extra={"programs": outs})
        real = CT.preimport_barrier_problems()
        record("R61-0", "R61", "the canonical barrier opens all three boundary programs, "
                               "verbatim, with no __future__ import", expected="ACCEPT",
               refused_at="pre-import barrier text", refused=bool(real), problems=real)
        rel = f"{NSC}/c11r_compare.py"
        src = CT.code_bytes(ch.root, rel).decode()
        doc_end = src.index('"""', 3) + 3
        ch.write(rel, (src[:doc_end] + "\nimport json\n" + src[doc_end:]).encode())
        moved = CT.preimport_barrier_problems(ch.root)
        record("R61-0b", "R61", "an import placed before the barrier", expected="REFUSE",
               refused_at="pre-import barrier text", refused=bool(moved), problems=moved)
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# TP: typed path refusals (review 6, N6-5) -- never an exception
# ---------------------------------------------------------------------------------------------
def _typed(fn):
    try:
        return fn(), None
    except Exception as e:                               # the control's own failure record
        return None, f"{type(e).__name__}: {str(e)[:200]}"


_OUTSIDE: list[pathlib.Path] = []


def c_TP():
    schema_rel = f"{NSC}/c11r_schema.py"

    def outside_symlink(ch):
        ext = pathlib.Path(tempfile.mkdtemp(prefix="tp_outside_"))
        _OUTSIDE.append(ext)
        (ext / "c11r_schema.py").write_bytes(CT.code_bytes(ch.root, schema_rel))
        (ch.root / schema_rel).unlink()
        os.symlink(ext / "c11r_schema.py", ch.root / schema_rel)

    def dangling(ch):
        (ch.root / schema_rel).unlink()
        os.symlink(ch.root / "nowhere" / "c11r_schema.py", ch.root / schema_rel)

    def loop(ch):
        (ch.root / schema_rel).unlink()
        os.symlink(ch.root / schema_rel, ch.root / schema_rel)

    def auth_directory(ch):
        (ch.root / AUTH_PATH).unlink()
        (ch.root / AUTH_PATH).mkdir()
    for cid, attack, change in (
            ("TP1", "a contract path replaced by a symlink to identical bytes OUTSIDE the "
                    "repository", outside_symlink),
            ("TP2", "a contract path replaced by a DANGLING symlink", dangling),
            ("TP3", "a contract path replaced by a symlink LOOP", loop),
            ("TP4", "a DIRECTORY where the authorization file belongs", auth_directory)):
        ch = Chain()
        try:
            ch.qualify()
            ch.authorize()
            change(ch)
            pf, exc = _typed(ch.preflight)
            record(cid, "TP", attack + " (runner pre-flight)", expected="REFUSE",
                   refused_at="runner pre-flight", refused=bool(pf and pf["problems"]),
                   problems=(pf or {}).get("problems") or [exc], must={"no_exception": exc is None})
        finally:
            ch.cleanup()

    def runs_dangling(ch):
        (ch.root / RUNS_PATH).unlink()
        os.symlink(ch.root / "nowhere.json", ch.root / RUNS_PATH)
    for cid, attack, after in (
            ("TP1c", "a contract path symlinked OUTSIDE the repository after the seal",
             outside_symlink),
            ("TP2c", "the runs artifact replaced by a DANGLING symlink after the seal",
             runs_dangling)):
        ch = Chain()
        try:
            ch.qualify()
            ch.authorize()
            pf = ch.preflight()
            ch.run(pf["identity"])
            after(ch)
            res, exc = _typed(ch.compare)
            if res is None:
                record(cid, "TP", attack, expected="REFUSE", refused_at="comparator",
                       refused=False, problems=[exc], must={"no_exception": False})
            else:
                record_compare(cid, "TP", attack, res, must={"no_exception": True})
        finally:
            ch.cleanup()
    for ext in _OUTSIDE:
        shutil.rmtree(ext, ignore_errors=True)


# ---------------------------------------------------------------------------------------------
# CMP: the comparison transaction (review 6, N6-3) -- a refusal writes NOTHING
# ---------------------------------------------------------------------------------------------
WRITER_DRIVER = r'''
import json, os, sys
_me = os.path.dirname(os.path.realpath(__file__))
sys.path[:] = [p for p in sys.path if os.path.realpath(p or ".") != _me]
sys.path.insert(0, sys.argv[1])
sys.modules["__main__"].__file__ = sys.argv[2]   # the reader identity, simulated (the residual)
import c11r_compare as K
print(K.write_comparison(sys.argv[3], json.loads(sys.stdin.read())))
'''


def _subprocess_writer(repo, out) -> str:
    """write_comparison in a process whose __main__ resolves to c11r_compare.py -- the recorded
    open-guard residual the chain uses; the payload is the synthetic chain's own result."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cmpwriter_"))
    try:
        drv = tmp / "cmp_writer.py"
        drv.write_text(WRITER_DRIVER)
        r = subprocess.run([sys.executable, "-B", str(drv), str(C.HERE),
                            str(C.HERE / "c11r_compare.py"), str(repo)],
                           input=json.dumps(out), capture_output=True, text=True)
        if r.returncode != 0:
            raise OSError(f"the writer process failed: {r.stderr.strip()[-300:]}")
        return r.stdout.strip().splitlines()[-1]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _refusing_writer(repo, out):
    raise AssertionError("a refused or failed comparison reached the writer")


class RaisingLoader(StubLoader):
    def __call__(self, stmt):
        self.calls += 1
        raise ValueError("synthetic post-load failure")


def _phase15(ch, *, writer=None, loader=None) -> dict:
    loader = loader or StubLoader()
    calls = {"writer": 0}

    def w(repo, out):
        calls["writer"] += 1
        return (writer or _refusing_writer)(repo, out)
    r, exc = _typed(lambda: K.phase15(ch.root, approved_commit=ch.approved, loader=loader,
                                      allow_fixture=True, writer=w))
    listed = C.git_in(ch.root, "ls-files", "--cached", "--others", "--",
                      f"{C.NS_REL}/evidence/comparison").splitlines()     # names only
    return {"r": r, "exception": exc, "loader_calls": loader.calls,
            "writer_calls": calls["writer"],
            "output_exists": os.path.lexists(ch.root / COMPARISON_PATH),
            "comparison_dir_entries": sorted(pathlib.PurePosixPath(x).name for x in listed)}


def _record_cmp(cid, attack, t, *, expected="REFUSE", must=None, prior_output=False):
    """`prior_output`: a valid comparison was ALREADY written by an earlier invocation; the
    refusal must leave it exactly as it was (checked by the caller) and write nothing new."""
    r = t["r"] or {}
    res = r.get("result") or {}
    outcome = r.get("outcome")
    must = dict(must or {}, no_exception=t["exception"] is None)
    if expected == "REFUSE":
        must.update(writer_never_called=t["writer_calls"] == 0,
                    outcome_REFUSED_BEFORE_LOAD=outcome == "REFUSED_BEFORE_LOAD")
        if prior_output:
            must.update(still_exactly_one_file=t["comparison_dir_entries"]
                        == [pathlib.PurePosixPath(COMPARISON_PATH).name])
        else:
            must.update(no_result_file=not t["output_exists"])
    record(cid, "CMP", attack, expected=expected, refused_at="comparison transaction",
           refused=outcome != "COMPARED", problems=res.get("identity_problems") or r.get("lines")
           or [t["exception"]], loader_calls=t["loader_calls"], step=res.get("refused_at"),
           must=must, extra={"outcome": outcome, "writer_calls": t["writer_calls"],
                             "output_exists": t["output_exists"],
                             "comparison_dir_entries": t["comparison_dir_entries"]})


def _sealed_chain() -> Chain:
    ch = Chain()
    ch.qualify()
    ch.authorize()
    pf = ch.preflight()
    ch.run(pf["identity"])
    return ch


def c_CMP():
    for cid, attack, after in (
            ("CMP1", "a stray Finder .DS_Store in evidence/runs",
             lambda ch: ch.write(f"{C.NS_REL}/evidence/runs/.DS_Store", b"\x00\x00\x00\x01Bud1")),
            ("CMP2", "a DIRECTORY where the runs artifact belongs",
             lambda ch: ((ch.root / RUNS_PATH).unlink(), (ch.root / RUNS_PATH).mkdir())),
            ("CMP2b", "the runs artifact is not valid JSON",
             lambda ch: ch.write(RUNS_PATH, b"{ not json\n")),
            ("CMP3", "a pre-load failure: a frozen code file edited after the seal",
             lambda ch: ch.edit_code("c11r_boxdata.py"))):
        ch = _sealed_chain()
        try:
            after(ch)
            _record_cmp(cid, attack, _phase15(ch))
        finally:
            ch.cleanup()
    ch = _sealed_chain()
    try:
        t = _phase15(ch, loader=RaisingLoader())
        _record_cmp("CMP4", "a failure AFTER the loader was entered (the loader raises)", t,
                    expected="POST_LOAD_FAILURE",
                    must={"outcome_POST_LOAD_FAILURE": (t["r"] or {}).get("outcome")
                          == "POST_LOAD_FAILURE", "loader_entered_once": t["loader_calls"] == 1,
                          "no_result_file": not t["output_exists"],
                          "writer_never_called": t["writer_calls"] == 0})
    finally:
        ch.cleanup()
    ch = _sealed_chain()
    try:
        def failing(repo, out):
            raise OSError("synthetic write failure")
        t = _phase15(ch, writer=failing)
        _record_cmp("CMP4b", "the write itself fails after the comparison was computed", t,
                    expected="POST_LOAD_FAILURE",
                    must={"outcome_POST_LOAD_FAILURE": (t["r"] or {}).get("outcome")
                          == "POST_LOAD_FAILURE", "no_result_file": not t["output_exists"]})
    finally:
        ch.cleanup()
    ch = _sealed_chain()
    try:
        t = _phase15(ch, writer=_subprocess_writer)
        _record_cmp("CMP5", "the valid chain: ONE comparison artifact, written exactly once", t,
                    expected="ACCEPT",
                    must={"outcome_COMPARED": (t["r"] or {}).get("outcome") == "COMPARED",
                          "written_once": t["writer_calls"] == 1,
                          "exactly_one_file": t["comparison_dir_entries"]
                          == [pathlib.PurePosixPath(COMPARISON_PATH).name],
                          "loader_called_once": t["loader_calls"] == 1})
        before = C.content_free_id(ch.root / COMPARISON_PATH)
        t = _phase15(ch)
        _record_cmp("CMP6", "a second comparator invocation meets the existing output", t,
                    prior_output=True,
                    must={"output_unchanged": C.content_free_id(ch.root / COMPARISON_PATH)
                          == before})
        ch.commit_paths([COMPARISON_PATH], "the comparison, committed")
        t = _phase15(ch)
        _record_cmp("CMP6b", "a third invocation after the comparison was committed (COMPARED)", t,
                    prior_output=True,
                    must={"output_unchanged": C.content_free_id(ch.root / COMPARISON_PATH)
                          == before})
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# RC: the required proving certificates (review 6, N6-4)
# ---------------------------------------------------------------------------------------------
def c_RC():
    ch = Chain()
    try:
        record_compare("RC1", "RC", "every required certificate present and cited as frozen",
                       full_valid(ch), expected="ACCEPT")
    finally:
        ch.cleanup()
    _compare_after("RC2", "the certificate_id field deleted from Abar",
                   run_mutate=lambda o: o["targets"]["Abar"].pop("certificate_id"), restamp=True,
                   group="RC")
    _compare_after("RC3", "Abar's certificate nulled",
                   run_mutate=lambda o: o["targets"]["Abar"].update(certificate_id=None),
                   restamp=True, group="RC")
    _compare_after("RC4", "Abar citing a certificate that does not exist",
                   run_mutate=lambda o: o["targets"]["Abar"].update(certificate_id="F_Kx"),
                   restamp=True, group="RC")
    _compare_after("RC5", "Abar citing another target's certificate (F_H)",
                   run_mutate=lambda o: o["targets"]["Abar"].update(certificate_id="F_H"),
                   restamp=True, group="RC")

    def not_proving(o):
        o["targets"]["Abar"].update(status="CERTIFIED", value="1111/100", reason=None)
    _compare_after("RC6", "Abar claimed CERTIFIED from a certificate that does not prove it",
                   certs=lambda ch: K.synthetic_certs(ch.stmt, ch.policy, certified_K=False),
                   run_mutate=not_proving, restamp=True, group="RC")

    def dropped(o):
        o["certificates"].pop("F_K")
        o["targets"]["Abar"].update(status="NOT_CERTIFIED", value=None, certificate_id=None)
    _compare_after("RC7", "R6's N6-4: the proving certificate REMOVED, Abar demoted, the "
                          "citation nulled", run_mutate=dropped, restamp=True, group="RC")


# ---------------------------------------------------------------------------------------------
# CG: the commit-graph file is not read (review 6, N6-6)
# ---------------------------------------------------------------------------------------------
def _plain_git(root, *a) -> subprocess.CompletedProcess:
    """DEMONSTRATION ONLY (exempted, by name, from the git-call scan): git as an UNPROTECTED
    caller runs it -- commit-graph honoured -- and the graph writer."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, env=env)


def _forge_commit_graph(root: pathlib.Path, commit: str) -> bool:
    """Rewrite the commit-graph so that `commit` (a merge) has NO second parent; the trailer is
    re-hashed, so git trusts the file."""
    import hashlib
    import struct
    gp = root / ".git" / "objects" / "info" / "commit-graph"
    data = bytearray(gp.read_bytes())
    if data[:4] != b"CGPH":
        return False
    chunks = {}
    for i in range(data[6] + 1):
        chunks[bytes(data[8 + 12 * i:12 + 12 * i])] = struct.unpack(
            ">Q", data[12 + 12 * i:20 + 12 * i])[0]
    fan = chunks[b"OIDF"]
    n = struct.unpack(">I", data[fan + 255 * 4:fan + 256 * 4])[0]
    oids = [bytes(data[chunks[b"OIDL"] + 20 * i:chunks[b"OIDL"] + 20 * i + 20]).hex()
            for i in range(n)]
    if commit not in oids:
        return False
    at = chunks[b"CDAT"] + 36 * oids.index(commit) + 24
    data[at:at + 4] = struct.pack(">I", 0x70000000)          # GRAPH_PARENT_NONE
    data[-20:] = hashlib.sha1(bytes(data[:-20])).digest()
    os.chmod(gp, 0o644)
    gp.write_bytes(bytes(data))
    return True


def c_CG():
    ch = Chain()
    try:
        ch.branch("side")
        ch.write(RUNS_PATH, b'{"synthetic": "a run merged in and hidden"}\n')
        ch.commit("a run on a side branch")
        ch.remove(RUNS_PATH)
        ch.commit("the run removed again on the side branch")
        ch.checkout(TRUNK)
        ch.write("notes/TRUNK.md", b"trunk moves\n")
        ch.commit("trunk moves")
        merge = ch.merge("side")                   # the merged tree holds no run: only the
        #                                            side commit does, through parent 2
        C.git_in(ch.root, "branch", "-q", "-D", "side")
        C.git_in(ch.root, "reflog", "expire", "--expire=now", "--all")
        wrote = _plain_git(ch.root, "commit-graph", "write", "--reachable").returncode == 0
        forged = wrote and _forge_commit_graph(ch.root, merge)
        raw = len(_plain_git(ch.root, "rev-list", "--all", "--reflog", "HEAD").stdout.split())
        real = len(C.git_in(ch.root, "rev-list", "--all", "--reflog", "HEAD").split())
        anywhere = CT.protocol_artifacts_anywhere(ch.root)
        record("CG1", "CG", "a merged run hidden by a FORGED commit-graph (the merge's second "
                            "parent dropped): the pre-result state check still finds it",
               expected="REFUSE", refused_at="pre-result state check",
               refused=bool(anywhere["holders"]["runs"]),
               problems=[f"commits holding a runs artifact: {len(anywhere['holders']['runs'])}"],
               must={"the_graph_was_forged": forged,
                     "an_unprotected_git_trusts_the_forged_graph": raw < real,
                     "the_campaign_reads_every_commit": real == anywhere["commits_checked"]},
               extra={"unprotected_rev_list_all": raw, "campaign_rev_list_all": real})
    finally:
        ch.cleanup()


# ---------------------------------------------------------------------------------------------
# WD, LG: what the lifecycle claims, and the repository-wide lineage (review 6, N6-2)
# ---------------------------------------------------------------------------------------------
def c_WD():
    overstated = "nothing re-enables execution"
    scanned, hits = 0, []
    for f in sorted(C.HERE.glob("*.py")):
        if f.name in ("c11r_errata.py", "c11r_chain.py"):  # the errata quote it; this control
            continue                                       # names it
        scanned += 1
        if overstated in C.read_code(C._rel(f)):
            hits.append(f.name)
    record("WD1", "WD", "the overstated 'nothing re-enables execution' is gone; the printed "
                        "message states the proved scope", expected="ACCEPT",
           refused_at="wording", refused=bool(hits), problems=hits,
           must={"files_scanned": scanned >= 20,
                 "NEXT_STEPS_names_the_scope": "LIFECYCLE_SCOPE" in R.NEXT_STEPS[2],
                 "the_scope_states_what_is_not_covered": "NOT covered" in CT.LIFECYCLE_SCOPE,
                 "the_contract_binds_the_scope":
                     CT.contract_body(C.REPO)["lifecycle"]["scope"] == CT.LIFECYCLE_SCOPE,
                 "guard_comment_no_longer_claims_copies": "a hard link or a renamed copy of "
                 "either under an innocent name is refused" not in C.read_code(
                     f"{C.NS_REL}/code/c11r_common.py")})


def c_LG():
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        auth_commit = C.git_in(ch.root, "rev-parse", "HEAD")
        pf = ch.preflight()
        ch.run(pf["identity"])                             # sealed on the trunk
        C.git_in(ch.root, "checkout", "-q", "-b", "sibling", auth_commit)
        again = ch.preflight()
        record("LG1", "LG", "a SIBLING branch forked at the authorization commit while the first "
                            "seal sits on another branch: the pre-flight refuses",
               expected="REFUSE", refused_at="runner pre-flight", refused=bool(again["problems"]),
               problems=again["problems"], extra={"lifecycle": _state(ch)["state"]})
        ch.run(pf["identity"], restamp=True,               # a second, forced execution
               mutate=lambda b: b.update(note="a second execution on a sibling branch"))
        record_compare("LG2", "LG", "the sibling's second seal is compared: refused",
                       ch.compare())
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        R.begin_execution(ch.root, pf["identity"])
        C.git_in(ch.root, "checkout", "--", PERMISSION_PATH)   # the GRANT restored from git
        st = _state(ch)["state"]
        again = ch.preflight()
        record("LG3", "LG", "STATED LIMIT (LIFECYCLE_SCOPE): an interrupted execution whose "
                            "EXECUTION_STARTED was never committed and the GRANT restored from "
                            "git leaves no trace; the pre-flight passes again -- not claimed",
               expected="ACCEPT", refused_at="runner pre-flight", refused=bool(again["problems"]),
               problems=again["problems"],
               must={"state_is_AUTHORIZED_again": st == "AUTHORIZED",
                     "the_limit_is_stated": "GRANT restored from git" in CT.LIFECYCLE_SCOPE,
                     "the_protocol_instruction_exists": "ABANDONED" in CT.INTERRUPTED_EXECUTION},
               extra={"stated_limit": True})
    finally:
        ch.cleanup()
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        auth_commit = C.git_in(ch.root, "rev-parse", "HEAD")
        pf = ch.preflight()
        ch.branch("attempt")
        R.begin_execution(ch.root, pf["identity"])
        ch.commit_paths([PERMISSION_PATH], "an interrupted execution, committed (ABANDONED)")
        ch.checkout(TRUNK)
        again = ch.preflight()
        record("LG4", "LG", "an execution ABANDONED on another branch; the trunk still holds the "
                            "GRANT: the pre-flight refuses", expected="REFUSE",
               refused_at="runner pre-flight", refused=bool(again["problems"]),
               problems=again["problems"],
               extra={"trunk_is_authorization_commit":
                      C.git_in(ch.root, "rev-parse", "HEAD") == auth_commit})
    finally:
        ch.cleanup()


CONTROLS = (c_R3T, c_unrelated, c_R3A, c_R3B, c_R3C, c_R3D, c_R3E, c_R3F, c_R3G, c_R3H, c_R3I,
            c_R3JKL, c_R3M, c_R3N, c_R3O, c_R3P, c_R3Q, c_R3R, c_R3S, c_real_repository_guard,
            c_MHT, c_LS, c_QF, c_IMP, c_ORD, c_GS, c_CF, c_PB, c_GR, c_DM, c_AC,
            c_R61, c_TP, c_CMP, c_RC, c_CG, c_WD, c_LG)


def main() -> int:
    for f in CONTROLS:
        f()
    failed = [r["id"] for r in RESULTS if not r["pass"]]
    refusals = [r for r in RESULTS if r["expected"] == "REFUSE"]
    post_load = [r for r in RESULTS if r["expected"] == "POST_LOAD_FAILURE"]
    accepts = [r for r in RESULTS if r["expected"] == "ACCEPT" and r["stage"] == "comparator"]
    ordering = all(r["stub_loader_calls"] == 0 for r in refusals) and all(
        r["stub_loader_calls"] == 1 for r in accepts)
    groups = {}
    for r in RESULTS:
        g = groups.setdefault(r["group"], {"controls": 0, "passed": 0})
        g["controls"] += 1
        g["passed"] += int(r["pass"])
    out = {"schema": "C11R_CHAIN_CONTROLS/2",
           "purpose": ("R3-1 and R4-1: the frozen execution identity binds end to end over "
                       "COMPLETE reachable history; N4-5: the loader is reached only by a valid "
                       "chain; N4-4: the typed qualification schema; N4-3: loaded-module "
                       "identity"),
           "synthetic": ("temporary git repositories; fixture Q1-Q18 qualification and "
                         "authorization (accepted only with allow_fixture=True); synthetic "
                         "certificates; a stub magnitude loader; subprocess drivers for the "
                         "loaded-module controls; the quarantine is never copied or opened"),
           "groups": groups,
           "controls": RESULTS,
           "quarantine_access_ordering": {
               "loader_never_called_on_a_refused_chain": ordering,
               "comparator_refusals": sum(1 for r in refusals if r["stage"] == "comparator"),
               "comparator_accepts": len(accepts),
               "rule": "the comparator calls the magnitude loader only after steps 1-12 of "
                       "c11r_compare.STEPS all pass",
               "post_load_controls_documented_separately": {
                   r["id"]: {"loader_calls": r["stub_loader_calls"], "pass": r["pass"],
                             "output_exists": r.get("output_exists")} for r in post_load},
               "post_load_rule": CT.COMPARISON_TRANSACTION},
           "not_covered": [
               CT.LIFECYCLE_SCOPE,
               CT.MODULE_IDENTITY_POLICY["not_covered"]],
           "failed": failed,
           "CHAIN_CLASS": "PASS" if not failed and ordering else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "chain" / "C11R_CHAIN_CONTROLS.json", out,
                         producer=__file__)
    for r in RESULTS:
        print(f"  {'ok  ' if r['pass'] else 'FAIL'} {r['id']:30s} {r['expected']:6s} "
              f"{str(r.get('refused_at_step') or r['stage'])[:26]:26s} "
              f"loader={r['stub_loader_calls']}  {r['attack'][:60]}")
        if not r["pass"]:
            for x in r["problems"]:
                print(f"         - {x}")
            if r.get("required"):
                print(f"         required: {r['required']}")
    print(f"\ngroups: {groups}")
    print(f"quarantine-access ordering holds: {ordering}")
    print(f"CHAIN_CLASS = {out['CHAIN_CLASS']}   failed={failed}")
    print(f"wrote evidence/chain/C11R_CHAIN_CONTROLS.json sha256 {s[:16]}...")
    return 0 if out["CHAIN_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
