# Independent package review R3 of the P309 formal-campaign package (candidate)
PACKAGE_REVIEW: COMPLETE

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

---

## Follow-up (2026-09-30): check of package rev. 2 against N1–N19

### F0. Follow-up execution declaration (written before any run beyond read-only checks)

Reviewed state: HEAD `a2678cc7`. It contains package rev. 2 (`814ff984`, which also preserves the text above verbatim)
and manifest rev. 2 (`2db92936`). The same brief, firewall and hard rules apply. The text above is not rewritten; only
line 2 is updated at the end.

| id | what | kernel / geometry / drift | evaluates? |
|---|---|---|---|
| FU-0 | Read-only checks: `git diff` of rev. 2; reading `protocol_prep/*` rev. 2 and the new ledger lines in `ZERO_TARGET_LEDGER.jsonl` / `CHECKPOINT_PUSHES.jsonl`; manifest rev. 2 pins recomputed as in RD3-0 (outside NS: blob by tree lookup only); sha256 of `make_candidate_manifest.py.txt` against `MANIFEST_GENERATOR_SHA256.txt` and the dangling `5ddf7b58` tool; comparison of `evidence/reviewer_r3/*` with my scratch files | none | no |
| FU-1 | `code/self_audit.py` `run()` through my RD3-1 wrapper (A10 through the RD3-2 wrapper), output to `scratchpad/r3/`, to confirm A1–A10 at HEAD | none | no |

The generator is not run: it names target-input paths and reads bytes outside NS. No test is re-run, because no
`impl/`, `code/`, `verify/` or `tests/` file changed since my runs (checked in FU-0). Nothing touches cells 305–309 or
evaluates any drift in the band or its mirror.

**Executed as declared.**
* **FU-0 (read-only checks).**
  * Since `1d8efbbb`, no `impl/`, `code/`, `verify/`, `tests/`, `config/`, `theory/` or `registry/` file changed
    (`git diff --stat` is empty), so my RD3 test results stand.
  * Manifest rev. 2 (`repository_head` `814ff984`): 45 code pins (37 NS, 8 outside) and 7 data pins. **Every blob
    matches** at `814ff984` and at HEAD. The sha256 of all 37 NS pins matches the committed bytes and the working tree.
    Pins outside NS were checked by blob only. The data pins carry only `path` and `git_blob`. Every rev.-1 pin is
    kept with identical blob and sha256. `protocol_prep/` did not change between `814ff984` and HEAD except the
    manifest and generator files.
  * `make_candidate_manifest.py.txt` hashes to `cb6694cc…`, which equals `MANIFEST_GENERATOR_SHA256.txt`. Against the
    dangling `5ddf7b58` tool it differs only by the added pin paths, the floor-r2 data path (still `rev-parse` only),
    the relabelled Python field and one open item.
  * The six files in `evidence/reviewer_r3/` are byte-identical to my scratch files. Ledger line 535, the transcription
    of my runs, is accurate.
* **FU-1 (self-audit at HEAD `a2678cc7`).** A1–A10 all PASS, with 536 ledger lines and max drift 37/32. The A10 envelope
  output is again byte-identical to the committed file. A11: local = remote = `a2678cc7`; the only dirt is this file.
  Outputs are in `scratchpad/r3/fu/`.
* Nothing in NS was written except this file. No git write.

### F1. Per-note status (rev. 2)

| note | status | evidence |
|---|---|---|
| N1 per-rung serialization; record everything | **SETTLED** | `P309_PROTOCOL.md:50-53` (one certificate per CERTIFIED (b, i, rung) via `certificate_json` on a single-rung block record, which works because `certificate_json` picks the best of the rungs it is given, `impl/srk_certify.py:324-331`), `:63` (min over admitted rungs), `:81-82` (all certificates, verdicts and the GateResult report sealed); `P309_FORMAL_PACKAGE.md:19`, `:38` (QC08), `:40` (QC10), `:110-111` (§E); brief checklist item 7 (`P309_REVIEW_BRIEFS.md:61-62`) |
| N2 Stage-1a failure mapping, budget and fallback wording | **SETTLED** (new notes F2.1–F2.2 on budget mechanics) | `P309_PROTOCOL.md:69-80` (mapping table), `:114` (adapter refusal is an exception), `:136`, `:183-185` (honest (a)–(d) consequence); `P309_FORMAL_PACKAGE.md:21`, `:25`, `:41` (QC11), `:164-166`; `P309_OWNER_DECISIONS.md:23` (owner row with the alternative), `:25` (efficacy wording consistent) |
| N3 in-run independent checks | **SETTLED** | `P309_PROTOCOL.md:126-130`, `:134`, `:136`, `:96-97` |
| N4 FC2 order and positive path | **SETTLED** (new note F2.4 on review mode) | `P309_PROTOCOL.md:162-171`; `P309_FORMAL_PACKAGE.md:46` (QC16), `:23` (freeze additions); `P309_REVIEW_BRIEFS.md:56-58` |
| N5 full review briefs | **SETTLED** | `P309_REVIEW_BRIEFS.md`: common firewall with R1 G6 (`:7-22`); verdict tokens (`:41`, `:74`, `:97`, `:110`); a self-contained 17-item checklist (`:50-73`); genuine-only restated for the execution reviewer (`:80-83`). The 307 checklist is not reproduced because it is firewalled, and the self-contained list is a reasonable substitute |
| N6 gates | **SETTLED** (README stale, F2.7) | `P309_FORMAL_PACKAGE.md:49-50` (Q01–Q17, one per QC, none waivable); QC order fixed (`:43-47`) |
| N7 FC4 static items | **SETTLED** | `P309_FORMAL_PACKAGE.md:42` (QC12: `_REAL_GEOMETRY_ITEMS` / `REAL_GEOMETRY` rebinding; pinned N / max_depth), `:189-190`; `P309_PROTOCOL.md:57-59` |
| N8 FC2 lettering, self-tests, probe guard | **SETTLED** | `P309_PROTOCOL.md:157-181` and `P309_FORMAL_PACKAGE.md:183-187` use the same (a)–(d); the 21 self-tests are in QC16 (`:46`) and §7(b) (`:167`); the probe guard is independent of every lifted list (`P309_PROTOCOL.md:178-180`) |
| N9 post-seal verification | **SETTLED** (qualification of review mode: F2.4) | `P309_FORMAL_PACKAGE.md:131-138` (review-mode admission: marker names the grant and the sealed result lists the sha256; genuine only; disagreement → INDETERMINATE); `P309_PROTOCOL.md:137` |
| N10 historical-control digest | **SETTLED** | `P309_PROTOCOL.md:119-122`, `:137`; `P309_FORMAL_PACKAGE.md:76`, `:115`, `:130`; `P309_REVIEW_BRIEFS.md:94` |
| N11 owner list and liabilities | **SETTLED** | `P309_OWNER_DECISIONS.md:18` (cell set), `:20` (G3 MEDIUM), `:24` (309R1-03, E-3, E-17(a), generator run), `:31` (separate grant), `:32` (push/merge); `P309_PROTOCOL.md:19` (P0-2); `P309_FORMAL_PACKAGE.md:95-96` (grant liabilities) |
| N12 Stage-1b | **SETTLED as a rule choice, flagged** (F3; F2.3 on the Stage-1b budget) | `P309_PROTOCOL.md:93-97`; `P309_FORMAL_PACKAGE.md:22`, `:167-169`, `:191-192`, QC17 `:47`; owner flag `P309_OWNER_DECISIONS.md:20` with the alternative "require the RLR307 NOT_CLOSED rule" |
| N13 pins and generator | **PARTLY SETTLED** | Added: A1 declaration, `TARGET_QUARANTINE_309.json`, 12 test files, the four package documents, floor r2 (data, blob only). The generator is preserved as inert text with a matching sha256. The Python field is relabelled (manifest `:16`). Generator runs are ledgered (`ledger/ZERO_TARGET_LEDGER.jsonl:536`). §A uses no prefixes (`P309_FORMAL_PACKAGE.md:23`). **Still unpinned:** `tests/planted_control_q309.py` (the scan's planted control, required by `q309_guard.scan` for QC15/A4), `registry/PHASE3_ROUTE_COMPARISON.md` (the SRK-T OUT record cited at `P309_PROTOCOL.md:83` via rule S) and `ERRATA.md` (E-15 / E-17(d), cited as binding). `c1b_kernel.py` (QC01) is pinned only if C1B_R2_CODE_PINS covers it, which I cannot check. See F2.6 on the ledger line |
| N14 QC coverage | **SETTLED** | `P309_FORMAL_PACKAGE.md:47` (QC17 S construction incl. the None → S_I1 fallback), `:40` (QC10 on the execution host; interpreter/platform pinned, also `:23`, `:74`); `P309_PROTOCOL.md:21`, `:84-86` |
| N15 Ew adjacency and non-re-attribution | **SETTLED** | `P309_PROTOCOL.md:36-39`, `:181`; `P309_FORMAL_PACKAGE.md:101-105`; `P309_OWNER_DECISIONS.md:17` |
| N16 wording | **SETTLED** | `P309_PROTOCOL.md:84-86` (T10 described as what it is; QC10 must show), `:147-148` (probe envelope 37/32 and −1/3); `P309_FORMAL_PACKAGE.md:36` ("The research qualification gave 1868/1868"; probe envelope; ledgered) |
| N17 U3 | **SETTLED** | `P309_PROTOCOL.md:20`, `:124`; `P309_FORMAL_PACKAGE.md:15`; `P309_OWNER_DECISIONS.md:22`; brief checklist item 17 (`P309_REVIEW_BRIEFS.md:73`) |
| N18 authorship evidence | **SETTLED** | `P309_PROTOCOL.md:160-161`, `:172-177`; brief checklist item 5 (`P309_REVIEW_BRIEFS.md:56-58`) |
| N19 Stage-2 wording, cell_blocks / run_block | **SETTLED** | `P309_PROTOCOL.md:115-116`, `:43-49` |

### F2. New or remaining issues introduced by rev. 2 (all text-level; no gap)

* **F2.1 Budget versus determinism.** §2.8 says every Stage-1a output is "a pure function of the pinned bytes and the
  pinned interpreter/platform" (`P309_PROTOCOL.md:84`). But the budget-exhaustion fallback (`:75`) makes the set of
  certificates depend on timing whenever the budget binds. Since Γ̄ is a min over admitted rungs, the outcome could
  then depend on host speed. Add the caveat: determinism holds only when the budget does not bind. The sealed record
  already stores the budget used and the timings (`P309_FORMAL_PACKAGE.md:116-117`).
* **F2.2 Budget mechanics are undefined.** State the following in the text, or in the driver pinned at the freeze and
  exercised by QC11:
  * what "CPU-h" measures (the summed CPU time of the worker processes, or wall time × workers);
  * whether in-process verification counts toward the budget;
  * the job granularity and the fixed job order. With `run_block` as the job, `run_block` returns only when all its
    rungs are done, so one unfinished sub-block drops every rung of that sub-block. Since Γ̄_i needs every sub-block,
    that means all four indices fall back;
  * that stopping at the budget is done by not starting jobs and discarding unfinished ones, not by an exception.
    Otherwise it would read as a §2.5 exception, giving EXECUTION_INDETERMINATE.
* **F2.3 Stage-1b budget.** The 21 600 s Stage-1b budget has no mapping in protocol §3. Only the §A row
  (`P309_FORMAL_PACKAGE.md:25`), whose "(protocol §2.5)" reference is Stage-1a-only, implies fallback. Say in §3 that
  Stage-1b budget exhaustion is treated like CERTIFICATION_FAILED (fallback to S_I1), or state otherwise.
* **F2.4 Review mode is not qualified.** The verifier's review mode has its own admission logic (the marker names the
  grant, and the sealed result lists the sha256) (`P309_FORMAL_PACKAGE.md:131-134`). QC16 qualifies only the official
  grant-scoped mode (`:46`). A review-mode bug that refuses a genuine certificate would, by the post-seal row
  (`P309_PROTOCOL.md:137`), turn a sealed closure into EXECUTION_INDETERMINATE. Add review-mode refusal and admission
  tests to QC16, in the sandbox, with a test band and hull only.
* **F2.5 Band wording.** "The band is forbidden except under QC16's test substitution" (`P309_FORMAL_PACKAGE.md:27`)
  and "except the QC16 test substitution" (`P309_REVIEW_BRIEFS.md:72`) read as if QC16 may touch the real band. QC16
  never uses the real band (`P309_PROTOCOL.md:169-170`). Reword: "the real band is forbidden without exception; QC16
  substitutes a test band".
* **F2.6 Ledger timing.** The GOVERNANCE line `ledger/ZERO_TARGET_LEDGER.jsonl:536`, stamped 00:34:10Z and committed
  at 00:34:11Z, lists generator runs at "~00:0xZ, ~00:3xZ, **~01:0xZ**". The last of these was still in the future when
  the line was written (I checked the clock at 00:37Z). Append a correction line, since the ledger is append-only.
* **F2.7 README.** `protocol_prep/README.md:8` still says "QC01–QC16" (now QC01–QC17). `:3` says rev. 2 "settles every
  note", but N13 is partial (F1). `:21` says the generator "reads git metadata only" while it hashes committed bytes of
  code files (the next clause says so).
* **F2.8 Incident-independence scope.** Rev. 2 adds three rule choices, all made by the exposed coordinator after
  review R3 and before any 309 Stage-1 number: the §2.5 mapping, the 48 CPU-h budget and the Stage-1b fallback.
  P0-2 records that RLR's "knockout is known" (`P309_PROTOCOL.md:19`). List these three choices explicitly in the
  incident-independence brief's task 1 (`P309_REVIEW_BRIEFS.md:34-37`), so their target independence is assessed. The
  generic "design, parameters" wording covers them only implicitly.

### F3. Are the rule choices coherent and correctly flagged?

* **N2 mapping: coherent.**
  * It separates anticipated, declared non-success from malfunction:
    * non-CERTIFIED statuses, non-ACCEPT verdicts and budget exhaustion fall back (safe for validity, by the min
      construction);
    * any exception is EXECUTION_INDETERMINATE (the target is consumed, with no conclusion and no retry).
  * Neither branch allows a retry or a parameter change, and the table stays exhaustive through the catch-all row.
  * The alternative (exceptions → fallback) is offered to the owner as a pre-freeze decision
    (`P309_PROTOCOL.md:79-80`; `P309_OWNER_DECISIONS.md:23`), and the efficacy risk of each branch is stated.
  * The QC16 positive path and QC11 reduce the risk that a guard or verifier defect is first met in the single
    execution.
* **The 48 CPU-h budget: coherent.**
  * Its basis is target-free: about 10× the qualified decoy cell. That cell costs about 4.5 CPU-h (decoy only; I make
    no extrapolation to 309).
  * It is fixed before any 309 number, and it is disclosed to the owner inside the mapping row.
  * Only its mechanics (F2.1, F2.2) need writing down.
* **N12 Stage-1b fallback: coherent, and correctly flagged under G3.**
  * RLR enters only through min(A1_I1, A1_RLR) and min(A2_I1, A2_RLR). None → S_I1 is a valid supply (THEOREM_SRK §3;
    rule S C2), and it mirrors the SRK fallback.
  * The RLR307 certifier rules stay verbatim; only the outcome mapping differs, and the text says so.
  * QC17 covers the None → S_I1 construction.
  * Exceptions and reconstruction mismatches remain EXECUTION_INDETERMINATE.
  * The owner row states the asymmetry with RLR307 and offers the RLR307 NOT_CLOSED rule as the alternative
    (`P309_OWNER_DECISIONS.md:20`).
  * The change favours closure in the failure case. It was chosen before any 309 Stage-1 number existed. Its
    target independence belongs to the incident-independence review (F2.8).

### F4. Follow-up verdict

**COMPLETE_WITH_NOTES** (line 2 unchanged in value, reconfirmed for rev. 2 at `a2678cc7`).
* 18 of 19 notes are SETTLED. N13 is PARTLY SETTLED: three NS files are still unpinned, and `c1b_kernel.py` coverage
  is unverifiable by me.
* Rev. 2 introduces no gap and no rule inconsistency that needs new science. F2.1–F2.8 are text-level fixes. F2.1–F2.4
  should be written before a freeze, because the frozen driver will otherwise fix the budget and review-mode behaviour
  without reviewed text.
* Nothing here authorizes a freeze: it still requires the owner (P0-1).

**Follow-up disclosures.**
* I saw no 305–309 value. I met only file paths and blob ids of the 309 input files and of the floor-r2 specification
  (metadata), and the class-level description of THEOREM_TCT lines 12 and 39 in the briefs (no values).
* The only runs were FU-0 (read-only) and FU-1 (self-audit, no evaluation).
* Nothing in the repository was written except this file. No git write.

---

## Follow-up 2 (2026-09-30): check of rev. 2b against the N13 residue and F2.1–F2.8

### G0. Declaration (written 00:42Z, before any run beyond read-only checks)

Reviewed state: HEAD `c391bc47`. It contains rev. 2b content (`36e672be`) and manifest rev. 2b (`d8016525`). My
follow-up is preserved at `429305b6`. The same brief, firewall and rules apply. Earlier text is not rewritten; only
line 2 is updated at the end.

| id | what | kernel / geometry / drift | evaluates? |
|---|---|---|---|
| FU2-0 | Read-only checks: `git diff a2678cc7..HEAD`; reading the changed `protocol_prep/*` text and the new ledger lines; manifest rev. 2b pins recomputed as before (outside NS: blob by tree lookup only); generator copy against its recorded sha256 | none | no |
| FU2-1 | `code/self_audit.py` through my RD3-1 wrapper, output to `scratchpad/r3/fu2/` | none | no |

I do not open `C1B_R2_CODE_PINS.json` (it is outside NS). The claim about its file names stays a coordinator claim.

**Executed as declared.**
* **FU2-0 (read-only checks).**
  * Since `a2678cc7`, no `impl/`, `code/`, `verify/`, `tests/`, `config/` or `theory/` file changed. `git status` was
    clean apart from this file.
  * Manifest rev. 2b (`repository_head` `36e672be`): 48 code pins and 7 data pins. **Every blob matches** at
    `36e672be` and at HEAD, and the sha256 of every NS pin matches the committed bytes and the working tree.
    * The three new pins are exactly `tests/planted_control_q309.py`, `registry/PHASE3_ROUTE_COMPARISON.md` and
      `ERRATA.md`.
    * Only the three edited package documents changed blob.
    * No pin was dropped, and the data pins still carry only `path` and `git_blob`.
  * The generator copy matches `MANIFEST_GENERATOR_SHA256.txt`.
* **FU2-1 (self-audit at HEAD `c391bc47`).** A1–A10 all PASS, with 538 ledger lines and max drift 37/32. The A10
  envelope output is byte-identical to the committed file. Outputs are in `scratchpad/r3/fu2/`.
* I did not open `C1B_R2_CODE_PINS.json`. Nothing was written except this file, and there was no git write.

### G1. Status of the N13 residue and F2.1–F2.8

| item | status | evidence |
|---|---|---|
| N13 residue | **SETTLED** | New pins verified (FU2-0). `P309_FORMAL_PACKAGE.md:181-185`: the planted control, ERRATA and PHASE3 are listed in FC1. The claim that c1b_kernel is covered through the pinned `C1B_R2_CODE_PINS.json` is stated honestly as a "file names only" check by the coordinator. I cannot verify it under the firewall, so the formal freeze should verify those pins' content |
| F2.1 host dependence | **SETTLED** | `P309_PROTOCOL.md:93-95` (the caveat, the recorded job list, validity unaffected), `:99-100` (§2.8 now conditional on the budget not binding) |
| F2.2 budget mechanics | **SETTLED** (polish P1, P2 below) | `P309_PROTOCOL.md:82-95`: CPU accounting as user+sys over workers, verification included; job = (b_j, rung); rung-major fixed order; start threshold 48 CPU-h; per-job limit 12 CPU-h (terminate and discard); stopping never raises. Also `P309_FORMAL_PACKAGE.md:25`, QC11 `:41` (the mechanics are exercised in the sandbox). The design is coherent: rung-major order gives every sub-block its cheapest rung first, and discarding only ever removes certificates, so validity is unaffected |
| F2.3 Stage-1b budget | **SETTLED** | `P309_PROTOCOL.md:112-114` (21 600 s CPU; not certified within budget → CERTIFICATION_FAILED → S_I1; the stop never raises) |
| F2.4 review mode qualified | **SETTLED** | `P309_FORMAL_PACKAGE.md:46` (QC16: review mode in a sandbox with a test marker, test grant and test sealed result; admits only then, refuses otherwise) |
| F2.5 band wording | **PARTLY SETTLED** (polish P3) | Fixed in `P309_FORMAL_PACKAGE.md:27`. Unchanged in the qualification checklist, `P309_REVIEW_BRIEFS.md:78` ("touches the target or the band, except the QC16 test substitution") |
| F2.6 ledger timing | **SETTLED** (disclosure D1; polish P4) | `ledger/ZERO_TARGET_LEDGER.jsonl:537` is an append-only PROCESS_NOTE correction, and `:538` records the rev.-2b generator run |
| F2.7 README | **SETTLED** | `protocol_prep/README.md:3-4` (no "settles every note" claim), `:9` (QC01–QC17, Q01–Q17), `:22-24` (data metadata only; code bytes hashed) |
| F2.8 incident brief | **SETTLED** | `P309_REVIEW_BRIEFS.md:40-45` (task 3 names the §2.5 mapping, the 48 CPU-h budget with its mechanics, and the Stage-1b fallback, with the RLR-knockout context) |

### G2. New issues

* **D1 (disclosure; recommended before the owner decides; changes no rule).** The F2.6 correction line
  (`ZERO_TARGET_LEDGER.jsonl:537`) reveals that the generator also ran in scratch on 2026-09-29 at about 23:14Z and
  about 23:59Z.
  * Both runs preceded R2's final FREEZE_READY commit `f026c80b` (2026-09-30 00:06:01Z). The 23:14Z run fell inside
    R2's phase-B window. The charter prepares `protocol_prep/` "only if a route is independently reviewed as
    FREEZE_READY" (`README.md:42`).
  * The runs were metadata and hashes only, with no target risk. But the owner row still says "the manifest-generator
    **run**" (`P309_OWNER_DECISIONS.md:24`), as does the incident brief (`P309_REVIEW_BRIEFS.md:35`), with no timing.
  * State "runs, from 2026-09-29 ~23:14Z, i.e. before R2's final verdict" in both places, so that the owner's P0-2
    acknowledgement and the incident-independence review cover the sequencing.
* **D2 (polish).** The coordinator's file-name read of `C1B_R2_CODE_PINS.json` (outside NS) appears in no ledger
  line. The rev.-2b ledger lines do not mention it, and `EXPOSURE_LEDGER.jsonl` is unchanged since `fae64157`, which
  I checked by git metadata without opening it. Add a GOVERNANCE line if the campaign ledgers necessary reads outside
  NS.

**Optional polish (changes no rule; not needed before a freeze).**
* **P1.** "Stage 1a ≤ 48 CPU-h total" (`P309_FORMAL_PACKAGE.md:25`; `P309_PROTOCOL.md:75`) is really a *start
  threshold*. Jobs already running may finish past it, up to the 12 CPU-h per-job limit (worst case about 48 + 4 × 12
  CPU-h). The mechanics at `P309_PROTOCOL.md:90-92` are explicit and govern, so only the label is loose.
* **P2.** §2.2 (`P309_PROTOCOL.md:46`) could say "`run_block` with `ladder = (d,)`" to match the (b_j, rung) job
  unit. The pinned `run_block` accepts a one-rung ladder (`impl/srk_certify.py:273`).
* **P3.** Reword checklist item 16 (`P309_REVIEW_BRIEFS.md:78`) as "the real band is never used; QC16 uses a test
  band".
* **P4.** The correction line says the rev.-2 manifest was "at a2678cc7". It was committed at `2db92936`; `a2678cc7` is
  its push record.
* **P5.** The protocol_prep documents' headers still read "rev. 2" for the rev.-2b content.

### G3. Follow-up 2 verdict

**COMPLETE_WITH_NOTES** (line 2).
* The N13 residue and F2.1–F2.4 and F2.6–F2.8 are SETTLED. F2.5 is settled except one checklist sentence (P3).
* The rev.-2b budget mechanics and the Stage-1b budget mapping are coherent and add no rule inconsistency.
* **Why not COMPLETE:** the only item I do not regard as optional is D1, a one-line disclosure fix in the owner row
  and the incident brief. It concerns what the owner acknowledges under P0-2, not any rule.
* **Once D1 is written, the remaining items (D2, P1–P5) are optional polish.** They change no rule, are not needed
  before a freeze, and would **justify COMPLETE** on their own.
* This classification authorizes nothing; a freeze still requires the owner (P0-1).

**Follow-up 2 disclosures.**
* I saw no 305–309 value. I met only file paths, blob ids and generator run times (metadata).
* The only runs were FU2-0 (read-only) and FU2-1 (self-audit, no evaluation).
* Nothing in the repository was written except this file. No git write.

---

## Follow-up 3 (2026-09-30): check of D1, D2 and P1–P5

### H0. Declaration (written 00:47Z, before any run beyond read-only checks)

Reviewed state: HEAD `29c0b49f`. The content is at `0a3f1604`, the manifest at `cb63fed6`, and follow-up 2 is
preserved at `eb3b3432`. The same brief, firewall and rules apply. Earlier text is not rewritten; only line 2 is updated
at the end.

**Firewall choice.** My original instructions list "do not open `ledger/INCIDENT_*`" among the non-negotiable hard
rules. So I do **not** open `ledger/INCIDENT_309R1_04_*`, although the coordinator now allows it. I assess 309R1-04 from
ERRATA E-18, the ledger lines, the package texts and git metadata. I also do not open any scratchpad file other than
my own `scratchpad/r3/`, and that includes the Phase-4 drafts.

| id | what | kernel / geometry / drift | evaluates? |
|---|---|---|---|
| FU3-0 | Read-only checks: `git diff c391bc47..HEAD` (excluding the incident file's content); the changed `protocol_prep/*` text, `ERRATA.md`, the new ledger lines and the `code/self_audit.py` diff; manifest pins recomputed as before | none | no |
| FU3-1 | `code/self_audit.py` (the new blob) through my RD3-1 wrapper, output to `scratchpad/r3/fu3/` | none | no |

**Executed as declared.**
* **FU3-0 (read-only checks).**
  * Manifest at `0a3f1604`: 48 code pins and 7 data pins. **Every blob and every NS sha256 matches** at `0a3f1604` and
    at HEAD.
  * No pin was added or dropped. The changed blobs are exactly `code/self_audit.py`, `ERRATA.md` and the four package
    documents. The data pins are unchanged and metadata only.
  * The generator copy matches its recorded sha256.
  * The `code/self_audit.py` diff only adds incidents 03 and 04 to the A3 immutability list (lines 43-46), so it is
    strictly more checking.
  * `EXPOSURE_LEDGER.jsonl` is unchanged, which I checked by git metadata only.
* **FU3-1 (self-audit, new blob, at HEAD `29c0b49f`).** A1–A10 all PASS, with 542 ledger lines and max drift 37/32. A3
  reports all five immutables unchanged, incidents 03 and 04 included. The A10 envelope output is byte-identical to the
  committed file. Local = remote = `29c0b49f`. Outputs are in `scratchpad/r3/fu3/`.
* I did not open `ledger/INCIDENT_309R1_04_*` or any other scratchpad file. Nothing was written except this file, and
  there was no git write.

### H1. Status

| item | status | evidence |
|---|---|---|
| D1 disclosure | **SETTLED** | Incident 309R1-04 plus ERRATA E-18 (`ERRATA.md:24`) appear in all of: the owner incidents row, with the generator runs now plural and dated "from 2026-09-29 23:11Z, before R2's final verdict" (`P309_OWNER_DECISIONS.md:24`); P0-2 (`P309_PROTOCOL.md:19`); the grant's `disclosed_liabilities` (`P309_FORMAL_PACKAGE.md:95-96`); the incident brief's task 1 (`P309_REVIEW_BRIEFS.md:34-38`). The times are corrected append-only (`ledger/ZERO_TARGET_LEDGER.jsonl:539`) |
| D2 ledger the C1B_R2 file-name read | **SETTLED** | `ledger/ZERO_TARGET_LEDGER.jsonl:540` (GOVERNANCE; names only; no pin value, hash or number) |
| P1 start threshold | **SETTLED** | `P309_PROTOCOL.md:90-92`; `P309_FORMAL_PACKAGE.md:25`. The §2.5 table row (`P309_PROTOCOL.md:75`) points to the mechanics, which govern |
| P2 `ladder = (d,)` | **SETTLED** | `P309_PROTOCOL.md:46` |
| P3 checklist item 16 | **SETTLED** | `P309_REVIEW_BRIEFS.md:79` |
| P4 commit ids | **SETTLED** | `ledger/ZERO_TARGET_LEDGER.jsonl:539` (`2db92936` is the content, `a2678cc7` the push record) |
| P5 rev. 2b headers | **SETTLED** (trivial residue) | `P309_PROTOCOL.md:1`, `P309_FORMAL_PACKAGE.md:1`, `P309_OWNER_DECISIONS.md:1`. `protocol_prep/README.md:1` still says "rev. 2". It is unpinned and cosmetic |

### H2. 309R1-04: adequacy, rating, effect on defensibility

I assessed this from E-18, the ledger lines, the package texts and git timestamps. I did not open the incident file.
* **Adequacy of the disclosure.** Adequate. It is recorded as an incident with an erratum. The times are corrected in
  an append-only way, with the earlier approximations kept visible. It appears in every place an owner or reviewer acts
  on: P0-2, the owner row, the grant's liabilities and the incident brief. It was self-reported and its scope widened
  beyond my D1 reading, which counts in its favour.
* **LOW is reasonable.**
  * It is a sequencing deviation from the charter (`README.md:42`), with no evaluation and no new exposure. Nothing
    entered the namespace before R2's final FREEZE_READY (`f026c80b`, 00:06:01Z).
  * The route was already fixed before the first draft: rule S was committed at `7f1eb363` (09-29 13:52:08Z) and
    THEOREM_SRK at `3df7a1a5` (13:15:54Z), while the first draft is from 14:11:58Z. So the drafting did not precede or
    shape the route choice.
  * R1 and R2 reviewed committed material only. R2 recorded `protocol_prep/` as empty, so neither route review saw a
    draft.
  * The package's rule choices with outcome effect (the §2.5 mapping, the budget, the Stage-1b fallback) were fixed
    in committed rev. 2/2b after R3, before any 309 Stage-1 number. They are already routed to the incident review
    (brief task 3).
  * The residual risk is anchoring of design before independent review, which is what LOW describes.
* **Effect on prospective defensibility: none on the package's rules.** Defensibility rests on three things, and
  309R1-04 changes none of them:
  * every rule and parameter is fixed and committed before any 309 Stage-1 number or target evaluation;
  * the texts contain no target information;
  * the independent reviews.

  One caveat: "no target information in the drafts" currently rests on the coordinator's statement.
* **Recommendation (process, not a package item; changes no rule).** The scratchpad is ephemeral. Before the
  incident-independence review, preserve the drafts' sha256 and timestamps. After a quarantine scan, also preserve
  inert copies, unless the incident file already does this. The review can then compare drafts with the committed
  package on primary evidence.

### H3. Follow-up 3 verdict

**COMPLETE** (line 2 updated).
* Every note of this review (N1–N19, F2.1–F2.8, D1, D2, P1–P5) is SETTLED.
* The only residues are the `protocol_prep/README.md:1` "rev. 2" header and the draft-preservation recommendation in
  H2. Both are optional: neither changes a rule, and neither is needed for the owner's freeze decision. The package is
  ready to be presented to the owner.
* **This verdict authorizes nothing.** A freeze requires the owner's explicit authorization (P0-1). It then requires,
  in order, the incident-independence review, the freeze, qualification, the qualification review and a separate grant.

**Follow-up 3 disclosures.**
* I saw no 305–309 value. I met only file paths, blob ids, commit and draft timestamps, and incident and erratum
  labels.
* The only runs were FU3-0 (read-only) and FU3-1 (self-audit, no evaluation).
* Nothing in the repository was written except this file. No git write.
