"""Independent review of P5X L5: hash binding, strip arithmetic, regularity-use audit.

Standard library only. No scientific compute: the only numbers evaluated are
closed-form Gaussian tail values used to *illustrate* strip widths whose
positivity is proved symbolically in README.md section 2.

  python -B code/l5_review_check.py verify-hashes
  python -B code/l5_review_check.py strip --out evidence/STRIP_ARITHMETIC.json
  python -B code/l5_review_check.py uses
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
INVENTORY = NS / "config" / "L5_HASH_INVENTORY.json"

L5_PATH = "level4/closure_proofs/p5x_global_nonlinear_dynamics/PROOF.md"
L5_FIRST, L5_LAST = 412, 482  # "## L5 — real-analyticity in `e`" .. last line of L5.6


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def l5_section_bytes(repo: Path = REPO) -> bytes:
    lines = (repo / L5_PATH).read_bytes().split(b"\n")
    return b"\n".join(lines[L5_FIRST - 1:L5_LAST]) + b"\n"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def verify_hashes(repo: Path = REPO) -> list[str]:
    inv = json.loads(INVENTORY.read_text())
    errors = []
    for group in ("l5_files", "consumed_definition_files", "consumer_files"):
        for rel, h in inv[group].items():
            p = repo / rel
            if not p.exists():
                errors.append(f"missing {rel}")
                continue
            if sha256(p.read_bytes()) != h["sha256"]:
                errors.append(f"sha256 mismatch {rel}")
            try:
                commits = git(repo, "log", "--format=%H", "--", rel).split()
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue  # not a git checkout: byte check only
            if commits and commits[-1] != h["introduced_in"]:
                errors.append(f"introducing commit mismatch {rel}")
            if commits and commits[0] != h["last_modified_in"]:
                errors.append(f"modified after binding {rel}")
    sec = inv["l5_section"]
    if sha256(l5_section_bytes(repo)) != sec["sha256"]:
        errors.append("L5 section sha256 mismatch")
    first = l5_section_bytes(repo).split(b"\n", 1)[0].decode()
    if first != sec["first_line"]:
        errors.append("L5 section does not start at the L5 heading")
    return errors


# ---------------------------------------------------------------- strip arithmetic

def phi(x: complex) -> complex:
    return cmath.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def upper_tail(c: float) -> float:
    return 0.5 * math.erfc(c / math.sqrt(2))


def modulus_identity_residual(samples=((0.3, 1e-4), (-2.0, 0.5), (5.5, 1.0), (-7.0, 2.0))) -> float:
    """|phi(a + i theta)| = phi(a) exp(theta^2/2); exact algebra, spot-checked in floating point."""
    worst = 0.0
    for a, th in samples:
        lhs = abs(phi(complex(a, th)))
        rhs = phi(a).real * math.exp(th * th / 2)
        worst = max(worst, abs(lhs - rhs) / rhs)
    return worst


def strip_record() -> dict:
    log_a = math.log(520.886133602749)
    detectors = {"CUSUM": {"c_D": 5.5, "p5t4_n0": 10, "p5t4_p0": upper_tail(1.0) ** 10},
                 "SR": {"c_D": log_a + 0.5, "p5t4_n0": 1, "p5t4_p0": upper_tail(log_a + 0.5)}}
    out = {"authority": "NON_AUTHORITATIVE double precision; positivity of every width is symbolic (README section 2)",
           "modulus_identity_max_rel_residual": modulus_identity_residual(),
           "detectors": {}}
    for name, d in detectors.items():
        p1 = 2 * upper_tail(d["c_D"])
        theta_l5 = math.sqrt(d["p5t4_p0"] / d["p5t4_n0"])        # exp(n0 th^2/2)(1-p0) <= exp(-p0/2) < 1
        theta_direct = math.sqrt(p1 / 2)                          # exp(th^2/2)(1-p1)^(1/2) <= exp(-p1/4) < 1
        ratio_l5 = math.exp(d["p5t4_n0"] * theta_l5 ** 2 / 2) * (1 - d["p5t4_p0"])
        ratio_direct = math.exp(theta_direct ** 2 / 2) * math.sqrt(1 - p1)
        out["detectors"][name] = {
            "c_D": d["c_D"],
            "L5_route": {"n0": d["p5t4_n0"], "p0": d["p5t4_p0"], "theta0": theta_l5, "block_ratio": ratio_l5,
                         "block_ratio_lt_1": ratio_l5 < 1},
            "direct_route": {"one_step_alarm_floor_p1": p1, "theta1": theta_direct, "series_ratio": ratio_direct,
                             "series_ratio_lt_1": ratio_direct < 1},
        }
    return out


# ---------------------------------------------------------------- K5-B regularity uses

USES = [
    ("U1", "R''(0) = 0 from oddness", "C2", "R'' exists at the interior point 0 and is odd"),
    ("U2", "MVT for R'' on C_k: R''(t) >= R''(x_{k-1}) + L_k (t - x_{k-1})", "C3",
     "R'' continuous on the closed cell, differentiable inside, R''' >= L_k"),
    ("U3", "cell 1: R''(t) >= L_1 t", "C3", "U1 + U2 on [0, x_1]"),
    ("U4", "g(e) = g(x_{k-1}) - int t R''(t) dt (FTC)", "C2", "g' = -e R'' continuous"),
    ("U5", "g' = R' - R' - e R''", "C2", "product rule on e R'(e)"),
    ("U6", "MVT for g about e0_k: |g(e) - g(e0)| <= rho sup|t R''|", "C2", "g differentiable on the closed cell"),
    ("U7", "K1 inputs H_k superset R''(C_k), M_k >= sup_{C_k}|R''| over the WHOLE closed cell (incl. cell 309 past 2)",
     "C2", "R'' defined on the whole closed cell"),
    ("U8", "L_k <= inf_{C_k} R''' is meaningful", "C3", "R''' defined on the whole closed cell"),
    ("U9", "D_k contains R'(e0_k); s'(e) = g/e^2; s strictly decreasing by MVT", "C1", "R differentiable on (0,2]"),
    ("U10", "s(0+) = -R'(0) = GammaTilde - 1", "C1", "R differentiable at 0 with R(0) = 0"),
    ("U11", "s continuous on (0,2]; s(2) < 1 iff R(2) > -2", "C0", "R continuous"),
]
ORDER = {"C0": 0, "C1": 1, "C2": 2, "C3": 3}


def uses_record() -> dict:
    top = max(ORDER[u[2]] for u in USES)
    return {"uses": [{"id": i, "step": s, "minimum": m, "why": w} for i, s, m, w in USES],
            "max_required_order": f"C{top}", "hidden_C4_in_K5B": top >= 4,
            "L5_supplies": "C-infinity (real-analytic) on all of R, every m >= 1, both detectors"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verify-hashes")
    s = sub.add_parser("strip")
    s.add_argument("--out")
    sub.add_parser("uses")
    a = ap.parse_args(argv)
    if a.cmd == "verify-hashes":
        errs = verify_hashes()
        print("OK" if not errs else "\n".join(errs))
        return 1 if errs else 0
    if a.cmd == "strip":
        rec = strip_record()
        text = json.dumps(rec, indent=1, sort_keys=True) + "\n"
        if a.out:
            (NS / a.out).write_text(text)
        print(text, end="")
        return 0
    print(json.dumps(uses_record(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
