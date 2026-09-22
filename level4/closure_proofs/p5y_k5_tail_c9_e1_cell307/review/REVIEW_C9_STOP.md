# Hostile review of the C9 `HARD_STOP_BEFORE_AUTHORIZATION`

Reviewer context: fresh, adversarial, nothing assumed. Target: campaign C9,
`level4/closure_proofs/p5y_k5_tail_c9_e1_cell307`, branch `p5y-k5-tail-c9-e1-cell307`,
HEAD `de5be756`. The brief was to attack the STOP, on the principle that a wrong STOP costs
exactly what a wrong GO costs.

Ground rules I held to: I ran no C9 producer (they rewrite their own evidence, and I wanted the
tree byte-identical under review); I contacted no AWS or Vultr host; I installed nothing; I
imported none of numpy/scipy/flint/mpmath/sympy/gmpy2; I modified no file except this one. All
probes were exact-`Fraction` arithmetic over committed artifacts, written to the session
scratchpad.

---

## 1. CRITICAL — C9 redefined E1 as a replay, then "discovered" that a replay replays. Blocker 1 is manufactured.

**Where.** `code/c9_common.py:1-2` ("one route (R3/E1 operator certification), **one authorized
certification**"); `STOP_RECORD_C9.md` ("not 'one authorized execution of the committed E1
producer'"); `evidence/phase5/C9_TOOLCHAIN.json` → `blocker_1_scientific.finding` and
`.consequence`; `code/c9_toolchain.py:35-61`.

**What is wrong.** E1 has a committed definition, and it is not "run the committed producer".

- `p5y_k5_tail_c6_evidence_recovery/evidence/leverage/C6_CLASSIFICATION.json`, entry `E1`:
  - `required_object`: "a tighter certified operator tuple (tau, D_lo, Abar) for A0"
  - `existence`: "**OBJECT_ONLY_HYPOTHESIZED (a BETTER tuple)**; the CURRENT tuple and its inputs
    are committed"
  - `GATE_DEFECT`: "E1's object is a BETTER operator tuple ... **it was never evaluated by anyone
    and there is nothing to replay**. The honest class — inputs present, new ZERO-NEW-REAL
    certification work required, blocked by toolchain — does not exist in the frozen gate."
  - `missing_what`: "a TOOLCHAIN **for the WORK**. Every input exists and is committed; **the
    result does not exist**."
  - and the file's own headline: "a faithful replay ... delivers the inputs and none of the gain.
    'Missing a toolchain' is true of the INPUTS and false of the RESULTS."
- `p5y_k5_tail_c8_operator_feasibility/config/DECISION_GATE_C8.json:31`: "R3": "E1 / operator
  certification — **a better certified UPPER bound** on sup E_a[tau] and better D1,D2,D_lo,C_T".

So the object C9 was chartered to obtain is *a tuple that does not yet exist*. C6 wrote the exact
warning against C9's reading, in bold, twice, and even recorded that C5's adjudicator had already
said the same (`NOT_a_C6_discovery`). C9's B0 audit **read that very entry** — `B0_15` quotes
`C6_classification = GATE_CLASS_GAP__nearest_is_HISTORICAL_REPLAY_REQUIRED` — and then adopted the
label C6 explicitly rejected as the gate's *defect*.

Blocker 1 is therefore not a finding. It is the restatement of C9's own too-narrow scope
definition. "E1 as committed cannot close cell 307" is true only of a reading of E1 that C6, C5's
adjudicator and C8's gate all disclaim.

**To fix.** Restate the finding as what it is — "a byte-faithful replay of the C2 build is worth
1.0000x, which C6 established in 2026-09; C9 confirms it structurally" — and stop treating it as an
independent blocker. Then answer the question actually posed: what configuration of the frozen
certifier delivers ≥ 1.0960072461462x, and is it reachable? See finding 2.

---

## 2. CRITICAL — the lever that closes cell 307 was sitting in C9's own committed inputs, costs zero new CPU, changes no geometry, and was never measured.

**Where.** `p5y_k5_tail_c2_closure/code/c2_refined_registry.py:53` (`TABOO_ALPHAS`), `:95-99`
(first-certifying-rung loop); `p5y_k5_perron_deflated_resolvent/code/taboo_certify.py:190-197`
(`block_proposal`), `:200-239` (`certify_block`), `:242-249` (`block_artifact`);
`p5y_k5_tail_c2_closure/evidence/registry_c2/taboo_block_307_00.json` … `_09.json`
(`margin_lower_bound`). Contradicted text: `README.md` "What a successor needs", item 3 ("**More
CPU does not buy this**"), and `evidence/phase5/C9_TOOLCHAIN.json` `blocker_1_scientific.consequence`.

**The mechanics C9 did not follow through.** The taboo supersolution candidate is *linear in the
ladder rung*: `block_proposal` returns `L1.dyadic_candidate(alpha_s * g + beta_s, n)` with
`beta_s = 0` on the taboo path, i.e. `w = dyadic(alpha * g)`. Everything `certify_block` then forms
is affine in `w`: `k0`, `k1` are linear (`Ops.khat`), `allow` is linear in `sup_w` and `sup_w` is a
sum of absolute coefficients (`rebaseguard_certify/residual.py:328-334`, positively homogeneous),
and `min_max_on_reachable` is a Bernstein enclosure whose bounds scale with the polynomial
(`resolvent_certificate.py:77-88`). Writing `c = alpha_new / alpha_old` and `m` for the recorded
`margin_lower_bound`:

    L_new_min  >=  c * (1 + m) - 1        and    w_min_new = c * w_min_old >= 0

so **any rung with c >= 1/(1+m) still certifies**, and `tau`, `C_T` both scale by `c`. Smaller
`tau` and `C_T` also strictly *improve* `D_lo` (`taboo_certify.py:321-337`: every propagation term
`p0,p1,p2,n0,n1` is monotone increasing in `T` and `Cc`), so holding `D_lo` fixed is conservative.

**The numbers, all read from committed artifacts.** Cell 307 took the **first** rung, `6/5`, on
**all ten** sub-blocks, with recorded margins 0.16089 … 0.16634. C1 did the same (`REGISTRY_C1.json`
cell 307, `taboo_alpha = 1.2`); C2's own pre-freeze review row 48 notes the rung was never varied.

| quantity | value |
|---|---|
| min recorded margin over the 10 sub-blocks | 0.1608913749747931 |
| guaranteed-certifying scale floor `c = 1/(1+m)` | 0.8614070373481011 → **alpha ≥ 1.0336884** |
| `tau` ceiling for closure (`D_lo` held fixed) | 4.4268617281486895 → **alpha ≤ 1.0727330** |

The window is **non-empty**. Explicitly, with `eff_now = 5.5979955104409465`,
`tau_C1 = 4.851872531738208`, `tau_C2 = 4.952056204691856`, `D_lo = 0.866716045536098`,
`Abar = 7.5556132138736665`:

| alpha | c | guaranteed new margin | new `tau_C2` | new `eff` | tightening | closes (≥1.0960072) |
|---|---|---|---|---|---|---|
| 6/5 (as committed) | 1.00000 | +0.160891 | 4.952056 | 5.597996 | 1.000000 | no |
| 11/10 | 0.91667 | +0.064150 | 4.539385 | 5.237453 | 1.068839 | no |
| 27/25 | 0.90000 | +0.044802 | 4.456851 | 5.142227 | 1.088633 | no |
| 107/100 | 0.89167 | +0.035128 | 4.415583 | 5.094614 | 1.098807 | **yes** |
| **21/20** | 0.87500 | **+0.015780** | 4.333049 | **4.999387** | **1.119736** | **yes** |
| 103/100 | 0.85833 | −0.003568 | — | — | — | below the certifying floor |

`alpha = 21/20` clears the frozen closure threshold with **2.1 % of margin on `eff`**, before any
credit for the `D_lo` improvement that must accompany it. Cost: the same ten sub-blocks at the same
`SUB_BLOCK_MAX_WIDTH = 1/100`, the same `DEGREE_TABOO = 20`, the same `depth = 2` — i.e. the same
~31 CPU-minutes C2 already spent on cell 307. **No geometry changes. No new real address. No extra
CPU.** The adoption threshold 1.3700090576827373 stays out of reach by this lever, which is
consistent with C8, but adoption is not the scientific criterion.

Residual caveats I will not hide: the new candidate is re-rounded to dyadic rather than being
exactly `c·w`, worth ~2e-13 against a margin of 1.6e-2; and executing it still needs a host, which
is blocker 2's business. Neither touches the conclusion that the *route* is alive.

**What is wrong, then.** C9's `README.md` tells the successor the opposite of this. It quotes C2's
sub-block refinement as the reference class ("moved `A0` only 4.5–4.9 % while making `tau`
1.90–2.24 % worse"), infers "a further halving is a much smaller step than that one, and 8.76 % is
required", and concludes "**More CPU does not buy this**". That is a correct statement about the
*expensive, weak* lever and it is used to discourage the *free, strong* one. The alpha rung is
named in passing in `blocker_1_scientific.consequence` ("or a different alpha ladder") and then
dismissed unquantified, in a campaign that had already read the margins it needed — Phase 1
reconstructed the whole cell-307 clause, Phase 4 walked the producer's module graph, and every
`taboo_block_307_*.json` was in scope. This is work C9 could have done with no toolchain, no host,
no authorization and no guard change, and it inverts the handover.

**To fix.** Compute the rung window as above from the committed `margin_lower_bound` fields; publish
it as the Phase 5 result; replace item 3 of "What a successor needs" with a pre-registerable ladder
extension (e.g. taboo rungs `23/20, 11/10, 27/25, 21/20, 1043/1000` appended below `6/5`, frozen
before any run) and the statement that the required 1.096x lies inside the certified feasibility
window C8 already published (`Lambda_floor` 3.734070 against `eff` 5.597996, headroom 1.4993x).

---

## 3. MAJOR — the determinism claim is false as written, and it makes the two "independent" blockers dependent.

**Where.** `code/c9_toolchain.py:42-43` → `C9_TOOLCHAIN.json` `blocker_1_scientific.why[2]`: "the
arithmetic is exact (fractions.Fraction) plus flint.arb interval arithmetic at a fixed precision,
**so the output is a deterministic function of the inputs**". Repeated in `README.md`.

**What is wrong.** Exactness applies to the *certification*, not to the *candidate*. The candidate
comes out of a float pipeline: `taboo_certify.py:90` `np.polynomial.legendre.leggauss`, `:109`
`np.einsum`, `:196` `np.linalg.solve`, then `cusum_layer1.py:67-86` `dyadic_candidate`, which itself
runs a `np.linalg.solve` on a Chebyshev–Vandermonde system before rounding at `scale_bits = 50`.
The certified outputs `(C_T, tau, D_lo, D1, D2)` are rigorous *bounds for whatever candidate came
out of that float path*, so they are reproducible only relative to a fixed numpy/BLAS/architecture.

That matters here specifically, because blocker 2's own `architecture_note` says the only machine in
sight is macOS/arm64 while the pins point at Linux. On a differing float stack the payload — and
hence the certified tuple — can differ without a single byte of source changing. So
`C9_TOOLCHAIN.json` `independence` ("blocker 1 holds even if a fully qualified host existed, because
the committed producer would reproduce the committed result") is unproven precisely in the scenario
blocker 2 describes. The two blockers are not independent; blocker 2's premise undermines blocker
1's.

(The drift would be ulp-scale and cannot deliver 8.76 %. The conclusion survives; the stated reason
does not.)

**To fix.** Say "deterministic given an identical float toolchain; the certification is rigorous
either way", and drop the independence claim or restate it as "blocker 1 holds on a bit-identical
replay host".

---

## 4. MAJOR — "the committed registry records the exact configuration it was produced under, so the reproduction is checkable field by field" — the check was never run, and C9's own two artifacts disagree.

**Where.** `code/c9_toolchain.py:32-34` and `:44-45`; `C9_TOOLCHAIN.json`
`blocker_1_scientific.same_configuration_recorded_in_the_committed_registry.code_sha256`;
`C9_FORENSICS.json` `entry_producer.sha256`.

**What is wrong.** Two hashes for the same file, in two C9 evidence files, never reconciled:

- registry-recorded `code_sha256.c2_refined_registry` = `4ac24d9e182656a4…`
- the file on disk at C9 HEAD = `0d1d8021a3780e13…` (C9's own forensics records this)

`c9_toolchain.py:32-34` pulls `code_sha256` out of the registry into `recorded` and then **never
compares it to anything**; the claim "checkable field by field" is asserted, not performed. The same
lines ask for a `bits` key the registry does not have, so the "fixed precision" claim silently rests
on nothing C9 read — `BITS = 256` lives in `taboo_certify.py:56`, a file `c9_toolchain.py` never
opens.

I ran the check C9 did not. The registry was built at `e71378a0` (`4ac24d9e`); the producer was
edited twice since, `e9c230d3` and `2b045564`, and both diffs are confined to `verify()` and the new
`--out` flag — the `build` path is untouched. So the scientific claim survives, **by luck, not by
verification**. Note also `c2_refined_registry.py:177` writes `sha(HERE.read_bytes())` into every
new registry, so a rebuild today cannot reproduce `REGISTRY_C2.json` byte-for-byte regardless.

**To fix.** Compare the recorded and actual hashes, and when they differ, diff the versions and state
that the delta is verify-only. Three lines of code; it is the check C9 claimed to have made.

---

## 5. MAJOR — "reproduces the committed cell-307 block EXACTLY" is false in the sha-checkable sense this programme uses everywhere.

**Where.** `C9_TOOLCHAIN.json` `blocker_1_scientific.finding`; `README.md` first line of Blocker 1.

**What is wrong.** Every sub-row carries `cpu_seconds` (`c2_refined_registry.py:117`, embedded at
`:158`), and so does every certificate (`taboo_certify.py:235`, `:347`). The registry then pins
`taboo_artifact_sha256` and `denominator_artifact_sha256` over those bytes (`:107`, `:113`), and the
verifier compares them (`:205`, `:211`). A re-run reproduces every *scientific* field and **no**
artifact hash. In a campaign whose B0 audit is built on blob shas, "EXACTLY" is the wrong word, and
C9's own cited verifier would have flagged it.

**To fix.** "reproduces every certified quantity; only timing fields and therefore artifact hashes
differ."

---

## 6. MAJOR — C9 inventoried the wrapper's CLI and called it the science's CLI.

**Where.** `code/c9_toolchain.py:24-25` (scrapes `add_argument` lines from `c2_refined_registry.py`
only) → `C9_TOOLCHAIN.json` `why[1]`: "the CLI exposes only `--outdir, --cells, --workers, --out` —
none of which is scientific".

**What is wrong.** True of the 100-line orchestration wrapper; false of the certifier that does the
work. `taboo_certify.py:369-377` exposes `--lo --hi --alpha (default 27/20) --beta --depth --degree
--full --out` as first-class CLI parameters, and `:378-384` the same for `cell`. `--alpha` is
exactly the knob finding 2 turns on. C9 stopped its scan one module short of the frozen science and
concluded "no scientific knob exists".

**To fix.** Scan the transitive graph C9's own Phase 4 already resolved (13 modules, `C9_FORENSICS.json`
`module_graph`) for exposed parameters, not just the entry point.

---

## 7. MAJOR — no C9 charter, gate or protocol is committed; the stop's entire authority is unverifiable prose.

**Where.** `README.md` ("The charter is explicit: *document the blocker, do not improvise around
it*"), `STOP_RECORD_C9.md` ("The charter hard-stops that fired", with two block quotes),
`C9_TOOLCHAIN.json` `charter_hard_stops_triggered`. Against:
`git ls-files level4/closure_proofs/p5y_k5_tail_c9_e1_cell307/{config,protocol,review}` → **0 files**;
all three directories exist and are empty.

**What is wrong.** Every predecessor froze and committed its gate — C2 `config/FEASIBILITY_GATES_C2.json`,
C8 `config/DECISION_GATE_C8.json` — and C9's own `B0_06` verifies C8's gate blob against its freeze
sha `55e74332…`. C9 froze nothing. A reviewer cannot check the scope clause "one authorized execution
of the committed E1 producer", cannot check "do not improvise around it", and cannot check the
hard-stop list that the campaign says fired. Given finding 1, **the scope definition is the single
load-bearing fact of this campaign**, and it exists only as quoted prose inside the artifacts it
justifies.

**To fix.** Commit the charter as a frozen, hashed `config/` artifact, and have the stop record cite
its sha, exactly as `B0_06` does for C8.

---

## 8. MAJOR — blocker 2 proved its governance half and overstated its technical half.

**Where.** `C9_TOOLCHAIN.json` `blocker_2_toolchain_and_host.network_state`, `.hosts.local_machine`;
`code/c9_toolchain.py:82-90` and `:107-123`; `code/c9_common.py:137-140`.

**What stands.** No C9 host authorization artifact exists (`authorized_C9_host_artifacts: []`,
`C9_authorization_artifacts_present: []`), AWS is out of scope, and Vultr's historical use is not
authorization. C6 already ruled host provisioning "a separately governed prerequisite ... requiring
the user's decision — not a campaign's". The honest correction of the earlier `c9`-in-hex-digest
false positive (`c9_toolchain.py:92-98`) is good work. **This half alone is sufficient to bar
execution**, and I am not disputing it.

**What does not stand.**

- `c9_common.toolchain_present()` probes only the **running** interpreter (3.14.5).
  `c9_toolchain.py:85-87` separately discovers `/Users/suzhe/.local/bin/python3.11`. The two results
  are never joined. I checked, read-only: that 3.11.15 has `pip`, `venv`, and a **working** CA bundle
  at `/private/etc/ssl/cert.pem`, while the 3.14 framework build's `openssl_cafile`
  (`…/Versions/3.14/etc/openssl/cert.pem`) **does not exist**. So `network_state`'s "this interpreter
  cannot verify TLS certificates ... so package installation is not currently possible **from it
  either**" is a per-interpreter misconfiguration reported as a fact about the machine, and it was
  never re-tested on the interpreter C9 itself found.
- `hosts.local_machine` asserts FLINT 3.6.0 must be installed and that "brew does not pin FLINT to
  3.6.0". That assumes FLINT must come from the system. python-flint ships binary wheels that carry
  their own FLINT, which is how the pinned pair (python-flint 0.9.0 / FLINT 3.6.0) appears *together*
  in the committed evidence C9 tabulated. C9 never checked, and `brew` is present on this machine.
- "A Homebrew install is system-wide and shared, so it is NOT the *dedicated* environment" conflates
  the interpreter with the environment: a venv is dedicated by construction, and C9's own pin table
  records the precedent — `"uv-managed CPython 3.12.3 (main, Apr 15 2024...)"` — in
  `historical_pins_from_committed_evidence.python`.

None of this authorizes an install, and I am not recommending one. But "qualification is not
possible" was reported where "qualification was not attempted, and provisioning is governed" is what
the evidence supports.

**To fix.** Either test the one interpreter that could plausibly host a venv and report the result,
or state plainly that the technical route was not explored *because* provisioning is governed — and
do not dress the second as the first.

---

## 9. MINOR — the C2 gate is over-read as programme-wide immutability.

**Where.** `C9_TOOLCHAIN.json` `blocker_1_scientific.gate_language` ("...and fixes both alpha
ladders") and `.consequence` ("a source mutation of a geometry the C2 gate froze");
`STOP_RECORD_C9.md` "What was deliberately NOT done".

**What is wrong.** `FEASIBILITY_GATES_C2.json` → `D_stage_design_fixed_now` states its own purpose:
"these designs are fixed before any C2 certification runs, **so that no partition or supply is
chosen after seeing which one closes a cell**", and records the ladders as "taboo (6/5, …) and ARL
(5/4, …), **as in C1**; first certifying rung taken". That is a prospective anti-tuning freeze
binding **C2**, plus an inherited default nobody ever optimised. It is not a finding that 6/5 is
minimal, and it does not bind a successor that pre-registers a lower rung *before* running — which
is precisely what C2 itself did. C9 was right not to edit a constant mid-campaign; it was wrong to
present a successor's prospective re-freeze as a gate violation.

---

## 10. OBSERVATION — the arithmetic checks out, and it is the cleanest this tail has shipped.

Independently reproduced from `REGISTRY_C1.json` / `REGISTRY_C2.json` / `C8_ADOPTION.json`:

- `eff = min(Abar 7.5556132138736665, min(tau_C1 4.851872531738208, tau_C2 4.952056204691856) /
  D_lo 0.866716045536098) = 5.5979955104409465` — matches `C9_PHASE1.json` and C8's `A_now.A0`
  exactly, and the componentwise MIN/MAX supply rule is as documented.
- Γ `+0.026354631323170525` vs C8's `0.026354631323170518` → 6.9e-18, as C9 claims.
- closure `1.0960072461461898` and adoption `1.3700090576827373` both match
  `C8_ADOPTION.json` `per_cell.307` exactly, are carried as **distinct** fields, and the
  `DISTINCTION` note forbidding substitution is correct and well placed.
- `required_new_eff_for_closure 5.107626368461312 = eff / 1.0960072461461898` ✓;
  `largest_uniform_scaling 4308700056021123253937347/4722366482869645213696000 = 1/closure` ✓;
  `M_now 3.374598931694219`, `M_needed_C5T 3.114961360548343`, `M_R2 5.335183825031916` ✓.
- All four evidence files' self-`sha256` recompute under `c9_common.write_evidence`'s rule (4/4).

The Phase 1 reconstruction is genuinely independent (it imports no C8 module) and it is the part of
C9 a successor should keep unchanged.

---

## 11. OBSERVATION — scope discipline is clean.

`git diff --stat 63a3f825..HEAD` = 12 files, all additions, all under
`level4/closure_proofs/p5y_k5_tail_c9_e1_cell307/`. No predecessor byte changed; C2–C8 trees verified
identical to their published heads by `B0_16`. No `K5_COVERAGE_MAP_R6` anywhere (`B0_11`); r5 remains
authoritative. No `authorization/` directory, no guard `ALLOW` anywhere in the tree (`B0_19`), guard
never left DENY. Cells 306/308/309 appear only as declared non-targets and as a C8-sourced
`NON_TARGET_DIAGNOSTIC`; no address of theirs was evaluated. `origin` is
`https://github.com/flaggielover/ReBaseGuard.git`, so `B0_03`/`B0_18`'s `ls-remote` are genuine remote
queries and not the local-clone trap. `AWS_CONTACTS: 0` is consistent with everything in the diff and
with the code, which makes no network call beyond `git`.

---

## Summary

The *action* C9 took — do not provision a host and do not run a certification — is defensible on
finding 8's governance half alone, and that half is correctly established. Nothing here says C9
should have executed.

But C9 stopped the **campaign**, not just the execution, and it did so on a blocker it built itself
(finding 1) supported by four claims that do not hold as written (findings 3–6), with no committed
charter to check the scope that makes the blocker work (finding 7). Worst, it stopped *one cheap
step short of the answer*: the margin fields in its own inputs show a rung window
`alpha ∈ [1.0337, 1.0727]` that closes cell 307 at the same geometry, the same degree and the same
CPU cost, against a required 1.0960072461462x — and C9's handover instead tells the successor
"More CPU does not buy this" and points at the expensive lever (finding 2). That analysis needed no
toolchain, no host, no authorization and no guard change. It was available at Phase 1 and it
reverses the campaign's conclusion about the route.

A wrong STOP costs what a wrong GO costs. This one shipped a "useful negative" that is, on the
campaign's own committed evidence, a positive.

VERDICT: STOP_PREMATURE
