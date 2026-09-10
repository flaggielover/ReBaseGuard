# P5Y K1 SR O9 — pre-T2 governance successor

**Classification: `T2_GOVERNANCE_REPAIR_CLOSED`.** Governance and evidence repair only.
No scientific threshold, degree, precision, patch, candidate, contract, obligation or
theorem target changes. No predecessor is edited. Machine-readable rulings:
`config/PRE_T2_GOVERNANCE.json`. Checker: `code/verify_pre_t2.py verify`.

## Issue 1 — reference reproduction criterion

The historical Task1R (`delta_F0 = 1.9581425988141803e-05`) and Gate-2F
(`w_panel_total_ABS = 2.9771109428542136e-08`) records were produced on the pre-resize
runtime and remain **immutable historical evidence** (file hashes bound in
`config/AUTHORIZED_RUNTIME_REFERENCES.json`, re-verified unchanged).

The frozen record already defines identity as *(producer, runtime contract, inputs)*:
aux4 `RUNTIME_BINDING` (OpenBLAS kernel choice moves 62/240 candidates),
`sr_patch.candidate_identity` ("a candidate built under a different numerical backend
cannot masquerade as this one"), the cap protocol's refusal of any runtime other than
`d49f0437...`, and replay determinism defined as zero moved scientific leaves. Under
that doctrine the T2 reference identity is **the frozen certifier algorithm executed
under the bound runtime contract, pinned by committed hashes**:

* **A (Task1R F_0):** runtime == `d49f0437...`; candidate identical to T1 (packet hash
  `c72f65b3...`); frozen `harness.certify` output hash committed; T2 baseline mode must be
  byte-equal to it; T2 O9 mode must have identical Taylor coefficients and error channels
  no smaller than baseline; per-line verdicts must equal the historical ones.
  Authorized-runtime `delta_F0 = 1.9581424276820705e-05` (drift vs historical 8.7e-8,
  every line PASS in both).
* **B (Gate-2F hhat_1):** the kernel enclosure and every runtime-insensitive field must be
  byte-identical to the *historical* record (they are); the `eps_cand`-derived fields are
  pinned to the frozen code's authorized-runtime output; `ABS_PASS` must equal historical
  and `w_panel <= w_panel_max` is checked in exact rationals. Drift 1.5e-11.
* **C (O9):** committed packet hashes `c72f65b3...` / `c0fc8609...` and the new per-shift
  (s = 0..3) hashes must be reproduced by the T2 contraction; baseline bit-exactness as in
  the committed worker; raw `z^s` weights validated by an exact-identity unit test.

Historical scalars are consistency/drift evidence only, never byte-exact acceptance
identities for the new runtime. Nothing is relaxed.

## Issue 2 — panel universe versus the binding P1 rule

The conflict is a **construction mismatch**, not a flaw of the census on its own terms:

| construction | used by | panels | binding P1 check |
|---|---|---|---|
| core partition + 2 strip panels (census) | Gate-2B cost census | 83,452 units | passes (0 failures; repair-invariant, Gate-2B s7) |
| census counts forced into the span construction | — | 83,452 | **fails on 1,011 / 3,994 patches** (headroom down to -0.138) |
| span partition + 2 analytic endpoint slivers (Task1R) | the frozen certifier / O9 backend / cap packet | 76,475 contracted + 7,988 sliver units = **84,463** | passes on all 3,994 (worst headroom 1.7e-3) |

The binding checkpoint binds the P1 block, not a panel count. The frozen certifier
(Task1R, the only adjudicated SR certifier, the backend's reference architecture, and the
owner of the frozen `B_end` sliver line) executes the span construction. **Ruling:** the
executable T2 panel universe is `task1r-span-p1-v1` (table `P1_PANEL_UNIVERSE.json`,
sha256 recorded in the governance file), with canonical IDs
`SRpanel:v2:task1r-span-p1:64:{i}:{j}:{k}/{n_z}` and `SRsliver:v2:task1r-span-p1:64:{i}:{j}:{L|U}`.
Boundaries are `z_k = L_c + 2hk`, `h = span/(2 n_z)` on every patch; counts differ from the
census in 1,011 patches. The 83,452 census is superseded only as the executable universe
and as a cost multiplier; it stays immutable historical evidence. The 102 contract
identities do not depend on panels and are unchanged. Reference patch (17,11) has
`n_z = 28` in both constructions, so references A and B are unaffected.

## Consequences

* **Scientific scope:** unchanged.
* **Rebinding:** every artifact that carries 83,452 / 2,689,824,864 / 11.474662 is listed
  with its hash and key paths in `rebinding_required`; none is edited here.
* **4500 CPU-h cap:** `UNQUALIFIED` — preserved as history, not revoked, but its basis is
  superseded and it omits known components; requalification at T7 from measured units.
  The governance file carries an arithmetic rebase of the contraction line only.
* **History preserved:** all historical values, the census, O9/cap artifacts, T1, and the
  first production attempt with its settled accounting (0 genuine cells, 16 cells at
  `torn_attempts = 1`).
* **T2 may resume**, implementing A1–A6, B1–B5, C1–C5 as gates and using the executable
  panel universe.
