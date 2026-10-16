/* Pure production helper tests. No sockets, process, manager, clocks or keys.
 */
#include "bootstrap_wire.h"
#include "h4_replay.h"
#include "held_stop_write.h"
#include "phase_state.h"
#include "safety_lease.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define G "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
#define H "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
static void init_lease(struct p309_safety_lease *l) {
  p309_lease_init(l);
  assert(p309_lease_begin(l, 0) == 0);
  assert(p309_lease_publish(l, 0, 0, 100));
}
struct fake {
  long result[3];
  int error[3];
  int call;
  int64_t time, step;
};
static long fake_write(int fd, void *v) {
  struct fake *f = v;
  assert(fd == 71);
  int i = f->call++;
  f->time += f->step;
  errno = f->error[i];
  return f->result[i];
}
static int64_t fake_now(void *v) { return ((struct fake *)v)->time; }
int main(void) {
  unsigned char header[4];
  size_t payload = 0;
  assert(p309_frame_header(8192, header) && header[0] == 0 && header[1] == 32);
  assert(p309_frame_length(header, &payload) && payload == 8192);
  assert(!p309_frame_header(0, header) && !p309_frame_header(8193, header));
  memset(header, 255, sizeof header);
  assert(!p309_frame_length(header, &payload));
  struct p309_safety_lease l;
  init_lease(&l);
  long long old = p309_lease_begin(&l, 1500000000LL);
  assert(!p309_lease_publish(&l, old, 1500000000LL,
                             2000000000LL)); /* exact old expiry */
  assert(p309_lease_begin(&l, 2000000001LL) == P309_LEASE_INVALID);
  init_lease(&l);
  old = p309_lease_begin(&l, 1500000000LL);
  assert(p309_lease_publish(&l, old, 1500000000LL, 1999999999LL));
  init_lease(&l);
  p309_lease_stop(&l);
  assert(p309_lease_begin(&l, 1) ==
         P309_LEASE_INVALID); /* Stop before blocking */
  init_lease(&l);
  old = p309_lease_begin(&l, 1);
  p309_lease_stop(&l);
  assert(!p309_lease_publish(&l, old, 1, 2)); /* Stop during blocked poll */
  init_lease(&l);
  old = p309_lease_begin(&l, 1);
  assert(p309_lease_publish(&l, old, 1, 2));
  p309_lease_stop(&l);
  assert(!p309_lease_current(&l, 3)); /* Stop after publish */
  init_lease(&l);
  assert(!p309_lease_watchdog(&l, 2000000000LL)); /* STARTING no link */
  assert(!p309_lease_publish(&l, 2000000000LL, 1900000000LL,
                             1999999999LL)); /* late poll cannot recover */
  p309_lease_init(&l);
  assert(p309_lease_watchdog(&l, 1));
  assert(!p309_lease_current(&l, 1)); /* unarmed distinct */
  init_lease(&l);
  assert(p309_lease_begin(&l, -1) == P309_LEASE_INVALID);
  atomic_int phase;
  atomic_uint state;
  atomic_init(&phase, 2);
  atomic_init(&state, 0);
  assert(p309_phase_advance(&phase, &state, 3, 6, 8));
  atomic_fetch_or(&state, 8);
  assert(p309_phase_visible(&phase, &state, 6, 8) == 6);
  assert(!p309_phase_advance(&phase, &state, 4, 6, 8));
  atomic_store(&phase, 6);
  assert(!p309_phase_advance(&phase, &state, 5, 6, 8));
  struct p309_h4_history history = {0};
  struct p309_h4_request r = {0};
  int dup = -1;
  memcpy(r.request_id, G, 33);
  assert(p309_h4_bind(&history, &r, G, &dup) == P309_H4_OK && !dup);
  assert(p309_h4_bind(&history, &r, G, &dup) == P309_H4_OK &&
         dup); /* only binding cached, no receipt/state */
  r.has_generation = 1;
  memcpy(r.generation, H, 33);
  assert(p309_h4_bind(&history, &r, G, &dup) == P309_H4_STALE &&
         !dup); /* before reused ID */
  memcpy(r.generation, G, 33);
  assert(p309_h4_bind(&history, &r, G, &dup) == P309_H4_REUSED);
  struct fake f = {{-1, 2, 0}, {EINTR, 0, 0}, 0, 0, 0};
  assert(p309_stop_write_bounded(71, fake_write, fake_now, &f));
  assert(f.call == 2);
  f = (struct fake){{1, 2, 0}, {0, 0, 0}, 0, 0, 0};
  assert(!p309_stop_write_bounded(71, fake_write, fake_now, &f));
  assert(f.call == 1);
  f = (struct fake){{-1, 2, 0}, {EIO, 0, 0}, 0, 0, 0};
  assert(!p309_stop_write_bounded(71, fake_write, fake_now, &f));
  assert(f.call == 1);
  f = (struct fake){{-1, -1, 2}, {EINTR, EINTR, 0}, 0, 0, 50000000LL};
  assert(!p309_stop_write_bounded(71, fake_write, fake_now, &f));
  assert(f.call == 2); /* reaches exact100ms before third attempt */
  puts("PASS production lease/phase/H4 binding/held-write pure helper "
       "assertions; no native API effects");
  return 0;
}
