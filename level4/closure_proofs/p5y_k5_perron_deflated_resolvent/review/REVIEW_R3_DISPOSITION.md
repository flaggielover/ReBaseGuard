# Review r3 — disposition

| item | disposition |
|---|---|
| B1 | `falsify_registry.py` r2: vectorised independent quadrature; ~5.2k states for blocks (4.1k for cells) including the line p+m = 1 at offsets −10⁻³, 0, +10⁻³ × 401 points, a 13 × 101 band around it, near-axis strips at 10⁻³…5·10⁻² and p+m = 4; a 21 × 21 local refinement around every extreme; pass criteria are the CERTIFIED claims (min ≥ margin_lower_bound; \|r\|/λ ≤ 1; C_T ≥ max w; τ ≥ w(a); Ā ≥ W(a); d_j(0,0) inside candidate_at_atom); six planted bugs incl. a 0.02 bump near (0.9, 0.1) and λ ÷ 1.2. Test run (blocks, cells 0 and 148) reproduces the reviewer's extremes: block slack +0.0020, ARL slack +3.3e-5, λ ratios 0.950 / 0.825; all six planted bugs flagged |
| F1 | `frozen_guard`: after the freeze, `git diff --name-only <freeze> HEAD -- <namespace>` may contain only `evidence/successor_r1/…`; checked before any parsing; the consumer script removes its own directory from `sys.path` before importing the standard library. Simulated in a scratch clone: a committed `code/json.py` is refused with the F1 message |
| F2 | `consume` requires the qualification's S00 head to equal the freeze commit (the commit that added the protocol); the result records `freeze_commit` and `evaluation_head`; S00 passes only at the freeze commit |
| F3 | `deflated_consume.py prefreeze` writes a JSON record (command, HEAD, namespace status, protocol sha, exception, message); S08 requires refused, the message "successor protocol is not tracked", the same protocol sha, and HEAD = the freeze commit's parent |
| F4 | FEASIBILITY_REPORT.md and review/ADJUDICATION_BRIEF.md committed before `make_protocol` |
| F5 | the adjudication brief compares S12 by verdict and tolerance; the protocol records it |
| N5 note | accepted as procedural: freeze-before-evaluation is enforced for `consume`; other entry points are pre-freeze tools |
