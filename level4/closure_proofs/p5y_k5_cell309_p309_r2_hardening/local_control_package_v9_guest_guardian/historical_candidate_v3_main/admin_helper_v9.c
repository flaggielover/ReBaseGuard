/* Fixed root administrative action, never reachable through H1-H4. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
static int64_t now_ns(void) {
  struct timespec t;
  if (clock_gettime(CLOCK_BOOTTIME, &t))
    return -1;
  return (int64_t)t.tv_sec * 1000000000LL + t.tv_nsec;
}
int main(int argc, char **argv) {
  (void)argv;
  if (argc != 1 || geteuid() != 0 || close_range(3, UINT_MAX, 0))
    return 64;
  const char *parents[] = {"/", "/run", "/run/rebaseguard-p309"};
  struct stat st;
  for (size_t i = 0; i < 3; i++)
    if (lstat(parents[i], &st) || !S_ISDIR(st.st_mode) || st.st_uid ||
        (st.st_mode & 0022))
      return 65;
  const char path[] = "/run/rebaseguard-p309/admin-v9.sock";
  if (lstat(path, &st) || !S_ISSOCK(st.st_mode) || st.st_uid || st.st_gid ||
      (st.st_mode & 0777) != 0600)
    return 65;
  int s = socket(AF_UNIX, SOCK_SEQPACKET | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
  if (s < 0)
    return 66;
  struct sockaddr_un address = {0};
  address.sun_family = AF_UNIX;
  memcpy(address.sun_path, path, sizeof path);
  if (connect(s, (struct sockaddr *)&address,
              offsetof(struct sockaddr_un, sun_path) + sizeof path))
    return 66;
  struct ucred peer;
  socklen_t size = sizeof peer;
  if (getsockopt(s, SOL_SOCKET, SO_PEERCRED, &peer, &size) ||
      size != sizeof peer || peer.uid != 0)
    return 66;
  static const char command[] = "PREPARE_DEV_IDLE_V9\n",
                    expected[] = "REQUEST_ACCEPTED_NOT_EXECUTED\n";
  if (send(s, command, sizeof command - 1, MSG_DONTWAIT | MSG_NOSIGNAL) !=
      (ssize_t)(sizeof command - 1))
    return 67;
  int64_t start = now_ns(), previous = start;
  if (start < 0)
    return 68;
  for (;;) {
    int64_t now = now_ns();
    if (now < previous || now - start >= 5000000000LL)
      return 68;
    previous = now;
    struct pollfd p = {s, POLLIN, 0};
    int rc = poll(&p, 1, 50);
    if (rc < 0) {
      if (errno == EINTR)
        continue;
      return 68;
    }
    if (p.revents & (POLLERR | POLLNVAL))
      return 68;
    if ((p.revents & POLLHUP) && !(p.revents & POLLIN))
      return 68;
    if (!(p.revents & POLLIN))
      continue;
    unsigned char raw[128];
    union {
      struct cmsghdr align;
      char bytes[CMSG_SPACE(16 * sizeof(int))];
    } ancillary;
    struct iovec i = {raw, sizeof raw};
    struct msghdr m = {0};
    m.msg_iov = &i;
    m.msg_iovlen = 1;
    m.msg_control = ancillary.bytes;
    m.msg_controllen = sizeof ancillary.bytes;
    ssize_t n = recvmsg(s, &m, MSG_DONTWAIT | MSG_CMSG_CLOEXEC);
    if (n < 0)
      return 69;
    int bad = !!(m.msg_flags & (MSG_TRUNC | MSG_CTRUNC));
    for (struct cmsghdr *c = CMSG_FIRSTHDR(&m); c; c = CMSG_NXTHDR(&m, c)) {
      bad = 1;
      if (c->cmsg_level == SOL_SOCKET && c->cmsg_type == SCM_RIGHTS &&
          c->cmsg_len >= CMSG_LEN(0)) {
        int *fds = (int *)CMSG_DATA(c);
        size_t count = (c->cmsg_len - CMSG_LEN(0)) / sizeof(int);
        for (size_t j = 0; j < count; j++)
          close(fds[j]);
      }
    }
    close(s);
    return !bad && n == (ssize_t)(sizeof expected - 1) &&
                   !memcmp(raw, expected, sizeof expected - 1)
               ? 0
               : 69;
  }
}
