# FC2 specification: grant-scoped band admission (guard and verifier variant)

This specification implements protocol rev. 2b §7 (a)–(d). Two **independent** implementations follow it:
* the producer-side guard, `FNS/code/p309_guard.py`, written by the coordinator;
* the verifier variant, `FNS/verify/srk_verify_indep_granted.py`, written by the independent verifier's author from
  this spec and the original verifier. The original verifier is left unchanged.

FNS = `level4/closure_proofs/p5y_k5_cell309_p309_r1/`. The research verifier `RNS/verify/srk_verify_indep.py` (sha
a32d5d39…) is **not modified**.

## 1. Band tables (compiled constants; never read from input)

| geometry (h, k) | band (and mirror) | role |
|---|---|---|
| (5, 1/2) | [6/5, 13/5] and [−13/5, −6/5] | the **real** quarantine band (the research quarantine, unchanged) |
| (3, 1/2) | [3/2, 7/4] and [−7/4, −3/2] | the **test** band, a synthetic geometry used only for sandbox positive-path qualification. It is disjoint from every declared h = 3 decoy (e ≤ 33/32) |

A certificate (or a guarded drift interval) **meets a band** if its block or weight block intersects the band or its
mirror, for its geometry. Geometries not in the table have no band.

## 2. Grant context

| field | real band (5, 1/2) | test band (3, 1/2) |
|---|---|---|
| repository | **the repository containing the implementing file** (resolved from `__file__`; never a parameter) | a sandbox repository path passed by the caller |
| grant file | `FNS/authorization/P309_GRANT.json`, **committed at HEAD** (read with `git show HEAD:<path>`) | `<sandbox>/<test grant path>` committed at the sandbox HEAD |
| marker ref | `refs/p5y-k5-cell309-p309-r1/target-consumed` (hard-coded) | a test marker ref name passed by the caller; it must start with `refs/p309-test/` |
| cell | the grant's `cell` must be 309 | the grant's `cell` must be the string `TEST` |

**Official-mode admission** of a band-meeting certificate or interval requires **all** of the following. Anything else
is a REFUSE, with a reason that starts with `quarantine:`.
1. The grant file exists at HEAD and parses as JSON with `schema` = `P309_GRANT/1`, the expected `cell`, and
   `drift_hull_Ew` = [lo, hi] as exact rational strings with lo < hi.
2. `git rev-parse HEAD` equals the commit that added the grant file (the grant commit is HEAD), and the marker ref
   resolves to that same commit.
3. The block **and** the weight block of the certificate (or the guarded interval) lie inside Ew. For a certificate,
   the weight block must equal Ew exactly.
4. The geometry equals the grant's geometry: (5, 1/2) for the real band; (3, 1/2) for the test band.
5. (Verifier only.) The grant's `verifier_id` equals `sha256:` + the sha256 of the verifier variant's own file bytes.

**Review mode** (verifier only; post-seal re-verification) additionally admits a band-meeting certificate when both
hold:
* the marker names the grant commit, and a commit whose parent is the grant commit adds the sealed result file
  `FNS/evidence/execution/P309_RESULT.json`;
* that sealed result lists the certificate's sha256 under `stage1a.certificates`.

In review mode HEAD may differ from the grant commit. Nothing else is admitted in review mode.

## 3. Dry admission (no evaluation)

Both implementations expose `admission_decision(...) -> (decision, reason)`, with decision ADMIT or REFUSE. It
evaluates **only** the rules above: parsing, git metadata, rational comparisons. It never evaluates the kernel. It is
what sandbox tests use for the **real** band, so that no in-band real-kernel quantity is ever computed before a grant.

## 4. Verifier variant behaviour

* **Outside every band:** identical to the original verifier, bit-for-bit in verdicts and reasons. This is checked in
  QC16 on the full decoy suite and the v2 batteries.
* **Band-meeting and not admitted:** REFUSE at parse time (the reason starts with `quarantine:`); nothing is
  evaluated.
* **Band-meeting and admitted:** verified exactly like any other certificate (the same mathematics). Positive paths
  are qualified **only** with the test geometry.
* **Probes:** the variant never constructs probes. Harness probe construction uses a band check against **its own
  compiled copy of the band tables above**, never against any lifted or grant-scoped list (§7(c)).

## 5. Guard behaviour (`p309_guard`)

* `guard_interval(geometry, lo, hi, ctx)`: an interval meeting a band is refused unless admitted (§2). Other
  intervals are allowed.
* `producer_adapter(ctx)`: returns an object with the `q309_guard` API that the pinned producer calls
  (`guard_drift`, `log_execution`). Band drifts are admitted only per §2. The driver installs it in place of
  `srk_certify.Q` **in execute mode only**. Everywhere else the research `q309_guard` stays in force.
* Without a grant, every band-meeting interval is refused. In this stage no grant exists.
