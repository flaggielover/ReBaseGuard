Saved-input integrity wrapper — staged development only, 2026-10-16

The existing `audit_root_coverage.py` opens the numeric CSV twice. A historical
execution record that pins the ETL/decoder but omits the numeric output SHA-256
cannot establish which exact CSV bytes those prior passes consumed. The new
wrapper does not repair or relabel that historical provenance. It requires
an explicit, separately recorded manifest digest and labels its result
POSTHOC_SAVED_INPUT_CHECK_ONLY.

The manifest binds exact CSV bytes/size, both QPC and independent CSwitch
decoder summaries, expected decoded and CSwitch row counts, the audit and
accounting sources and the wrapper itself. Duplicate JSON keys, non-finite
JSON values, booleans posing as numeric counts, decoder errors/losses,
different event/processor counts, malformed numeric rows and mismatched
counts/digests cause refusal. There is no implicit trust-on-first-use manifest
generator and no automatic large-record run in this staging package.

The wrapper pins all input/source files and ancestors with Windows
CreateFileW GENERIC_READ, FILE_SHARE_READ and BACKUP_SEMANTICS |
OPEN_REPARSE_POINT. Existing writers and reparse points cause refusal. Each
Python data stream must match the held handle's volume/file identity. All
small JSON/source bytes are snapshotted from matching handles and verified
before use; source execution uses those exact bytes rather than an ambient
module path. The audit's `rows` and `read` global dependencies are rebound to
one still-open verified CSV handle and the bound summary snapshot. Every
fully consumed CSV pass records and verifies its own exact-byte SHA-256,
total row count and CSwitch count; exactly two passes are required. Lifetime,
unknown attribution, thresholds and stop/qualification semantics are unchanged.

The input pins remain held across prevalidation, both audit passes and final
digest checks. They are a normal Windows data-write/delete sharing control,
not a claim that every metadata mutation is prohibited. Small synthetic-file
tests showed that access-zero handles did not deny a writable file open;
GENERIC_READ pins did. Separate owned-directory probes showed that even
GENERIC_READ plus FILE_SHARE_READ does not prevent a WRITE_ATTRIBUTES open or
toggling the hidden attribute. The audit therefore uses the same verified
file handle, not a path reopen whose safety would depend on claiming all
metadata writes were prevented. File sharing is not administrator/kernel
custody or a proof concerning pre-existing hostile writable mappings.

The explicit same-handle dependency substitution preserves the historical
parser for the validated numeric schema; it does not grant new evidence
semantics. The wrapper requires the historical audit to keep coverage false
and admission BLOCKED. It explicitly leaves the decoder's two CPU identity
fields unresolved, I1–I7 open, protected-process/other-partition coverage
unproven, and original decoder-output binding absent.

Actual scoped verification:

- 11 targeted tests use tiny saved synthetic CSV/JSON/source files. The
  success case executes the copied actual historical audit and accounting
  sources. Other cases check changed bytes, manifest/source pin failures,
  missing/CSwitch rows, decoder loss, malformed CSV, duplicate keys, pre-existing
  writer refusal and both-pass write/ancestor-rename refusal.
- Initial access-zero testing failed two cases; the original actual failures
  are preserved in INITIAL_ACCESS_ZERO_FAILURE.json as an explicitly manual
  transcription. After GENERIC_READ, all 11 passed. After adding same-handle
  audit passes and exact-byte pass receipts, the same 11 passed again. Logs
  retain the successive runs rather than replacing earlier results.
- ANCESTOR_SHARING_ACTUAL.json contrasts only newly created owned directories:
  access-zero allowed GENERIC_WRITE; GENERIC_READ refused it with error32.
  Rename was refused in both examples (5 versus32). WRITE_ATTRIBUTES and the
  hidden-attribute toggle succeeded in both. No real reparse point was created.

Only this C-workspace staging directory was written. No D repository/record,
private build, large CSV or ETL was modified or reprocessed. No host facts,
trace, WHP/QEMU/VM, UAC, policy, installation, service, production key or P309
workload was queried/started/changed. These changes are not committed to D,
independently reviewed or admitted for real records yet.

Future explicit use requires a reviewer to record the six input/source hashes,
CSV length/counts and post-hoc scope in a manifest, record its own SHA-256,
then invoke `run_verified_audit.py --root ... --manifest ...
--manifest-sha256 ... --audit-source ... --account-source ... --output ...`.
Output is CreateNew only. Do not reinterpret its post-hoc result as proof that
the original decoder execution bound its numeric output.
