/* Pure production lease state: no clock, filesystem, manager or test adapter.
 * Callers supply their actual monotonic reads. DEAD is irreversible. */
#ifndef P309_SAFETY_LEASE_H
#define P309_SAFETY_LEASE_H
#include <limits.h>
#include <stdatomic.h>
#include <stdint.h>
#define P309_LEASE_NS 2000000000LL
#define P309_POLL_NS 1000000000LL
#define P309_LEASE_DEAD (-1LL)
#define P309_LEASE_INVALID LLONG_MIN
struct p309_safety_lease {
  atomic_llong deadline;
};
static inline void p309_lease_init(struct p309_safety_lease *l) {
  atomic_init(&l->deadline, 0);
}
static inline void p309_lease_stop(struct p309_safety_lease *l) {
  atomic_exchange(&l->deadline, P309_LEASE_DEAD);
}
static inline long long p309_lease_begin(struct p309_safety_lease *l,
                                         int64_t now) {
  long long old = atomic_load(&l->deadline);
  if (old < 0 || now < 0 || now > INT64_MAX - P309_LEASE_NS ||
      (old > 0 && (now < old - P309_LEASE_NS || now >= old))) {
    p309_lease_stop(l);
    return P309_LEASE_INVALID;
  }
  return old;
}
static inline int p309_lease_publish(struct p309_safety_lease *l, long long old,
                                     int64_t issued, int64_t completed) {
  if (old < 0 || issued < 0 || issued > INT64_MAX - P309_LEASE_NS ||
      completed < issued || completed - issued > P309_POLL_NS ||
      (old > 0 && (issued < old - P309_LEASE_NS || completed >= old))) {
    p309_lease_stop(l);
    return 0;
  }
  /* STOP and renewal use this same atomic word. STOP cannot be overwritten;
   * old lease must still cover completion, independently of watchdog
   * scheduling. */
  if (!atomic_compare_exchange_strong(&l->deadline, &old,
                                      issued + P309_LEASE_NS)) {
    p309_lease_stop(l);
    return 0;
  }
  return 1;
}
static inline int p309_lease_current(struct p309_safety_lease *l, int64_t now) {
  long long old = atomic_load(&l->deadline);
  if (old <= 0)
    return 0;
  if (now < old - P309_LEASE_NS || now >= old) {
    p309_lease_stop(l);
    return 0;
  }
  return 1;
}
static inline int p309_lease_watchdog(struct p309_safety_lease *l,
                                      int64_t now) {
  /* No false expiration before initial safety exchange has published a lease.
   */
  if (atomic_load(&l->deadline) == 0)
    return now >= 0;
  return p309_lease_current(l, now);
}
#endif
