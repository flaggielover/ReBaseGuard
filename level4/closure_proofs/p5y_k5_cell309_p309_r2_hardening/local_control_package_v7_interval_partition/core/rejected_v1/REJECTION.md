# Rejected v1

These four original files were copied byte-for-byte before the v2 repair. PREPARATION.json preserves the actual 11-test PASS receipt and original hashes. Raw v1 console output was not separately persisted at the time; no reconstructed log is presented as an original artifact.

Independent review found that per-slice rebinding could move the tail of one CSwitch span to a new TID generation, and move an existing thread to a new ProcessKey after PID reuse. Three original test expectations encoded those errors. The 11 PASS result is historical execution evidence for the rejected model, not correctness or admission evidence. Do not run this source against actual data.
