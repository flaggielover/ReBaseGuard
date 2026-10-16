# Fresh bounded check FR2: corrections to FR1's conditions, and host-attestation acceptance procedure r2 (Cell-308 MB-S new-host route, Cloud r1)

## 1. Header

- Reviewer: reviewerFR2 (fresh agent, brief FR2)
- Date: 2026-10-16
- Pinned commit: `6d5f9a63816ad9294afc85b17df0e49e0dec8bf3` (detached worktree `scratchpad/FR2/tree_6d5f9a63`)
- Eligibility statement: `scratch/ELIGIBILITY_AND_EXPOSURE_FR2.md` (the coordinator reports committing it at `45a52623`,
  a commit after the pinned one; I have not read that commit).
- Abbreviations. NS = `level4/closure_proofs/p5y_k5_cell308_research/`. G = `NS/governance/new_host_route_cloud_r1/`.
  The original texts are "amd" (route amendment r5), "pkt" (readiness packet), "lsp" (L-DET packet), "add" (L-DET
  reference addendum), "hep" (H1–H8 plan) and "hap" (procedure r1).
  The corrections are "disp" (FR1 disposition), "aE1" (amendment erratum E1), "lE1" (L-DET packet erratum E1), "r2"
  (procedure r2), "pkg" (D-* package r2) and "hE1" (plan erratum E1).
  The accepted sources are "gov", "gA1", "gE1", "rat", "bR2", "reg", "rA1", "rE1" and "rE2", as in FR1. "lxp" =
  `NS/streams/CLOUD_R1_LINUX_DEV/lx_platform.py`. "s12" = the S12 brief draft.
  Line numbers refer to the pinned tree.
- Scope integrity. Every sha256 prefix that the correction files give for the originals matches the files at
  6d5f9a63:
  * amd `d0963b11…ba933`;
  * pkt `078f2ab2…3a17b`;
  * lsp `f0f367a9…80e4`;
  * add `4efcd152…5277`;
  * hep `901a05d7…4ec8`;
  * hap `91e61e8d…0322`;
  * FR1 `af150ef4…b6df`;
  * lxp `da32ce8c…6389`.

  `git diff --stat 29d79e70 6d5f9a63` over G shows additions only, so no reviewed file was edited.
- The worktree is **shallow** (`git rev-parse --is-shallow-repository` = true). No history-dependent claim was
  re-verified here.

## 2. Exposure disclosure (actual contact)

- **Shared checkout.** I read only the brief there. Every other read used the pinned worktree. Its git directory is
  `/home/user/ReBaseGuard/.git/worktrees/tree_6d5f9a631`, so git object reads went through the shared object store.
- **Opened in full:**
  * all twelve scope files;
  * FR1;
  * `USER_AUTHORIZATION_20261016_OD2.md`;
  * rA1, rE1, rE2, gE1 (the D3 block) and reg.
- **Opened in part:**
  * gov lines 95–131;
  * gA1 lines 130–183;
  * rat lines 1–90, read truncated to 500 characters per line;
  * bR2 lines 47–48, 146–147, 241, 254, 400–440 and 439, plus a grep for "launchd", "first in effect" and section
    headings;
  * ROUTE_PREPARATION lines 17–20 and 39–42;
  * s12 lines 25–32 and 55–65;
  * lxp: a definitions listing, and lines 77–84, 617–626, 897–924, 1066–1145, 1185–1555 and 1609 (read, not imported
    or run).
- **git:**
  * `rev-parse HEAD`;
  * `status`;
  * `log --oneline -8` (one-line subjects of eight Cell-308 research commits, 9db01504..6d5f9a63);
  * `show --stat de160b56` (message and file list);
  * `diff --stat` over G;
  * `rev-parse --verify afa93072^{commit}` (printed the full id only);
  * `rev-parse --git-dir --is-shallow-repository`.

  Every git process ran with HOME and GNUPGHOME under `FR2/home` and `FR2/gnupg`. No Python process was started.
- **Accidental contact (disclosed).**
  * **One recursive grep.** I ran `grep -rn "Complete the fresh S12"` over all of NS, limited to `*.md` and `*.txt`.
    That read the bytes of files the brief excludes, including:
    * `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
    * any `NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`;
    * any `NS/audit/*`;
    * `NS/reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`.

    It printed matches only from `FR1_DISPOSITION_20261016.md`. No line of any excluded file was printed or seen.
  * **One `find`.** A `find` over NS by file name (`*S12*`, `*READINESS_MATRIX*`) walked the directory entries of the
    excluded directories. It printed only the s12 draft path.
  * **One file name containing "309".** A listing of `NS/governance/` showed the file name `K5_AUDIT_EXCL_309.md`.
    I did not open it. The grep above read its bytes (no match, nothing printed).
- **Not opened:**
  * any MB r1 record, postexec or target-run material;
  * anything under `p5y_k5_cell308_mb_r1/`;
  * any Cell-309 branch, ref or content;
  * the ledger.
- **Not run:** no scientific, candidate, decoy, qualification or L-DET code, and no tests. No clone and no
  `git ls-remote`.
- **Not available at the pinned commit:**
  * `ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt`, which disp §1 lists as a correction file;
  * `READINESS_MATRIX_R2_20261016.md`, which is deferred;
  * this brief FR2 itself.

## 3. Verdict lines

FR1_CONDITIONS: MET_WITH_EXCEPTIONS
ATTESTATION_PROCEDURE_R2: ACCEPTED_WITH_CONDITIONS

**These verdicts bring nothing into force and decide no D-\* item.** They are advice to the owner from an agent that
runs in the coordinator's session. `DECIDED` stays empty (lxp:79). The owner's adoption, the S12 rating, OD-1, OD-3,
MBS-6/7/8, S16(c), S1 and every later gate are still required.

**FR1_CONDITIONS.** Conditions 2, 4, 5, 6, 8, 9 and 10 are met in text. The minor defects in them are listed in §6.
Five conditions have exceptions:
* condition 3: the s12 part is UNVERIFIED;
* condition 7: amd's L-PIN row is not amended (K1);
* condition 11: met only in part (the matrix part is DEFERRED);
* condition 12: met only in part (G13, G20);
* condition 13: subject to this review's conditions.

**ATTESTATION_PROCEDURE_R2.** It is ACCEPTED_WITH_CONDITIONS, not NOT_ACCEPTED, because it now resolves FR1's four
named defects in substance:
* G9: two read bases;
* G10: an anchor check with fail-closed rules;
* G11: a split acceptance;
* G26: the digest reported by the reviewer, the self-assertion removed, agent identity defined.

It is also candid about what in-repository checks cannot establish. It is not ACCEPTED, for four reasons:
* rejections are not anchored outside the repository (K2);
* the "direct" digest channel does not exist for an agent reviewer that the coordinator launches (K3);
* the split acceptance has no mechanism or gate binding (K4);
* amd's L-LIFE row still conflicts with it (K1).

## 4. Conditions 1–14

| # | FR1 condition | status | reason | evidence |
|---|---|---|---|---|
| 1 | G12: OD-2 text committed verbatim; the owner confirms or re-commissions | OWNER-RESERVED. Disposition **mostly correct** | The commit order is correct: 29d79e70 → de160b56 (OD-2) → 6b3aac20 (FR1 eligibility). But the record is verbatim only for the "operative parts". The work list is summarised, and "the owner's full text is kept in the session transcript". disp G27 and §3 quote owner words, "Complete the fresh S12 review using an eligible reviewer", that are **not** in the committed record (K16) | OD2:3–4, 16; disp:41, 56, 73, 92 |
| 2 | G1: sufficient conditions, HOST-row status, S4 instrument | MET | The four sufficient conditions, CONDITIONAL status, failure ⇒ EXCLUDED, and route-audit addendum A2 as the S4 instrument are all stated. Remaining defects: the status timing, the record count and the pin list (K7, K8) | aE1:22–49; pkg:30; gov S4 (gov:104–108) |
| 3 | G2: "not lower than HIGH" in pkt §4, amd §6, s12 Q1 | PARTLY (s12 part UNVERIFIED) | amd §6 is replaced (aE1.6) and pkt §4 is superseded by pkg row 1. The commissioned S12 brief is **absent** at 6d5f9a63. The draft still reads "HIGH, or a rating with stated mitigations". aE1.6 also deletes the "decisive argument lost / second draw" clause that aE1.2 cites "(§6)" (K9) | aE1:82–90; pkg:30; s12:55–56; disp:23 |
| 4 | G3: MBS-7 before OD-3; members no longer accepted-unchanged | MET in text | aE1.1 strikes the members, labels them [OPEN] MBS-7 and requires the owner to record MBS-7 before OD-3. lE1 §3 adds a step 0. pkt §6 item 9 still lists MBS-7 after a match; that belongs to the deferred dependency list (condition 11) | aE1:14–17; lE1:37–38; pkt:179 |
| 5 | G4: MBR1_REPRO still runs, not a repeat, mismatch STOP; L-DET bound to a named commit | MET | All stated. The commit is "a named commit" in principle, but no text says who names it, when, or where it is recorded. The list of files that may differ is deferred to "the accepted amendment" (K15) | aE1:51–63; lE1:29–35; pkg:33; rA1:64–68 |
| 6 | G5: H1, H3, H8 from the L-DET interpreter build; L-DET pins binding | MET | aE1.4 and hE1 §2 set the windows. aE1.2 item 2 and lE1 §4 make the pins binding. Nothing requires the interpreter build to follow the H3 actions or acceptance part 1 (K11) | aE1:65–70; hE1:43–44; lE1:69 |
| 7 | G6 / G24: L-PIN for a non-dpkg interpreter, libpython, workers, post-pin mappings; D-INTERPRETER and L-PIN agree | PARTLY | lE1 §4 covers every element. But the **governing** amd §3 L-PIN row is not amended (aE1.9: "Everything else in amendment r5 stands"). It still pins "dpkg versions of libc6 and the interpreter's packages (an unknown owner package never matches)", so a source-built interpreter (pkg row 2) can never pass it (lxp:1070–1088, 1137–1142). lE1 §4's list also omits `sys.version` and the architecture (K1, K8) | amd:144; aE1:112–115; lE1:40–69; pkg:31 |
| 8 | G7: authoritative store, value-free transport, exact assertion | MET | pkg row 20 (a)–(e): the store is an owner fact; an owner-supplied `for-each-ref` listing; the exact assertion with the full id `afa930727d08…` (verified with `rev-parse`); absent ⇒ refuse; no push. The listing's location for preflight and its per-step freshness are unspecified (K13) | pkg:49; gA1:157–162 |
| 9 | G8: unknown ⇒ refuse; the re-read labelled, bounded and recorded | MET | Exited ⇒ unknown ⇒ no reading ⇒ refuse (the L-EXCL wording at amd:139 supports it). Re-read: a NEW RULE, ≤ 3, each reading recorded, none after the marker | aE1:72–80; pkg:42 |
| 10 | G21–G23: (a)∧(b); strict fs regex with gcd = 1; number tokens; exactness control; floor | MET | All present. The floor is structural (> 0 per job and case), FR1's second option. Remaining gaps in the (b) Decimal text rule and the exactness control (K14) | lE1:11–27 |
| 11 | G11 / G25: matrix and dependency list corrected; split H2/H5; S12 before rows 14 and 16; MBS-7 before OD-3 | PARTLY; the matrix part is **DEFERRED** | The split is in r2 §4 and hE1 §2. MBS-7 is in aE1.1. The pkt §3 matrix and the pkt §6 dependency list are not corrected by any file at this commit (matrix R2 is unwritten). The split has no mechanism and does not place H4 (K4) | r2:92–108; hE1:45–48; pkt:47–73, 161–180 |
| 12 | G13–G20, G35, G37: source classes and labels | PARTLY | G14–G19, G35 and G37 are met (pkg rows 2, 3, 5, 6, 8, 9, 14, 16; aE1.1). G13 is part met: aE1.8 relabels amd, but pkt §2 still classes bR2 **ACCEPTED** (pkt:40), and no file supersedes pkt §2. G20 is part met: the SUBST list is incomplete (K12) | aE1:101–110; pkg:28–71; pkt:40 |
| 13 | hap revised for G9, G10, G26 and reviewed afresh; D-HOST-LIFETIME not put to the owner before acceptance | PARTLY | r2 is written and is reviewed here: ACCEPTED_WITH_CONDITIONS. D-HOST-LIFETIME should not go to the owner before the conditions in §7 are met in text | r2; pkg:50 |
| 14 | Appointments (G27): the owner names the S12 and acceptance reviewers; the s12:29 delegation removed or restricted | OWNER-RESERVED. Disposition **partly correct** | It correctly says "partly accepted" for the S12 reviewer, whom the coordinator appoints. The acceptance reviewer is owner-appointed in r2 §2. The removal of the s12:29 option is in a brief absent at this commit (UNVERIFIED); the draft keeps it (s12:29–30). The delegation rests on an owner quote not in the committed record (K16). S12 was commissioned before condition 1 was met, against FR1 §7's ordering; this is disclosed (disp:88–93) | disp:56, 86, 88–93; r2:47; s12:29–30 |

## 5. Procedure r2 findings

**Soundness, item by item.**
* **G9: resolved in the procedure.**
  * C fixes the accepted bytes.
  * HEAD's whole history fixes the veto.
  * C must be an ancestor of HEAD (r2:24–32).

  **Not resolved across texts.** FR1 asked to "fix one rule in both texts". amd's L-LIFE row is unamended and still
  reads the acceptance and the fixed set at HEAD (amd:146). r2:31 merely asserts that "the same rule applies to L-LIFE"
  (K1). Gaps:
  * C is never defined relative to `review_commit`;
  * r2 does not say whether a later change or deletion of the attestation or review at HEAD refuses. The development
    code requires both at HEAD (lxp:1524, 1423) (K5).
* **G10: resolved in substance.**
  * Who: the owner or a checker the owner names.
  * When: before L-DET, the designated series, qualification, `execute`, and each `resume` / `recover`.
  * What: C, the review sha256 and the attestation sha256, plus C being an ancestor of HEAD.
  * Record: in the owner's record, mirrored in the ledger.
  * Fail closed: absent, MISMATCH or an unreachable owner all refuse (r2:110–143).

  Gaps (K6):
  * the step list omits the interpreter build (inside the H8 window, aE1.4), the official decoy runs and the marker
    or grant;
  * it does not say that both part anchors are checked;
  * the consequence of "wait" against the 7-day deadline is unstated.
* **G11: resolved as FR1 worded it**, with parts 1 and 2 (r2:99–108). The mechanism is missing (K4):
  * both parts accept the same attestation sha with the identical line `HOST_ATTESTATION_ACCEPTED sha256=<sha>`, so
    the in-repository check (lxp:1459) cannot tell part 1 from part 2;
  * "a gate that needs H2 or H5" names no gate. The attestation-consuming gates are H1, H3 and H6 (lxp:625, 1609;
    `host_lifetime_attested`);
  * H4 (attestation field `exclusivity`, hep:43) is in neither part.
* **G26: resolved in text.**
  * `reviewer_reported_sha256` must equal both the recomputed digest and the owner's recorded digest (r2:61–83).
  * The attestation's self-asserted `reviewed` / `accepted` fields are dropped from the successor schema. r2:87–88
    correctly states that lxp:1538 still requires them.
  * Agent identity = the brief and its sha256, the session or agent id, and the owner's record.

  **Not achievable as written for an agent that the coordinator launches**, as FR1, FR2 and the S12 reviewer were.
  That agent's "final reply" and any channel run through the coordinator's session, and the coordinator supplies the
  agent id (K3).

**Honesty about in-repository limits.** Adequate.
* §6 states that the class of false-history attacks cannot be closed in-repository, and that every in-repository
  check is defence in depth.
* It states the H1/H8 circularity that FR1 F5 named, and drops hap's circular trust item "a host the owner controls".
* It says that preflight cannot read the anchor and that the mirrored-line check is only defence in depth.

Two overstatements:
* The circularity is confined to H1/H8, although every H-item reading is taken by the attested host (K10).
* "It already reads the veto over HEAD's history" (r2:35) is true for `reviews/` blobs (lxp:1336–1373, 1443–1448).
  The development code does not read ledger REJECTED lines, which r2's veto row includes. The veto row also
  describes the veto as "any `HOST_ATTESTATION_REJECTED` blob", which is narrower than the L-LIFE negative-word and
  extra-verdict veto (amd:146; lxp:1326–1333) (K17).

**Statements about the development code, checked against lxp (read only):**
* The completeness precondition matches lxp:1191–1214: not shallow; no promisor, partial-clone or `fsck.*` key;
  `fsck --full --strict`.
* The tree-mode walk over every commit matches lxp:1277–1311.
* "Does not take C" is true: every read is at HEAD.
* `reviewed` / `accepted` are required (lxp:1538), as stated.
* r2 §4 describes the order rule as "the commit that first introduces the accepting line". The code requires
  **every** commit that adds or removes the line to follow every commit that adds or removes the blob
  (lxp:1481–1500). The code is stricter than the description (K19).

**Still missing:**
* external anchoring of rejections and of the set of appointed reviews (K2);
* an owner-controlled channel for the digest and verdict (K3);
* a part marker and a gate mapping for the split, and a place for H4 (K4);
* the definition of C and the HEAD-versus-C consistency rule (K5);
* an amendment of amd's L-LIFE row (K1);
* who writes and approves the acceptance reviewer's brief (K18).

## 6. Findings

| id | severity | location | finding | required correction |
|---|---|---|---|---|
| K1 | MAJOR | amd:144, 146; aE1:112–115; lE1:40–69; r2:31 | Corrections to two gate rows live only in side documents. aE1.9 keeps "everything else in amendment r5", including the L-PIN row ("dpkg versions … of the interpreter's packages (an unknown owner package never matches)") and the L-LIFE row (the acceptance and fixed set read at HEAD). lE1 §4 and r2 §1 redefine both, without a precedence clause in amd. The proposed route therefore holds two conflicting L-PIN rules, under one of which a source-built interpreter cannot pass, and two conflicting L-LIFE read bases. FR1 G9 ("fix one rule in both texts") and condition 7 ("D-INTERPRETER and L-PIN agree") are unmet in the governing text | Add an amendment erratum that replaces amd §3's L-PIN and L-LIFE rows and the D-HOST-LIFETIME row's carried items with the lE1 §4 and r2 §1 rules, or states expressly that those texts replace the rows |
| K2 | MAJOR | r2:61–66, 84, 112–118, 27 | Rejections are not anchored outside the repository. The reviewer reports only its digest to the owner, not its verdict. The anchor records only acceptance commits. A rejection survives only through in-repository history and ledger lines that the coordinator writes, which §6 itself treats as defence in depth. A rejection that is never committed, followed by a second appointed review (or a re-attestation with trivially different bytes, hence a new sha), leaves no external trace | The reviewer reports verdict, digest and attestation sha256 to the owner. The owner's record lists every appointment and its outcome. The anchor check refuses if that record holds a REJECTED outcome, or an appointment without an outcome, for this attestation or for an earlier attestation of the same machine. A new attestation cites every prior rejected sha |
| K3 | MAJOR | r2:49–53, 61–66; brief FR2 lines 8–10; disp:56 | G26's "the reviewer's digest reaches the owner directly" has no channel when the acceptance reviewer is an agent that the coordinator launches in its own session. The reply, and the agent id that identity item 2 relies on, pass through the coordinator, which also commits the review bytes | Require the acceptance reviewer to be a human, or an agent launched by the owner in a session the coordinator cannot access, reporting to the owner directly. Otherwise state that, for a coordinator-launched agent, the G26 control does not hold and acceptance rests on the owner's adoption alone |
| K4 | MAJOR | r2:99–108; hE1:45–48; hep:43; lxp:1459, 625, 1609 | The split acceptance cannot be enforced as specified. Both parts produce the same accepting line for the same sha, so in-repository checks cannot tell part 1 from part 2. "A gate that needs H2 or H5" names no gate. H4 (field `exclusivity`) belongs to neither part. The effect of a part-2 rejection on part 1 is unstated (the history veto would void both) | Give each part a distinct acceptance line (or a separate attestation file). List, per gate, which part it requires. Place H4 in a part, or state that it is a live gate only and drop its attestation field. State the effect of a part-2 rejection |
| K5 | MINOR | r2:16–37, 74–76 | C ("the acceptance commit") is undefined relative to `review_commit` and the ledger commit. r2 does not say whether a change or deletion at HEAD of the attestation or accepting review, after C, refuses. The development code requires both at HEAD | Define C (e.g. the commit that introduced the accepting review). Require the blob ids at HEAD to equal those at C, or define any change after C as refusal |
| K6 | MINOR | r2:120–143; aE1:67–70 | The anchor-check step list omits the L-DET interpreter build (inside the H8 window), the official decoy runs used for caps (pkg row 17) and the marker or grant. It does not require both part anchors to be checked. "An unreachable owner is a wait": its interaction with the 7-day deadline and resume budget is unstated | Extend the list. Require every applicable part anchor to be checked. State that a wait never extends the deadline, and what an owner absence near the deadline means |
| K7 | MINOR | aE1:26–49 | Inconsistent timing: "After the owner adopts this route, it reads CONDITIONAL", but "Until it [A2] exists the HOST row reads EXCLUDED", and A2 is written after the adoption. "All four compared records" conflicts with five record files (the ladder pair is two). Which "fresh bounded check" A2 needs (FR2, or a later one) is unstated | Make the status CONDITIONAL only from A2. Say "four cases (five records, listed by blob id)". Name the check |
| K8 | MINOR | aE1:31–33; lE1:51–63; rE1:51–53; rA1:61–63 | The pin list of sufficient condition 2, and lE1 §4's L-PIN list, omit two pins of the accepted RC2 pin: `sys.version` and the architecture. lE1 §4 also omits the interpreter path. All three are in amd's L-PIN row and in lxp `PIN_KEYS` (lxp:1133). Accepted RC2 still binds, but the lists are presented as complete | Add `sys.version`, architecture (`machine`) and interpreter path to both lists |
| K9 | MINOR | aE1:82–90; amd:246–248; aE1:39–41 | aE1.6's ellipsis replacement deletes "with the decisive argument lost and the successor's value a second, different draw" from §6, while aE1.2 cites "(§6)" for that statement | Restate the clause in the aE1.6 replacement |
| K10 | MINOR | r2:149–156 | The circularity is stated for H1/H8 only. H2, H3, H4 and H6 readings are also taken on the attested host by its own software | State that every inventory reading shares the circularity, and that only owner and provider statements plus repeated identity readings support any H item |
| K11 | MINOR | aE1:65–70; hE1:20, 43–48; lE1:48; pkt §6 | Nothing orders the L-DET interpreter build after the owner's H3 actions and acceptance part 1. If the build comes first, the window "from the interpreter build" starts before updates are shown disabled | State that the build follows acceptance part 1 and is an anchored step (K6) |
| K12 | MINOR | pkg:52–65; hep:44, 47; pkg:49 | The SUBST list omits the H5 storage attestation and H8's owner-attestation fallback (amd:83). Its owner listing in D-S15-NEWHOST (b) is itself an owner-supplied statement. The PREP:19 list omits rules that change measurement rules or thresholds: D-PAUSE (1) (rat item 4, the EVAL_CAP clock); D-POWER-ABSENT (the prepared-state AC condition of R-FREE attainability, rat:61–62); D-TEXT-LAUNCHD (R-MEM step 1 inputs; rat items 30–31 timeouts). pkg row 18 also drops the bR2 §9 launch row ("only under the launchd launcher", bR2:420) that amd:179 listed for D-TEXT-LAUNCHD | Complete both lists, and restore the bR2 §9 launch row in pkg row 18 |
| K13 | MINOR | pkg:49 | D-S15-NEWHOST (b) does not say where the owner's listing is placed so that the preflight can read it ("recorded in the owner's record" is unreadable by preflight, like the anchor), nor how it is bound to a step (a step id and time, the step's commit) | Specify a committed location and per-step binding, and keep the owner's record as the evidence |
| K14 | MINOR | lE1:23–27 | The (b) Decimal rule ("exact plain decimal text with no exponent") does not say whether trailing zeros and the sign of a zero are kept, or how an exponent-form input is written. The exactness control is undefined when a view has no Decimal leaf. The prefix manifest `lib/python3.14/**` includes `__pycache__`, whose rewriting between steps would give a mismatch that consumes the one attempt | Fix the Decimal text rule (e.g. the source token's digits preserved verbatim). Define the control's fallback (an fs-string leaf, or INCOMPLETE stated in advance). State the bytecode-cache rule (a read-only prefix; `PYTHONDONTWRITEBYTECODE`; caches included and pinned) |
| K15 | MINOR | aE1:60–63; lE1:32–35 | The L-DET commit is "a named commit", but no text says who names it, when, or where it is recorded. The list of files that may differ is deferred to "the accepted amendment" | Name and record the L-DET commit and the diff list in the OD-3 record, before OD-3 |
| K16 | MINOR | disp:41, 56, 92; OD2:3–4, 16 | disp quotes the owner, "Complete the fresh S12 review using an eligible reviewer", as the basis for the coordinator appointing the S12 reviewer and commissioning S12 before condition 1. The committed OD-2 record holds only a summary ("fresh S12 review"). FR1 condition 1 asked for a verbatim commit; the record is verbatim only for operative parts | Commit the full OD-2 text verbatim, or withdraw the quote. Have the owner's adoption expressly cover the S12 appointment and its commissioning before condition 1 |
| K17 | MINOR | r2:27, 35 | The veto row ("any `HOST_ATTESTATION_REJECTED` blob or ledger REJECTED line") is narrower than L-LIFE's veto: a negative word, or any verdict-like line other than the acceptance line, in any blob under `reviews/` in HEAD's history (amd:146; lxp:1326–1333). "Already reads the veto" overstates, because ledger lines are not read | State the veto as L-LIFE's plus ledger REJECTED lines, and say the ledger part is unimplemented |
| K18 | NOTE | r2:39–53 | r2 excludes reviewerFR1 but not reviewerFR2 (the reviewer of r2) or the S12 reviewer. It does not say who writes the acceptance reviewer's brief, or that the owner approves it (the brief frames the scope; FR1 G27) | State both |
| K19 | NOTE | r2:94–95; lxp:1481–1500 | r2 §4 describes the development order rule as "first introduces". The code requires every commit that adds or removes the line to follow every commit that adds or removes the blob | Describe it accurately |
| K20 | NOTE | r2:24 vs r2:19 | The C row's read basis is the owner's external record, not a git object, which contradicts "every fact is read from git objects" | Separate the in-repository facts from the owner's check facts |
| K21 | NOTE | lE1:83–86 | The reference-list re-derivation that makes the list "the reviewer's own" (lsp §4) rests on FR1's self-declared eligibility. FR1 disclosed a full-branch blob:none clone and ref-name contact including "309" (FR1:47–55) | Record that its standing depends on the owner's adoption of FR1 (condition 1) |
| K22 | NOTE | hE1:1, 10–12 | "Reviewed host-selection criteria" can be read as accepted. The disclaimer follows | Prefer "classed (not accepted)" in the title |

Also checked (C), the [ACCEPTED] quotations added or relied on, against their sources:

| quotation or reliance (location) | source | result |
|---|---|---|
| gov S4 "a route audit (Phase 3)" (aE1:43) | gov:107 | verbatim fragment |
| route A1 §3 "mismatch … STOP and the S4 changed branch" (aE1:58; lE1:33) | rA1:66–67 | correct paraphrase |
| "exact equality of every certified leaf, timing stripped" (lE1:15) | rA1:65–66 | verbatim |
| route E2 escalates a fired trigger to HIGH (aE1:89) | rE2:17–18 | correct paraphrase |
| T1 "the science is then 'changed' under S4" (aE1:88) | incident review (excluded) | UNVERIFIED by FR2; identical to amd:244 (FR1 G38) |
| S17; MBS-3 / route E2 L6 (aE1:98; hE1:20) | gA1:174–176; rE2:13–14 | correct |
| brief R2 line 402 (aE1:104) | bR2:402 | correct. Line 402 names four sources, not only the protocol draft; aE1.8 handles this by citing accepted texts where they exist |
| ratification items 4, 24, 25 (aE1:106) | rat:15, 29, 30 | they exist and are on point (EVAL_CAP clock, memory pressure, LPM). The mapping from row to item is not given (condition 12) |
| MBS-5(b) via route E2 (aE1:107) | bR2:146–147; rE2:18 | correct |
| PREP:19, PREP:41 (aE1:108–110) | ROUTE_PREPARATION:19, 41 | verbatim fragment; [PREPARATION], not [ACCEPTED] |
| MBS-7 [OPEN] (aE1:15) | reg:34; bR2:66 ("MBS-7 comes first in effect"; FR1 cited bR2:47–48 for this) | correct |
| S15 assertion, full marker id (pkg:49) | gA1:158; `rev-parse` → `afa930727d084a5b70e6b85d30ca8f34c0e8ae74` | correct |
| R-ALLOW (b) includes `/usr/sbin/`, `/sbin/` (pkg:43) | rat:75 | correct |
| item 15 (pkg:45) | rat:21 | correct |
| bR2 line 241 "under its launchd launcher" (pkg:47) | bR2:241 | verbatim. pkg row 18 drops the bR2 §9 launch row "only under the launchd launcher" (bR2:420), which amd:179 listed (a narrowing of amd's list; K12) |
| rat items 30–31 timeouts (pkg:47) | rat:33–34 | correct |
| R-FREE, R-MEM step 5, rows 24, 25 (pkg:34–38) | rat:58–59, 49–50, 29–30 | correct |
| close-indeterminate after the marker, "RC2 pin rule" (lE1:68) | rE1:54–55 (at resume) | correct for resume; an extension by analogy to `execute` |
| rE1 DR2, gov S6, rat 18–19, route A1 HOST row, bR2 "this host only" (hE1 §1.1) | rE1:56–58; gov:111–116; rat:23–24; rA1:40; bR2:419 | correct (FR1 F3's classing) |
| S13 with E1 D3 (r2:45) | gA1:148–153; gE1:40–48 | correct |
| OD-2 "Select fresh, eligible independent reviewers. Record their identities…" (disp:41) | OD2:10 | verbatim |
| OD-2 "Complete the fresh S12 review using an eligible reviewer" (disp:56, 92) | OD2 | **not found** (K16) |

No accepted text is weakened by the corrections. aE1.4 and aE1.6 are stricter than the accepted texts. One addition
may be read as a proposal presented as settled: lE1 §5 treats the reference list as re-derived and agreed by FR1
(K21).

Not verified by FR2:
* the incident-review quotation;
* the `fs` grammar at driver 317–319 (relied on FR1);
* history facts (shallow worktree);
* the S12 brief and matrix R2 (absent);
* the requirements document cited by pkg row 3 (outside scope).

## 7. Conditions

For ATTESTATION_PROCEDURE_R2: ACCEPTED_WITH_CONDITIONS, and for the exceptions to FR1_CONDITIONS. Each item can be
checked against a committed text. Conditions 1–5 must be met before D-HOST-LIFETIME is put to the owner. Conditions
6–9 must be met before OD-3.

1. **K1.** An amendment erratum replaces amd §3's L-PIN and L-LIFE rows, and the D-HOST-LIFETIME carried items, with
   the rules of lE1 §4 (including `sys.version`, architecture and interpreter path, per K8) and r2 §1. Alternatively it
   states expressly that those texts govern over the rows.
2. **K2.** r2 requires:
   * the reviewer's verdict, as well as its digest, reported to the owner;
   * the owner's record to list every appointment and its outcome;
   * the anchor check to refuse on any recorded REJECTED outcome, or any appointment without an outcome, for this
     attestation or any earlier attestation of the same machine.
3. **K3.** r2 states the reporting channel for an agent reviewer: owner-launched, outside the coordinator's session.
   Otherwise it states that G26's control does not hold for a coordinator-launched agent.
4. **K4.** r2 defines a distinct acceptance marker per part, the per-gate part requirement and H4's place, and the
   effect of a part-2 rejection.
5. **K5, K6, K17.** r2 defines C. It requires that HEAD's attestation and review blobs equal those at C, extends the
   anchor-check step list (interpreter build, official decoys, marker), and restates the veto as L-LIFE's plus ledger
   REJECTED lines.
6. **Condition 3 (s12 part) and condition 14.** The commissioned S12 brief is committed. It reads "not lower than
   HIGH" in Q1, and it removes the s12:29 delegation option.
7. **K16.** The full OD-2 text is committed verbatim, or the disposition's unrecorded quote is withdrawn. The owner's
   adoption expressly covers the coordinator's S12 appointment and the commissioning of S12 before condition 1.
8. **Conditions 11 and 12.** Matrix R2 and a corrected dependency list are committed (MBS-7 before OD-3, S12 before
   rows 14 and 16, the split acceptance, the class corrections), and pkt §2 reclasses bR2. They get a bounded check.
9. **K7–K9, K11–K15.** These are corrected in the respective errata.

Findings by severity: BLOCKING 0 · MAJOR 4 (K1–K4) · MINOR 13 (K5–K17) · NOTE 5 (K18–K22).
