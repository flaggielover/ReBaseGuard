#include "h4_replay.h"
#include <string.h>
enum p309_h4_result p309_h4_bind(struct p309_h4_history *h,
                                 const struct p309_h4_request *r, const char *g,
                                 int *duplicate) {
  *duplicate = 0;
  /* Match current generation BEFORE ANY request-ID binding/cache access. */
  if (r->has_generation && (!g || strcmp(r->generation, g)))
    return P309_H4_STALE;
  for (size_t i = 0; i < h->used; i++)
    if (!strcmp(h->entries[i].request_id, r->request_id)) {
      const struct p309_h4_request *old = &h->entries[i];
      if (old->stop != r->stop || old->has_generation != r->has_generation ||
          strcmp(old->generation, r->generation))
        return P309_H4_REUSED;
      *duplicate = 1;
      return P309_H4_OK;
    }
  if (h->used == P309_H4_IDS)
    return P309_H4_EXHAUSTED;
  h->entries[h->used++] = *r;
  return P309_H4_OK;
}
