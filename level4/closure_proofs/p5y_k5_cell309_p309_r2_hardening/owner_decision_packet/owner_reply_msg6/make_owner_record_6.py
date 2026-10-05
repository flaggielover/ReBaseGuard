"""Build the additive record of the owner's message 6 (SF1-A incorporation authorization; task 8, step 1).

usage: make_owner_record_6.py <message body .txt> <out dir>
Writes OWNER_DECISIONS_R2_MSG6_VERBATIM.md: the message verbatim in one fenced block; its sha256 covers the body
without the newline that precedes the closing fence (r2 addendum 2 F10, as for messages 4 and 5).
"""
import hashlib
import sys
from pathlib import Path

body = Path(sys.argv[1]).read_text().rstrip("\n")
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
sha = hashlib.sha256(body.encode()).hexdigest()
md = f"""# Owner decision for P309-r2, message 6 (VERBATIM; received 2026-10-05 in the coordinating cloud session)

This record holds the owner's authorization to incorporate the independently accepted SF1-A delta into r2. The
message is held verbatim in one fenced block, with its sha256 below it. The hash follows addendum 2, F10: it covers
the body without the newline that precedes the closing fence.

* **Transcription.** The message was received as chat text and is transcribed here with its line breaks as received.
  Nothing is redacted, and nothing is added inside the block.
* **Additive.** It is a new file. No earlier governance record is changed, including
  `OWNER_DECISIONS_R2_MSG5_VERBATIM.md` and `OWNER_DECISIONS_R2_RECORD_1.json`.
* **What it answers.** The line left unanswered by message 5 (`OWNER_DECISIONS_R2_RECORD_1.json`,
  `not_answered_or_pending`, "SF1-A incorporation into r2"). It authorizes exactly the fast-forward of r2 from
  `b66a45f0` to `716946e8`, verified before and after, and then one separate governance-only commit in r2.
* **What it does not authorize.** Anything else, as the text states. In particular it authorizes no freeze, no
  qualification, no grant and no Γ309 evaluation. OD-R2-0(D) remains OPEN, and Cell 309 remains OPEN.

## Message 6

```text
{body}
```

sha256: `{sha}` (bytes: {len(body.encode())})
"""
(out / "OWNER_DECISIONS_R2_MSG6_VERBATIM.md").write_text(md)
print("sha256", sha, "bytes", len(body.encode()))
