"""Cross-host scientific qualification runner. Identical bytes on every host.
Result-free: produces no production SR cell record."""
import hashlib, json, sys, time
from pathlib import Path

ROOT = Path(sys.argv[1])
HOST = sys.argv[2]
CP = ROOT / "level4/closure_proofs"
for p in (CP / "p5y_k1_sr_backend_cost_audit/code",
          CP / "p5y_k1_task1r_budget_harness/code",
          CP / "p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic",
          ROOT / "rebaseguard-proof/src"):
    sys.path.insert(0, str(p))

from flint import arb, ctx
import harness as H, sr_local as L, opt_backend as OB
from rebaseguard_certify.arb_backend import rational

par = json.loads((CP / "p5y_k1_task1r_budget_harness/config/frozen_parameters.json"
                  ).read_text())["selection"]
D, Z = par["D_selected"], par["Z_selected"]
ctx.prec = H.PROD_BITS
PATCH = (17, 11)
E = rational(H.E_NUM, H.E_DEN)


def geom_for(patch, e):
    A, b, c = L.sr_constants()
    geo = L.patch_geometry(*patch, grid=H.GRID)
    p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
    m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
    Hh = (geo["yp"][1] - geo["yp"][0]) / arb(2)
    U_c, L_c = c - p_c, m_c - c
    return dict(A=A, b=b, c=c, e=e, geo=geo, p_c=p_c, m_c=m_c, H=Hh,
                U_c=U_c, L_c=L_c, span=U_c - L_c)


def rnd_cand(s):
    import random
    random.seed(s)
    n = H.CAND_DEGREE + 1
    return [[arb(random.randint(-50, 50)) / arb(97) for _ in range(n)] for _ in range(n)]


def ball(x):
    x = arb(x)
    m, me = x.mid().man_exp()
    r, re_ = x.rad().man_exp()
    return [[str(int(m)), str(int(me))], [str(int(r)), str(int(re_))]]


g = geom_for(PATCH, E)
p1 = H.p1_rule(g["H"], g["span"])
n_z = p1["n_panels"]
Hh, L_c = g["H"], g["L_c"]
h = g["span"] / (arb(2) * arb(n_z))
ctxt = (Hh, h, D, Z, [Hh ** a for a in range(2 * D + 2)],
        [h ** k for k in range(2 * Z + 2)])
Dp = D + 1

out = {"host": HOST, "n_panels": n_z, "D": D, "Z": Z,
       "precision_bits": H.PROD_BITS, "contract": [], "selection": []}


def panel_drift(shift):
    z_lo = L_c + arb(2) * arb(shift) * h
    z_c = z_lo + h
    z_hi = z_lo + arb(2) * h
    sh = OB.PanelShared(g["p_c"], g["m_c"], z_c, g["b"], ctxt)
    Nf = H.panel_moments(z_lo, z_hi, z_c, E, 2 * Z + 4, h)
    return OB.PanelDrift(sh, Nf)


t_contract = []
for shift in (0, 1, 2, 3):
    pd = panel_drift(shift)
    for seed in (0, 1, 2):
        cand = rnd_cand(seed)
        t0 = time.process_time()
        coef, ex, ez = OB.contract(pd, cand)
        t_contract.append(time.process_time() - t0)
        out["contract"].append({
            "moment_shift": shift, "seed": seed,
            "coef": [[ball(coef[a][bq]) for bq in range(Dp)] for a in range(Dp)],
            "err_x": ball(ex), "err_z": ball(ez), "N0": ball(pd.N0)})

for tag, cell, cu in (("EASY", 315, "8589984305/4294967296"),
                      ("MIDDLE", 157, "1714657327304/4294967296"),
                      ("DIFFICULT", 0, "5179460569968/4294967296")):
    num, den = cu.split("/")
    C_SR = int(num) / int(den)
    sel = H.select_parameters(g, p1, C_SR)
    ser = {}
    for k in sorted(sel):
        v = sel[k]
        ser[k] = ball(v) if isinstance(v, arb) else (
            v if isinstance(v, (int, str, bool, type(None))) else repr(v))
    out["selection"].append({"tier": tag, "cell": cell, "C_upper": cu,
                             "C_SR_float": repr(C_SR), "selected": ser})

blob = json.dumps({k: out[k] for k in ("contract", "selection", "n_panels",
                                       "D", "Z", "precision_bits")},
                  sort_keys=True, separators=(",", ":")).encode()
out["SCIENTIFIC_HASH"] = hashlib.sha256(blob).hexdigest()
out["median_contract_s"] = sorted(t_contract)[len(t_contract) // 2]
Path(sys.argv[3]).write_text(json.dumps(out, sort_keys=True, indent=1))
print("HOST              :", HOST)
print("n_panels          :", n_z)
print("contracts recorded:", len(out["contract"]))
print("median contract s :", out["median_contract_s"])
print("SCIENTIFIC_HASH   :", out["SCIENTIFIC_HASH"])
