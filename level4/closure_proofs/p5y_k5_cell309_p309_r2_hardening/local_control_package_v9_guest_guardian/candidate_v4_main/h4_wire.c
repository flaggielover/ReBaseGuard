/* Bounded, nonrecursive JSON parser for the existing four-field D2 H4 shape.
 * Accepts ASCII unescaped literals only. Canonical D2 clients are compatible;
 * JSON escape spellings/UTF8 non-ASCII are refused, never normalized. */
#include "h4_wire.h"
#include <string.h>
struct cursor {
  const unsigned char *s;
  size_t n, at;
};
static void space(struct cursor *c) {
  while (c->at < c->n && (c->s[c->at] == ' ' || c->s[c->at] == '\t' ||
                          c->s[c->at] == '\n' || c->s[c->at] == '\r'))
    c->at++;
}
static int take(struct cursor *c, unsigned char ch) {
  space(c);
  if (c->at >= c->n || c->s[c->at++] != ch)
    return 0;
  return 1;
}
static int string(struct cursor *c, char *out, size_t cap) {
  if (!take(c, '"'))
    return 0;
  size_t n = 0;
  while (c->at < c->n) {
    unsigned char ch = c->s[c->at++];
    if (ch == '"') {
      out[n] = 0;
      return 1;
    }
    if (ch < 32 || ch > 126 || ch == '\\' || n + 1 >= cap)
      return 0;
    out[n++] = (char)ch;
  }
  return 0;
}
static int id(const char *s) {
  if (strlen(s) != 32)
    return 0;
  for (size_t i = 0; i < 32; i++)
    if (!((s[i] >= 'a' && s[i] <= 'f') || (s[i] >= '0' && s[i] <= '9')))
      return 0;
  return 1;
}
int p309_h4_parse(const unsigned char *raw, size_t n,
                  struct p309_h4_request *out) {
  if (!raw || !out || !n || n > 16384)
    return 0;
  struct cursor c = {raw, n, 0};
  struct p309_h4_request r = {0};
  unsigned seen = 0;
  if (!take(&c, '{'))
    return 0;
  for (size_t i = 0; i < 4; i++) {
    char key[32], value[65];
    unsigned bit;
    if (i && !take(&c, ','))
      return 0;
    if (!string(&c, key, sizeof key) || !take(&c, ':'))
      return 0;
    if (!strcmp(key, "protocol"))
      bit = 1;
    else if (!strcmp(key, "request_id"))
      bit = 2;
    else if (!strcmp(key, "operation"))
      bit = 4;
    else if (!strcmp(key, "generation"))
      bit = 8;
    else
      return 0;
    if (seen & bit)
      return 0;
    seen |= bit;
    space(&c);
    if (bit == 8 && c.n - c.at >= 4 && !memcmp(c.s + c.at, "null", 4)) {
      c.at += 4;
      r.has_generation = 0;
      continue;
    }
    if (!string(&c, value, sizeof value))
      return 0;
    if (bit == 1) {
      if (strcmp(value, "P309_DEV_BROKER_CONTROL/2"))
        return 0;
    } else if (bit == 2) {
      if (!id(value))
        return 0;
      memcpy(r.request_id, value, 33);
    } else if (bit == 4) {
      if (!strcmp(value, "stop"))
        r.stop = 1;
      else if (strcmp(value, "status"))
        return 0;
    } else {
      if (!id(value))
        return 0;
      memcpy(r.generation, value, 33);
      r.has_generation = 1;
    }
  }
  if (seen != 15 || !take(&c, '}'))
    return 0;
  space(&c);
  if (c.at != c.n || (r.stop && !r.has_generation))
    return 0;
  *out = r;
  return 1;
}
