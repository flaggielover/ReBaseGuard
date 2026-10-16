/* Fixed root DEV relay/bootstrap. No manager Start, keygen, enrollment or
 * generic signing endpoint. Installation and real device permissions remain
 * prerequisites. Only this one approved connection/boot may be consumed. */
#define _GNU_SOURCE
#include "authority_binding.h"
#include "bootstrap_wire.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <sys/sysmacros.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
#define PORT "org.rebaseguard.p309.h2"
#define ENDPOINT "/run/rebaseguard-p309/host-anchor-v10.sock"
#define SEED                                                                   \
  "/sys/firmware/qemu_fw_cfg/by_name/opt/org.rebaseguard.p309/bootstrap/raw"
static volatile sig_atomic_t stopping;
static void on_signal(int n) {
  (void)n;
  stopping = 1;
}
static int64_t now_ns(void) {
  struct timespec t;
  if (clock_gettime(CLOCK_BOOTTIME, &t))
    return -1;
  return (int64_t)t.tv_sec * 1000000000LL + t.tv_nsec;
}
static int64_t deadline(void) {
  int64_t n = now_ns();
  return n < 0 || n > INT64_MAX - 20000000000LL ? -1 : n + 20000000000LL;
}
/* Root-owned fixed ancestry. Kernel sysfs by_name symlinks are allowed only
 * when explicitly requested; final secret must itself be regular root0400 on
 * sysfs. Ordinary /etc,/run,/var state never permits symlink ancestry. */
static int parents(const char *path, int sysfs) {
  char b[PATH_MAX];
  if (strlen(path) >= sizeof b)
    return 0;
  strcpy(b, path);
  for (char *s = b + 1; *s; s++)
    if (*s == '/') {
      *s = 0;
      struct stat st;
      int ok = !lstat(b, &st) && st.st_uid == 0 &&
               ((S_ISDIR(st.st_mode) && !(st.st_mode & 0022)) ||
                (sysfs && S_ISLNK(st.st_mode)));
      *s = '/';
      if (!ok)
        return 0;
    }
  return 1;
}
static int fixed_read(const char *path, void *out, size_t n, mode_t mode,
                      int sysfs) {
  if (!parents(path, sysfs))
    return 0;
  int f = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (f < 0)
    return 0;
  struct stat st;
  struct statfs fs;
  int ok = !fstat(f, &st) && S_ISREG(st.st_mode) && st.st_uid == 0 &&
           (st.st_mode & 0777) == mode &&
           (sysfs ? (!fstatfs(f, &fs) && fs.f_type == 0x62656572)
                  : st.st_nlink == 1);
  size_t at = 0;
  while (ok && at < n) {
    ssize_t r = read(f, (char *)out + at, n - at);
    if (r < 0 && errno == EINTR)
      continue;
    if (r <= 0) {
      ok = 0;
      break;
    }
    at += (size_t)r;
  }
  char more;
  if (ok && read(f, &more, 1) != 0)
    ok = 0;
  close(f);
  return ok;
}
static int digest(const char *name, char out[65]) {
  char path[256], raw[65];
  int z = snprintf(path, sizeof path, "/etc/rebaseguard-p309/%s", name);
  if (z <= 0 || (size_t)z >= sizeof path ||
      !fixed_read(path, raw, 65, 0444, 0) || raw[64] != '\n')
    return 0;
  for (size_t i = 0; i < 64; i++)
    if (!((raw[i] >= '0' && raw[i] <= '9') || (raw[i] >= 'a' && raw[i] <= 'f')))
      return 0;
  memcpy(out, raw, 64);
  out[64] = 0;
  return 1;
}
static int local_boot(char out[33]) {
  int f = open("/proc/sys/kernel/random/boot_id",
               O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (f < 0)
    return 0;
  char b[38];
  ssize_t n = read(f, b, sizeof b);
  close(f);
  if (n != 37 || b[36] != '\n')
    return 0;
  size_t at = 0;
  for (size_t i = 0; i < 36; i++) {
    if (i == 8 || i == 13 || i == 18 || i == 23) {
      if (b[i] != '-')
        return 0;
      continue;
    }
    if (!((b[i] >= '0' && b[i] <= '9') || (b[i] >= 'a' && b[i] <= 'f')))
      return 0;
    out[at++] = b[i];
  }
  out[32] = 0;
  return at == 32;
}
static int device(void) {
  const char path[] = "/dev/virtio-ports/" PORT;
  if (!parents(path, 0))
    return -1;
  struct stat link;
  char target[96];
  if (lstat(path, &link) || !S_ISLNK(link.st_mode) || link.st_uid)
    return -1;
  ssize_t n = readlink(path, target, sizeof target - 1);
  if (n <= 0 || (size_t)n >= sizeof target - 1)
    return -1;
  target[n] = 0;
  /* Normal udev link ../vport<controller>p<port>; no arbitrary path walk. */
  unsigned a, b;
  char tail;
  if (sscanf(target, "../vport%up%u%c", &a, &b, &tail) != 2)
    return -1;
  char canonical[96];
  int cn = snprintf(canonical, sizeof canonical, "../vport%up%u", a, b);
  if (cn <= 0 || (size_t)cn >= sizeof canonical || strcmp(canonical, target))
    return -1;
  char node[128], sys[256], name[64], numbers[64];
  snprintf(node, sizeof node, "/dev/%s", target + 3);
  int f = open(node, O_RDWR | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW);
  if (f < 0)
    return -1;
  struct stat st = {0};
  int ok = !fstat(f, &st) && S_ISCHR(st.st_mode) && st.st_uid == 0 &&
           st.st_gid == 0 && (st.st_mode & 0777) == 0600;
  snprintf(sys, sizeof sys, "/sys/class/virtio-ports/%s/name", target + 3);
  int q = open(sys, O_RDONLY | O_CLOEXEC);
  ssize_t z = q < 0 ? -1 : read(q, name, sizeof name - 1);
  if (q >= 0)
    close(q);
  if (z <= 0 || (size_t)z >= sizeof name - 1)
    ok = 0;
  else {
    name[z] = 0;
    if (strcmp(name, PORT "\n"))
      ok = 0;
  }
  snprintf(sys, sizeof sys, "/sys/class/virtio-ports/%s/dev", target + 3);
  q = open(sys, O_RDONLY | O_CLOEXEC);
  z = q < 0 ? -1 : read(q, numbers, sizeof numbers - 1);
  if (q >= 0)
    close(q);
  unsigned major_n = 0, minor_n = 0;
  if (z <= 0 || (size_t)z >= sizeof numbers - 1)
    ok = 0;
  else {
    numbers[z] = 0;
    if (sscanf(numbers, "%u:%u%c", &major_n, &minor_n, &tail) != 3 ||
        tail != '\n' || major(st.st_rdev) != major_n ||
        minor(st.st_rdev) != minor_n)
      ok = 0;
  }
  if (!ok) {
    close(f);
    return -1;
  }
  return f;
}
static int wait_io(int fd, short events, int64_t end,
                   const struct p309_peer_identity *peer) {
  for (;;) {
    int64_t n = now_ns();
    if (stopping || end < 0 || n < end - 20000000000LL || n >= end ||
        (peer && !p309_peer_alive(peer)))
      return 0;
    struct pollfd p = {fd, events, 0};
    int r = poll(&p, 1, 50);
    if (r < 0) {
      if (errno == EINTR)
        continue;
      return 0;
    }
    if (p.revents & (POLLHUP | POLLERR | POLLNVAL))
      return 0;
    if (p.revents & events)
      return 1;
  }
}
static int stream_bytes(int fd, unsigned char *b, size_t n, int sending,
                        int64_t end, const struct p309_peer_identity *peer) {
  size_t at = 0;
  while (at < n) {
    if (!wait_io(fd, sending ? POLLOUT : POLLIN, end, peer))
      return 0;
    ssize_t z = sending ? write(fd, b + at, n - at) : read(fd, b + at, n - at);
    if (z < 0 && (errno == EINTR || errno == EAGAIN))
      continue;
    if (z <= 0)
      return 0;
    at += (size_t)z;
  }
  return 1;
}
static int stream_frame(int fd, unsigned char b[8192], size_t *n, int sending,
                        const struct p309_peer_identity *peer) {
  unsigned char header[4];
  int64_t end = deadline();
  if (sending && !p309_frame_header(*n, header))
    return 0;
  if (!stream_bytes(fd, header, 4, sending, end, peer))
    return 0;
  if (!sending && !p309_frame_length(header, n))
    return 0;
  return stream_bytes(fd, b, *n, sending, end, peer);
}
static int listener(void) {
  char pid[32];
  snprintf(pid, sizeof pid, "%ld", (long)getpid());
  if (!getenv("LISTEN_PID") || strcmp(getenv("LISTEN_PID"), pid) ||
      !getenv("LISTEN_FDS") || strcmp(getenv("LISTEN_FDS"), "1") ||
      !getenv("LISTEN_FDNAMES") ||
      strcmp(getenv("LISTEN_FDNAMES"), "host-anchor-v10") ||
      !parents(ENDPOINT, 0))
    return 0;
  struct stat st;
  if (lstat(ENDPOINT, &st) || !S_ISSOCK(st.st_mode) || st.st_uid || st.st_gid ||
      (st.st_mode & 0777) != 0600)
    return 0;
  struct sockaddr_un address = {0};
  socklen_t size = sizeof address;
  int type = 0, accepting = 0;
  socklen_t ts = sizeof type;
  if (getsockname(3, (struct sockaddr *)&address, &size) ||
      address.sun_family != AF_UNIX ||
      size != offsetof(struct sockaddr_un, sun_path) + sizeof ENDPOINT ||
      strcmp(address.sun_path, ENDPOINT) ||
      getsockopt(3, SOL_SOCKET, SO_TYPE, &type, &ts) || type != SOCK_SEQPACKET)
    return 0;
  ts = sizeof accepting;
  if (getsockopt(3, SOL_SOCKET, SO_ACCEPTCONN, &accepting, &ts) || !accepting)
    return 0;
  int flags = fcntl(3, F_GETFL);
  if (flags < 0 || fcntl(3, F_SETFL, flags | O_NONBLOCK) ||
      fcntl(3, F_SETFD, FD_CLOEXEC))
    return 0;
  unsetenv("LISTEN_PID");
  unsetenv("LISTEN_FDS");
  unsetenv("LISTEN_FDNAMES");
  return !close_range(4, UINT_MAX, 0);
}
static int seq_receive(int s, unsigned char b[8192], size_t *n,
                       const struct p309_peer_identity *peer) {
  int64_t end = deadline();
  if (!wait_io(s, POLLIN, end, peer))
    return 0;
  union {
    struct cmsghdr a;
    char bytes[CMSG_SPACE(16 * sizeof(int))];
  } control;
  struct iovec i = {b, 8192};
  struct msghdr m = {0};
  m.msg_iov = &i;
  m.msg_iovlen = 1;
  m.msg_control = control.bytes;
  m.msg_controllen = sizeof control.bytes;
  ssize_t z = recvmsg(s, &m, MSG_CMSG_CLOEXEC | MSG_DONTWAIT);
  if (z < 0)
    return 0;
  int bad = z == 0 || !!(m.msg_flags & (MSG_TRUNC | MSG_CTRUNC));
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
  int64_t received = now_ns();
  if (bad || !p309_peer_alive(peer) || received < end - 20000000000LL ||
      received >= end)
    return 0;
  *n = (size_t)z;
  return 1;
}
static int accepted(struct p309_peer_identity **owner) {
  if (!wait_io(3, POLLIN, deadline(), *owner))
    return -1;
  int s = accept4(3, NULL, NULL, SOCK_NONBLOCK | SOCK_CLOEXEC);
  if (s < 0)
    return -1;
  struct ucred peer;
  socklen_t size = sizeof peer;
  if (getsockopt(s, SOL_SOCKET, SO_PEERCRED, &peer, &size) ||
      size != sizeof peer || peer.uid || peer.pid <= 1) {
    close(s);
    return -1;
  }
  if (!*owner)
    *owner = p309_peer_acquire(P309_PEER_BROKER, peer.pid);
  if (!*owner || !p309_peer_matches(*owner, peer.pid, peer.uid)) {
    close(s);
    return -1;
  }
  return s;
}
static int boot_fence(const unsigned char *b, size_t n, const char *boot) {
  const char path[] = "/var/lib/rebaseguard-p309-control/bootstrap-v11.claim";
  if (!parents(path, 0))
    return 0;
  int d = open("/var/lib/rebaseguard-p309-control",
               O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  struct stat st;
  if (d < 0)
    return 0;
  if (fstat(d, &st) || st.st_uid || (st.st_mode & 0777) != 0700) {
    close(d);
    return 0;
  }
  int f = openat(d, "bootstrap-v11.claim",
                 O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
  if (f < 0) {
    close(d);
    return 0;
  }
  /* Public request plus actual boot only; never persist the seed/HMAC secret.
   */
  int ok =
      write(f, b, n) == (ssize_t)n && write(f, boot, 32) == 32 && fsync(f) == 0;
  if (close(f))
    ok = 0;
  if (fsync(d))
    ok = 0;
  close(d);
  return ok;
}
int main(int argc, char **argv) {
  (void)argv;
  if (argc != 1 || geteuid() != 0 || !listener())
    return 64;
  struct sigaction sa = {0};
  sa.sa_handler = on_signal;
  sigemptyset(&sa.sa_mask);
  if (sigaction(SIGTERM, &sa, NULL) || sigaction(SIGINT, &sa, NULL) ||
      sigaction(SIGHUP, &sa, NULL))
    return 65;
  struct p309_peer_identity *self =
                                p309_peer_acquire(P309_PEER_RELAY, getpid()),
                            *broker = NULL;
  if (!self)
    return 66;
  int h2 = device();
  if (h2 < 0)
    return 67;
  struct p309_boot_inputs in = {0};
  unsigned char secret[32] = {0}, wire[8192], response[2048];
  char seed_pin[65], actual[65];
  if (!local_boot(in.boot) || !digest("package-v9.sha256", in.package) ||
      !digest("guest-v9.sha256", in.guest) ||
      !digest("runtime-v9.sha256", in.runtime) ||
      !digest("policy-v9.sha256", in.policy) ||
      !digest("guest-blocked-v10.spki.sha256", in.root_pin) ||
      !digest("bootstrap-v11.sha256", seed_pin) ||
      !fixed_read(SEED, secret, 32, 0400, 1))
    return 68;
  unsigned char hash[32];
  unsigned hn = 0;
  if (!EVP_Digest(secret, 32, hash, &hn, EVP_sha256(), NULL) || hn != 32)
    return 68;
  for (size_t i = 0; i < 32; i++)
    snprintf(actual + 2 * i, 3, "%02x", hash[i]);
  if (strcmp(actual, seed_pin)) {
    OPENSSL_cleanse(secret, sizeof secret);
    return 68;
  }
  size_t n = 0, rn = 0;
  if (!stream_frame(h2, wire, &n, 0, self) ||
      !p309_bootstrap_response(wire, n, &in, secret, response, &rn) ||
      !boot_fence(wire, n, in.boot)) {
    OPENSSL_cleanse(secret, sizeof secret);
    return 69;
  }
  OPENSSL_cleanse(secret, sizeof secret);
  memcpy(wire, response, rn);
  n = rn;
  if (!stream_frame(h2, wire, &n, 1, self))
    return 70;
  char generation[33] = {0}, challenge[65] = {0};
  for (int phase = 0; phase < 2; phase++) {
    int s = accepted(&broker);
    if (s < 0)
      return 71;
    if (!seq_receive(s, wire, &n, broker) ||
        !p309_root_proof_shape(wire, n, &in, generation, challenge, phase) ||
        !stream_frame(h2, wire, &n, 1, broker)) {
      close(s);
      return 72;
    }
    for (int reply = 0; reply < (phase ? 1 : 2); reply++) {
      if (!stream_frame(h2, wire, &n, 0, broker) || n > 4480 ||
          !p309_peer_alive(broker) ||
          send(s, wire, n, MSG_DONTWAIT | MSG_NOSIGNAL) != (ssize_t)n) {
        close(s);
        return 73;
      }
    }
    close(s);
  }
  /* Preserve the same owned H2 connection after Final. Loss/extra traffic exits
   * this held relay instance; broker's pinned relay pidfd watchdog then Stops.
   * No reconnect, fresh nonce, second broker transaction or restart/rearm. */
  for (;;) {
    if (stopping || !p309_peer_alive(broker))
      return 74;
    struct pollfd fds[3] = {
        {h2, POLLIN, 0}, {3, POLLIN, 0}, {p309_peer_pidfd(broker), POLLIN, 0}};
    int rc = poll(fds, 3, 50);
    if (rc < 0 && errno == EINTR)
      continue;
    if (rc < 0 || fds[0].revents || fds[1].revents || fds[2].revents)
      return 74;
  }
}
