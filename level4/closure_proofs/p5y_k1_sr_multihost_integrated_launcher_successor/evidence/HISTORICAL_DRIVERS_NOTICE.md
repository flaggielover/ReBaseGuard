# Historical, non-authoritative drivers

Additive notice. Nothing below is modified or deleted; governance requires the
historical namespaces to remain byte-intact.

The ONLY authoritative production entry point for the multi-host SR campaign is:

    p5y_k1_sr_multihost_integrated_launcher_successor/driver/integrated_sr_launcher.py

The following is HISTORICAL and MUST NOT be launched:

    p5y_k1_sr_driver_bound_successor/driver/sr_production_driver.py

It is superseded because it imports only the historical gates/ledger, requires
AWS_ONLY (so it cannot run the 69-cell Vultr shard), does not bind the multi-host
trusted-domain layer, and its --produce path is unconditionally unreachable.

Also historical and MUST NOT be launched for this campaign:

    p5y_k1_production_driver/k1prod/driver.py

It dispatches on detector "SR", but over the earlier K1 cover-ledger unit
universe (S.unit_id / K.run_unit), not the 316-cell multi-host SR campaign. It
binds none of the shard manifest, per-role runtime hash, thread contract,
trusted numeric domain, or the ONE global 4500 CPU-h cap.
