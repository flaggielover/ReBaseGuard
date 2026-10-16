#ifndef P309_H4_WIRE_H
#define P309_H4_WIRE_H
#include <stddef.h>
struct p309_h4_request {
  char request_id[33], generation[33];
  int stop, has_generation;
};
int p309_h4_parse(const unsigned char *, size_t, struct p309_h4_request *);
#endif
