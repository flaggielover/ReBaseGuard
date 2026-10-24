# Formal route / governance review FR1: Cell-308 MB-S new-host route, Cloud r1

## 1. Header

- Reviewer: reviewerFR1 (fresh agent, brief FR1)
- Date: 2026-10-16
- Pinned commit: `29d79e7045e36c71fa1f30c03d83e92be8a58006` (detached worktree `tree_29d79e70`; branch
  `codex/cell308-claude-r5-integration`, draft PR #3)
- Eligibility statement: `scratch/ELIGIBILITY_AND_EXPOSURE_FR1.md` (recorded by the coordinator at `6b3aac20`, a commit
  after the pinned one, which I have not read).
- NS = `level4/closure_proofs/p5y_k5_cell308_research/`. File:line references are to the pinned tree unless stated.
  "amd" = `NS/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md`; "pkt" =
  `FORMAL_ROUTE_READINESS_PACKET_20261016.md`; "add" = `PROPOSED_LDET_REFERENCE_ADDENDUM_R1_20261015.md`; "lsp" =
  `LDET_SPECIFICATION_PACKET_20261016.md`; "hep" = `HOST_EVIDENCE_PLAN_H1_H8_20261016.md`; "hap" =
  `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_20261016.md`; "s12" = `S12_RISK_REVIEW_BRIEF_DRAFT_20261016.md` (all in the
  same directory); "rA1" = `NS/registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md`; "rE1"/"rE2" its errata; "gov" =
  `NS/governance/SUCCESSOR_GOVERNANCE_308.md`; "gA1" its addendum A1; "gE1" the A1 erratum; "rat" =
  `NS/governance/CONSTANTS_RATIFICATION_MBS308.md`; "bR2" = `NS/governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`;
  "reg" = `NS/governance/SUCCESSOR_CONDITIONS_REGISTER_308.md`; "lxp" =
  `NS/streams/CLOUD_R1_LINUX_DEV/lx_platform.py`.

Scope integrity: the sha256 of all eight scope files at 29d79e70 equal the values in brief FR1. The accepted sources'
sha256 equal the prefixes in pkt §2 (pkt:40). Route E2 is `620bfbb9…a5c1` (pkt §2 gives no value for it).

## 2. Exposure disclosure (actual contact during this review)

- **Shared checkout.** I read only the brief there. Every other file was read from the pinned worktree. The
  worktree's git directory is `/home/user/ReBaseGuard/.git/worktrees/tree_29d79e70`, so every git object read went
  through the shared repository's object store. I read no working-tree file of the shared checkout.
- **Files opened (pinned tree):**
  * the eight scope files;
  * owner brief r5, ROUTE_PREPARATION, OWNER_SELECTION, USER_AUTHORIZATION_20261014;
  * the Codex integration supplement and the r71 supplement in full. I grepped r67, r69 and r70 for the cited
    sections only;
  * the accepted sources gov, gA1, gE1, rat, bR2, reg, rA1, rE1, rE2 in full;
  * from `streams/CLOUD_R1_LINUX_DEV/`: a directory listing, and lxp lines 60–116, 700–790, 1026–1145 and
    1165–1555 (read, not imported);
  * the last six ledger lines, truncated to 600 characters each.
- **Candidate source (142d97a9).** I extracted the blobs `mbs308_qualify.py` (`0ac40ba9…`) and `mbs308_driver.py`
  (`80c88355…`) into my scratch directory. I parsed them with Python `ast` only (`python3 -I -B`; nothing imported or
  run). I read these lines:
  * qualify 94, 1109–1114, 1815–1862 (MBR1_RECORD_PINS and nearby pin constants) and 2405–2580;
  * driver 310–355 and 1870–1900.
  None of these lines holds a record value.
- **PR2 line (3b244277), by `git show`, for the A1/A2/A5 trace only:** the headings, the exposure paragraph and
  lines 22–33 of `reviews/REVIEW_CLOUD_R1_DELTA_R3_CODEX_AMENDMENT.md`, plus grep hits in the Codex r4 and its
  erratum E1.
- **History-complete clone.** I made a `--bare --filter=blob:none` clone of github.com/flaggielover/ReBaseGuard in
  my scratch directory. It fetched the commit and tree objects (no blobs) of **every** advertised branch, which may
  include Cell-309 branches. I inspected no Cell-309 object. Every history query was limited to explicit commits
  (142d97a9, 29d79e70, 3b244277) and to the five reference paths. I ran no `--all` query.
- **Ref names.** A `git ls-remote` saved 145 ref lines to a scratch file. Forty-two of them contain "309" somewhere
  (in the name or the hash). I printed no line containing "309": only aggregate prefix counts, and a search for the
  MB r1 marker prefix (0 hits). I deleted the file after use. This is **name-level contact** with the existence of
  such refs, nothing more.
- **Commit subjects.** I printed the one-line subjects (truncated to 150 characters) of the pre-grant commits
  3a05aef7, 29b68d5e, d031dad8, c46434a3, 7eb057bb and afa93072. They name MB r1 qualification and freeze outcomes.
  d031dad8's subject includes Q12 cap figures from the r2 **decoy** qualification. Every one of these commits
  precedes the grant (afa93072, 2026-09-29T20:47+09:00), so none can carry a target-run observation. I reproduce no
  figure here. For 21e99cf0 I printed only its committer date, not its subject.
- **Hashed only (git object read, piped to sha256sum, content never printed):** the five MB r1 r3 qualification
  blobs.
- **Not opened, grepped or hashed:** every item excluded by brief FR1 §EXPOSURE, including
  `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`; any MB r1 postexec or target-run material; Cell-309 content.
- **Not run:** no scientific, candidate, decoy, qualification or L-DET code. I made no call to `attestation_valid` or
  `lx_verified`. I did not run the optional unit tests.
- **Environment contact:** system reminders in my context showed the coordinator session's task list (titles only,
  e.g. "OD-2 formal review FR1, S12 review, readiness dependencies"). This reviewer therefore runs inside the
  coordinator's session environment (see F6 / G27).
- Every git and Python process ran with HOME and GNUPGHOME under my scratch directory. Only commands that touched no
  git or Python process ran without them.
- **Not available to me:** the owner's OD-2 instruction named in brief FR1 line 2
  (`governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261016_OD2.md`) **does not exist at the pinned commit**
  (directory listing; `find -name '*OD2*'` gives no match in that directory).

## 3. Verdict lines

ROUTE_TEXTS: ACCEPTED_WITH_CONDITIONS
LDET_SPEC: ACCEPTED_WITH_CONDITIONS
ATTESTATION_PROCEDURE: NOT_ACCEPTED

**This formal-review verdict brings nothing into force.** Still required:
* the owner's decisions on every [OPEN] item;
* the fresh S12 rating;
* every later gate (OD-1, the host evidence and its acceptance, the reviewed successor build, the implementation
  review, OD-3, the MBS-6/7/8 and S16(c) decisions, S1).

**No D-* item is decided by this review.** My F2 dispositions are advice to the owner. `DECIDED` stays empty. The
verdicts are also subject to G12: the owner's OD-2 text is not in the pinned commit.

ROUTE_TEXTS is ACCEPTED_WITH_CONDITIONS, not ACCEPTED, because of the MAJOR findings G1–G8 and G11. The texts are
honest in their labelling overall. However:
* they leave the route-level effect of acceptance undefined (G1);
* they invite a rating below an accepted floor (G2);
* they misorder three dependencies (G3, G5, G11);
* they contain one mechanism that cannot work as specified (G7).

ATTESTATION_PROCEDURE is NOT_ACCEPTED. Its pass rule ("all three agree", hap:57–60) has no specified procedure for
the external-anchor comparison (G10). Its read basis (commit C) conflicts with L-LIFE (HEAD) on where the veto is read
(G9). A revised text needs a fresh review before D-HOST-LIFETIME can be put to the owner.

## 4. Required findings F1–F8

### F1. Accepted versus proposed

**Verbatim check.** Each [ACCEPTED] quotation below was compared with its source. Differences of line wrapping,
emphasis and ellipsis were ignored; there are no other differences.

| quotation (location) | source | result |
|---|---|---|
| HOST row (amd:51–53) | rA1:40 | verbatim |
| RC2 "Determinism is conditional on RC2…" (amd:188–190) | rA1:22–24 | verbatim |
| MBR1_REPRO (amd:192–196; add:33–34; lsp:50–51) | rA1:64–68 | verbatim |
| DR2 no-update sentences (amd:62–63) | rE1:57–58 | verbatim |
| "not settled" (amd:198) | bR2:439 | verbatim |
| S5, S7, S10 (amd:254–256, 258–260, 282–284) | gov:109–111, 118–120, 125–126 | verbatim |
| S13 in full (amd:263–269) | gA1:148–153 | verbatim |
| E1 D2, D3 (amd:271–277) | gE1:33–34, 42–48 | verbatim |
| S15 sentence (amd:181; pkt:132) | gA1:161 | verbatim |
| S12 (s12:10–12) | gA1:145–147 | verbatim |
| MBS-5(b) (amd:36–37; s12:14–15) | bR2 §4 item 5 (lines 146–147), rE2:18 | verbatim |
| R-FREE quantity (pkt:97; amd:165) | rat:58–59 | verbatim |
| R-MEM step 5 (pkt:98) | rat:49–50 | verbatim (fragment) |
| R-MEM step 1 "under the launchd launcher" (amd:179) | rat:39 | verbatim |
| item 15 (pkt:123) | rat:21 | verbatim with ellipsis |
| rows 24 and 25 (pkt:99, 106) | rat:29, 30 | correct |
| R-EXCL-PCT, R-ALLOW (pkt:115–117) | rat:65–80 | correct paraphrase/quote |
| EVAL_CAP basis (pkt:109; amd:174) | bR2:254 | verbatim |
| [PREPARATION] quote (amd:158–160) | ROUTE_PREPARATION:41 | verbatim |
| incident-review N1–N4 and T1 (amd:239–244) | `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md` | **UNVERIFIED by FR1** (excluded file, G38) |

**Proposal presented as accepted, or source class overstated:**

* **bR2 is cited as [ACCEPTED] for start-gate rows.** Examples: "Thermal pressure level 0" (pkt:105; amd:168), and
  the AC, Low Power Mode and Memory rows. bR2 is a decision brief by briefer2. Its §9 table is sourced from "protocol
  draft §4–§8 (at `216c465f`), the ratified constants, governance S17 and route E1 DR2" (bR2:402). The thermal gate in
  particular exists in no accepted rule text; it is a protocol-draft gate. pkt §2 (pkt:40) classes bR2 ACCEPTED "as
  quoted [ACCEPTED] by amendment r5", which is circular. **G13.**
* **amd §1 (amd:29–34) and §4 disagree.** §1 says "no change … is proposed" to "every number of R-MEM, R-FREE,
  R-EXCL-PCT and R-ALLOW". §4's options and pkt §4's recommendations change the measured quantities, remove
  R-EXCL-PCT's exception, drop R-ALLOW's base set and add numbers (30 s, N = 3). Every one of these is labelled in
  §4, so this is a wording conflict, not a hidden change. **G35.**
* **amd §1 lists "the members" as Unchanged [ACCEPTED]** (amd:31). Whether the members stay unchanged is the open
  owner decision MBS-7 (reg:34; bR2 §5). The amendment presupposes MBS-7 (i) without saying so. **G3.**

**Accepted requirement weakened:**

* **The rating floor.** pkt:88 says the route is rated "HIGH unless S12 states otherwise", and s12:61–62 asks for "HIGH,
  or a rating with stated mitigations". Under the recommended reading of D-RC2-SCOPE the science is "changed" under
  S4, which is the condition of trigger T1 (amd:243–244). rE2:17–18 makes triggers escalate the rating to HIGH. A
  rating below HIGH would then contradict accepted text. **G2.**
* **D-EXCL-WINDOW's exit rule** (pkt:115) turns an unknown into a possible pass, unlabelled. **G8.**
* **Attestation substitutions** (D-LPM, D-POWER-ABSENT, D-PAUSE (2), D-S15-NEWHOST (2)) replace a measured gate with an
  owner statement. Each is labelled "amends", but none is labelled as a change of evidentiary class. **G20.**

Nothing else weakens an accepted requirement. The case-set addition, comparison (b), H3's vector list, D-ALLOW-BASE39
and D-ALLOW-PATHS are all stricter. The labels in pkt §4 are checked under F2.

### F2. The 21 D-* recommendations

The dispositions are in the table of §5. The label check, by item:

* **D-ALLOW-PATHS "Amends nothing" is wrong.** R-ALLOW (b)'s literal path list includes `/usr/sbin/` and `/sbin/`
  (rat:75), and both exist on Linux. Read literally on Linux, R-ALLOW (b) would auto-allow a busy `/usr/sbin` daemon.
  "None" therefore amends R-ALLOW (b) (stricter). **G14.**
* **D-WORKERS-CORES "Reading only" is wrong.** Making ≥ 6 online CPUs a host requirement is a **new host
  requirement**. Item 15 (rat:21) is a rationale for EXCL_CPU_PCT, not a requirement. **G15.**
* **D-THERMAL "amends the brief row".** There is no accepted thermal rule to amend; it is a new rule replacing a
  protocol-draft gate. **G13 / G19.**
* **D-INTERPRETER and D-PIN-POINT.** pkt §4 omits amd §4's labels "new pin" and "new pin rule" (amd:178, 183).
  **G37.**
* **D-EXCL-WINDOW.** Two new rules are unlabelled: the exit-charge rule and the start-gate re-read. **G8.**
* **D-LPM, D-POWER-ABSENT, D-S15-NEWHOST.** The attestation fallbacks are new rules as well as amendments. **G20.**
* **The rest** are labelled correctly: D-MEM-FREE, D-MEM-WIRED, D-MEM-PRESSURE, D-PAUSE, D-ALLOW-BASE39, D-CAPS-CPU,
  D-TEXT-LAUNCHD, D-ID-ZOMBIE, D-HOST-LIFETIME, D-LDET-REPEAT, D-LID (the readiness checklist is candidate code, not an
  accepted text; the label is correct as stated) and D-RC2-SCOPE (a reading; see G1).

The count is right: pkt §4 holds exactly 21 ids, equal to `OPEN_DECISIONS` (lxp:86–112), and `DECIDED` is empty
(lxp:79).

### F3. Host-selection criteria

Each requirement is classed by the support it has in accepted text:

| criterion | support | class |
|---|---|---|
| the owner can disable every update vector for the whole window | rE1 DR2 (rE1:55–60) | **accepted** (the vector list in H3 is proposed) |
| one machine for every step (H1, H8) | rA1 HOST row; bR2 §9 host row ("this host only") | **accepted in substance**. "Not paused / reclaimed" and DMI identity are proposals |
| a launcher that survives the hosting app's and its parent's death (H2) | gov S6 (gov:113) | accepted. "systemd PID 1" is the proposed means |
| durable, fsync-honouring persistence (H5) | gov S6 | accepted. The reboot-survival check is proposed |
| no other heavy compute, including other sessions (H4) | gA1 S17 (gA1:174–175) | accepted |
| a readable memory allowance for R-MEM / R-FREE (H6) | rat R-MEM, R-FREE | accepted in substance. "No hidden cgroup ancestor" and its attestation are proposed |
| operator access for resume within 7 days (H7) | rat items 18, 19 | accepted |
| ≥ 6 online CPUs | rat item 15 rationale only | **proposal** (G15: count physical cores, not logical CPUs) |
| readable thermal zones | D-THERMAL | **proposal** |
| bare metal or dedicated, no hypervisor pause | D-PAUSE | **proposal** |
| PSI available | D-MEM-PRESSURE | **proposal** (implied, not listed in pkt:187) |
| DMI `product_uuid` | H8 | **proposal** |
| network reach to the canonical GitHub remote at every preflight | D-S15-NEWHOST (1) | **proposal, unlisted** (and see G7) |

**Minimum before an inventory is worth taking** (derived from the accepted rows above; a "no" on any one makes the
inventory pointless):
1. One persistent machine under the owner's control, not a provider-managed session image.
2. The owner can disable every update vector, including image changes and automatic reboot, from no later than the
   L-DET interpreter build to the 7-day deadline (G5).
3. systemd as PID 1, and the campaign can run as a service with no agent session on the machine during the window
   (G28).
4. A local persistent disk.
5. A memory allowance that is the machine's own: no container runtime, initial cgroup namespace.
6. Exclusivity can be arranged.
7. Operator access within the window.
8. A hardware-bound identity, or a stated substitute.

The proposal-level preferences come after that: ≥ 6 physical cores in the unit's cpuset, PSI, readable thermal zones
with passive trips, bare metal.

**Architecture** (x86_64 or arm64) is not a criterion in any text. Choosing it before L-DET is a legitimate owner
choice, because no result exists yet. It must be fixed in OD-1 and never changed after an L-DET outcome (amd §5 item
7).

### F4. Reproduction semantics

**Case set.** L-DET's case set equals MBR1_REPRO's (amd:207–208 vs rA1:64–66). The QC04 serial block-0 record
(lsp §2) is an addition beyond the accepted set. It is stricter, and it is in the candidate's `MBR1_RECORD_PINS`
(qualify 1823–1839) and full-form `mbr1_repro` (qualify 2549–2579). I endorse including it, labelled as a new rule,
fixed before OD-3.

**Comparison.** The candidate's `_compare` (qualify 2467–2469) is structural: `va == vb` on `json.loads` trees. Under
that comparison:
* floats compare as doubles;
* `True == 1` holds;
* `-0.0 == 0.0` holds.

The proposed (a) exact-rational plus (b) canonical-byte comparison (lsp:33–40) is stricter on each point and changes
no science. The two halves have opposite holes:
* (b) `_canon` returns a string, so a Decimal leaf and the string of its text serialise identically;
* (a) maps an fs-grammar string and a number of equal value to the same Fraction.

The conjunction closes both holes. The spec must therefore state that MATCH requires **both**, and that neither is
ever used alone. **G21.**

**fs grammar** (driver 317–319). `fs` writes `f"{x.numerator}/{x.denominator}"` of a normalised `Fraction`. Every fs
string therefore contains "/", integers appear as `n/1`, the denominator is positive, and gcd = 1. The (a) conversion
must accept **only** the regex `^-?(0|[1-9][0-9]*)/[1-9][0-9]*$` with gcd = 1. `Fraction(str)` alone would also accept
"0.5", " 3/4 " or "2/4". **G21.**

**Control.** `_planted` perturbs a number by +1. On Decimal-parsed leaves (not `int`/`float`) it falls through to
`str(v) + "#planted"`, a type change. No control tests exactness (a change of the rational that keeps the double).
**G22.**

**Non-vacuity floor.** The floor (lsp:38) needs the reference records to be parsed. Brief FR1 bars this reviewer from
opening them, so the floor is **UNVERIFIED** and needs an eligible named agent. **G23.**

**MBR1_REPRO versus L-DET.** rA1 §3 places MBR1_REPRO in the successor's **qualification**, at the frozen commit. L-DET
runs earlier, on a build that the later apply step changes (pkt §6 items 8–9; ROUTE_PREPARATION steps 5–7). The texts
do not say whether the qualification's own MBR1_REPRO still runs, or whether it would count as a "repeat" under
D-LDET-REPEAT. **G4.**

**Reference provenance**, confirmed on a history-complete clone (blob:none, value-free):

* All five blobs are first introduced on the candidate line by `7eb057bbbcb3c8d18afc852c1d90f0b3fc0fefc8`
  (2026-09-29T19:22:35+09:00). Its subject reads "official qualification at freeze r3 c46434a3: PASS", which confirms
  that these are the r3 records.
* Ancestry: `c46434a3` is an ancestor of `7eb057bb`, and `7eb057bb` is an ancestor of `142d97a9` and of `21e99cf0`.
* Neither `29d79e70` nor `3b244277` has any commit touching the paths.
* No change to the five paths in `7eb057bb..142d97a9`.
* At `7eb057bb`, `21e99cf0` and `142d97a9` the blobs are identical.
* Recomputed sha256 of all five blobs equal add:38–42. So do the two code blobs (add:62–63).

**Not disclosed by the addendum:** the same five paths held two earlier generations of records:
* blobs added at `3a05aef7` (qualification at the freeze-r1 commit `a7fe3028`, FAIL) and deleted at `29b68d5e`;
* blobs added at `d031dad8` (qualification at freeze r2, FAIL) and deleted **by freeze r3 `c46434a3` itself**.

add:47 ("none of the five paths exists at c46434a3") is true but incomplete. This confirms that reads must be by blob
id (lsp:33). **G29.**

**Source bindings.** All 16 `source_sha256` values (add:71–86) recompute exactly with `ast.get_source_segment` under
CPython 3.13.16. That is the definition actually used; the add's "exact source segment" should say so. **G30.**
`source_sha256` as the binding digest is endorsed (lsp:95).

**Interpreter.** The D-INTERPRETER recommendation (a source-built CPython) is **incompatible with the L-PIN reader as
specified**. `_python_packages` (lxp:1070–1088) uses `dpkg -S` on the executable. A non-dpkg interpreter yields
`UNKNOWN_PACKAGE`, and `pin_mismatches` (lxp:1137–1142) then never matches. Separately, with no dpkg package nothing
pins the pure-Python stdlib (e.g. `fractions.py`, `json/`). **G6.**

**Accepted RC2 pins** (rA1:61–63). The accepted list includes libpython sha256. L-PIN covers it only implicitly:
through the mapped objects for a shared build, or through the executable for a static build. **G24.**

**D-RC2-SCOPE.** The cumulative reading (pkt:88) is consistent with rA1 §1 and the HOST row: a different host means
the changed branch, and exact reproduction is required. It states only that a match is **necessary**. It does not say
what discharges the HOST row, so acceptance has no defined effect on the HOST row status. **G1.**

### F5. Attestation trust assumptions

**What is sound and honest:**
* reading git tree paths and blob contents only (hap:9–19, matching r70 T6);
* the explicit statement that in-repository checks are defence in depth (hap:68–83, review 67 N7);
* the requirement of a non-coordinator, non-holder, owner-appointed reviewer (hap:25–35).

**What is missing or conflicting:**
1. **Read basis.** hap reads every fact at the acceptance commit C (hap:16–18). L-LIFE and `attestation_valid` read at
   HEAD, with a history-wide veto (lxp:1409–1462, 1508–1550). Read at C, a rejection committed after C is outside the
   read. Rejections must be read at HEAD and across HEAD's whole history; C fixes the accepted bytes only. **G9.**
2. **External anchor.** "A gate passes only if all three agree" (hap:57–60), but no step says who compares the anchor
   with the repository, at which official steps, or where the comparison is recorded. preflight cannot read the
   anchor. **G10.**
3. **Integrity of the review bytes.** The reviewer's file is committed by the coordinator. `review_sha256` is
   recomputed "by an agent other than the reviewer" (hap:54–55), which may be the coordinator. Nothing binds the
   committed bytes to what the reviewer wrote. The reviewer's own digest should reach the owner directly. **G26.**
4. **Self-asserted fields.** The schema fields `reviewed` and `accepted` (hep:49–50; lxp:1538) must be true in the
   **owner's** attestation blob before any review exists, so the attestation asserts its own acceptance. **G26.**
5. **H2 / H5 evidence ordering.** The acceptance evidence for H2 (a "reviewed procedure" dry launch) and H5
   ("durable-write tests of the reviewed implementation") (hep:41, 44) needs the reviewed build. In the dependency
   list that build comes after the attestation acceptance (pkt §6 items 5–7). **G11.**
6. **Codex supplement outdated.** The supplement (Codex supplement:17) says the veto is HEAD-only. The current
   development code has a full-history veto (`_historical_review_blobs`, lxp:1336–1373). The texts do not reconcile
   this. **G34.**

**What cannot be established in-repository, correctly stated:** reviewer identity, honesty, and a history rewrite with
new ids. hap adds a trust assumption that the check runs "on a host the owner controls". That host is the official
host, which is the attested object itself, so the check is circular for H1/H8. This should be stated.

### F6. Reviewer independence

* **Acceptance reviewer (hap §2).** The eligibility rules are adequate in content. "Appointed by the owner, by name"
  needs a definition for an agent reviewer, which has no persistent identity: the brief text, the session or agent id,
  and the owner's record of both. The coordinator's appointment is **not sufficient** for this role, by hap's own
  terms.
* **S12 reviewer (s12 §2).** The rules are adequate in content. The option "appointed by the formal route / governance
  reviewer under the owner's delegation" (s12:29) is **not sufficient**. A formal reviewer that is an agent ends with
  its report and cannot hold or exercise a delegation. The owner should appoint.
* **Formal route reviewer (this role).** Brief FR1 says the coordinator appoints me under the owner's OD-2
  instruction. That instruction is **not in the pinned commit**, so its scope and any delegation are **UNVERIFIED**.
  **G12.**
* **Independence of this reviewer.** Freshness is self-declared. I run inside the coordinator's session environment:
  shared object store, a scratch directory the coordinator can read and write, and its task list visible. The
  coordinator wrote the brief that frames my scope. This is sufficient for a bounded formal review only if the owner
  adopts it knowingly. **G27.**
* **Self-declared holder status.** E1″ holder status cannot be checked by any reviewer barred from
  `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`. The holder list is named there (gA1:148–149).
* **The addendum compiler.** The compiler's non-holder status (add:12–19) is self-declared. The remedy in lsp §4, an
  independent re-derivation, is **done here** for provenance (F4). The list is now independently confirmed by FR1 from
  `MBR1_RECORD_PINS` and the history.

### F7. Progression authority

**Class errors in the readiness matrix** (pkt §3):
* row 7 (A5) is BLOCKED (on row 14, the successor build), not UNMET;
* row 10 (official host) is BLOCKED on OD-1;
* row 13 (comparison semantics) is OPEN_DECISION: a rule is missing, not evidence;
* row 18(c) and row 19 (MBS-6/7/8) are OPEN_DECISION (owner decisions; reg:29, 33–35), not UNMET;
* row 1 mixes MET and UNMET; for the official host it is BLOCKED on OD-1.

**Missing dependencies:**
* rows 14 and 16 omit row 9 (S12). ROUTE_PREPARATION step 2 puts the fresh risk assessment before step 3, and s12 Q4
  asks about L-DET, so the rating should precede OD-3;
* MBS-7 must precede OD-3 (G3).

**Ordering errors in the dependency list** (pkt §6):
* MBS-7 is placed after L-DET (item 9). bR2:47–48 says "MBS-7 comes first in effect", and (ii) would change the object
  L-DET tests (G3);
* the H2/H5 acceptance evidence precedes the reviewed build (G11);
* the platform window (H1/H3/H8, pins) starts at the designated series or qualification, after L-DET (G5).

**Authority.** The authority column is correct except:
* row 4's "formal reviewer" holds no authority beyond advice;
* every R + O item is in effect O, because only the owner can bring a rule change into force;
* the appointing authority for every role should be the owner (F6).

S14 (row 17) is MET only per reg:27. The commits `a40211cc`, `9ad632c9` and `e451e634` are not objects of this
repository (they are absent from the full clone), so S14 is **UNVERIFIED** here. **G33.**

### F8. Other findings

* **G1: the S4 instrument.** gov S4 (gov:106–108) requires "a route audit (Phase 3)" to decide a changed branch. The
  amendment never says whether its acceptance is that route-audit decision, or how the HOST row's EXCLUDED status
  changes.
* **G7: D-S15-NEWHOST (1) cannot work as written.** `git ls-remote` of the canonical remote on 2026-10-16 advertises
  **no** ref under `refs/p5y-k5-cell308-mb-r1/` (0 matches among 145 refs). Mechanism (1) would therefore refuse at
  every preflight, or tempt someone into pushing formal refs.
* **G28: option V-A.** The recommended V-A (pkt:187) puts Claude sessions on the official host. That conflicts with
  S17 (no other session's compute) and MBS-3 / route E2 L6 (no in-run observation) unless no session runs there from
  the marker to the seal.
* **G36: the PREPARATION instruction.** ROUTE_PREPARATION:19 instructs "Do not change … measurement rules or
  thresholds to accommodate the cloud". Many D-* recommendations change measurement rules (labelled). The owner must
  expressly set that instruction aside for each one.
* **G32: restart count.** hep:20 says the container restarted three times. Inventory r3 (`observed_in_this_session`)
  records two.

## 5. F2 dispositions of the 21 D-* items (advice; nothing is decided)

| # | id | disposition | change, reason, or what the owner needs (pkt line) |
|---|---|---|---|
| 1 | D-RC2-SCOPE | ENDORSE_WITH_CHANGES | Keep the cumulative reading (pkt:88). Add the **sufficient** conditions for "RC2 discharged there": an L-DET MATCH; the pins at the L-DET pin point; those pins re-verified unchanged at every later computing step; the qualification's own MBR1_REPRO (G4); and the no-update window from the L-DET build (G5). Replace "HIGH unless S12 states otherwise" with "not lower than HIGH" (G2). The owner adopts the reading. |
| 2 | D-INTERPRETER | CANNOT_ASSESS_WITHOUT_HOST | Fact needed: whether CPython 3.14.5 builds from the official tarball, with recorded flags, on the named host's toolchain and glibc / libm. Procedure changes now: (i) replace the dpkg package pin for a non-dpkg interpreter with the build-provenance record plus a sha256 manifest of the installed prefix (`lib/python3.14/**`, `lib-dynload`) (G6); (ii) fix the build before any decoy or L-DET run, and never change it after an L-DET outcome. |
| 3 | D-PIN-POINT | ENDORSE_WITH_CHANGES | The static closure must include stdlib and C-extension modules reached by the science (e.g. `fractions`, `decimal`/`_decimal`, `json`, `math`, `multiprocessing`). The pin must be taken (or verified identical) **in every worker process** after its imports. A post-job check must refuse when a shared object was mapped after the pin point (G24). The list can be fixed only once the successor build exists (pkt:90). Label it "new pin rule" (G37). |
| 4 | D-LDET-REPEAT | ENDORSE_WITH_CHANGES | Keep "no repeat" (pkt:91). Add: any later owner ruling to resume on the same platform after a non-completion is a post-result decision. It requires a fresh S12 re-rating and a fresh formal review with the failed attempt in view, as amd §5 item 7 already requires for a new host. |
| 5 | D-MEM-FREE | ENDORSE_WITH_CHANGES | Option (d) is acceptable as a new measure, labelled "amends R-FREE" (pkt:97). Withdraw "most conservative of the Linux analogues": MemFree + Inactive(file) (option b) can be lower than MemAvailable. If maximal conservatism is intended, use min((a), (b), (c)). Define the chain as the campaign unit's cgroup and all its ancestors, read from inside the unit. Numeric only with H6 attested. The owner must approve the R-FREE amendment. |
| 6 | D-MEM-WIRED | ENDORSE_WITH_CHANGES | `memory.current` does not exist for the cgroup-v2 root, and on the recommended bare-metal host the chain may have no limit. Define idle usage for that case (e.g. MemTotal − MemAvailable in the prepared state) and say which cgroup's usage is meant (G18). Labelled "amends R-MEM step 5" correctly. |
| 7 | D-MEM-PRESSURE | ENDORSE | PSI `some avg10 = 0.00` × 3 readings 30 s apart, start gate only; labels correct (pkt:99). Also label `avg10` and `0.00` as new parameters. A host must have PSI enabled (some kernels boot with `psi=0`), which becomes a host criterion (F3). |
| 8 | D-THERMAL | ENDORSE_WITH_CHANGES | Define the rule for a zone with no passive trip point (only critical / hot). State whether hwmon sensors (e.g. coretemp) count. Relabel: a **new rule**; the thermal gate has no accepted text, only the protocol draft as described in bR2 §9 (G13, G19). |
| 9 | D-LPM | ENDORSE_WITH_CHANGES | `powersave` is the **normal** governor under `intel_pstate` / `amd-pstate` active mode, so the rule as drafted fails ordinary hosts or invites a settings change. Key the rule on `scaling_driver` plus the energy-performance preference (`power`) and `platform_profile`. Label the attestation fallback as a measurement replaced by a statement (G16, G20). |
| 10 | D-POWER-ABSENT | ENDORSE_WITH_CHANGES | Accept the server rule only for a host whose inventory shows no supply entries **and** a non-portable DMI chassis type. Label it as a measured AC gate replaced by an owner statement (G20). The boot-id → CONSUMED_INTERRUPTED rule is unchanged (pkt:107). |
| 11 | D-LID | ENDORSE_WITH_CHANGES | Derive "host without a lid" from the inventory (DMI chassis type), never from assumption. The readiness checklist is candidate code (`mbs308_qualify.py` 338–341), not accepted text; the label is accurate as stated (pkt:108). |
| 12 | D-PAUSE | ENDORSE_WITH_CHANGES | (1) `CLOCK_MONOTONIC` stops in system suspend on Linux. This is correct, and the amendment of EVAL_CAP's basis is labelled. (2) Prefer **bare metal only**. If the attestation route is kept, label it a statement replacing an undetectable fact (G20). (3) Unchanged (pkt:109). |
| 13 | D-EXCL-WINDOW | ENDORSE_WITH_CHANGES | The 30 s window and "hosting app = none" are acceptable (pkt:115). The exit rule "charged its last observed ticks" is **not an upper bound**: a process seen at t0 with few ticks that burns CPU and exits before t1 would pass. Keep exited ⇒ unknown ⇒ refuse, or charge `dt × 100 %` (G8). Make the start-gate re-read a labelled new rule, with a pre-registered maximum count and every reading recorded. |
| 14 | D-ALLOW-PATHS | ENDORSE_WITH_CHANGES | "None" is endorsed, but it **amends R-ALLOW (b)** (stricter): the literal list includes `/usr/sbin/` and `/sbin/` (rat:75) (G14). |
| 15 | D-ALLOW-BASE39 | ENDORSE | Drop the 39 macOS names; stricter; "amends R-ALLOW" is correct (pkt:117). |
| 16 | D-WORKERS-CORES | ENDORSE_WITH_CHANGES | Relabel as a **new host requirement** derived from item 15's rationale. State it in **physical cores in the campaign unit's effective cpuset** (≥ 6), not online logical CPUs: SMT siblings count as CPUs on Linux (G15). WORKERS unchanged. |
| 17 | D-CAPS-CPU | OWNER_RESERVED | MBS-8 is the owner's choice (bR2 §6; reg:35). The owner needs: (i) the bR2 §8 sequencing answer; (ii) the official decoy runtimes on the named host under the reviewed launcher (non-holder, decoys only, S3/S13); (iii) Q12's result under option (i) on that host. A recommendation for (ii) is acceptable advice. L-DET runtimes stay excluded (amd §5 item 9). |
| 18 | D-TEXT-LAUNCHD | ENDORSE_WITH_CHANGES | Also list the other texts that name launchd: bR2 §6 MBS-8 (ii) ("under its launchd launcher", bR2:241) and rat items 30–31 (launchctl timeouts). Label "amends R-MEM step 1 and those texts". |
| 19 | D-ID-ZOMBIE | ENDORSE | No: a zombie proves nothing; current fail-closed behaviour; amends nothing (pkt:131). |
| 20 | D-S15-NEWHOST | ENDORSE_WITH_CHANGES | Mechanism (1) cannot pass as written: the canonical remote advertises no `refs/p5y-k5-cell308-mb-r1/*` ref (G7). Specify (a) the authoritative store that holds the formal refs (the owner's Mac repository?) and how its refs reach the new host value-free (e.g. an owner-signed ref listing); (b) the exact assertion that `refs/p5y-k5-cell308-mb-r1/target-consumed` = `afa930727d084a5b70e6b85d30ca8f34c0e8ae74` is the only ref under the prefix; (c) fail-closed when unreadable. Label (2) a statement replacing a check (G20). |
| 21 | D-HOST-LIFETIME | ENDORSE_WITH_CHANGES | Adopt hap only after G9, G10, G11 and G26 are corrected and the revised hap passes a fresh review (ATTESTATION_PROCEDURE: NOT_ACCEPTED). The appointing authority is the owner. The new schema fields need an implementation review (hap:89–90). |

## 6. Numbered findings

| id | severity | location | finding | required correction |
|---|---|---|---|---|
| G1 | MAJOR | amd §1, §5 (amd:43–53, 200–203); pkt:88; gov:106–108 | Acceptance of the amendment has no stated effect on the accepted HOST row ("EXCLUDED unless RC2 is discharged there"). D-RC2-SCOPE names only a necessary condition. gov S4 requires a route audit to decide a changed branch, and the texts do not say whether this formal review is that audit. | State the conditions that discharge the HOST row (§5 row 1). State that acceptance plus the owner's decision constitutes the S4 route-audit decision for this changed branch, or name the instrument that does. Say what the HOST row reads after acceptance (e.g. "CONDITIONAL: L-DET MATCH plus pins"). |
| G2 | MAJOR | pkt:88; s12:61–62; amd:246–248; rE2:17–18 | "HIGH unless S12 states otherwise" and "HIGH, or a rating with stated mitigations" allow a rating below HIGH. Under the recommended changed-branch reading, T1's condition ("the science is then 'changed' under S4", amd:244) holds by construction, and rE2 escalates triggers to HIGH. | Replace with "not lower than HIGH". Ask S12 whether T1 fires by construction and what mitigations are required at HIGH. Make no lower rating possible without a written finding that T1 has not fired. |
| G3 | MAJOR | amd:31; pkt §6 item 9 (pkt:179); bR2:47–48; reg:34 | MBS-7 (members) is an open owner decision but is presented as unchanged [ACCEPTED], and is sequenced after L-DET. Option (ii) would change the science L-DET tests, and deciding it after an L-DET outcome is a post-result choice. | Move MBS-7 before OD-3 (or state that this route presupposes MBS-7 (i) and requires the owner to record (i) before OD-3). Relabel "the members" in amd §1 accordingly. |
| G4 | MAJOR | amd §5; lsp §0; rA1:64–68; pkt §6 items 8–9 | The relation between pre-freeze L-DET and the accepted MBR1_REPRO at the successor's qualification is undefined. L-DET runs on a build that the apply step changes later. The texts do not say whether MBR1_REPRO still runs at qualification on the frozen commit, or whether that second run is barred as a "repeat". | State that L-DET is an additional pre-gate. State that the accepted MBR1_REPRO still runs at the official qualification at the frozen commit, is not a repeat, and that a mismatch there is STOP. Bind L-DET to a named commit and list which evaluation-path files may differ at the freeze (none on the science path). |
| G5 | MAJOR | amd:76–83 (H1, H3, H8); hep:40–47; pkt §6 | The platform window starts too late. H1 starts "from the designated series", H3 "from qualification", but L-DET precedes both. A platform change between L-DET and the freeze would void the match, and re-running would be a forbidden repeat. The L-DET pins are not declared binding for later steps. | Start H1, H3 and H8 no later than the interpreter build for L-DET. Record the L-DET pins and require every later computing step (designated series, qualification, execute, resume) to match them exactly. Any mismatch is STOP for the platform. |
| G6 | MAJOR | pkt:89; lsp §5; lxp:1070–1088, 1137–1142 | The recommended source-built CPython cannot pass L-PIN as specified: `dpkg -S` finds no owner, `UNKNOWN_PACKAGE` never matches, and the pure-Python stdlib has no pin. | Amend L-PIN for a non-dpkg interpreter: a build-provenance record plus a sha256 manifest of the installation prefix (stdlib and lib-dynload), checked at the pin point. Or choose a distro-packaged interpreter and say so in D-INTERPRETER. |
| G7 | MAJOR | pkt:132; gA1:157–162 | D-S15-NEWHOST mechanism (1) presumes that the MB r1 refs are in "the pushed repository". `git ls-remote` of github.com/flaggielover/ReBaseGuard (2026-10-16) advertises no ref under `refs/p5y-k5-cell308-mb-r1/`, so the assertion would refuse at every preflight. | Name the store that holds the formal refs and a value-free, owner-attested transport of its ref listing. Never push formal refs as a side effect of this route. Re-state the assertion exactly (§5 row 20). |
| G8 | MAJOR | pkt:115; amd:139 (L-EXCL) | The exit rule "charged its last observed ticks" converts an unknown in-window usage into a possible PASS, contrary to amd §2.2's "an unknown is a failure". The unbounded start-gate re-read is an unlabelled new rule. | Keep exited ⇒ refuse, or charge the full window. Label the re-read rule as new, with a pre-registered maximum and full recording. |
| G9 | MAJOR | hap:14–19, 56; amd:146; lxp:1409–1462 | hap reads every fact at commit C, while L-LIFE reads at HEAD with a full-history veto. Read at C, a rejection committed after C escapes the veto, so the two texts conflict on veto scope. | State that the accepted attestation and review bytes are fixed by C, while veto and rejection scans run over HEAD's full history at every check. Require C to be an ancestor of HEAD. Fix one rule in both texts. |
| G10 | MAJOR | hap:57–60, 74–76 | The pass rule requires the external anchor, but no procedure says who compares it with the repository, when (every official step?), how the result is recorded, or what happens if the owner is unavailable. Automated preflight cannot read it. | Specify the anchor check: the owner, or an owner-appointed checker, compares the full commit id with `acceptance_commit` before each official step. The result is recorded in the owner's own record and mirrored in the ledger. Fail closed if absent. |
| G11 | MAJOR | hep:41, 44; pkt §6 items 5–7 | The acceptance evidence for H2 and H5 requires the reviewed implementation and procedure, which do not exist until items 6–7. Attestation acceptance at item 5 is therefore impossible for H2 and H5. | Split acceptance: H1, H3, H6, H7 and H8 at item 5; H2 and H5 after the implementation review; both before OD-3. Reflect this in the matrix. |
| G12 | MAJOR | brief FR1 line 2; pinned tree | The owner's OD-2 instruction (`USER_AUTHORIZATION_20261016_OD2.md`) is absent at 29d79e70. The commission's scope, the delegation of reviewer appointment, and so this review's standing are UNVERIFIED by the reviewer. | Commit the OD-2 text verbatim. The owner confirms that it covers the appointment of reviewerFR1 and the scope of brief FR1, or re-commissions. Until then this review is advice without formal standing. |
| G13 | MINOR | pkt:40, 105–109; amd:168–174; bR2:402 | bR2, a decision brief, is classed ACCEPTED. Its §9 rows describe the protocol draft, and no accepted text holds a thermal gate. | Class bR2 as a reader-checked brief. Cite rat items (4, 24, 25), gA1 S17 or rE1 DR2 where they exist, and "protocol draft (216c465f) as described in bR2 §9" otherwise. |
| G14 | MINOR | pkt:116; amd:171; rat:75 | D-ALLOW-PATHS "None … Amends nothing" is wrong: R-ALLOW (b) literally includes `/usr/sbin/` and `/sbin/`. | Relabel "amends R-ALLOW (b) (stricter)". |
| G15 | MINOR | pkt:123; rat:21 | D-WORKERS-CORES is a new host requirement, not a reading. "Online CPUs" counts SMT siblings, and the macOS host had six real cores (2 P + 4 E). | Relabel it. Require ≥ 6 physical cores in the unit's effective cpuset. |
| G16 | MINOR | pkt:106 | D-LPM's governor test misreads `intel_pstate` / `amd-pstate`, where `powersave` is the normal dynamic governor. | Key on driver, EPP and `platform_profile` (§5 row 9). |
| G17 | MINOR | pkt:97 | "The most conservative of the Linux analogues" is false: (b) can be lower than (a). | Withdraw the claim, or use min((a), (b), (c)). Define the chain. |
| G18 | MINOR | pkt:98 | D-MEM-WIRED is undefined at the cgroup-v2 root and with no chain limit. | Define it (§5 row 6). |
| G19 | MINOR | pkt:105 | D-THERMAL leaves zones without a passive trip, and hwmon sensors, undefined. | Define them (§5 row 8). |
| G20 | MINOR | pkt:106, 107, 109, 132 | Owner or provider attestations replace measured gates (LPM, AC power, pause, the Mac store's S15 state). These are labelled as amendments but not as a change of evidentiary class. | Label each "measurement replaced by owner statement". List them together for the owner and the S12 reviewer. |
| G21 | MINOR | lsp:36–40 | Comparison (a) conflates fs strings with numbers of equal value, and (b) conflates Decimals with strings. Only the conjunction is sound. `Fraction(str)` accepts strings that `fs` never writes. | State that MATCH requires (a) ∧ (b) and that neither may be used alone. Accept only the strict fs regex with gcd = 1 (F4). Have `_canon` emit a JSON number token, not a string. |
| G22 | MINOR | lsp:39; qualify 2472–2490 | The planted control turns Decimal leaves into strings (a type change) and does not probe exactness. | Add a control that changes a leaf's rational value while keeping its double (e.g. append a far decimal digit), which (a) must detect. |
| G23 | MINOR | lsp:38 | The leaf-count floor needs the reference records parsed. No eligible agent is named; FR1 is barred from doing it. | Name an eligible non-holder agent permitted to parse the records and record counts only, before OD-3; or define the floor structurally (> 0 per job and per case, as the candidate does). |
| G24 | MINOR | amd:144; lxp:1026–1051, 1105–1131; rA1:61–63 | Coverage of libpython sha256 (an accepted RC2 pin) is implicit. Workers' mapped objects are unpinned. Objects mapped after the pin point are unchecked. | State the libpython coverage explicitly (a shared build: a required mapped member; a static build: the executable). Pin or verify in every worker. Add a post-job no-new-mapping check. |
| G25 | MINOR | pkt §3 rows 1, 7, 10, 13, 14, 16, 18, 19 | Status classes are wrong (F7), and S12 is missing from the dependencies of rows 14 and 16. | Re-class the rows as in F7. Add row 9 to rows 14 and 16 (and, per G3, MBS-7 to row 16). |
| G26 | MINOR | hap:40–56; hep:49–50; lxp:1538 | The committer (the coordinator) controls the review bytes. The attestation's own `reviewed` / `accepted: true` fields are self-asserted before any review. "By name" is undefined for agents. | The reviewer's digest goes to the owner directly and is recorded in the owner's record. Drop or redefine the self-assertion fields (acceptance lives only in the review, ledger and anchor). Define agent identity as the brief text plus the session or agent id plus the owner's record. |
| G27 | MINOR | brief FR1 lines 3, 7–10; s12:29 | The reviewer is appointed by the coordinator, works in the coordinator's environment, and its freshness is self-declared. s12 lets a formal (agent) reviewer appoint the S12 reviewer. | The owner appoints the S12 and acceptance reviewers. The owner adopts or rejects this review knowingly. Delete the delegation option in s12:29, or restrict it to a named human. |
| G28 | MINOR | pkt:187; gA1:174–176; rE2:13–14 | V-A places Claude sessions on the official host, which risks S17 compute and MBS-3 / L6 in-run observation. | Require that no agent session runs on the host from the marker to the seal, and that none runs during designated or official measurements. Or drop V-A. |
| G29 | NOTE | add:44–53 | The addendum omits that the same paths held r1-qualification blobs (3a05aef7, deleted at 29b68d5e) and r2-qualification blobs (d031dad8, deleted by c46434a3). | Add a sentence; it reinforces reading by blob id. |
| G30 | NOTE | add:65–67 | "source_sha256 = exact source segment" is really `ast.get_source_segment` (verified). | State the function, or use whole-line byte ranges. |
| G31 | NOTE | lsp:34–36 | CPython's int-string digit limit (4300 digits by default) can make `parse_int` or `Fraction(str)` raise on very large rationals. | State the handling: INCOMPLETE fail-closed, or a pinned `sys.set_int_max_str_digits` value. |
| G32 | NOTE | hep:20; inventory r3 | Three restarts in the plan versus two in the inventory. | Reconcile. |
| G33 | NOTE | pkt:70; reg:1, 27 | S14 MET rests on the register, whose header says "status as of 2026-09-29 ~19:35Z", and on ids that are not objects of this repository. | Cite the repository or record holding a40211cc / 9ad632c9 / e451e634, or mark it "MET per register". |
| G34 | NOTE | Codex supplement:17; lxp:1336–1373 | The supplement says rejection is not permanent (a HEAD-only veto). The current code implements a full-history veto. | Reconcile in the next disposition text. |
| G35 | NOTE | amd:29–34 | "No change … is proposed" to the R-rules' numbers conflicts with §4's quantity and base-set changes and new numbers. | Reword to "numbers unchanged; measured quantities, bases and added parameters are [OPEN] in §4". |
| G36 | NOTE | ROUTE_PREPARATION:19, 41 | "Do not change … measurement rules" versus the D-* measurement-rule amendments. | The owner expressly sets the instruction aside per amended rule (line 41 permits putting it to the owner). |
| G37 | NOTE | pkt:89–90; amd:178, 183 | The "new pin" / "new pin rule" labels are missing in pkt §4. | Add them. |
| G38 | NOTE | amd:239–244 | The incident-review quotations are UNVERIFIED by FR1 (excluded file). The Codex amendment review on PR2 (`REVIEW_CLOUD_R1_DELTA_R3_CODEX_AMENDMENT.md` line 27, `3b244277`) reports them verbatim at incident review:129–130 and 207. | None, beyond recording that the verification is that reviewer's, not FR1's. |

## 7. Conditions (for ROUTE_TEXTS and LDET_SPEC: ACCEPTED_WITH_CONDITIONS)

Each condition is checkable against a revised text. Every condition must be met, and the revised texts re-checked by
a fresh bounded review, **before OD-3 is put to the owner**. Conditions 1, 2, 3 and 12 must be met before the S12
review is commissioned.

1. **G12:** the owner's OD-2 text is committed verbatim, and the owner confirms or re-commissions this review's
   appointment and scope.
2. **G1:** the amendment states the sufficient conditions that discharge the HOST row, the HOST row's status after
   acceptance, and the instrument that makes the S4 changed-branch decision.
3. **G2:** every "HIGH unless …" or "a rating with stated mitigations" is replaced by "not lower than HIGH" in pkt §4,
   amd §6 and s12 §4 Q1.
4. **G3:** MBS-7 is placed before OD-3 (or MBS-7 (i) is recorded by the owner as a precondition), and amd §1 no
   longer lists the members as accepted-unchanged.
5. **G4:** the texts state that the accepted MBR1_REPRO still runs at the official qualification on the frozen commit,
   that it is not a repeat, and that a mismatch there is STOP. L-DET is bound to a named commit.
6. **G5:** H1, H3 and H8 start no later than the L-DET interpreter build, and the L-DET pins are binding for every
   later computing step.
7. **G6 / G24:** L-PIN covers a non-dpkg interpreter (provenance plus a prefix manifest), libpython explicitly,
   worker processes, and post-pin mappings. D-INTERPRETER and L-PIN agree.
8. **G7:** D-S15-NEWHOST names the authoritative ref store and a value-free transport. The exact assertion is stated.
9. **G8:** D-EXCL-WINDOW keeps unknown ⇒ refuse (or a full-window charge), and the re-read rule is labelled, bounded
   and recorded.
10. **G21–G23:** lsp §1 requires (a) ∧ (b), uses the strict fs regex with gcd = 1, emits number tokens in (b), adds an
    exactness control, and assigns the leaf-count floor to a named eligible agent (or makes it structural).
11. **G11 / G25:** the matrix and the dependency list are corrected: classes; S12 before rows 14 and 16; split H2/H5
    acceptance; MBS-7 before OD-3.
12. **G13–G20, G35, G37:** the source classes and labels are corrected as listed. Every attestation substitution is
    labelled as such.
13. **ATTESTATION_PROCEDURE:** hap is revised for G9, G10 and G26, then reviewed afresh. D-HOST-LIFETIME is not put to
    the owner before that review accepts it.
14. **Appointments (G27):** the owner names the S12 reviewer and the acceptance reviewer. s12:29's delegation option is
    removed or restricted.

**Not reviewed or UNVERIFIED by FR1:**
* the incident-review quotations (G38);
* S14's commits (G33);
* the external artifact audit (pkt:27–30), already labelled unverified there;
* development code correctness beyond the lines cited (an implementation-review matter);
* the leaf-count floor (G23);
* the OD-2 text (G12).

Findings by severity: BLOCKING 0 · MAJOR 12 (G1–G12) · MINOR 16 (G13–G28) · NOTE 10 (G29–G38).
