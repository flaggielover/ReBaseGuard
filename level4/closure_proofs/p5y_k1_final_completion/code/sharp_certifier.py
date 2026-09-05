"""Re-certification with drift-aware operator norms.

The ONLY change against the validated Repair1/Repair2 path is the certified
operator-norm table: `self.norms` is replaced by the drift-aware one from
`sharp_norms`. Everything downstream -- the residual envelopes in
`cusum_layer2.all_residuals`, the propagation in `propagate`, the whole-cell
refinement in `refine`, and the Repair1 S0 correction -- reads `norms["k"]` and
`norms["j"]` and therefore inherits the sharper bounds automatically. Nothing
else is touched:

  * the frozen cover geometry, cell endpoints and Taylor radius: unchanged
  * the frozen precision (256 bits) and Taylor degree: unchanged
  * budgets, caps and thresholds: unchanged
  * STYLE_1, the complete D_interval, the single Taylor charge: unchanged
  * the Repair1 single-S0-charge accounting: unchanged
  * the Repair2 producer / source-certificate provenance: unchanged

A sharper certified bound on the same operator is not a relaxation. Each entry
is `min(drift-aware, reviewed whole-line, Cauchy-Schwarz)`, so the norm table
can only tighten, and a guard asserts exactly that.
"""
from __future__ import annotations

from fractions import Fraction as F

import base                                                     # noqa: F401

import opnorms as reviewed_norms                                # noqa: E402
from intervals import exact                                     # noqa: E402
from repair_layer2 import RepairedCellCertifier                 # noqa: E402

import sharp_norms                                              # noqa: E402


class NormRegression(RuntimeError):
    """A drift-aware norm came out LOOSER than the reviewed whole-line bound."""


class SharpCellCertifier(RepairedCellCertifier):
    """Repair1's certifier with drift-aware certified operator norms."""

    uses_drift_aware_norms = True

    def prepare(self):
        super().prepare()
        reviewed = self.norms
        sharp = sharp_norms.table(self.left, self.right)
        # A sharper bound may only tighten. Assert it, per order, both families.
        e_max = exact(self.e_max)
        for i in sharp["k"]:
            if sharp["k"][i].upper() > reviewed_norms.kernel_norm(i).upper():
                raise NormRegression(f"k_{i} loosened")
        for i in sharp["j"]:
            if sharp["j"][i].upper() > reviewed_norms.raw_kernel_norm(i, e_max).upper():
                raise NormRegression(f"j_{i} loosened")
        # Preserve every key the reviewed table exposed, then override k and j.
        merged = dict(reviewed)
        merged.update({"k": sharp["k"], "j": sharp["j"],
                       "window": sharp["window"],
                       "provenance": {**reviewed["provenance"],
                                      **sharp["provenance"],
                                      "drift_aware": True}})
        self.norms = merged
        self.reviewed_norms_snapshot = {
            "k": {i: reviewed["k"][i] for i in reviewed["k"]},
            "j": {i: reviewed["j"][i] for i in reviewed["j"]}}
        return self

    def norm_improvement(self) -> dict:
        return sharp_norms.improvement_report(self.left, self.right)
