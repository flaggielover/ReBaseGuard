/* Pure parser assertions only, no sockets/manager/keys/process operations. */
#include "h4_wire.h"
#include <assert.h>
#include <string.h>
#define ID "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
static int parse(const char *s) {
  struct p309_h4_request r;
  return p309_h4_parse((const unsigned char *)s, strlen(s), &r);
}
int main(void) {
  assert(
      parse("{\"protocol\":\"P309_DEV_BROKER_CONTROL/2\",\"request_id\":\"" ID
            "\",\"operation\":\"status\",\"generation\":null}"));
  assert(parse("{\"generation\":\"" ID
               "\",\"operation\":\"stop\",\"request_id\":\"" ID
               "\",\"protocol\":\"P309_DEV_BROKER_CONTROL/2\"}"));
  assert(
      !parse("{\"protocol\":\"P309_DEV_BROKER_CONTROL/2\",\"request_id\":\"" ID
             "\",\"operation\":\"start\",\"generation\":\"" ID "\"}"));
  assert(
      !parse("{\"protocol\":\"P309_DEV_BROKER_CONTROL/2\",\"request_id\":\"" ID
             "\",\"operation\":\"stop\",\"generation\":null}"));
  assert(
      !parse("{\"protocol\":\"P309_DEV_BROKER_CONTROL/2\",\"request_id\":\"" ID
             "\",\"operation\":\"status\",\"operation\":\"stop\"}"));
  assert(
      !parse("{\"protocol\":\"P309_DEV_BROKER_CONTROL/2\",\"request_id\":\"" ID
             "\",\"operation\":\"status\",\"generation\":null,\"pid\":1}"));
  assert(
      !parse("{\"protocol\":\"P309_DEV_BROKER_CONTROL/2\",\"request_id\":\"" ID
             "\",\"operation\":\"status\",\"generation\":null}{}"));
  assert(
      !parse("{\"protocol\":\"P309_DEV_BROKER_CONTROL/2\",\"request_id\":\"" ID
             "\",\"operation\":\"sta\\u0074us\",\"generation\":null}"));
  return 0;
}
