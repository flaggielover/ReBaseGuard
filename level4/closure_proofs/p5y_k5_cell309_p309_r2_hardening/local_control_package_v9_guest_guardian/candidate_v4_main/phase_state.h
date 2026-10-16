#ifndef P309_PHASE_STATE_H
#define P309_PHASE_STATE_H
#include <stdatomic.h>
/* Pure diagnostic projection; control stop bit is authoritative. */
static inline int p309_phase_visible(atomic_int *phase, atomic_uint *state,
                                     int stop_phase, unsigned mask) {
  int p = atomic_load(phase);
  return p < stop_phase && (atomic_load(state) & mask) ? stop_phase : p;
}
static inline int p309_phase_advance(atomic_int *phase, atomic_uint *state,
                                     int next, int stop_phase, unsigned mask) {
  int current = atomic_load(phase);
  while (current < stop_phase && !(atomic_load(state) & mask)) {
    if (next < current || next >= stop_phase)
      return 0;
    if (atomic_compare_exchange_weak(phase, &current, next)) {
      if (!(atomic_load(state) & mask))
        return 1;
      atomic_store(phase, stop_phase);
      return 0;
    }
  }
  return 0;
}
#endif
