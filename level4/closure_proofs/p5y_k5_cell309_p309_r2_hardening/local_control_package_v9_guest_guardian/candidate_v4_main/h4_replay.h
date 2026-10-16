#ifndef P309_H4_REPLAY_H
#define P309_H4_REPLAY_H
#include "h4_wire.h"
#define P309_H4_IDS 4096
struct p309_h4_history {
  struct p309_h4_request entries[P309_H4_IDS];
  size_t used;
};
enum p309_h4_result {
  P309_H4_OK,
  P309_H4_STALE,
  P309_H4_REUSED,
  P309_H4_EXHAUSTED
};
/* Pure request binding; never caches state/receipt and grants no execution. */
enum p309_h4_result p309_h4_bind(struct p309_h4_history *,
                                 const struct p309_h4_request *,
                                 const char *current, int *duplicate);
#endif
