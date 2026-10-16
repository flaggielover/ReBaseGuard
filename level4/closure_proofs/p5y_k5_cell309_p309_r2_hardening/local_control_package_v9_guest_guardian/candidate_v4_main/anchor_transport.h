#ifndef P309_ANCHOR_TRANSPORT_H
#define P309_ANCHOR_TRANSPORT_H
#include "authority_binding.h"
#include <stddef.h>
/* Dedicated internal relay. Response: canonical ASCII || RSA signature[384].
 * Relay credentials alone never authorize: caller MUST verify signed response.
 * Request is one ASCII frame, optionally followed by guest signature[384]. */
int p309_host_exchange(const struct p309_start_control *, const unsigned char *,
                       size_t, unsigned char[4480], size_t *);
/* One reserve transaction, two ordered signed frames: context then ReserveACK.
 */
int p309_host_reserve_exchange(const struct p309_start_control *,
                               const unsigned char *, size_t,
                               unsigned char[4480], size_t *,
                               unsigned char[4480], size_t *);
int p309_monitor_exchange(const struct p309_start_control *,
                          const unsigned char *, size_t, unsigned char[4480],
                          size_t *);
#endif
