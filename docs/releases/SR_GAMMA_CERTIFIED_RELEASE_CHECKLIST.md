# SR Gamma certified release checklist

This checklist governs the additive tag `rebaseguard-sr-gamma-certified`. It is
separate from the historical `rebaseguard-level4-closed` checklist.

- [x] Historical `LEVEL-4-CLOSED` authority retained: 17 PASS, 1 PARTIAL, 0
  FAIL, 0 OPEN; 16/16 mandatory PASS; L4R-13 nonmandatory PARTIAL
- [x] Original Level-4 tag target retained
- [x] `SR-GAMMA-CERTIFIED` authority exists
- [x] Rigorous `Gamma_SR` interval has lower endpoint strictly above two
- [x] `epsilon_a`, `epsilon_b`, resolvent, `K_z`, precision, and candidate
  metadata match certificate artifacts
- [x] Global `a` and `b` covers each certify 1,210/1,210 patches
- [x] Independent resolvent, global-`a`, and global-`b`/propagation auditors pass
- [x] Focused 28-test and full 94-test SR suites pass
- [x] Closed-upgrade reproduction passes and is byte-stable
- [x] All 52 original SR paths remain byte-identical
- [x] The 52-to-92 additive freeze behavior is documented without weakening the
  historical guard
- [x] Current reviewer materials use explicit terminal/current temporal wording
- [x] Historical reports and original release wording remain historically true
- [x] Claim firewall still prohibits detector-independent, distribution-free,
  universal, production, priority, and operational-transition overclaims
- [x] Figure audit found no stale SR-open visual claim; images were not
  regenerated
- [x] Separate post-Level-4 verifier and archive manifest pass fail-closed checks
- [x] Level-4 and SR reproduction commands are independently documented
- [x] Git diff contains only additive certificate, current-facing integration,
  release, provenance, and guard artifacts
- [ ] Final integration/content commit recorded in archive manifest
- [ ] PR #1 marked ready, merged without force, and local `main` synchronized
- [ ] Annotated SR tag pushed and verified against remote
- [ ] Post-Level-4 GitHub Release created without altering the Level-4 Release
- [ ] Deterministic source archive generated and SHA-256 reported

The unchecked release-engineering items are completed only after the associated
remote actions are mechanically verified.
