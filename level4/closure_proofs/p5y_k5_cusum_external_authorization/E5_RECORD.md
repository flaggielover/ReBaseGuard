# E5 record: amended-packet verification before authorization

`EXECUTION_BINDING_R4.json` prerequisite E5 is: re-run the prelaunch verifier and an independent static review on the
amended packet before any authorization. This record covers the amendment `842d3565`
(`EXECUTION_BINDING_AMENDMENT.json`, sha256 `0c6809a2d56fc15603fc15a27bf79cc0e94977bf4370cacee9740295f1972bb4`),
committed after the review `585c9a01` (`review/AMENDMENT_REVIEW.md`, sha256 `9240e7b5…`, PASS_WITH_SCOPE_LIMITATION,
canonical sources sha256 `b437adba64cd4098d6f8998f01af159e7092c14b6597c219cc9ab130da97c015`).

## Independent static review

`review/AMENDED_PACKET_REVIEW_E5.md` is the reviewer's own record, verbatim. The reviewer is the fresh-context session
that wrote the amendment review. It worked from its own clones and ends with `E5_AMENDED_PACKET_REVIEW: PASS`.

## Mechanical verification by the preparer

All runs used fresh GitHub clones at `842d3565`, unmodified frozen code, and read-only steps.

| file | where | result |
|---|---|---|
| `evidence/e5/E5_PKT_VERIFY_MAC.json` | owner's Mac, fresh clone, after publication | every check PASS |
| `evidence/e5/E5_PKT_VERIFY_HOST.json` | vultr-02, fresh blobless clone, contract venv | every check PASS |
| `evidence/e5/E5_FROZEN_VERIFIER_TEMPLATE_REPORT.json` | vultr-02, `code/prelaunch_verify.py` with its default (the inactive template) | REFUSED as expected |

**What `code/pkt_verify.py --stage amendment` checks:**
- publication against the real GitHub `ls-remote`;
- the science freeze (introduced once at `852b2d65`, first parent `5da170db`), and frozen P05;
- the amendment: introduced once, strictly after the freeze, allowed keys only, BOUND_QUALIFIED, science sha256;
- the executor identity recomposed from the 11 bound files (`ef1c86e4…`), and all 279 executor pins;
- the two entries, and exactly 14 sources at their current hashes;
- the canonical sources sha256, computed both by the frozen `probe_rules.canonical` and independently;
- the review-file binding (exactly one verdict line and one sources line), and that the review was committed no later
  than the amendment;
- that the committed amendment equals the reviewed draft except for the two placeholder fields;
- the **unmodified frozen `check_P06`**, given an in-memory authorization that names the amendment sha256: PASS,
  "executor bound, qualified and independently reviewed".

**Frozen verifier with the inactive template.** The expected result is a refusal on the activation-dependent checks only:
- P05 and P07–P10 PASS, and the real GitHub publication read returns `842d3565`;
- P01–P04 and P11–P12 fail because no authorization or LAUNCH_NOTICE exists;
- P06 fails on exactly one clause, "authorization names another executor binding", because the template carries
  `SET_AT_ACTIVATION`.

## Conclusion

The amended packet is intact and ready for the authorization step. Authorization must name the amendment sha256 above.
This record changes no packet file, no executor, adapter or frozen file, and no scientific rule.
`EXECUTION_AUTHORIZED = false` and the guard is DENY at this commit.
