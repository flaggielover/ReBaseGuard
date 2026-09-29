"""Dimensionless decoy-only summary of SRK certificates (latent-proxy class: never juxtaposed with tail numbers)."""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
KAPPA = {0: 1.0, 1: 0.7978845608, 2: 0.9678829, 3: 1.5100130, 4: 2.8006003}  # q309: literal-ok (Gaussian moments E|He_i|, not drifts)


def main(sub="srk_decoys"):
    for fp in sorted((NS / "evidence" / sub).glob("*.json")):
        d = json.loads(fp.read_text())
        A = F(d["Abar_W"]) if d["Abar_W"] else None
        st = [(r["degree"], r["W_status"]) for r in d["rungs"]]
        g = {i: (round(float(F(v)) / (KAPPA[int(i)] * float(A)), 4) if (v and A) else None) for i, v in d["Gamma"].items()}
        print(fp.name, "rungs", st, "| Gamma_i/(kappa_i*Abar_W):", g)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "srk_decoys")
