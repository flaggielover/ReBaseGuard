# Independent review r3 (freeze readiness of 8d0c50c5; same fresh-context reviewer, read-only, nothing run remotely)

**Verdict: NOT_READY** — one blocking reason (B1). The registry itself is fine: re-assembled byte-identically
(1b7f5da7); every certified bound checked held against dense independent quadrature, including at the worst region.

Round-2 items: M1 remainder PARTIALLY_RESOLVED (see B1); M2 note RESOLVED; stale qualification RESOLVED; N1 RESOLVED (no
repository import outside the 13 pins; version strings, not library bytes, are bound; scipy has no certifying use); N2
RESOLVED (but not tied to the freeze commit, F2); N3 PARTIALLY (S08 only greps "DeflationRefusal"); N4 RESOLVED; N5
PARTIALLY (the guard prevents accidents, not deliberate misuse); N6, N7, N8 RESOLVED.

**B1.** S12 samples the atom-collapse line p+m = 1 too coarsely and tests against 0, not against the certified claims.
Dense scans with S12's own quadrature:

| certificate | S12 sampled extreme | dense-scan extreme | certified |
|---|---|---|---|
| taboo blocks 0 / 5 / 11, min w−1−K̂w | 0.0826 / 0.0808 / 0.0771 at (0.95, 0.05) | 0.0462 / 0.0437 / 0.0388 at (0.898, 0.102) | 0.0442 / 0.0416 / 0.0367 |
| taboo cells 0 / 148, max \|r\|/λ_mid | 0.67 / 0.60 | 0.950 / 0.931 near (0.9, 0.1) | ≤ 1 |
| taboo cells, max \|r\|/λ_cell | 0.55 / 0.48 | 0.82 / 0.74 | ≤ 1 |
| ARL cells 0 / 74 / 148, min W−1−KW | 0.068128 | 0.0680776 / 0.0866640 / 0.1304617 | 0.0680462 / 0.0866056 / 0.1303472 |

All consistent with the certificates, but with small slack, and a gate as written would pass a supersolution violated by
up to ≈ 0.036 at p+m = 1 or λ bounds ≈ 35 % too small. Planted bugs too coarse (P2 is 0.8·w, not "0.9 K̂"; P4 ÷10 while
the real sensitivity is ≈ 1.05). Missing checks: C_T ≥ max w, τ ≥ w(a), Ā ≥ W(a), d_j(0,0) inside candidate_at_atom (all
hold, checked locally). Fix: dense r ∈ {1−10⁻³, 1, 1+10⁻³} × ≥ 400 t plus near-axis strips, local refinement, compare
with the certified claims, localized planted bugs (0.02 bump near (0.9, 0.1); λ ÷ 1.2), the four checks. No rebuild needed.

Freeze procedure: sound; gaps F1 (post-freeze commits unrestricted — e.g. a committed code/json.py shadows the standard
library), F2 (qualification not tied to the freeze commit; `freeze_head` actually records the evaluation head), F3 (S08
should match the specific refusal and protocol sha, and log command/HEAD/status), F4 (untracked files must be committed
before make_protocol), F5 (compare S12 by tolerance, not bytes).
