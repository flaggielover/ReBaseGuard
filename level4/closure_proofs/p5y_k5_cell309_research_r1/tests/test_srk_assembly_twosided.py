"""Two-sided exact test of the SRK assembly (impl/srk_assemble.py) against an INDEPENDENT recomputation written from
THEOREM_SRK section 3 in polynomial-in-s form, plus a textual mutant battery of the primary's srk_coefficients /
rad_srk.  A mutant is caught if its output differs (exactly) from the independent value on at least one input of the
declared battery.  The battery deliberately includes inputs where the raw SRK coefficient EXCEEDS the TC-T term
(so dropping the min is observable), inputs with Gamma = None, and boundary ties raw == old.
Also: malformed-input refusals (missing field, float, negative, rho <= 0)."""
import random
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "impl"))
import srk_assemble as SA  # noqa: E402

SRC = (HERE.parent / "impl" / "srk_assemble.py").read_text()


def independent(fields: dict, gamma: dict) -> F:
    """rad(s) at s = rho, built as polynomial coefficient lists [c0, c1, c2, ...] in s."""
    f = {k: F(v) for k, v in fields.items()}
    g = {i: (None if gamma.get(i) is None else F(gamma[i])) for i in (1, 2, 3, 4)}
    A0, A1, A2, r = f["A0"], f["A1"], f["A2"], f["rho"]
    # order-0 channel coefficients in s: [A0 fH, B3, B4/2]
    c3_old = A0 * f["fG"]
    c4_old = A0 * f["Env4"]
    cand3 = [c3_old]
    if all(g[i] is not None for i in (1, 2, 3)):
        lin = sum((w * gv for w, gv in ((3 * f["sH"], g[1]), (3 * f["sD"], g[2]), (f["sF"], g[3]))), F(0))
        cand3.append(lin + A0 * f["sigma3"] + A0 * f["eps3"])
    cand4 = [c4_old]
    if all(g[i] is not None for i in (2, 3, 4)):
        w2, w3 = 6 * f["sH"], 4 * f["sD"] + 4 * r * f["sH"]
        w4 = f["sF"] + r * f["sD"] + r * r * f["sH"] / 2
        cand4.append(w2 * g[2] + w3 * g[3] + w4 * g[4] + A0 * f["sigma4"])
    ch0 = [A0 * f["fH"], min(cand3), min(cand4) / 2]
    p1 = [f["fD"], f["fH"], f["fG"] / 2, f["Env4"] / 6]
    p0 = [f["fF"], f["fD"], f["fH"] / 2, f["fG"] / 6, f["Env4"] / 24]
    ev = lambda c: sum((ck * r ** k for k, ck in enumerate(c)), F(0))  # noqa: E731
    return ev(ch0) + 2 * A1 * ev(p1) + A2 * ev(p0)


def battery(seed: int = 424242, n: int = 80) -> list:
    rng = random.Random(seed)
    out = []
    for t in range(n):
        R = lambda a=1, b=10 ** 4: F(rng.randint(a, b), rng.randint(1, 10 ** 3))  # noqa: E731
        f = {k: R() for k in SA.REQUIRED}
        f["rho"] = F(rng.randint(1, 60), 1000)
        f["eps3"] = F(0) if t % 5 == 0 else R()
        A0 = f["A0"]
        mode = t % 4
        if mode == 0:        # SRK wins both
            g = {i: A0 * F(rng.randint(1, 90), 100) for i in (1, 2, 3, 4)}
            f["fG"] = 3 * f["sH"] + 3 * f["sD"] + f["sF"] + f["sigma3"] + f["eps3"] + R()
            f["Env4"] = f["sigma4"] + 6 * f["sH"] + 4 * (f["sD"] + f["rho"] * f["sH"]) + f["sF"] + R()
        elif mode == 1:      # SRK loses both (raw > old): min must select the old term
            g = {i: A0 * F(rng.randint(200, 900), 100) for i in (1, 2, 3, 4)}
        elif mode == 2:      # some Gamma missing
            g = {i: (None if i == rng.randint(1, 4) else A0 * F(rng.randint(1, 150), 100)) for i in (1, 2, 3, 4)}
        else:                # tie: raw3 == old3 exactly
            g = {i: A0 * F(rng.randint(1, 150), 100) for i in (1, 2, 3, 4)}
            raw3 = A0 * (f["sigma3"] + f["eps3"]) + 3 * f["sH"] * g[1] + 3 * f["sD"] * g[2] + f["sF"] * g[3]
            f["fG"] = raw3 / A0
        out.append((f, g))
    return out


MUTANTS = {
    "drop_min3": ("B3 = old3 if new3 is None or new3 >= old3 else new3", "B3 = old3 if new3 is None else new3"),
    "drop_min4": ("B4 = old4 if new4 is None or new4 >= old4 else new4", "B4 = old4 if new4 is None else new4"),
    "coef_3sH_to_1": ('3 * f["sH"] * g[1]', '1 * f["sH"] * g[1]'),
    "coef_6sH_to_4": ('6 * f["sH"] * g[2]', '4 * f["sH"] * g[2]'),
    "drop_eps3": ('(f["sigma3"] + f["eps3"])', 'f["sigma3"]'),
    "rho_not_rho2": ("rho ** 2 / 2 * B4", "rho / 2 * B4"),
    "drop_A0fH": ('rad = f["A0"] * f["fH"] + rho * B3', 'rad = rho * B3'),
    "wrong_gamma_index": ('3 * f["sD"] * g[2]', '3 * f["sD"] * g[1]'),
    "rho_sH_dropped_in_B4": ('4 * (f["sD"] + rho * f["sH"]) * g[3]', '4 * f["sD"] * g[3]'),
    "missing_as_zero": ("if None in (g[1], g[2], g[3]):", "if False:"),
}


DOM_CHECK = ("    if not rad <= base:   # review R1 B4: a refusal, not an assert (asserts vanish under -O)\n"
             "        raise AssemblyRefusal(\"rad_srk: dominance violated (rad_srk > rad_tct)\")\n")


def load_mutant(name: str, keep_dominance_check: bool = False):
    old, new = MUTANTS[name]
    assert SRC.count(old) >= 1, (name, old)
    mod = types.ModuleType("srk_assemble_mut_" + name)
    code = SRC.replace(old, new, 1)
    if name == "missing_as_zero":
        code = code.replace("            g[i] = None\n", "            g[i] = F(0)\n", 1)
    assert code.count(DOM_CHECK) == 1
    if not keep_dominance_check:
        code = code.replace(DOM_CHECK, "")      # mutants may violate dominance; compare values only
    exec(compile(code, name, "exec"), mod.__dict__)
    return mod


def refusals() -> dict:
    base = {k: F(1) for k in SA.REQUIRED}
    out = {}
    for label, mod in (("missing", lambda d: d.pop("sF")), ("float", lambda d: d.__setitem__("sF", 0.5)),
                       ("negative", lambda d: d.__setitem__("fH", F(-1))), ("rho0", lambda d: d.__setitem__("rho", 0)),
                       ("neg_gamma", None)):
        d = dict(base)
        g = {1: 1, 2: 1, 3: 1, 4: 1}
        if mod is None:
            g[2] = F(-1)
        else:
            mod(d)
        try:
            SA.rad_srk(d, g)
            out[label] = False
        except SA.AssemblyRefusal:
            out[label] = True
    return out


def run():
    bat = battery()
    genuine = all(SA.rad_srk(f, g)["rad_srk"] == independent(f, g) for f, g in bat)
    dominance = all(SA.rad_srk(f, g)["rad_srk"] <= SA.rad_tct(f) for f, g in bat)
    caught = {}
    for name in MUTANTS:
        m = load_mutant(name)
        caught[name] = any(m.rad_srk(f, g)["rad_srk"] != independent(f, g) for f, g in bat)
    ref = refusals()
    # the dominance refusal is live (not stripped by -O): the unstripped min-dropped mutants must refuse somewhere
    for name in ("drop_min3", "drop_min4"):
        if name in MUTANTS:
            m = load_mutant(name, keep_dominance_check=True)
            hit = False
            for f, g in bat:
                try:
                    m.rad_srk(f, g)
                except m.AssemblyRefusal:          # the mutant module defines its own class
                    hit = True
                    break
            ref[f"dominance_refusal_live_{name}"] = hit
    ok = genuine and dominance and all(caught.values()) and all(ref.values())
    return ok, {"genuine_equal": genuine, "dominance": dominance, "mutants_caught": caught, "refusals": ref,
                "battery": len(bat)}


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
