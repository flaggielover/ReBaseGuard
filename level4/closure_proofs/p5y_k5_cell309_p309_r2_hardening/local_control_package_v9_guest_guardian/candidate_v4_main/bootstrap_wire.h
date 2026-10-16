#ifndef P309_BOOTSTRAP_WIRE_H
#define P309_BOOTSTRAP_WIRE_H
#include <stddef.h>
#include <stdint.h>
struct p309_boot_inputs {
  char package[65], guest[65], runtime[65], policy[65], root_pin[65], boot[33];
};
int p309_bootstrap_response(const unsigned char *, size_t,
                            const struct p309_boot_inputs *,
                            const unsigned char secret[32],
                            unsigned char out[2048], size_t *);
int p309_root_proof_shape(const unsigned char *, size_t,
                          const struct p309_boot_inputs *, char generation[33],
                          char challenge[65], int blocked);
static inline int p309_frame_length(const unsigned char b[4], size_t *n) {
  uint32_t x = (uint32_t)b[0] | ((uint32_t)b[1] << 8) | ((uint32_t)b[2] << 16) |
               ((uint32_t)b[3] << 24);
  if (!x || x > 8192)
    return 0;
  *n = x;
  return 1;
}
static inline int p309_frame_header(size_t n, unsigned char b[4]) {
  if (!n || n > 8192)
    return 0;
  for (unsigned i = 0; i < 4; i++)
    b[i] = (unsigned char)(n >> (8 * i));
  return 1;
}
#endif
