# READING_EXTERNAL_ER_T6_ROLE_HOLDERS (ER-T6 r2, bounded register-metadata lookup)

**Status: COMPLETE as a bounded register lookup.** Every subject is reported individually. All 24 subject rows
returned **CANNOT_TELL**. No row returned HOLDER. No row returned NOT_LISTED. For the reasons, see §5 and §6.

Reader: ER-T6-Metadata-Reader (a delegated AI reader, not the owner personally). Report addressed to the owner only.
Date of lookup: 2026-10-17 (UTC).

## 1. Actual role, exposure and limitations

* **Identity.** Claude Code cloud session `session_01RQPL4w9cd4o1evySZeqLTq`, environment
  `env_01GTgmTdDaUY28GtoGZVi3QY`, origin `web_claude_ai`, created 2026-10-17. These are taken from the session service's
  description of this session.
* **Project involvement within my actual context.** None before this appointment. This conversation began with the
  owner's appointment file. It carries no earlier coordinator, reviewer, B1, B2 or B3 context. It is not a reused
  coordinator or reviewer conversation.
* **Prior restricted exposure.** None that I know of from my own context. I did not read REVIEW_EXECUTION_INTERRUPTION,
  the recovery chain, the execution review, any adjudication, any incident review, `NSF/postexec/*`, MB r1 target-run
  material or Cell-309 content, either before or during this task.
* **Relationship to the coordinating environment: UNVERIFIED.** This session runs on the same product family (Claude
  Code cloud) as the coordinator-side sessions named in ER-T6 r2 §3, R1a and R2. The session is linked to the
  repository `flaggielover/ReBaseGuard`. I cannot establish any of the following, and I do not certify isolation:
  * whether it shares an account, environment, container image, memory or settings with those sessions;
  * whether any other session can observe it.
* **Infrastructure and control independence: UNVERIFIED** (Q5).

## 2. Request and governing-source bindings (verified before relying on content)

Repository `flaggielover/ReBaseGuard`. Request commit `58769a0f39014a43be984773de0f39f9fc8d469d`.

Each file was retrieved only as
`https://raw.githubusercontent.com/flaggielover/ReBaseGuard/<commit>/<path>`. All paths are under
`level4/closure_proofs/p5y_k5_cell308_research/`. SHA256 was computed over the raw bytes with Python's `hashlib`. The
Git blob identifier was computed with Git's blob hashing, `sha1("blob <len>\0" + bytes)`.

| id | path | bytes | sha256 (raw bytes) | git blob | vs. appointment |
|---|---|---|---|---|---|
| A | `governance/new_host_route_cloud_r1/EVIDENCE_REQUEST_ER_T6_ROLE_HOLDER_CHECK_R2_20261017.md` | 6868 | `fac34cb9cc3dcd52745ebb50a81dfc64d33ab27c3c54a89cecf00b704d3acf0a` | `c999063bfc3a6c43127983cf1d01e942d98b5bd4` | MATCH |
| B | `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md` | 11627 | `c170c726c43601ee8c3d028a64b0639708c8b5799698aaf1ced62f5a13ee152c` | `a8baf592056284ef5afb30673ffed0ee3d5fd9cb` | MATCH |
| C | `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md` | 2946 | `a1972ad3cbd7d59d431724e32fa45ecf3edece36e9251c607b241d7f160c224c` | `911095ed1eaa13333f325917dfdf4878dbcd76ab` | MATCH |
| D | `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md` | 7696 | `84379c99a25d32cf6232dde185592d274141e7847726c3e167cb61efbb3e5162` | `b84501c6ddf57d93471e4f92d9fe92b50a680bfd` | MATCH |

### 2.1 How the request was read (accepted requirements vs. author-prepared text)

* **A (ER-T6 r2) is self-described as "AUTHOR CORRECTION · PREPARED · NOT APPOINTED · NOT COMPLETED"** (A line 3). I
  use only these parts of it:
  * its §3 subject list;
  * its output format;
  * its result vocabulary.

  I do not treat A as adopted as a whole.
* **The §4 reader restriction** (A lines 63–66: "the owner personally, or an existing listed holder …") is
  author-prepared and unadopted. For this reader it is replaced by the owner's appointment. That appointment does not
  manufacture prior exposure as a qualification. I was not given observation access to become eligible.
* **A §4 also lists source facts the owner is to supply before reading** (A lines 68–78): path, commit pin, raw-byte
  sha256, and whether the location list is separate. The owner's appointment fixes the path and the commit. It
  expressly states that no expected source digest was supplied. The digest below was therefore **computed by me at
  binding**. It identifies the retrieved bytes and is **not** a match against an independently supplied value. I
  determined the separate-or-contained question from the register itself (§3.2).
* **Search for a conflicting binding requirement.** C (erratum E1) records the governance delta review as
  DELTA_ACCEPTED (C lines 3–5). That makes A1 (B) as amended an accepted text. B §4 S13 (B lines 148–153) and the
  register's restriction block (register L95–98) bar the successor's route, implementation and caps agents from
  having seen the observations. I hold none of those roles, and this appointment retires me from all of them. In B, C,
  D and the bound register I found no accepted text that restricts who may read the names-only register. **No
  conflicting binding requirement was identified.**
* **S13 and A1 9(e) (D lines 98–100) are descriptions, not verification.** They describe the register as naming
  observations, never values. I verified the actual bytes separately (§3).

## 3. Register binding

### 3.1 Binding receipt (byte-only, before semantic reading)

```
commit: 00d4df454f67dd1c26f34d68c14296f67896010b
path:   level4/closure_proofs/p5y_k5_cell308_research/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md
bytes:  10275
sha256: cc0b0be8c3d989bbe0105ad9660706b459c443a0374bef726191e1dc93e9d53f   (computed; no expected digest was supplied)
blob:   a4def0a8da563cff84d98f360ea464a60b1aeb29                           (computed from the bytes)
```

* The owner selected this source snapshot. It was not chosen through `git log`.
* Retrieval was by the exact raw URL at that commit (HTTP 200).
* No directory listing, history, branch collection or local checkout was used.
* The same saved bytes were used for the reading.
* The blob id was computed from the bytes. It was not cross-checked against a tree listing, because tree listings are
  outside this appointment's scope.
* The file has 128 content lines. Line references below (`L…`) are to these bytes.

### 3.2 MBS-1 location list

The MBS-1 location list is **contained in the register**: "E1″ erratum 2 (successor incident re-rating MBS-1; X1–X3)",
**L110–L124**. The locations are at L111–L116 and the holders at L117–L124. No separate document was bound or read.
I did not follow any listed location.

### 3.3 Holder entries present in the register (identifier and line only)

* E1″ table, holder column: L88–L93.
* Holder statement: L102.
* E1″ erratum: L107–L108.
* E1″ erratum 2 holders: L117–L124.
* Statement: L125–L127.

Named holders:

| holder | lines |
|---|---|
| role term "coordinator" | L88–L93, L102, L125–L127 (defined at L3 as "the main agent of this session", with no label or session id) |
| reviewINT | L90–L92 |
| reviewEXEC | L90, L91, L93 |
| "the adjudicator" | L91 |
| reviewGOV | L107, L119 |
| step-8 adjudication reviewer | L107–L108 |
| reviewINC2 | L118 |
| adjudicator308 | L120 |
| reviewADJ | L121 |

Class (non-enumerated) holder entries:

| class entry | line |
|---|---|
| "later readers of the chain" | L92 |
| "every agent that read one of the locations above" | L122 |

## 4. Results, one per subject

Subjects as in A §3 (A lines 45–56). The format is `<row>: RESULT — <register line references>`. The codes in
brackets are explained in §5.

```
R1a: CANNOT_TELL — L3, L88–L93, L102, L125–L127 [U]; L92, L122 [K]
R1b: CANNOT_TELL — L3, L88–L93, L102, L125–L127 [U]; L92, L122 [K]; mapping unresolved per A L51 [M]
R2: CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R3a: CANNOT_TELL — L88–L93, L102, L125–L127 [U]; L92, L122 [K]
R3b: CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R3c: CANNOT_TELL — no stable identifier per A L52 [M]
  R3c sublabel "coordinator recording independent code/evidence reviews": CANNOT_TELL — L88–L93, L102, L125–L127 [U]; L92, L122 [K]; [M]
  R3c sublabel "fresh independent evidence reviewer": CANNOT_TELL — L1–L128 [N]; L92, L122 [K]; [M]
R4-59 (reviewCLOUD_R1): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-60 (reviewCLOUD_R1_DELTA): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-61 (reviewCLOUD_R1_DELTA2): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-62 (reviewCLOUD_R1_DELTA3): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-63 (reviewCLOUD_R1_DELTA4): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-64 (reviewREVIEW63_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-65 (reviewREVIEW64_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-66 (reviewREVIEW65_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-67 (reviewREVIEW66_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-68 (reviewREVIEW67_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-69 (reviewREVIEW68_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-70 (reviewREVIEW69_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R4-71 (reviewREVIEW70_REPAIR): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R5a (reviewerFR1): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R5b (reviewerFR2): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R5c (reviewerS12): CANNOT_TELL — L1–L128 [N]; L118 [A]; L92, L122 [K]
R6a (B1-External (Codex)): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
R6b (B3-External): CANNOT_TELL — L1–L128 [N]; L92, L122 [K]
```

## 5. Basis codes, and why no row is NOT_LISTED

* **[N] No name match.** A literal string check of the bound bytes found none of the following anywhere in
  L1–L128:
  * the subject's label;
  * the subject's session id (R1a, R2);
  * the owner-released B3 identifiers (Codex thread `01a1449c-7b38-7273-a5b4-9364ee8a50a5`, report sha256
    `16188ffd…ce96a`).

  The only string hits were false positives: `B3` matched inside `MB308` (L79, L81), and `worker` matched inside
  `per-worker` (L89, L126).
* **[K] Class holder entries cannot be resolved from the register.** L92 ("later readers of the chain") and L122
  ("every agent that read one of the locations above") define holders by conduct, not by name. Whether a subject falls
  in either class depends on facts outside the register: what that subject actually read. **Because of these two
  entries, the absence of a name match does not establish that the register leaves a subject out of its holder list.**
  NOT_LISTED would therefore be a default negative. It is not used.
* **[U] Unmapped role term.** The register names its holder as "the coordinator" (L88–L93, L102, L125–L127). It defines
  that term only as "the main agent of this session" (L3), with no label, session id or date-of-label. Neither of the
  following can be tied with certainty to that role term using register evidence:
  * `claude_cloud_coordinator_20261014` / `session_01S66r3p84SFdY6Vc4RchSWr` (R1a);
  * any Codex coordinator label (R3a, the first R3c sublabel).

  The E1″ addendum is dated 2026-09-30 in its heading (L79). The R1a label carries the date 20261014. That date
  difference is recorded as a reason for caution, not as a finding either way. **I do not assign the register's
  "coordinator" to any participant.**
* **[A] Possible unverified alias.** `reviewerS12` might denote the reviewer of governance condition S12 (B lines
  145–147: a fresh incident-independence reviewer re-rates the risk). The register names "reviewINC2 (the incident
  re-rating reviewer)" at L118. Nothing in the permitted sources establishes that these are the same participant.
  **The alias is unmatched.** I do not report a HOLDER on this basis.
* **[M] Mapping unresolved upstream.** A marks R1b and R3c as CANNOT_TELL for identity (A lines 51–52). R3c's two
  sublabels are unstable ledger agent labels. I invent no participant behind them.

## 6. Gaps, kept separate (none implies another)

| # | question | finding of this lookup |
|---|---|---|
| Q1 | identity mapping | **Unresolved** for every row (see [U], [A], [M]). For R4–R6, the session or thread behind each label is not in the register. The owner-released B3 thread id supplements R6b's identifier only, and does not appear in the register. Participants with no ledger label are not covered (A lines 58–59). |
| Q2 | source completeness | **UNKNOWN.** Only the owner-selected snapshot `00d4df45…` was read. I did not check whether later commits amend the register or the MBS-1 list, or whether the class entries L92 and L122 are complete. History was out of scope. |
| Q3 | register coverage | §4: 24 subject rows (plus R3c's two sublabels), all CANNOT_TELL. The register names nine holder identifiers or roles and two conduct-defined classes (§3.3). No subject identifier appears among them. |
| Q4 | actual restricted exposure | **UNVERIFIED.** A register lookup does not establish it. |
| Q5 | platform / control independence | **UNVERIFIED** (§1). |

## 7. Contact and exposure disclosure (no observation values reproduced)

* **Automatic repository contact.** When this cloud session started, the environment attached
  `flaggielover/ReBaseGuard` as the session source and cloned it to the container's working directory. That happened
  automatically, before I acted.
  * I did not read, list, search or run anything from that checkout.
  * Shell commands started in that directory as their default working directory, but read nothing from it.
  * I cannot verify what the harness itself read from the checkout (for example, project configuration files).
    **UNVERIFIED.**
* **Network contact.** Exactly five raw-file GETs at pinned commits: the four governance files, then the register.
  No GitHub API calls. One session-service call, describing this session's own metadata.
* **What the register exposed to me.**
  * The register itself is not among its listed locations (L111–L116).
  * It names observation types, locations and holders without values. Its E1″ section states that no values are
    recorded there (L81–L84).
  * Its row and statement labels contain **two clock-time anchors of audit and logging events** (in L89, L91, L126).
    I treated these as disclosure-event metadata, not as runtime or host readings. I do not reproduce them here.
  * Its pre-campaign section contains **one committed historical figure** (L37). It is not an MB r1 target-run
    observation. I do not reproduce it.
  * Governance file C lines 44–45 name a CPU-figure source without giving values.
  * **I cannot assert that no exposure occurred.** I hold the register's names-and-locations content and the two
    event-time anchors.
* **No unexpected restricted content** (no runtime, CPU, thermal, load, memory or host reading values) was encountered,
  so semantic reading was not stopped.
* **Retained artifacts.** The raw register bytes and the governance files remain in this session's isolated scratch
  directory. They were not sent to the coordinator, root, B1, B2, B3 or any other conversation.

## 8. Non-effects

* **No policy is adopted.** ER-T6 r2 is not declared adopted.
* **No future reviewer standing is granted** to anyone, including this reader. This reader's role ends with this
  report, and it takes no later role in route design, implementation, provenance assessment, caps, qualification,
  acceptance or risk rating.
* **No execution is authorized.** This report is none of the following:
  * a B3 review;
  * a policy-provenance review;
  * a material-change determination;
  * a risk rating;
  * a T6 applicability ruling;
  * an owner eligibility determination;
  * host acceptance, OD-3, S1, L-DET, decoy, qualification or formal execution.

  CANNOT_TELL clears neither A15 nor A17 (A lines 94–97).
* **Bounded scope.** These are not established here: the absence of exposure, non-holder eligibility, completeness of
  the register or location list, identity mapping, and independence.
* **No repository writes.** No commit, push, publication, delegation, scheduled work or contact with another
  conversation was made.
