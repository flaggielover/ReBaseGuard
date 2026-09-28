"""Cell-307 RLR campaign (r1) -- read-only verification of the starting repository state (campaign brief section 0).

Every item is read from committed evidence on refs of this repository; nothing is inferred from the brief. The script
writes nothing unless --out is given, and never evaluates any cell.

    python3.14 -I -S -B verify_start_state.py [--out PATH]
exit 0 = every item as expected; 1 = a material difference (the campaign must STOP).
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
OV_NS = CP + "p5y_k5_tail_overnight_research"
NS_REL = CP + "p5y_k5_cell307_rlr_r1"
ENV = {"PATH": "/usr/bin:/bin", "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1", "LC_ALL": "C"}

OVERNIGHT_BRANCH = "refs/heads/p5y-k5-tail-overnight-306-309"
OVERNIGHT_HANDOVER = "7f45e048c39023f4805b21a461650fd332af951f"
OVERNIGHT_BASE = "8b9fc0bb"
R5_PATH = CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
R5_BLOB = "f978eeb6b41188eabaf3c6d590c9178d711f1ce6"
STATE_SOURCES = {
    "K1": ("refs/heads/p5y-k1-successor-final-assembly",
           CP + "p5y_k1_successor_final_adjudication/evidence/FINAL_ADJUDICATION.json"),
    "K2_K3": ("refs/heads/p5y-k2-k3-final-closure", CP + "p5y_k2_k3_final_countersignature/FINAL_COUNTERSIGNATURE.json"),
    "K4_P5Y": ("refs/heads/p5y-k4r1-final-closure", CP + "p5y_k4r1_final_adjudication/K4R1_FINAL_VERDICT.json"),
}
C306 = [("9c2cbf21", CP + "p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md",
         "CELL306_NOT_ADOPTED"),
        ("c5324a78", CP + "p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_ADJUDICATION_REVIEW.md",
         "ADJUDICATION_ACCEPTED")]
FLOOR_R2 = [("a15d083b", "floor r2 rule"), ("3fadb422", "REPLACEMENT_FLOOR_ACCEPTED")]
REJECTED_CLOSEOUT = ["08e9acd1", "591b4394", "dfcd8f79", "0d275038", "9f702acb", "8b9fc0bb"]
EXACTLY_ONCE_REFS = {"refs/c12r2/cell306-target-consumed": "dec92e09", "refs/c12r2/cell306-pending-result": "0ac46b3d",
                     "refs/c11rd/r1-execution-consumed": "4b716d43"}
CAMPAIGN_REF_PREFIX = "refs/p5y-k5-cell307-rlr-r1/"
REGISTRY = OV_NS + "/registry/K5_OVERNIGHT_ROUTE_REGISTRY.md"
PROTOCOL_DRAFT = OV_NS + "/streams/C_308/LR/RLR_FREEZE_PROTOCOL_DRAFT.md"


def git(*args) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), *args], capture_output=True, text=True,
                       env=ENV, stdin=subprocess.DEVNULL)
    return p.stdout if p.returncode == 0 else ""


def ok_git(*args) -> bool:
    return subprocess.run(["/usr/bin/git", "-C", str(REPO), *args], capture_output=True, env=ENV,
                          stdin=subprocess.DEVNULL).returncode == 0


def show_json(ref: str, path: str):
    try:
        return json.loads(git("show", f"{ref}:{path}"))
    except ValueError:
        return None


def find(d, keys: set, pre: str = "") -> dict:
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if k in keys and not isinstance(v, (dict, list)):
                out[pre + k] = v
            out.update(find(v, keys, pre + k + "."))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(find(v, keys, pre + str(i) + "."))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    items, fails = {}, []

    def item(name: str, observed, good: bool):
        items[name] = {"observed": observed, "ok": bool(good)}
        if not good:
            fails.append(name)

    head = git("rev-parse", "HEAD").strip()
    item("overnight_branch_tip", git("rev-parse", OVERNIGHT_BRANCH).strip(),
         git("rev-parse", OVERNIGHT_BRANCH).strip() == OVERNIGHT_HANDOVER)
    item("head_descends_from_handover", head, ok_git("merge-base", "--is-ancestor", OVERNIGHT_HANDOVER, "HEAD"))
    item("handover_descends_from_base", OVERNIGHT_BASE,
         ok_git("merge-base", "--is-ancestor", OVERNIGHT_BASE, OVERNIGHT_HANDOVER))
    outside = [p for p in git("diff", "--name-only", OVERNIGHT_BASE, OVERNIGHT_HANDOVER).split()
               if not p.startswith(OV_NS + "/")]
    item("overnight_commits_inside_namespace", outside, outside == [])
    since = [p for p in git("diff", "--name-only", OVERNIGHT_HANDOVER, "HEAD").split() if not p.startswith(NS_REL + "/")]
    item("since_handover_only_campaign_namespace", since, since == [])

    r5_blob = git("rev-parse", f"HEAD:{R5_PATH}").strip()
    r5 = show_json("HEAD", R5_PATH) or {}
    m5 = {c["cell"]: c["verdict"] for c in r5.get("per_m", {}).get("5", {}).get("cells", [])}
    obs = {"blob": r5_blob, "K5_COVERAGE_COMPLETE": r5.get("K5_COVERAGE_COMPLETE"),
           "union_open_ranges": r5.get("union_open_ranges"), "m5_306_309": {k: m5.get(k) for k in (306, 307, 308, 309)}}
    item("r5_authoritative_306_309_open", obs, r5_blob == R5_BLOB and r5.get("K5_COVERAGE_COMPLETE") is False
         and r5.get("union_open_ranges") == [[306, 309]] and all(m5.get(k) != "PASS" for k in (306, 307, 308, 309)))
    r6 = sorted({p for p in git("log", "--all", "--format=", "--name-only").split() if "COVERAGE_MAP_R6" in p})
    item("r6_absent_on_every_ref", r6, r6 == [])

    keys = {"k1_scientific_line", "k1_successor_verdict", "K1", "K2", "K3", "K4", "K5", "P5Y",
            "K4_SCIENTIFIC_LINE", "K4R1_SUCCESSOR_VERDICT"}
    st = {n: find(show_json(ref, path), keys) for n, (ref, path) in STATE_SOURCES.items()}
    k4 = st["K4_P5Y"]
    item("K1_CLOSED", st["K1"], st["K1"].get("scientific_verdict.k1_scientific_line") ==
         "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN" and k4.get("P5Y_STATE.K1") == "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN")
    item("K2_K3_CLOSED", st["K2_K3"], st["K2_K3"].get("status.K2") == "CLOSED" and st["K2_K3"].get("status.K3") ==
         "CLOSED" and k4.get("P5Y_STATE.K2") == "CLOSED" and k4.get("P5Y_STATE.K3") == "CLOSED")
    item("K4_CLOSED", {k: v for k, v in k4.items() if "K4" in k},
         k4.get("K4R1_SUCCESSOR_VERDICT") == "CLOSED" and k4.get("P5Y_STATE.K4") == "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN")
    item("K5_OPEN_P5Y_NOT_YET_CLOSED", {"K5": k4.get("P5Y_STATE.K5"), "P5Y": k4.get("P5Y_STATE.P5Y")},
         k4.get("P5Y_STATE.K5") == "OPEN" and k4.get("P5Y_STATE.P5Y") == "NOT_YET_CLOSED")
    closed_msgs = [ln for ln in git("log", "--all", "--format=%h %s").splitlines()
                   if any(t in ln for t in ("K5 CLOSED", "P5Y CLOSED", "P5Y_CLOSED", "K5_CLOSED"))]
    item("no_ref_records_K5_or_P5Y_closed", closed_msgs, closed_msgs == [])

    c306 = {}
    for commit, path, token in C306:
        text = git("show", f"HEAD:{path}")
        c306[path] = {"ancestor": ok_git("merge-base", "--is-ancestor", commit, "HEAD"),
                      "line2": text.splitlines()[1].strip() if len(text.splitlines()) > 1 else None}
    item("cell306_OPEN_NOT_ADOPTED", c306, all(v["ancestor"] for v in c306.values()) and
         [v["line2"] for v in c306.values()] == [t for _, _, t in C306])
    fl = {c: {"ancestor": ok_git("merge-base", "--is-ancestor", c, "HEAD"), "subject": git("log", "-1", "--format=%s", c)}
          for c, _ in FLOOR_R2}
    item("floor_r2_in_lineage", fl, all(v["ancestor"] for v in fl.values()))
    rc = {c: ok_git("cat-file", "-e", c + "^{commit}") for c in REJECTED_CLOSEOUT}
    item("rejected_closeout_commits_present", rc, all(rc.values()))
    eo = {r: git("rev-parse", "-q", "--verify", r).strip() for r in EXACTLY_ONCE_REFS}
    item("historical_exactly_once_refs_unchanged", eo, all(eo[r].startswith(p) for r, p in EXACTLY_ONCE_REFS.items()))

    refs = git("for-each-ref", "--format=%(refname)").split()
    own_branch = "refs/heads/p5y-k5-cell307-rlr-r1"            # this campaign's working branch (created at the handover)
    branchy = ("refs/heads/", "refs/remotes/", "refs/tags/")
    named = [r for r in refs if r != own_branch and (r.startswith(CAMPAIGN_REF_PREFIX) or "307" in r.split("/")[-1]
                                                     or "rlr" in r.lower())]
    markers = [r for r in named if not r.startswith(branchy)]        # exactly-once markers / pending / result refs
    item("no_cell307_marker_or_result_ref", markers, markers == [])
    # historical branches whose name mentions 307 (e.g. C9, which executed nothing): must lie inside the verified lineage
    hb = {r: ok_git("merge-base", "--is-ancestor", r, "HEAD") for r in named if r.startswith(branchy)}
    item("historical_307_named_branches_inside_lineage", hb, all(hb.values()))
    hist = sorted({p for p in git("log", "--all", "--format=", "--name-only").split()
                   if "CELL307" in p.upper() and "RESULT" in p.upper()})
    item("no_cell307_result_artifact_in_any_history", hist, hist == [])

    reg = git("show", f"HEAD:{REGISTRY}")
    row = next((ln for ln in reg.splitlines() if ln.startswith("| **RLR**")), "")
    draft = git("show", f"HEAD:{PROTOCOL_DRAFT}")
    item("overnight_RLR_FREEZE_READY_closure_only_307", {"registry_row_has_FREEZE_READY": "FREEZE_READY" in row,
                                                         "closure_only": "closure-only" in row,
                                                         "draft_cell_set_307_only": "{307} only" in draft,
                                                         "draft_not_frozen": "DRAFT ONLY. NOT FROZEN" in draft},
         "FREEZE_READY" in row and "closure-only" in row and "{307} only" in draft and "DRAFT ONLY. NOT FROZEN" in draft)

    out = {"schema": "rebaseguard.p5y.k5.cell307-rlr-r1.start-state.v1", "head": head,
           "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "items": items, "material_differences": fails, "pass": not fails}
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    print(f"START STATE {'PASS' if not fails else 'FAIL'}: {len(items) - len(fails)}/{len(items)} items as expected"
          + (f"; differences: {fails}" if fails else ""))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
