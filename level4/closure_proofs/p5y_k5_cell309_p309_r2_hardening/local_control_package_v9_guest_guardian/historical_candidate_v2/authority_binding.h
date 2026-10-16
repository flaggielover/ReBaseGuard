/* Real Linux/systemd initialization; no caller-created authority or D2 types. */
#ifndef P309_AUTHORITY_BINDING_H
#define P309_AUTHORITY_BINDING_H
#include <sys/types.h>
#include <stdatomic.h>
/* Safety-only cancellation state; cannot create authority. Initialize once to
 * {0}, retain for the broker lifetime, and NEVER clear bits or reuse it. */
struct p309_start_control { atomic_uint state; };
void p309_start_cancel(struct p309_start_control *);
int p309_start_is_cancelled(const struct p309_start_control *);
int p309_authority_host_ack_consume(const struct p309_start_authority *);
int p309_authority_note_guardian_ready(const struct p309_start_authority *,int guardian_pidfd);
struct p309_start_authority;
const struct p309_start_authority *p309_authorize_guardian(pid_t peer,const char *generation,const int fds[5]);
const struct p309_start_authority *p309_authorize_gate(pid_t broker);
const char *p309_authority_generation(const struct p309_start_authority *a);
/* Root broker service internal API: consumes fixed on-disk one-use IDLE permit,
 * makes exactly one StartTransientUnit call and returns held object handles.
 * Caller must already own the fixed gate listener before calling. No CLI. */
int p309_start_fixed_gate(struct p309_start_control *,struct p309_start_authority **out);
int p309_authority_stopped(const struct p309_start_authority *);
void p309_authority_stop(const struct p309_start_authority *);
int p309_authority_release_begin(const struct p309_start_authority *);
int p309_authority_release_pending(const struct p309_start_authority *);
int p309_authority_release_commit(const struct p309_start_authority *);
/* Borrowed descriptors: broker pidfd, worker pidfd, cgroup dir, killfd.
 * Never expose to H3/H4 or worker. No automatic dispose before proven cleanup. */
pid_t p309_authority_worker_pid(const struct p309_start_authority *a);
int p309_authority_claim_handoff(const struct p309_start_authority *a);
int p309_authority_cleanup_observed(const struct p309_start_authority *a);
int p309_guardian_pidfd(void);
int p309_guardian_cleanup_observed(int fd);
void p309_guardian_release_reference(void);
int p309_authority_dispose_after_cleanup(struct p309_start_authority *a);
int p309_authority_current(const struct p309_start_authority *a);
int p309_authority_fds(const struct p309_start_authority *a,int out[4]);
#endif
