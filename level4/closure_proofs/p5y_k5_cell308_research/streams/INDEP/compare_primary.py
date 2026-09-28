"""compare_primary.py -- Stream F2 V2 (comparison with the primary) and V3 (planted mutants) harness.

This file MAY import the primary; mb_independent.py may not. Everything here is synthetic / decoy only:
  * decoys: regenerated IN MEMORY by streams/ASSEMBLY/decoy_gen.decoy_set() (labels DECOY, cells 9000+i, geometry
    outside the drift band and its mirror); primary outputs from streams/ASSEMBLY/tptb_tail.evaluate_bundle;
  * committed-format reference functions, reached ONLY through the primary's frozen-path loader (loaded by path under
    c308E_fp_* names, sha256-pinned; the historical module names are never imported):
      L1  deflated_consume.atom_constants_r2 (frozen Dv' r2 reference, kappa defaults K1_BOUND/K2_BOUND) and
          c2_d5_forecast._atom_independent;
      L4  tct_rule.atom_constants_generic (Lemma G);
      L6  c2_d5_forecast.combine (componentwise min with provenance);
      L8  OV tpt.penalty_blocked / penalty_closed / penalty_c5t (via the primary's output record and direct calls for
          the planted mutants);
  * p5y_k5_cell307_rlr_r1/code/rlr307_independent.py (stdlib-only pure functions, loaded by path; NOT an
    exactly-once protocol step) for L3 (declaration D14 with the C3 A0 slot), L7 (Lemma Lad) and L1/L4;
  * the COMMITTED composed fields (U, L) of the A0 LADDER files (written by a0_ladder.compose; validation drifts 3
    and 7/2 only; the A0 code is not executed here) for L7.
Every drift set passes c308_quarantine.guard_drift; every label passes guard_cell. No tail input is opened.

V2  equality (exact) of every layer with its reference, and the primary's TPT-B P*_B inside the F2 bracket:
    P_lo <= P_primary <= P_hi + tol, tol an F2-side bound of the primary's 60-bit non-binding-side split excess.
V3  planted mutants of PRIMARY-SHAPED outputs travel through the SAME comparison functions as V2 and must be
    reported DISAGREE (two-sided: too-large and too-small). Mutants whose output equals the original exactly are
    counted as EQUIVALENT (no defect manifests), never as detections.
Writes results/V2V3_RESULTS.json. Exit code 0 iff every V2 comparison agrees and every non-equivalent V3 mutant is
detected in both directions where both directions occur.
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
CP = NS.parent
sys.path.insert(0, str(HERE))


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


Q = _load("c308E_quarantine", NS / "code" / "c308_quarantine.py")
Q.install_import_guard()
import mb_independent as MB  # noqa: E402

DG = _load("c308F2_decoy_gen", NS / "streams" / "ASSEMBLY" / "decoy_gen.py")
TB = DG.TB                                   # the primary (c308E_tptb_tail), already loaded by decoy_gen
C2, T, DC, TPT = TB.C2, TB.T, TB.DC, TB.TPT  # frozen modules via the primary's pinned loader
RLRI = _load("c308F2_rlr307_independent", CP / "p5y_k5_cell307_rlr_r1" / "code" / "rlr307_independent.py")

EPS = F(1, 2 ** 40)
FIELDS = ("A0", "A1", "A2")
RESULTS: dict = {"schema": "F2_V2V3_RESULTS/1", "module_revision": MB.MODULE_REVISION}


def q(x):
    return x if isinstance(x, F) else F(x)


def l2(x: F):
    """floor(log2 |x|) as an int (None for 0) -- a size descriptor, not a value."""
    if x == 0:
        return None
    x = abs(x)
    return x.numerator.bit_length() - x.denominator.bit_length()


# ================================================================== comparison functions (used by V2 AND V3)

def cmp_triple(mine: tuple, prim: dict, keys=FIELDS) -> dict:
    """Exact equality of a triple with a primary-shaped dict."""
    diff = [k for k, v in zip(keys, mine) if q(prim[k]) != v]
    return {"agree": not diff, "diff": diff}


def cmp_supply(mine: dict, prim_A: dict, prim_prov: dict) -> dict:
    diff = [k for k in FIELDS if q(prim_A[k]) != mine[k]]
    prov_bad = [k for k in FIELDS if prim_prov.get(k) not in mine["attaining_mapped"][k]]
    return {"agree": not diff and not prov_bad, "diff": diff, "prov_mismatch": prov_bad}


def cmp_record(mine: dict, prim: dict, keys) -> dict:
    diff = [k for k in keys if (k in mine) != (k in prim) or (k in mine and q(prim[k]) != mine[k])]
    return {"agree": not diff, "diff": diff}


def cmp_envelope(mine: list, prim: list) -> dict:
    diff = [j for j, (a, b) in enumerate(zip(mine, prim)) if (a is None) != (b is None) or (a is not None and q(b) != a)]
    return {"agree": not diff and len(mine) == len(prim), "diff": diff}


def cmp_penalty(bracket: dict, P_prim: F, tol: F) -> dict:
    """The primary's P*_B (an upper bound, 60-bit split) must lie in [P_lo, P_hi + tol]."""
    ok = bracket["P_lo"] <= P_prim <= bracket["P_hi"] + tol
    excess = P_prim - bracket["P_hi"]
    return {"agree": ok, "below_P_lo": P_prim < bracket["P_lo"], "above_P_hi_plus_tol": P_prim > bracket["P_hi"] + tol,
            "excess_over_P_hi_log2": l2(excess) if excess > 0 else None, "excess_sign": (excess > 0) - (excess < 0),
            "tol_log2": l2(tol)}


# ================================================================== L8 on decoys

def my_inputs(bundle: dict, out: dict):
    v = out["values"]
    e0, rho = q(v["e0"]), q(v["rho"])
    srcs = []
    for t in out["extracted_tuple"]:
        srcs.append({"f_F": q(t["fF"]), "f_D": q(t["fD"]), "f_H": q(t["fH"]), "f_G": q(t["fG"]),
                     "Env4": q(t["Env4"]), "Hhat": [q(t["H_at_a"][0]), q(t["H_at_a"][1])], "G_abs": q(t["abs_G"])})
    prof = {"e0": e0, "rho": rho, "x_lo": e0 - rho, "x_hi": e0 + rho, "m": len(srcs), "sources": srcs,
            "W": [q(out["W_sum"][0]), q(out["W_sum"][1])], "H_final": [q(v["H_final"][0]), q(v["H_final"][1])],
            "M_consumed": q(out["frozen"]["M"])}
    S = tuple(q(out["supply"][k]) for k in FIELDS)
    if bundle.get("blocks"):
        blocks = [{"lo": q(b["e_lo"]), "hi": q(b["e_hi"]), "A0": q(b["A0"]), "A1": q(b["A1"]), "A2": q(b["A2"])}
                  for b in sorted(bundle["blocks"], key=lambda b: q(b["e_lo"]))]
    else:
        blocks = [{"lo": e0 - rho, "hi": e0 + rho, "A0": S[0], "A1": S[1], "A2": S[2]}]
    return prof, blocks, S


def f2_tol(prof: dict, blocks: list, br: dict) -> F:
    """F2-side bound of the primary's split excess: per piece a sliver of width rho/2^60 (the primary's _crossing
    isolates on [0, rho] to 60 bits, on the non-binding side), weight <= x_hi, |integrand gap| <= |cap| + max|g|."""
    P = MB._parse_profile(prof, True)
    Hlo, Hhi = P["H"]
    amp = F(0)
    for b in blocks:
        lo_p, hi_p = MB.profile_polys(P, (q(b["A0"]), q(b["A1"]), q(b["A2"])))
        for s in (F(0), P["rho"]):
            amp = max(amp, abs(Hlo) + abs(MB._peval(lo_p, s)), abs(Hhi) + abs(MB._peval(hi_p, s)))
    n = sum(len(v) for v in br["pieces"].values())
    return n * P["rho"] / 2 ** 60 * P["x_hi"] * amp


def f2_tol_tight(prof: dict, blocks: list, br: dict) -> F:
    """Tight F2-side bound of the primary's split excess. The primary (tpt._crossing) isolates the crossing s* of each
    block polynomial with its cap over [0, rho] by 60 bisection steps and returns the LEFT end a, s* - rho/2^60 <= a
    <= s*; on [max(a, s_a), min(s*, s_b)] it integrates the cap instead of the (smaller) profile. With my own root
    bracket [alpha, beta] of s* (2^-200 wide) and g nondecreasing, the excess of one piece is at most
    delta * x_hi * max(0, c - g(max(s_a, alpha - delta))), delta = rho/2^60, and only pieces meeting
    [alpha - delta, beta] contribute."""
    P = MB._parse_profile(prof, True)
    Hlo, Hhi = P["H"]
    rho, e0, xh = P["rho"], P["e0"], P["x_hi"]
    delta = rho / 2 ** 60
    blk = MB._parse_blocks(blocks, P["x_lo"], P["x_hi"])
    tot = F(0)
    for side, pieces in br["pieces"].items():
        for pc in pieces:
            lo_p, hi_p = MB.profile_polys(P, blk[pc["block"]][2])
            if side == "R":
                w, g, c = [e0, F(1)], [-x for x in lo_p], -Hlo
            else:
                w, g, c = [e0, F(-1)], list(hi_p), Hhi
            _, _, info = MB._piece_bracket(w, g, c, F(0), rho, 200)
            if info["root"] is None:
                continue                      # cap on all of [0, rho] (primary returns 0) or no crossing: exact
            alpha, beta = info["root"]
            if beta < pc["s_a"] or alpha - delta > pc["s_b"]:
                continue
            gap = c - MB._peval(g, max(pc["s_a"], alpha - delta))
            if gap > 0:
                tot += delta * xh * gap
    return tot


def primary_cp(bundle: dict, out: dict):
    v = out["values"]
    S = tuple(q(out["supply"][k]) for k in FIELDS)
    terms = [TPT.SourceTerm(H_at_a=(q(t["H_at_a"][0]), q(t["H_at_a"][1])), abs_G_at_a=q(t["abs_G"]), fF=q(t["fF"]),
                            fD=q(t["fD"]), fH=q(t["fH"]), fG=q(t["fG"]), Env4=q(t["Env4"]))
             for t in out["extracted_tuple"]]
    lab = bundle["label"]
    return TPT.CellProfile(detector=str(lab["detector"]), m=int(lab["m"]), cell=int(lab["cell"]), e0=q(v["e0"]),
                           rho=q(v["rho"]), g_hi=q(v["g_hi"]), A0=S[0], A1=S[1], A2=S[2], terms=terms,
                           W=(q(out["W_sum"][0]), q(out["W_sum"][1])),
                           H_K1=(q(v["H_final"][0]), q(v["H_final"][1])), M_consumed=q(out["frozen"]["M"]))


def tpt_blocks(blocks):
    return [TPT.Block(e_lo=b["lo"], e_hi=b["hi"], A0=q(b["A0"]), A1=q(b["A1"]), A2=q(b["A2"])) for b in blocks]


def l8_decoys(decoys: list) -> dict:
    rows, mut = [], {}

    def add_mut(cls, P_orig, P_mut, br, tol, source):
        r = mut.setdefault(cls, {"n": 0, "equivalent": 0, "too_large": 0, "too_small": 0, "detected_large": 0,
                                 "detected_small": 0, "undetected": [], "source": source})
        r["n"] += 1
        if P_mut == P_orig:
            r["equivalent"] += 1
            return
        c = cmp_penalty(br, P_mut, tol)
        side = "large" if P_mut > P_orig else "small"
        r["too_" + side] += 1
        if not c["agree"]:
            r["detected_" + side] += 1
        else:
            r["undetected"].append({"dir": side, "delta_log2": l2(P_mut - P_orig)})

    for d in decoys:
        lab = d["label"]
        Q.guard_cell(lab["detector"], lab["m"], lab["cell"])
        out = TB.evaluate_bundle(d)
        meta = d["decoy_meta"]
        row = {"cell_label": lab["cell"], "regime": meta["regime"], "cap_mode": meta["cap_mode"],
               "nblocks": meta["nblocks"], "primary_status": out["status"]}
        if out["status"] != "OK":
            row["primary_stop"] = out.get("stop_code")
            rows.append(row)
            continue
        prof, blocks, S = my_inputs(d, out)
        Q.guard_drift(prof["x_lo"], prof["x_hi"])
        v = out["values"]
        t0 = time.process_time()
        try:
            br = MB.tptb(prof, blocks)
        except MB.Refusal as exc:
            row.update(f2_status="REFUSED", f2_reason=str(exc)[:100], agree=False)
            rows.append(row)
            continue
        brc = MB.tptb(prof, [{"lo": prof["x_lo"], "hi": prof["x_hi"], "A0": S[0], "A1": S[1], "A2": S[2]}])
        row["f2_cpu_s"] = round(time.process_time() - t0, 3)
        tol = f2_tol_tight(prof, blocks, br)
        cellb = [{"lo": prof["x_lo"], "hi": prof["x_hi"], "A0": S[0], "A1": S[1], "A2": S[2]}]
        tolc = f2_tol_tight(prof, cellb, brc)
        row["tol_loose_log2"] = l2(f2_tol(prof, blocks, br))
        P_B, P_tpt = q(v["P_B"]), q(v["P_tpt"])
        cB = cmp_penalty(br, P_B, tol)
        cT = cmp_penalty(brc, P_tpt, tolc)
        c5_mine = MB.p5_c5t_closed_form(prof)
        g = MB.gamma_mb(q(v["g_hi"]), br)
        prim_closed = q(v["Gamma_B"]) < 0
        dec_ok = (g["decision"] == "UNDECIDED") or ((g["decision"] == "CLOSED") == prim_closed)
        # the primary's own penalty_blocked on the reconstructed CellProfile must reproduce its record exactly
        cp = primary_cp(d, out)
        rb = TPT.penalty_blocked(cp, tpt_blocks(blocks))
        row.update(f2_status="OK", width_log2=l2(br["width"]), split_pieces=sum(
            1 for s in br["pieces"].values() for p in s if p["regime"].startswith("split")),
            n_pieces=sum(len(s) for s in br["pieces"].values()), P_B_in_bracket=cB, P_tpt_in_bracket=cT,
            c5t_equal=(c5_mine == q(v["P_c5t"])), gamma_decision_f2=g["decision"], primary_closed=prim_closed,
            decision_consistent=dec_ok, primary_cp_reproduces_P_B=(rb["P_star_B"] == P_B),
            primary_exact_equal=(br["P_lo"] == br["P_hi"] == P_B),
            argmax_interior=(br["argmax"] is not None and br["argmax"]["s_end"] != prof["rho"]))
        row["agree"] = cB["agree"] and cT["agree"] and row["c5t_equal"] and dec_ok and row["primary_cp_reproduces_P_B"]
        rows.append(row)

        # ---------------- V3 mutants of the primary-shaped P*_B (same comparison function cmp_penalty)
        if P_B != 0:
            for sg in (1, -1):
                add_mut("P_B x (1 +/- 2^-40)", P_B, P_B * (1 + sg * EPS), br, tol, "primary record value")
        else:
            for sg in (1, -1):
                add_mut("P_B +/- 2^-40 (P_B = 0)", P_B, P_B + sg * EPS, br, tol, "primary record value")
        for i in range(len(blocks)):
            for k in FIELDS:
                for sg in (1, -1):
                    bl2 = [dict(b) for b in blocks]
                    bl2[i][k] = q(bl2[i][k]) * (1 + sg * EPS)
                    Pm = TPT.penalty_blocked(cp, tpt_blocks(bl2))["P_star_B"]
                    add_mut("block supply component x (1 +/- 2^-40)", P_B, Pm, br, tol,
                            "primary tpt.penalty_blocked on mutated block triples")
        for i in range(len(blocks) - 1):
            bl2 = [dict(b) for b in blocks]
            for k in FIELDS:
                bl2[i][k], bl2[i + 1][k] = blocks[i + 1][k], blocks[i][k]
            Pm = TPT.penalty_blocked(cp, tpt_blocks(bl2))["P_star_B"]
            add_mut("swapped block triple", P_B, Pm, br, tol, "primary tpt.penalty_blocked on swapped triples")
            mid = (blocks[i]["lo"] + blocks[i + 1]["hi"]) / 2
            keep = blocks[i] if mid <= blocks[i]["hi"] else blocks[i + 1]
            merged = blocks[:i] + [dict(keep, lo=blocks[i]["lo"], hi=blocks[i + 1]["hi"])] + blocks[i + 2:]
            Pm = TPT.penalty_blocked(cp, tpt_blocks(merged))["P_star_B"]
            add_mut("missing piece end (block boundary dropped)", P_B, Pm, br, tol,
                    "primary tpt.penalty_blocked with one block end removed (the merged piece keeps the triple of "
                    "the block containing its midpoint)")
        add_mut("endpoint-only rule max(0, I_R(rho), I_L(rho))", P_B,
                max(F(0), rb["I_right_full"], rb["I_left_full"]), br, tol, "primary tpt.penalty_blocked fields")
        flip = MB.tptb(prof, blocks, _mutant="flip_t", K=64, target_width_bits=0)["P_hi"]
        add_mut("sign flip of t", P_B, flip, br, tol, "F2 planted-defect hook value placed in the primary record")
        # centre / cap mutants: H_final end moved by 2^-40 relative (the consumed enclosure is an input of the record)
        for idx in (0, 1):
            for sg in (1, -1):
                cp2 = primary_cp(d, out)
                H = list(cp2.H_K1)
                H[idx] = H[idx] * (1 + sg * EPS) if H[idx] != 0 else H[idx] + sg * EPS
                if H[0] > H[1]:
                    continue
                cp2.H_K1 = tuple(H)
                cp2.M_consumed = None
                try:
                    Pm = TPT.penalty_blocked(cp2, tpt_blocks(blocks))["P_star_B"]
                except ValueError:
                    continue
                add_mut("consumed H_final end x (1 +/- 2^-40)", P_B, Pm, br, tol,
                        "primary tpt.penalty_blocked with a perturbed cap")
    return {"rows": rows, "mutants": mut}


def l8_synthetic(n: int = 150, seed: int = 424242) -> dict:
    """L8 on synthetic exact profiles (the V1 generator: several source terms, 1-6 blocks with DECREASING constants in
    part of the cases, tight caps with crossings, drifts outside the band) evaluated by the primary's frozen
    tpt.penalty_blocked directly (label DECOY, cell 9100+i). Adds the non-monotone running integrals the decoys do not
    exercise (endpoint-only rule). The primary here is tpt.penalty_blocked ALONE: it checks the band only at s = 0
    with the cell constants, so cases the F2 module refuses under C6 are counted, not compared (the per-piece C6
    check is the consumer's obligation, done in tptb_tail G-R4)."""
    import v1_synthetic as V1
    rng = random.Random(seed)
    stats = {"n": 0, "agree": 0, "exact_equal": 0, "f2_refused_C6": 0, "argmax_interior": 0, "split_cases": 0}
    mut: dict = {}
    fails = []

    def add_mut(cls, P_orig, P_mut, br, tol):
        r = mut.setdefault(cls, {"n": 0, "equivalent": 0, "too_large": 0, "too_small": 0, "detected_large": 0,
                                 "detected_small": 0, "undetected": []})
        r["n"] += 1
        if P_mut == P_orig:
            r["equivalent"] += 1
            return
        c = cmp_penalty(br, P_mut, tol)
        side = "large" if P_mut > P_orig else "small"
        r["too_" + side] += 1
        if not c["agree"]:
            r["detected_" + side] += 1
        else:
            r["undetected"].append({"dir": side, "delta_log2": l2(P_mut - P_orig)})

    cases = []
    pc = V1.prof(4, 1, [V1.src(f_F=1, Hhat=[1, 1])], (-100, 100))           # V1 hand case (c)
    cases.append((pc, [{"lo": 3, "hi": 4, "A0": 0, "A1": 0, "A2": 0}, {"lo": 4, "hi": F(9, 2), "A0": 0, "A1": 0, "A2": 5},
                       {"lo": F(9, 2), "hi": 5, "A0": 0, "A1": 0, "A2": 0}]))
    for _ in range(n):
        cases.append(V1.random_case(rng))
    for _ in range(40):                     # rise-then-fall right side: the endpoint-only rule must fail here
        e0, rho = rng.choice([(F(3), F(1, 4)), (F(7, 2), F(1, 3)), (F(4), F(1, 2)), (F(1, 2), F(1, 4)),
                              (F(3, 4), F(1, 5))])
        m = rng.randint(1, 3)
        h = V1.rnd_q(rng, 1, 4, 16)
        srcs = [V1.src(f_F=V1.rnd_q(rng, F(1, 2), 2, 16), f_D=V1.rnd_q(rng, 0, F(1, 4), 64),
                       f_H=V1.rnd_q(rng, 0, F(1, 4), 64), Hhat=[h, h + V1.rnd_q(rng, 0, F(1, 8), 64)]) for _ in range(m)]
        big = V1.rnd_q(rng, 5, 20, 8) * h
        f = F(rng.randint(2, 6), 8)
        ends = [e0 - rho, e0 - rho / 2, e0, e0 + f * rho, e0 + rho]
        trip = [(0, 0, big * F(1, 1000)), (0, 0, big * F(1, 1000)), (0, big / 100, big), (0, 0, big * F(1, 1000))]
        blocks = [{"lo": a, "hi": b, "A0": t[0], "A1": t[1], "A2": t[2]} for (a, b), t in zip(zip(ends, ends[1:]), trip)]
        H = [-10 ** 6, 10 ** 6] if rng.random() < 0.5 else [-(big * 3), 10 ** 6]
        cases.append((V1.prof(e0, rho, srcs, H), blocks))
    stats["C6_decision"] = {"n": 0, "agree": 0, "both_refuse": 0}
    for i, (P, blocks) in enumerate(cases):
        Q.guard_drift(P["x_lo"], P["x_hi"])
        Pp = MB._parse_profile(P, True)
        # C6 refusal decision vs the primary consumer's per-piece G-R4 rule (tptb_tail._pieces + band_at at s_a)
        ext = {"terms": [{"fF": r["f_F"], "fD": r["f_D"], "fH": r["f_H"], "fG": r["f_G"], "Env4": r["Env4"],
                          "abs_G": r["G_abs"], "H_at_a": tuple(r["Hhat"])} for r in Pp["sources"]],
               "W": Pp["W"], "e0": Pp["e0"], "rho": Pp["rho"], "x_lo": Pp["x_lo"], "x_hi": Pp["x_hi"]}
        tb_blocks = [(F(b["lo"]), F(b["hi"]), (F(b["A0"]), F(b["A1"]), F(b["A2"]))) for b in blocks]
        prim_refuse = False
        for side in ("R", "L"):
            for sa, sb, A in TB._pieces(ext, tb_blocks, side):
                L0, U0 = TB.band_at(ext, A, sa, Pp["H"])
                prim_refuse = prim_refuse or L0 > U0
        try:
            br = MB.tptb(P, blocks)
            f2_refuse = False
        except MB.Refusal as exc:
            if "C6" not in str(exc):
                raise
            f2_refuse = True
        stats["C6_decision"]["n"] += 1
        stats["C6_decision"]["agree"] += (f2_refuse == prim_refuse)
        stats["C6_decision"]["both_refuse"] += (f2_refuse and prim_refuse)
        if f2_refuse:
            stats["f2_refused_C6"] += 1
            continue
        Amax = tuple(max(F(b[k]) for b in blocks) for k in FIELDS)
        terms = [TPT.SourceTerm(H_at_a=tuple(r["Hhat"]), abs_G_at_a=r["G_abs"], fF=r["f_F"], fD=r["f_D"],
                                fH=r["f_H"], fG=r["f_G"], Env4=r["Env4"]) for r in Pp["sources"]]
        cp = TPT.CellProfile(detector="DECOY", m=Pp["m"], cell=9100 + i, e0=Pp["e0"], rho=Pp["rho"], g_hi=F(0),
                             A0=Amax[0], A1=Amax[1], A2=Amax[2], terms=terms, W=Pp["W"], H_K1=Pp["H"])
        bl = [{"lo": F(b["lo"]), "hi": F(b["hi"]), "A0": F(b["A0"]), "A1": F(b["A1"]), "A2": F(b["A2"])} for b in blocks]
        rb = TPT.penalty_blocked(cp, tpt_blocks(bl))
        P_B = rb["P_star_B"]
        tol = f2_tol_tight(P, bl, br)
        c = cmp_penalty(br, P_B, tol)
        stats["n"] += 1
        stats["agree"] += c["agree"]
        stats["exact_equal"] += (br["P_lo"] == br["P_hi"] == P_B)
        stats["argmax_interior"] += (br["argmax"] is not None and br["argmax"]["s_end"] != Pp["rho"])
        stats["split_cases"] += any(p["regime"].startswith("split") for s_ in br["pieces"].values() for p in s_)
        if not c["agree"]:
            fails.append({"case": i, "cmp": c})
        # mutants (same comparison function)
        if P_B != 0:
            for sg in (1, -1):
                add_mut("P_B x (1 +/- 2^-40)", P_B, P_B * (1 + sg * EPS), br, tol)
        add_mut("endpoint-only rule max(0, I_R(rho), I_L(rho))", P_B,
                max(F(0), rb["I_right_full"], rb["I_left_full"]), br, tol)
        for j in range(len(bl)):
            k = FIELDS[rng.randrange(3)]
            for sg in (1, -1):
                bl2 = [dict(b) for b in bl]
                bl2[j][k] = bl2[j][k] * (1 + sg * EPS)
                add_mut("block supply component x (1 +/- 2^-40)", P_B,
                        TPT.penalty_blocked(cp, tpt_blocks(bl2))["P_star_B"], br, tol)
        for j in range(len(bl) - 1):
            bl2 = [dict(b) for b in bl]
            for k in FIELDS:
                bl2[j][k], bl2[j + 1][k] = bl[j + 1][k], bl[j][k]
            add_mut("swapped block triple", P_B, TPT.penalty_blocked(cp, tpt_blocks(bl2))["P_star_B"], br, tol)
            mid = (bl[j]["lo"] + bl[j + 1]["hi"]) / 2
            keep = bl[j] if mid <= bl[j]["hi"] else bl[j + 1]
            merged = bl[:j] + [dict(keep, lo=bl[j]["lo"], hi=bl[j + 1]["hi"])] + bl[j + 2:]
            add_mut("missing piece end (block boundary dropped)", P_B,
                    TPT.penalty_blocked(cp, tpt_blocks(merged))["P_star_B"], br, tol)
        flip = MB.tptb(P, blocks, _mutant="flip_t", K=64, target_width_bits=0)["P_hi"]
        add_mut("sign flip of t", P_B, flip, br, tol)
    return {"v2": stats, "fails": fails[:10], "mutants": mut}


# ================================================================== L1 / L2 / L4 / L6 / L3 / L7 / L5 synthetic + decoy

def rq(rng, lo, hi, den=997):
    return F(lo) + (F(hi) - F(lo)) * F(rng.randint(0, den), den)


def l1_l2_l4(rng, decoys) -> dict:
    res = {"L1_v2": {"n": 0, "agree": 0}, "L1_vs_c2_independent": {"n": 0, "agree": 0},
           "L1_vs_rlr_independent": {"n": 0, "agree": 0}, "L2_substitution": {"n": 0, "agree": 0},
           "L4_v2": {"n": 0, "agree": 0}, "L4_vs_rlr_independent": {"n": 0, "agree": 0}}
    mut = {"L1 component x (1 +/- 2^-40)": [0, 0, 0], "L2 component x (1 +/- 2^-40)": [0, 0, 0],
           "L4 component x (1 +/- 2^-40)": [0, 0, 0]}   # [n, detected_large, detected_small]
    k1, k2 = DC.K1_BOUND, DC.K2_BOUND
    cases = []
    for d in decoys:                                  # the decoys' own Dv' / Lemma-G sources
        for name, src in (d.get("supply_sources") or {}).items():
            if src["kind"] == "lemma_Dv_prime":
                cases.append(tuple(q(src[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")))
    for _ in range(400):                              # synthetic grid, both Abar-binding and tau/D_lo-binding
        tau = rq(rng, 1, 40)
        Dlo = rq(rng, F(1, 50), 2)
        Abar = rq(rng, 1, 2 * tau / Dlo)
        cases.append((Abar, tau, tau + rq(rng, 0, 60), Dlo, rq(rng, 0, 5), rq(rng, 0, 20)))
    for args in cases:
        mine = MB.dv_prime(*args, k1, k2)
        ref = DC.atom_constants_r2(*args)            # frozen reference with its default kappas
        c = cmp_triple(mine, ref)
        res["L1_v2"]["n"] += 1
        res["L1_v2"]["agree"] += c["agree"]
        c2 = cmp_triple(mine, C2._atom_independent(*args))
        res["L1_vs_c2_independent"]["n"] += 1
        res["L1_vs_c2_independent"]["agree"] += c2["agree"]
        c3 = cmp_triple(mine, RLRI.dv_prime_r2(*args, k1, k2))
        res["L1_vs_rlr_independent"]["n"] += 1
        res["L1_vs_rlr_independent"]["agree"] += c3["agree"]
        for k in FIELDS:                               # V3: mutate the primary-shaped output, same cmp_triple
            for sg in (1, -1):
                bad = dict(ref)
                bad[k] = ref[k] * (1 + sg * EPS)
                m = mut["L1 component x (1 +/- 2^-40)"]
                m[0] += 1
                if not cmp_triple(mine, bad)["agree"]:
                    m[1 if sg > 0 else 2] += 1
        # L2: Dv'-M == frozen Dv' r2 evaluated at the substituted Abar' = min(Abar, Ubar)
        U = rq(rng, F(1), args[0] * 2)
        mine2 = MB.dv_prime_M({"A_bar": args[0], "tau": args[1], "C_T": args[2], "D_lo": args[3], "D1": args[4],
                               "D2": args[5]}, U, k1, k2)
        ref2 = DC.atom_constants_r2(min(args[0], U), *args[1:])
        c = cmp_triple(mine2, ref2)
        res["L2_substitution"]["n"] += 1
        res["L2_substitution"]["agree"] += c["agree"]
        for k in FIELDS:
            for sg in (1, -1):
                bad = dict(ref2)
                bad[k] = ref2[k] * (1 + sg * EPS)
                m = mut["L2 component x (1 +/- 2^-40)"]
                m[0] += 1
                if not cmp_triple(mine2, bad)["agree"]:
                    m[1 if sg > 0 else 2] += 1
    gcases = []
    for d in decoys:
        kn = [q(v) for v in d["meas"]["norms"]["k"]]
        for name, src in (d.get("supply_sources") or {}).items():
            if src["kind"] == "lemma_G":
                gcases.append((q(src["C_upper"]), kn[1], kn[2]))
    for _ in range(200):
        gcases.append((rq(rng, 1, 30), rq(rng, F(1, 100), 3), rq(rng, F(1, 100), 3)))
    for C, a, b in gcases:
        mine = MB.lemma_g(C, a, b)
        ref = T.atom_constants_generic(C, a, b)
        c = cmp_triple(mine, ref)
        res["L4_v2"]["n"] += 1
        res["L4_v2"]["agree"] += c["agree"]
        c3 = cmp_triple(mine, RLRI.lemma_g(C, a, b))
        res["L4_vs_rlr_independent"]["n"] += 1
        res["L4_vs_rlr_independent"]["agree"] += c3["agree"]
        for k in FIELDS:
            for sg in (1, -1):
                bad = dict(ref)
                bad[k] = ref[k] * (1 + sg * EPS)
                m = mut["L4 component x (1 +/- 2^-40)"]
                m[0] += 1
                if not cmp_triple(mine, bad)["agree"]:
                    m[1 if sg > 0 else 2] += 1
    return {"v2": res, "v3": {k: {"n": v[0], "detected_large": v[1], "detected_small": v[2]} for k, v in mut.items()}}


def l6(rng, decoys) -> dict:
    """L6 vs the frozen c2_d5_forecast.combine (componentwise min, provenance)."""
    res = {"n": 0, "agree": 0, "prov_checked": 0}
    mut = {"n": 0, "detected_large": 0, "detected_small": 0}
    sets = []
    for d in decoys:
        if d.get("supply_sources"):
            kn = [q(v) for v in d["meas"]["norms"]["k"]]
            sup = {}
            for name, src in d["supply_sources"].items():
                if src["kind"] == "lemma_G":
                    sup[name] = T.atom_constants_generic(q(src["C_upper"]), kn[1], kn[2])
                else:
                    sup[name] = DC.atom_constants_r2(*(q(src[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")))
            sets.append(sup)
    for _ in range(300):
        n = rng.randint(1, 4)
        sup = {}
        for i in range(n):
            base = (rq(rng, 1, 10, 7), rq(rng, 1, 50, 7), rq(rng, 1, 400, 7))
            sup[f"M{i}"] = {k: v for k, v in zip(FIELDS, base)}
        sets.append(sup)
    for sup in sets:
        names = list(sup)
        # F2 names: the first member plays S_I1 (MB section 6 item 1); the rest keep their names
        mapping = {names[0]: "S_I1"} | {n: n for n in names[1:]}
        members = {mapping[n]: tuple(sup[n][k] for k in FIELDS) for n in names}
        mine = MB.block_supply(members)
        inv = {v: k for k, v in mapping.items()}
        mine["attaining_mapped"] = {k: [inv[x] for x in mine["attaining"][k]] for k in FIELDS}
        A, prov = C2.combine(sup)
        c = cmp_supply(mine, A, prov)
        res["n"] += 1
        res["agree"] += c["agree"]
        res["prov_checked"] += 1
        for k in FIELDS:
            for sg in (1, -1):
                bad = dict(A)
                bad[k] = A[k] * (1 + sg * EPS)
                mut["n"] += 1
                if not cmp_supply(mine, bad, prov)["agree"]:
                    mut["detected_large" if sg > 0 else "detected_small"] += 1
    return {"v2": res, "v3": {"L6 component x (1 +/- 2^-40)": mut}}


def l3(rng) -> dict:
    """L3 vs rlr307_independent.block_supply (declaration D14 with A0 slot min(Abar_eff, C_R)):
       (a) plain D14: d14_M(Ubar=INF, no refresh) == RLRI.block_supply(inp);
       (b) D14-M: d14_M(Ubar, no refresh) == RLRI.block_supply(inp with A_bar := min(A_bar, Ubar));
       (c) D14-M + DM: d14_M(Ubar, refresh) == RLRI.block_supply(inp with A_bar := Abar', D_lo := D_lo').
       V3: component mutants; and the Lemma-DM mutant D_lo'' = D_lo' (1 + 2^-40) > tau_a_lo/Abar' when that binds
       (and D_lo'' = D_lo' (1 - 2^-40), too small), evaluated by the SAME reference and compared."""
    k1, k2 = F(7978845609, 10 ** 10), 4 * F(24197072451914337, 10 ** 17)
    res = {"plain_D14": [0, 0], "D14M": [0, 0], "D14M_DM": [0, 0], "DM_binding_cases": 0}
    mut = {"L3 component x (1 +/- 2^-40)": [0, 0, 0], "L3 D_lo' x (1 +/- 2^-40) (DM mutant)": [0, 0, 0, 0]}
    for i in range(400):
        tau = rq(rng, 1, 30)
        Dlo = rq(rng, F(1, 100), 1)
        tal = rq(rng, 1, tau)
        inp = {"A_bar": rq(rng, 1, 3 * tau / Dlo), "tau": tau, "C_T": tau + rq(rng, 0, 40), "C_R": rq(rng, 1, 600),
               "tau_a_lo": tal, "D_lo": Dlo, "D1": rq(rng, 0, 3), "D2": rq(rng, 0, 10), "L1_up": rq(rng, 0, 200),
               "L2_up": rq(rng, 0, 900)}
        U = rq(rng, 1, 2 * inp["A_bar"])

        def ref(x):
            r = RLRI.block_supply(x, k1, k2)
            return {"A0": r["A0_SUPPLY"], "A1": r["A1_SUPPLY"], "A2": r["A2_SUPPLY"]}
        mine = MB.d14_M(inp, None, k1, k2, False)
        c = cmp_triple(mine, ref(inp))
        res["plain_D14"][0] += 1
        res["plain_D14"][1] += c["agree"]
        Ap = min(inp["A_bar"], U)
        mine = MB.d14_M(inp, U, k1, k2, False)
        r_b = ref(dict(inp, A_bar=Ap))
        c = cmp_triple(mine, r_b)
        res["D14M"][0] += 1
        res["D14M"][1] += c["agree"]
        det = MB.d14_M_detail(inp, U, k1, k2, True)
        Dp = max(Dlo, tal / Ap)
        res["DM_binding_cases"] += Dp > Dlo
        r_c = ref(dict(inp, A_bar=Ap, D_lo=Dp))
        c = cmp_triple((det["A0"], det["A1"], det["A2"]), r_c)
        res["D14M_DM"][0] += 1
        res["D14M_DM"][1] += c["agree"] and det["D_lo_used"] == Dp
        for k in FIELDS:
            for sg in (1, -1):
                bad = dict(r_c)
                bad[k] = r_c[k] * (1 + sg * EPS)
                m = mut["L3 component x (1 +/- 2^-40)"]
                m[0] += 1
                if not cmp_triple((det["A0"], det["A1"], det["A2"]), bad)["agree"]:
                    m[1 if sg > 0 else 2] += 1
        for sg in (1, -1):
            bad = ref(dict(inp, A_bar=Ap, D_lo=Dp * (1 + sg * EPS)))
            m = mut["L3 D_lo' x (1 +/- 2^-40) (DM mutant)"]
            if bad == r_c:
                m[3] += 1                               # equivalent: D_lo does not reach the output here
                continue
            m[0] += 1
            if not cmp_triple((det["A0"], det["A1"], det["A2"]), bad)["agree"]:
                m[1 if sg > 0 else 2] += 1
    out_mut = {}
    for k, v in mut.items():
        out_mut[k] = {"n": v[0], "detected_large": v[1], "detected_small": v[2]} | (
            {"equivalent": v[3]} if len(v) > 3 else {})
    return {"v2": {k: ({"n": v[0], "agree": v[1]} if isinstance(v, list) else v) for k, v in res.items()},
            "v3": out_mut}


RL_MAP = {"S2hat_up": "S2_up", "T_N_up": "TN_up"}


def l7(rng) -> dict:
    """L7 vs rlr307_independent.ladder (certified rungs only; its key names S2_up/TN_up mapped) and vs
    the committed a0_ladder.compose output fields of the A0 LADDER files (U = min certified upper, L = max certified
    lower)."""
    ups = ("C_R", "tau", "C_T", "A_bar", "tau_a_up", "S2hat_up", "T_N_up", "D1", "D2", "L1_up", "L2_up")
    lows = ("tau_a_lo", "D_lo", "Lambda_lo")
    res = {"vs_rlr_independent": [0, 0], "vs_a0_compose": [0, 0]}
    mut = {"L7 composed key x (1 +/- 2^-40)": [0, 0, 0], "L7 upper key by max (wrong direction)": [0, 0, 0, 0]}
    for _ in range(200):
        n = rng.randint(1, 3)
        rungs = []
        for d in range(n):
            r = {"degree": 4 + 2 * d, "status": rng.choice(["CERTIFIED", "CERTIFIED", "FAILED"])}
            for k in ups + lows:
                r[k] = rq(rng, 1, 100, 13)
            rungs.append(r)
        cert = [r for r in rungs if r["status"] == "CERTIFIED"]
        mine = MB.ladder(rungs)
        ref = RLRI.ladder([{RL_MAP.get(k, k): v for k, v in r.items()} for r in cert])
        if ref is None or mine is None:
            res["vs_rlr_independent"][0] += 1
            res["vs_rlr_independent"][1] += (ref is None and mine is None)
            continue
        ref = {k: ref[RL_MAP.get(k, k)] for k in ups + lows}
        mine_v = {k: mine[k] for k in ups + lows}
        c = cmp_record(mine_v, ref, ups + lows)
        res["vs_rlr_independent"][0] += 1
        res["vs_rlr_independent"][1] += c["agree"]
        k = rng.choice(ups + lows)
        for sg in (1, -1):
            bad = dict(ref)
            bad[k] = ref[k] * (1 + sg * EPS)
            m = mut["L7 composed key x (1 +/- 2^-40)"]
            m[0] += 1
            if not cmp_record(mine_v, bad, ups + lows)["agree"]:
                m[1 if sg > 0 else 2] += 1
        ku = rng.choice(ups)
        bad = dict(ref)
        bad[ku] = max(q(r[ku]) for r in cert)
        m = mut["L7 upper key by max (wrong direction)"]
        if bad[ku] == ref[ku]:
            m[3] += 1
        else:
            m[0] += 1
            if not cmp_record(mine_v, bad, ups + lows)["agree"]:
                m[1] += 1
    for p in sorted((NS / "streams" / "A0" / "results").glob("LADDER_e*.json")):
        rec = json.loads(p.read_text())
        drift = F(rec["drift"]) if "drift" in rec else None
        if drift is not None:
            Q.guard_drift(drift)
        my_rungs = []
        for r in rec["rungs"]:
            my_rungs.append({"status": r.get("status_U"), "A_bar": r.get("U")})
            my_rungs.append({"status": r.get("status_L"), "Lambda_lo": r.get("L")})
        mine = MB.ladder([{k: v for k, v in r.items() if v is not None} for r in my_rungs])
        ref = {"U": rec.get("U"), "L": rec.get("L")}      # committed output of a0_ladder.compose
        ok = mine is not None and ref["U"] is not None and q(ref["U"]) == mine["A_bar"] and \
            (ref["L"] is None) == ("Lambda_lo" not in mine) and (ref["L"] is None or q(ref["L"]) == mine["Lambda_lo"])
        res["vs_a0_compose"][0] += 1
        res["vs_a0_compose"][1] += ok
    return {"v2": {k: {"n": v[0], "agree": v[1]} for k, v in res.items()},
            "v3": {k: {"n": v[0], "detected_large": v[1], "detected_small": v[2]} | (
                {"equivalent": v[3]} if len(v) > 3 else {}) for k, v in mut.items()}}


def l5(rng) -> dict:
    """L5: no primary implementation exists (MB section 2 is implemented only here). A reference envelope is built
    in this harness by the literal definition Ubar_j = min_{i <= j} U_i (list comprehension, different code); V3
    mutants: the 'right-hand U' envelope min_{i <= j+1} U_i, a max-envelope, and a component x (1 +/- 2^-40)."""
    res = {"n": 0, "agree": 0}
    mut = {"right-hand U envelope": [0, 0, 0, 0], "L5 component x (1 +/- 2^-40)": [0, 0, 0, 0]}
    for _ in range(300):
        n = rng.randint(1, 8)
        drifts = sorted(rng.sample([F(k, 8) for k in range(0, 9)] + [F(k, 4) for k in range(11, 25)], n))
        Us = [None if rng.random() < 0.2 else rq(rng, 1, 50, 31) for _ in range(n)]
        mine = MB.envelope(Us, drifts)
        ref = []
        for j in range(n):
            vals = [u for u in Us[:j + 1] if u is not None]
            ref.append(min(vals) if vals else None)
        c = cmp_envelope(mine, ref)
        res["n"] += 1
        res["agree"] += c["agree"]
        rh = []
        for j in range(n):
            vals = [u for u in Us[:j + 2] if u is not None]
            rh.append(min(vals) if vals else None)
        m = mut["right-hand U envelope"]
        if rh == ref:
            m[3] += 1
        else:
            m[0] += 1
            if not cmp_envelope(mine, rh)["agree"]:
                m[2] += 1                                # the right-hand envelope is never larger: too small
        idx = [j for j, u in enumerate(ref) if u is not None]
        if idx:
            j = rng.choice(idx)
            for sg in (1, -1):
                bad = list(ref)
                bad[j] = ref[j] * (1 + sg * EPS)
                m = mut["L5 component x (1 +/- 2^-40)"]
                m[0] += 1
                if not cmp_envelope(mine, bad)["agree"]:
                    m[1 if sg > 0 else 2] += 1
    return {"v2": {"vs_literal_definition": res},
            "v3": {k: {"n": v[0], "detected_large": v[1], "detected_small": v[2], "equivalent": v[3]}
                   for k, v in mut.items()}}


# ================================================================== main

def main() -> int:
    t0 = time.time()
    rng = random.Random(20260929)
    decoys = DG.decoy_set()
    RESULTS["decoys"] = {"n": len(decoys), "labels": sorted(d["label"]["cell"] for d in decoys),
                         "detector": sorted({d["label"]["detector"] for d in decoys})}
    RESULTS["L8"] = l8_decoys(decoys)
    RESULTS["L8_synthetic"] = l8_synthetic()
    RESULTS["L1_L2_L4"] = l1_l2_l4(rng, decoys)
    RESULTS["L6"] = l6(rng, decoys)
    RESULTS["L3"] = l3(rng)
    RESULTS["L7"] = l7(rng)
    RESULTS["L5"] = l5(rng)

    # ---------------- verdicts
    rows = RESULTS["L8"]["rows"]
    ok_rows = [r for r in rows if r["primary_status"] == "OK"]
    v2_l8 = all(r.get("agree") for r in ok_rows) and len(ok_rows) == len(rows)
    v2_other = True
    for key in ("L1_L2_L4", "L6", "L3", "L7", "L5"):
        for name, v in RESULTS[key]["v2"].items():
            if isinstance(v, dict) and "n" in v and v["n"] != v["agree"]:
                v2_other = False
    v3_ok = True
    v3_summary = []
    for key in ("L1_L2_L4", "L6", "L3", "L7", "L5"):
        for name, m in RESULTS[key]["v3"].items():
            det = m["detected_large"] + m["detected_small"]
            full = det == m["n"]
            v3_ok = v3_ok and full and m["n"] > 0
            v3_summary.append({"class": name, "n": m["n"], "detected": det, "equivalent": m.get("equivalent", 0),
                               "all_detected": full})
    for name, m in RESULTS["L8"]["mutants"].items():
        det = m["detected_large"] + m["detected_small"]
        ne = m["n"] - m["equivalent"]
        full = det == ne
        v3_ok = v3_ok and full
        v3_summary.append({"class": "L8 " + name, "n": m["n"], "non_equivalent": ne, "detected": det,
                           "too_large": m["too_large"], "too_small": m["too_small"],
                           "detected_large": m["detected_large"], "detected_small": m["detected_small"],
                           "equivalent": m["equivalent"], "all_detected": full, "source": m["source"]})
    syn = RESULTS["L8_synthetic"]
    v2_l8 = v2_l8 and syn["v2"]["n"] == syn["v2"]["agree"] and syn["v2"]["n"] > 0 and \
        syn["v2"]["C6_decision"]["n"] == syn["v2"]["C6_decision"]["agree"]
    for name, m in syn["mutants"].items():
        det = m["detected_large"] + m["detected_small"]
        ne = m["n"] - m["equivalent"]
        full = det == ne
        v3_ok = v3_ok and full
        v3_summary.append({"class": "L8-synthetic " + name, "n": m["n"], "non_equivalent": ne, "detected": det,
                           "too_large": m["too_large"], "too_small": m["too_small"],
                           "detected_large": m["detected_large"], "detected_small": m["detected_small"],
                           "equivalent": m["equivalent"], "all_detected": full})
    allm = list(RESULTS["L8"]["mutants"].values()) + list(syn["mutants"].values())
    two_sided = {"L8_large": sum(m["detected_large"] for m in allm), "L8_small": sum(m["detected_small"] for m in allm)}
    RESULTS["verdict"] = {"V2_L8_all_agree": v2_l8, "V2_other_layers_all_agree": v2_other,
                          "V3_all_non_equivalent_mutants_detected": v3_ok, "V3_two_sided_L8": two_sided,
                          "V3_summary": v3_summary, "wall_s": round(time.time() - t0, 1)}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "V2V3_RESULTS.json").write_text(json.dumps(RESULTS, indent=1, default=str) + "\n")
    print(json.dumps(RESULTS["verdict"], indent=1, default=str))
    ok = v2_l8 and v2_other and v3_ok and two_sided["L8_large"] > 0 and two_sided["L8_small"] > 0
    Q.log_event("streams/INDEP/compare_primary.py",
                "stream F2 V2/V3: F2 independent composition layers vs the primary (ASSEMBLY tptb_tail on 18 in-memory "
                "decoys; frozen atom_constants_r2 / atom_constants_generic / combine via the primary's pinned loader; "
                "rlr307_independent pure functions and a0_ladder.compose on synthetic inputs / validation-drift ladder "
                f"files); verdict ok={ok}", klass="SYNTHETIC_VALIDATION", agent="streamF2",
                notes="decoy labels DECOY 9000+i only; drift sets outside the band (guarded); no tail input opened")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
