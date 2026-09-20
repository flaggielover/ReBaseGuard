# K5 Campaign C1 — certified operator-only registry extension over the CUSUM m = 5 tail (cells 305–309)

Additive namespace. Start: `p5y-postk1-frontier` at `76c37de1`, after Campaign B stopped under its own frozen
`stop_rule`. Nothing outside this namespace is modified; AWS SR/PS1 untouched; `main` untouched.

**Policy: `NEW_REAL_ADDRESSES = 0`.** C1 evaluates no new real scientific value. It certifies *operator* quantities
only — supersolutions of the kernel, the taboo resolvent and the renewal denominator — and consumes them through the
adopted theorem TC-T and the frozen K5-B. `REAL_SCIENTIFIC_COMPUTE` stays **DENY** for the whole campaign. If any
step turns out to need a new real scientific address, the campaign stops and hands a C2 design to a successor.

## Why C1 exists

Campaign B established that theorem TC-T with Lemma G's *generic* atom constants (A0 = C_upper, A1 = k₁C²,
A2 = k₂C² + 2k₁²C³) closes cell 305 and leaves 306–309 at 0.941×, 0.761×, 0.607× and 0.497× of what the frozen K5-B
needs. Those constants are the non-sharp one-sided block bound. Theorem AD's Lemma Dv′ replaces them with
A0 = Ā_eff ≥ sup E_a[τ] and its companions, supplied by a **certified operator registry** — machinery that already
exists and is adopted (`p5y_k5_perron_deflated_resolvent`), but whose registry r1 certifies only e ∈ [0, 0.1147].
The tail is e ∈ [1.6209, 2.0923]. C1 extends the certification to that domain and nothing else.

The open question, which C1 does **not** presume: *how many of the five tail cells can a certified operator-only
extension close?* Campaign B's own continuation note put the required uniform atom-constant reduction at
1.071× / 1.362× / 1.771× / 2.253× on cells 306…309 and gave two disagreeing indications of what is achievable — a
2.46× historical precedent at e = 0 and a ≈ 1.7× renewal heuristic. 5/5 is not assumed.

| phase | where | state |
|---|---|---|
| gate (frozen **before** any forecast) | `config/FEASIBILITY_GATES_C1.json` | frozen at this commit |
| A. authoritative-input verification | `code/`, `evidence/` | — |
| B. tail operator certification and forecast | — | — |
| C. execution decision under the frozen gate | — | — |

K5 remains **PARTIAL** (m = 5 open on 305–309) and coverage map r4 (`a3bddd83…`) remains authoritative until an
adopted C1 result says otherwise.
