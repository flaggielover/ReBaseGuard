"""Independent reconstruction of the research state at eb9a9c22 (formal campaign p5y_k5_cell309_p309_r1, step 0)."""
import hashlib, json, subprocess, sys
REPO = "/home/user/ReBaseGuard"
RS = "eb9a9c22b093f938e1bf13e0b30512608c58c370"
NS = "level4/closure_proofs/p5y_k5_cell309_research_r1/"
def git(*a, text=True):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, check=True, text=text).stdout
out = {"research_head": RS, "checks": {}, "detail": {}}
man = json.loads(git("show", f"{RS}:{NS}protocol_prep/P309_CANDIDATE_FREEZE_MANIFEST.json"))
bad = []
for p in man["code_pins"]:
    b = subprocess.run(["git", "show", f"{RS}:{p['path']}"], cwd=REPO, capture_output=True, check=True).stdout
    blob = git("rev-parse", f"{RS}:{p['path']}").strip()
    if blob != p["git_blob"] or hashlib.sha256(b).hexdigest() != p["sha256"]:
        bad.append(p["path"])
for p in man["data_pins_blob_only"]:
    if git("rev-parse", f"{RS}:{p['path']}").strip() != p["git_blob"]:
        bad.append(p["path"])
out["checks"]["manifest_pins_match_at_research_head"] = not bad
out["detail"]["manifest_repository_head"] = man["repository_head"]
out["detail"]["code_pins"] = len(man["code_pins"]); out["detail"]["data_pins"] = len(man["data_pins_blob_only"])
out["detail"]["pin_mismatches"] = bad
# package documents changed after the manifest commit?
changed = git("diff", "--name-only", man["repository_head"], RS, "--", NS + "protocol_prep/").split()
out["detail"]["package_files_changed_after_manifest_commit"] = changed
out["checks"]["package_docs_pinned_equal_head"] = not [c for c in changed if c.endswith(("P309_PROTOCOL.md", "P309_FORMAL_PACKAGE.md", "P309_REVIEW_BRIEFS.md", "P309_OWNER_DECISIONS.md"))]
for f, key in (("reviews/REVIEW_SRK_R2.md", "ROUTE_REVIEW: FREEZE_READY"), ("reviews/REVIEW_P309_PACKAGE_R3.md", "PACKAGE_REVIEW: COMPLETE")):
    out["checks"][f"verdict_{f.split('/')[-1]}"] = git("show", f"{RS}:{NS}{f}").splitlines()[1].strip() == key
em = json.loads(git("show", f"{RS}:{NS}evidence/SRK_EVIDENCE_MANIFEST.json"))
out["checks"]["evidence_manifest_complete"] = em["complete"] and em["present_jobs"] == em["declared_jobs"] == 19
vr = json.loads(git("show", f"{RS}:{NS}verify/VERIFY_RESULTS.json"))
s = vr["summary"]
out["detail"]["verify_summary"] = {"certificates": s["certificates"], "ACCEPT": s["ACCEPT"], "v2_run": s["by_harness"]["v2"]["mutants_run"], "v2_met": s["by_harness"]["v2"]["mutant_expectations_met"]}
out["checks"]["verifier_all_accept_v2_all_met"] = s["ACCEPT"] == s["certificates"] == 107 and s["by_harness"]["v2"]["mutants_run"] == s["by_harness"]["v2"]["mutant_expectations_met"]
out["ok"] = all(out["checks"].values())
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
