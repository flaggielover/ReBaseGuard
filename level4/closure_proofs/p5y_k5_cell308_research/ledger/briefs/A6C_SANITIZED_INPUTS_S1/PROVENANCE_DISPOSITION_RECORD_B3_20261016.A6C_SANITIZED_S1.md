# Consolidated provenance and disposition record after external B3 (Cell-308 Cloud route r1)

**Status: PROPOSED RECORD · TEXTUAL PROVENANCE ONLY · NOTHING ADOPTED, IMPLEMENTED OR EVIDENCED OPERATIONALLY.** This
record answers external B3 findings Y4 and Y6 (`reviews/external/REVIEW_EXTERNAL_B3_PROVENANCE.md`, `16188ffd…e96a`,
lines 193–203). It brings every route-introduced number and rule that B3 traced into one place:
* T01–T11 and N1–N2: the trace table, lines 67–85;
* X01–X09: the brief r2 item 1a rules, lines 89–99;
* Z01–Z06: the procedure-E2 clarification, lines 101–112;
* O01–O30: the omissions, lines 114–151.

**B3's verdict is kept with its qualification. A label alone is never the record.** No value, definition, threshold or
rule is changed here. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Categories (each row marks every category that applies)

| code | category |
|---|---|
| **INH** | an inherited number or rule from accepted or ratified text, unchanged |
| **MAP** | a new mapping of an accepted quantity onto Linux or the new route. Equivalence is not shown |
| **CHO** | a free choice: policy or engineering content that the origin does not uniquely entail |
| **PSC** | primary-source corroboration missing: a technical or provider fact asserted but not verified from its primary source here |
| **FUT** | a future artifact: a concrete output (commit, value, view list, code, attestation) that does not exist yet |
| **OPS** | operational evidence that can exist only at a named later stage |

Common to every row (B3 lines 61–63):
* No MB r1 target-run observation is needed to formulate or assess the rule.
* "Traced" does not mean that every upstream primary source was inspected, that the authors' private knowledge was
  verified, that the rule is adopted, or that it was observed to operate.
* Ratification and brief R2 contain historical **non-target** runtime evidence. A claim that they contain no MB r1
  runtime of any kind would be false.

## 2. T01–T11, N1, N2

T01–T11 are corrected in package erratum E2, and N1–N2 in recommendations erratum E1. They are summarised here so the
record is complete.

| id | categories | B3 verdict and qualification (abridged faithfully) | gate where remaining evidence arises |
|---|---|---|---|
| T01 | INH (30 s), MAP, CHO | TRACED_WITH_FREE_CHOICE: the number is copied; using a sampling cadence as an integration window is new | OPS-7 (B4 onward) |
| T02 | INH (3, 30 s), MAP, CHO | TRACED_WITH_FREE_CHOICE: moved from R-FREE to PSI; spans 60 s, not a continuous window | B4 |
| T03 | MAP, CHO, PSC | TRACED_WITH_FREE_CHOICE: an operational definition, not an equivalence; a displayed zero is not the exact absence of stalls; no PSI primary documentation | B4 |
| T04 | CHO | TRACED_WITH_FREE_CHOICE: 3 has no derivation | — |
| T05 | INH (WORKERS 5), CHO | TRACED_WITH_FREE_CHOICE: a new host criterion | B4 |
| T06 | CHO | TRACED_WITH_FREE_CHOICE: aggregation and missing-data policy are choices; no equivalence to the old gate | B4 |
| T07 | INH (bases), CHO | TRACED_WITH_FREE_CHOICE: a new governance construction; sufficiency is not derived | B7 (route-audit A2) |
| T08 | CHO, FUT | TRACED_WITH_FREE_CHOICE as a slot; UNTRACED as an adopted value | A17; OPS-5 |
| T09 | CHO, FUT | TRACED_WITH_FREE_CHOICE as a slot; UNTRACED as an adopted value; no response-capacity evidence | A17; B1; OPS-10 |
| T10 | INH (formula), CHO, FUT, OPS | TRACED (formula); TRACED_WITH_FREE_CHOICE (option, translation, N1 ceiling); concrete caps UNTRACED, not yet produced | C1 |
| T11 | CHO, PSC | TRACED_WITH_FREE_CHOICE: unlimited rather than a finite bound; the CPython default was not independently checked | B9 |
| N1 | CHO, OPS | TRACED_WITH_FREE_CHOICE: choices C1–C6 (recommendations E1.1); a planning envelope, not capacity | A17; OPS-10 |
| N2 | CHO, PSC (narrowed) | TRACED_WITH_FREE_CHOICE: choices D1–D4; the cadence does not establish an update-free interval; B3's source fetch failed, and the coordinator side's recorded retrieval is not independent (recommendations E1.3) | A17; OPS-5 |

## 3. X01–X09 (brief r2 item 1a)

| id | rule | categories | B3 verdict and qualification | gate |
|---|---|---|---|---|
| X01 | L-DET E3.1 record → view → leaf order | INH (the five-record order, from the reference addendum), CHO, FUT | TRACED_WITH_FREE_CHOICE: priority use, depth-first pre-order, code-point key order and array index order are deterministic choices. The per-record view declaration is a future reviewed artifact, bound before OD-3 | B13 |
| X02 | E3.2 Decimal eligibility and mutation | CHO | TRACED_WITH_FREE_CHOICE: the precision bound (digit count + 41) is an engineering bound. Eligibility is computed inside the authorized attempt | B14 |
| X03 | offset 40 and `fs` fallback | CHO | TRACED_WITH_FREE_CHOICE: 40 is expressly discretionary. Eligibility is decided by the stated tests, not by a magnitude heuristic | B14 |
| X04 | two passes; NOT_APPLICABLE | CHO | TRACED_WITH_FREE_CHOICE: NOT_APPLICABLE is a chosen coverage boundary, not proof that the exactness control ran. NOT_APPLICABLE and INCOMPLETE are not interchangeable | B14 |
| X05 | in-attempt timing; bounded output; no extra trial | CHO, OPS | TRACED_WITH_FREE_CHOICE: output minimisation and the schema are new controls. Whether they were obeyed is operational evidence | B14 |
| X06 | L-DET E2.1 source tokens verbatim | CHO | TRACED_WITH_FREE_CHOICE: a strict reproduction contract in addition to rational equality. The older `default=str` proposal does not govern | B9 (implementation) |
| X07 | E2.3 bytecode caches | CHO, FUT | TRACED_WITH_FREE_CHOICE: the manifest exclusion **plus** an independent cache-absence check form the rule. Implementation is unverified | B9; B10 |
| X08 | procedure r3 E1.2 NOT_COMPLETED; appointment coverage | CHO | TRACED_WITH_FREE_CHOICE: adverse like REJECTED; the upstream B1 / FR2 excerpts were not independently verified by B3 | B6; B11 |
| X09 | E1.4 withdrawal of per-part veto scoping | CHO, FUT | TRACED_WITH_FREE_CHOICE: a broad defence-in-depth policy. It needs an implementation review and cannot be inferred to exist from text | B8; B9 |

## 4. Z01–Z06 (procedure r3 erratum E2, the Z1 clarification; Y7)

All six are **author proposals**. Procedure E2 labels itself AUTHOR-PROPOSED, NOT INDEPENDENTLY CONFIRMED, NOT
ACCEPTED, NOT IN FORCE and NOT IMPLEMENTED. Its precedence is limited to its named wording, and its pin (`d4bdf26a`) is
separate. B3 did not inspect the B1 excerpt or receipt it cites.

| id | rule | categories | B3 verdict and qualification | gate |
|---|---|---|---|---|
| Z01 | permanent machine-wide refusal on REJECTED or NOT_COMPLETED | CHO | TRACED_WITH_FREE_CHOICE: explicit policy, not derived and not accepted | A15 |
| Z02 | a pending entry ends only by its own valid ACCEPTED | CHO | TRACED_WITH_FREE_CHOICE: ACCEPTED is not a general reset | A15 |
| Z03 | planned review time is waiting, not a failed check | CHO | TRACED_WITH_FREE_CHOICE: authorizes no step while pending; pauses or extends neither N2 nor the deadline | A15 |
| Z04 | an actual refused check stays refused | CHO | TRACED_WITH_FREE_CHOICE: a later acceptance does not remove an incurred stop | A15 |
| Z05 | NOT_COMPLETED cannot be withdrawn or relabelled | CHO | TRACED_WITH_FREE_CHOICE: closes a bookkeeping escape. It supplies **no** review-completion deadline | A15 |
| Z06 | named-wording precedence; implementation requirement | FUT | TRACED as precedence; code, tests, acceptance and adoption UNTRACED | B8; B9 |

## 5. O01–O30 (rules the short trace omitted)

| id | subject | categories | B3 qualification kept | gate |
|---|---|---|---|---|
| O01 | Linux free memory: min(MemAvailable, MemFree + Inactive(file), every ancestor limit − usage); H6 / initial-namespace prerequisite | MAP, CHO, FUT | a new mapping of R-FREE; no proof of equivalence to vm_stat; cgroup quantities are host inputs | B4 |
| O02 | idle usage / W_idle analogue; effective limit; root / no-limit case | MAP, CHO | changes a measurement definition; R-MEM factors and floors stay inherited | B4; C1 |
| O03 | low-power profile / governor / EPP cases; no-interface statement | MAP, CHO, PSC | chosen Linux predicates; no primary-source Linux equivalence verification | B4 |
| O04 | no-supply AC substitute; chassis criterion; lid; supply statuses | MAP, CHO, OPS | an owner statement substitutes for an AC reading; the interruption rule is retained | B4 |
| O05 | CLOCK_MONOTONIC awake time; bare metal only; no CLEAN without a reviewed journal reader | MAP, CHO, FUT | the old sleep / sample tolerances are inherited by reference, not re-derived; their values were not checkable without non-allowlisted code | B8; B9 |
| O06 | exclusivity: 25 % of one CPU kept; no hosting-app exception; fail-closed observability | INH (25 %), MAP, CHO | the measured quantity, the exception removal and the observability predicates are new. Re-reads do not turn an incomplete observation into a pass | B4 |
| O07 | no Linux allow-paths; drop the 39 macOS names | CHO | stricter, but a policy amendment, not derived from Linux daemon measurements | A17 |
| O08 | CPython 3.14.5 from the tarball; build provenance; prefix / libpython / worker / post-job pins | INH (version continuity), CHO, FUT | the source hash, toolchain, flags, import closure and no-late-map evidence are future, UNTRACED as artifacts | B10 |
| O09 | launcher translation; process identity and liveness; RSS units | MAP, CHO | Linux implementation conformance not established | B9 |
| O10 | launcher timeouts carried (30 s, 15 s, 2 s, PRE_CAP + 100 s) | INH (numbers), CHO | adequacy under systemd is not established by launchd measurements | B9 |
| O11 | update-vector coverage; unit classification | CHO, PSC | the complete 13-root systemd search list and the provider semantics are UNTRACED at primary-source level | B4; B5 |
| O12 | sleep prevention; boot identity; durable writes; stale temporary files; 2 GiB disk floor | INH (2 GiB), CHO, OPS | the 2 GiB rationale is host-specific; its adequacy on a new host is not established | B11 (P2) |
| O13 | S15 store listing; first listing anchored before OD-3; two-marker assertion | CHO, OPS | store completeness is partly an owner statement | B12 |
| O14 | every SUBST item and its cross-check | CHO | DMI is mandatory with no substitute; H7 and the anchor have **no** independent measured cross-check; host software can falsify its own readings | B4–C7 |
| O15 | no L-DET repeat; disclosure; no repair after mismatch; qualification MBR1_REPRO kept | CHO | a pre-marker stop does not restore an L-DET attempt | B14; C5 |
| O16 | exact comparison contract | CHO, FUT | a count > 0 is structural non-vacuity, **not** proof of full certified-field coverage; the pinned views / strip / serializer are still required | B9; B13 |
| O17 | four cases / five records; QC04 serial inclusion; source-digest convention | INH (records), CHO | the record and function bytes were not read by B3 | A16 |
| O18 | L-DET commit and evaluation-path equality; differing files; view declarations | CHO, FUT | the concrete commit, view list and permitted-difference list are UNTRACED, not supplied | B13 |
| O19 | H1–H8; window from the interpreter build; A2 before official steps; H8 DMI | CHO, FUT, OPS | provider terms, owner actions and repeated identities are not established | B2–B10 |
| O20 | reviewer eligibility; direct channel; appointment identity; P1 / P2 mappings | CHO | integrity rules do not prove independence by themselves | B6; B11 |
| O21 | R / C distinction; ordering; git-object basis; no self-assertion; external adverse records | CHO, FUT | code conformance unverified | B8; B9 |
| O22 | decisions before host information (21 D-*, N1 / N2, MBS-6 / 7 / 8) | CHO | **TARGET_INFORMED_RISK** if the deleted Q12 input were reinstated, or a gate changed after readings. Nothing proves the earlier risk was exercised, or that all historical preparers were unexposed | A17; A18; OPS-3; OPS-4 |
| O23 | all-outcome, all-platform finality | CHO | broadens the older INDETERMINATE-only wording; no owner record exists | A15; A18; C6 |
| O24 | every host disclosed; no host shopping before or after L-DET | CHO | **TARGET_INFORMED_RISK**: host resources or earlier failures can affect completion selection. A rule requiring target-free decisions is not evidence that a specific OD-1 decision met it | B2; OPS-1; OPS-2 |
| O25 | post-marker non-action incidents; fixed deadline; EVAL_CAP ≤ 24 h and stop before the freeze | CHO, OPS | adds policy beyond the historical caps; no response-capacity or elapsed-overhead evidence | C1; OPS-10 |
| O26 | V-A runner stopped and disabled, build to seal | CHO, OPS | no process-list evidence | OPS-6 |
| O27 | E8 extended to decision documents | CHO | a broadened output boundary | every decision document |
| O28 | source classes; separation of text / adoption / implementation / operations / authorization | CHO | a PC is not a VC, OD, IT, OPS or AX; historical standing issues remain limits | all rows |
| O29 | rule-by-rule line-19 set-asides; host-choice hygiene | CHO | ROUTE_PREPARATION itself was not fetched by B3; any extra host property needs a target-free reason and a non-holder check | A17; B2 |
| O30 | the procedure-E2 adverse / pending / wait / finality rules | CHO | see §4 | A15 |

B3 found no further route-introduced constant in its bounded search. That is not a claim about non-allowlisted code
or documents (line 151).

## 6. Disposition (Y4, Y6)

* **Y4 (MAJOR): addressed in text by this record.** The short trace in package E1 §3 is no longer presented as
  exhaustive, and every omitted rule appears here with B3's qualification.
* **Y6 (MAJOR): addressed in text.** Textual provenance discharges **no** operational, implementation or non-holder
  condition. Specifically:
  * no row of this record marks OPS, IT or AX;
[A6C-SANITIZED S1: original line 127 redacted, class R: reference to the historical T6 mitigation series, B2-derived]
  * the deleted Q12-informed MBS-8 input stays deleted. Reinstating it, or changing a gate after readings, would
    restore a target-informed selection risk (O22).
* **Code-level constants.** Constants that only the successor build will introduce do not exist yet. They are not
[A6C-SANITIZED S1: original line 131 redacted, class R: reference to the historical T6 mitigation series, B2-derived]
  B9-T). Any untraced code constant blocks the interpreter build (B10).
[A6C-SANITIZED S1 artifact of level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROVENANCE_DISPOSITION_RECORD_B3_20261016.md at 4f814796757bb1a14086b88d677adef94309d0f6 (14529 bytes, sha256 f8987a938a80dd0189ab1af7fc4f80ed01cae02f6d20dff39b3416eae8012046). 2 lines redacted line-for-line (R=2); every other line is byte-identical to the original; line numbers are preserved.]
