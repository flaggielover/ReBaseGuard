# DECOY-ONLY: barrier-1 refusals of the sandbox's own frozen verifier at the (decoy) freeze state with planted artifacts.
import importlib.util, json, sys
from pathlib import Path
SCR = Path(sys.argv[1]).resolve()
V_PATH = "/Users/suzhe/ReBaseGuard-k5c11rd/level4/closure_proofs/p5y_k5_tail_c12r1_cell306_adoption/code/c12r1_verify.py"
spec = importlib.util.spec_from_file_location("v_probe", V_PATH); V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
D0 = V.load_driver("c12r1_pre"); fz = D0.freeze_commit(); assert fz.startswith("5cfe336a")
root = SCR / "sbx2"; root.mkdir(parents=True, exist_ok=True)
sb, pins, blobs = V.make_decoy_sandbox(root, fz)
assert all(json.loads(sb.p(r).read_text()).get("DECOY") is True for r in (V.C11R_CMP, V.C11RD_CMP, V.C11RD_RUNS))
NS = V.NS_REL
def plant_file(rel, text="{}"):
    def f():
        sb.p(rel).parent.mkdir(parents=True, exist_ok=True); sb.p(rel).write_text(text)
    return f
def side_branch_grant():
    sb.g("checkout", "-q", "-b", "side")
    plant_file(D0.GRANT_REL)(); sb.commit_all("side grant")
    sb.g("checkout", "-q", "-f", "campaign")
cases = [("own result on disk", plant_file(D0.RESULT_REL)),
         ("grant on disk (uncommitted)", plant_file(D0.GRANT_REL)),
         ("adjudication on disk", plant_file(NS + "/adjudication/C12R1_ADOPTION_ADJUDICATION.md", "# x\nCELL306_ADOPTED\n")),
         ("r6 in evidence/coverage", plant_file(NS + "/evidence/coverage/K5_COVERAGE_MAP_R6.json")),
         ("grant only in history of a side branch", side_branch_grant),
         ("empty evidence/execution directory", lambda: sb.p(NS + "/evidence/execution").mkdir(parents=True))]
out = {}
for label, setup in cases:
    sb.reset()
    for br in ("side",):
        sb.g("branch", "-q", "-D", br)
    setup()
    code, text = V.run_cli(sb.root, "c12r1_verify.py", "--review", "--out", str(SCR / "nested.json"))
    out[label] = {"exit": code, "refused": "VERIFY REFUSED" in text, "reason": text.strip().splitlines()[-1][:140] if text.strip() else ""}
sb.reset()
print(json.dumps(out, indent=1))
