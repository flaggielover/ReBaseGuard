# PROPOSED route amendment r4 — erratum E1: bounded revision-5 development repair semantics

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Prepared 2026-10-15 after the independent revision-4 code review.
This is an additive clarification of the proposed Linux development contract. Amendment r4 and all earlier drafts
remain byte-unchanged, including every original accepted quotation. **A formal route / governance review must read
`PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4.md` together with this erratum E1.** For the proposed assessment and input
boundaries identified below, this erratum supplies the additional semantics to be reviewed; it changes no accepted
rule.

`new_target_evaluations = 0` · `cell309_activity = none`. All **20 D-* decisions in r4 §4 remain undecided**.
No host is selected. This erratum grants no operational, designation, qualification, freeze, grant, S1 or target
authority. Preparation of this text is not independent review or acceptance of the development implementation.

## 1. Source, scope and evidence status

The preserved independent source is `reviews/REVIEW_CLOUD_R1_DELTA_R4_CODEX_CODE.md`, reviewed input
`aef3bead293759e0e4cc1af26e0c01f060bb9abc`, preserved with the review artifacts at
`64c0909d0ae4c14fd09cbb34ca9e4a72eae3fc98`. Its SHA256 is
`0940ed8f9c6d581b4cfc0a6707239bf25dec420cd98d187e21c2c6c2c52d8fa3`. The report returns **NOT_FAIL_CLOSED** and records
five bounded findings F1–F5 about individual evidence-producing APIs. It demonstrates no whole-preflight false PASS
or native Linux reproduction. Its default preflight remains blocked by open decisions.

The following is the intended narrow **development revision-5** repair contract for
`streams/CLOUD_R1_LINUX_DEV/lx_platform.py`. It describes required behavior, not proof that a code change implements
it. **Exact-input Linux baseline, regression/mutation evidence and fresh independent follow-up review of revision 5
remain pending.** No revision-5 test count, mutant count, passing run or code-closure verdict is asserted here. Any
revision-4 test result applies to its own inputs and cannot discharge these findings or establish revision-5 behavior.

The scope is confined to observed clock/counter evidence and recognised proc/snapshot input schemas. No theorem,
scientific input, criterion, member, WORKERS value, cap, rule output, accepted measurement definition, threshold or
owner decision is changed. In particular, `SLEEP_GAP_TOL_NS` stays **2,000,000,000 ns (2 s)** and
`MAX_SAMPLE_GAP_S` remains unchanged. This text neither chooses D-PAUSE nor establishes Linux/macOS measurement
equivalence.

## 2. Effective proposed L-SLEEP assessment — F1 and F2

Read r4 §3 L-SLEEP and §12 P3 with these additional requirements. The observation sequence is
`[start, *samples, end]`, in its recorded order. Existing schema, sample-order/coverage, boot, power and journal
requirements remain. Missing, malformed or unrecognised evidence cannot yield CLEAN.

**F1 — every observed clock interval is checked.** For **every adjacent pair** in that sequence, and independently
for the **start-to-end pair**, calculate the changes in MONOTONIC, BOOTTIME and REALTIME using recognised nonnegative
integer nanosecond readings, excluding bool. Apply the existing checks and the same 2 s tolerance to each pair:

* Non-increasing MONOTONIC or BOOTTIME adds AMBIGUOUS evidence.
* BOOTTIME change minus MONOTONIC change greater than 2 s adds CONTAMINATED evidence (K′).
* That difference less than −2 s adds AMBIGUOUS evidence.
* The absolute difference between REALTIME change and MONOTONIC change greater than 2 s adds AMBIGUOUS evidence (P).

Endpoint realignment cannot erase a reason observed between adjacent readings. The tolerance comparisons remain
strict: equality with the existing tolerance alone does not fire a divergence check. P remains an ambiguity signal,
not a pause detector; a hypervisor pause invisible to guest clocks remains the unresolved D-PAUSE limitation.

**F2 — every suspend-counter observation is used.** Every sequence member must carry a recognised nonnegative
integer `suspend_success`, excluding bool. Compare each adjacent pair. The S′ channel applies this precedence:

1. Any malformed or absent counter yields AMBIGUOUS evidence.
2. Otherwise, any adjacent decrease or reset yields AMBIGUOUS evidence. An inconsistent counter sequence cannot
   establish contamination through that channel.
3. Otherwise, any increase yields CONTAMINATED evidence; an unchanged sequence contributes no counter reason.

Equal endpoints cannot erase intermediate counter evidence. In particular, `0 → 1 → 0` yields S′ AMBIGUOUS only,
because the decrease makes that counter sequence inconsistent; the intermediate increase is not accepted as a valid
contamination proof from the same channel.

Reasons from the independent channels remain accumulated. The existing aggregate classification applies: any valid
CONTAMINATED channel reason makes the interval CONTAMINATED, including an independent positive channel when S′ is
AMBIGUOUS; otherwise any AMBIGUOUS reason makes it AMBIGUOUS. CLEAN is possible only if every required channel is
available and no reason fires. No journal reader has
been established by this erratum: r4's L′ availability limitation remains, as do boot-change and power checks at
every reading.

## 3. Effective proposed proc-view completeness — F3 and F4

Read r4 §3 L-EXCL and §12 P5 with these input-boundary requirements for `proc_view_complete`:

* **F3:** the sole accepted `/proc` mount candidate must have recognised positive numeric mount and parent IDs and
  recognised numeric, nonnegative `major:minor` device metadata. Retain the existing complete mount-record shape,
  separator, root `/`, mountpoint `/proc`, proc-filesystem, unique-candidate and unrestricted-option requirements.
  Unrecognised mount headers cannot establish a complete view.
* **F4:** the status record must contain **exactly one NSpid field**, with exactly one recognised positive integer
  token. Missing, malformed or duplicate fields cannot establish completeness. Duplicate fields are refused even
  when identical; contradictory duplicates are refused in either order. The existing initial-PID-namespace check
  remains mandatory.

Absent/unrecognised readings and positively restrictive or ambiguous views remain unavailable/refused according to
the existing failure-state distinction; they never return a complete view. A caller cannot rely on a favourable
first line while ignoring a malformed or conflicting later line. This is a strict supplied-record boundary, not a
claim that native Linux normally emits malformed mount headers or duplicate NSpid fields. L-EXCL still refuses when
the proc view is not established as complete.

## 4. Effective proposed exclusivity snapshot identity — F5

Read r4 §3 L-EXCL and §12 P1 with this additional requirement for `busy_processes`: **each CPU snapshot separately
contains at most one identity per PID**. Two `(pid, starttime)` keys for the same PID in either t0 or t1 make that
snapshot ambiguous and return **no reading**, before campaign ownership or child exemptions are evaluated.

PID reuse across two different snapshots is still representable. A child exemption still requires the exact parent
identity in the applicable snapshot to belong to the campaign, with the existing child-start ordering check. An old
campaign parent key cannot establish ownership when that same snapshot also asserts a conflicting reused identity.
Recognised external births retain all-ticks charging, exits retain unknown-usage reporting, invalid arithmetic or
counter regression remains no reading, and no name/path allowance is introduced. No reading cannot establish
exclusive host use or a passed gate. No exclusivity window or threshold is chosen; D-EXCL-WINDOW, D-ALLOW-PATHS and
D-ALLOW-BASE39 remain open.

## 5. Validation and continuing conditions

| Preserved finding | Narrow required regression / control | Evidence status |
|---|---|---|
| F1 | transient REALTIME and BOOTTIME divergence in a middle observation, with realigned endpoints; aligned sequence control; adjacent and endpoint checks use the same existing tolerance | revision-5 exact-input Linux validation and independent review pending |
| F2 | counter sequence `0 → 1 → 0`, recognised decrease/reset and increase; unchanged-counter control | revision-5 exact-input Linux validation and independent review pending |
| F3 | unrecognised mount/parent/device metadata refused; recognised single unrestricted proc-mount control | revision-5 exact-input Linux validation and independent review pending |
| F4 | duplicate NSpid fields in both orders and identical duplicates refused; exactly one valid field/token control | revision-5 exact-input Linux validation and independent review pending |
| F5 | two identities for one PID in either snapshot return no reading; valid forward PID reuse still reports the external child | revision-5 exact-input Linux validation and independent review pending |

Bind validation to the resulting immutable revision and actual imported source/test/harness hashes. Require a
passing exact-input baseline before interpreting mutations, preserve command/interpreter/environment provenance and
per-mutant behavioral attribution, and retain invalid-run classification for unrelated errors, skips and timeouts.
A synthetic repair result supplies no native lifecycle, hardware, storage or provider guarantee.

All r4 integration and authorization conditions remain, including A1's verified current-host attestation provenance,
A2's live launcher corroboration and reviewed restrictions on injected seams/configuration, and A5's fixed complete
science import list and independently reviewed pin-point wrapper in every computing mode. The non-holder reference
addendum with record/strip/serializer digests must remain part of the text the formal review accepts before OD-3.
The fixed interpreter/toolchain, no-repeat/no-host-shopping rules, conservative D-RC2-SCOPE treatment, fresh S12 and
all governing sequence gates remain. Neither this erratum nor later development validation accepts r4/E1 or decides
any owner option. Current work remains target-free development and review only.
