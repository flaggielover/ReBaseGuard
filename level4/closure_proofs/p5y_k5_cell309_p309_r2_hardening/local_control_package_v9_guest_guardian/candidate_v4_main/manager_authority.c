/* Real libsystemd transaction and independent authority verification.
 * Linux static source only in this preparation. No model/fake adapter selected.
 * Fixed idle permit is separate from and cannot represent formal P309 grants.
 */
#define _GNU_SOURCE
#include "anchor_crypto.h"
#include "anchor_transport.h"
#include "authority_binding.h"
#include "held_stop_write.h"
#include "protocol.h"
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <limits.h>
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <poll.h>
#include <pwd.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/random.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <sys/syscall.h>
#include <systemd/sd-bus.h>
#include <time.h>
#include <unistd.h>
_Static_assert(ATOMIC_LLONG_LOCK_FREE == 2 && ATOMIC_INT_LOCK_FREE == 2,
               "Stop/lease atomics must be lock-free");
#define BROKER "rebaseguard-p309-control.service"
#define WORKER "p309-dev-owned-check.service"
#define BROKER_EXE "/usr/local/libexec/rebaseguard-p309/control-broker-v9"
#define GATE_EXE "/usr/local/libexec/rebaseguard-p309/fixed-gate-v9"
#define RECORD_DIR "/run/rebaseguard-p309/bindings-v9"
#define STATE_DIR "/var/lib/rebaseguard-p309-control"
#define PACKAGE_DIR "/etc/rebaseguard-p309"
#define DEST "org.freedesktop.systemd1"
#define MGR "/org/freedesktop/systemd1"
#define MI "org.freedesktop.systemd1.Manager"
#define UI "org.freedesktop.systemd1.Unit"
#define SI "org.freedesktop.systemd1.Service"
struct binding_record {
  char magic[16], generation[33], boot[37], broker_inv[33], worker_inv[33],
      package[65], approval[65];
  uint32_t broker_pid, worker_pid, job_id, reserved;
  uint64_t broker_start, worker_start, cgroup_dev, cgroup_ino, kill_ino,
      broker_exec_start;
};
#define START_DISPATCHED 1u
#define RELEASE_PREPARING 2u
#define RELEASE_DISPATCHED 4u
#define STOP_LATCHED 8u
struct host_binding {
  char guest[65], runtime[65], policy[65], challenge[65], guest_boot[33],
      host_boot[33], epoch[21], anchor[65], checkpoint[65], reserve_record[65],
      guardian_inv[33], vm_lifetime[65], guest_pin[65];
  uint64_t reserve_seq;
  int reserved;
  struct p309_peer_identity *relay;
  atomic_int guardian_ready, final_consumed, reserve_attempted, relay_published;
};
struct p309_safety_state {
  atomic_int polling;
  uint64_t sequence, last_signed, last_end, frequency, suspend_epoch;
  char previous[65], source[33];
  struct p309_peer_identity *monitor;
};
struct p309_start_authority {
  struct binding_record r;
  int f[4];
  atomic_int handoff_claimed, owned, stop_write;
  sd_bus *manager_ref;
  struct p309_start_control *control;
  struct host_binding host;
  struct p309_safety_state safety;
};
void p309_start_cancel(struct p309_start_control *c) {
  if (c) {
    atomic_fetch_or(&c->state, STOP_LATCHED);
    p309_lease_stop(&c->lease);
  }
}
int p309_start_is_cancelled(const struct p309_start_control *c) {
  return !c || !!(atomic_load(&c->state) & STOP_LATCHED);
}
int p309_authority_stopped(const struct p309_start_authority *a) {
  return !a || !a->control ||
         !!(atomic_load(&a->control->state) & STOP_LATCHED);
}
void p309_authority_stop(const struct p309_start_authority *a) {
  if (a)
    p309_start_cancel(a->control);
}
static int64_t clock_ns(void);
static int64_t stop_clock(void *ctx) {
  (void)ctx;
  return clock_ns();
}
static long stop_write_once(int fd, void *ctx) {
  (void)ctx;
  return (long)write(fd, "1\n", 2);
}
int p309_authority_request_stop_owned(const struct p309_start_authority *a) {
  if (!a)
    return -EINVAL;
  p309_authority_stop(a);
  if (!atomic_load(&a->owned))
    return -EAGAIN;
  int expected = 0;
  if (!atomic_compare_exchange_strong(
          &((struct p309_start_authority *)a)->stop_write, &expected, 1))
    return expected == 2 ? 0 : -EIO;
  int ok = p309_stop_write_bounded(a->f[3], stop_write_once, stop_clock, NULL);
  atomic_store(&((struct p309_start_authority *)a)->stop_write, ok ? 2 : 3);
  return ok ? 0 : -EIO;
}
int p309_authority_release_begin(const struct p309_start_authority *a) {
  unsigned expected = START_DISPATCHED;
  return a && a->control && p309_authority_safety_current(a) &&
         atomic_compare_exchange_strong(&a->control->state, &expected,
                                        START_DISPATCHED | RELEASE_PREPARING);
}
int p309_authority_release_pending(const struct p309_start_authority *a) {
  return a && a->control &&
         atomic_load(&a->control->state) ==
             (START_DISPATCHED | RELEASE_PREPARING);
}
int p309_authority_release_commit(const struct p309_start_authority *a) {
  unsigned expected = START_DISPATCHED | RELEASE_PREPARING;
  return a && a->control && p309_authority_safety_current(a) &&
         atomic_load(&a->host.final_consumed) == 2 &&
         atomic_compare_exchange_strong(&a->control->state, &expected,
                                        START_DISPATCHED | RELEASE_PREPARING |
                                            RELEASE_DISPATCHED);
}
static struct p309_start_authority verified;
static struct {
  uint32_t pid;
  char inv[33];
  sd_bus *bus;
  int fd;
} guardian_record = {0};
static int64_t clock_ns(void) {
  struct timespec t;
  if (clock_gettime(CLOCK_BOOTTIME, &t))
    return -1;
  return (int64_t)t.tv_sec * 1000000000LL + t.tv_nsec;
}
static int directory(const char *path) {
  if (path[0] != '/') {
    errno = EINVAL;
    return -1;
  }
  char copy[PATH_MAX];
  if (strlen(path) >= sizeof copy)
    return -1;
  strcpy(copy, path);
  int fd = open("/", O_RDONLY | O_CLOEXEC | O_DIRECTORY | O_NOFOLLOW);
  if (fd < 0)
    return -1;
  char *save = NULL;
  struct stat st;
  for (char *s = strtok_r(copy, "/", &save); s;
       s = strtok_r(NULL, "/", &save)) {
    if (!strcmp(s, ".") || !strcmp(s, "..") || fstat(fd, &st) ||
        st.st_uid != 0 || (st.st_mode & 0022)) {
      close(fd);
      return -1;
    }
    int next = openat(fd, s, O_RDONLY | O_CLOEXEC | O_DIRECTORY | O_NOFOLLOW);
    close(fd);
    fd = next;
    if (fd < 0)
      return -1;
  }
  if (fstat(fd, &st) || st.st_uid != 0 || (st.st_mode & 0022)) {
    close(fd);
    return -1;
  }
  return fd;
}
static int read_fixed(int d, const char *name, void *out, size_t bytes,
                      mode_t mode) {
  int f = openat(d, name, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (f < 0)
    return -1;
  struct stat st;
  if (fstat(f, &st) || !S_ISREG(st.st_mode) || st.st_uid != 0 ||
      (st.st_mode & 0777) != mode || st.st_nlink != 1 ||
      st.st_size != (off_t)bytes) {
    close(f);
    return -1;
  }
  size_t at = 0;
  while (at < bytes) {
    ssize_t n = read(f, (char *)out + at, bytes - at);
    if (n < 0 && errno == EINTR)
      continue;
    if (n <= 0) {
      close(f);
      return -1;
    }
    at += (size_t)n;
  }
  char extra;
  int ok = read(f, &extra, 1) == 0;
  close(f);
  return ok ? 0 : -1;
}
static int write_all(int fd, const void *data, size_t bytes) {
  size_t at = 0;
  while (at < bytes) {
    ssize_t n = write(fd, (const char *)data + at, bytes - at);
    if (n < 0 && errno == EINTR)
      continue;
    if (n <= 0)
      return -1;
    at += (size_t)n;
  }
  return 0;
}
static int hex64(const char *s) {
  for (int i = 0; i < 64; i++)
    if (!((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'a' && s[i] <= 'f')))
      return 0;
  return s[64] == 0;
}
static int installed_digest(const char *name, char out[65]) {
  int d = directory(PACKAGE_DIR);
  if (d < 0)
    return 0;
  char raw[65];
  int ok = !read_fixed(d, name, raw, sizeof raw, 0444);
  close(d);
  if (!ok || raw[64] != '\n')
    return 0;
  memcpy(out, raw, 64);
  out[64] = 0;
  return hex64(out);
}
static int package_hash(char out[65]) {
  int d = directory(PACKAGE_DIR);
  if (d < 0)
    return -1;
  char raw[65];
  int rc = read_fixed(d, "package-v9.sha256", raw, 65, 0444);
  close(d);
  if (rc || raw[64] != '\n')
    return -1;
  memcpy(out, raw, 64);
  out[64] = 0;
  return hex64(out) ? 0 : -1;
}
static int boot(char out[37]) {
  int f = open("/proc/sys/kernel/random/boot_id", O_RDONLY | O_CLOEXEC);
  if (f < 0)
    return -1;
  char raw[38];
  ssize_t n = read(f, raw, sizeof raw);
  close(f);
  if (n != 37 || raw[36] != '\n')
    return -1;
  memcpy(out, raw, 36);
  out[36] = 0;
  return 0;
}
static uint64_t start_ticks(pid_t pid) {
  char path[64], buf[4097];
  snprintf(path, sizeof path, "/proc/%ld/stat", (long)pid);
  int f = open(path, O_RDONLY | O_CLOEXEC);
  if (f < 0)
    return 0;
  ssize_t n = read(f, buf, sizeof buf - 1);
  close(f);
  if (n <= 0 || n == (ssize_t)sizeof buf - 1)
    return 0;
  buf[n] = 0;
  char *last = strrchr(buf, ')');
  if (!last || last[1] != ' ')
    return 0;
  char *save = NULL, *field = strtok_r(last + 2, " ", &save);
  for (int i = 0; i < 19 && field; i++)
    field = strtok_r(NULL, " ", &save);
  if (!field)
    return 0;
  char *end;
  errno = 0;
  unsigned long long v = strtoull(field, &end, 10);
  return errno || *end ? 0 : (uint64_t)v;
}
static int exe_is(pid_t pid, const char *expected) {
  char p[64], v[PATH_MAX];
  snprintf(p, sizeof p, "/proc/%ld/exe", (long)pid);
  ssize_t n = readlink(p, v, sizeof v - 1);
  if (n < 0 || (size_t)n >= sizeof v - 1)
    return 0;
  v[n] = 0;
  if (strcmp(v, expected))
    return 0;
  struct stat st;
  if (stat(p, &st) || !S_ISREG(st.st_mode) || st.st_uid != 0 ||
      (st.st_mode & 0022))
    return 0;
  return 1;
}
static int alive(int fd) {
  struct pollfd p = {fd, POLLIN, 0};
  return poll(&p, 1, 0) == 0;
}
static int pidfd(pid_t pid) { return (int)syscall(SYS_pidfd_open, pid, 0); }
static int unit(sd_bus *b, const char *name, char **path) {
  sd_bus_message *m = NULL;
  sd_bus_error e = SD_BUS_ERROR_NULL;
  int rc = sd_bus_call_method(b, DEST, MGR, MI, "GetUnit", &e, &m, "s", name);
  const char *p = NULL;
  if (rc >= 0)
    rc = sd_bus_message_read(m, "o", &p);
  if (rc == 0 || (rc > 0 && !p))
    rc = -EBADMSG;
  if (rc >= 0 && p) {
    *path = strdup(p);
    if (!*path)
      rc = -ENOMEM;
  }
  sd_bus_error_free(&e);
  sd_bus_message_unref(m);
  return rc;
}
static int property_string(sd_bus *b, const char *p, const char *iface,
                           const char *key, const char *expected) {
  char *value = NULL;
  int rc = sd_bus_get_property_string(b, DEST, p, iface, key, NULL, &value);
  int ok = rc >= 0 && value && !strcmp(value, expected);
  free(value);
  return ok;
}
static int invocation(sd_bus *b, const char *p, char out[33]) {
  sd_bus_message *m = NULL;
  int rc = sd_bus_get_property(b, DEST, p, UI, "InvocationID", NULL, &m, "ay");
  const void *v = NULL;
  size_t n = 0;
  if (rc >= 0)
    rc = sd_bus_message_read_array(m, 'y', &v, &n);
  if (rc >= 0 && n == 16) {
    const unsigned char *a = v;
    for (int i = 0; i < 16; i++)
      snprintf(out + 2 * i, 3, "%02x", a[i]);
  } else
    rc = -EINVAL;
  sd_bus_message_unref(m);
  return rc;
}
static int facts(sd_bus *b, const char *name, uint32_t *pid, char inv[33],
                 int worker) {
  char *p = NULL;
  if (unit(b, name, &p) < 0)
    return -1;
  uint32_t main = 0, exec = 0;
  int ok = property_string(b, p, UI, "Id", name) &&
           property_string(b, p, UI, "ActiveState", "active") &&
           property_string(b, p, UI, "SubState", "running") &&
           sd_bus_get_property_trivial(b, DEST, p, SI, "MainPID", NULL, 'u',
                                       &main) >= 0 &&
           sd_bus_get_property_trivial(b, DEST, p, SI, "ExecMainPID", NULL, 'u',
                                       &exec) >= 0 &&
           main > 1 && main == exec && invocation(b, p, inv) >= 0;
  if (worker)
    ok = ok &&
         property_string(b, p, SI, "ControlGroup", "/system.slice/" WORKER);
  sd_bus_message *m = NULL;
  uint32_t job = 1;
  const char *jobpath = NULL;
  if (sd_bus_get_property(b, DEST, p, UI, "Job", NULL, &m, "(uo)") < 0 ||
      sd_bus_message_read(m, "(uo)", &job, &jobpath) < 0 || job)
    ok = 0;
  sd_bus_message_unref(m);
  free(p);
  if (ok)
    *pid = main;
  return ok ? 0 : -1;
}
struct p309_peer_identity {
  pid_t pid;
  uid_t uid;
  uint64_t start;
  char invocation[33], code_sha256[65];
  int fd, execfd;
  dev_t exe_dev;
  ino_t exe_ino;
  sd_bus *bus;
  const char *unit;
};
static int peer_code_pin(struct p309_peer_identity *p, const char *pin_name) {
  char path[64], expected[65];
  snprintf(path, sizeof path, "/proc/%ld/exe", (long)p->pid);
  if (!installed_digest(pin_name, expected))
    return 0;
  p->execfd = open(path, O_RDONLY | O_CLOEXEC);
  if (p->execfd < 0)
    return 0;
  struct stat s;
  if (fstat(p->execfd, &s) || !S_ISREG(s.st_mode) || s.st_uid ||
      (s.st_mode & 0022) || s.st_size <= 0 || s.st_size > 67108864)
    return 0;
  p->exe_dev = s.st_dev;
  p->exe_ino = s.st_ino;
  EVP_MD_CTX *ctx = EVP_MD_CTX_new();
  if (!ctx)
    return 0;
  int ok = EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) > 0;
  unsigned char buffer[16384], digest[32];
  unsigned int dn = 0;
  off_t total = 0;
  while (ok) {
    ssize_t n = read(p->execfd, buffer, sizeof buffer);
    if (n < 0) {
      if (errno == EINTR)
        continue;
      ok = 0;
      break;
    }
    if (!n)
      break;
    total += n;
    if (total > s.st_size || EVP_DigestUpdate(ctx, buffer, (size_t)n) <= 0)
      ok = 0;
  }
  if (total != s.st_size || EVP_DigestFinal_ex(ctx, digest, &dn) <= 0 ||
      dn != 32)
    ok = 0;
  EVP_MD_CTX_free(ctx);
  if (!ok)
    return 0;
  for (size_t i = 0; i < 32; i++)
    snprintf(p->code_sha256 + 2 * i, 3, "%02x", digest[i]);
  return !strcmp(p->code_sha256, expected);
}
struct p309_peer_identity *p309_peer_acquire(enum p309_peer_role role,
                                             pid_t expected) {
  if (geteuid() != 0)
    return NULL;
  const char *name, *exe, *pin_name;
  uid_t uid = 0;
  if (role == P309_PEER_MONITOR) {
    name = "rebaseguard-p309-monitor.service";
    exe = "/usr/local/libexec/rebaseguard-p309/monitor-v9";
    pin_name = "monitor-v9.sha256";
    struct passwd pw, *out = NULL;
    char buf[16384];
    if (getpwnam_r("p309-monitor", &pw, buf, sizeof buf, &out) || !out ||
        !pw.pw_uid)
      return NULL;
    uid = pw.pw_uid;
  } else if (role == P309_PEER_ADMIN) {
    name = "rebaseguard-p309-admin-helper.service";
    exe = "/usr/local/libexec/rebaseguard-p309/admin-helper-v9";
    pin_name = "admin-helper-v9.sha256";
  } else if (role == P309_PEER_BROKER) {
    name = BROKER;
    exe = BROKER_EXE;
    pin_name = "control-broker-v9.sha256";
  } else if (role == P309_PEER_RELAY) {
    name = "rebaseguard-p309-host-h2-relay.service";
    exe = "/usr/local/libexec/rebaseguard-p309/host-h2-relay-v11";
    pin_name = "host-h2-relay-v11.sha256";
  } else
    return NULL;
  struct p309_peer_identity *p = calloc(1, sizeof *p);
  if (!p)
    return NULL;
  p->fd = -1;
  p->execfd = -1;
  p->unit = name;
  p->uid = uid;
  if (sd_bus_open_system(&p->bus) < 0)
    goto fail;
  sd_bus_set_method_call_timeout(p->bus, 2000000);
  uint32_t actual;
  char *path = NULL;
  if (facts(p->bus, name, &actual, p->invocation, 0) || actual <= 1 ||
      (expected > 0 && actual != (uint32_t)expected) ||
      !exe_is((pid_t)actual, exe))
    goto fail;
  p->pid = (pid_t)actual;
  p->start = start_ticks(p->pid);
  p->fd = pidfd(p->pid);
  if (!p->start || p->fd < 0 || !alive(p->fd) ||
      start_ticks(p->pid) != p->start || unit(p->bus, name, &path) < 0)
    goto fail;
  uint32_t actual_uid = UINT32_MAX;
  int ok = sd_bus_get_property_trivial(p->bus, DEST, path, SI, "UID", NULL, 'u',
                                       &actual_uid) >= 0 &&
           actual_uid == uid;
  free(path);
  if (!ok)
    goto fail;
  if (!peer_code_pin(p, pin_name) || !p309_peer_alive(p) ||
      sd_bus_call_method(p->bus, DEST, MGR, MI, "RefUnit", NULL, NULL, "s",
                         name) < 0)
    goto fail;
  return p;
fail:
  if (p->fd >= 0)
    close(p->fd);
  if (p->execfd >= 0)
    close(p->execfd);
  sd_bus_unref(p->bus);
  free(p);
  return NULL;
}
int p309_peer_matches(const struct p309_peer_identity *p, pid_t pid,
                      uid_t uid) {
  return p && p->pid == pid && p->uid == uid && p309_peer_alive(p);
}
int p309_peer_alive(const struct p309_peer_identity *p) {
  if (!p || !alive(p->fd))
    return 0;
  char path[64];
  struct stat s;
  snprintf(path, sizeof path, "/proc/%ld/exe", (long)p->pid);
  return !stat(path, &s) && s.st_dev == p->exe_dev && s.st_ino == p->exe_ino &&
         s.st_uid == 0 && !(s.st_mode & 0022);
}
int p309_peer_pidfd(const struct p309_peer_identity *p) {
  return p ? p->fd : -1;
}
void p309_peer_destroy_after_join(struct p309_peer_identity *p) {
  if (!p)
    return;
  (void)sd_bus_call_method(p->bus, DEST, MGR, MI, "UnrefUnit", NULL, NULL, "s",
                           p->unit);
  sd_bus_unref(p->bus);
  close(p->fd);
  close(p->execfd);
  free(p);
}
int p309_authority_monitor_is(const struct p309_start_authority *a,
                              const struct p309_peer_identity *expected) {
  if (!a || !expected || !p309_peer_alive(expected) ||
      !p309_peer_alive(a->safety.monitor))
    return 0;
  const struct p309_peer_identity *actual = a->safety.monitor;
  return actual->pid == expected->pid && actual->uid == expected->uid &&
         actual->start == expected->start &&
         !strcmp(actual->invocation, expected->invocation) &&
         !strcmp(actual->code_sha256, expected->code_sha256);
}
static int broker_facts(sd_bus *b, pid_t peer, struct binding_record *r) {
  uint32_t p;
  char inv[33];
  if (facts(b, BROKER, &p, inv, 0) || p != (uint32_t)peer)
    return -1;
  /* Non-root gate cannot assume ptrace-style readlink access to root /proc/exe.
   * It uses manager-owned InvocationID+PID+ExecMainStartTimestampMonotonic.
   * Root broker/guardian additionally validate executable and /proc start. */
  uint64_t ticks = 0;
  if (geteuid() == 0) {
    if (!exe_is(peer, BROKER_EXE) || (ticks = start_ticks(peer)) == 0)
      return -1;
  }
  char *path = NULL;
  uint64_t stamp = 0;
  if (unit(b, BROKER, &path) < 0)
    return -1;
  int ok = sd_bus_get_property_trivial(b, DEST, path, SI,
                                       "ExecMainStartTimestampMonotonic", NULL,
                                       't', &stamp) >= 0 &&
           stamp;
  free(path);
  if (!ok)
    return -1;
  r->broker_pid = p;
  r->broker_start = ticks;
  r->broker_exec_start = stamp;
  memcpy(r->broker_inv, inv, 33);
  return 0;
}
static int record_read(struct binding_record *r) {
  int d = directory(RECORD_DIR);
  if (d < 0)
    return -1;
  int rc = read_fixed(d, "active-v9.bin", r, sizeof *r, 0444);
  close(d);
  if (rc || memcmp(r->magic, "P309_GUARD_V9\0\0\0", 16) ||
      !p309_generation(r->generation) || !hex64(r->package) ||
      !hex64(r->approval) || !r->job_id || r->reserved)
    return -1;
  char current_boot[37], package[65];
  if (boot(current_boot) || package_hash(package) ||
      memcmp(current_boot, r->boot, 37) || memcmp(package, r->package, 65))
    return -1;
  return 0;
}
static int trivial_is(sd_bus *b, const char *p, const char *iface,
                      const char *key, char type, uint64_t expected) {
  uint64_t t = 0;
  uint32_t u = 0;
  int i = 0;
  void *v = type == 't' ? (void *)&t : type == 'u' ? (void *)&u : (void *)&i;
  if (sd_bus_get_property_trivial(b, DEST, p, iface, key, NULL, type, v) < 0)
    return 0;
  return (type == 't' ? t : type == 'u' ? u : (uint64_t)i) == expected;
}
static int empty_array(sd_bus *b, const char *p, const char *iface,
                       const char *key, const char *element) {
  sd_bus_message *m = NULL;
  char signature[80];
  snprintf(signature, sizeof signature, "a%s", element);
  int ok =
      sd_bus_get_property(b, DEST, p, iface, key, NULL, &m, signature) >= 0 &&
      sd_bus_message_enter_container(m, 'a', element) > 0 &&
      sd_bus_message_at_end(m, 0) > 0;
  sd_bus_message_unref(m);
  return ok;
}
static int exec_start_is_fixed(sd_bus *b, const char *p) {
  sd_bus_message *m = NULL;
  const char *exe = NULL, *arg = NULL;
  int ignore = 1;
  uint64_t x1, x2, x3, x4;
  uint32_t pid;
  int code, status;
  int ok = sd_bus_get_property(b, DEST, p, SI, "ExecStart", NULL, &m,
                               "a(sasbttttuii)") >= 0 &&
           sd_bus_message_enter_container(m, 'a', "(sasbttttuii)") > 0 &&
           sd_bus_message_enter_container(m, 'r', "sasbttttuii") > 0 &&
           sd_bus_message_read(m, "s", &exe) > 0 && !strcmp(exe, GATE_EXE) &&
           sd_bus_message_enter_container(m, 'a', "s") > 0 &&
           sd_bus_message_read(m, "s", &arg) > 0 && !strcmp(arg, GATE_EXE) &&
           sd_bus_message_at_end(m, 0) > 0 &&
           sd_bus_message_exit_container(m) >= 0 &&
           sd_bus_message_read(m, "bttttuii", &ignore, &x1, &x2, &x3, &x4, &pid,
                               &code, &status) > 0 &&
           !ignore && sd_bus_message_at_end(m, 0) > 0 &&
           sd_bus_message_exit_container(m) >= 0 &&
           sd_bus_message_at_end(m, 0) > 0;
  sd_bus_message_unref(m);
  return ok;
}
static int worker_policy(sd_bus *b, const char *p) {
  /* Actual readback, not merely the values sent in StartTransientUnit.
   * Reject unsupported properties rather than assume a permissive default. */
  const char *strings[][2] = {{"Type", "exec"},
                              {"User", "p309-runner"},
                              {"Group", "p309-runner"},
                              {"Restart", "no"},
                              {"KillMode", "control-group"},
                              {"ProtectSystem", "strict"},
                              {"StandardInput", "null"},
                              {"StandardOutput", "null"},
                              {"StandardError", "null"},
                              {"ControlGroup", "/system.slice/" WORKER}};
  const char *yes[] = {"NoNewPrivileges", "PrivateTmp", "PrivateDevices",
                       "ProtectControlGroups", "SendSIGKILL"};
  struct {
    const char *name;
    uint64_t value;
  } limits[] = {{"RuntimeMaxUSec", 120000000},
                {"TimeoutStopUSec", 10000000},
                {"MemoryMax", 67108864},
                {"TasksMax", 8},
                {"CPUWeight", 1},
                {"IOWeight", 1},
                {"AmbientCapabilities", 0},
                {"CapabilityBoundingSet", 0}};
  const char *emptyexec[] = {"ExecCondition", "ExecStartPre", "ExecStartPost",
                             "ExecReload",    "ExecStop",     "ExecStopPost"};
  if (!property_string(b, p, UI, "Id", WORKER) ||
      !property_string(b, p, UI, "FragmentPath",
                       "/run/systemd/transient/" WORKER) ||
      !property_string(b, p, UI, "SourcePath", "") ||
      !trivial_is(b, p, UI, "Transient", 'b', 1) ||
      !empty_array(b, p, UI, "DropInPaths", "s") ||
      !empty_array(b, p, SI, "SupplementaryGroups", "s") ||
      !trivial_is(b, p, SI, "Delegate", 'b', 0) ||
      !trivial_is(b, p, SI, "DynamicUser", 'b', 0) ||
      !trivial_is(b, p, SI, "KillSignal", 'i', SIGKILL) ||
      !exec_start_is_fixed(b, p))
    return 0;
  for (size_t i = 0; i < sizeof strings / sizeof strings[0]; i++)
    if (!property_string(b, p, SI, strings[i][0], strings[i][1]))
      return 0;
  for (size_t i = 0; i < sizeof yes / sizeof yes[0]; i++)
    if (!trivial_is(b, p, SI, yes[i], 'b', 1))
      return 0;
  for (size_t i = 0; i < sizeof limits / sizeof limits[0]; i++)
    if (!trivial_is(b, p, SI, limits[i].name, 't', limits[i].value))
      return 0;
  for (size_t i = 0; i < sizeof emptyexec / sizeof emptyexec[0]; i++)
    if (!empty_array(b, p, SI, emptyexec[i], "(sasbttttuii)"))
      return 0;
  /* Reentrant NSS lookup; numeric manager identity must match the fixed UID. */
  struct passwd pw, *pwout = NULL;
  struct group gr, *grout = NULL;
  char pb[16384], gb[16384];
  if (getpwnam_r("p309-runner", &pw, pb, sizeof pb, &pwout) || !pwout ||
      pw.pw_uid == 0 || getgrnam_r("p309-runner", &gr, gb, sizeof gb, &grout) ||
      !grout || gr.gr_gid == 0 || pw.pw_gid != gr.gr_gid)
    return 0;
  return trivial_is(b, p, SI, "UID", 'u', pw.pw_uid) &&
         trivial_is(b, p, SI, "GID", 'u', gr.gr_gid);
}
static int current_binding(pid_t peer, struct binding_record *r, int released) {
  sd_bus *b = NULL;
  int rc = -1;
  if (sd_bus_open_system(&b) < 0)
    return -1;
  sd_bus_set_method_call_timeout(b, 2000000);
  struct binding_record current = {0};
  uint32_t wp;
  char wi[33];
  if (!broker_facts(b, peer, &current) && current.broker_pid == r->broker_pid &&
      (geteuid() != 0 || current.broker_start == r->broker_start) &&
      current.broker_exec_start == r->broker_exec_start &&
      !memcmp(current.broker_inv, r->broker_inv, 33) &&
      !facts(b, WORKER, &wp, wi, 1) && wp == r->worker_pid &&
      !memcmp(wi, r->worker_inv, 33) &&
      start_ticks((pid_t)wp) == r->worker_start &&
      (exe_is((pid_t)wp, GATE_EXE) ||
       (released && exe_is((pid_t)wp, P309_IDLE)))) {
    char *p = NULL;
    if (unit(b, WORKER, &p) >= 0 && worker_policy(b, p))
      rc = 0;
    free(p);
  }
  sd_bus_unref(b);
  return rc;
}
/* This helper verifies pidfd identity through kernel fdinfo, not caller PID. */
static pid_t fd_pid(int fd) {
  char p[64], buf[1024];
  snprintf(p, sizeof p, "/proc/self/fdinfo/%d", fd);
  int f = open(p, O_RDONLY | O_CLOEXEC);
  if (f < 0)
    return -1;
  ssize_t n = read(f, buf, sizeof buf - 1);
  close(f);
  if (n <= 0 || n == (ssize_t)sizeof buf - 1)
    return -1;
  buf[n] = 0;
  char *x = strstr(buf, "\nPid:\t");
  if (!x)
    return -1;
  char *end;
  long v = strtol(x + 6, &end, 10);
  return *end == '\n' && v > 1 && v <= INT_MAX ? (pid_t)v : -1;
}
const struct p309_start_authority *
p309_authorize_guardian(pid_t peer, const char *g, const int fds[5]) {
  struct binding_record r;
  if (geteuid() != 0 || record_read(&r) || strcmp(r.generation, g) ||
      current_binding(peer, &r, 0))
    return NULL;
  struct stat d, k;
  struct statfs fs;
  if (fd_pid(fds[0]) != peer || fd_pid(fds[1]) != (pid_t)r.worker_pid ||
      !alive(fds[0]) || !alive(fds[1]) || fstat(fds[2], &d) ||
      fstat(fds[3], &k) || fstatfs(fds[2], &fs) || fs.f_type != 0x63677270 ||
      (uint64_t)d.st_dev != r.cgroup_dev ||
      (uint64_t)d.st_ino != r.cgroup_ino || (uint64_t)k.st_ino != r.kill_ino ||
      k.st_dev != d.st_dev)
    return NULL;
  verified.r = r;
  for (int i = 0; i < 4; i++)
    verified.f[i] = fds[i];
  return &verified;
}
const struct p309_start_authority *p309_authorize_gate(pid_t peer) {
  struct binding_record r;
  if (geteuid() == 0 || record_read(&r) || r.worker_pid != (uint32_t)getpid() ||
      start_ticks(getpid()) != r.worker_start)
    return NULL;
  /* Protected systemd-activated listener reports PID1, not the acceptor.
   * PID1 is not substituted for broker identity: manager rechecks recorded
   * actual broker InvocationID/PID/start after the completed start. */
  if (peer != 1 && peer != (pid_t)r.broker_pid)
    return NULL;
  if (current_binding((pid_t)r.broker_pid, &r, 0))
    return NULL;
  verified.r = r;
  for (int i = 0; i < 4; i++)
    verified.f[i] = -1;
  return &verified;
}
const char *p309_authority_generation(const struct p309_start_authority *a) {
  return a ? a->r.generation : NULL;
}
int p309_authority_fds(const struct p309_start_authority *a, int out[4]) {
  if (!a)
    return -1;
  for (int i = 0; i < 4; i++) {
    if (a->f[i] < 0)
      return -1;
    out[i] = a->f[i];
  }
  return 0;
}
/* One-use permit syntax: IDLE_V9_ONCE newline, approval digest newline,
 * package manifest digest newline. No supplied command, unit or generation. */
static int consume_permit(struct binding_record *r) {
  int d = directory(STATE_DIR);
  if (d < 0)
    return -1;
  char raw[143];
  if (read_fixed(d, "idle-v9.permit", raw, sizeof raw, 0600) ||
      memcmp(raw, "IDLE_V9_ONCE\n", 13) || raw[77] != '\n' ||
      raw[142] != '\n') {
    close(d);
    return -1;
  }
  memcpy(r->approval, raw + 13, 64);
  r->approval[64] = 0;
  char approved_package[65];
  memcpy(approved_package, raw + 78, 64);
  approved_package[64] = 0;
  if (!hex64(r->approval) || !hex64(approved_package) ||
      package_hash(r->package) || strcmp(approved_package, r->package)) {
    close(d);
    return -1;
  }
  int f = openat(d, "idle-v9.consumed",
                 O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
  if (f < 0) {
    close(d);
    return -1;
  }
  int rc = write_all(f, raw, sizeof raw) || fsync(f);
  close(f);
  if (fsync(d))
    rc = -1;
  close(d);
  return rc ? -1 : 0;
}
static int prop(sd_bus_message *m, const char *name, const char *sig,
                const void *value) {
  int rc = sd_bus_message_open_container(m, 'r', "sv");
  if (rc < 0)
    return rc;
  if ((rc = sd_bus_message_append(m, "s", name)) < 0 ||
      (rc = sd_bus_message_open_container(m, 'v', sig)) < 0)
    return rc;
  if (*sig == 's')
    rc = sd_bus_message_append(m, "s", (const char *)value);
  else
    rc = sd_bus_message_append_basic(m, *sig, value);
  if (rc < 0 || (rc = sd_bus_message_close_container(m)) < 0)
    return rc;
  return sd_bus_message_close_container(m);
}
/* Signals can arrive during sd_bus_call before the method reply is returned.
 * Keep a bounded immutable cache, then correlate ALL of id/path/unit/result. */
struct completed_job {
  uint32_t id;
  char path[96], result[64];
};
struct completion {
  uint32_t expected;
  int seen, overflow;
  size_t count;
  struct completed_job jobs[16];
};
static void correlate(struct completion *c) {
  if (!c->expected)
    return;
  char canonical[96];
  snprintf(canonical, sizeof canonical, "/org/freedesktop/systemd1/job/%u",
           c->expected);
  int found = 0;
  c->seen = 0;
  if (c->overflow) {
    c->seen = -1;
    return;
  }
  for (size_t i = 0; i < c->count; i++)
    if (c->jobs[i].id == c->expected) {
      if (++found != 1 || strcmp(c->jobs[i].path, canonical) ||
          strcmp(c->jobs[i].result, "done")) {
        c->seen = -1;
        return;
      }
      c->seen = 1;
    }
}
static int removed(sd_bus_message *m, void *userdata, sd_bus_error *error) {
  (void)error;
  struct completion *c = userdata;
  uint32_t id;
  const char *path, *name, *result;
  if (sd_bus_message_read(m, "uoss", &id, &path, &name, &result) <= 0)
    return -EBADMSG;
  if (strcmp(name, WORKER))
    return 0;
  if (c->count == 16 || strlen(path) >= sizeof c->jobs[0].path ||
      strlen(result) >= sizeof c->jobs[0].result) {
    c->overflow = 1;
    c->seen = -1;
    return 0;
  }
  struct completed_job *j = &c->jobs[c->count++];
  j->id = id;
  strcpy(j->path, path);
  strcpy(j->result, result);
  correlate(c);
  return 0;
}
static int no_collision(sd_bus *b) {
  sd_bus_message *m = NULL;
  sd_bus_error e = SD_BUS_ERROR_NULL;
  int rc = sd_bus_call_method(b, DEST, MGR, MI, "GetUnit", &e, &m, "s", WORKER);
  int absent = rc < 0 &&
               sd_bus_error_has_name(&e, "org.freedesktop.systemd1.NoSuchUnit");
  sd_bus_message_unref(m);
  sd_bus_error_free(&e);
  if (!absent)
    return -1;
  m = NULL;
  rc = sd_bus_call_method(b, DEST, MGR, MI, "GetUnitFileState", &e, &m, "s",
                          WORKER);
  absent = rc < 0 &&
           sd_bus_error_has_name(&e, "org.freedesktop.systemd1.NoSuchUnitFile");
  sd_bus_message_unref(m);
  sd_bus_error_free(&e);
  if (!absent)
    return -1;
  m = NULL;
  /* Reject orphan, generic and dash-prefix drop-ins BEFORE executing anything.
   * Trusted installer/root must not mutate manager configuration concurrently.
   * A non-existent UnitPath entry is normal; only ENOENT counts as absent. */
  const char *names[] = {WORKER,
                         "service.d",
                         "p309-.service.d",
                         "p309-dev-.service.d",
                         "p309-dev-owned-.service.d",
                         WORKER ".d"};
  int ok = 0;
  const char *base = NULL;
  if (sd_bus_get_property(b, DEST, MGR, MI, "UnitPath", NULL, &m, "as") < 0 ||
      sd_bus_message_enter_container(m, 'a', "s") <= 0)
    goto finish;
  for (;;) {
    rc = sd_bus_message_read(m, "s", &base);
    if (rc < 0)
      goto finish;
    if (!rc)
      break;
    if (!base || base[0] != '/')
      goto finish;
    for (size_t i = 0; i < sizeof names / sizeof names[0]; i++) {
      char path[PATH_MAX];
      struct stat st;
      int n = snprintf(path, sizeof path, "%s/%s", base, names[i]);
      if (n < 0 || (size_t)n >= sizeof path)
        goto finish;
      if (lstat(path, &st) == 0 || errno != ENOENT)
        goto finish;
    }
  }
  ok = 1;
finish:
  sd_bus_message_unref(m);
  return ok ? 0 : -1;
}
#include "anchor_authority.inc"
#include "safety_authority.inc"
int p309_prepare_fixed_gate(struct p309_start_control *control,
                            struct p309_start_authority **out) {
  if (!out)
    return -EINVAL;
  *out = NULL;
  if (geteuid() != 0 || !control || atomic_load(&control->state))
    return -EPERM;
  struct p309_start_authority *a = calloc(1, sizeof *a);
  if (!a)
    return -ENOMEM;
  a->control = control;
  atomic_init(&a->handoff_claimed, 0);
  atomic_init(&a->owned, 0);
  atomic_init(&a->stop_write, 0);
  atomic_init(&a->host.final_consumed, 0);
  atomic_init(&a->host.reserve_attempted, 0);
  atomic_init(&a->host.guardian_ready, 0);
  atomic_init(&a->host.relay_published, 0);
  atomic_init(&a->safety.polling, 0);
  a->safety.sequence = 1;
  memset(a->safety.previous, '0', 64);
  a->safety.previous[64] = 0;
  for (int i = 0; i < 4; i++)
    a->f[i] = -1;
  memcpy(a->r.magic, "P309_GUARD_V9\0\0\0", 16);
  sd_bus *b = NULL;
  int rc = -1, consumed = 0;
  if (boot(a->r.boot) || sd_bus_open_system(&b) < 0)
    goto fail;
  sd_bus_set_method_call_timeout(b, 2000000);
  if (broker_facts(b, getpid(), &a->r) || no_collision(b))
    goto fail;
  int rd = directory(RECORD_DIR);
  if (rd < 0)
    goto fail;
  struct stat st;
  int exists = fstatat(rd, "active-v9.bin", &st, AT_SYMLINK_NOFOLLOW);
  int missing = exists < 0 && errno == ENOENT;
  close(rd);
  if (!missing)
    goto fail;
  unsigned char random[16];
  if (getrandom(random, sizeof random, 0) != (ssize_t)sizeof random)
    goto fail;
  for (int i = 0; i < 16; i++)
    snprintf(a->r.generation + 2 * i, 3, "%02x", random[i]);
  if (p309_authority_stopped(a) || consume_permit(&a->r))
    goto fail;
  consumed = 1; /* Never unconsume, even on failure. */
  /* Opaque PRESTART: real broker facts, local random G/challenge and durable
   * local fence precede the one host reserve. No guest worker exists yet. */
  a->safety.monitor = p309_peer_acquire(P309_PEER_MONITOR, 0);
  if (!a->safety.monitor || p309_authority_stopped(a))
    goto fail;
  sd_bus_unref(b);
  *out = a;
  return 0;
fail:
  p309_start_cancel(control);
  (void)consumed;
  p309_peer_destroy_after_join(a->safety.monitor);
  sd_bus_unref(b);
  free(a);
  return rc;
}
int p309_authority_reserve_host(struct p309_start_authority *a) {
  if (!a || getpid() != (pid_t)a->r.broker_pid)
    return 0;
  if (atomic_exchange(&a->host.reserve_attempted, 1) || !host_reserve_once(a) ||
      p309_authority_stopped(a) || !p309_peer_alive(a->safety.monitor)) {
    p309_authority_stop(a);
    return 0;
  }
  return 1;
}
int p309_start_prepared_gate(struct p309_start_authority *a) {
  if (!a || getpid() != (pid_t)a->r.broker_pid || !a->host.reserved ||
      !p309_authority_safety_current(a))
    return -EPERM;
  struct p309_start_control *control = a->control;
  sd_bus *b = NULL;
  sd_bus_message *m = NULL, *reply = NULL;
  sd_bus_slot *slot = NULL;
  sd_bus_error e = SD_BUS_ERROR_NULL;
  int rc = -1;
  if (sd_bus_open_system(&b) < 0)
    goto fail;
  sd_bus_set_method_call_timeout(b, 2000000);
  struct binding_record current = {0};
  if (broker_facts(b, getpid(), &current) ||
      current.broker_start != a->r.broker_start ||
      strcmp(current.broker_inv, a->r.broker_inv))
    goto fail;
  struct completion complete = {0};
  if (sd_bus_match_signal(b, &slot, DEST, MGR, MI, "JobRemoved", removed,
                          &complete) < 0 ||
      sd_bus_call_method(b, DEST, MGR, MI, "Subscribe", &e, NULL, "") < 0)
    goto fail;
  if (sd_bus_message_new_method_call(b, &m, DEST, MGR, MI,
                                     "StartTransientUnit") < 0 ||
      sd_bus_message_append(m, "ss", WORKER, "fail") < 0 ||
      sd_bus_message_open_container(m, 'a', "(sv)") < 0)
    goto fail;
  const char *strings[][2] = {
      {"Description", "P309 fixed gated idle, not formal workload"},
      {"Type", "exec"},
      {"User", "p309-runner"},
      {"Group", "p309-runner"},
      {"Restart", "no"},
      {"KillMode", "control-group"},
      {"ProtectSystem", "strict"},
      {"StandardInput", "null"},
      {"StandardOutput", "null"},
      {"StandardError", "null"}};
  for (size_t i = 0; i < sizeof strings / sizeof strings[0]; i++)
    if (prop(m, strings[i][0], "s", strings[i][1]) < 0)
      goto fail;
  int yes = 1, no = 0, kill = SIGKILL;
  uint64_t runtime = 120000000, timeout = 10000000, memory = 67108864,
           tasks = 8, weight = 1, zero = 0;
  const char *bools[] = {"NoNewPrivileges", "PrivateTmp", "PrivateDevices",
                         "ProtectControlGroups", "SendSIGKILL"};
  for (size_t i = 0; i < sizeof bools / sizeof bools[0]; i++)
    if (prop(m, bools[i], "b", &yes) < 0)
      goto fail;
  if (prop(m, "Delegate", "b", &no) < 0 ||
      prop(m, "DynamicUser", "b", &no) < 0 ||
      prop(m, "AmbientCapabilities", "t", &zero) < 0 ||
      prop(m, "CapabilityBoundingSet", "t", &zero) < 0 ||
      prop(m, "KillSignal", "i", &kill) < 0 ||
      prop(m, "RuntimeMaxUSec", "t", &runtime) < 0 ||
      prop(m, "TimeoutStopUSec", "t", &timeout) < 0 ||
      prop(m, "MemoryMax", "t", &memory) < 0 ||
      prop(m, "TasksMax", "t", &tasks) < 0 ||
      prop(m, "CPUWeight", "t", &weight) < 0 ||
      prop(m, "IOWeight", "t", &weight) < 0)
    goto fail;
  if (sd_bus_message_open_container(m, 'r', "sv") < 0 ||
      sd_bus_message_append(m, "s", "ExecStart") < 0 ||
      sd_bus_message_open_container(m, 'v', "a(sasb)") < 0 ||
      sd_bus_message_open_container(m, 'a', "(sasb)") < 0 ||
      sd_bus_message_open_container(m, 'r', "sasb") < 0 ||
      sd_bus_message_append(m, "s", GATE_EXE) < 0 ||
      sd_bus_message_open_container(m, 'a', "s") < 0 ||
      sd_bus_message_append(m, "s", GATE_EXE) < 0 ||
      sd_bus_message_close_container(m) < 0 ||
      sd_bus_message_append(m, "b", 0) < 0)
    goto fail;
  for (int i = 0; i < 4; i++)
    if (sd_bus_message_close_container(m) < 0)
      goto fail;
  if (sd_bus_message_close_container(m) < 0 ||
      sd_bus_message_open_container(m, 'a', "(sa(sv))") < 0 ||
      sd_bus_message_close_container(m) < 0)
    goto fail;
  /* Exactly ONE start call. Failure/timeout retains consumed fence and no
   * retry. */
  if (no_collision(b))
    goto fail;
  unsigned initial = 0;
  if (!p309_authority_safety_current(a) ||
      !atomic_compare_exchange_strong(&control->state, &initial,
                                      START_DISPATCHED))
    goto fail;
  if (sd_bus_call(b, m, 2000000, &e, &reply) < 0)
    goto fail;
  const char *job = NULL;
  static const char job_prefix[] = "/org/freedesktop/systemd1/job/";
  if (sd_bus_message_read(reply, "o", &job) <= 0 || !job ||
      strncmp(job, job_prefix, sizeof job_prefix - 1))
    goto fail;
  char *job_end = NULL;
  errno = 0;
  unsigned long long job_number =
      strtoull(job + sizeof job_prefix - 1, &job_end, 10);
  if (errno || !job_number || job_number > UINT32_MAX || !job_end || *job_end)
    goto fail;
  complete.expected = (uint32_t)job_number;
  char canonical_job[96];
  snprintf(canonical_job, sizeof canonical_job,
           "/org/freedesktop/systemd1/job/%u", complete.expected);
  if (strcmp(job, canonical_job))
    goto fail;
  correlate(&complete);
  a->r.job_id = complete.expected;
  int64_t start = clock_ns();
  if (start < 0)
    goto fail;
  while (!complete.seen) {
    int64_t now = clock_ns();
    if (now < start || now - start >= 3000000000LL)
      goto fail;
    int processed = sd_bus_process(b, NULL);
    if (processed < 0)
      goto fail;
    if (!processed && sd_bus_wait(b, 50000) < 0)
      goto fail;
  }
  if (complete.seen != 1 ||
      facts(b, WORKER, &a->r.worker_pid, a->r.worker_inv, 1) ||
      !exe_is((pid_t)a->r.worker_pid, GATE_EXE))
    goto fail;
  char *worker_path = NULL;
  if (unit(b, WORKER, &worker_path) < 0)
    goto fail;
  int policy_ok = worker_policy(b, worker_path);
  free(worker_path);
  if (!policy_ok)
    goto fail;
  if (sd_bus_call_method(b, DEST, MGR, MI, "RefUnit", &e, NULL, "s", WORKER) <
      0)
    goto fail;
  a->r.worker_start = start_ticks((pid_t)a->r.worker_pid);
  if (!a->r.worker_start)
    goto fail;
  a->f[0] = pidfd(getpid());
  a->f[1] = pidfd((pid_t)a->r.worker_pid);
  a->f[2] = directory(P309_CGROUP);
  if (a->f[0] < 0 || a->f[1] < 0 || a->f[2] < 0)
    goto fail;
  a->f[3] = openat(a->f[2], "cgroup.kill", O_WRONLY | O_NOFOLLOW | O_CLOEXEC);
  struct stat ds, ks;
  struct statfs fs;
  if (a->f[3] < 0 || fstat(a->f[2], &ds) || fstat(a->f[3], &ks) ||
      fstatfs(a->f[2], &fs) || fs.f_type != 0x63677270 || !alive(a->f[1]) ||
      start_ticks((pid_t)a->r.worker_pid) != a->r.worker_start)
    goto fail;
  a->r.cgroup_dev = ds.st_dev;
  a->r.cgroup_ino = ds.st_ino;
  a->r.kill_ino = ks.st_ino;
  /* Successful manager transaction + actual identities + retained kernel
   * objects already establish ownership. Publish stop capability BEFORE any
   * record I/O; persistence failure must not discard the only exact handles. */
  a->manager_ref = b;
  b = NULL;
  atomic_store(&a->owned, 1);
  if (p309_authority_stopped(a)) {
    (void)p309_authority_request_stop_owned(a);
    goto fail;
  }
  int rd = directory(RECORD_DIR);
  if (rd < 0)
    goto fail;
  int file = openat(rd, "active-v9.bin",
                    O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
  if (file < 0) {
    close(rd);
    goto fail;
  }
  int bad = write_all(file, &a->r, sizeof a->r) || fsync(file) ||
            fchmod(file, 0444) || fsync(file);
  close(file);
  if (fsync(rd))
    bad = 1;
  close(rd);
  if (bad)
    goto fail;
  sd_bus_slot_unref(slot);
  sd_bus_message_unref(m);
  sd_bus_message_unref(reply);
  sd_bus_error_free(&e);
  /* A late successful START after cancellation is owned but never releasable.
   * Return the retained authority for cleanup even with ECANCELED. */
  if (p309_authority_stopped(a)) {
    (void)p309_authority_request_stop_owned(a);
    return -ECANCELED;
  }
  return 0;
fail:
  /* Gated worker has its own fixed timeout. No unknown unit name kill/adopt.
   * Preserve permit/partial record. Full broker must report RECOVERY_UNKNOWN.
   */
  p309_start_cancel(control);
  if (atomic_load(&a->owned)) {
    (void)p309_authority_request_stop_owned(a);
    /* Caller retains authority even on error: UNKNOWN, never close/reopen. */
  } else {
    for (int i = 0; i < 4; i++)
      if (a->f[i] >= 0) {
        close(a->f[i]);
        a->f[i] = -1;
      }
  }
  sd_bus_slot_unref(slot);
  sd_bus_message_unref(m);
  sd_bus_message_unref(reply);
  sd_bus_error_free(&e);
  sd_bus_unref(b);
  return rc;
}
int p309_start_fixed_gate(struct p309_start_control *c,
                          struct p309_start_authority **out) {
  int rc = p309_prepare_fixed_gate(c, out);
  if (rc)
    return rc;
  if (!p309_authority_reserve_host(*out))
    return -EPERM;
  if (!p309_authority_safety_poll(*out))
    return -EPERM;
  return p309_start_prepared_gate(*out);
}

pid_t p309_authority_worker_pid(const struct p309_start_authority *a) {
  return a ? (pid_t)a->r.worker_pid : -1;
}
int p309_authority_current(const struct p309_start_authority *a) {
  if (!a || !a->control || getpid() != (pid_t)a->r.broker_pid ||
      !p309_peer_alive(a->safety.monitor) || !p309_peer_alive(a->host.relay))
    return 0;
  unsigned phase = atomic_load(&a->control->state);
  int released = !!(phase & RELEASE_DISPATCHED);
  return !(phase & STOP_LATCHED) &&
         !current_binding(getpid(), (struct binding_record *)&a->r, released) &&
         alive(a->f[1]) && !p309_authority_stopped(a);
}

int p309_authority_claim_handoff(const struct p309_start_authority *a) {
  if (!a || getpid() != (pid_t)a->r.broker_pid)
    return 0;
  return !atomic_exchange(&((struct p309_start_authority *)a)->handoff_claimed,
                          1);
}
int p309_guardian_pidfd(void) {
  sd_bus *b = NULL;
  uint32_t pid;
  char inv[33];
  int fd = -1;
  if (sd_bus_open_system(&b) < 0)
    return -1;
  sd_bus_set_method_call_timeout(b, 2000000);
  if (!facts(b, "rebaseguard-p309-guardian.service", &pid, inv, 0) &&
      exe_is((pid_t)pid, "/usr/local/libexec/rebaseguard-p309/guardian-v9")) {
    uint64_t start = start_ticks((pid_t)pid);
    fd = pidfd((pid_t)pid);
    if (!start || fd < 0 || !alive(fd) || start_ticks((pid_t)pid) != start) {
      if (fd >= 0)
        close(fd);
      fd = -1;
    }
  }
  if (fd >= 0 &&
      sd_bus_call_method(b, DEST, MGR, MI, "RefUnit", NULL, NULL, "s",
                         "rebaseguard-p309-guardian.service") >= 0) {
    guardian_record.pid = pid;
    memcpy(guardian_record.inv, inv, 33);
    guardian_record.bus = b;
    guardian_record.fd = fd;
    return fd;
  }
  if (fd >= 0)
    close(fd);
  sd_bus_unref(b);
  return -1;
}
int p309_authority_cleanup_observed(const struct p309_start_authority *a) {
  if (!a || getpid() != (pid_t)a->r.broker_pid)
    return 0;
  struct pollfd pf = {a->f[1], POLLIN, 0};
  if (poll(&pf, 1, 0) != 1 || pf.revents != POLLIN)
    return 0;
  char events[256];
  int ef = openat(a->f[2], "cgroup.events", O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
  if (ef < 0)
    return 0;
  ssize_t n = read(ef, events, sizeof events - 1);
  close(ef);
  if (n <= 0 || n == (ssize_t)sizeof events - 1)
    return 0;
  events[n] = 0;
  if (strcmp(events, "populated 0\nfrozen 0\n"))
    return 0;
  sd_bus *b = NULL;
  char *path = NULL;
  int ok = 0;
  if (sd_bus_open_system(&b) < 0)
    return 0;
  sd_bus_set_method_call_timeout(b, 2000000);
  if (unit(b, WORKER, &path) < 0)
    goto done;
  char inv[33];
  uint32_t main = 1, exec = 0;
  int32_t code = 0;
  uint64_t exited_at = 0;
  if (invocation(b, path, inv) < 0 || memcmp(inv, a->r.worker_inv, 33))
    goto done;
  if (!(property_string(b, path, UI, "ActiveState", "inactive") ||
        property_string(b, path, UI, "ActiveState", "failed")) ||
      !(property_string(b, path, UI, "SubState", "dead") ||
        property_string(b, path, UI, "SubState", "failed")))
    goto done;
  if (sd_bus_get_property_trivial(b, DEST, path, SI, "MainPID", NULL, 'u',
                                  &main) < 0 ||
      main ||
      sd_bus_get_property_trivial(b, DEST, path, SI, "ExecMainPID", NULL, 'u',
                                  &exec) < 0 ||
      exec != a->r.worker_pid ||
      sd_bus_get_property_trivial(b, DEST, path, SI, "ExecMainCode", NULL, 'i',
                                  &code) < 0 ||
      code == 0 ||
      sd_bus_get_property_trivial(b, DEST, path, SI,
                                  "ExecMainExitTimestampMonotonic", NULL, 't',
                                  &exited_at) < 0 ||
      !exited_at)
    goto done;
  sd_bus_message *m = NULL;
  uint32_t job = 1;
  const char *jp = NULL;
  if (sd_bus_get_property(b, DEST, path, UI, "Job", NULL, &m, "(uo)") >= 0 &&
      sd_bus_message_read(m, "(uo)", &job, &jp) >= 0 && !job)
    ok = 1;
  sd_bus_message_unref(m);
done:
  free(path);
  sd_bus_unref(b);
  return ok;
}
int p309_authority_dispose_after_cleanup(struct p309_start_authority *a) {
  /* Fail closed rather than silently dropping the last broker ownership FD. */
  if (!p309_authority_cleanup_observed(a))
    return 0;
  if (a->manager_ref) {
    (void)sd_bus_call_method(a->manager_ref, DEST, MGR, MI, "UnrefUnit", NULL,
                             NULL, "s", WORKER);
    sd_bus_unref(a->manager_ref);
  }
  for (int i = 0; i < 4; i++)
    if (a->f[i] >= 0) {
      close(a->f[i]);
      a->f[i] = -1;
    }
  p309_peer_destroy_after_join(a->safety.monitor);
  p309_peer_destroy_after_join(a->host.relay);
  free(a);
  return 1;
}

int p309_guardian_cleanup_observed(int fd) {
  if (fd != guardian_record.fd || !guardian_record.bus)
    return 0;
  struct pollfd pollfd = {fd, POLLIN, 0};
  if (poll(&pollfd, 1, 0) != 1 || pollfd.revents != POLLIN)
    return 0;
  sd_bus *b = guardian_record.bus;
  char *path = NULL;
  int ok = 0;
  if (unit(b, "rebaseguard-p309-guardian.service", &path) < 0)
    return 0;
  uint32_t main = 1, exec = 0;
  int32_t code = 0;
  uint64_t time = 0;
  char inv[33];
  if (invocation(b, path, inv) < 0 || memcmp(inv, guardian_record.inv, 33) ||
      !property_string(b, path, UI, "ActiveState", "inactive") ||
      !property_string(b, path, UI, "SubState", "dead"))
    goto done;
  if (sd_bus_get_property_trivial(b, DEST, path, SI, "MainPID", NULL, 'u',
                                  &main) < 0 ||
      main ||
      sd_bus_get_property_trivial(b, DEST, path, SI, "ExecMainPID", NULL, 'u',
                                  &exec) < 0 ||
      exec != guardian_record.pid ||
      sd_bus_get_property_trivial(b, DEST, path, SI, "ExecMainCode", NULL, 'i',
                                  &code) < 0 ||
      code == 0 ||
      sd_bus_get_property_trivial(b, DEST, path, SI,
                                  "ExecMainExitTimestampMonotonic", NULL, 't',
                                  &time) < 0 ||
      !time)
    goto done;
  sd_bus_message *m = NULL;
  uint32_t job = 1;
  const char *jp = NULL;
  if (sd_bus_get_property(b, DEST, path, UI, "Job", NULL, &m, "(uo)") >= 0 &&
      sd_bus_message_read(m, "(uo)", &job, &jp) >= 0 && !job)
    ok = 1;
  sd_bus_message_unref(m);
done:
  free(path);
  return ok;
}
void p309_guardian_release_reference(void) {
  if (!guardian_record.bus)
    return;
  (void)sd_bus_call_method(guardian_record.bus, DEST, MGR, MI, "UnrefUnit",
                           NULL, NULL, "s",
                           "rebaseguard-p309-guardian.service");
  sd_bus_unref(guardian_record.bus);
  guardian_record.bus = NULL;
}
