# Eligibility and exposure statement (brief FR1, phase 1)

- Role label: reviewerFR1 (fresh agent, brief FR1)
- Date: 2026-10-16
- Pinned commit for the review (phase 2): 29d79e7045e36c71fa1f30c03d83e92be8a58006

## Prior reading of excluded material
None. This is a fresh context. Before writing this file I read exactly one file:
/home/user/ReBaseGuard/level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/FR1_formalROUTE_REVIEW_CLOUD_R1.txt
(the brief). I have not opened, grepped or otherwise read any of the excluded material (NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*,
NS/audit/INCIDENT_AUDIT*, NS/reviews/REVIEW_EXECUTION_INTERRUPTION*, NS/reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md,
level4/closure_proofs/p5y_k5_cell308_mb_r1/postexec/, any MB r1 target-run record or qualification record,
NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md, or any Cell-309 branch, file or record).
MB r1 target-run observations: none, from this or any earlier context I can recall. The only contact with
project content of any kind is the file names, sha256 values and summary descriptions listed in the brief itself.

## Earlier roles in this project
None. I wrote none of the reviewed material and took no part in development reviews 59-71, the Codex integration
reviews, the MB r1 or MB-S campaigns, or the coordinator's preparation. I have no memory of any earlier session on
this project.

## Acceptance of restrictions
I accept the restrictions of brief FR1:
- review only; no repair, commit, push or edit of any repository file; write only under my scratch directory
  (/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/FR1/);
- read only from the pinned worktree tree_29d79e70 (plus the brief in the shared checkout), the PR2 line by
  `git show` for the A1/A2/A5 trace only, and optionally a history-complete clone in my scratch for git-object reads;
- the exposure restrictions (governance S13, S10) listed in the brief, including blob hashing of MB r1 qualification
  records only via cat-file | sha256sum without printing content;
- no scientific, candidate, decoy, qualification or L-DET code is run; no call to attestation_valid or lx_verified
  against the real repository; only the optional `python3 -B -m unittest discover -s tests` in
  NS/streams/CLOUD_R1_LINUX_DEV/;
- every git, gpg or Python process runs with HOME and GNUPGHOME under my scratch directory;
- any accidental contact will be disclosed;
- phase 2 does not begin until the message "BEGIN PHASE 2" is received.
