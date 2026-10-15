"""Bounded Linux process-tree fixture. Never accepts a command, PID, or grant.

The dedicated subreaper owns an unreaped group leader until its final signal.
Only this fixed, non-escaping three-process fixture is supported. This is not
containment for arbitrary or hostile workloads, nor a P309 execution adapter.
"""
import ctypes
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import threading
import time


class StopError(RuntimeError):
    pass


def identity(pid):
    """Linux /proc identity; comm may contain whitespace and parentheses."""
    fields = Path('/proc/%d/stat' % pid).read_text().rsplit(')', 1)[1].split()
    return dict(pid=pid, state=fields[0], ppid=int(fields[1]),
                pgid=int(fields[2]), sid=int(fields[3]), start_ticks=int(fields[19]))


def _signal_owned(leader, owner_pid, sig):
    current = identity(leader['pid'])
    if (current['start_ticks'] != leader['start_ticks'] or
            current['ppid'] != owner_pid or current['pgid'] != leader['pid'] or
            current['sid'] != owner_pid or leader['pid'] == os.getpgrp()):
        raise StopError('owned group leader identity mismatch; no signal sent')
    # The caller is its parent and has never waited/reaped this child. Even an
    # exited leader remains a zombie, reserving its PID/PGID until final kill.
    os.killpg(leader['pid'], sig)


def _emit(value):
    print(json.dumps(value, sort_keys=True), flush=True)


def _worker(write_fd, stubborn, depth=0):
    signal.signal(signal.SIGTERM, signal.SIG_IGN if stubborn else signal.SIG_DFL)
    if depth == 0:
        os.setpgid(0, 0)
    if depth < 2:
        child = os.fork()
        if child == 0:
            _worker(write_fd, stubborn, depth + 1)
            os._exit(0)
    os.write(write_fd, (json.dumps(identity(os.getpid())) + '\n').encode())
    os.close(write_fd)
    # Independent, fixed lifetime limits leftovers after supervisor failure.
    # No allocations, evaluation, external command, or user-provided payload.
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        time.sleep(.02)
    os._exit(0)


def _supervisor(stubborn):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER; this child only.
        raise OSError(ctypes.get_errno(), 'subreaper unavailable')
    read_fd, write_fd = os.pipe()
    leader_pid = os.fork()
    if leader_pid == 0:
        os.close(read_fd)
        _worker(write_fd, stubborn)
        os._exit(0)
    os.close(write_fd)
    rows, pending = [], b''
    leader = None
    final_signal_sent = False
    try:
        deadline = time.monotonic() + 2
        while len(rows) < 3:
            left = deadline - time.monotonic()
            if left <= 0 or not select.select([read_fd], [], [], left)[0]:
                raise StopError('fixed tree readiness timeout')
            chunk = os.read(read_fd, 4096)
            if not chunk:
                raise StopError('incomplete fixed tree')
            pending += chunk
            while b'\n' in pending:
                line, pending = pending.split(b'\n', 1)
                rows.append(json.loads(line))
        leader = next(row for row in rows if row['pid'] == leader_pid)
        if len({r['pid'] for r in rows}) != 3 or any(
                r['pgid'] != leader_pid or r['sid'] != os.getpid() for r in rows):
            raise StopError('fixed tree ownership mismatch')
        _emit(dict(kind='ready', owner_pid=os.getpid(), members=rows))
        # EOF also stops the fixture if the controller exits without cleanup.
        readable = select.select([sys.stdin.fileno()], [], [], 5)[0]
        trigger = 'controller_eof' if readable else 'fixed_lease_expired'
        if readable and os.read(sys.stdin.fileno(), 1):
            trigger = 'unexpected_input'
        _signal_owned(leader, os.getpid(), signal.SIGTERM)
        time.sleep(.1)
        live = []
        for row in rows:
            try:
                current = identity(row['pid'])
            except FileNotFoundError:
                continue
            if current['start_ticks'] == row['start_ticks'] and current['state'] != 'Z':
                live.append(row['pid'])
        # Never reap the anchor before the last group signal.
        _signal_owned(leader, os.getpid(), signal.SIGKILL)
        final_signal_sent = True
        reaped = []
        deadline = time.monotonic() + 3
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                break
            if pid:
                reaped.append(dict(pid=pid, wait_status=status))
            elif time.monotonic() >= deadline:
                raise StopError('owned descendants not reaped before deadline')
            else:
                time.sleep(.01)
        if {r['pid'] for r in reaped} != {r['pid'] for r in rows}:
            raise StopError('reaped set does not match the fixed fixture')
        _emit(dict(kind='stopped', trigger=trigger, members=rows, reaped=reaped,
                   sigkill_required=bool(live), owned_tree_reaped=True,
                   formal_admission='BLOCKED', qualification_authorized=False,
                   target_execution_authorized=False))
    finally:
        os.close(read_fd)
        # On a failed handshake, the direct child is still an unreaped anchor.
        # Derive its identity rather than accepting any caller-supplied PID.
        if not final_signal_sent:
            try:
                if leader is None:
                    leader = identity(leader_pid)
                _signal_owned(leader, os.getpid(), signal.SIGKILL)
            except (FileNotFoundError, ProcessLookupError, StopError):
                pass  # Refused identity never permits a signal to another group.
        # Normal completion already reaped everything; failures are bounded by
        # the workers' eight-second lifetime, with no false success report.
        deadline = time.monotonic() + 9
        while time.monotonic() < deadline:
            try:
                pid, _ = os.waitpid(-1, os.WNOHANG)
            except ChildProcessError:
                break
            if not pid:
                time.sleep(.01)


class SyntheticOwnedTree:
    """One-shot fixture bound to a stop Event; no attach/resume/restart method."""
    def __init__(self, stop_event, *, synthetic_only=False, stubborn=True):
        if synthetic_only is not True or not isinstance(stop_event, threading.Event):
            raise ValueError('explicit synthetic_only=True and stop Event required')
        if type(stubborn) is not bool or stop_event.is_set():
            raise ValueError('invalid fixture mode or stop already requested')
        if sys.platform != 'linux':
            raise StopError('Linux /proc, fork, process groups and subreaper required')
        self._event = stop_event
        self._close = threading.Event()
        self._done = threading.Event()
        self._error = None
        self._report = None
        self._lock = threading.Lock()
        self._pending = b''
        self._process = subprocess.Popen(
            [sys.executable, '-I', '-B', str(Path(__file__).resolve()),
             '--fixed-synthetic-supervisor', 'stubborn' if stubborn else 'cooperative'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            bufsize=0, start_new_session=True)
        try:
            self.ready = self._receive(time.monotonic() + 4)
            if self.ready.get('kind') != 'ready' or self.ready['owner_pid'] != self._process.pid:
                raise StopError('supervisor handshake refused')
        except BaseException:
            self._process.stdin.close()
            try:
                self._process.wait(timeout=12)
            finally:
                self._process.stdout.close()
            raise
        self._thread = threading.Thread(target=self._run, name='p309-synthetic-owned-stop', daemon=True)
        self._thread.start()

    def _receive(self, deadline):
        while b'\n' not in self._pending:
            left = deadline - time.monotonic()
            if left <= 0 or not select.select([self._process.stdout], [], [], left)[0]:
                raise StopError('supervisor response timeout; termination unconfirmed')
            chunk = os.read(self._process.stdout.fileno(), 4096)
            if not chunk:
                raise StopError('supervisor EOF; termination unconfirmed')
            self._pending += chunk
            if len(self._pending) > 16384:
                raise StopError('supervisor response oversized')
        line, self._pending = self._pending.split(b'\n', 1)
        return json.loads(line)

    def _run(self):
        try:
            while not (self._event.is_set() or self._close.is_set()):
                if select.select([self._process.stdout], [], [], .01)[0]:
                    break  # Fixed lease expiry or supervisor failure.
            self._process.stdin.close()  # No dependency on session/monitor I/O locks.
            report = self._receive(time.monotonic() + 5)
            code = self._process.wait(timeout=3)
            if (code != 0 or report.get('kind') != 'stopped' or
                    report.get('members') != self.ready['members'] or
                    report.get('owned_tree_reaped') is not True or
                    {r['pid'] for r in report.get('reaped', [])} !=
                    {r['pid'] for r in self.ready['members']} or
                    report.get('formal_admission') != 'BLOCKED' or
                    report.get('qualification_authorized') is not False or
                    report.get('target_execution_authorized') is not False):
                raise StopError('invalid stop acknowledgement; termination unconfirmed')
            with self._lock:
                self._report = report
        except Exception as exc:
            with self._lock:
                self._error = str(exc)
        finally:
            self._process.stdin.close()
            self._process.stdout.close()
            try:
                self._process.wait(timeout=12)
            except subprocess.TimeoutExpired:
                with self._lock:
                    self._error = 'supervisor still running; termination unconfirmed'
            self._done.set()

    def wait_stopped(self, timeout=5):
        if not self._done.wait(timeout):
            raise StopError('stop acknowledgement pending; termination unconfirmed')
        with self._lock:
            if self._error:
                raise StopError(self._error)
            return json.loads(json.dumps(self._report))

    def close(self):
        self._close.set()
        return self.wait_stopped()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != '--fixed-synthetic-supervisor' or sys.argv[2] not in ('stubborn', 'cooperative'):
        raise SystemExit('Only the bounded synthetic fixture is supported')
    _supervisor(sys.argv[2] == 'stubborn')
