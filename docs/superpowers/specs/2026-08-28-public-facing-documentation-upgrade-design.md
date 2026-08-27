# Public-facing documentation upgrade design

## Objective

Refactor the root `README.md` into a compact research landing page and replace
the template `rebaseguard-lean/README.md` with an exact external-review guide.
The work changes presentation only. Frozen scientific artifacts, theorem
statements, Lean sources, Arb sources and certificates, experiments, results,
and historical decisions remain untouched.

## Authoritative evidence and claim order

Repository-authoritative scientific artifacts override presentation prose.
The landing page will present the strongest rigorous core as a three-part
evidence chain for the frozen two-sided Gaussian CUSUM at `m=1`, `rho=1`,
`k=1/2`, and `h=5`:

1. the human theorem connects the stopped expectation derivative to the
   conditional-mean reference map;
2. Lean kernel-checks the stopped-likelihood differentiation and moment spine;
3. Arb independently certifies `Gamma_CUSUM > 2` by an outward-rounded
   interval enclosure.

Only the combination supports the local-repulsion conclusion for the
deterministic conditional-mean fixed point. Lean will not be described as
proving the numerical inequality, and Arb will not be described as proving
differentiation under the expectation.

The later `SR-GAMMA-CERTIFIED` result may appear as a scoped related result,
but it does not replace the CUSUM core as the primary fully instantiated Lean
entry point. All deterministic results remain distinct from stochastic or
operational behavior.

## Root README architecture

Target 120--160 source lines using a result-first evidence ladder:

1. title and one-sentence research problem;
2. a short explanation of stopping-selected recursive re-baselining;
3. the strongest-result box with the human, Lean, and Arb roles visibly
   separated;
4. a compact evidence table covering human mathematics, numerical
   correspondence, Lean, and Arb;
5. the shortest verified reproduction path;
6. a reviewer-oriented repository map;
7. concise limitations and a negative-result summary;
8. one short forward-looking internal-scope note;
9. author, citation, and unresolved-license pointers.

Detailed policy performance, validation task counts, stage chronology,
theorem dependencies, and the full result catalogue will move behind links to
`docs/research_synthesis/`, the Research Brief, and frozen reports. The README
will preserve the minimum headings and exact status markers needed by the
current presentation guard without restoring campaign-log density.

The limitations section will preserve these boundaries:

- historical Stage-D D2.3 and Track 1A remain failed even though the separate
  Track 1B theorem requirement later closed within its own convention;
- L4R-13 remains a nonmandatory partial extension;
- results are detector-, convention-, and parameter-scoped;
- deterministic local stability is not an operational phase-transition
  theorem;
- the frozen crossing study produced a scoped negative result;
- semi-real evidence is not production validation;
- novelty wording remains limited to the documented search scope.

## Lean README architecture

`rebaseguard-lean/README.md` will be an audit guide with the following
sections.

### Scope

Explain that the primary imported Lean library formalizes the critical frozen
CUSUM analytic proof spine. It does not formalize the entire project.

### Environment and build

Record the actual configuration:

- Lean and Lake `v4.34.0-rc1`;
- Mathlib input tag `v4.34.0-rc1`, pinned revision
  `de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11`;
- `lean-toolchain`, `lakefile.toml`, and `lake-manifest.json`;
- exact check command `cd rebaseguard-lean && lake build`.

The implementation audit must rerun the command and report its exit status
truthfully. Existing cosmetic warnings are recorded, not repaired in frozen
Lean sources.

### Formal theorem correspondence

Use exact declarations from the source and closure theorem map, including:

- `stoppedIntegrand_hasDerivAt`;
- `hasDerivAt_integral_stoppedIntegrand_zero`;
- `isStoppingTime_cusumTau`;
- `integrable_exp_abs_walkAt_of_moment_tail`;
- `exists_pos_integrable_exp_abs_walkAt_rebaseguard`;
- `rebaseguard_separate_moments`;
- `hasDerivAt_integral_rebaseguard_gaussian`;
- `hasDerivAt_rebaseguard_cusum`.

Each row will identify the human proof role, exact Lean name, source file, and
kernel-checked status. A short navigation chain will route reviewers from
`closure/02_THEOREM_MAP.md` to the declaration, source module, and build
command.

### Bypass and axiom audit

Every zero-bypass statement will be explicitly scoped to the primary imported
proof path, `rebaseguard-lean/RebaseguardLean.lean` and the modules it imports.
The README will state that this path contains no `sorry`, `admit`, project
`axiom`, `unsafe`, or `native_decide` occurrence.

Immediately after that statement it will disclose the deliberate unimported
negative fixture `closure/ENVIRONMENT_PROOF/logs/EnvProof.lean`, which contains
`sorry` specifically to demonstrate that the environment audit detects it.
The fixture is not part of the imported scientific proof path. This disclosure
prevents an inaccurate repository-wide zero-`sorry` claim.

The axiom section will report the audited headline baseline of `propext`,
`Classical.choice`, and `Quot.sound`, with no project-specific scientific
axiom or `sorryAx` in the primary path.

### Related separate formalizations

Link the `m>1` Track 1B, symmetric SR, regular location-family, and period-two
Lean sources as related, conditional, and separate formalizations. State
explicitly that the presence or successful compilation of a Lean source does
not by itself establish the scientific theorem, discharge its human analytic
obligations, certify its numerical premises, or close the corresponding
campaign. Their own correspondence reports and frozen decisions remain the
authority.

### What Lean does not prove

Retain a full, prominent boundary section. The primary Lean project does not
prove:

- either CUSUM or SR Arb interval enclosure;
- the human bridge from the stopped expectation derivative to the complete
  conditional-mean map conclusion;
- numerical correspondence or Monte Carlo results;
- complete concrete infinite-process obligations for the separate conditional
  `m>1`, SR, or location-family spines;
- simulator correctness, policy performance, semi-real validation, or the
  operational-crossing result;
- all Stage A--F or repository-wide scientific conclusions.

## Verification and failure handling

After editing, verification will:

1. run `lake build` from `rebaseguard-lean/`;
2. search the primary imported path for `sorry`, `admit`, `axiom`, `unsafe`,
   and `native_decide`;
3. confirm the deliberate `EnvProof.lean` fixture and its non-imported status;
4. verify every documented theorem name in Lean source;
5. verify every repository-relative path and Markdown link;
6. run the current academic-presentation guard with `--no-diff-check` and the
   synthesis verifier, because the guard's older fixed presentation allowlist
   predates this required design checkpoint;
7. inspect `git diff --check`, `git status --short`, and the complete diff;
8. assert that the implementation diff changes only `README.md` and
   `rebaseguard-lean/README.md` relative to this separately committed design
   checkpoint.

Any disagreement with authoritative evidence, broken link, missing theorem,
build failure, guard failure, source-code diff, or frozen-artifact diff stops
the commit. Verification failures will not be repaired by weakening scientific
claims or changing scientific artifacts.

## Git handoff

The design specification is a separate workflow checkpoint. After the user
reviews it, implementation will modify only the two intended README files,
run the stated checks, commit with
`docs: improve research and Lean verification READMEs`, and push by ordinary
fast-forward update only. Historical tags and releases will not move.
