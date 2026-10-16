#ifndef P309_ANCHOR_CRYPTO_H
#define P309_ANCHOR_CRYPTO_H
#include <stddef.h>
/* Verification only. No key generation, trust-on-first-use, signing oracle,
 * network listener, D2 model or caller-selected trust file. */
int p309_anchor_verify(const unsigned char *,size_t,const unsigned char signature[384]);
#endif
