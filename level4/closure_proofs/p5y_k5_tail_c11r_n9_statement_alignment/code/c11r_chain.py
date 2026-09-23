"""C11R round 4 -- the R3A-R3T end-to-end identity controls, on SYNTHETIC git repositories.

WHY. Review round 3 (blocker R3-1) broke the execution -> seal -> comparison chain twice: a
certifier edited, committed, used and reverted before the seal was accepted, and a policy edited in
place with its sha256 field left alone passed authorization. These controls replay those exact
attacks, and eighteen more, against the PRODUCTION checks -- c11r_contract (contract, gate,
frozen paths, qualification, authorization, runner pre-flight, run identity), c11r_runs.preflight,
c11r_qualify.emit_qualification and c11r_compare.execute_comparison / verify_seal -- not against
copies of them.

HOW, AND WHAT IS SYNTHETIC. Each control builds a fresh temporary git repository holding byte
copies of every frozen code file and of the bound artifacts, builds the execution contract and the
gate there with the production builders, and commits them as the "approved" commit A. It then
walks the chain -- qualification, authorization, runner pre-flight, run, seal, comparison -- and
applies one attack at one step. Three things are synthetic, and only these:
  * the qualification carries synthetic items and `fixture: true`, and the authorization
    `fixture: true`; the verifiers accept them only when called with allow_fixture=True, which
    only this module passes (a real Phase 13/15 never does);
  * the certificates are c11r_compare.synthetic_certs -- no certifier ran, no value is real;
  * the magnitude loader is a stub returning deliberately round synthetic values, which records
    whether it was called: the controls prove the comparator reaches it ONLY when every identity
    check has passed. The quarantine is never copied and never opened.
The registry the statement table was extracted from is not copied (it is protected); its
content-free id in a synthetic contract is therefore null, consistently on every side.
No target computation happens; no real authorization, qualification or runs artifact is created.
"""
from __future__ import annotations

import copy
import json
import pathlib
import shutil
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
FIXTURE_ITEMS = [{"id": "FX1", "name": "synthetic fixture item", "pass": True, "detail": {}}]


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
        for a in (("init", "-q"), ("config", "user.email", "chain@c11r.invalid"),
                  ("config", "user.name", "c11r chain controls"),
                  ("config", "commit.gpgsign", "false")):
            C.git_in(self.root, *a)
        for rel in CT.closure_paths():
            self.write(rel, CT.code_bytes(C.REPO, rel))
        for rel in COPIED_ARTIFACTS:
            self.write(CT.ns_path(rel), CT.artifact_bytes(C.REPO, rel))
        self.stmt = CT.load_artifact(self.root, CT.STMT_REL)
        self.policy = CT.load_artifact(self.root, CT.POLICY_REL)
        self.approved = self.freeze("approved: synthetic frozen state")

    # -- plumbing -------------------------------------------------------------------------------
    def write(self, rel: str, data: bytes) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def ns(self, rel: str) -> pathlib.Path:
        return self.root / C.NS_REL / rel

    def commit(self, msg: str) -> str:
        C.git_in(self.root, "add", "-A")
        C.git_in(self.root, "commit", "-q", "--allow-empty", "-m", msg)
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

    def qualify(self, mutate=None, items=None, restamp=True) -> None:
        q = C.evidence_body(Q.emit_qualification(self.root, items or FIXTURE_ITEMS, fixture=True),
                            producer=Q.__file__)
        if mutate:
            mutate(q)
            if restamp:
                q["sha256"] = CT.body_digest(q)
        self.write(CT.ns_path(CT.QUAL_REL), _dump(q))
        self.commit("qualification (synthetic fixture)")

    def authorize(self, approved=None, operator="synthetic-fixture", mutate=None) -> list[str]:
        r = CT.build_authorization(self.root, approved_commit=approved or self.approved,
                                   operator=operator, fixture=True)
        if r["problems"] and mutate is None:
            return r["problems"]
        a = r["authorization"]
        if mutate:
            mutate(a)
            a["sha256"] = CT.body_digest(a)
        self.write(CT.ns_path(CT.AUTH_REL), _dump(a))
        self.commit("authorization (synthetic fixture)")
        return r["problems"]

    def preflight(self) -> dict:
        return R.preflight(self.root, allow_fixture=True, check_processes=False)

    def run(self, identity: dict, certs=None, mutate=None) -> dict:
        runs = R.assemble(policy=self.policy, stmt=self.stmt,
                          certs=certs or K.synthetic_certs(self.stmt, self.policy),
                          stop_reason=None, extra={"timings_seconds": {"x": 0.0}},
                          identity=identity)
        body = C.evidence_body(runs, producer=R.__file__)   # exactly what the runner writes
        if mutate:
            mutate(body)
        self.write(CT.ns_path("evidence/runs/C11R_RUNS.json"), _dump(body))
        self.seal = self.commit("seal: runs artifact (synthetic)")
        self.runs_body = body
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
# the controls
# ---------------------------------------------------------------------------------------------
RESULTS: list[dict] = []


# The reason each refusal must carry. A control refused for some OTHER reason proves nothing
# about its attack (the vacuous-control lesson): a refusal counts only if its problems contain
# the expected reason.
EXPECTED_REASON = {
    "R3A": "touched a frozen path", "R3B": "policy", "R3C": "statements", "R3D": "N9R_GATE_C11R",
    "R3E": "qualification: execution_contract_sha256", "R3F": "PASS claimed with failing items",
    "R3G": "authorization: execution_contract_sha256", "R3H": "c11r_runs.py",
    "R3I": "c11r_certificate.py", "R3J": "policy", "R3K": "policy", "R3L": "policy",
    "R3M": "changed after it was sealed", "R3N": "authorization_sha256", "R3O": "policy",
    "R3O_run": "stored sha256", "R3P": "policy: stored sha256", "R3P_run": "stored sha256",
    "R3Q": "c7_gaussian.py", "R3R": "qualification: execution_contract_sha256",
    "R3S": "another approved commit", "GUARD_real_repository": "Phase 15"}


def record(cid, attack, *, expected, refused_at, refused, problems, loader_calls=0, extra=None):
    reason = EXPECTED_REASON.get(cid)
    has_reason = reason is None or any(reason in str(x) for x in (problems or []))
    ok = (refused and has_reason) if expected == "REFUSE" else (not refused)
    RESULTS.append({"id": cid, "attack": attack, "expected": expected,
                    "stage": refused_at, "refused": bool(refused),
                    "expected_reason": reason, "refused_for_the_expected_reason": has_reason,
                    "pass": bool(ok), "stub_loader_calls": loader_calls,
                    "problems": [str(x)[:200] for x in (problems or [])][:8], **(extra or {})})


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


def refused_compare(res: dict) -> bool:
    return res["N9_VERDICT"] == "EXECUTION_INVALID" and res["stub_loader_calls"] == 0


def c_R3T():
    ch = Chain()
    try:
        res = full_valid(ch)
        record("R3T", "all identities correct: the synthetic path runs to a verdict",
               expected="ACCEPT", refused_at="comparator",
               refused=res["N9_VERDICT"] == "EXECUTION_INVALID",
               problems=res["identity_problems"], loader_calls=res["stub_loader_calls"],
               extra={"verdict": res["N9_VERDICT"],
                      "loader_called_exactly_once": res["stub_loader_calls"] == 1})
    finally:
        ch.cleanup()


def c_unrelated():
    ch = Chain()
    try:
        res = full_valid(ch, extra_commit=True)
        record("R3T_unrelated", "an unrelated commit (no frozen path) between approval and seal",
               expected="ACCEPT", refused_at="comparator",
               refused=res["N9_VERDICT"] == "EXECUTION_INVALID",
               problems=res["identity_problems"], loader_calls=res["stub_loader_calls"])
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
        res = ch.compare()
        record("R3A", "certifier edited -> committed -> used -> reverted before the seal",
               expected="REFUSE", refused_at="comparator", refused=refused_compare(res),
               problems=res["identity_problems"], loader_calls=res["stub_loader_calls"],
               extra={"runner_preflight_at_the_edit_refused": bool(at_edit["problems"])})
    finally:
        ch.cleanup()


def _authorize_after(change, cid, attack):
    ch = Chain()
    try:
        ch.qualify()
        change(ch)
        probs = ch.authorize()
        record(cid, attack, expected="REFUSE", refused_at="authorization", refused=bool(probs),
               problems=probs)
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
        record("R3E", "qualification bound to a different contract", expected="REFUSE",
               refused_at="authorization", refused=bool(probs), problems=probs)
    finally:
        ch.cleanup()


def c_R3F():
    ch = Chain()
    try:
        items = [dict(FIXTURE_ITEMS[0]), {"id": "FX2", "name": "failing item", "pass": False,
                                          "detail": {}}]
        ch.qualify(items=items, mutate=lambda q: q.update(QUALIFICATION_CLASS="PASS", failed=[]))
        probs = ch.authorize()
        ch2 = Chain()
        ch2.qualify(mutate=lambda q: q.update(produces_target_constants=True), restamp=False)
        probs2 = ch2.authorize()
        ch2.cleanup()
        record("R3F", "qualification PASS forged over a failing item (re-stamped); and a body "
                      "edited without re-stamping", expected="REFUSE",
               refused_at="authorization",
               refused=bool(probs) and any("stored sha256" in x for x in probs2),
               problems=probs + probs2)
    finally:
        ch.cleanup()


def _preflight_after(change, cid, attack, *, auth_mutate=None):
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize(mutate=auth_mutate)
        if change:
            change(ch)
            ch.commit(f"{cid}: change after authorization")
        pf = ch.preflight()
        record(cid, attack, expected="REFUSE", refused_at="runner pre-flight",
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


def _consistent_policy_edit(ch, change):
    obj = CT.load_artifact(ch.root, CT.POLICY_REL)
    change(obj)
    C.write_evidence(ch.ns(CT.POLICY_REL), {k: v for k, v in obj.items()
                                            if k not in ("sha256", "provenance")},
                     producer=pathlib.Path(C.HERE / "c11r_policy.py"))
    ch.commit("a consistently re-stamped policy after the freeze")


def c_R3JKL():
    for cid, attack, change in (
            ("R3J", "selected depth changed (policy re-stamped)",
             lambda o: o["configuration"]["chosen"].update(depth=6)),
            ("R3K", "selected panel count changed (policy re-stamped)",
             lambda o: o["configuration"]["chosen"].update(panels=16)),
            ("R3L", "resource-cap policy changed (policy re-stamped)",
             lambda o: o["configuration"].update(cap_seconds=10 ** 6))):
        _authorize_after(lambda ch, c=change: _consistent_policy_edit(ch, c), cid, attack)


def _compare_after(cid, attack, run_mutate=None, after_seal=None, identity_change=None):
    ch = Chain()
    try:
        ch.qualify()
        ch.authorize()
        pf = ch.preflight()
        ident = dict(pf["identity"])
        if identity_change:
            identity_change(ch, ident)
        ch.run(ident, mutate=run_mutate)
        if after_seal:
            after_seal(ch)
        res = ch.compare()
        record(cid, attack, expected="REFUSE", refused_at="comparator",
               refused=refused_compare(res), problems=res["identity_problems"],
               loader_calls=res["stub_loader_calls"])
    finally:
        ch.cleanup()


def c_R3M():
    def after(ch):
        obj = copy.deepcopy(ch.runs_body)
        obj["targets"]["Abar"]["value"] = "7"
        obj["sha256"] = CT.body_digest(obj)
        ch.write(CT.ns_path("evidence/runs/C11R_RUNS.json"), _dump(obj))
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
        record("R3R", "qualification stale after a legitimate policy replacement and re-freeze",
               expected="REFUSE", refused_at="authorization", refused=bool(probs),
               problems=probs)
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
        record("R3S", "comparator invoked against a valid-looking seal from the wrong contract",
               expected="REFUSE", refused_at="comparator", refused=refused_compare(wrong),
               problems=wrong["identity_problems"], loader_calls=wrong["stub_loader_calls"],
               extra={"the_same_chain_under_its_own_contract_is_accepted":
                      right["N9_VERDICT"] != "EXECUTION_INVALID" and right["stub_loader_calls"] == 1})
    finally:
        ch.cleanup()


def c_real_repository_guard():
    """The comparator's real-repository path is unreachable from any program but Phase 15."""
    try:
        K.verify_seal(C.REPO)
        refused, why = False, []
    except PermissionError as e:
        refused, why = True, [str(e)]
    record("GUARD_real_repository", "a non-comparator program calls the seal check on the REAL "
                                    "repository", expected="REFUSE", refused_at="runtime guard",
           refused=refused, problems=why)


CONTROLS = (c_R3T, c_unrelated, c_R3A, c_R3B, c_R3C, c_R3D, c_R3E, c_R3F, c_R3G, c_R3H, c_R3I,
            c_R3JKL, c_R3M, c_R3N, c_R3O, c_R3P, c_R3Q, c_R3R, c_R3S, c_real_repository_guard)


def main() -> int:
    for f in CONTROLS:
        f()
    failed = [r["id"] for r in RESULTS if not r["pass"]]
    ordering = all((r["stub_loader_calls"] == 0) for r in RESULTS
                   if r["expected"] == "REFUSE") and all(
        r["stub_loader_calls"] == 1 for r in RESULTS if r["id"] in ("R3T", "R3T_unrelated"))
    out = {"schema": "C11R_CHAIN_CONTROLS/1",
           "purpose": "R3-1: the frozen execution identity binds end to end",
           "synthetic": ("temporary git repositories; fixture qualification and authorization "
                         "(accepted only with allow_fixture=True); synthetic certificates; a stub "
                         "magnitude loader; the quarantine is never copied or opened"),
           "controls": RESULTS,
           "quarantine_access_ordering": {
               "loader_never_called_on_a_refused_chain": ordering,
               "rule": "the comparator calls the magnitude loader only after seal and chain "
                       "verify"},
           "failed": failed,
           "CHAIN_CLASS": "PASS" if not failed and ordering else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "chain" / "C11R_CHAIN_CONTROLS.json", out,
                         producer=__file__)
    for r in RESULTS:
        print(f"  {'ok  ' if r['pass'] else 'FAIL'} {r['id']:22s} {r['expected']:6s} "
              f"{r['stage']:18s} loader={r['stub_loader_calls']}  {r['attack'][:70]}")
        if not r["pass"]:
            for x in r["problems"]:
                print(f"         - {x}")
    print(f"\nquarantine-access ordering holds: {ordering}")
    print(f"CHAIN_CLASS = {out['CHAIN_CLASS']}   failed={failed}")
    print(f"wrote evidence/chain/C11R_CHAIN_CONTROLS.json sha256 {s[:16]}...")
    return 0 if out["CHAIN_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
