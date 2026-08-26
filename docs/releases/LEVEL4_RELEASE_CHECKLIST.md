# Level-4 publication release checklist

This checklist records the release gate for tag
`rebaseguard-level4-closed`. Evidence-producing commands are listed beside each
item; the scientific state is read-only throughout.

- [x] `LEVEL-4-CLOSED` unchanged — terminal decision assertion in
  `verify_publication_release.py`
- [x] `17 PASS / 1 PARTIAL / 0 FAIL / 0 OPEN` unchanged — terminal decision
  assertion
- [x] 16/16 mandatory requirements pass — terminal decision assertion
- [x] L4R-13 remains nonmandatory `PARTIAL` — terminal decision assertion
- [x] Rigorous SR local-instability Arb certificate remains `OPEN` — terminal
  decision assertion
- [x] Final synthesis passes — `python3
  docs/research_synthesis/verify_synthesis.py --no-diff-check`
- [x] Eight final figures are traceable — manifest source/path/hash checks
- [x] Figure generation is deterministic — two clean regenerations produce
  identical PNG, SVG, manifest, and provenance hashes
- [x] README and release prose are claim-safe — publication claim-firewall
  checks
- [x] No scientific or historical artifact is modified — strict
  presentation-only diff guard
- [x] No network science or simulation is invoked — generator import and
  source scan
- [x] Unsuccessful external-validation tasks remain visible — task/count
  assertions and Figure 7
- [x] Limitations and negative result are visible — required prose and Figure 8
- [x] Terminal focused tests pass — final-closure test suite
- [x] Terminal adversarial checks pass — final-closure adversarial verifier
- [x] Repository verification passes — `bash scripts/verify_level_4.sh`
- [x] Terminal reproducer passes — `bash
  level4/final_level4_closure/reproduce.sh`
- [x] Local and remote `main` are synchronized — verified after fast-forward
  push
- [x] Annotated release tag points to the intended publication commit —
  verified after tag push
- [x] GitHub Release uses the prepared notes — verified after creation

Release metadata boundary:

- No DOI has been assigned.
- No explicit repository license exists.
- No `CITATION.cff` was created because repository-authoritative records do not
  establish sufficiently complete author metadata.
