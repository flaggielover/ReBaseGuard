# Independent follow-up of development revision 4

Reviewed commit: aef3bead293759e0e4cc1af26e0c01f060bb9abc. Date: 2026-10-15 (Asia/Tokyo). Three fresh independent reports are preserved verbatim beside this file.

DEV_CODE_R4: NOT_FAIL_CLOSED
AMENDMENT_DRAFT_R4: FIT_WITH_CONDITIONS
EVIDENCE: Linux baseline 103 PASS; 73/73 valid assertion kills; exact input hashes verified.

The original targeted defects are repaired. The independent code reviewer found five bounded adjacent record/assessment defects: intermediate clock divergence and suspend changes can cancel at endpoints; malformed mount metadata and duplicate NSpid fields can establish completeness; duplicate PID identities in a supplied snapshot can hide an external child. These concern supplied evidence APIs, not a demonstrated whole-preflight bypass. All five must be repaired before a stronger code verdict.

The amendment's raw-memory caller provenance, fixed static-import list, and restricted checker/observer seams are explicit integration conditions; all20 decisions remain undecided. One README reference still points to r3 instead of r4. No reviewer accepts a route or authorizes an official step.

Native verification supplement: GitHub run38636549368 used exactly aef3bead, Ubuntu/Python3.12, strict ResourceWarning handling, clean baseline first, full diagnostics and unchanged input hashes. The evidence reviewer independently verified all73 complete assertion failures and preserved historical record hashes. This resolves the native-runtime uncertainty in the code report's reviewed test scope, but does not erase the five separately reproduced API defects.

No source files changed during this follow-up review. Reviewers were fresh without prior authorship or inherited parent chat. Forbidden content restrictions remained; one document reviewer saw an unrelated forbidden filename in a narrow listing but did not open its contents, as its disclosure states. New target evaluations=0; no science/decoy/qualification evaluator ran.
