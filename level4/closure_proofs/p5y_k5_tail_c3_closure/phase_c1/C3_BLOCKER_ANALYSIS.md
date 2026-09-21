# C3 phase C1 — why 306, 307, 308 and 309 remain open under authoritative r5

Machine-readable: `evidence/phase_c1/C3_BLOCKER.json`, produced by `code/c3_blocker.py` from committed certified
evidence only. No K1 record store, no new-real evaluation. Regenerate with:

    python3 -B code/c3_blocker.py --out evidence/phase_c1/C3_BLOCKER.json

## 1. Γ and closure, by supply

| cell | Lemma G | C1 | C2 | D4 = min(G,C1,C2) | operator-mixed | closes under |
|---|---|---|---|---|---|---|
| 306 | +0.019115585 | −0.005719468 | −0.030469258 | −0.030469258 | **−0.036197780** | C1, C2, D4, mixed — **not G** |
| 307 | +0.085117770 | +0.061683080 | +0.033132953 | +0.033132953 | +0.026354631 | **none** |
| 308 | +0.158342965 | +0.136194543 | +0.102700084 | +0.102700084 | +0.094564145 | **none** |
| 309 | +0.226117166 | +0.198810311 | +0.162249411 | +0.162249411 | +0.153019689 | **none** |

## 2. The deterministic envelope is exhausted by the operator-level best

Two structural facts, derived rather than assumed:

**(a) The componentwise-best operator tuple dominates every other supply on all three atom constants.** A0, A1 and
A2 are each monotone decreasing in (τ↓, C_T↓, D1↓, D2↓, D_lo↑, Ā↓), so the tuple that is componentwise best on
the six operator constants simultaneously minimises all three A_j. Verified on every open cell: mixed ≤ C1, mixed
≤ C2 and mixed ≤ G, componentwise, 4/4 cells.

**Consequence:** a componentwise minimum over A-vectors — C2's D4 rule extended to include the mixed supply —
returns the mixed supply itself. **A-level mixing adds nothing.** C3 still pre-registers it, because a rule that
happens to be inert on this data must not be chosen after seeing that it is.

**(b) Per-sub-block mixing is identical to whole-cell mixing, not tighter.** One might hope to take, per sub-block
*i*, `min(τ_C1, τ_C2,i)` and only then compose by max. But min distributes over max:
`max_i min(a, b_i) = min(a, max_i b_i)`, and dually for the lower bound D_lo. So the finer construction yields
exactly the same six constants. **There is no gain to be had there**, and C3 does not claim one.

Together these say the operator-level best **is** the deterministic envelope available from committed evidence.

## 3. Blocker classification

### Cells 307, 308, 309 — **SCIENTIFIC BLOCKER**

No supply closes them, and the best available deterministic supply still requires uniform atom-constant reductions
of **1.111966 / 1.460655 / 1.847873**. This is not a certification or governance problem: the enclosure is simply
too wide. C2's phase-D1 diagnosis locates why — the order-3 residual f_G carries 73–80 % of the radius on every
tail cell, the operator constants act only through A0 with elasticity ≈ 0.82, and cell 309 would need A to fall to
47.6 % of its certified value, i.e. τ ≤ 2.48 against a certified 4.42 where τ bounds a genuine expected hitting
time. Operator-level tightening cannot bridge a factor of 1.85.

### Cell 306 — **GOVERNANCE / INDEPENDENCE BLOCKER**, not scientific, not certification

- *Scientific*: none. It closes, and the mixed supply closes it with more room than C2 had
  (Γ = −0.036197780 against C2's −0.030469258).
- *Certification*: none. Its eighteen artifacts re-certified bit-identically at 256 bits and remained valid at 384
  on a host whose OS, architecture, Python and Arb/FLINT build are recorded, and the full 105-artifact registry
  verification passed.
- *Independence*: **blocking.** Every supply that closes 306 — C1, C2, D4, mixed — is a Lemma Dv′ instantiation
  over the same `taboo_certify` Arb supersolution surface. `OPEN_NOTES_DISPOSITION_C2.md` N9 records that no
  second, independently written certifier exists; N10 records that the registry's build host is recorded nowhere.
  Lemma G, the one supply that touches none of that, leaves 306 **open** at Γ = +0.019115585.

**Mixing cannot repair this, and makes it formally worse.** Because the mixed supply is componentwise ≤ Lemma G, it
is strictly *more* dependent on the registry surface, not less. The best uniform-A margin any deterministic supply
gives 306 is **1.1555** — the factor by which every atom constant could be inflated before the cell reopens.

So the C2 adjudicator's prospective floor, which asks for either registry-independent closure or survival of a
×1.25 degradation, is **not reachable for 306 by any deterministic route available from committed evidence**: the
first disjunct fails (G does not close it) and the second fails (1.1555 < 1.25). C3 records this before freezing
its gate, and does not weaken the floor to change it.

## 4. The improvement figures depend entirely on which baseline is used

| cell | requirement under D4 (what r5 records) | under mixed | fall vs r5 | requirement under C1 | fall vs C1 |
|---|---|---|---|---|---|
| 307 | 1.140764 | 1.111966 | **20.46 %** | 1.262057 | 57.27 % |
| 308 | 1.500288 | 1.460655 | **7.92 %** | 1.663451 | 30.57 % |
| 309 | 1.899015 | 1.847873 | **5.69 %** | 2.101597 | 23.03 % |

The widely quoted **57.27 / 30.57 / 23.03 %** are measured against **Campaign C1 — two campaigns back** — because
that was the baseline C2's own gate froze. Against **r5, the current authoritative state**, the same step buys
**20.46 / 7.92 / 5.69 %**.

Both columns are arithmetically correct; they answer different questions. C3's gate measures against r5, because
that is the state C3 must improve on. Recording this distinction before the gate is frozen is deliberate: comparing
against a superseded baseline and presenting the result as current progress is the defect class C2's reviews caught
repeatedly, and it would flatter C3 by a factor of roughly three.
