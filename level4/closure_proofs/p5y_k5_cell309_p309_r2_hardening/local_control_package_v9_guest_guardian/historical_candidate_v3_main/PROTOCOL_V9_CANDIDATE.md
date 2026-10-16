# V3 native candidate protocol contracts

Status: prepared source, no native v3 build or actual execution evidence. I1-I7 OPEN; formal admission BLOCKED. Root software attestation assumes trusted OS/root/approved installer; it is not hardware attestation. Fixed scope DEV_FIXED_IDLE_ONLY only.

## Entry sequence and ownership

The fixed manager service verifies three activated listeners, fixed M identity and source pin. No Start on activation/status. A separately started fixed root admin-helper makes the only prepare request. Prepare verifies broker manager identity, chooses G, consumes local one-use fence and retains actual M. Main publishes G before blocking host reserve. Reserve creates challenge, signs ROOT_PRESTART and records it before the one host exchange. Validated session+ReserveACK then permit initial Observer safety query. Start is a single manager transaction with early JobRemoved cache, full effective-policy readback and owned handles. Guardian READY must be actual and durably bound. GateReady then signed FinalACK consumption precede release dispatch CAS. Failures never create another G or retry a consumed stage.

STOP before a dispatch CAS forbids that dispatch. STOP after CAS races an in-flight operation; it is not represented as no-dispatch. Owned stop targets only retained cgroup.kill, without manager lookup, ACK or logging. Guard timeout/parent loss is independent. Stop acceptance, local quiescence, manager cleanup and formal STOPPED are separate concepts.

## Purpose-signed host contracts

Canonical bodies are strict ASCII key=value lines, single LF after every field including last, no BOM/CR/extras/duplicate fields. Hex lowercase. G/boot/invocations 32 hex; digests/challenge 64 hex; positive canonical decimal sequences at most INT64_MAX. Wire is body concatenated with exactly 384 signature bytes. RSA3072 SHA256 PKCS1-v1.5, pin SHA256 of canonical rsaEncryption SPKI DER. No new key creation or caller-selected key.

ROOT_PRESTART ordered 11 fields:
protocol=P309_GUEST_ROOT_PRESTART/1, scope, G, guest_boot, package, guest, runtime, policy, challenge, approval_sha256, guest_root_public_spki_sha256.

Context ordered 18:
protocol=P309_HOST_VM_SESSION/1, scope, G, host_epoch_seq, host_boot, guest_boot, package, guest, runtime, policy, challenge, host_record_seq, host_record_sha256, anchor_binding_sha256, checkpoint, vm_lifetime_sha256, guest_root_public_spki_sha256, ack_public_spki_sha256.

Reserve ordered 15:
protocol=P309_HOST_ANCHOR_RESERVE_ACK/1 followed by Context fields scope through checkpoint in the same order.

Blocked ordered 20:
protocol=P309_GUEST_BLOCKED_INVOCATION/1, scope, G, host_epoch_seq, host_boot, guest_boot, package, guest, runtime, policy, workerInv, brokerInv, guardianInv, challenge, reserve_record_seq, reserve_record_sha256, anchor_binding_sha256, checkpoint, vm_lifetime_sha256, guest_root_public_spki_sha256.

Final ordered 18:
protocol=P309_HOST_ANCHOR_ACK/1, scope, G, host_epoch_seq, host_boot, guest_boot, package, guest, runtime, policy, workerInv, brokerInv, challenge, blocked_proof_sha256, host_record_seq, host_record_sha256, anchor_binding_sha256, checkpoint.

G/challenge/guestboot/digests/root pin originate locally or in approved installed inputs, not copied from ACK as expectations. Host context is a distinct signed purpose. The host owns a genuine held-VM/enrollment/H2 factory and durable Reserve/Bind; that external factory is not implemented by this guest client. Missing it means refusal. M identity is locally held and checked by the attester but absent as explicit fields from the above host schemas; do not claim otherwise.

Fixed root0600 host-anchor-v10.sock carries ROOT_PRESTART once and returns two ordered packets (context, same-reservation ACK). Blocked proof returns one final packet. Each exchange has an absolute local BOOTTIME 2-second limit, no retry and no FD passing. Actual H2 server is an external dependency.

## Production safety protocol proposal

Separate root0600 monitor-facts-v9.sock is B-to-M facts query, not H4 and not a start authority. Request ordered 14 fields:
protocol=P309_ROLLING_SAFETY_REQUEST/1, scope, G, host_epoch_seq, host_boot, guest_boot, package, guest, runtime, policy, sequence, nonce, previous_sha256, vm_lifetime_sha256.

Response ordered 27:
protocol=P309_HOST_SAFETY_FACTS/1, scope, collector=LIVE_ROLLING_ETW_V1, G, host_epoch_seq, host_boot, guest_boot, package, guest, runtime, policy, sequence, nonce, previous_sha256, qpc_frequency, interval_start_qpc, interval_end_qpc, signed_qpc, event_loss, unknown_ticks, coverage_complete, quiet, policy_stable, suspend_epoch, source_instance, vm_lifetime_sha256, source_evidence_sha256.

Response uses the same RSA3072 wire convention but a distinct enrolled Observer public pin. Observer pin must differ from Controller ACK pin. It is not enough to rename synthetic facts: the producer must derive fields from its real owned rolling collector, identity generations, completeness/loss/quiet/policy evidence and genuine VM lifetime. Such a producer and monitor relay are not supplied here. No injected constant green path exists.

Every request uses fresh 32-byte getrandom nonce, sequence 1..4096 and previous full signed-wire SHA256 (initial 64 zeroes). Reply must match context, request and previous hash. Stable QPC frequency in 1..1e9; observed window 60..105 seconds; signature QPC no earlier than interval end and at most 0.5 seconds later. Later end/signed QPC strictly increase, source instance/frequency/suspend epoch stay fixed; gaps at most 45 seconds. Loss and unknown must be zero, coverage/quiet/policy flags exactly 1. source_instance is 32 hex and evidence hash 64 hex.

Independent guest checks: request/verification RTT at most 1 second; lease expires at request-issue BOOTTIME +2 seconds, never completion +2. No old lease renewal during pending request. Current lease also requires retained same M identity. Host QPC and guest BOOTTIME remain separate numeric domains. These additional restrictive DEV_FIXED_IDLE_ONLY bounds do not relax or replace formal 60/5/45 rules. Missing/late/invalid frame, M loss, source change or any unknown irreversibly Stops. Real provider/interop/runtime verification remains open.

## Required approved installation inputs

Fixed root-protected /etc/rebaseguard-p309 inputs: package-v9.sha256, guest-v9.sha256, runtime-v9.sha256, policy-v9.sha256, monitor-v9.sha256, admin-helper-v9.sha256; guest-blocked-v10.private.pem root0400 and corresponding .spki.sha256; host-anchor-ack-v10.spki.der/.spki.sha256; host-observer-v9.spki.der/.spki.sha256. Public/hash files root0444, link/ancestor constraints per code. No TOFU/keygen. Install-tree/source proof and keys require separate approved ceremony; merely finding these files does not close I4.

Fixed root0700 state retains exclusive permit consumption, monitor claim, root prestart, context/reserve, guardian READY, blocked/final consumption and main diagnostic journal. No deletion/reset/rearm. Unit templates and proposed paths are not installed by this source package.
