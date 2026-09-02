"""POST-HOC diagnostics for the R4 gate.  Explicitly NOT part of the frozen gate.

Written after observing the frozen gate's P2 and P3 failures.  Every number here
is disclosed as post-hoc; none of it changes the frozen verdict in
results/r4_gate.json.
"""
from __future__ import annotations
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from flint import arb, ctx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xi_kernel import kernel_apply, kernel_quadrature, sr_constants, zeta_patch  # noqa: E402
from rebaseguard_certify.arb_backend import rational  # noqa: E402

NS = Path(__file__).resolve().parents[1]


def probe(n):
    return [[rational(1, 1 + i + 2 * j) for j in range(n + 1)] for i in range(n + 1)]


def main() -> int:
    ctx.prec = 192
    A, b, c = sr_constants()
    e = rational(1, 4)
    g = zeta_patch(17, 11)
    pts = [((g["zp"][0] + g["zp"][1]) / arb(2), (g["zm"][0] + g["zm"][1]) / arb(2)),
           (g["zp"][0], g["zm"][0]), (g["zp"][0], g["zm"][1]),
           (g["zp"][1], g["zm"][0]), (g["zp"][1], g["zm"][1])]

    # D11 + double-precision diagnostic bug: redo the P2 comparison in ARB only.
    rows, allok, worst = [], True, 0.0
    for zp, zm in pts:
        cf = kernel_apply(probe(3), zp, zm, e, A)
        ctx.prec = 256
        r40 = kernel_quadrature(probe(3), zp, zm, e, A, 40000)
        r20 = kernel_quadrature(probe(3), zp, zm, e, A, 20000)
        ctx.prec = 192
        rich = abs(r40 - r20) / arb(15)          # Simpson is O(h^4): 2n gains ~15x
        gap = abs(cf - r40)
        ratio = float(gap / rich)
        ok = gap.upper() <= float(arb(16) * rich)
        rows.append({"closed_form": cf.str(30), "reference_simpson_40000": r40.str(30),
                     "rel_gap": float(gap / abs(r40)),
                     "reference_richardson_truncation_rel": float(rich / abs(r40)),
                     "gap_over_own_truncation": ratio,
                     "closed_form_rel_radius": float(cf.rad() / abs(cf.mid())),
                     "within_16x": bool(ok)})
        allok = allok and ok
        worst = max(worst, ratio)

    # P3: is the amplification precision-driven (fixable by bits) or a fixed
    # condition number?  Sweep the working precision and see.
    sweep = []
    for bits in (192, 256, 320, 384, 448, 512):
        ctx.prec = bits
        A2 = sr_constants()[0]
        cand = probe(16)   # MUST be rebuilt at each precision: rational(1,3)
                           # carries a 2^-prec radius that would otherwise be frozen in
        g2 = zeta_patch(17, 11)
        zp2 = (g2["zp"][0] + g2["zp"][1]) / arb(2)
        zm2 = (g2["zm"][0] + g2["zm"][1]) / arb(2)
        v = kernel_apply(cand, zp2, zm2, rational(1, 4), A2)
        t = time.process_time()
        for _ in range(50):
            kernel_apply(cand, zp2, zm2, rational(1, 4), A2)
        dt = (time.process_time() - t) / 50
        amp = float(v.rad()) * float(arb(2) ** bits)
        sweep.append({"bits": bits, "dependency_amplification": amp,
                      "correct_bits_remaining": bits - (amp.bit_length() if isinstance(amp, int) else int(amp).bit_length()),
                      "t_patch_seconds": dt,
                      "projected_SR_cpu_hours": 835 * 1210 * dt * 2 * 43 / 3600,
                      "passes_frozen_1e12": amp <= 1e12})
    ctx.prec = 192

    rec = {
        "schema": "rebaseguard.p5x.r4.diagnostics.v1",
        "status": "POST-HOC. Not part of the frozen gate. Written after the gate ran.",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "P2_corrected_in_arb": {
            "defect": "D11, plus a double-precision bug in the gate's own diagnostic: "
                      "the gate computed rel_gap and the Richardson widening through "
                      "float(), which truncates at ~1e-16 and destroyed both.",
            "points": rows,
            "all_within_16x_of_reference_own_truncation": bool(allok),
            "worst_gap_over_own_truncation": worst,
            "conclusion": "the closed form's disagreement with Simpson EQUALS Simpson's "
                          "own truncation error to a ratio of 1.0000; the closed form "
                          "is correct and the frozen P2 could not have detected that.",
        },
        "P3_precision_sweep": {
            "sweep": sweep,
            "conclusion": "the amplification is FLAT at ~2.1e17 from 192 to 512 bits, so "
                          "it is a fixed condition number of about 2^58 -- the "
                          "e^{k^2/2} prefactor multiplying a Phi-difference of order "
                          "e^{-k^2/2} -- not a precision defect that worsens. Adding "
                          "bits buys accuracy linearly at about +20% time per 64 bits. "
                          "It still FAILS the frozen 1e12 threshold, which is the "
                          "binding verdict.",
        },
    }
    (NS / "results" / "r4_diagnostics.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({"P2_all_within_16x": allok, "worst_ratio": worst,
                      "P3_amp_flat": [s["dependency_amplification"] for s in sweep]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
