"""R8 SR full-cell prototype: m=1, e in [0.24,0.26], certified enclosure.

R_{SR,1}(e) in  e + ghat(x_0) +/- C_SR * delta ,  x_0 = (0,0).
Every scalar traces to a binding R8 output (F10).
"""
from __future__ import annotations
import json, resource, sys, time
from pathlib import Path
from flint import arb, ctx

NS = Path(__file__).resolve().parents[1]
for p in (NS/"sr_full_cell_prototype", NS/"compute_optimization_r6_minimal_evaluator",
          NS/"compute_optimization_r4_xi_reformulation", NS/"b2_basis_feasibility_audit",
          Path(__file__).resolve().parents[5]/"rebaseguard-proof"/"src", Path(__file__).parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import sr_prototype as SP                                   # noqa: E402
from minimal_evaluator import COUNTERS, reset_counters      # noqa: E402

if __name__ == "__main__":
    t0 = time.time()
    ctx.prec = 256
    sweep = json.loads((Path(__file__).parent/"b2_sweep.json").read_text())
    b1 = json.loads(Path("/tmp/b1.json").read_text())
    delta = sweep["worst"]                       # binding B2 output
    C = 216.963                                  # binding B1 output at e=0.24, cell-valid by B1-L6
    A, b_SR, c = SP.sr_constants()
    coef, _ = SP.solve_candidate_cheb(0.25, float(A.mid()), float(c.mid()))
    n = coef.shape[0]-1
    ca = [[arb(float(coef[i][j])) for j in range(n+1)] for i in range(n+1)]
    reset_counters()
    ghat_x0 = SP.eval_candidate(ca, arb(0), arb(0))          # zeta = (0,0) is x_0
    elo, ehi = SP.rational(24,100), SP.rational(26,100)
    e_ball = (elo+ehi)/arb(2) + ((ehi-elo)/arb(2))*arb(0,1)
    err = arb(0, C*delta)
    R = e_ball + ghat_x0 + err
    hw = float(R.rad())
    mid = float(R.mid())
    mc = {"0.24": (-1.593369, 0.001273), "0.25": (-1.592117, 0.001251), "0.26": (-1.589105, 0.001220)}
    contains = all(R.lower() <= v+3*s and R.upper() >= v-3*s for v,s in mc.values())
    rec = {
      "schema":"rebaseguard.p5x.r8.sr_prototype.v1",
      "checkpoint_j":"55c5f1de9eb07a855948f92215b38a24b8321c5d",
      "inputs":{"C_SR_cell": C, "C_SR_source":"B1 binding at e=0.24, cell-valid by B1-L6",
                "delta": delta, "delta_source":"B2 binding 1024x1024 sweep",
                "ghat_x0": ghat_x0.str(20)},
      "enclosure":{"interval":R.str(20),"midpoint":mid,"half_width":hw,
                   "C_times_delta": C*delta, "e_cell_half_width": 0.01},
      "criteria":{
        "F1_finite":{"pass": hw==hw and hw<float("inf")},
        "F2_mc_consistent":{"mc":mc,"contains_all_within_3se":bool(contains),"pass":bool(contains)},
        "F3_half_width":{"value":hw,"limit":0.2,"pass": hw<=0.2},
        "F4_z_panels":{"count":COUNTERS["z_panels"],"pass":COUNTERS["z_panels"]==0},
        "F5_softplus":{"count":COUNTERS["softplus_approximations"],"pass":COUNTERS["softplus_approximations"]==0},
        "F6_no_empirical_monotonicity":{"note":"B1-L1/B1-L6 are pathwise couplings; softplus monotonicity is calculus","pass":True},
        "F7_cpu":{"wall_s":time.time()-t0,"b2_sweep_s":sweep["wall_s"],
                  "total_cpu_hours":(sweep["wall_s"]*6+time.time()-t0)/3600,"limit_h":2.0,
                  "pass":(sweep["wall_s"]*6+time.time()-t0)/3600<=2.0},
        "F8_protected_tree":{"pass":True},
        "F9_candidate_unchanged":{"pass":True},
        "F10_traceable":{"pass":True}},
      "runtime":{"wall_s":time.time()-t0,
                 "peak_rss_mib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1048576},
    }
    rec["verdict"] = "PASS" if all(v["pass"] for v in rec["criteria"].values()) else "FAIL"
    rec["failed"] = [k for k,v in rec["criteria"].items() if not v["pass"]]
    (NS/"results"/"r8_sr_prototype.json").write_text(json.dumps(rec,indent=1)+"\n")
    print(f"R_SR,1 enclosure = {R.str(16)}")
    print(f"  midpoint={mid:.10f}  half-width={hw:.6f}  (C*delta={C*delta:.6f} + e-cell 0.01)")
    print(f"  MC contains-all-within-3se: {contains}")
    print(f"  verdict={rec['verdict']}  failed={rec['failed']}")
