# Actual saved ETL extension scan, 2026-10-16

The reviewed fixed native scanner and entry were invoked once at 06:26:00.123937 UTC from source commit 84440ce7cf9da42199ced3131e2b7d991b4a54b1. Native execution took 1.906 seconds. Native and wrapper exits were zero; input identity, pre/post hashes, source and binary hashes and handle closes all passed. No timeout or termination was needed.

All 4,249,919 events in the existing 308,346,880-byte ETL were inspected. Every event had zero extension items. Process Start Key was absent in all events; no candidate keys were recovered. The original ETL SHA-256 is 3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870. The aggregate SHA-256 is f877759f2239d6dc538ba8851fb5186c769db45116af369f6366dda546dfc224.

This decisively excludes recovering extension keys from this saved file. It does not establish that Windows cannot collect them, nor that a future collection would resolve thread-lifetime attribution. The previously recorded UNKNOWN CPU 0.3413936 seconds is unchanged. Observed zero loss counters do not certify capture completeness. I2 is not closed; I1-I7 remain OPEN and admission remains BLOCKED.

This was saved-file analysis only: no fresh tracing, host sampling, elevation, VM, installation, policy change or P309 workload. Historical v7 results and all failures are preserved. Raw ETL and private path/process binding records remain local. The evidence inventory is a hash ledger, not permission to publish its listed files. Public data here are explicitly allowlisted aggregates and execution statuses.
