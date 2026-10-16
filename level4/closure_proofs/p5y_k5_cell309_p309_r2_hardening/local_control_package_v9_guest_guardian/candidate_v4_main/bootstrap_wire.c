/* Fixed DEV purpose only; no arbitrary message/key signing service. */
#include "bootstrap_wire.h"
#include <openssl/crypto.h>
#include <openssl/hmac.h>
#include <stdio.h>
#include <string.h>
static int hex(const char *s, size_t n) {
  if (strlen(s) != n)
    return 0;
  for (size_t i = 0; i < n; i++)
    if (!((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'a' && s[i] <= 'f')))
      return 0;
  return 1;
}
static int fields(const unsigned char *b, size_t n, const char *const *keys,
                  size_t count, char v[][65]) {
  size_t at = 0;
  for (size_t i = 0; i < count; i++) {
    size_t k = strlen(keys[i]), z = 0;
    if (at + k + 2 > n || memcmp(b + at, keys[i], k) || b[at + k] != '=')
      return 0;
    at += k + 1;
    while (at < n && b[at] != '\n') {
      unsigned char c = b[at++];
      if (c < 33 || c > 126 || c == '=' || z >= 64)
        return 0;
      v[i][z++] = (char)c;
    }
    if (at >= n || !z)
      return 0;
    v[i][z] = 0;
    at++;
  }
  return at == n;
}
int p309_bootstrap_response(const unsigned char *b, size_t n,
                            const struct p309_boot_inputs *in,
                            const unsigned char secret[32],
                            unsigned char out[2048], size_t *len) {
  static const char *const keys[] = {
      "protocol", "scope",   "host_nonce", "package",
      "guest",    "runtime", "policy",     "guest_root_public_spki_sha256"};
  char v[8][65];
  *len = 0;
  if (n > 2048 || !fields(b, n, keys, 8, v) ||
      strcmp(v[0], "P309_HOST_BOOT_CHALLENGE/1") ||
      strcmp(v[1], "DEV_FIXED_IDLE_ONLY") || !hex(v[2], 64) ||
      !hex(in->boot, 32) || strcmp(v[3], in->package) ||
      strcmp(v[4], in->guest) || strcmp(v[5], in->runtime) ||
      strcmp(v[6], in->policy) || strcmp(v[7], in->root_pin))
    return 0;
  int q = snprintf(
      (char *)out, 2048,
      "protocol=P309_GUEST_BOOTSTRAP/"
      "1\nscope=DEV_FIXED_IDLE_ONLY\nhost_nonce=%s\nguest_boot=%s\npackage=%"
      "s\nguest=%s\nruntime=%s\npolicy=%s\nguest_root_public_spki_sha256=%s\n",
      v[2], in->boot, in->package, in->guest, in->runtime, in->policy,
      in->root_pin);
  if (q <= 0 || q >= 1900)
    return 0;
  unsigned char hmac[32];
  unsigned int hn = 0;
  if (!HMAC(EVP_sha256(), secret, 32, out, (size_t)q, hmac, &hn) || hn != 32)
    return 0;
  char digest[65];
  for (size_t i = 0; i < 32; i++)
    snprintf(digest + 2 * i, 3, "%02x", hmac[i]);
  OPENSSL_cleanse(hmac, sizeof hmac);
  int z = snprintf((char *)out + q, 2048 - (size_t)q, "proof_hmac_sha256=%s\n",
                   digest);
  if (z <= 0 || (size_t)z >= 2048 - (size_t)q)
    return 0;
  *len = (size_t)q + (size_t)z;
  return 1;
}
int p309_root_proof_shape(const unsigned char *b, size_t n,
                          const struct p309_boot_inputs *in, char g[33],
                          char challenge[65], int blocked) {
  static const char *const pre[] = {"protocol",
                                    "scope",
                                    "G",
                                    "guest_boot",
                                    "package",
                                    "guest",
                                    "runtime",
                                    "policy",
                                    "challenge",
                                    "approval_sha256",
                                    "guest_root_public_spki_sha256"};
  static const char *const post[] = {"protocol",
                                     "scope",
                                     "G",
                                     "host_epoch_seq",
                                     "host_boot",
                                     "guest_boot",
                                     "package",
                                     "guest",
                                     "runtime",
                                     "policy",
                                     "workerInv",
                                     "brokerInv",
                                     "guardianInv",
                                     "challenge",
                                     "reserve_record_seq",
                                     "reserve_record_sha256",
                                     "anchor_binding_sha256",
                                     "checkpoint",
                                     "vm_lifetime_sha256",
                                     "guest_root_public_spki_sha256"};
  char v[20][65];
  if (n <= 384 || n > 4480 ||
      !fields(b, n - 384, blocked ? post : pre, blocked ? 20 : 11, v) ||
      strcmp(v[0], blocked ? "P309_GUEST_BLOCKED_INVOCATION/1"
                           : "P309_GUEST_ROOT_PRESTART/1") ||
      strcmp(v[1], "DEV_FIXED_IDLE_ONLY") || !hex(v[2], 32))
    return 0;
  size_t boot = blocked ? 5 : 3, pkg = blocked ? 6 : 4, ch = blocked ? 13 : 8,
         pin = blocked ? 19 : 10;
  if (strcmp(v[boot], in->boot) || strcmp(v[pkg], in->package) ||
      strcmp(v[pkg + 1], in->guest) || strcmp(v[pkg + 2], in->runtime) ||
      strcmp(v[pkg + 3], in->policy) || strcmp(v[pin], in->root_pin) ||
      !hex(v[ch], 64))
    return 0;
  if (blocked)
    return !strcmp(v[2], g) && !strcmp(v[ch], challenge);
  memcpy(g, v[2], 33);
  memcpy(challenge, v[ch], 65);
  return 1;
}
