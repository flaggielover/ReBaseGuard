#ifndef P309_HELD_STOP_WRITE_H
#define P309_HELD_STOP_WRITE_H
#include <errno.h>
#include <stdint.h>
/* Callback seam is private source plumbing; no external FD/authority API.
 * Only EINTR retries, up to 32 attempts and 100ms from issue. Short write or
 * any other error is UNKNOWN. A blocked kernel syscall itself is not preempted.
 */
static inline int p309_stop_write_bounded(int fd,
                                          long (*write_once)(int, void *),
                                          int64_t (*now)(void *), void *ctx) {
  int64_t start = now(ctx);
  if (start < 0)
    return 0;
  for (unsigned i = 0; i < 32; i++) {
    int64_t before = now(ctx);
    if (before < start || before - start >= 100000000LL)
      return 0;
    long n = write_once(fd, ctx);
    if (n == 2)
      return 1; /* exactly one accepted command, never retry success */
    if (n >= 0 || errno != EINTR)
      return 0;
  }
  return 0;
}
#endif
