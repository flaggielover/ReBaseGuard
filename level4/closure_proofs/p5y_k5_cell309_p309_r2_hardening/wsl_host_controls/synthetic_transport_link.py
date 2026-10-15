"""Synthetic signing -> observation monitor adapter; never launches work.

The caller owns the existing signer, monitor/session and fixed fixture. A failed
or delayed signer automatically publishes stop without acquiring signer/session
locks or waiting for signer cleanup. No collector or production trust is added.
"""
import math
import threading
import time

import dev_session as D


class LinkError(RuntimeError):
    pass


class SyntheticObservationLink:
    def __init__(self, monitor, signer, *, synthetic_only=False, response_timeout=2):
        if synthetic_only is not True:
            raise ValueError('explicit synthetic_only=True required')
        if (type(response_timeout) not in (int, float) or
                not math.isfinite(response_timeout) or not .05 <= response_timeout <= 5):
            raise ValueError('synthetic response timeout must be 0.05..5 seconds')
        if not monitor.poll():
            raise LinkError('monitor already stopped')
        self.monitor, self.signer = monitor, signer
        self.response_timeout = response_timeout
        self._state = threading.Lock()
        self._operation = threading.Lock()
        self._idle = threading.Event()
        self._idle.set()
        self._reason = None
        self._closed = False
        self._job = None
        # This adapter explicitly enables the existing monitor watchdog.
        if not monitor.status()['watchdog_active']:
            monitor.start_watchdog(.01)

    def _stop(self, reason):
        with self._state:
            if self._reason is None:
                self._reason = reason
        self.monitor.bridge_failed()

    def _check(self):
        with self._state:
            if self._reason is not None or self._closed:
                raise LinkError(self._reason or 'link_closed')
        if not self.monitor.poll():
            raise LinkError('monitor_stopped')

    def observe(self, payload):
        """Sign a synthetic payload, then verify/diagnose its exact envelope.

        At most one signer request is ever outstanding. A timed-out worker cannot
        be cancelled safely: it is retained, late output is ignored, and reuse is
        refused permanently. close reports incomplete work rather than hiding it.
        """
        if not self._operation.acquire(blocking=False):
            self._stop('concurrent_observation_refused')
            raise LinkError('concurrent_observation_refused')
        self._idle.clear()
        try:
            self._check()
            if type(payload) is not dict:
                raise LinkError('synthetic payload must be an object')
            token = self.monitor.challenge()
            raw = D.canonical(dict(token, payload=payload))
            if len(raw) > D.MAX_MESSAGE:
                raise LinkError('synthetic payload exceeds message budget')
            job = dict(done=threading.Event(), result=None, error=None)
            def request():
                try:
                    job['result'] = self.signer.sign(raw)
                except Exception:
                    job['error'] = 'synthetic_signer_failed'
                finally:
                    job['done'].set()
            with self._state:
                if self._reason is not None or self._closed:
                    raise LinkError('link_stopped_before_signing')
                self._job = job
                thread = threading.Thread(target=request, name='p309-synthetic-link-sign', daemon=True)
                job['thread'] = thread
                deadline = time.monotonic() + self.response_timeout
                try:
                    thread.start()
                except Exception:
                    self._job = None
                    raise
            while not job['done'].wait(.01):
                self._check()
                if time.monotonic() >= deadline:
                    self._stop('synthetic_signer_timeout')
                    raise LinkError('synthetic_signer_timeout')
            self._check()
            # Completion observed after the budget cannot create a fresh window.
            if time.monotonic() >= deadline:
                self._stop('synthetic_signer_timeout')
                raise LinkError('synthetic_signer_timeout')
            if job['error'] is not None:
                self._stop(job['error'])
                raise LinkError(job['error'])
            result = self.monitor.accept(job['result'])
            self._check()
            return result
        except Exception as exc:
            self._stop('synthetic_observation_refused')
            if isinstance(exc, LinkError):
                raise
            raise LinkError('synthetic_observation_refused') from exc
        finally:
            self._idle.set()
            self._operation.release()

    def status(self):
        with self._state:
            job = self._job
            return dict(scope='SYNTHETIC_ONLY', reason=self._reason, closed=self._closed,
                        signer_pending=job is not None and job['thread'].is_alive(),
                        observation_pending=not self._idle.is_set(), formal_admission='BLOCKED',
                        qualification_authorized=False, target_execution_authorized=False)

    def close(self, timeout=2):
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout < 0:
            raise ValueError('cleanup timeout must be finite and nonnegative')
        with self._state:
            self._closed = True
        # Publish stop BEFORE any operation/worker wait. The caller can reap its
        # fixed tree even when a signer holds its own lock during blocked cleanup.
        self._stop('link_closed')
        deadline = time.monotonic() + timeout
        if not self._idle.wait(max(0, deadline - time.monotonic())):
            raise LinkError('observation still running; cleanup incomplete')
        with self._state:
            job = self._job
        if job is not None:
            job['thread'].join(max(0, deadline - time.monotonic()))
            if job['thread'].is_alive():
                raise LinkError('signer still running; cleanup incomplete')
        return self.status()
