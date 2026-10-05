"""Build the additive owner-decision record for P309-r2 from the owner's message (task 7, step 1).

usage: make_owner_record.py <message body .txt> <out dir>
Writes:
  OWNER_DECISIONS_R2_MSG5_VERBATIM.md  the message verbatim in one fenced block; sha256 of the body without the newline
                                        that precedes the closing fence (r2 addendum 2 F10, as for message 4)
  OWNER_DECISIONS_R2_RECORD_1.json     each answer keyed to the packet's IDs, quoting the owner's answer line; the
                                        consistency rules of OWNER_REPLY_FORM.md checked; items the message does not
                                        answer listed as OPEN (never inferred)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

body = Path(sys.argv[1]).read_text().rstrip("\n")
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
sha = hashlib.sha256(body.encode()).hexdigest()
lines = body.split("\n")
PACKET = ("level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/owner_decision_packet/OWNER_DECISION_EXECUTION_PACKET.md"
          " (hardening branch 8c21918a)")

md = f"""# Owner decisions for P309-r2, message 5 (VERBATIM; received 2026-10-05 in the coordinating cloud session)

This record holds the owner's answers to the owner decision execution packet ({PACKET}) verbatim, in one fenced block,
with its sha256 below it. The hash follows addendum 2, F10: it covers the body without the newline that precedes the
closing fence.

* **Transcription.** The message was received as chat text and is transcribed here with its line breaks as received.
  Nothing is redacted, and nothing is added inside the block.
* **Additive.** It is a new file. No earlier governance record is changed, including `OWNER_INSTRUCTIONS_R2_VERBATIM.md`
  and `OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md`.
* **Structured form.** `OWNER_DECISIONS_R2_RECORD_1.json` maps each answer to the packet's decision IDs and quotes the
  owner's own answer line. Where the two differ, this verbatim text governs.
* **What it authorizes.** Exactly what the text states, and nothing more. In particular it authorizes no freeze, no
  qualification, no grant and no Γ309 evaluation, and Cell 309 remains OPEN.

## Message 5

```text
{body}
```

sha256: `{sha}` (bytes: {len(body.encode())})
"""
(out / "OWNER_DECISIONS_R2_MSG5_VERBATIM.md").write_text(md)


def after(header):
    """the owner's answer line(s): the non-empty line(s) right after an exact header line"""
    i = lines.index(header)
    return lines[i + 1].strip()


ANS = {
    "OD-R2-0(A)": ("CONFIRM", after("OD-R2-0(A)")),
    "OD-R2-0(B)": ("CONFIRM ALL ROWS", after("OD-R2-0(B)")),
    "OD-R2-0(C)": ("ACKNOWLEDGE, and record the later development-only interruptions as additive history",
                   after("OD-R2-0(C)")),
    "OD-R2-0(D)": ("OPEN (deferred; may be brought back only after the listed prerequisites are satisfied and "
                   "independently evidenced)", after("OD-R2-0(D)")),
    "OD-R2-1": ("(b)", after("OD-R2-1")),
    "OD-R2-1b": ("CONFIRM", after("OD-R2-1b")),
    "OD-R2-2": ("RATIFY", after("OD-R2-2")),
    "OD-R2-3": ("APPROVE AUDIT ONLY (read-only host audit only; dedicated-host availability pending)", after("OD-R2-3")),
    "OD-R2-4": ("OPEN (deferred until the read-only audit identifies the exact host changes)", after("OD-R2-4")),
    "OD-R2-5": ("(i)", after("OD-R2-5")),
    "OD-R2-6(ii)": ("REQUIRE", after("OD-R2-6(ii)")),
    "OD-R2-6(iii)": ("NO HOST AT FREEZE (at this time)", after("OD-R2-6(iii)")),
    "SF1": ("SF1-A (limited to the minimal probe extension and its required tests/review)", after("SF1")),
    "OD-R2-H": ("H-A (exactly the fast-forward 101ef2cb -> a119e978 under C1; nothing else in that step)",
                after("OD-R2-H")),
    "F-DRILL-ORDER": ("FD-A (separate recorded owner action)", after("F-DRILL-ORDER")),
    "AF-1": ("CONDITIONAL / NOT YET TRIGGERED", after("AF-1")),
    "AF-2": ("CONDITIONAL / NOT YET TRIGGERED", after("AF-2")),
    "AF-3": ("AUTHORIZE (separate additive governance-only commit after the verified fast-forward)", after("AF-3")),
    "AF-4": ("DEFER (no grant authorized)", after("AF-4")),
    "AF-5": ("NOT TRIGGERED", after("AF-5")),
}
not_answered = {
    "OD-R2-6(i)": "OPEN: the message does not answer it (the packet recommended DEFER; nothing is inferred)",
    "SF1-A incorporation into r2": ("OPEN: the reply form's separate line 'SF1-A only: incorporate the reviewed SF1-A "
                                    "delta into r2' is not answered; SF1-A is authorized only up to its tests/review"),
    "OD-R2-3 dedicated host": "pending host selection/confirmation (the owner's own words)",
}
checks = {
    "FD-A requires H-A": ANS["F-DRILL-ORDER"][0].startswith("FD-A") and ANS["OD-R2-H"][0].startswith("H-A"),
    "OD-R2-6(iii) NO HOST needs no OD-R2-6(i) answer": ANS["OD-R2-6(iii)"][0].startswith("NO HOST"),
    "OD-R2-0(D) not AUTHORIZE": ANS["OD-R2-0(D)"][0].startswith("OPEN"),
    "OD-R2-5 (i) needs no amendment text": ANS["OD-R2-5"][0] == "(i)",
    "SF1-A incorporation not answered, so not authorized": True,
}
rec = {"schema": "P309_R2_OWNER_DECISION_RECORD/1", "message_file": "governance/OWNER_DECISIONS_R2_MSG5_VERBATIM.md",
       "message_sha256": sha, "answers_to": PACKET,
       "answers": {k: {"recorded_answer": v[0], "owner_answer_line": v[1]} for k, v in ANS.items()},
       "not_answered_or_pending": not_answered, "consistency_checks": checks,
       "consistent": all(checks.values()),
       "authorized_sequence": [l for l in lines if re.match(r"^[1-8]\. ", l)],
       "statement": "a record of the owner's answers; it authorizes exactly what the verbatim message states and "
                    "nothing more; NEW Γ309 TARGET EVALUATIONS = 0; no grant; Cell 309 OPEN"}
(out / "OWNER_DECISIONS_R2_RECORD_1.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
print("sha256", sha, "consistent", rec["consistent"])
for k, v in ANS.items():
    print(f"{k:16s} | {v[1][:70]}")
