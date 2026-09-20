# Campaign C2, R stage — costed design for cells 307, 308, 309. **DESIGN ONLY; nothing is executed.**

Produced under the frozen gate's `D_PARTIAL` rule, which requires the R-stage design in the same campaign as the
D-stage adoption. **No new real scientific address is evaluated by this document or by anything in C2.** The guard is
DENY and there is no authorization artifact, because none may exist until the R-stage sub-gate, an independent
review, qualification and a distinct authorization are all complete, with N1 closed first.

> **BLOCKING PRECONDITION, added after the pre-freeze review (note 11).** A sound, cheaper, deterministic step
> that this campaign did not pre-register already clears the gate's own 20 % bar on **all three** still-open cells,
> including the cell 309 that cost C2 the `D_USEFUL` class. It uses constants that are already certified, committed
> and reviewed, and costs **zero** new CPU and zero new real addresses. See
> [`../phase_d/D_PRIME_OPPORTUNITY.md`](../phase_d/D_PRIME_OPPORTUNITY.md).
>
> The premise under which a real order-3 address would be spent — that the deterministic direction is exhausted —
> is therefore **not established by this campaign**. What ran out is C2's pre-registration, not the deterministic
> direction. **No address designed below may be authorized until a successor has frozen a D′ gate and run that step
> first.** Everything else in this document — the attribution test, the minimal address set, the cost model, the
> no-transport argument — is unaffected and remains usable as written.

## 1. Eligibility, as the gate pre-registered it

- **(a)** the D stage did not close all five cells — 307, 308, 309 remain open. ✔
- **(b)** the residual is order-3-attributable on each of them: with f_G at its `eps_src[3]` floor and every other
  input unchanged, magnitudes fall to 1.1311 / 1.1744 / 1.1995 and Γ to −0.1718 / −0.1267 / −0.0873. ✔

## 2. The decisive number, and it is not the attribution test

The attribution test uses a *perfect* order-3 candidate. A real one pays its own certified supremum through Env4 and
its value at the atom through the centre motion ρ·|Ĝ(a)| — which is precisely what invalidated Campaign B's route
T2. Modelled on the adopted Campaign-A evidence — |Ĝ(a)| = 0.681·s_G, and δ_G at each Taylor index r's own worst
adopted value across the 34 lower-front cells (a per-r maximum, not one maximum over all r) — the **critical
ratio** is the largest s_G/s_H at which a real candidate still closes the cell:

| cell | Lemma G (Campaign B) | **C1 (true)** | **C2** | C2 over C1 | adopted lower-front s_G/s_H |
|---|---|---|---|---|---|
| 307 | 32.03283 | **34.55795** | **37.32219** | **+8.0 %** | 34.79 – 80.50 |
| 308 | 19.19506 | **20.93621** | **23.26035** | **+11.1 %** | 34.79 – 80.50 |
| 309 | 10.54598 | **12.18694** | **14.15799** | **+16.2 %** | 34.79 – 80.50 |

**Corrected after the pre-freeze review (notes 61 and 62), and this correction is the most important one in the
campaign.** The first version of this table had two columns, headed "under C1 constants" and "under C2 constants",
and concluded that *"C2's deterministic work raised every threshold by 16–34 %"*. The left column was not C1. It
was Campaign B's **Lemma-G** column — digit for digit `TAIL_FORECAST_R2.critical_sup_G_over_sup_H_ratio`, a file
whose own `premise_supply` field states that every route in it uses the Lemma-G constants. C1 never computed a
critical ratio at all. So the improvement quoted was C2 over **Campaign B, two campaigns back**, presented under
C1's name, and it overstated C2's own contribution by about a factor of two. The true improvement over the
immediate predecessor is **+8.0 / +11.1 / +16.2 %**.

This is the same defect class C1's own pre-freeze reviewer caught in C1 — a comparison computed on a different
quantity than its label states — and it appeared here in the one document that would justify spending the
programme's first real order-3 tail address. It is recorded rather than quietly patched for that reason.

The repair also closed a provenance gap the review did not raise: these ratios were published from an uncommitted
scratch script. They now have a committed producer, `code/c2_critical_ratio.py` → `evidence/phase_d5/
C2_CRITICAL_RATIOS.json`, which computes the ratio under every supply **by name** so the labels cannot drift again,
runs from committed evidence alone on any machine with stdlib Python (no record store, no compute host, no new real
address), and **refuses to emit anything** unless it first reproduces two independently published anchors
bit-exactly: Campaign B's Lemma-G column, and C2's own published Γ, Γ-with-a-perfect-candidate and critical ratio.
Those two anchors are what license the C1 column, which nothing else in the programme has ever computed.

**And the surviving claim is weaker than it first read.** Cell 307's C2 ratio of 37.32 does sit inside the adopted
range, whose lower end is 34.786. But the componentwise minimum of the two supplies *already certified when C1
stopped* — Lemma G and C1's registry — gives **34.82089**, which is already inside that range, marginally. What C2
bought at 307 is therefore not entry into the adopted range; it is margin within it (37.32 against 34.82, +7.2 %).
The word "now" in the original text carried more weight than the arithmetic supports. The recommendation below
survives the correction; its justification is simply narrower than it was stated to be.

The tail's own s_G/s_H has never been measured, and this campaign does not pretend otherwise: it is the single
quantity the R stage would buy.

## 3. Minimal address set

The gate requires the minimum set the residual analysis supports, chosen before any real output is seen.

- **R-a (recommended): cell 307 only — 1 new real address, ≈ 0.44 CPU-h.** It has the highest critical ratio, it is
  the only still-open cell inside the adopted range, and a single evaluation settles the tail's s_G/s_H for all
  three, because the ratio varies slowly across neighbouring cells (the adopted front varies by ≤ 2.3× across 34
  cells). If s_G/s_H at 307 comes in at or below 23.26 it also tells the programme that 308 would have closed, at
  the cost of one address rather than three.
- **R-b: cells 307, 308, 309 — 3 addresses, ≈ 1.3 CPU-h.** Closes whatever the measured ratio permits in one
  campaign. It is not minimal and it spends two addresses on cells whose thresholds the same measurement predicts.
- **Not recommended: all five.** Cells 305 and 306 are closed deterministically by C2 and need nothing.

An anchor at one cell does **not** certify a neighbour: theorem TC-T's candidate is fixed at that cell's own
midpoint and the enclosure's centre motion is ρ|Ĝ(a)| on that cell. What transfers between neighbouring cells is the
*estimate* of s_G/s_H, not a certificate. Any design claiming multi-cell certification from one anchor would need a
transport theorem that does not exist, and C2 does not propose one.

## 4. What the R stage must carry before it may run

| requirement | state |
|---|---|
| R-stage sub-gate, frozen before any R forecast | **not written** — the next campaign owns it |
| N1 authorization bridge, successor-owned, historical registry unedited | **OPEN** — see `OPEN_NOTES_DISPOSITION_C2.md` |
| N3 tail-domain manufactured fixtures and exact cross-checks for the order-3 injection | **required**, not yet built |
| N5 identity gates on the four new order-3 fields (name, role, source hash, sign/range, insertion point, mutation detection) | **required**, not yet built |
| independent pre-freeze review, qualification, distinct authorization, seal before interpretation | **required** |
| caps | preferred 3 CPU-h, hard 6 CPU-h new-real (frozen in the C2 gate) |

Forecast cost is far inside the caps under either option, so the caps are not the binding constraint — the N1, N3
and N5 obligations are.

## 5. Honest assessment

**First, the precondition at the head of this document.** R-a is not authorized by anything here, and on the
evidence now available it should not be the programme's next step: a deterministic D′ step that costs nothing
clears the same bar on every open cell and must be tried first. The assessment below is what remains true *if* D′
is run and still closes no further cell.

R-a is worth doing and R-b is not yet. The measurement R-a buys is the one quantity that has blocked three
campaigns, it costs one address, and its outcome determines whether 308 and 309 are reachable at all or whether the
tail needs a higher-order theorem instead. Launching three addresses before that measurement exists would spend two
of them on a prediction this campaign cannot make.
