/* Linux source only, not compiled/executed/installed by this preparation.
 * One systemd socket activation, one root handoff, one generation. No adoption.
 * Holds kernel objects after stop. LOCAL_QUIESCENT != manager cleanup or
 * STOPPED.
 */
#define _GNU_SOURCE
#include "authority_binding.h"
#include "held_stop_write.h"
#include "protocol.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
#define CGROUP2_MAGIC 0x63677270
#define LEASE_NS 3000000000LL
#define HARD_NS 120000000000LL
#define BOOTSTRAP_MS 3000
static volatile sig_atomic_t requested = 0;
static void on_signal(int sig) {
  (void)sig;
  requested = 1;
}
static int64_t now_ns(void) {
  struct timespec t;
  if (clock_gettime(CLOCK_BOOTTIME, &t))
    return -1;
  return (int64_t)t.tv_sec * 1000000000LL + t.tv_nsec;
}
static int poll_one(int fd, short what, int timeout) {
  struct pollfd p = {fd, what, 0};
  int n;
  do {
    n = poll(&p, 1, timeout);
  } while (n < 0 && errno == EINTR && !requested);
  return n < 0 ? -1 : n == 0 ? 0 : p.revents;
}
static int read_at(int dir, const char *name, char *buf, size_t size) {
  int fd = openat(dir, name, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
  if (fd < 0)
    return -1;
  ssize_t n = read(fd, buf, size);
  int saved = errno;
  close(fd);
  errno = saved;
  if (n < 0 || (size_t)n >= size)
    return -1;
  buf[n] = 0;
  return (int)n;
}
static int link_is(int fd, const char *expected) {
  char path[64], value[PATH_MAX];
  snprintf(path, sizeof path, "/proc/self/fd/%d", fd);
  ssize_t n = readlink(path, value, sizeof value - 1);
  if (n < 0 || (size_t)n >= sizeof value - 1)
    return 0;
  value[n] = 0;
  return !strcmp(value, expected);
}
static pid_t pidfd_pid(int fd) {
  char path[64], buf[2048];
  if (!link_is(fd, "anon_inode:[pidfd]"))
    return -1;
  snprintf(path, sizeof path, "/proc/self/fdinfo/%d", fd);
  int f = open(path, O_RDONLY | O_CLOEXEC);
  if (f < 0)
    return -1;
  ssize_t n = read(f, buf, sizeof buf - 1);
  close(f);
  if (n <= 0 || n == (ssize_t)sizeof buf - 1)
    return -1;
  buf[n] = 0;
  char *p = strstr(buf, "\nPid:\t");
  if (!p)
    return -1;
  char *end;
  errno = 0;
  long v = strtol(p + 6, &end, 10);
  if (errno || *end != '\n' || v <= 1 || v > INT_MAX)
    return -1;
  return (pid_t)v;
}
static int exited(int fd) {
  int ev = poll_one(fd, POLLIN, 0);
  if (ev < 0 || (ev & (POLLERR | POLLNVAL)))
    return -1;
  return !!(ev & POLLIN);
}
static int protected_dir(int fd) {
  struct stat st;
  return !fstat(fd, &st) && S_ISDIR(st.st_mode) && st.st_uid == 0 &&
         !(st.st_mode & 0022);
}
static int endpoint_parent(void) {
  int fd = open("/", O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
  const char *parts[] = {"run", "rebaseguard-p309"};
  if (fd < 0)
    return 0;
  for (size_t i = 0; i < 2; i++) {
    if (!protected_dir(fd)) {
      close(fd);
      return 0;
    }
    int next =
        openat(fd, parts[i], O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    close(fd);
    fd = next;
    if (fd < 0)
      return 0;
  }
  int ok = protected_dir(fd);
  struct stat st;
  ok = ok && !fstatat(fd, "guardian-v9.sock", &st, AT_SYMLINK_NOFOLLOW) &&
       S_ISSOCK(st.st_mode) && st.st_uid == 0 && st.st_gid == 0 &&
       (st.st_mode & 0777) == 0600;
  close(fd);
  return ok;
}
static int listener_ok(int fd) {
  int type = 0, accepting = 0;
  socklen_t n = sizeof type;
  struct sockaddr_un a = {0};
  if (getsockopt(fd, SOL_SOCKET, SO_TYPE, &type, &n) || type != SOCK_SEQPACKET)
    return 0;
  n = sizeof accepting;
  if (getsockopt(fd, SOL_SOCKET, SO_ACCEPTCONN, &accepting, &n) || !accepting)
    return 0;
  n = sizeof a;
  if (getsockname(fd, (struct sockaddr *)&a, &n) || a.sun_family != AF_UNIX)
    return 0;
  return n == offsetof(struct sockaddr_un, sun_path) +
                  strlen(P309_GUARD_SOCKET) + 1 &&
         !strcmp(a.sun_path, P309_GUARD_SOCKET) && endpoint_parent();
}
/* Receive descriptors only at handoff. Close every delivered FD on malformed
 * input. */
static ssize_t receive(int sock, char *buf, int out[5], size_t *count,
                       int allow_fds) {
  union {
    struct cmsghdr align;
    char bytes[CMSG_SPACE(16 * sizeof(int))];
  } control;
  struct iovec iov = {buf, P309_PACKET_MAX};
  struct msghdr m = {0};
  m.msg_iov = &iov;
  m.msg_iovlen = 1;
  m.msg_control = control.bytes;
  m.msg_controllen = sizeof control.bytes;
  *count = 0;
  ssize_t n = recvmsg(sock, &m, MSG_CMSG_CLOEXEC | MSG_DONTWAIT);
  if (n < 0)
    return n;
  int all[16], total = 0,
               bad = n == 0 || !!(m.msg_flags & (MSG_TRUNC | MSG_CTRUNC));
  for (struct cmsghdr *c = CMSG_FIRSTHDR(&m); c; c = CMSG_NXTHDR(&m, c)) {
    if (c->cmsg_level != SOL_SOCKET || c->cmsg_type != SCM_RIGHTS) {
      bad = 1;
      continue;
    }
    if (c->cmsg_len < CMSG_LEN(0)) {
      bad = 1;
      continue;
    }
    size_t bytes = c->cmsg_len - CMSG_LEN(0);
    if (bytes % sizeof(int))
      bad = 1;
    size_t num = bytes / sizeof(int);
    int *p = (int *)CMSG_DATA(c);
    for (size_t i = 0; i < num; i++) {
      if (total < 16)
        all[total++] = p[i];
      else {
        close(p[i]);
        bad = 1;
      }
    }
  }
  if ((allow_fds && total != 5) || (!allow_fds && total))
    bad = 1;
  if (bad) {
    for (int i = 0; i < total; i++)
      close(all[i]);
    errno = EPROTO;
    return -1;
  }
  for (int i = 0; i < total; i++)
    out[i] = all[i];
  *count = (size_t)total;
  return n;
}
static int send_frame(int sock, const char *verb, const char *g) {
  char raw[P309_PACKET_MAX];
  size_t n = p309_packet(raw, verb, g);
  return n && send(sock, raw, n, MSG_DONTWAIT | MSG_NOSIGNAL) == (ssize_t)n;
}
static int handoff_ok(int f[5], pid_t peer) {
  /* Ordered FDs: broker pidfd, worker pidfd, cgroup dir, cgroup.kill, heartbeat
   * read. */
  if (pidfd_pid(f[0]) != peer || exited(f[0]) != 0 || exited(f[1]) != 0)
    return 0;
  pid_t worker = pidfd_pid(f[1]);
  if (worker <= 1 || worker == peer)
    return 0;
  struct stat ds, ks, at, beat;
  struct statfs fs;
  char buf[256], path[64];
  if (!protected_dir(f[2]) || !link_is(f[2], P309_CGROUP) ||
      fstatfs(f[2], &fs) || fs.f_type != CGROUP2_MAGIC)
    return 0;
  if (read_at(f[2], "cgroup.type", buf, sizeof buf) < 0 ||
      strcmp(buf, "domain\n"))
    return 0;
  if (fstat(f[2], &ds) || fstat(f[3], &ks) ||
      fstatat(f[2], "cgroup.kill", &at, AT_SYMLINK_NOFOLLOW))
    return 0;
  if (!S_ISREG(ks.st_mode) || ks.st_uid != 0 || (ks.st_mode & 0022) ||
      ks.st_dev != at.st_dev || ks.st_ino != at.st_ino ||
      !link_is(f[3], P309_CGROUP "/cgroup.kill"))
    return 0;
  int kflags = fcntl(f[3], F_GETFL), bflags = fcntl(f[4], F_GETFL);
  if (kflags < 0 || (kflags & O_ACCMODE) != O_WRONLY || bflags < 0 ||
      (bflags & O_ACCMODE) != O_RDONLY || fstat(f[4], &beat) ||
      !S_ISFIFO(beat.st_mode) || poll_one(f[4], POLLIN, 0) != 0)
    return 0;
  snprintf(path, sizeof path, "/proc/%d/cgroup", worker);
  int p = open(path, O_RDONLY | O_CLOEXEC);
  if (p < 0)
    return 0;
  ssize_t n = read(p, buf, sizeof buf - 1);
  close(p);
  if (n < 0 || (size_t)n >= sizeof buf - 1)
    return 0;
  buf[n] = 0;
  if (strcmp(buf, P309_MEMBER) || exited(f[1]) != 0)
    return 0;
  if (fcntl(f[4], F_SETFL, bflags | O_NONBLOCK))
    return 0;
  return 1;
}
static int quiescent(int f[5]) {
  char buf[256];
  if (exited(f[1]) != 1 || read_at(f[2], "cgroup.events", buf, sizeof buf) < 0)
    return 0;
  int populated = -1, frozen = -1;
  char *save = NULL;
  for (char *line = strtok_r(buf, "\n", &save); line;
       line = strtok_r(NULL, "\n", &save)) {
    if (!strcmp(line, "populated 0")) {
      if (populated != -1)
        return 0;
      populated = 0;
    } else if (!strcmp(line, "populated 1")) {
      if (populated != -1)
        return 0;
      populated = 1;
    } else if (!strcmp(line, "frozen 0")) {
      if (frozen != -1)
        return 0;
      frozen = 0;
    } else if (!strcmp(line, "frozen 1")) {
      if (frozen != -1)
        return 0;
      frozen = 1;
    } else
      return 0;
  }
  return populated == 0 && frozen == 0;
}
static int64_t now_ns(void);
static int64_t stop_clock(void *ctx) {
  (void)ctx;
  return now_ns();
}
static long stop_write_once(int fd, void *ctx) {
  (void)ctx;
  return (long)write(fd, "1\n", 2);
}
static void publish_stop(int sock, int killfd, const char *g, bool *notified,
                         bool *write_ok) {
  if (*notified)
    return;
  *write_ok =
      p309_stop_write_bounded(killfd, stop_write_once, stop_clock, NULL);
  *notified = true;
  (void)send_frame(sock, *write_ok ? "STOP_REQUESTED" : "STOP_WRITE_UNKNOWN",
                   g);
}
int main(void) {
  if (geteuid() != 0)
    return 64;
  char expected[32];
  snprintf(expected, sizeof expected, "%ld", (long)getpid());
  if (!getenv("LISTEN_PID") || strcmp(getenv("LISTEN_PID"), expected) ||
      !getenv("LISTEN_FDS") || strcmp(getenv("LISTEN_FDS"), "1") ||
      !getenv("LISTEN_FDNAMES") ||
      strcmp(getenv("LISTEN_FDNAMES"), "guardian-v9") || !listener_ok(3))
    return 65;
  unsetenv("LISTEN_PID");
  unsetenv("LISTEN_FDS");
  unsetenv("LISTEN_FDNAMES");
  if (close_range(4, UINT_MAX, 0))
    return 65;
  struct sigaction sa = {0};
  sa.sa_handler = on_signal;
  sigemptyset(&sa.sa_mask);
  if (sigaction(SIGTERM, &sa, NULL) || sigaction(SIGINT, &sa, NULL) ||
      sigaction(SIGHUP, &sa, NULL))
    return 65;
  if (poll_one(3, POLLIN, BOOTSTRAP_MS) <= 0)
    return 66;
  int sock = accept4(3, NULL, NULL, SOCK_CLOEXEC | SOCK_NONBLOCK);
  close(3);
  if (sock < 0)
    return 66;
  struct ucred peer = {0};
  socklen_t peerlen = sizeof peer;
  if (getsockopt(sock, SOL_SOCKET, SO_PEERCRED, &peer, &peerlen) ||
      peerlen != sizeof peer || peer.uid != 0 || peer.pid <= 1)
    return 66;
  if (poll_one(sock, POLLIN, BOOTSTRAP_MS) <= 0)
    return 66;
  char raw[P309_PACKET_MAX], g[33], other[33];
  int f[5] = {-1, -1, -1, -1, -1};
  size_t count;
  ssize_t n = receive(sock, raw, f, &count, 1);
  if (n <= 0 || !p309_parse(raw, (size_t)n, "BIND", g) ||
      !handoff_ok(f, peer.pid))
    return 67;
  /* Structural FD checks alone NEVER establish successful-start ownership.
   * Manager/permit-derived record and current broker/worker identities are
   * independently required before READY or any cgroup write. */
  if (!p309_authorize_guardian(peer.pid, g, f))
    return 78;
  /* From this point we own a validated kill FD. Every failure latches stop. */
  bool stopped = false, write_ok = false, notified = false,
       local_notified = false, connected = true;
  int64_t started = now_ns(), last = started, previous = started;
  if (started < 0 || requested || !send_frame(sock, "READY", g))
    stopped = true;
  for (;;) {
    int64_t now = now_ns();
    if (now < 0 || now < previous || now - last >= LEASE_NS ||
        now - started >= HARD_NS || requested)
      stopped = true;
    if (now >= 0)
      previous = now;
    if (stopped)
      publish_stop(sock, f[3], g, &notified, &write_ok);
    struct pollfd p[4] = {{connected ? sock : -1, POLLIN, 0},
                          {stopped ? -1 : f[4], POLLIN, 0},
                          {stopped ? -1 : f[0], POLLIN, 0},
                          {stopped ? -1 : f[1], POLLIN, 0}};
    int rc = poll(p, 4, stopped ? 100 : 50);
    if (rc < 0 && errno != EINTR)
      stopped = true;
    if (p[2].revents || p[3].revents)
      stopped = true;
    if (p[0].revents & (POLLHUP | POLLERR | POLLNVAL)) {
      stopped = true;
      connected = false;
    }
    if (p[1].revents & (POLLHUP | POLLERR | POLLNVAL))
      stopped = true;
    if (!stopped && (p[1].revents & POLLIN)) {
      char beat[2];
      ssize_t got = read(f[4], beat, sizeof beat);
      int64_t t = now_ns();
      if (got != 1 || beat[0] != 'H' || t < last || t < 0 ||
          t - last >= LEASE_NS || t - started >= HARD_NS)
        stopped = true;
      else
        last = t;
    }
    bool retire = false;
    if (p[0].revents & POLLIN) {
      int ignored[5];
      size_t nf = 0;
      ssize_t got = receive(sock, raw, ignored, &nf, 0);
      if (got <= 0) {
        stopped = true;
        connected = false;
      } else if (p309_parse(raw, (size_t)got, "STOP", other) &&
                 !strcmp(other, g))
        stopped = true;
      else if (stopped && p309_parse(raw, (size_t)got, "RETIRE", other) &&
               !strcmp(other, g))
        retire = true;
      else
        stopped = true;
    }
    if (stopped)
      publish_stop(sock, f[3], g, &notified, &write_ok);
    bool local = stopped && write_ok && quiescent(f);
    if (local && !local_notified) {
      local_notified = true;
      (void)send_frame(sock, "LOCAL_QUIESCENT", g);
    }
    if (retire && local) {
      /* Root broker must independently establish manager/no-inflight proof.
       * This ack is permission to close these FDs, not a STOPPED assertion. */
      (void)send_frame(sock, "RETIRING", g);
      for (int i = 0; i < 5; i++)
        close(f[i]);
      close(sock);
      return 0;
    }
    /* EOF after stop never forgets identity or automatically exits/rearms.
     * Lost broker requires separately reviewed administrative reconciliation.
     */
  }
}
