# P6 handoff — what a safe re-baselining controller should regulate

P5 does **not** design P6. This is the evidence P5 hands over, and the control
targets that evidence supports.

## 1. The recommendation P5 explicitly does NOT make

> **Do not target `rho < rho_c`.**

P7 established that `rho_c` has no operational signature under its frozen
criterion. P5's conditional T10 is consistent with that result: the measured
period-two branch has vanishing amplitude against an `O(1)` noise floor.

**`rho_c` is on the wrong side of the optimum.** In all eight frozen cells the
stationary reference RMS is still *decreasing* at `rho_c`, and the in-control
ARL is still *increasing*. Operating at `rho_c` is worse than operating at
`1.5x`–`4.9x rho_c` on both metrics simultaneously on the measured grid.
Restricting reuse to the
locally-attracting region buys nothing and costs dispersion.

## 2. The single most useful new fact for P6

There is a **well-defined interior optimum in `rho`**, and reference dispersion
and in-control ARL are optimised at essentially the same place:

| det | m | `rho_c` | `rho*` (min RMS) | `rho*/rho_c` | RMS at `rho*` | RMS at `rho_c` | RMS at `rho=1` | ARL at `rho*` | ARL at `rho=1` |
|---|---|---|---|---|---|---|---|---|---|
| CUSUM | 1 | 0.067 | **0.30** | 4.5 | 0.841 | 0.939 | 1.371 | 95.3 | 49.9 |
| CUSUM | 2 | 0.082 | **0.20** | 2.5 | 0.619 | 0.658 | 1.066 | 124.8 | 61.6 |
| CUSUM | 3 | 0.091 | **0.20** | 2.2 | 0.515 | 0.535 | 0.925 | 145.0 | 69.4 |
| CUSUM | 5 | 0.108 | **0.16** | 1.5 | 0.405 | 0.412 | 0.761 | 175.6 | 80.1 |
| SR | 1 | 0.061 | **0.30** | 4.9 | 0.840 | 0.944 | 1.367 | 90.8 | 48.4 |
| SR | 2 | 0.074 | **0.20** | 2.7 | 0.618 | 0.662 | 1.058 | 119.4 | 59.4 |
| SR | 3 | 0.084 | **0.20** | 2.4 | 0.513 | 0.537 | 0.910 | 138.7 | 66.6 |
| SR | 5 | 0.099 | **0.20** | 2.0 | 0.405 | 0.413 | 0.743 | 167.8 | 78.6 |

Against full reuse, operating at `rho*` cuts stationary reference RMS by
**39%–47%** and roughly **doubles** the in-control ARL, in every cell, on both
detectors. That is a larger, better-founded operating-point gain than anything
the local theory suggests.

## 3. Control targets P5's evidence supports

Ranked by how well P5 supports them.

1. **Stationary reference RMS, `sqrt(E_pi[e^2])` — supported, and now a legal
   target.** T7 proves `pi` exists, is unique and has a finite second moment for
   every admissible `(D, m, rho)`, so "regulate `E_pi[e^2]`" is a well-posed
   objective rather than a hopeful one. The measured curves have a clear
   interior minimum and closely match across the two calibrated detectors.
   Exact optimum locations have near-ties in three cells.
2. **In-control ARL / false-alarm rate — supported, and nearly co-optimal with
   (1).** Its optimum coincides with (1) to within one grid point in 7/8 cells.
   A controller regulating either will approximately optimise the other. This
   co-optimality is a P5 finding and should be re-verified by P6 before being
   relied on.
3. **Tail mass `P_pi(|e| > c)` — supported, and finite by theorem.** T7 gives
   moments of every order, so tail targets are well-posed. Measured `P(|e|>2)`
   traces the same U as RMS (`0.045 -> 0.016 -> 0.139` for CUSUM `m=1`).
   Because the reference law is *platykurtic*, tail mass adds little information
   beyond RMS in this model; it may matter more under P8 conditions.
4. **The reuse window `m` — strongly supported as a control variable.**
   Over `m in {1,2,3,5}`, increasing `m` improves the listed dispersion and ARL
   metrics: it lowers the measured maximum of `|R|`,
   lowers `S(0)` (from `4.04` to `1.59`), lowers the stationary RMS at every
   `rho`, raises the ARL, raises `rho_c`, and shifts `rho*` *down*. P5 measured
   only `m <= 5`; the trend does not saturate over that range.
5. **State-dependent `rho` — plausible but untested.** T2 shows the conditional
   variance `rho^2 S(e) + (1-rho)^2/m` is state-dependent through `S(e)`, and
   `S` varies by a factor of `8` over `e in [0, 4]` (`4.04` at `0`, `0.48` near
   `e=0.5`). A controller that reduced `rho` when `|e|` is small and raised it
   when `|e|` is moderate would be exploiting real structure. **P5 provides no
   evidence that this helps**; it is a hypothesis for P6.

## 4. Control targets P5's evidence does NOT support

* **`rho < rho_c` or `rho/rho_c` as the control variable** — see §1.
* **`ACF1` or the alternation rate as a safety target.** They are strong,
  clean signals (`ACF1 -> -0.54`, alternation `-> 0.93`) but they are monotone
  in `rho` through the optimum: they do not distinguish good from bad operating
  points. They are excellent *diagnostics* of how much reuse is in effect.
* **Suppressing the period-2 structure.** The orbit is not the harm. Dispersion
  is minimised at `rho* ~ 0.2-0.3`, which is `2x-5x` *above* the bifurcation
  point, so the optimal controller operates on the bifurcated branch by design.
* **Anything that assumes a heavy-tailed reference law.** It is platykurtic
  (`LIMITATIONS.md` §5).

## 5. Two structural facts a controller can rely on

* **One-step forgetting (T1, measured).** Whatever damage a controller does, the
  chain nearly resets in one cycle in the stress experiment: from `e_0 = 10^6`
  the mean `|e_1|` is `0.83`. T5/T7 rule out divergence in distribution for the
  frozen constant policy. They do not eliminate the need for controller guards
  under adaptive policies or changed models.
* **Cross-detector similarity (measured).** The nonlinear summaries are close
  for calibrated CUSUM and SR while the linearisation at `0` differs by about
  9%. Transfer is a hypothesis for P6 to re-check, not an authoritative rule.

## 6. What P6 should measure that P5 did not

1. Whether the `rho*` optimum survives a genuine process shift (`Delta > 0`);
   P5 worked entirely at `Delta = 0`.
2. Whether the RMS/ARL co-optimality of §3.2 is a coincidence of this
   calibration or structural.
3. Whether state-dependent `rho` or fresh-sample injection beats the best fixed
   `rho`, using the exact conditional variance decomposition of T2 as the design
   equation.
4. `m > 5`, where P5's trend suggests continuing gains and P3's boundary table
   does not reach.
