"""C11RD -- the comparator. Runs ONCE, only after the sealed execution was reviewed EXECUTION_ACCEPTED
(freeze section U). Nothing runs at import; no original magnitude is loaded before step U5.

    python3 -I -S -B c11rd_compare.py --seal-commit SHA --execution-review-commit SHA

U0 RUN ONCE. No comparison artifact on disk AND none ever in reachable history (any ref, any reflog
   entry, full history: committed-then-deleted, reverted, or introduced on a merged or unmerged side
   branch) -- c11rd_model.history_commits, which ignores replace refs, does not trust a commit-graph
   and REFUSES a shallow repository, a grafts file or any git error.
U1 SEAL. evidence/runs/C11RD_RUNS.json at HEAD is byte-identical to the file at the seal commit; the
   seal commit descends from the runs artifact's freeze commit; the review commit descends from the
   seal commit and its tree holds review/C11RD_EXECUTION_REVIEW.md whose verdict line is exactly
   EXECUTION_ACCEPTED.
U2 IDENTITY. The runs artifact's code hashes equal the freeze's; a status other than CERTIFIED makes
   both targets INSUFFICIENT (no number is compared).
U3 RECOMPUTATION. Each sub-block bound is recomputed exactly from its recorded lam, atom candidate
   values and half-width, the premise and the kernel norms; the sub-blocks tile the cell block
   exactly; the cell value is their maximum. Any mismatch: INVALID.
U4 STATEMENT BEFORE NUMBER. C11R's statement-equivalence semantics (mirrored here; fidelity to
   C11R's own frozen functions is validation V19): exact fields, drift domain as exact rationals,
   premises as sets with the _independent suffix normalised. Not EQUIVALENT/STRONGER: INVALID.
U5 NUMBER. Only now are the originals loaded -- from C11R's quarantine, blob-bound -- and each target
   classified by the factor-2 rule C11R froze before any result (factor read from C11R's statement
   table and required to be 2).
U6 An independent value EXACTLY equal to the original is INVALID (copied, not certified).
U7 POST-HOC LEAK CHECK. No file of the C11RD namespace at the freeze commit contains the original D1
   or D2 rendered with 4 or more significant digits: decimal tokens, tokens with a bare leading point
   and scientific notation are normalised to plain decimals first (exact rational strings are not
   scanned: see the freeze's N-9 disposition).
U8 N9 REASSEMBLY. The C_T, tau, Abar and D_lo classes are READ from C11R's accepted comparison
   (blob-bound, never recomputed) and combined with D1, D2 by C11R's precedence:
   INDEPENDENCE_VIOLATION > SCIENTIFIC_DISAGREEMENT > EXECUTION_INVALID > N9_CLOSED >
   AGREEMENT_INSUFFICIENT; N9_CLOSED iff all six are AGREES or STRONGER.
The artifact evidence/comparison/C11RD_COMPARISON.json is written once (exclusive create) after the
classification; a refusal before U5 writes nothing and exits 3.
"""
# ---- PRE-IMPORT BARRIER (must stay the first statements; builtin modules only: `sys` and `posix`
# are built into the interpreter and cannot be shadowed from any path). Before ANY other import it
# refuses unless: the interpreter runs isolated (-I), without site (-S), without writing bytecode
# (-B) and without a pycache prefix; this code directory holds exactly the frozen files (no
# __pycache__, no .pyc, nothing else); and C7's code directory (which c11rd_tm puts on sys.path)
# holds no __pycache__, no .pyc and no file or directory named like a standard-library module. With
# no bytecode anywhere on those two directories, every module they supply runs from its source.
import sys
import posix

CODE_FILES = frozenset({"c11rd_certify.py", "c11rd_compare.py", "c11rd_float.py", "c11rd_kernel.py",
                        "c11rd_model.py", "c11rd_runs.py", "c11rd_tm.py", "c11rd_validate.py"})


def _preimport_barrier(main_file: str) -> tuple:
    f = main_file if main_file.startswith("/") else posix.getcwd() + "/" + main_file
    code_dir = f.rpartition("/")[0]
    c7_dir = code_dir.rpartition("/")[0].rpartition("/")[0] + "/p5y_k5_tail_c7_e2_lambda309/code"
    problems = []
    fl = sys.flags
    if not (fl.isolated and fl.no_site and fl.dont_write_bytecode) or sys.pycache_prefix is not None:
        problems.append("the interpreter must run as `python3 -I -S -B` without a pycache prefix")
    have = set(posix.listdir(code_dir))
    if have != CODE_FILES:
        problems.append(f"code directory entries differ from the frozen files: extra {sorted(have - CODE_FILES)}, "
                        f"missing {sorted(CODE_FILES - have)}")
    std = sys.stdlib_module_names
    for name in posix.listdir(c7_dir):
        stem = name[:-3] if name.endswith(".py") else name
        if name == "__pycache__" or name.endswith(".pyc") or stem in std:
            problems.append(f"C7 code directory holds {name!r}")
    if problems:
        raise SystemExit("REFUSE R0 (pre-import barrier): " + "; ".join(problems))
    return code_dir, c7_dir


_CODE_DIR, _C7_DIR = _preimport_barrier(__file__)
# ---- end of the barrier; ordinary imports follow
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c11rd_certify as CE  # noqa: E402
import c11rd_model as MD  # noqa: E402

NS = HERE.parent
RUNS_REL = "evidence/runs/C11RD_RUNS.json"
FREEZE_REL = "protocol/C11RD_FREEZE_R1.json"
REVIEW_REL = "review/C11RD_EXECUTION_REVIEW.md"
OUT_REL = "evidence/comparison/C11RD_COMPARISON.json"
QUARANTINE_REL = f"{MD.C11R_NS}/evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json"
QUARANTINE_BLOB = "219e0122a7febf4347ce9205e5e5ed9f18b20ffb"
C11R_COMPARISON_REL = f"{MD.C11R_NS}/evidence/comparison/C11R_COMPARISON.json"
C11R_COMPARISON_BLOB = "5269c2aaa354385b714c669ec516ecc22f36c59d"
FACTOR = 2
SIX = ("C_T", "tau", "Abar", "D_lo", "D1", "D2")
PRECEDENCE = ("INDEPENDENCE_VIOLATION", "SCIENTIFIC_DISAGREEMENT", "EXECUTION_INVALID", "N9_CLOSED",
              "AGREEMENT_INSUFFICIENT")

# C11R's frozen schema constants that the equivalence uses (c11r_schema; equality is V19)
EXACT_FIELDS = ("constant", "quantity", "kernel", "convention", "direction", "state_set", "proposition")
STATEMENT_FIELDS = EXACT_FIELDS + ("drift_domain", "aggregation", "dependencies", "producer")
CONVENTION = {"K_e": "full", "Khat_e": "atom_removed"}
VALID_AGGREGATION = {"UPPER_BOUND": {"max_over_sub_blocks", "single_certificate_whole_block"},
                     "LOWER_BOUND": {"min_over_sub_blocks", "single_certificate_whole_block"}}
ROUTE_REQUIRED_DEPENDENCIES = {"independent_derivative_propagation": frozenset({"C_T_independent",
                                                                              "tau_independent"})}
ROUTE_CAN_PRODUCE = {"independent_derivative_propagation": frozenset({"D_lo", "D1", "D2"})}
INDEPENDENT_ROUTES = frozenset({"independent_supersolution", "independent_subsolution",
                                "independent_derivative_propagation"})
FORBIDDEN_PRODUCERS = frozenset({"taboo_certify", "resolvent_certificate", "opnorms", "ra_certifier",
                                 "fast_range", "intervals", "rebaseguard_certify", "rung3_engine", "spec"})


class Refusal(Exception):
    pass


def git(*args, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "--no-replace-objects", "-c", "core.commitGraph=false", "-C", str(MD.REPO),
                           *args], capture_output=True, text=True, check=check)


# ---------------------------------------------------------------------------------------------
# pure functions (self-tested; V19 checks them against C11R's own frozen functions)
# ---------------------------------------------------------------------------------------------
def check_internal(st: dict) -> list:
    p = [f"missing field {f!r}" for f in STATEMENT_FIELDS if f not in st]
    if p:
        return p
    if CONVENTION.get(st["kernel"]) != st["convention"]:
        p.append(f"kernel {st['kernel']} requires convention {CONVENTION.get(st['kernel'])!r}")
    if st["aggregation"].get("method") not in VALID_AGGREGATION.get(st["direction"], set()):
        p.append(f"aggregation {st['aggregation'].get('method')!r} does not preserve 'for every e'")
    prod = st["producer"]
    route = prod.get("route")
    if route not in INDEPENDENT_ROUTES:
        p.append(f"route {route!r} is not an independent route")
    mod = str(prod.get("module", "")).split(".")[0].split("/")[-1].removesuffix(".py")
    if mod in FORBIDDEN_PRODUCERS:
        p.append(f"producer {prod.get('module')!r} is in the original's load-bearing graph")
    if not prod.get("file_sha256"):
        p.append("producer declares no file hash")
    if st["constant"] not in ROUTE_CAN_PRODUCE.get(route, frozenset()):
        p.append(f"route {route!r} cannot produce {st['constant']!r}")
    missing = sorted(ROUTE_REQUIRED_DEPENDENCIES.get(route, frozenset()) - set(st["dependencies"]))
    if missing:
        p.append(f"route {route!r} necessarily consumes {missing}, which the record omits")
    originals = sorted(d for d in st["dependencies"] if d in SIX)
    if originals:
        p.append(f"depends on ORIGINAL constants {originals} -- an independence violation")
    return p


def _domain(orig: list, indep: list) -> str:
    olo, ohi, ilo, ihi = F(orig[0]), F(orig[1]), F(indep[0]), F(indep[1])
    if (ilo, ihi) == (olo, ohi):
        return "EQUAL"
    if ilo <= olo and ihi >= ohi:
        return "SUPERSET"
    if ilo >= olo and ihi <= ohi:
        return "SUBSET"
    return "INCOMPARABLE"


def _premises(orig: list, indep: list) -> str:
    norm, o = {d.removesuffix("_independent") for d in indep}, set(orig)
    if norm == o:
        return "SAME"
    if norm < o:
        return "FEWER"
    if norm > o:
        return "MORE"
    return "DIFFERENT"


def compare_statement(orig: dict, indep: dict | None) -> dict:
    if indep is None:
        return {"STATUS": "NO_INDEPENDENT_STATEMENT"}
    internal = check_internal(indep)
    if internal:
        return {"STATUS": "INVALID", "reasons": internal,
                "independence_violation": any("independence violation" in r or "load-bearing graph" in r
                                              for r in internal)}
    mism = [f for f in EXACT_FIELDS if orig.get(f) != indep.get(f)]
    if mism:
        return {"STATUS": "NOT_EQUIVALENT", "field_mismatches": mism}
    dom, prem = _domain(orig["drift_domain"], indep["drift_domain"]), _premises(orig["dependencies"],
                                                                                  indep["dependencies"])
    if dom == "INCOMPARABLE" or prem == "DIFFERENT":
        status = "NOT_COMPARABLE"
    else:
        stronger, weaker = dom == "SUPERSET" or prem == "FEWER", dom == "SUBSET" or prem == "MORE"
        status = "NOT_COMPARABLE" if stronger and weaker else "WEAKER" if weaker else \
            "STRONGER" if stronger else "EQUIVALENT"
    return {"STATUS": status, "domain": dom, "premises": prem}


def classify_numeric(direction: str, indep: F, orig: F, factor: int = FACTOR) -> str:
    if direction == "UPPER_BOUND":
        if indep <= orig:
            return "STRONGER"
        return "AGREES" if indep <= factor * orig else "INSUFFICIENT"
    if direction == "LOWER_BOUND":
        if indep >= orig:
            return "STRONGER"
        return "AGREES" if indep * factor >= orig else "INSUFFICIENT"
    raise ValueError(f"unknown direction {direction!r}")


def n9_verdict(classes: dict, violations: list) -> str:
    if violations:
        return "INDEPENDENCE_VIOLATION"
    if any(c == "DISAGREES" for c in classes.values()):
        return "SCIENTIFIC_DISAGREEMENT"
    if any(c == "INVALID" for c in classes.values()):
        return "EXECUTION_INVALID"
    if all(c in ("AGREES", "STRONGER") for c in classes.values()):
        return "N9_CLOSED"
    return "AGREEMENT_INSUFFICIENT"


def recompute(runs: dict, premise: dict, kappa: dict, block: tuple) -> list:
    """U3: every recorded bound, recomputed exactly from its own ingredients. Returns problems."""
    ex = runs["execution"]
    subs = ex["sub_blocks"]
    p = []
    lo, hi = block
    edges = [(F(s["e_lo"]), F(s["e_hi"])) for s in subs]
    if not edges or edges[0][0] != lo or edges[-1][1] != hi or \
            any(edges[i][1] != edges[i + 1][0] for i in range(len(edges) - 1)) or any(a >= b for a, b in edges):
        p.append("the sub-blocks do not tile the cell block exactly")
    D1 = D2 = None
    for i, s in enumerate(subs):
        a, b = F(s["e_lo"]), F(s["e_hi"])
        de = (b - a) / 2
        at = [F(x) for x in s["atom_candidate_values"]]
        d1a = abs(at[1]) + abs(at[2]) * de + abs(at[3]) / 2 * de ** 2
        d2a = abs(at[2]) + abs(at[3]) * de
        pr = CE.propagate([F(x) for x in s["lam"]], premise["C_T"], premise["tau"], kappa)
        if F(s["D1"]) != d1a + pr["err_D1"] or F(s["D2"]) != d2a + pr["err_D2"]:
            p.append(f"sub-block {i}: the recorded bound is not the recomputed one")
        cand0 = s["candidates"]["D0"]["0"]
        for j in range(4):
            if F(s["candidates"][f"D{j}"]["0"].get("0,0", "0")) != at[j]:
                p.append(f"sub-block {i}: atom value D{j}(a) is not the band-0 constant of its candidate")
        del cand0
        D1 = F(s["D1"]) if D1 is None else max(D1, F(s["D1"]))
        D2 = F(s["D2"]) if D2 is None else max(D2, F(s["D2"]))
    for k, v in (("D1", D1), ("D2", D2)):
        if runs["targets"][k]["value"] is None or F(runs["targets"][k]["value"]) != v:
            p.append(f"{k}: the cell value is not the maximum over the sub-blocks")
    return p


NUMERIC_TOKEN = re.compile(r"(?<![0-9.])([0-9]*[.][0-9]+)(?:[eE]([+-]?[0-9]+))?")


def normalized_numeric_tokens(text: str) -> list:
    """Every decimal token of `text` as a plain decimal string: '.25' -> '0.25', '4.5e-01' -> '0.45'."""
    from decimal import Decimal
    out = []
    for mant, exp in NUMERIC_TOKEN.findall(text):
        if mant.startswith("."):
            mant = "0" + mant
        if exp:
            try:
                d = Decimal(mant).scaleb(int(exp))
            except (ArithmeticError, ValueError):
                continue
            mant = format(d, "f")
            if "." not in mant:
                continue
        out.append(mant)
    return out


def value_patterns(s: str) -> set:
    """Every rendering of the decimal string s that carries >= 4 significant digits: its truncations
    and its roundings to 4..9 significant digits."""
    first = next(i for i, ch in enumerate(s) if ch not in "0.")
    out = set()
    for end in range(first + 1, len(s) + 1):
        if s[end - 1].isdigit() and sum(ch.isdigit() for ch in s[first:end]) >= 4:
            out.add(s[:end])
    for n in range(4, 10):
        out.add(format(float(s), f".{n}g"))
    return out


def token_prefixes(tok: str) -> set:
    return {tok[:i] for i in range(1, len(tok) + 1) if tok[i - 1].isdigit()}


def leak_hits(texts: dict, originals: dict) -> dict:
    """U7: {file: [constants]} for every file with a numeric token that STARTS with a rendering of an
    original value (a token boundary precedes it: no digit or point)."""
    pats = {k: value_patterns(v) for k, v in originals.items()}
    hits = {}
    for name, txt in texts.items():
        for tok in normalized_numeric_tokens(txt):
            pre = token_prefixes(tok)
            for k, ps in pats.items():
                if pre & ps and k not in hits.get(name, []):
                    hits.setdefault(name, []).append(k)
    return hits


# ---------------------------------------------------------------------------------------------
# the transaction
# ---------------------------------------------------------------------------------------------
def blob_at(commit: str, rel: str) -> str | None:
    r = git("rev-parse", f"{commit}:{rel}", check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def verify_own_code(fz: dict) -> None:
    """U2: the comparator runs only as frozen -- every C11RD code file (itself included) and C7's
    c7_gaussian.py have the sha256 the freeze recorded."""
    bad = sorted(rel for rel, h in fz["code_sha256"].items()
                 if hashlib.sha256((NS / rel).read_bytes()).hexdigest() != h)
    c7 = fz["input_bindings"]["c7_gaussian"]
    if hashlib.sha256((MD.REPO / c7["path"]).read_bytes()).hexdigest() != c7["sha256"]:
        bad.append("c7_gaussian")
    if bad:
        raise Refusal(f"U2: code differs from the freeze: {bad}")


def verify_seal(seal: str, review: str) -> dict:
    runs_rel = f"{MD.NS_REL}/{RUNS_REL}"
    disk = (NS / RUNS_REL).read_bytes()
    committed = subprocess.run(["git", "--no-replace-objects", "-c", "core.commitGraph=false", "-C", str(MD.REPO),
                                "show", f"{seal}:{runs_rel}"], capture_output=True).stdout
    if disk != committed:
        raise Refusal("U1: the runs artifact differs from the sealed one")
    runs = json.loads(disk)
    fc = runs.get("freeze_commit", "")
    for anc, desc, what in ((fc, seal, "the freeze commit is not an ancestor of the seal"),
                            (seal, review, "the seal is not an ancestor of the review commit"),
                            (review, "HEAD", "the review commit is not an ancestor of HEAD")):
        if git("merge-base", "--is-ancestor", anc, desc, check=False).returncode != 0:
            raise Refusal(f"U1: {what}")
    rv = git("show", f"{review}:{MD.NS_REL}/{REVIEW_REL}", check=False)
    verdicts = [ln.strip() for ln in rv.stdout.splitlines() if ln.strip() in ("EXECUTION_ACCEPTED",
                                                                                "EXECUTION_REJECTED")]
    if rv.returncode != 0 or verdicts != ["EXECUTION_ACCEPTED"]:
        raise Refusal("U1: the review commit does not hold exactly one EXECUTION_ACCEPTED verdict line")
    fz = json.loads(git("show", f"{fc}:{MD.NS_REL}/{FREEZE_REL}").stdout)
    verify_own_code(fz)
    if runs.get("code_sha256") != fz["code_sha256"]:
        raise Refusal("U2: the run's code hashes are not the freeze's")
    return {"runs": runs, "freeze": fz, "freeze_commit": fc}


def run_once_problems(repo=None, ns=None, ns_rel: str | None = None) -> list:
    """U0: the comparison may run only if its artifact is absent from disk AND from every reachable
    history (fail-closed on an incomplete or unreadable history)."""
    ns = pathlib.Path(ns or NS)
    rel = f"{ns_rel or MD.NS_REL}/{OUT_REL}"
    p = []
    if os.path.lexists(ns / OUT_REL):
        p.append("a comparison artifact exists on disk")
    try:
        hist = MD.history_commits([rel], repo=repo)
    except MD.ModelError as exc:
        return p + [f"history is ambiguous: {exc}"]
    if hist:
        p.append(f"a comparison artifact was in reachable history ({len(hist)} commits, e.g. {hist[0][:12]})")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seal-commit", required=True)
    ap.add_argument("--execution-review-commit", required=True)
    a = ap.parse_args(argv)
    out_path = NS / OUT_REL
    once = run_once_problems()
    if once:
        print(f"REFUSE U0: the comparison has already run or cannot be shown not to have: {once}")
        return 3
    try:
        s = verify_seal(a.seal_commit, a.execution_review_commit)
        runs, fc = s["runs"], s["freeze_commit"]
        premise = MD.c11r_fh_premise()
        kappa = MD.kernel_norms()
        block = MD.cell_block()
        table = MD._load_bound(MD.STATEMENT_TABLE_REL, MD.STATEMENT_TABLE_BLOB)
        rule = MD.comparison_rule(table)
        if rule.get("factor") != FACTOR:
            raise Refusal("U5: C11R's frozen factor is not 2")
        orig_st = {k: table["original_statements"][k] for k in ("D1", "D2")}
        per, violations = {}, []
        if runs.get("status") != "CERTIFIED":
            for k in ("D1", "D2"):
                per[k] = {"CLASS": "INSUFFICIENT", "why": f"run status {runs.get('status')}"}
        else:
            probs = recompute(runs, premise, kappa, block)
            for k in ("D1", "D2"):
                cmp = compare_statement(orig_st[k], runs["targets"][k]["statement"])
                if cmp.get("independence_violation"):
                    violations.append(k)
                if probs:
                    per[k] = {"CLASS": "INVALID", "why": probs, "statement": cmp}
                elif cmp["STATUS"] not in ("EQUIVALENT", "STRONGER"):
                    per[k] = {"CLASS": "INVALID", "why": f"statement {cmp['STATUS']}", "statement": cmp}
                else:
                    per[k] = {"CLASS": None, "statement": cmp, "independent_value": runs["targets"][k]["value"],
                              "direction": orig_st[k]["direction"]}
    except Refusal as exc:
        print(f"REFUSED before the originals were loaded: {exc}")
        return 3
    # ---- U5: the originals, loaded only now ----
    if MD.git_blob(MD.REPO / QUARANTINE_REL) != QUARANTINE_BLOB:
        print("REFUSED: C11R's quarantine is not the frozen blob")
        return 3
    q = json.loads((MD.REPO / QUARANTINE_REL).read_text())
    mags = {k: F(q["magnitudes"][k]["value"]) for k in ("D1", "D2")}
    for k in ("D1", "D2"):
        rec = per[k]
        rec["original_value"] = str(mags[k])
        if rec["CLASS"] is None:
            v, o = F(rec["independent_value"]), mags[k]
            if v == o:
                rec.update(CLASS="INVALID", why="equal to the original EXACTLY -- copied, not certified")
            else:
                num = classify_numeric(rec["direction"], v, o)
                rec.update(CLASS=num, numeric={"class": num, "ratio": str(v / o), "ratio_float": float(v / o),
                                               "factor": FACTOR})
    # ---- U7: post-hoc leak check over the namespace at the freeze commit ----
    names = git("ls-tree", "-r", "--name-only", fc, "--", MD.NS_REL).stdout.split()
    texts = {n: git("show", f"{fc}:{n}").stdout for n in names}
    leaks = leak_hits(texts, {k: format(float(v), ".9f") for k, v in mags.items()})
    if leaks:
        for k in ("D1", "D2"):
            per[k].update(CLASS="INVALID", why=f"U7: original values found in frozen files {sorted(leaks)}")
    # ---- U8: N9 reassembly ----
    if MD.git_blob(MD.REPO / C11R_COMPARISON_REL) != C11R_COMPARISON_BLOB:
        print("POST-LOAD FAILURE: C11R's comparison is not the frozen blob")
        return 4
    c11r = json.loads((MD.REPO / C11R_COMPARISON_REL).read_text())
    classes = {k: c11r["result"]["per_target"][k]["CLASS"] for k in ("C_T", "tau", "Abar", "D_lo")}
    classes.update({k: per[k]["CLASS"] for k in ("D1", "D2")})
    verdict = n9_verdict(classes, violations)
    body = {"schema": "c11rd.comparison.v1", "seal_commit": a.seal_commit,
            "execution_review_commit": a.execution_review_commit, "freeze_commit": fc,
            "per_target": per, "classes": classes, "classes_source": {
                "C_T, tau, Abar, D_lo": f"C11R accepted comparison {C11R_COMPARISON_REL} @ blob {C11R_COMPARISON_BLOB}",
                "D1, D2": "this comparison"},
            "independence_violations": violations, "leak_check": {"hits": leaks, "files": len(texts)},
            "factor": FACTOR, "precedence": list(PRECEDENCE), "N9_VERDICT": verdict}
    body["sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "x") as fh:
        fh.write(json.dumps(body, indent=1, sort_keys=True) + "\n")
    print(f"N9_VERDICT = {verdict}; D1 {per['D1']['CLASS']}, D2 {per['D2']['CLASS']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
