# DIRECT / HIGH-PARTIAL candidate audit

No DIRECT work was found. Every HIGH-PARTIAL work is audited below from abstract at minimum; access limits are retained.

## W01 — Self-Starting Cusum Charts for Location and Scale

**Evidence:** ABSTRACT · **DOI:** `10.2307/2348827`

- **1. Exact problem:** Self-starting location/scale CUSUM when in-control parameters are unknown.
- **2. What is selected by stopping:** No; the running estimates use all observations since startup, before any alarm selection.
- **3. Data reused:** Past startup observations enter running mean/scale estimates and standardized future CUSUM inputs.
- **4. New reference/baseline:** Yes, continuously estimated in-control parameters, but not from an alarm-stopped batch.
- **5. Affects next cycle:** No post-alarm next cycle is described in the inspected abstract.
- **6. Repeated:** No evidence of repeated alarm/re-baseline cycles.
- **7. Local derivative/stability:** No reference-map derivative or local fixed-point stability analysis.
- **8. m>1 window:** No ReBaseGuard convention-A stopped finite window.
- **9. rho stability:** No.
- **10. SR:** No.
- **11. General score theorem:** No stopped-score identity.
- **12. Subsuming theorem:** No theorem found that subsumes C3-C9.
- **13. Required claim change:** Do not describe recursively estimated/self-starting CUSUM references as new; specify alarm-stopped post-alarm reuse.

## W03 — Adaptive CUSUM procedures with EWMA-based shift estimators

**Evidence:** ABSTRACT · **DOI:** `10.1080/07408170801961412`

- **1. Exact problem:** Adaptive CUSUM for good detection across unknown mean-shift sizes.
- **2. What is selected by stopping:** No evidence that the EWMA estimator's observations are selected by a completed alarm.
- **3. Data reused:** Streaming observations update an EWMA shift estimate that sets the current CUSUM reference value.
- **4. New reference/baseline:** Yes, an adaptive within-run reference value.
- **5. Affects next cycle:** It affects later increments in the current chart; no post-alarm reference cycle is shown.
- **6. Repeated:** No repeated alarm-selected re-baselining established.
- **7. Local derivative/stability:** Run-length analysis, not a local derivative of a cross-cycle reference map.
- **8. m>1 window:** No.
- **9. rho stability:** No.
- **10. SR:** No.
- **11. General score theorem:** No.
- **12. Subsuming theorem:** No load-bearing ReBaseGuard theorem is subsumed.
- **13. Required claim change:** Forbid broad claims that adaptive CUSUM reference updating is introduced here; retain only the stopped post-alarm cross-cycle distinction.

## W05 — Continuous monitoring for changepoints in data streams using adaptive estimation

**Evidence:** ABSTRACT · **DOI:** `10.1007/s11222-016-9684-8`

- **1. Exact problem:** Continuous changepoint monitoring using adaptive forgetting factors over multiple change sizes.
- **2. What is selected by stopping:** Unclear from accessible abstract; the estimator is described as continuously adaptive, not alarm-stopped.
- **3. Data reused:** Streaming observations update forgetting-factor estimates used for detection.
- **4. New reference/baseline:** An adaptive state/estimate is formed; an alarm-selected baseline is not established.
- **5. Affects next cycle:** Continuous monitoring is supported, but a discrete post-alarm reference cycle is not specified in accessible evidence.
- **6. Repeated:** Multiple changes are the use case; exact alarm-reset mechanics were inaccessible.
- **7. Local derivative/stability:** No ReBaseGuard stopped-score derivative/local phase boundary in accessible evidence.
- **8. m>1 window:** No ReBaseGuard random-window theorem.
- **9. rho stability:** No.
- **10. SR:** No.
- **11. General score theorem:** No.
- **12. Subsuming theorem:** No evidence of a subsuming theorem.
- **13. Required claim change:** Do not claim continuous detector-estimator feedback or adaptive forgetting as new.

## W06 — Quasi-stationary biases of change point and change magnitude estimation after sequential cusum test

**Evidence:** ABSTRACT · **DOI:** `10.1080/07474949908836432`

- **1. Exact problem:** Bias of change-point and change-magnitude estimates after a sequential CUSUM detects a Brownian-drift change.
- **2. What is selected by stopping:** Yes; inference is conditioned on the change being detected by the CUSUM stopping rule.
- **3. Data reused:** The stopped detection path is used to estimate change point and magnitude.
- **4. New reference/baseline:** No evidence that the estimate becomes a monitoring reference.
- **5. Affects next cycle:** No.
- **6. Repeated:** No recursive repeated-monitoring feedback.
- **7. Local derivative/stability:** Bias asymptotics, not a reference-map derivative or stability result.
- **8. m>1 window:** No.
- **9. rho stability:** No.
- **10. SR:** No.
- **11. General score theorem:** No ReBaseGuard stopped-score derivative identity.
- **12. Subsuming theorem:** No.
- **13. Required claim change:** General stopping-induced post-alarm estimation bias is prior art; claims must target its recursive reuse consequence, not the existence of bias itself.

## W08 — Estimation of Change-point and Post-change Parameters after Adaptive Sequential CUSUM Test in an Exponential Family

**Evidence:** FULL-TEXT · **DOI:** `10.5539/ijsp.v5n5p43`

- **1. Exact problem:** Adaptive sequential CUSUM with recursive post-change parameter estimation and conditional post-detection bias in an exponential family.
- **2. What is selected by stopping:** The final change-point/post-change estimates are evaluated after the alarm; within-run estimators are updated before the alarm. An unknown pre-change mean is updated when subtests cross downward, not after the alarm threshold.
- **3. Data reused:** Observations within candidate post-change segments update the CUSUM's adaptive parameter; the stopped path yields reported post-alarm estimates.
- **4. New reference/baseline:** Within-run shift parameters and, in one subsection, a pre-change estimate across downward-reset subtests are formed. Alarm-triggering observations do not become a next alarm cycle's reference.
- **5. Affects next cycle:** It affects subsequent subtests before the first alarm, not a post-alarm monitoring cycle.
- **6. Repeated:** Subtests repeat until one alarm; the paper stops at that alarm and does not analyze repeated post-alarm re-baselining.
- **7. Local derivative/stability:** No cross-cycle reference-map derivative, fixed-point stability, or period-2 certificate.
- **8. m>1 window:** No convention-A terminal-window theorem or short-cycle correction.
- **9. rho stability:** No reuse-fraction phase boundary.
- **10. SR:** Adaptive SR is cited, but the studied procedure is CUSUM.
- **11. General score theorem:** Uses exponential-family likelihood/renewal theory, not C8's stopped accumulated-score identity.
- **12. Subsuming theorem:** No theorem subsumes C3-C9.
- **13. Required claim change:** Adaptive CUSUM estimation, recursive unknown-baseline updates across negative subtests, and post-detection bias are established; current wording must isolate post-alarm alarm-sample reuse and its derivative/stability consequences.

## W10 — Nonanticipating estimation applied to sequential analysis and changepoint detection

**Evidence:** FULL-TEXT · **DOI:** `10.1214/009053605000000183`

- **1. Exact problem:** Sequential tests and SRRS changepoint detection with unknown post-change parameters estimated nonanticipatingly.
- **2. What is selected by stopping:** No post-alarm sample is selected for a next baseline; estimators are predictable from observations before each current likelihood-ratio factor.
- **3. Data reused:** Past observations in each putative post-change segment estimate parameters used in later likelihood ratios.
- **4. New reference/baseline:** Adaptive post-change likelihood parameters are formed, not a post-alarm in-control reference.
- **5. Affects next cycle:** They affect the same detection run; the full paper does not feed alarm-stopped estimates into a later cycle.
- **6. Repeated:** No reference-coupled repeated alarms.
- **7. Local derivative/stability:** No reference feedback derivative/stability map.
- **8. m>1 window:** No.
- **9. rho stability:** No.
- **10. SR:** Yes, an SRRS procedure with estimated unknown post-change parameter.
- **11. General score theorem:** General parametric estimation is present, but not C8's location-score covariance identity.
- **12. Subsuming theorem:** Its ARL/delay theorems do not subsume C3-C9.
- **13. Required claim change:** Adaptive/unknown-parameter SR cannot be claimed as introduced; C7 must remain the derivative identity for the frozen reference-reuse map.

## W14 — An Adaptive Shiryaev–Roberts Procedure for Signalling Varying Location Shifts

**Evidence:** ABSTRACT · **DOI:** `10.1080/03610918.2014.906611`

- **1. Exact problem:** Adaptive SR chart for varying unknown future location shifts.
- **2. What is selected by stopping:** No evidence in the inspected abstract that the adaptive reference is estimated from a completed alarm's stopped sample.
- **3. Data reused:** Streaming data drive an adaptive reference/shift estimate in the active chart.
- **4. New reference/baseline:** Yes, an adaptive within-chart reference value.
- **5. Affects next cycle:** It affects later states of the same two-dimensional Markov chart; a post-alarm next reference is not shown.
- **6. Repeated:** No alarm-selected repeated reference cycle established.
- **7. Local derivative/stability:** Markov run-length performance, not the local derivative of a reference map.
- **8. m>1 window:** No.
- **9. rho stability:** No.
- **10. SR:** Yes.
- **11. General score theorem:** No.
- **12. Subsuming theorem:** No theorem found that subsumes C7.
- **13. Required claim change:** Avoid any claim that adaptive SR reference values are new; state the stopping-selected post-alarm feedback and derivative identity precisely.

## W25 — Learning from Time-Changing Data with Adaptive Windowing

**Evidence:** ABSTRACT · **DOI:** `10.1137/1.9781611972771.42`

- **1. Exact problem:** Online concept-drift detection and learning with a statistically adaptive window.
- **2. What is selected by stopping:** Partly: window cuts are triggered by a change test over the current window, not by a CUSUM/SR alarm stopping time.
- **3. Data reused:** The retained recent portion of the tested window supplies future estimates/model updates.
- **4. New reference/baseline:** Yes, a new adaptive window/state for future learning and detection.
- **5. Affects next cycle:** Yes in practical repeated streaming operation, though not as a discrete stopped sample-mean reference cycle.
- **6. Repeated:** Yes, the window is recomputed online repeatedly.
- **7. Local derivative/stability:** False-positive/negative guarantees, not local deterministic reference-map stability.
- **8. m>1 window:** No ReBaseGuard convention-A theorem.
- **9. rho stability:** No.
- **10. SR:** No.
- **11. General score theorem:** No.
- **12. Subsuming theorem:** No load-bearing theorem is subsumed.
- **13. Required claim change:** Practical change-triggered adaptive reference windows are prior art; claims must not imply otherwise.

## W33 — A Self-Starting CUSUM Chart Combined with a Maximum Likelihood Estimator for the Time of a Detected Shift in the Process Mean

**Evidence:** ABSTRACT · **DOI:** `10.1002/qre.1511`

- **1. Exact problem:** Self-starting CUSUM detection followed by MLE estimation of detected shift time.
- **2. What is selected by stopping:** Yes; the path is selected by a CUSUM alarm, and the estimator is applied after detection.
- **3. Data reused:** Alarm-path data, and optionally extra post-alarm observations, estimate the change time.
- **4. New reference/baseline:** No evidence that the estimate defines the next in-control reference.
- **5. Affects next cycle:** No.
- **6. Repeated:** No recursive post-alarm monitoring feedback in the abstract.
- **7. Local derivative/stability:** No.
- **8. m>1 window:** No.
- **9. rho stability:** No.
- **10. SR:** No.
- **11. General score theorem:** No.
- **12. Subsuming theorem:** No.
- **13. Required claim change:** Post-alarm reuse of a CUSUM path for retrospective estimation is known; distinguish reuse to form a future monitoring reference.

