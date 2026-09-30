# Independent package review R3 of the P309 formal-campaign package (candidate)
PACKAGE_REVIEW: COMPLETE_WITH_NOTES

**Status.** Final, 2026-09-30, written 00:19–00:4xZ. I reviewed HEAD `f1f8a459`: the package content commit is
`ce829bb4`, the manifest commit `65b64e9e` and the brief `b48a1fa2`. The tree was clean and no campaign process was
running. I am neither the R1 nor the R2 reviewer, and I have no stake in the outcome. Brief:
`reviews/BRIEF_P309_PACKAGE_REVIEW_R3.md`.

During the review, the coordinator (not I) committed and pushed a WIP snapshot of this file's declaration draft
(`1d8efbbb`, 00:26:44Z) and its push record (`a231594d`). I checked `git diff --stat f1f8a459 HEAD`: those commits touch
only this file and `ledger/CHECKPOINT_PUSHES.jsonl`. `protocol_prep/` and every pinned file are unchanged, so the
findings below hold at `a231594d`. The snapshot is not a verdict source; this file's final text is.

**Bottom line.**
* The package covers all 15 Phase-4 items. The consumer criterion is fixed, exact and strict. The route, the gate and
  the adapter are carried over faithfully, and FC1–FC6 (including the FC2 extension) are all present.
* I found no path by which the target could be evaluated twice, without the historical control, or with parameters
  chosen after a 309 number exists.
* Every pin I could check matches the committed files.
* The notes below are text-level fixes. Four of them (N1–N4) should be settled in the text **before** the owner freezes
  the package. Once frozen, each would become a rule change.
* Nothing here authorizes anything. A freeze still requires the owner (P0-1).

---

## 0. Reviewer execution declaration (written 2026-09-30T00:19Z, before any run beyond read-only checks)

Rules I follow:
* `PYTHONDONTWRITEBYTECODE=1`.
* Library calls only, never a `__main__` that writes evidence.
* The q309 exec and exposure ledgers are redirected to `scratchpad/r3/` (`q309_guard.EXEC_LEDGER`, `EXPOSURE_LEDGER`).
* Nothing is written in the repository except this file, and no git write.
* I do not open `ledger/EXPOSURE_LEDGER.jsonl`, `ledger/INCIDENT_*` or any file outside NS.
* I also do not open the NS files most likely to carry 305–309 numbers: `dossier/CELL309_DOSSIER.md`,
  `dossier/digests/*`, `dossier/sources/READER_A_*` and `dossier/ROUTE_MATRIX.md`.

| id | what | kernel / geometry / drift | evaluates? |
|---|---|---|---|
| RD3-0 | Read-only checks: git metadata (`rev-parse`, `ls-tree`, `log`, `diff --stat`, `merge-base`); for pins outside NS, the blob id by tree lookup only (no content read, no sha256 of their bytes); sha256 of NS committed blobs and working-tree files; JSON metadata of NS decoy evidence (rung status, runtime seconds) and `verify/VERIFY_RESULTS.json` (settings, timing); the dangling NS commit `5ddf7b58` (manifest tool) | none | no |
| RD3-1 | `code/self_audit.py`: `run("r3")` in-process through a scratch wrapper. Its A10 subprocess (`code/verifier_probe_envelope.py`) is replaced by a scratch wrapper that runs the same `main()` with the one output write redirected to scratch. Audit JSON to scratch. Includes the tool's own git reads and `git ls-remote origin` (a network read) | none (A10 rebuilds probe dicts only) | no |
| RD3-2 | `code/verifier_probe_envelope.py` `main()` through the same wrapper (output to scratch) | none | no |
| RD3-3 | NS tests via their `run()` functions, in-process, ledgers redirected: `test_q309_guard`, `test_srk_gate` (constructed objects, h = 3), `test_srk_adapter` (manufactured objects), `test_srk_assembly_twosided` (exact algebra), `test_srk_envelope` (real-kernel envelope primitives, drifts in [0, 1/2]) | real kernel only at e ∈ [0, 1/2] (envelope primitives); otherwise none | envelope primitives only |

Not run:
* any producer or verifier on any certificate;
* `test_srk_port_identity` and `test_srk_fsm_truth`, which import overnight modules outside NS and are not needed here;
* `e2e_cell_family`, `srk_mc_control`, `test_srk_cert_mutants`, `test_verify_selftests`, `run_verify_all` and
  `build_evidence_manifest`.

Nothing touches cells 305–309 or evaluates any drift in [6/5, 13/5] or its mirror.

**Executed as declared.** Scratch files are in `scratchpad/r3/`: `audit_wrap.py`, `vpe_wrap.py`, `tests_wrap.py`,
`SELF_AUDIT_r3.json`, `VERIFIER_PROBE_ENVELOPE_r3.json` and `tests_r3.json`.
* **RD3-1 (self-audit):** A1–A10 all PASS. Max ledgered |drift| is 37/32 over 534 ledger lines and 19 evidence files.
  A11: local HEAD = remote tip = `f1f8a459`; the only dirt is this file.
* **RD3-2 (envelope):** the output is **byte-identical** to the committed `evidence/VERIFIER_PROBE_ENVELOPE.json`
  (`cmp`), with ok = true. v1 real [−1/8, 37/32]; v2 real [−1/3, 37/32]. There are 0 in-band evaluated probes, and the
  self-test real-kernel max |e| is 1.0497.
* **RD3-3 (tests):** all five pass:
  * q309 guard 7/7;
  * gate 33/33;
  * adapter 19 checks × 20 cases, including `geometry_override_impossible` and `real_geometry_immutable`;
  * two-sided assembly: genuine equal, all 10 textual mutants caught, 7 refusals;
  * envelope: 0/240 sandwich failures, 4/4 wrong-corner mutants caught.
* No `log_execution` call was reached, so the scratch exec ledger was never created.
* Nothing in NS was written: the pycache and evidence timestamps all predate the run, and `git status` shows only
  this file.

---

## 1. Findings per brief item

### Item 1. Completeness: PASS (with NOTEs N5, N6, N13, N14)

| Phase-4 item | where | finding |
|---|---|---|
| prospective protocol | `protocol_prep/P309_PROTOCOL.md` (whole) | present |
| frozen parameter specification | `P309_FORMAL_PACKAGE.md:8-23` (§A) | present; pin list gaps in N13 |
| target quarantine rules | `P309_PROTOCOL.md:108-114` (§6), `:116-130` (§7); QC12 `P309_FORMAL_PACKAGE.md:42` | present (inherited, stricter-only) |
| qualification suite | `P309_FORMAL_PACKAGE.md:25-48` (QC01–QC16) | present; gaps in N4, N14 |
| independent review brief(s) | `P309_FORMAL_PACKAGE.md:120-136` (§G.1, §G.2) | present as **outlines** (N5) |
| exactly-once driver design | `P309_FORMAL_PACKAGE.md:50-83` (§C) | present |
| grant schema | `P309_FORMAL_PACKAGE.md:85-94` (§D) | present; names Ew, `verifier_id` and `in_band_verification` |
| recording the result from memory | `P309_FORMAL_PACKAGE.md:96-104` (§E), §C step 10 (`:80-81`) | present; content note in N1 |
| post-execution checks | `P309_FORMAL_PACKAGE.md:106-118` (§F) | present; N10 |
| execution-review brief | `P309_FORMAL_PACKAGE.md:131-133` (§G.3) | outline with 11 enumerated checks (N5) |
| adjudication rule | `P309_FORMAL_PACKAGE.md:138-141` (§H) and `P309_PROTOCOL.md:95-106` (§5) | present |
| adjudication-review brief | `P309_FORMAL_PACKAGE.md:134-136` (§G.4) | outline (N5) |
| failure and recovery semantics | `P309_FORMAL_PACKAGE.md:143-157` (§I); `P309_PROTOCOL.md:102-105` | present; ambiguity in N2 |
| pinned source hashes and constants | `P309_CANDIDATE_FREEZE_MANIFEST.json`; §A `:18`, `:21` | present and verified (item 6) |
| candidate freeze manifest | `P309_CANDIDATE_FREEZE_MANIFEST.json` | present |

The package also mirrors the 307 anatomy (`dossier/sources/READER_B_GOVERNANCE_REPORT.md:54-103`). The exceptions are
small:
* there is no explicit provenance-timeline step or latent-proxy addendum (anatomy items 2 and 5);
* "handover" (item 19) is not mentioned;
* there is no explicit S-construction QC (N14).

### Item 2. Consumer criterion fixed before any target evaluation: PASS (with NOTEs N3, N12, N17)

* **Criterion.** "Γ < 0, strict. Γ = 0 or an incomplete evaluation is NOT pass" (`P309_PROTOCOL.md:89`). It is exact
  rational (`:88`; §E stores Γ "as an exact rational string", `P309_FORMAL_PACKAGE.md:101`) and it is repeated in the
  grant's `closure_criterion` (`P309_FORMAL_PACKAGE.md:87`).
* **Outcome table.** `P309_PROTOCOL.md:95-106` has a catch-all row "any post-marker failure → EXECUTION_INDETERMINATE"
  (`:102`) and a CONTROL_FAILED row (`:103`). It says "Strictness, rounding, tolerance, margin and adoption semantics
  never change after the freeze" (`:106`).
* **Scope.** CLOSURE_ONLY (`P309_PROTOCOL.md:34`; grant `closure_only` true, with adoption, floor, r6 and K5/P5Y all
  NOT AUTHORIZED, `P309_FORMAL_PACKAGE.md:87-89`). Adjudication applies §5 verbatim with an exact-Fraction recomputation
  (`:138-141`).
* **Would a freeze commit them unchanged?** Yes, under the default U3 = CLOSURE_ONLY. §A's scope row
  (`P309_FORMAL_PACKAGE.md:14`) and P0-3 (`P309_PROTOCOL.md:18`) allow a prior frozen U3 floor extension. That would
  need a revised outcome table and grant before the freeze, so "commit them unchanged" holds only under CLOSURE_ONLY
  (N17).
* **Ambiguities (text-level).**
  * Row 1 requires "independent checks equal" (`P309_PROTOCOL.md:99`), but the package never says which in-run
    independent checks these are, and no row covers "unequal" (N3).
  * Row 3 reads "TARGET_EVALUATED; Stage-1b CERTIFICATION_FAILED" (`:101`) without saying whether Stage 2 runs after a
    Stage-1b failure. The outcome (NOT_CLOSED) is fixed either way (N12).

### Item 3. Consistency with the reviewed route: PASS (with NOTE N1)

* **THEOREM_SRK §3.** The S2 substitution of rad_r by rad_r^SRK = A0 f_H + ρB3 + (ρ²/2)B4 + 2A1p1 + A2p0
  (`theory/THEOREM_SRK.md:105-107`) is what the protocol invokes (`P309_PROTOCOL.md:32-33`). §4's "only the order-0
  channel term" (`THEOREM_SRK.md:142-152`) matches the adapter (`impl/srk_adapter.py:103-122`).
* **THEOREM_SRK §11.** Ew = [⌊e_lo·2¹⁰⌋/2¹⁰, ⌈e_hi·2¹⁰⌉/2¹⁰], four equal sub-blocks, every certificate with weight block Ew
  (`THEOREM_SRK.md:305-309`). This matches `P309_PROTOCOL.md:38-40` and §A `P309_FORMAL_PACKAGE.md:15-16`. The rule
  "Γ̄_i = max_j min(admitted rungs on b_j), else None" (`THEOREM_SRK.md:332`) matches `P309_PROTOCOL.md:57-60`.
* **THEOREM_SRK §12 constants.** μ = 2⁻²⁰, base cover 1/4, ≤ 4 extra levels (≤ 3 for W ≥ 0), KT = 10, 96/24/40 bits,
  40-bit root brackets, 2⁻¹⁰ hull and N_E = 4 (`THEOREM_SRK.md:344-355`). All match `P309_PROTOCOL.md:44-46` and §A
  `:18`.
* **Gate.** The protocol's admission list (`P309_PROTOCOL.md:47-53`) is a faithful subset of G1–G6
  (`impl/srk_gate.py:6-16`, `:138-180`) and defers to "rules G1–G6". I re-ran the gate test: 33/33.
* **Adapter.**
  * Signature `srk_enclosure(meas, A, m, cell, gate_result, frozen_obj, frozen_lohi, coefficients, *, verifier_id)`
    (`impl/srk_adapter.py:96-97`). The protocol call (`P309_PROTOCOL.md:78-79`) matches it in order and keyword.
  * Every refusal the protocol lists (`:80-85`) exists: reproduction (`srk_adapter.py:110-114`); cell, geometry, kernel
    and verifier (`:73-78`, `:88-89`); source (`:67-68`); rho (`:79-80`); float cell (`srk_gate.py:88-92`).
  * The adapter also refuses non-GateResult inputs, wrong index sets, Ĝ ≠ 0 and dominance violations
    (`srk_adapter.py:65-66`, `:82-83`, `:107-108`, `:121-122`).
  * The geometry is fixed with no override (`:57-59`). I re-ran the adapter test: 19 × 20.
* **Rule S and the SRK-T exclusion.** SRK-T is OUT under C5 (`registry/ROUTE_SELECTION_RULE.md:17`, `:27`;
  `registry/PHASE3_ROUTE_COMPARISON.md:84-102`). This is carried at `P309_PROTOCOL.md:61-62` and §A `:17`, and enforced
  by the adapter (`PACKAGE1_SOURCES = {GATE, EMPTY}`, `srk_adapter.py:60`, `:67-68`). ERRATA E-15's binding of any
  future SRK-T package is reflected in the optional owner row (`P309_OWNER_DECISIONS.md:26`).
* **Supply S.** S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)) is identical in `P309_PROTOCOL.md:30-31`,
  `P309_FORMAL_PACKAGE.md:13` and `ROUTE_SELECTION_RULE.md:35`. It is a valid supply under THEOREM_SRK §3 ("their
  componentwise minimum, or any other valid supply", `THEOREM_SRK.md:90-91`). The same S feeds both
  `tail_enclosure` and `srk_enclosure` (`P309_PROTOCOL.md:76-78`).
* **One consistency issue (N1).** The protocol's rule "Γ_{i,b} := min over ACCEPTED rungs" (`P309_PROTOCOL.md:57`)
  needs one certificate **per rung** to reach the verifier and the gate. The only qualified serializer,
  `srk_certify.certificate_json`, emits the **best producer rung only** (`impl/srk_certify.py:324-331`). It is used
  by the decoy suite (`impl/srk_decoy_suite.py:40`), and every evidence file carries one certificate per index (checked
  on `evidence/srk_decoys_cell/`). With best-rung serialization, a REJECT of the best rung gives None even if another
  rung would be ACCEPTED, which is a different rule. R2 asked for this choice to be "decided in advance"
  (`reviews/REVIEW_SRK_R2.md:96`). The package does not state it explicitly, and its FC3 omits it
  (`P309_FORMAL_PACKAGE.md:186-187`). The gate already supports several rungs per (i, b): `genuine_max_of_min` passes.

### Item 4. R2's FC1–FC6, including the FC2 extension: PASS (with NOTEs N4, N7, N8, N13)

| FC | package | finding |
|---|---|---|
| FC1 | `P309_FORMAL_PACKAGE.md:161-168`; manifest | Producer lock and fingerprint, c1b_gauss, gate, adapter and assemble at the post-C1 state (blobs equal `b5ad2372`), verifier `a32d5d39…`, harness v2 `3455c141…`, self-tests `8357be85…`, spec, theorem, declarations, rule S, verifier settings N = 8 / depth 24 / width 1/4 (equal to `VERIFY_RESULTS.json` settings) and Python version: all present. Gaps in N13 |
| FC2 (a) grant-scoped guard | `P309_PROTOCOL.md:120-121`; `P309_FORMAL_PACKAGE.md:172-173`, `:83` | present (marker = grant = HEAD, pins verify, inside Ew only) |
| FC2 (b) verifier variant with its own re-qualification | `P309_PROTOCOL.md:122-125`; `P309_FORMAL_PACKAGE.md:174-177`; QC16 `:45` | present. The timing text conflicts, and the admit path is unqualified (N4). The self-tests are named in the protocol but not in J or QC16 (N8) |
| FC2 genuine-only, no mutant battery on in-band certificates | `P309_PROTOCOL.md:54-56`; `P309_FORMAL_PACKAGE.md:180-182`; grant `in_band_verification` `:94` | present; stricter than R2 (no probes at all). Not restated in the execution-review outline (N5) |
| FC2 probe construction guarded independently of any lifted band list | `P309_PROTOCOL.md:126`; `P309_FORMAL_PACKAGE.md:180-182`; QC16 | present |
| FC2 grant names Ew | `P309_PROTOCOL.md:127`; `P309_FORMAL_PACKAGE.md:178`; grant `drift_hull_Ew` `:94` | present |
| FC3 | `P309_FORMAL_PACKAGE.md:186-187`; `P309_PROTOCOL.md:59-60` | present (None → TC-T, no retry). The optional "emit every certified rung" is not decided explicitly (N1). Exceptions and caps are not mapped (N2) |
| FC4 | `P309_FORMAL_PACKAGE.md:188-193` | In-process verdicts, `verifier_id` from the pinned bytes, exact cells from `cells.json`, and a static check (`_TOKEN`, `object.__setattr__`, `GateResult(`). R2's Phase-C/D addition, forbidding rebinding of `srk_adapter._REAL_GEOMETRY_ITEMS` / `REAL_GEOMETRY` (`REVIEW_SRK_R2.md:826-827`, `:976`), is covered only by "any geometry or kernel override" (N7) |
| FC5 | `P309_FORMAL_PACKAGE.md:194-195`; `P309_PROTOCOL.md:66-70` | present |
| FC6 | `P309_FORMAL_PACKAGE.md:196` (§§C–I) | present |

Labelling: the protocol letters FC2 as (a) guard, (b) verifier, (c) probe guard, (d) Ew (`P309_PROTOCOL.md:120-127`).
The formal package letters it (a) guard, (b) verifier, (c) Ew, (d) genuine-only plus probe guard
(`P309_FORMAL_PACKAGE.md:172-182`). This is cosmetic but confusing for a freeze text (N8).

### Item 5. Exactly-once and failure semantics: PASS for exactly-once; NOTE for failure mapping and fallback honesty (N2, N9, N10, N12)

* **No double evaluation.**
  * The marker is armed by CAS from the zero OID to the grant (`P309_FORMAL_PACKAGE.md:75`).
  * A consumed marker is never rerun (`:146`). Lost information means no recomputation without new governance
    (`:147`).
  * `seal-only` never computes (`:58`). A second `execute` is refused (`:111-112`).
  * An existing 307/308/309 marker namespace is refused (`:22`).
  * The grant-scoped guard admits band drifts only when marker = grant = HEAD (`:83`; `P309_PROTOCOL.md:120-121`), so
    no in-band Stage-1a computation is possible before consumption.
* **Historical control.** It runs at step 4, before the marker at step 5 (`P309_FORMAL_PACKAGE.md:74-75`). On mismatch
  the result is CONTROL_FAILED, not consumed, STOP (`P309_PROTOCOL.md:91-93`). No other mode computes the target:
  modes at `P309_FORMAL_PACKAGE.md:52-58`; QC12 static check `:42`. The control's digest is sealed (`:103`), but no
  post-exec or execution-review check names it (N10).
* **Parameters fixed before any 309 number.** Every Stage-1a/1b parameter is pinned in §A or taken verbatim from RLR307.
  Stage-1 numbers first exist after the marker. The one open choice with outcome effect, per-rung versus best-rung
  certificates, is fixable now in text (N1).
* **Stage-1 failure, no retry.**
  * Stage 1a: non-acceptance gives None and TC-T, "not a failure and never triggers a retry" (`P309_PROTOCOL.md:59-60`,
    `:105`; `P309_FORMAL_PACKAGE.md:156`).
  * Stage 1b: CERTIFICATION_FAILED gives NOT_CLOSED with no retry (`P309_PROTOCOL.md:101`;
    `P309_FORMAL_PACKAGE.md:157`).
* **Is the TC-T fallback stated honestly? Only partly (N2).** "Without (a)–(d), SRK falls back to TC-T. That is safe"
  (`P309_PROTOCOL.md:129-130`; "silently", `P309_FORMAL_PACKAGE.md:184`; `P309_OWNER_DECISIONS.md:20`).
  * This holds for **verifier non-acceptance** (a REFUSE or REJECT verdict drops the certificate at the gate).
  * It does not hold, as written, for the **producer side**. An in-band drift refused by the producer guard raises
    `QuarantineRefusal` inside `certify_W`/`run_block` (`impl/srk_certify.py:99-101`, `:202`, `:279`); it does not
    return a non-CERTIFIED status.
  * The same applies to a producer or verifier exception and to exceeding the §A cap "Stage 1a ≤ 6 CPU-h"
    (`P309_FORMAL_PACKAGE.md:23`), whose consequence is not stated.
  * Read literally, all of these are post-marker failures, so the target is consumed with EXECUTION_INDETERMINATE
    (`P309_PROTOCOL.md:102`), not a TC-T fallback. Read through FC3 ("a sub-block without an admitted certificate"),
    they fall back. The two readings give different sealed outcomes.
  * Context for the cap (decoy-only; I make no extrapolation to 309): on the qualified real-kernel A2 decoy cell
    (`evidence/srk_decoys_cell/cell_h5_*`, e ≤ 527/1024), the producer logs sum to about 16 300 CPU-s (W ≈ 360 s,
    V ≈ 15 940 s), about 4.5 CPU-h. So the cap is not far above a qualified decoy's cost.
* **Post-seal re-verification.** The post-exec check re-runs the verifier on the sealed in-band certificates
  (`P309_FORMAL_PACKAGE.md:117-118`). After the seal, HEAD ≠ grant, and the package does not say under what condition
  the grant-scoped verifier admits in-band drifts then (review mode?). A mismatch there has no mapped outcome (N9).

### Item 6. Candidate manifest: PASS (with NOTE N13)

Recomputed in RD3-0 at `ce829bb4` (the manifest's `repository_head`, `P309_CANDIDATE_FREEZE_MANIFEST.json:4`) and at
HEAD `f1f8a459`.
* **19 NS code pins.** For every pin, the git blob at both commits equals the manifest. The sha256 of the committed
  blob and of the working-tree file equal the manifest, and the git-sha1 of the working-tree bytes equals the blob.
* **Producer lock.** The four producer blobs at the lock `2a03e838` equal the manifest. Gate, adapter and assemble
  blobs at `b5ad2372` (the R2 C1 repair) equal the manifest. The verifier blob at `bf5c87c4` equals HEAD. Self-audit A5
  (fingerprint `377057be…`) passes.
* **8 out-of-NS code pins.** The git blob at both commits equals the manifest (tree lookup only). I did **not** verify
  their sha256 (firewall), except c1b_gauss: `3189208d…` equals the `c1b_gauss.py` entry recorded in the producer
  fingerprint of all 19 NS evidence files, and A5 recomputes the combined fingerprint. The other seven sha256 values
  have no independent cross-reference inside NS.
* **6 data pins.** They are metadata-only: each entry has only `path` and `git_blob` (`:159-184`). The generator used
  `git rev-parse` only for them (the dangling tool `5ddf7b58:…/protocol_prep/make_candidate_manifest.py:42-43`). Their
  blobs equal the tree at both commits. r5 is `f978eeb6` (A6 PASS).
* **Missing from the pins (N13):**
  * `config/SRK_DECOY_DECLARATION_A1.json`, which is named by §A's glob `SRK_DECOY_DECLARATION*.json`
    (`P309_FORMAL_PACKAGE.md:21`);
  * `config/TARGET_QUARANTINE_309.json`, which the protocol keeps "in force until the grant"
    (`P309_PROTOCOL.md:110`);
  * the qualification test files behind QC01–QC08b and QC15 (only `test_verify_selftests.py` is pinned), and the
    planted scan control `tests/planted_control_q309.py`;
  * "floor r2", listed in §A's pin row (`P309_FORMAL_PACKAGE.md:21`) but absent from both the pins and `open_items`;
  * `c1b_kernel.py`, which QC01 compares against, unless C1B_R2_CODE_PINS covers it;
  * `registry/PHASE3_ROUTE_COMPARISON.md` (the SRK-T OUT record) and `ERRATA.md` (E-15, E-17(d)), both cited as
    binding.
  * The driver, the grant-scoped guard and the verifier variant do not exist yet. §A should say they are pinned at the
    freeze: the driver appears only in the grant (`:90`), and §A calls `verify/srk_verify_indep.py`'s sha "the
    adapter's `verifier_id`" (`:21`), whereas FC2 makes the **variant's** sha the `verifier_id`
    (`P309_PROTOCOL.md:123`).

### Item 7. Governance: PASS (with NOTEs N11, N15)

* **Nothing is frozen, authorized or executed, and this is stated everywhere:**
  * `protocol_prep/README.md:10-16`;
  * `P309_PROTOCOL.md:1-12`;
  * `P309_FORMAL_PACKAGE.md:3-5`;
  * `P309_OWNER_DECISIONS.md:3-8`, `:28-33`;
  * the manifest `status`.
  The owner requirement for the freeze (P0-1) is explicit (`P309_PROTOCOL.md:4-5`, `:16`). A8 confirms that no marker
  or odd ref exists. R2's statement "this verdict authorizes nothing" is carried over faithfully.
* **`P309_OWNER_DECISIONS.md` against R2's owner list** (`reviews/REVIEW_SRK_R2.md:942-958`):
  * G1, G2, G3, U2, U3, the optional SRK-T row, efficacy, 309R1-03 and the unverifiable pre-commit self-test runs
    (E-17(a)) are all present (`P309_OWNER_DECISIONS.md:14-20`, `:26`). R1 G4 (E-3) is also present.
  * **Missing (N11):** from "the recorded user items" (`REVIEW_SRK_R2.md:958`;
    `READER_B_GOVERNANCE_REPORT.md:46-52`), **push/merge** is absent. The **separate grant after
    QUALIFICATION_ACCEPTED** is folded into P0-1 ("This includes authorizing … a grant", `P309_OWNER_DECISIONS.md:14`)
    instead of being its own later decision. The **cell set** is implicit only.
  * **Also (N11):** the protocol's P0-2 (`P309_PROTOCOL.md:17`) and the grant's `disclosed_liabilities`
    (`P309_FORMAL_PACKAGE.md:91-92`) omit 309R1-03, E-3 and E-17(a), which the owner file lists. The two texts should
    agree.
* **Ew adjacency (N15).** R2 notes that Ew "extends up to 2⁻¹⁰ beyond C, possibly into an adjacent quarantined cell's
  drift range" (`REVIEW_SRK_R2.md:90-91`). The owner row P0-1/G2 mentions Ew but not this. Neither the protocol nor the
  grant forbids re-attributing sealed 309 Stage-1a material to a neighbour (incident 02,
  `READER_B_GOVERNANCE_REPORT.md:115-116`).

### Item 8. Claim discipline: NOTE (N2, N16, N18)

* **No overstatement of efficacy.** "Efficacy at 309 is unknown by design" (`P309_OWNER_DECISIONS.md:20`;
  `PHASE3_ROUTE_COMPARISON.md:148-149`). Readiness is consistently kept apart from authorization.
* **Overstated or imprecise:**
  * "The rehearsal on decoys shows byte-identical reruns" (`P309_PROTOCOL.md:63-64`). No Stage-1a cell rehearsal
    exists yet. The research evidence is T10, one synthetic certificate produced twice, and R2 noted its round trip
    covers V only (`REVIEW_SRK_R2.md:503`). This should read "QC10 must show" (N16).
  * "1868/1868 at qualification" (QC06, `P309_FORMAL_PACKAGE.md:34`) is a research-campaign figure that R2
    reproduced. It is not a formal qualification (N16).
  * QC06 says "real kernel e ≤ 33/32" (`:34`), but the v2 battery's widened and shifted probes evaluate the real
    kernel on [−1/3, 37/32] (ERRATA E-17(a); RD3-2). QC06 and QC16 should state the probe envelope, not only the
    certificate envelope (N16).
  * The fallback is described as "safe"/"silently" (item 5; N2).
* **"Independent" and authorship.** FC2(b) requires the variant to be "written by the verifier's author and not by the
  producer side" (`P309_PROTOCOL.md:122`; `P309_FORMAL_PACKAGE.md:174`). Git cannot prove this, since every commit is
  authored "Claude" (`REVIEW_SRK_R2.md:777-778`). The package should say what evidence of authorship the qualification
  review will accept (N18).

---

## 2. Notes and gaps

No gaps. All notes are text-level and change no rule of the package as written.

### Settle in the text before any freeze (after a freeze, each would be a rule change)

* **N1. Stage-1a serialization (items 3, 4, 5).**
  * State that every producer-CERTIFIED rung of every (b, i) is serialized as its own certificate. Each is verified
    in-process and submitted to the gate, so that "Γ_{i,b} := min over ACCEPTED rungs" is what is computed.
    `srk_certify.certificate_json` emits the best rung only and must not be the Stage-1a serializer.
  * Name the serializer in the pin set, and have QC08 and QC10 exercise it.
  * Seal **all** certificates, all verdicts and the GateResult report, not "the ACCEPTED ones" only
    (`P309_FORMAL_PACKAGE.md:99`), so that the execution review can check each non-admission.
* **N2. Stage-1a failure mapping and the cap (items 5, 8).**
  * State which of these gives "no admitted certificate" (TC-T fallback) and which gives a post-marker failure
    (EXECUTION_INDETERMINATE):
    * producer exceptions (including guard refusals);
    * verifier exceptions;
    * `W_REPAIR_INAPPLICABLE` / `W_NEGATIVE` statuses;
    * reaching the 6 CPU-h cap (and whether that cap is total or per job).
  * The minimal text fix consistent with the table as written: non-CERTIFIED statuses and non-ACCEPT verdicts fall
    back; any exception or cap overrun is EXECUTION_INDETERMINATE.
  * Correct the "safe/silent fallback" sentences (`P309_PROTOCOL.md:129-130`, `P309_FORMAL_PACKAGE.md:184`,
    `P309_OWNER_DECISIONS.md:20`) to match, so the owner knows a Stage-1a resource failure consumes the target without
    a conclusion.
  * If the owner prefers mapping these failures to fallback, that is a rule decision, to be taken before the freeze.
* **N3. "Independent checks equal" (item 2).** Name the in-run independent checks referred to in outcome row 1
  (`P309_PROTOCOL.md:99`): for example, the in-process verifier verdicts for Stage 1a and the RLR307 independent
  reconstruction for Stage 1b. State that inequality is a post-marker failure and gives EXECUTION_INDETERMINATE, as
  the catch-all row already implies.
* **N4. FC2 ordering and the admit path (item 4).**
  * The variant must be re-qualified "before the freeze" (`P309_PROTOCOL.md:123`; `P309_FORMAL_PACKAGE.md:176-177`).
    But QC16 is part of qualification, which follows the freeze (§C step 1, QC13), and R2 says "before the seal"
    (`REVIEW_SRK_R2.md:88`, `:969`). Fix one order: written and hashed before the freeze, pinned by it, and re-qualified
    in QC16 before the grant.
  * QC16 qualifies only the refusal paths: no grant, and outside Ew. Add a sandbox positive-path test of the grant
    logic, using a synthetic geometry or a substituted test band and hull and never the real band. That way, "admits
    inside Ew with a valid grant" is not first exercised in the single execution.

### Other text-level notes

* **N5. Review briefs are outlines** (`P309_FORMAL_PACKAGE.md:120-136`).
  * Before issue, each needs allowed reading and running, a firewall, and verdict tokens (for example
    INCIDENT_AUDIT_ACCEPTED or QUALIFICATION_ACCEPTED).
  * The qualification review's "17-item checklist of the 307 pattern" should be reproduced, not cited.
  * Carry R1 G6's exclusion (`reviews/REVIEW_SRK_R1.md:344-345`).
  * Restate the genuine-only / no-mutant-battery rule in the execution-review brief. Its reviewer re-runs the verifier
    on in-band certificates.
* **N6. Gates.** The text says "Gates Q1–Q13 follow the 307 pattern" (`P309_FORMAL_PACKAGE.md:48`), but R2 and the
  governance report say Q1–Q12 (`READER_B_GOVERNANCE_REPORT.md:71`). Enumerate the gates, and list QC13–QC16 in order.
* **N7. FC4 static check.** Name the forbidden rebinding of `srk_adapter._REAL_GEOMETRY_ITEMS` and `REAL_GEOMETRY`
  explicitly (R2 update). Require the pinned N and max_depth in the `verdicts_from_verifier` call, since
  `verifier_identity` hashes the file only (`impl/srk_gate.py:95-107`). Attach the check to QC12.
* **N8. FC2 wording.**
  * Use one lettering in both documents.
  * Add the 21 self-tests to FC2(b) in J and to QC16, as the protocol already does (`P309_PROTOCOL.md:124`).
  * Say that the probe-construction guard also must not rely on the grant-scoped guard, which lifts the band inside Ew.
* **N9. Post-seal verification.** State the admission condition of the grant-scoped verifier after the seal, when
  HEAD ≠ grant (for example, "review mode: marker names the grant and the sealed result exists"). Map a disagreement in
  the post-exec re-verification to an outcome.
* **N10. Historical control in the checks.** Add "historical-control digest present and equal to C2's committed
  record" to §F and to the execution-review checks.
* **N11. Owner list and liabilities.**
  * Add push/merge and the separate grant after QUALIFICATION_ACCEPTED as their own rows in
    `P309_OWNER_DECISIONS.md`, and state the cell set.
  * Align P0-2 (`P309_PROTOCOL.md:17`) and the grant's `disclosed_liabilities` (`P309_FORMAL_PACKAGE.md:91-92`) with
    the owner file: add 309R1-03, E-3 and E-17(a).
  * Add the MEDIUM RLR rating from P0-2 to the owner file's G3 row.
* **N12. Stage-1b.**
  * Say whether Stage 2 runs after a Stage-1b CERTIFICATION_FAILED (row 3 reads "TARGET_EVALUATED").
  * Owner awareness: a Stage-1a failure falls back to TC-T, but a Stage-1b failure forfeits the evaluation (NOT_CLOSED)
    even though RLR is also a min component, where S_I1 would remain valid. This is a legitimate frozen choice (RLR307
    verbatim), but it should be visible to the owner under G3.
* **N13. Pins.** Add the items listed under item 6.
  * Use one notation in §A: "tc_rule.py (pin 8d402d11)" is a sha256 prefix, while the neighbouring pins are blob
    prefixes.
  * The generator (`make_candidate_manifest.py`) survives only in the unreachable local commit `5ddf7b58`, which was
    rewritten away before push and is subject to gc. If the manifest's generation is to be auditable, preserve it as
    inert text with its hash.
  * `python_used_for_qualification` was taken from the generator's own interpreter. No research evidence file records
    the Python version.
  * The generator hashed the bytes of two other campaigns' JSON files (`RLR307_FREEZE.json`, `C1B_R2_CODE_PINS.json`).
    That is not an exposure, but I found no ZERO_TARGET_LEDGER line for the run; the EXPOSURE_LEDGER was not opened.
    The incident-independence review should see it.
* **N14. QC coverage.**
  * Add an explicit S-construction QC. The 307 anatomy had one (`READER_B_GOVERNANCE_REPORT.md:68`); QC09 cites the
    RLR307 QC numbers only.
  * State whether QC10 determinism is required on the execution host (P0-4 names the host). Only the Python version is
    pinned, not the platform or libm, while float proposals feed the certificate bytes.
* **N15. Ew adjacency and non-re-attribution.** In the P0-1/G2 owner row and in the grant, state that Ew may overlap a
  neighbouring quarantined cell's drift range. Also state that sealed 309 Stage-1a certificates are bound to cell 309
  (as the gate and adapter already enforce) and must never be re-attributed to another cell (incident 02).
* **N16. Wording.** Make the three corrections of item 8: the rehearsal "shows", "1868/1868 at qualification", and the
  QC06 real-kernel envelope, which should state the 37/32 and −1/3 probe envelope.
* **N17. U3.** Say explicitly that the outcome table and grant schema are written for CLOSURE_ONLY. A U3 floor
  extension would require revising them before the freeze (P0-3).
* **N18. Authorship evidence.** Say how the FC2(b) authorship requirement will be evidenced, since git cannot show
  it. Keep "independent" for the verifier as a procedural claim for the qualification review to assess.
* **N19. Minor text.**
  * The protocol's Stage-2 formula uses undefined symbols (M_R2, H) (`P309_PROTOCOL.md:87`). Replace it with "exactly
    as the pinned `direct`/`combine` compute it with 𝓗_SRK substituted" or define the symbols.
  * Stage 1a could cite `srk_certify.cell_blocks` / `run_cell` (THEOREM_SRK §11) rather than the lower-level calls
    (`P309_PROTOCOL.md:41-43`).

---

## 3. Disclosures

* **Exposures.** I saw no numeric value of any cell 305–309 quantity. The only 305–309-related material I met was:
  * the path names and git blob ids of the 309 input files, in the manifest and the dangling generator source
    (metadata only);
  * the symbol "Λ_309" in a formula line of `theory/PHASE1_RESULTS.md` (a symbol, no value);
  * generic band literals in R2's text (7q refusal-probe blocks), which carry no cell quantity.
  Decoy runtimes and decoy blocks (e ≤ 33/32) were read from NS evidence.
* **Executions.** RD3-0 to RD3-3, as declared in §0 before running. No run touched a cell 305–309 or evaluated any
  drift in the band or its mirror. The only real-kernel evaluations were envelope primitives at e ∈ [0, 1/2] (RD3-3).
* **Writes.** Nothing was written in the repository except this file. No git write. No process was started or stopped
  other than my own.
