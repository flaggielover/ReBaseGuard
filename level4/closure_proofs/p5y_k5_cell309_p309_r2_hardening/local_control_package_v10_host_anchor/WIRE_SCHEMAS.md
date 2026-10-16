# Fixed purposes and byte schemas

All bodies use UTF-8 without BOM, ASCII field values, exact case/order, `key=value` followed by one LF per field including the last, no CR, duplicate/unknown/optional fields or trailing bytes. G, host_boot, guest_boot and invocation IDs are 32 lowercase hex characters; hashes and challenge are 64. Sequences are positive canonical decimal, supported range 1..9223372036854775807. No value is an arbitrary command or authority chosen by an IPC client. Signature is RSA3072/SHA256/PKCS1v1.5, exactly 384 bytes; one transport packet is `canonical body || signature`. The trusted public pin is SHA256 of standard rsaEncryption SubjectPublicKeyInfo DER, independently enrolled. A received packet never enrolls its own key.

Session context (18 fields):

```text
protocol=P309_HOST_VM_SESSION/1
scope=DEV_FIXED_IDLE_ONLY
G
host_epoch_seq
host_boot
guest_boot
package
guest
runtime
policy
challenge
host_record_seq
host_record_sha256
anchor_binding_sha256
checkpoint
vm_lifetime_sha256
guest_root_public_spki_sha256
ack_public_spki_sha256
```

Every name after the first two lines denotes a required `name=value` line. Context is signed only from opaque RecordedReservation after its file flush. Guest expectations come from its own fixed root manager transaction/boot/installed digests and independently enrolled pins, never copied from the ACK itself. Context is not a start/continuation grant.

Reserve ACK (15 fields): exactly the first 15 context field names/order, changing only protocol to `P309_HOST_ANCHOR_RESERVE_ACK/1`. It is separately signed once, from the same sequence-2 reservation. A future authenticated H2 transport delivers the already-generated context then reserve ACK in one attempt/connection; failure ends that G, not a request to re-reserve/re-sign/retry.

Final ACK (18 fields):

```text
protocol=P309_HOST_ANCHOR_ACK/1
scope=DEV_FIXED_IDLE_ONLY
G
host_epoch_seq
host_boot
guest_boot
package
guest
runtime
policy
workerInv
brokerInv
challenge
blocked_proof_sha256
host_record_seq
host_record_sha256
anchor_binding_sha256
checkpoint
```

This signs only the opaque sequence-3 RecordedConsumption produced by BindOnce after verified blocked-instance proof and successful flush. `blocked_proof_sha256` hashes the entire exact canonical root proof body, excluding signature. A reserve ACK/context cannot pass this purpose. One generation gets no second signing attempt after error/loss.

Guest root pre-start proof agreed for the separately implemented factory (11 fields): `protocol=P309_GUEST_ROOT_PRESTART/1`, `scope=DEV_FIXED_IDLE_ONLY`, `G`, `guest_boot`, `package`, `guest`, `runtime`, `policy`, `challenge`, `approval_sha256`, `guest_root_public_spki_sha256`.

Guest blocked proof agreed for that factory (20 fields): `protocol=P309_GUEST_BLOCKED_INVOCATION/1`, `scope=DEV_FIXED_IDLE_ONLY`, `G`, `host_epoch_seq`, `host_boot`, `guest_boot`, `package`, `guest`, `runtime`, `policy`, `workerInv`, `brokerInv`, `guardianInv`, `challenge`, `reserve_record_seq`, `reserve_record_sha256`, `anchor_binding_sha256`, `checkpoint`, `vm_lifetime_sha256`, `guest_root_public_spki_sha256`.

The guest root signer must derive boot/invocations from the real successful manager transaction and guardian READY. The host factory must verify root signature against independent enrollment, exact outstanding challenge, current held VM/H2/channel, pins/digests, reserve record and instance/guardian state. This library accepts only the resulting opaque internal lease and proof hash; it does not treat these proposed wire formats as an already implemented/authenticated transport or hardware attestation.

Enrollment revision 3 exact order is defined by Binding.Keys. The future installer creates its 4096-byte ENROLLED journal header binding the SHA256 of the exact enrollment bytes; the first claim binds this exact additional canonical body:

```text
P309_HOST_ANCHOR_BINDING/3
enrollment_sha256=...
G=...
prestart_proof_sha256=...
host_boot=...
guest_boot=...
challenge=...
vm_lifetime_sha256=...
```

No host installation/enrollment occurred. These development schemas do not amend the accepted r2/D2 lifecycle or authorize any actual phase.
