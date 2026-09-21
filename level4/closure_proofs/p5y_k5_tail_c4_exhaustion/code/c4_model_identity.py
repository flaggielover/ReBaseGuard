"""The frozen CUSUM model, extracted from its frozen producer rather than transcribed.

`cusum_layer1.py` cannot be imported here (it imports numpy, which this host does not carry and which C4 does not
need). The constants and the two model-defining code blocks are therefore read out of the pinned source text, and
the pin is what makes the reading evidence. Any edit to the producer changes the sha and this module refuses.

The model these lines define, and the only thing C4 uses about it:

    state      the reachable closure X = {(p, m) in [0,H]^2 : p = 0 or m = 0 or p + m <= H - 2K},
               which is T-invariant and contains the atom a = (0, 0)   (OPERATOR_AUDIT.md section 1)
    innovation z with density phi(z + e)   i.e.  z ~ N(-e, 1)
    update     s+ <- max(0, s+ + z - K),   s- <- max(0, s- - z - K)
    alarm      iff  z > C - s+  or  z < s- - C,  with C = H + K
               equivalently iff the unclipped s+ + z - K > H or s- - z - K > H
    tau        the first alarm step;  (I - K_e)^-1 1 (x) = E_x[tau]   (theorem AD section 3)
"""
import re
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c4_common import MODEL_SOURCE, sha  # noqa: E402

MODEL_SHA = "efcc0f36632632577a24c4ddf1a7c2c3579d471cdba5a752dd72c708667cdc79"

# The two blocks that define the model. Matched literally; a changed line is a refusal, not a silent drift.
ALARM_LINE = "            ell, upper = m - C_CUSUM, C_CUSUM - p"
UPDATE_LINES = ("                wp = _basis(max(0.0, p + z - K_FROZEN), nodes, bary)",
                "                wm = _basis(max(0.0, m - z - K_FROZEN), nodes, bary)")
DENSITY_LINE = "                dens = rad * weight * math.exp(-0.5 * y * y) / norm"
DRIFT_LINE = "                y = z + drift"
H1_LINE = "            h1[row] = 1.0 - Phi(au) + Phi(al)"
NODE_LINE = "    nodes = 0.5 * H_FROZEN * (1.0 - x)"


def model(strict: bool = True) -> dict:
    src = MODEL_SOURCE.read_text()
    got = sha(MODEL_SOURCE)
    if strict and got != MODEL_SHA:
        raise SystemExit(f"frozen CUSUM producer does not match its pin: {got}")
    def const(name):
        m = re.search(rf"^{name} = ([0-9.]+)$", src, re.M)
        if not m:
            raise SystemExit(f"constant {name} not found in the frozen producer")
        return F(m.group(1))
    K, H = const("K_FROZEN"), const("H_FROZEN")
    missing = [ln for ln in (ALARM_LINE, DENSITY_LINE, DRIFT_LINE, H1_LINE, NODE_LINE, *UPDATE_LINES)
               if ln not in src]
    if missing:
        raise SystemExit(f"the frozen producer no longer contains {len(missing)} model-defining line(s)")
    if not re.search(r"^C_CUSUM = H_FROZEN \+ K_FROZEN", src, re.M):
        raise SystemExit("C_CUSUM is no longer H_FROZEN + K_FROZEN")
    return {"source": MODEL_SOURCE.relative_to(MODEL_SOURCE.parents[3]).as_posix(), "source_sha256": got,
            "K": K, "H": H, "C": H + K,
            "state_space": "reachable closure X = {(p, m) in [0,H]^2 : p = 0 or m = 0 or p + m <= H - 2K}; "
                            "B(X) is the space Lemma SM(d) is stated on. The ambient box [0,H]^2 is NOT the "
                            "operator's state space (pre-result review, item D.1).",
            "atom": "(0, 0), in X",
            "state_space_source": "p5y_k5_perron_deflated_resolvent/theorem/OPERATOR_AUDIT.md section 1",
            "innovation": "z with density phi(z + e), i.e. z ~ N(-e, 1)",
            "update": "s+ <- max(0, s+ + z - K); s- <- max(0, s- - z - K)",
            "alarm": "z > C - s+  or  z < s- - C, i.e. unclipped s+ + z - K > H or s- - z - K > H",
            "tau": "first alarm step; (I - K_e)^-1 1 (x) = E_x[tau]"}


if __name__ == "__main__":
    if "--print-sha" in sys.argv:
        print(sha(MODEL_SOURCE))
    else:
        m = model()
        print({k: (str(v) if isinstance(v, F) else v) for k, v in m.items()})
