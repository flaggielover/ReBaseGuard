# Failure diagnoses

## F1 — initial live collector transport failed

The first concurrent Python-URL collector produced an all-unavailable diagnostic because the local Python certificate chain could not validate the proxy. Direct `curl` probes succeeded. Before any result interpretation, the collector transport was changed to bounded `curl` subprocesses and the identical frozen queries were rerun. The final manifest contains 72 completed primary runs and preserves source-access failures separately.

## F2 — scholarly source access limitations

Semantic Scholar returned HTTP 429 at the access probe and Google Scholar yielded no inspectable result payload. No search was claimed for either source. Two independent scholarly indexes completed every frozen query.

## F3 — historical AI review was not recoverable

The repository had only an unsupported project-history statement. Its listed names guided explicitly labeled follow-up searches but supplied no evidence. `Touboul` remains an unresolved historical reference.

## F4 — partial overlap required claim narrowing

W03/W14 already update adaptive CUSUM/SR reference values; W06/W08/W33 study post-stopping estimation; W13 is multi-cyclic; W25 adapts a future reference window after change tests. Broad novelty language is therefore forbidden even though no DIRECT combination was found.

## F5 — first adversarial run was 16/18

The first frozen adversarial run is preserved in `results/adversarial_first.json`. A17 correctly failed before the final repository-verification record existed. A4 failed because the anti-simulation regular expression matched its own literal inside `run_adversarial.py`; the checker was repaired by excluding only its own source file from that source-code scan. No campaign scope, scientific criterion, or literature classification changed.

## F6 — first offline reproducer invocation used the wrong root depth

The first `reproduce.sh` invocation climbed four directories from the campaign instead of three and stopped immediately with a missing-interpreter message. It ran no test, generator, or scientific command and changed no artifact. The root path was corrected before the successful end-to-end reproduction.

## F7 — corrected reproducer exposed a self-referential human mirror

The next invocation reached the initial byte check and stopped because `ADVERSARIAL_AUDIT.md` embedded A14's generator digest, while that digest itself covered the report. The human mirror now states the stable A14 outcome without embedding the digest; canonical JSON retains the check evidence. No audit criterion changed.
