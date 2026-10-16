/* Development-only fixed idle guardian; no launcher or P309 authority.
 * Receives an already-bound cgroup.kill FD and a private heartbeat pipe from
 * its trusted root parent. Never discovers PIDs/units or reopens a kill path.
 * A future installer/controller must protect this binary and every ancestor.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <time.h>
#include <unistd.h>

#define CGROUP2_SUPER_MAGIC 0x63677270
#define IDLE_HARD_LIMIT_MS 120000LL
#define HEARTBEAT_LEASE_MS 3000LL
static int kill_fd = -1;

static void stop_and_exit(int code) {
    /* write and _exit are async-signal-safe; no stdio, manager or storage wait. */
    if (kill_fd >= 0 && write(kill_fd, "1\n", 2) != 2) _exit(74);
    _exit(code);
}

static void stopped_signal(int sig) { (void)sig; stop_and_exit(73); }

static int parse_fd(const char *s) {
    char *end = NULL;
    if (!s || !*s || s[0] == '+' || s[0] == '-') return -1;
    errno = 0;
    long n = strtol(s, &end, 10);
    if (errno || !end || *end || n < 3 || n > INT_MAX) return -1;
    return (int)n;
}

static int64_t now_ms(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_BOOTTIME, &t) != 0) stop_and_exit(72);
    return (int64_t)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}

int main(int argc, char **argv) {
    if (argc != 4 || strcmp(argv[1], "--fixed-idle-owned-fds") != 0 || geteuid() != 0)
        return 64;
    int heartbeat_fd = parse_fd(argv[2]);
    int candidate_kill_fd = parse_fd(argv[3]);
    if (heartbeat_fd < 0 || candidate_kill_fd < 0 || heartbeat_fd == candidate_kill_fd)
        return 64;
    struct stat beat_stat, stop_stat;
    struct statfs stop_fs;
    int stop_flags = fcntl(candidate_kill_fd, F_GETFL);
    int beat_flags = fcntl(heartbeat_fd, F_GETFL);
    char fd_path[64], bound_path[256];
    int n = snprintf(fd_path, sizeof(fd_path), "/proc/self/fd/%d", candidate_kill_fd);
    if (n < 0 || n >= (int)sizeof(fd_path)) return 65;
    ssize_t bytes = readlink(fd_path, bound_path, sizeof(bound_path) - 1);
    if (bytes < 0 || bytes >= (ssize_t)sizeof(bound_path) - 1) return 65;
    bound_path[bytes] = 0;
    if (strcmp(bound_path, "/sys/fs/cgroup/system.slice/p309-dev-owned-check.service/cgroup.kill") != 0
        || fstat(heartbeat_fd, &beat_stat) || !S_ISFIFO(beat_stat.st_mode)
        || fstat(candidate_kill_fd, &stop_stat) || stop_stat.st_uid != 0
        || !S_ISREG(stop_stat.st_mode) || (stop_stat.st_mode & 0022)
        || fstatfs(candidate_kill_fd, &stop_fs) || stop_fs.f_type != CGROUP2_SUPER_MAGIC
        || stop_flags < 0 || (stop_flags & O_ACCMODE) != O_WRONLY
        || beat_flags < 0 || (beat_flags & O_ACCMODE) != O_RDONLY)
        return 65;
    kill_fd = candidate_kill_fd;
    const int64_t started = now_ms();
    pid_t parent = getppid();
    if (parent <= 1) stop_and_exit(66);
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = stopped_signal;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGTERM, &sa, NULL) || sigaction(SIGINT, &sa, NULL)
        || sigaction(SIGHUP, &sa, NULL) || sigaction(SIGPIPE, &sa, NULL)) stop_and_exit(66);
    if (prctl(PR_SET_PDEATHSIG, SIGTERM) || getppid() != parent
        || prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) || prctl(PR_SET_DUMPABLE, 0))
        stop_and_exit(66);
    if (fcntl(heartbeat_fd, F_SETFD, FD_CLOEXEC) || fcntl(kill_fd, F_SETFD, FD_CLOEXEC)
        || fcntl(heartbeat_fd, F_SETFL, beat_flags | O_NONBLOCK)) stop_and_exit(66);
    /* Parent must use close_fds/pass_fds to give us only these descriptors.
     * Close any unexpected descriptors here as defense in depth. */
    unsigned low = heartbeat_fd < kill_fd ? (unsigned)heartbeat_fd : (unsigned)kill_fd;
    unsigned high = heartbeat_fd > kill_fd ? (unsigned)heartbeat_fd : (unsigned)kill_fd;
    if ((low > 3 && close_range(3, low - 1, 0))
        || (high > low + 1 && close_range(low + 1, high - 1, 0))
        || close_range(high + 1, UINT_MAX, 0)) stop_and_exit(66);
    int64_t last = started;
    for (;;) {
        int64_t now = now_ms();
        if (now < last || now - started >= IDLE_HARD_LIMIT_MS
            || now - last >= HEARTBEAT_LEASE_MS) stop_and_exit(70);
        struct pollfd item = {heartbeat_fd, POLLIN, 0};
        int rc = poll(&item, 1, 100);
        if (rc < 0) { if (errno == EINTR) continue; stop_and_exit(71); }
        if (item.revents & (POLLHUP | POLLERR | POLLNVAL)) stop_and_exit(71);
        if (item.revents & POLLIN) {
            char message[2];
            ssize_t got = read(heartbeat_fd, message, sizeof(message));
            /* Backlogged/duplicated heartbeats cannot manufacture a new lease. */
            if (got != 1 || message[0] != 'H') stop_and_exit(71);
            now = now_ms();
            if (now < last || now - last >= HEARTBEAT_LEASE_MS
                || now - started >= IDLE_HARD_LIMIT_MS) stop_and_exit(70);
            last = now;
        }
    }
}
