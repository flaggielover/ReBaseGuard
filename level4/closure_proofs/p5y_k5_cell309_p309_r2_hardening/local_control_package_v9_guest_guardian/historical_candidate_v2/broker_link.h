#ifndef P309_BROKER_LINK_H
#define P309_BROKER_LINK_H
#include "authority_binding.h"
struct p309_guardian_link;
/* Internal broker calls only, never a socket/API start operation. */
int p309_guardian_bind(const struct p309_start_authority *,struct p309_guardian_link **);
/* gate socket is accepted from the fixed root-owned listener; peer is rechecked.
 * No payload release until this same link received READY and authority remains current. */
int p309_release_fixed_gate(struct p309_guardian_link *,int gate_socket);
int p309_guardian_heartbeat(struct p309_guardian_link *);
/* Latches first; attempts held killFD once, then best-effort STOP.
 * Return 0 means local stop write accepted, never cleanup completed. */
int p309_guardian_request_stop(struct p309_guardian_link *);
/* STOP is concurrent-safe and atomically irreversible; no manager/storage lock.
 * Release dispatch CAS defines the in-flight boundary. Guardian independently
 * enforces lease if the broker blocks. No in-process realtime watchdog claim.
 * Retirement requires stop + LOCAL_QUIESCENT + manager exit/no-job + guardian
 * process exit. Handles remain retained until destroy-after-join to prevent
 * concurrent STOP/heartbeat descriptor reuse. It is not formal STOPPED;
 * durable terminal publication/external anchor remain the full broker's job. */
int p309_guardian_retire(struct p309_guardian_link *);
/* Owner joins ALL callers before destroying link, then disposes authority. */
int p309_guardian_destroy_after_join(struct p309_guardian_link *);
#endif
