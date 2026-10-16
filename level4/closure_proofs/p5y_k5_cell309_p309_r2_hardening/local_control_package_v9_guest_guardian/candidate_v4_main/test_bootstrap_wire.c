/* Synthetic constants only; no real key, file, endpoint or VM API. */
#include "bootstrap_wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
  struct p309_boot_inputs in = {0};
  char *digests[] = {in.package, in.guest, in.runtime, in.policy, in.root_pin};
  for (size_t i = 0; i < 5; i++) {
    memset(digests[i], 'a', 64);
    digests[i][64] = 0;
  }
  memset(in.boot, 'c', 32);
  in.boot[32] = 0;
  unsigned char secret[32], out[2048];
  for (size_t i = 0; i < 32; i++)
    secret[i] = (unsigned char)i;
  char request[2048], nonce[65];
  memset(nonce, 'b', 64);
  nonce[64] = 0;
  int n =
      snprintf(request, sizeof request,
               "protocol=P309_HOST_BOOT_CHALLENGE/"
               "1\nscope=DEV_FIXED_IDLE_ONLY\nhost_nonce=%s\npackage=%s\nguest="
               "%s\nruntime=%s\npolicy=%s\nguest_root_public_spki_sha256=%s\n",
               nonce, in.package, in.guest, in.runtime, in.policy, in.root_pin);
  size_t z = 0;
  assert(n > 0);
  assert(p309_bootstrap_response((unsigned char *)request, (size_t)n, &in,
                                 secret, out, &z));
  assert(strstr((char *)out, "proof_hmac_sha256="
                             "59af2ec5db1976b8131eec929431ced123e5b08172006887a"
                             "e86f0671d16e596\n") != NULL);
  assert(!p309_bootstrap_response((unsigned char *)request, (size_t)n - 1, &in,
                                  secret, out, &z));
  request[0] = 'X';
  assert(!p309_bootstrap_response((unsigned char *)request, (size_t)n, &in,
                                  secret, out, &z));
  request[0] = 'p';
  in.guest[0] = 'd';
  assert(!p309_bootstrap_response((unsigned char *)request, (size_t)n, &in,
                                  secret, out, &z));
  in.guest[0] = 'a';
  request[n] = '\n';
  assert(!p309_bootstrap_response((unsigned char *)request, (size_t)n + 1, &in,
                                  secret, out, &z));
  puts("PASS fixed-purpose bootstrap canonical/HMAC known-answer and refusal "
       "assertions; synthetic bytes only");
  return 0;
}
