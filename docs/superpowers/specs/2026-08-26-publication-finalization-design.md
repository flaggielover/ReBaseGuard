# Publication finalization design

## Objective and boundary

Finalize ReBaseGuard as a reviewer-facing research release after terminal
`LEVEL-4-CLOSED` closure and the authoritative research synthesis. This stage
changes presentation only: eight consolidated figures, the root README,
release documentation, and presentation/release guards. It does not run
scientific experiments, alter data, modify theorem or certificate content,
change protocols, or revise any historical or terminal status.

The immutable state remains 17 PASS, one nonmandatory PARTIAL, zero FAIL, zero
OPEN in the original 18-row ledger, with 16/16 mandatory requirements passing.
L4R-13 remains PARTIAL; the rigorous SR local-instability Arb certificate
remains OPEN; `Gamma_SR>2` remains confirmatory numerical; D4 remains a local
deterministic boundary; empirical safety remains regime-dependent; novelty
remains N2.

## Selected architecture

Use a deterministic hybrid figure pipeline in `figures/final/`.

- `scripts/generate_final_figures.py` reads only frozen repository evidence and
  the synthesis narrative. It imports no simulator, downloads nothing, and
  produces no scientific result files.
- Eight publication figures are rendered as SVG plus high-resolution PNG with
  one shared accessible visual system. SVG identifier salts and metadata are
  fixed so repeated runs are byte-stable in the frozen environment.
- Figures based on quantitative evidence are redrawn from stored JSON or a
  frozen generated report table. Conceptual diagrams are derived only from the
  final synthesis.
- Historical figures are neither moved, deleted, nor modified. They remain
  evidence and visual references in their campaign namespaces.
- `figures/final/README.md` is the provenance ledger and records source paths,
  transformations, evidence class, paper section, limitations, and generated
  SHA-256 digests.

This is preferred over copying existing figures unchanged because the existing
panels have inconsistent typography and several legacy labels. It is preferred
over reconstructing every scientific curve because that would risk creating a
new estimand or an uncertified interpolation. The hybrid redraws only quantities
already frozen and uses explanatory diagrams where a scientifically exact
curve is not required.

## Eight-figure story

1. **Recursive re-baselining mechanism.** A cycle diagram shows reference,
   monitoring, stopping-time alarm, selected-window reuse, and the next cycle.
   It distinguishes the noisy cycle from the deterministic conditional-mean
   map.
2. **Stopped-selection derivative and local instability.** A proof/evidence
   diagram connects `F'_rho(0)=rho(1-Gamma_CUSUM)` to the Lean-checked spine,
   the Arb enclosure, and the scoped local consequence.
3. **Certified deterministic-skeleton period two.** A symmetric two-node orbit
   uses the certified root interval and multiplier. It does not draw an
   uncertified smooth map or imply period two for the noisy chain.
4. **`m`-`rho` local-stability map.** The D4 `GammaTilde_m` grid defines
   `rho_c(m)` and the stable/unstable regions, with the `[70,72]` full-reuse
   crossing and a visible “not operational” boundary note.
5. **Stability-aware P3 policy.** The four frozen actions are plotted against
   P0, P1, and fixed P2, with the lower-95%-bound construction and `m=100`
   saturation explicit.
6. **Reference and monitoring consequences.** Frozen simultaneous lower bounds
   for P1-minus-P3 reference MSE and P3-minus-P1 ARL0 are shown for active
   regimes. P2 descriptive advantages and P3=P1 saturation remain visible as
   limitations.
7. **Semi-real external-validation synthesis.** A task-level matrix retains all
   Stage E, V2, and V3 tasks, shows 0/3, 1/3, and 2/2, and reports the non-pooled
   count of three supporting tasks against two required.
8. **Negative operational-crossing result.** The mathematical crossing is
   placed beside the four frozen operational trends, normalized only for
   presentation. The figure states 0/4 peaked and 4/4 were monotone in log `m`.

Every panel remains readable without color through marker, hatch, line-style,
or text redundancy. Main typography, line widths, panel letters, whitespace,
legend placement, and export dimensions are shared.

## Root README

Replace the stale chronology-heavy README with a concise public entry point:

1. identity and internal-closure status;
2. why stopping-selected recursive reuse matters, with Figure 1;
3. compact core derivative result;
4. seven grouped findings;
5. evidence map;
6. P3 policy and limitations, with Figures 5--6;
7. semi-real validation and the first-class negative result, with Figures 7--8;
8. authoritative reproduction commands;
9. reviewer-first repository map;
10. limitations, citation guidance, and actual license status.

“Level 4” is defined as an internally frozen research-program criterion rather
than external academic certification. The README links to the synthesis rather
than duplicating theorem proofs.

## Release package

Create `docs/releases/LEVEL4_RELEASE_NOTES.md` and
`docs/releases/LEVEL4_RELEASE_CHECKLIST.md`. Release notes identify the
publication checkpoint, terminal lineage, principal results, evidence types,
negative result, semi-real validation, N2 position, reproduction command,
limitations, and authoritative artifact locations.

No license is selected because no license file or repository license metadata
exists. No DOI, venue, publication date, institutional endorsement, ORCID, or
coauthor is invented. `CITATION.cff` is omitted because the only
repository-authoritative author identity is the Git username `suzhe`, which is
insufficient for honest required person metadata. The README instead gives a
minimal tag/commit citation instruction and explicitly says there is no DOI.

After verification, create the final commit
`Finalize ReBaseGuard figures, README, and Level-4 release`, fast-forward push
`main`, create and push the annotated tag `rebaseguard-level4-closed`, and use
authenticated `gh` to create the matching GitHub Release. The existing
`level1-3-closure-v1` local/remote mismatch is historical and unrelated; this
stage does not move or rewrite it.

## Guards and verification

Add a presentation-only verifier and focused tests. They fail if:

- any final figure or provenance entry is missing;
- regeneration changes SVG or PNG bytes;
- a plotted source path or digest does not match frozen evidence;
- README or release prose crosses the claim firewall;
- terminal verdict, counts, L4R-13, SR evidence boundary, or N2 position drifts;
- the implementation diff touches anything outside the root README,
  `figures/final/`, the final-figure generator, release documents, this
  design/plan, and presentation-only guards;
- failed tasks, limitations, or the negative result disappear.

Verification runs figure provenance and deterministic regeneration checks,
README/release claim checks, existing synthesis verification, terminal focused
and adversarial checks, authoritative repository verification, and the final
offline closure reproducer as required. A failure is fixed only in
presentation artifacts; scientific or historical sources are never rewritten.
