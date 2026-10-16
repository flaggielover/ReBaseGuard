"""Fixed development-unit stop primitive; no launcher, daemon or public CLI.

Only a future reviewed root broker can bind this from its own successful start
transaction. Merely finding a named unit MUST NOT authorize adoption. The caller
must supply its internally recorded invocation, PID and start ticks. No wire
request is allowed to supply these fields. Actual deployment remains unapproved.
"""
from dataclasses import dataclass
import os
import re
import select
import stat
import subprocess

UNIT = 'p309-dev-owned-check.service'
CGROUP = '/system.slice/' + UNIT
SYSTEMCTL = '/usr/bin/systemctl'
PROPERTIES = ('Id', 'InvocationID', 'MainPID', 'ExecMainPID', 'ControlGroup',
              'ActiveState', 'SubState', 'Result', 'Job')


class OwnershipUnknown(RuntimeError):
    pass


def parse_properties(raw):
    if type(raw) is not bytes or len(raw) > 16384:
        raise OwnershipUnknown('invalid manager response length')
    try:
        rows = raw.decode('ascii').splitlines()
        result = {}
        for line in rows:
            key, value = line.split('=', 1)
            if key not in PROPERTIES or key in result:
                raise ValueError('duplicate or extra property')
            result[key] = value
        if set(result) != set(PROPERTIES):
            raise ValueError('missing property')
        for name in ('MainPID', 'ExecMainPID'):
            if not re.fullmatch(r'0|[1-9][0-9]*', result[name]):
                raise ValueError('invalid PID')
            result[name] = int(result[name])
        return result
    except (UnicodeError, ValueError) as exc:
        raise OwnershipUnknown('malformed manager response') from exc


def manager_facts():
    # Fixed executable, unit and property list. No shell or request arguments.
    try:
        p = subprocess.run([SYSTEMCTL, 'show', UNIT, '--no-pager',
                            '--property=' + ','.join(PROPERTIES)],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, timeout=2, check=True,
                           close_fds=True, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
    except (OSError, subprocess.SubprocessError) as exc:
        raise OwnershipUnknown('manager unavailable') from exc
    return parse_properties(p.stdout)


def proc_start_ticks(pid):
    try:
        with open('/proc/%d/stat' % pid, 'rb') as f:
            raw = f.read(4097)
        if len(raw) > 4096 or not raw.startswith(('%d (' % pid).encode()):
            raise ValueError('stat shape')
        # comm may contain spaces or ')'; fields after the final ')' begin at 3.
        fields = raw[raw.rindex(b')') + 2:].split()
        return int(fields[19])
    except (OSError, ValueError, IndexError) as exc:
        raise OwnershipUnknown('process start identity unavailable') from exc


def _protected_dir(fd):
    st = os.fstat(fd)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o022:
        raise OwnershipUnknown('unprotected directory')
    return st


def open_fixed_cgroup():
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    fd = os.open('/', flags)
    try:
        _protected_dir(fd)
        for part in ('sys', 'fs', 'cgroup', 'system.slice', UNIT):
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
            _protected_dir(fd)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _read_at(directory, name, limit=4096):
    fd = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW, dir_fd=directory)
    try:
        result = os.read(fd, limit + 1)
        if len(result) > limit:
            raise OwnershipUnknown('oversized kernel fact')
        return result
    finally:
        os.close(fd)


def parse_cgroup_events(raw):
    try:
        rows = [line.split() for line in raw.decode('ascii').splitlines()]
        result = {}
        for key, value in rows:
            if key in result or value not in ('0', '1'):
                raise ValueError('ambiguous cgroup event')
            result[key] = int(value)
        if 'populated' not in result or 'frozen' not in result:
            raise ValueError('missing kernel evidence')
        return result
    except (UnicodeError, ValueError) as exc:
        raise OwnershipUnknown('malformed cgroup events') from exc


@dataclass(frozen=True)
class StartedIdentity:
    """Root broker internal start receipt; NEVER deserialize from H1-H4."""
    generation: str
    invocation: str
    pid: int
    start_ticks: int
    boot_id: str

    def validate(self):
        if (type(self.generation) is not str or not re.fullmatch('[0-9a-f]{32}', self.generation)
                or type(self.invocation) is not str or not re.fullmatch('[0-9a-f]{32}', self.invocation)
                or type(self.pid) is not int or self.pid <= 1
                or type(self.start_ticks) is not int or self.start_ticks <= 0
                or type(self.boot_id) is not str or not re.fullmatch(
                    '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', self.boot_id)):
            raise OwnershipUnknown('invalid internal receipt')


class BoundInstance:
    def __init__(self, identity):
        identity.validate()
        if os.geteuid() != 0:
            raise OwnershipUnknown('root broker required')
        self.identity = identity
        self.pidfd = self.directory = self.killfd = None
        self.stop_latched = False
        self.stop_write_error = None
        self.cleanup_confirmed = False
        try:
            with open('/proc/sys/kernel/random/boot_id', encoding='ascii') as f:
                if f.read().strip() != identity.boot_id:
                    raise OwnershipUnknown('wrong boot')
            before = manager_facts()
            self._match_running(before)
            if proc_start_ticks(identity.pid) != identity.start_ticks:
                raise OwnershipUnknown('wrong process generation')
            self.pidfd = os.pidfd_open(identity.pid, 0)
            os.set_inheritable(self.pidfd, False)
            self.directory = open_fixed_cgroup()
            self.cgroup_stat = os.fstat(self.directory)
            self.killfd = os.open('cgroup.kill', os.O_WRONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                                  dir_fd=self.directory)
            with open('/proc/%d/cgroup' % identity.pid, 'rb') as f:
                if f.read(4097) != ('0::' + CGROUP + '\n').encode('ascii'):
                    raise OwnershipUnknown('main process not in owned cgroup')
            if proc_start_ticks(identity.pid) != identity.start_ticks or self._exited():
                raise OwnershipUnknown('identity raced binding')
            self._match_running(manager_facts())
        except BaseException:
            self._dispose_binding()
            raise

    def _match_running(self, facts):
        if (facts['Id'] != UNIT or facts['InvocationID'] != self.identity.invocation
                or facts['MainPID'] != self.identity.pid or facts['ExecMainPID'] != self.identity.pid
                or facts['ControlGroup'] != CGROUP or facts['ActiveState'] != 'active'
                or facts['SubState'] != 'running' or facts['Job'] not in ('', '0')):
            raise OwnershipUnknown('manager invocation mismatch or in-flight job')

    def _exited(self):
        p = select.poll()
        p.register(self.pidfd, select.POLLIN)
        events = p.poll(0)
        if any(flags & (select.POLLNVAL | select.POLLERR) for _, flags in events):
            raise OwnershipUnknown('invalid pidfd observation')
        return any(flags & select.POLLIN for _, flags in events)

    def request_stop(self):
        """Latch first. Only the already-held cgroup.kill FD is written.

        Does not query systemd, log, persist, wait or reopen a pathname. This is
        a stop request, NOT a cleanup acknowledgement. The caller must arrange a
        genuinely independent guardian; this class alone is not that guardian.
        """
        self.stop_latched = True
        if self.killfd is None:
            self.stop_write_error = 'closed ownership binding'
            return False
        try:
            if os.write(self.killfd, b'1\n') != 2:
                raise OSError('short cgroup.kill write')
            return True
        except OSError as exc:
            self.stop_write_error = str(exc)
            return False

    def cleanup_facts(self):
        """Conservative fixed-unit proof. Missing/replaced/GC state is UNKNOWN."""
        result = {'generation': self.identity.generation, 'cleanup_confirmed': False,
                  'formal_admission': 'BLOCKED', 'state': 'RECOVERY_UNKNOWN'}
        try:
            if not self.stop_latched or self.stop_write_error is not None:
                raise OwnershipUnknown('stop request not established')
            if self.directory is None or self.pidfd is None:
                raise OwnershipUnknown('closed ownership handles')
            now = os.fstat(self.directory)
            if (now.st_dev, now.st_ino) != (self.cgroup_stat.st_dev, self.cgroup_stat.st_ino):
                raise OwnershipUnknown('cgroup object changed')
            events = parse_cgroup_events(_read_at(self.directory, 'cgroup.events'))
            facts = manager_facts()
            if facts['Id'] != UNIT or facts['InvocationID'] != self.identity.invocation:
                raise OwnershipUnknown('manager identity absent or replaced')
            proven = (self._exited() and events['populated'] == 0 and events['frozen'] == 0
                      and facts['MainPID'] == 0 and facts['ExecMainPID'] == self.identity.pid
                      and facts['ActiveState'] in ('inactive', 'failed')
                      and facts['SubState'] in ('dead', 'failed') and facts['Job'] in ('', '0'))
            result.update(state='STOPPED' if proven else 'CLEANUP_PENDING',
                          cleanup_confirmed=proven, manager=facts, cgroup_events=events)
            self.cleanup_confirmed = proven
        except (OSError, OwnershipUnknown) as exc:
            result['reason'] = str(exc)
        return result

    def close(self):
        # Reject accidentally dropping the only held ownership binding before
        # cleanup. Construction failure uses a separate private disposal path.
        if not self.cleanup_confirmed:
            raise OwnershipUnknown('cannot release ownership before proven cleanup')
        self._dispose_binding()

    def _dispose_binding(self):
        for name in ('killfd', 'directory', 'pidfd'):
            value = getattr(self, name, None)
            if value is not None:
                os.close(value)
                setattr(self, name, None)
