# Erratum E2 to the consolidated D-* package r2 (Cell-308 Cloud route r1) — §3 provenance corrected after external B3 (Y3)

**Status: PROPOSED CORRECTION · ADVICE TO THE OWNER · NOTHING DECIDED.** This erratum replaces the table of
`CONSOLIDATED_DSTAR_PACKAGE_R2_ERRATUM_E1_20261016.md` §3 (sha256 `a71e277a…0b81`), which is preserved unchanged.

**Precedence:** E2 over E1 for §3 only. E1 §1–§2 stand, and package r2 (`038278fe…e5f`) stands where E1 does not
replace it.

Its source is external B3 (`reviews/external/REVIEW_EXTERNAL_B3_PROVENANCE.md`, `16188ffd…e96a`): trace rows T01–T11
(lines 67–79) and finding Y3 (lines 189–191).

**No value, threshold, definition or rule is changed.** Only the provenance statements are corrected. `DECIDED` stays
empty. `new_target_evaluations = 0` · `cell309_activity = none`.

## E2.1 — §3 table, replaced

**Column key:**
* **origin**: what is inherited from accepted or ratified text;
* **new content**: what this route adds;
* **class**: one of
  * **INHERITED** (an unchanged accepted number or rule);
  * **NEW MAPPING** (an accepted quantity re-expressed on Linux, not shown equivalent);
  * **FREE CHOICE**;
  * **POLICY SLOT** (a rule that needs an owner number);
* **later evidence**: what can exist only at a later stage.

| B3 row | constant / rule | value | origin | new content | class | later evidence |
|---|---|---|---|---|---|---|
| T01 | exclusivity window (D-EXCL-WINDOW) | 30 s | the **number** 30 s is R-FREE's reading cadence ("30 s apart") | using a sampling cadence as the **integration window** for a CPU share is a new choice. Ratification derives no exclusive-CPU window of that length | NEW MAPPING + FREE CHOICE (E1's "no, copied" is withdrawn) | process readings on the named host (OPS-7) |
| T02 | PSI readings (D-MEM-PRESSURE) | N = 3, 30 s apart | the **numbers** 3 and 30 s are R-FREE's attainability rule | moving them from free-memory attainability to PSI is discretionary. Three readings span **60 s**, first to last. They do **not** establish a continuous no-stall interval | NEW MAPPING + FREE CHOICE (E1's "no, copied" is withdrawn) | PSI on the named host |
| T03 | PSI field and level | `memory some avg10` displayed as `0.00` | ratification row 24's macOS normal-pressure code, as the analogy | choosing PSI, `some`, `avg10` and a displayed zero is an operational definition. It is **not** an equivalence derived from the macOS code. A displayed, rounded average of zero does **not** establish the exact absence of stalls. No PSI primary documentation or equivalence validation is supplied. A host without PSI fails | NEW MAPPING + FREE CHOICE; measurement non-equivalence stated | PSI readings |
| T04 | start-gate re-reads (amendment E1.5) | ≤ 3, every reading recorded, none after the marker | none | the number 3 has no derivation. The pre-marker-only limit and full recording are additional chosen controls. The initial reading plus up to three re-reads. Re-reading never turns an incomplete observation into a pass | FREE CHOICE (as E1 said) | — |
| T05 | physical cores (D-WORKERS-CORES) | ≥ 6 physical cores in the unit's effective cpuset, SMT siblings excluded; WORKERS 5 | WORKERS 5, and ratification item 15's rationale (5 workers on 6 cores, one spare) | turning an old host's rationale into a **new host criterion** (physical, cpuset-accessible, SMT excluded). It is not an unchanged threshold | NEW HOST CRITERION + FREE CHOICE (E1's "no, copied" is withdrawn) | topology and cpuset on the named host |
| T06 | thermal rule (D-THERMAL) | every readable zone below its lowest trip point of any type; a missing zone or trip fails; hwmon recorded only | the protocol-draft gate as described in brief R2 §9 (amendment E1.8) | "no number" is not "no choice". All trip types, the lowest-trip aggregation, the strict comparison, refusal on missing data, and hwmon excluded from gating are policy choices. No equivalence to the old pressure-level gate is shown | NEW RULE + FREE CHOICE (E1's "no number" is withdrawn as a claim of no choice) | zones and trips on the named host |
| T07 | HOST-row conditions (amendment E1.2, E2.1–E2.2) | four sufficient conditions | the RC2 pins (route A1 §1), MBR1_REPRO (route A1 §3), route E1 DR2 | combining L-DET MATCH, later pin equality, the expanded platform window and qualification MBR1_REPRO into **sufficient** conditions for a CONDITIONAL HOST row is a **new governance construction**. "Four" is its count, not a derivation of sufficiency | NEW GOVERNANCE CONSTRUCTION + FREE CHOICE (E1's "no" is withdrawn) | route-audit addendum A2 before any official step (matrix R4 B7). Satisfaction is not established now |
| T08 | window bound (amendment E2.7) | owner number; recommended 21 days (N2) | the accepted bounded-exposure principle (ratification row 19) | the rule's slot is a policy choice, and so is the recommended value (recommendations erratum E1.2) | POLICY SLOT; **no adopted value** | compliance from the interpreter build (OPS-5) |
| T09 | H7 / anchor response time (procedure r3 §5) | owner number; recommended 24 hours (N1) | ratification rows 18–19 | checker identity, timing origin and coverage must be fixed before operation (recommendations erratum E1.1) | POLICY SLOT; **no adopted value** | response capacity (OPS-10) |
| T10 | MBS-8 (ii) caps | by the frozen §3.2 rule: EVAL_CAP = max(6 h, ceil(2 × projection) in hours); per-job cap = max(3 × wall rounded up to 300 s, 1 800 s) | the accepted §3.2 formula (route A1 §3, route E1 N5, brief R2 §6) | choosing option (ii); the launcher translation; governance of the input series; N1's added ceiling (EVAL_CAP ≤ 24 h) | INHERITED formula; FREE CHOICE for the option and the ceiling | official non-holder decoy runs on the named host (stage C1). **No concrete caps exist now** |
| T11 | comparator digit limit (L-DET E1 §2) | `sys.set_int_max_str_digits(0)` | none | disables CPython's decimal-integer digit guard to avoid an INCOMPLETE that would consume the one attempt. Choosing an unlimited conversion rather than a justified finite bound is a technical choice. The CPython default of 4,300 is stated by L-DET E1 and was not checked against CPython's documentation here | FREE CHOICE (technical) | implementation review (B9) |

## E2.2 — What the table does and does not claim

* **Target-free means no target observation is needed to formulate or assess the rule.** It does **not** mean the
  source documents contain no MB r1 runtime of any kind. The ratification and brief R2 contain historical non-target
  (decoy and host) runtime evidence. No such runtime is needed to recompute the copying or arithmetic above (B3 line
  63).
* A rationale written now **does not show historical non-dependence**: it cannot show what every author of the earlier
  texts knew.
* A traced discretionary proposal is **not** a uniquely derived or ratified constant. Each NEW MAPPING, NEW RULE and
  FREE CHOICE row amends or adds to an accepted measurement rule only if the owner adopts it, and expressly sets aside
  ROUTE_PREPARATION line 19 where E1 §2 lists that rule.
* The rules B3 found outside this table (O01–O30, X01–X09, Z01–Z06) are traced in
  `PROVENANCE_DISPOSITION_RECORD_B3_20261016.md`.
