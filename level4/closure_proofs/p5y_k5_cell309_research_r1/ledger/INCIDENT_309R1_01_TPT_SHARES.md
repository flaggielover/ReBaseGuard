# Incident 309R1-01: coordinator exposure to tail radius shares (TPT proxy class)

| field | value |
|---|---|
| when | 2026-09-29, Phase 0, before any theory, implementation or route selection of this campaign |
| who | the coordinator (main agent) |
| class | PROXY_EXPOSURE (qualitative; nothing computed, nothing written down as a number) |
| how | A `grep -n "30[5-9]"` over `THEOREM_TPT.md`, `FREEZE_DESIGN_TPT_TAIL.md` and `reviews/REVIEW_TPT_R1.md`, run to test whether those files carry tail numbers, printed its matched lines. The lines of `REVIEW_TPT_R1.md` (29, 49–61) quote the material withdrawn in overnight incident 01: committed per-Taylor-order shares of the tail radius S̄ at 306–309. |
| what | the share of S̄ carried by the order-1 (ρ·f_G-type) term and by the A0·ρ²·Env4/2 term at 306–309, and the A0·f_H share; plus the sealed Γ(5, 306; S_I2) |
| aggravating | earlier in Phase 0, `graph_A_consumer.md` §2 (necessary reading, ledgered) showed the committed 309 gap between the clause-tolerated A0 and the Λ floor. With both, the coordinator formed a rough mental impression of how TPT's generic order factors (1/2, 1/3) compare with that gap at 309. That impression is a qualitative target-equivalent proxy of the same kind as overnight incident 01. |
| not done | no code was run, no number was computed or written, and nothing was tuned |

## Consequences, fixed now, before any route work

1. **TPT at 309 is liability-bearing for this campaign.**
   * Any 309 route whose closure power comes from the TPT transport carries overnight incident 01, and now also
     incident 309R1-01.
   * Its motivation-provenance risk is rated **HIGH**, not MEDIUM.
   * This campaign may study TPT as mathematics: it may re-derive and strengthen the theorem and validate it on decoys.
     It may not present a TPT-based 309 route as clean prospective evidence.
   * Selecting TPT for 309 requires an explicit user governance decision taken with both incidents disclosed.
2. **Route selection rule.** A preferred route may be chosen only by a target-free rule that is written down before any
   comparison, such as a dominance or composition rule, and never by this impression.
3. **Search practice.** From now on the coordinator uses only `grep -l` or `grep -c` on files under tail-cell
   namespaces. Documents that may carry tail numbers are read by firewalled readers.
