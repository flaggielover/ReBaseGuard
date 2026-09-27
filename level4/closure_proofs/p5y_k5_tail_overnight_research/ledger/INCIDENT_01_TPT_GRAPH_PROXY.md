# Incident 01: qualitative target proxy in the dependency graph (TPT)

| item | value |
|---|---|
| found by | independent TPT review, `reviews/REVIEW_TPT_R1.md` blocker B1 (preserved at 32413877) |
| introduced by | the campaign coordinator (this session's main agent), commit 4403f86f, `graph/K5_TAIL_DEPENDENCY_GRAPH.md` §3 rank-1 row |
| class | **PROXY_EXPOSURE (qualitative)**: 1 target-equivalent proxy in the campaign record |
| new Γ evaluations | 0 |
| numbers computed on target cells | 0 |

## What happened

The rank-1 row of the looseness table combined two things in prose:
* the committed **tail-cell** shares of the radius sum S̄: A0·ρ·f_G ≈ 60 % and A0·ρ²·Env4/2 ≈ 20 %, both quoted from
  C5 for cells 306–309;
* theorem TPT's generic charges of ≈ 1/2 and ≈ 1/3 on the linear and quadratic Taylor terms (Proposition TPT-G).

The product is an estimator of TPT's reduction of the tail transport penalty. It is not Γ, and not its sign, but it is
"a ratio from which such a Γ could be inferred" in the sense of ROUTE_AUDIT_R1 §8. It also used target-cell data to
rank a route (charter S1). THEOREM_TPT.md stated that this combination "was not done". At campaign level that
statement was false.

## Motivation provenance (disclosure)

Before designing TPT (af4365aa), the coordinator knew from the programme's committed records and from its own project
memory of campaign C5 that, at the tail:
* the radius sum is dominated by the order-3 surrogate term (≈ 59–62 %) and the order-4 envelope term (≈ 20–23 %);
* the midpoint residual term is ≈ 0.1 %.

The first version of THEOREM_TPT §0 said that the midpoint radius is "typically orders of magnitude smaller" than the
edge radius. That sentence reflected this knowledge. It is true at the tail and false on the lower front (V3).

TPT's mathematical content is general, and no parameter of it was tuned. However, the choice to develop it first, and
the expectation behind that sentence, were informed by committed tail structure.

## Consequences (applied now, under the charter)

1. **TPT's tail application fails G8 at campaign level and cannot become FREEZE_READY in this campaign.**
   * Charter: a route that fails G1, G7 or G8 cannot be rescued tonight.
   * Route state for any 306–309 use: **BLOCKED (PROXY_EXPOSURE)**.
   * Theorem TPT, Lemma TC-P and TPT-B remain valid mathematics, VALIDATED_NON_TARGET on synthetic and lower-front
     data.
2. **Any future campaign that applies TPT, or any profile transport, to 306–309 must:**
   * carry this incident as a disclosed result-chasing liability;
   * obtain the user's floor-extension ruling knowing it (route audit U3 / §7 liability).
3. **The row is retracted** in `graph/K5_TAIL_DEPENDENCY_GRAPH.md` §3. The withdrawn text is quoted there, marked
   WITHDRAWN, and no longer asserted. THEOREM_TPT.md is corrected to disclose the combination and the motivation
   provenance.
4. **Ledger.** One line of class `PROXY_EXPOSURE` with `target_equivalent_proxies: 1` was appended. The final report
   will count 1 qualitative proxy, not 0.
5. **Scope check of other artifacts.** No other artifact of this campaign combines a new route's gain factor with
   tail-cell shares or factors. The coordinator checked by grep for the committed tail share figures and the C8/C3
   factor figures across `streams/`, `graph/` and `registry/`. The node table's "Dom" column quotes committed history
   (charter §5 asks for it) and attaches no route factor.
