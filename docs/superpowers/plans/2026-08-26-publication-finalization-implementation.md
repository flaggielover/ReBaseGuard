# Publication finalization implementation plan

1. Freeze the clean synchronized starting commit and inventory final evidence,
   source figures, release/tag conventions, citation facts, and license status.
2. Implement a presentation-only data loader and deterministic Matplotlib
   renderer in `scripts/generate_final_figures.py`; read only frozen JSON,
   Markdown tables, and synthesis prose.
3. Generate eight shared-style publication figures as SVG and high-resolution
   PNG under `figures/final/`, then create a provenance README containing exact
   source paths, transformations, evidence classes, limitations, sections, and
   SHA-256 digests.
4. Replace the root README with the reviewer-first structure from the approved
   design, embedding the figure story and linking directly to authoritative
   synthesis/proof/certificate/validation artifacts.
5. Create Level-4 release notes and a mechanical release checklist. Record that
   no DOI, explicit license, or sufficiently complete author metadata exists;
   do not create speculative citation metadata.
6. Add a presentation-only verifier and focused tests for source integrity,
   deterministic figure bytes, README/release claim safety, terminal-state
   boundaries, required negative/limiting evidence, and strict diff scope.
7. Run the final-figure generator twice and compare digests; visually inspect
   all eight PNGs; run presentation and synthesis checks, terminal focused and
   adversarial checks, authoritative repository verification, and the terminal
   closure reproducer.
8. Inspect the complete diff, commit as `Finalize ReBaseGuard figures, README,
   and Level-4 release`, fast-forward push `main`, create/push the annotated tag
   `rebaseguard-level4-closed`, and verify it resolves to the final commit.
9. Use authenticated GitHub CLI to create `ReBaseGuard — Level-4 Closed
   Research Release` from the prepared notes. Confirm clean worktree and 0/0
   local/remote divergence without rewriting any existing tag or history.
