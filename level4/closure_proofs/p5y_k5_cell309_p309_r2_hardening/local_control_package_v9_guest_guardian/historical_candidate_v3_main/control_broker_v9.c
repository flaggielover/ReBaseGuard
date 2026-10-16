/* Actual root broker entry. Source only until separately approved native build
 * and acceptance. Socket activation/status never creates Start authority. */
#define _GNU_SOURCE
#include "authority_binding.h"
#include "broker_link.h"
#include "h4_wire.h"
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <limits.h>
#include <poll.h>
#include <pthread.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
#define ROOT "/run/rebaseguard-p309/"
enum phase {
  WAIT_ADMIN,
  PREPARING,
  PREPARED,
  STARTING,
  OWNED,
  RELEASE_DISPATCHED,
  STOP_LATCHED,
  CLEANUP_OBSERVED,
  RECOVERY_UNKNOWN
};
static const char *const phase_name[] = {
    "WAIT_ADMIN",      "PREPARING",
    "PREPARED",        "STARTING",
    "OWNED",           "RELEASE_DISPATCHED",
    "STOP_LATCHED",    "LOCAL_CLEANUP_OBSERVED",
    "RECOVERY_UNKNOWN"};
struct broker {
  struct p309_start_control control;
  _Atomic(struct p309_start_authority *) authority;
  _Atomic(struct p309_guardian_link *) link;
  struct p309_peer_identity *monitor;
  int h4, admin, gate, logfd;
  atomic_int phase, reason, shutdown, monitor_connected, admin_consumed;
};
static volatile sig_atomic_t signalled;
static void signal_stop(int number) {
  (void)number;
  signalled = 1;
}
static int64_t now_ns(void) {
  struct timespec t;
  if (clock_gettime(CLOCK_BOOTTIME, &t))
    return -1;
  return (int64_t)t.tv_sec * 1000000000LL + t.tv_nsec;
}
static void stop(struct broker *b, int reason) {
  p309_start_cancel(&b->control);
  int empty = 0;
  (void)atomic_compare_exchange_strong(&b->reason, &empty, reason);
  struct p309_guardian_link *l = atomic_load(&b->link);
  struct p309_start_authority *a = atomic_load(&b->authority);
  if (l)
    (void)p309_guardian_request_stop(l);
  else if (a)
    (void)p309_authority_request_stop_owned(a);
  atomic_store(&b->phase, STOP_LATCHED);
}
static int protected_directory(int fd, mode_t exact) {
  struct stat s;
  return !fstat(fd, &s) && S_ISDIR(s.st_mode) && s.st_uid == 0 &&
         !(s.st_mode & 0022) && (!exact || (s.st_mode & 0777) == exact);
}
static int socket_parent(void) {
  int d = open("/", O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
  const char *parts[] = {"run", "rebaseguard-p309"};
  for (size_t i = 0; d >= 0 && i < 2; i++) {
    if (!protected_directory(d, 0)) {
      close(d);
      return -1;
    }
    int n =
        openat(d, parts[i], O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    close(d);
    d = n;
  }
  if (d < 0)
    return -1;
  if (!protected_directory(d, 0755)) {
    close(d);
    return -1;
  }
  return d;
}
static int socket_ok(int fd, const char *leaf, gid_t gid, mode_t mode) {
  char path[108];
  int n = snprintf(path, sizeof path, ROOT "%s", leaf);
  if (n < 0 || (size_t)n >= sizeof path)
    return 0;
  struct sockaddr_un addr = {0};
  socklen_t len = sizeof addr;
  int type = 0, accepting = 0;
  socklen_t ilen = sizeof type;
  if (getsockopt(fd, SOL_SOCKET, SO_TYPE, &type, &ilen) ||
      type != SOCK_SEQPACKET)
    return 0;
  ilen = sizeof accepting;
  if (getsockopt(fd, SOL_SOCKET, SO_ACCEPTCONN, &accepting, &ilen) ||
      !accepting)
    return 0;
  if (getsockname(fd, (struct sockaddr *)&addr, &len) ||
      addr.sun_family != AF_UNIX ||
      len != offsetof(struct sockaddr_un, sun_path) + strlen(path) + 1 ||
      strcmp(addr.sun_path, path))
    return 0;
  int d = socket_parent();
  if (d < 0)
    return 0;
  struct stat s;
  int ok = !fstatat(d, leaf, &s, AT_SYMLINK_NOFOLLOW) && S_ISSOCK(s.st_mode) &&
           s.st_uid == 0 && s.st_gid == gid && (s.st_mode & 0777) == mode;
  close(d);
  int flags = fcntl(fd, F_GETFL);
  return ok && flags >= 0 && !fcntl(fd, F_SETFL, flags | O_NONBLOCK) &&
         !fcntl(fd, F_SETFD, FD_CLOEXEC);
}
static int group_id(const char *name, gid_t *gid) {
  struct group g, *out = NULL;
  char buf[16384];
  if (getgrnam_r(name, &g, buf, sizeof buf, &out) || !out || !g.gr_gid)
    return 0;
  *gid = g.gr_gid;
  return 1;
}
static int activation(struct broker *b) {
  char pid[32];
  snprintf(pid, sizeof pid, "%ld", (long)getpid());
  const char *names = getenv("LISTEN_FDNAMES");
  if (!getenv("LISTEN_PID") || strcmp(getenv("LISTEN_PID"), pid) ||
      !getenv("LISTEN_FDS") || strcmp(getenv("LISTEN_FDS"), "3") || !names ||
      strlen(names) > 64)
    return 0;
  char copy[65];
  strcpy(copy, names);
  char *save = NULL, *part = strtok_r(copy, ":", &save);
  b->h4 = b->admin = b->gate = -1;
  for (int fd = 3; fd < 6; fd++) {
    if (!part)
      return 0;
    if (!strcmp(part, "control-v9") && b->h4 < 0)
      b->h4 = fd;
    else if (!strcmp(part, "admin-v9") && b->admin < 0)
      b->admin = fd;
    else if (!strcmp(part, "gate-v9") && b->gate < 0)
      b->gate = fd;
    else
      return 0;
    part = strtok_r(NULL, ":", &save);
  }
  if (part || b->h4 < 0 || b->admin < 0 || b->gate < 0)
    return 0;
  gid_t monitor, runner;
  if (!group_id("p309-monitor", &monitor) ||
      !group_id("p309-runner", &runner) || monitor == runner)
    return 0;
  if (!socket_ok(b->h4, "control.sock", monitor, 0660) ||
      !socket_ok(b->admin, "admin-v9.sock", 0, 0600) ||
      !socket_ok(b->gate, "launch-gate-v9.sock", runner, 0660))
    return 0;
  unsetenv("LISTEN_PID");
  unsetenv("LISTEN_FDS");
  unsetenv("LISTEN_FDNAMES");
  return !close_range(6, UINT_MAX, 0);
}
static ssize_t plain_frame(int s, unsigned char *raw, size_t cap) {
  union {
    struct cmsghdr align;
    char bytes[CMSG_SPACE(16 * sizeof(int))];
  } ancillary;
  struct iovec i = {raw, cap};
  struct msghdr m = {0};
  m.msg_iov = &i;
  m.msg_iovlen = 1;
  m.msg_control = ancillary.bytes;
  m.msg_controllen = sizeof ancillary.bytes;
  ssize_t n = recvmsg(s, &m, MSG_DONTWAIT | MSG_CMSG_CLOEXEC);
  if (n < 0)
    return n;
  int bad = n == 0 || !!(m.msg_flags & (MSG_TRUNC | MSG_CTRUNC));
  for (struct cmsghdr *c = CMSG_FIRSTHDR(&m); c; c = CMSG_NXTHDR(&m, c)) {
    bad = 1;
    if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS &&
        c->cmsg_len >= CMSG_LEN(0)) {
      size_t count = (c->cmsg_len - CMSG_LEN(0)) / sizeof(int);
      int *fds = (int *)CMSG_DATA(c);
      for (size_t j = 0; j < count; j++)
        close(fds[j]);
    }
  }
  return bad ? -1 : n;
}
static int peer(int s, struct ucred *p) {
  socklen_t n = sizeof *p;
  return !getsockopt(s, SOL_SOCKET, SO_PEERCRED, p, &n) && n == sizeof *p &&
         p->pid > 1;
}
static int log_open(void) {
  int d = open("/", O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
  const char *parts[] = {"var", "lib", "rebaseguard-p309-control"};
  for (size_t i = 0; d >= 0 && i < 3; i++) {
    if (!protected_directory(d, 0)) {
      close(d);
      return -1;
    }
    int n =
        openat(d, parts[i], O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    close(d);
    d = n;
  }
  if (d < 0)
    return -1;
  if (!protected_directory(d, 0700)) {
    close(d);
    return -1;
  }
  int f = openat(d, "broker-v9.events",
                 O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
  int ok = f >= 0 && !fsync(d);
  close(d);
  if (!ok) {
    if (f >= 0)
      close(f);
    return -1;
  }
  return f;
}
static int record(struct broker *b, const char *event) {
  /* Single owner thread only; never called by independent stop thread. */
  char line[512];
  struct p309_start_authority *a = atomic_load(&b->authority);
  const char *g = a ? p309_authority_generation(a) : "NONE";
  int n = snprintf(
      line, sizeof line,
      "{\"event\":\"%s\",\"generation\":\"%s\",\"phase\":\"%s\",\"stop_"
      "latched\":%s,\"reason\":%d,\"formal_admission\":\"BLOCKED\"}\n",
      event, g, phase_name[atomic_load(&b->phase)],
      p309_start_is_cancelled(&b->control) ? "true" : "false",
      atomic_load(&b->reason));
  if (n <= 0 || (size_t)n >= sizeof line)
    return 0;
  size_t at = 0;
  while (at < (size_t)n) {
    ssize_t wrote = write(b->logfd, line + at, (size_t)n - at);
    if (wrote < 0 && errno == EINTR)
      continue;
    if (wrote <= 0)
      return 0;
    at += (size_t)wrote;
  }
  return !fsync(b->logfd);
}
struct cached {
  struct p309_h4_request request;
  char reply[512];
  size_t bytes;
};
static void *stop_loop(void *arg) {
  struct broker *b = arg;
  int client = -1;
  struct cached cache[64];
  size_t used = 0;
  int64_t previous = now_ns(), beat = previous;
  while (!atomic_load(&b->shutdown)) {
    int64_t now = now_ns();
    if (signalled || now < previous || now < 0 ||
        now - previous >= 5000000000LL || !p309_peer_alive(b->monitor))
      stop(b, 1);
    previous = now;
    struct p309_guardian_link *l = atomic_load(&b->link);
    struct p309_start_authority *a = atomic_load(&b->authority);
    if (p309_start_is_cancelled(&b->control))
      stop(b, 2);
    else if (l && (!a || !p309_authority_safety_current(a)))
      stop(b, 3);
    else if (l && now - beat >= 1000000000LL) {
      if (p309_guardian_heartbeat(l))
        stop(b, 4);
      beat = now;
    }
    struct pollfd p[4] = {
        {b->h4, POLLIN, 0},
        {client, POLLIN, 0},
        {p309_peer_pidfd(b->monitor), POLLIN, 0},
        {atomic_load(&b->admin_consumed) ? b->admin : -1, POLLIN, 0}};
    int rc = poll(p, 4, 50);
    if (rc < 0) {
      if (errno == EINTR)
        continue;
      stop(b, 5);
      break;
    }
    if (p[2].revents)
      stop(b, 6);
    /* After the single admin transaction, any queued duplicate request is
     * terminal. No manager lookup or additional Start occurs here. */
    if (p[3].revents)
      stop(b, 20);
    if (p[0].revents & (POLLERR | POLLHUP | POLLNVAL)) {
      stop(b, 7);
      break;
    }
    if (p[0].revents & POLLIN) {
      int accepted = accept4(b->h4, NULL, NULL, SOCK_CLOEXEC | SOCK_NONBLOCK);
      if (accepted >= 0) {
        struct ucred credentials;
        if (!peer(accepted, &credentials) ||
            !p309_peer_matches(b->monitor, credentials.pid, credentials.uid))
          close(accepted);
        else if (client >= 0) {
          close(accepted);
          stop(b, 8);
        } else {
          client = accepted;
          atomic_store(&b->monitor_connected, 1);
        }
      }
    }
    if (client < 0)
      continue;
    if (p[1].revents & (POLLERR | POLLHUP | POLLNVAL)) {
      close(client);
      client = -1;
      atomic_store(&b->monitor_connected, 0);
      stop(b, 9);
      continue;
    }
    if (!(p[1].revents & POLLIN))
      continue;
    unsigned char raw[16384];
    ssize_t bytes = plain_frame(client, raw, sizeof raw);
    struct p309_h4_request request;
    if (bytes <= 0 || !p309_h4_parse(raw, (size_t)bytes, &request)) {
      stop(b, 10);
      close(client);
      client = -1;
      atomic_store(&b->monitor_connected, 0);
      continue;
    }
    size_t index = used;
    for (size_t i = 0; i < used; i++)
      if (!strcmp(cache[i].request.request_id, request.request_id)) {
        index = i;
        break;
      }
    if (index < used) {
      struct p309_h4_request *old = &cache[index].request;
      if (old->stop != request.stop ||
          old->has_generation != request.has_generation ||
          strcmp(old->generation, request.generation)) {
        stop(b, 11);
        close(client);
        client = -1;
        atomic_store(&b->monitor_connected, 0);
        continue;
      }
    } else {
      if (used == 64) {
        stop(b, 12);
        close(client);
        client = -1;
        atomic_store(&b->monitor_connected, 0);
        continue;
      }
      a = atomic_load(&b->authority);
      const char *g = a ? p309_authority_generation(a) : NULL;
      int match =
          !request.has_generation || (g && !strcmp(request.generation, g));
      if (request.stop && match)
        stop(b, 13);
      cache[index].request = request;
      char generation[36];
      if (g)
        snprintf(generation, sizeof generation, "\"%s\"", g);
      else
        strcpy(generation, "null");
      int n = snprintf(cache[index].reply, sizeof cache[index].reply,
                       "{\"protocol\":\"P309_DEV_BROKER_CONTROL/"
                       "2\",\"request_id\":\"%s\",\"generation\":%s,\"result\":"
                       "\"%s\",\"phase\":\"%s\",\"stop_latched\":%s,\"formal_"
                       "admission\":\"BLOCKED\"}",
                       request.request_id, generation,
                       match ? "ACKNOWLEDGED" : "GENERATION_MISMATCH",
                       phase_name[atomic_load(&b->phase)],
                       p309_start_is_cancelled(&b->control) ? "true" : "false");
      if (n <= 0 || (size_t)n >= sizeof cache[index].reply) {
        stop(b, 14);
        break;
      }
      cache[index].bytes = (size_t)n;
      used++;
    }
    if (send(client, cache[index].reply, cache[index].bytes,
             MSG_DONTWAIT | MSG_NOSIGNAL) != (ssize_t)cache[index].bytes) {
      close(client);
      client = -1;
      atomic_store(&b->monitor_connected, 0);
      stop(b, 15);
    }
  }
  if (client >= 0)
    close(client);
  atomic_store(&b->monitor_connected, 0);
  return NULL;
}
static void *safety_loop(void *arg) {
  struct broker *b = arg;
  struct p309_start_authority *a = atomic_load(&b->authority);
  while (!atomic_load(&b->shutdown) && !p309_start_is_cancelled(&b->control)) {
    if (!p309_authority_safety_poll(a)) {
      stop(b, 16);
      break;
    }
    struct timespec delay = {0, 250000000};
    while (nanosleep(&delay, &delay) < 0 && errno == EINTR && !signalled) {
    }
  }
  return NULL;
}
static int accept_admin(struct broker *b) {
  for (;;) {
    if (p309_start_is_cancelled(&b->control) || signalled)
      return 0;
    struct pollfd p = {b->admin, POLLIN, 0};
    int rc = poll(&p, 1, 100);
    if (rc < 0) {
      if (errno == EINTR)
        continue;
      return 0;
    }
    if (p.revents & (POLLERR | POLLHUP | POLLNVAL))
      return 0;
    if (!(p.revents & POLLIN))
      continue;
    int s = accept4(b->admin, NULL, NULL, SOCK_CLOEXEC | SOCK_NONBLOCK);
    if (s < 0)
      continue;
    struct ucred credentials;
    if (!peer(s, &credentials) || credentials.uid != 0) {
      close(s);
      continue;
    }
    struct p309_peer_identity *admin =
        p309_peer_acquire(P309_PEER_ADMIN, credentials.pid);
    if (!admin) {
      close(s);
      continue;
    }
    int64_t issued = now_ns();
    int good = 0;
    while (issued >= 0 && !p309_start_is_cancelled(&b->control) &&
           p309_peer_alive(admin)) {
      int64_t now = now_ns();
      if (now < issued || now - issued >= 1000000000LL)
        break;
      struct pollfd q = {s, POLLIN, 0};
      rc = poll(&q, 1, 50);
      if (rc < 0) {
        if (errno == EINTR)
          continue;
        break;
      }
      if (q.revents & (POLLERR | POLLHUP | POLLNVAL))
        break;
      if (!(q.revents & POLLIN))
        continue;
      unsigned char frame[64];
      ssize_t n = plain_frame(s, frame, sizeof frame);
      static const char command[] = "PREPARE_DEV_IDLE_V9\n";
      good = n == (ssize_t)(sizeof command - 1) &&
             !memcmp(frame, command, sizeof command - 1);
      break;
    }
    if (good && !p309_start_is_cancelled(&b->control) &&
        p309_peer_alive(admin)) {
      static const char response[] = "REQUEST_ACCEPTED_NOT_EXECUTED\n";
      good =
          send(s, response, sizeof response - 1, MSG_DONTWAIT | MSG_NOSIGNAL) ==
          (ssize_t)(sizeof response - 1);
    } else
      good = 0;
    close(s);
    p309_peer_destroy_after_join(admin);
    if (!good)
      stop(b, 17);
    return good;
  }
}
int main(int argc, char **argv) {
  (void)argv;
  if (argc != 1 || geteuid() != 0)
    return 64;
  struct broker b = {0};
  b.logfd = -1;
  atomic_init(&b.control.state, 0);
  atomic_init(&b.authority, NULL);
  atomic_init(&b.link, NULL);
  atomic_init(&b.phase, WAIT_ADMIN);
  atomic_init(&b.reason, 0);
  atomic_init(&b.shutdown, 0);
  atomic_init(&b.monitor_connected, 0);
  atomic_init(&b.admin_consumed, 0);
  if (!activation(&b))
    return 65;
  b.logfd = log_open();
  if (b.logfd < 0)
    return 66;
  struct sigaction sa = {0};
  sa.sa_handler = signal_stop;
  sigemptyset(&sa.sa_mask);
  if (sigaction(SIGTERM, &sa, NULL) || sigaction(SIGINT, &sa, NULL) ||
      sigaction(SIGHUP, &sa, NULL))
    return 67;
  b.monitor = p309_peer_acquire(P309_PEER_MONITOR, 0);
  if (!b.monitor) {
    (void)record(&b, "MONITOR_UNAVAILABLE");
    return 78;
  }
  pthread_t stopper, safety;
  int safety_started = 0;
  if (pthread_create(&stopper, NULL, stop_loop, &b))
    return 68;
  int result = 78;
  struct p309_start_authority *a = NULL;
  struct p309_guardian_link *link = NULL;
  if (!record(&b, "WAIT_ADMIN") || !accept_admin(&b))
    goto done;
  atomic_store(&b.admin_consumed, 1);
  if (!atomic_load(&b.monitor_connected))
    goto done;
  atomic_store(&b.phase, PREPARING);
  if (!record(&b, "ADMIN_ACCEPTED"))
    goto done;
  if (p309_prepare_fixed_gate(&b.control, &a))
    goto done;
  if (!p309_authority_monitor_is(a, b.monitor))
    goto done;
  atomic_store(&b.authority, a);
  atomic_store(&b.phase, PREPARED);
  if (!p309_authority_reserve_host(a))
    goto done;
  if (!p309_authority_safety_poll(a) || !record(&b, "SIGNED_SAFETY_INITIAL"))
    goto done;
  if (pthread_create(&safety, NULL, safety_loop, &b))
    goto done;
  safety_started = 1;
  atomic_store(&b.phase, STARTING);
  if (p309_start_prepared_gate(a))
    goto done;
  atomic_store(&b.phase, OWNED);
  int bound = p309_guardian_bind(a, &link);
  if (link)
    atomic_store(&b.link, link);
  if (bound)
    goto done;
  int accepted = -1;
  int64_t began = now_ns();
  while (!p309_start_is_cancelled(&b.control) && began >= 0) {
    int64_t now = now_ns();
    if (now < began || now - began >= 2000000000LL)
      break;
    struct pollfd p = {b.gate, POLLIN, 0};
    int rc = poll(&p, 1, 50);
    if (rc < 0) {
      if (errno == EINTR)
        continue;
      break;
    }
    if (p.revents & (POLLERR | POLLHUP | POLLNVAL))
      break;
    if (p.revents & POLLIN) {
      accepted = accept4(b.gate, NULL, NULL, SOCK_NONBLOCK | SOCK_CLOEXEC);
      break;
    }
  }
  if (accepted < 0 || p309_release_fixed_gate(link, accepted))
    goto done;
  atomic_store(&b.phase, RELEASE_DISPATCHED);
  if (!record(&b, "RELEASE_DISPATCHED_NOT_FORMAL_RUNNING"))
    goto done;
  began = now_ns();
  while (!p309_start_is_cancelled(&b.control)) {
    int64_t now = now_ns();
    if (now < began || now - began >= 120000000000LL) {
      stop(&b, 18);
      break;
    }
    struct timespec delay = {0, 50000000};
    (void)nanosleep(&delay, NULL);
  }
done:
  stop(&b, 19);
  if (safety_started)
    pthread_join(safety, NULL);
  int cleaned = link && p309_guardian_retire(link) == 0;
  atomic_store(&b.shutdown, 1);
  pthread_join(stopper, NULL);
  /* STOP is already irrevocable and guardian is independent. Only after all
   * writers join may the owner publish a stable terminal diagnostic phase. */
  atomic_store(&b.phase, cleaned ? CLEANUP_OBSERVED : RECOVERY_UNKNOWN);
  result = cleaned ? 0 : 78;
  if (!record(&b, "TERMINAL_LOCAL_ONLY"))
    result = 78;
  /* Retain UNKNOWN ownership until process exit; never name-based repair. */
  if (result == 0) {
    (void)p309_guardian_destroy_after_join(link);
    if (!p309_authority_dispose_after_cleanup(a))
      result = 78;
  }
  p309_peer_destroy_after_join(b.monitor);
  close(b.logfd);
  close(b.h4);
  close(b.admin);
  close(b.gate);
  return result;
}
