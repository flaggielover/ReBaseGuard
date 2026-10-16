/* Internal trusted-root protocol only; never H3/H4 or formal run authority. */
#ifndef P309_PROTOCOL_H
#define P309_PROTOCOL_H
#include <stddef.h>
#include <string.h>
#define P309_CGROUP "/sys/fs/cgroup/system.slice/p309-dev-owned-check.service"
#define P309_MEMBER "0::/system.slice/p309-dev-owned-check.service\n"
#define P309_GUARD_SOCKET "/run/rebaseguard-p309/guardian-v9.sock"
#define P309_GATE_SOCKET "/run/rebaseguard-p309/launch-gate-v9.sock"
#define P309_IDLE "/usr/local/libexec/rebaseguard-p309/idle-owned-v9"
#define P309_PACKET_MAX 96
static inline int p309_generation(const char *g) {
  for (size_t i = 0; i < 32; i++)
    if (!((g[i] >= '0' && g[i] <= '9') || (g[i] >= 'a' && g[i] <= 'f')))
      return 0;
  return g[32] == 0;
}
static inline int p309_parse(const char *raw, size_t n, const char *verb,
                             char g[33]) {
  size_t v = strlen(verb);
  if (n != v + 34 || memcmp(raw, verb, v) || raw[v] != ' ' ||
      raw[n - 1] != '\n')
    return 0;
  memcpy(g, raw + v + 1, 32);
  g[32] = 0;
  return p309_generation(g);
}
static inline size_t p309_packet(char out[P309_PACKET_MAX], const char *verb,
                                 const char *g) {
  size_t v = strlen(verb);
  if (!p309_generation(g) || v + 34 > P309_PACKET_MAX)
    return 0;
  memcpy(out, verb, v);
  out[v] = ' ';
  memcpy(out + v + 1, g, 32);
  out[v + 33] = '\n';
  return v + 34;
}
#endif
