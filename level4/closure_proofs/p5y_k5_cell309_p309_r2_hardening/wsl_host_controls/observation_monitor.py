"""Development-only diagnostic monitor and stop-event latch.

No launcher, sampling, process signalling or job execution is implemented. The
watchdog publishes a stop request independently of blocked signing/verification;
an operational controller that can stop its owned work is still required.
"""
import base64
import math
import threading
import time

import dev_session as D
import host_controls as H


class MonitorError(Exception):
    pass


class ObservationMonitor:
    def __init__(self, session, *, wall_clock=time.time, monotonic=time.monotonic):
        self.session = session
        self.wall_clock, self.monotonic = wall_clock, monotonic
        self._state_lock = threading.RLock()
        self._operation_lock = threading.Lock()
        self._shutdown = threading.Event()
        self.stop_requested = threading.Event()
        self._thread = None
        self._reason = None
        self._last_clock = None
        self._deadline = None
        self._count = 0
        self._baseline = D.strict_json(session.baseline_raw)
        self._previous = D.strict_json(session.baseline_raw)
        try:
            initial = H.assess(self._baseline['host'], self._baseline['guest'], now=self.wall_clock())
            if not initial['candidate_observations_pass']:
                self._stop('baseline_observations_refused')
            else:
                self._renew_deadline(self._baseline)
        except Exception:
            self._stop('baseline_or_clock_invalid')

    def _now(self):
        try:
            value = self.monotonic()
            valid = (type(value) in (float, int) and math.isfinite(value) and value >= 0
                     and (self._last_clock is None or value >= self._last_clock))
        except (OverflowError, TypeError):
            valid = False
        if not valid:
            raise MonitorError('invalid or regressing watchdog clock')
        self._last_clock = value
        return value

    def _stop(self, reason):
        # Deliberately no I/O or session lock: blocked verification/fsync must not
        # prevent this latch or the stop event reaching a controlling caller.
        with self._state_lock:
            if self._reason is None:
                self._reason = reason
                self.stop_requested.set()
                self._shutdown.set()

    def _renew_deadline(self, payload):
        with self._state_lock:
            if self._reason is not None:
                raise MonitorError(self._reason)
            now = self._now()
            wall = self.wall_clock()
            end = payload['host']['end']['wall_s']
            if not H.number(wall) or not H.number(end):
                raise MonitorError('invalid observation age')
            age = wall - end
            limit = H.THRESHOLDS['sample_s'] + H.THRESHOLDS['monitor_gap_tolerance_s']
            if not 0 <= age <= limit:
                raise MonitorError('observation expired before acknowledgment')
            # Time in transit/verification is not a fresh monitoring window.
            self._deadline = now + limit - age

    def poll(self):
        with self._state_lock:
            if self._reason is not None:
                return False
            if self.session.terminal:
                self._stop('session_terminated')
                return False
            try:
                if self._deadline is None or self._now() > self._deadline:
                    self._stop('observation_deadline_exceeded')
            except Exception:
                self._stop('watchdog_clock_invalid')
            return self._reason is None

    def bridge_failed(self):
        """A controlling transport reports EOF/timeout; no receipt can reset it."""
        self._stop('bridge_failed')

    def challenge(self):
        with self._operation_lock:
            if not self.poll():
                raise MonitorError(self._reason)
            try:
                token = self.session.challenge()
                if not self.poll():
                    raise MonitorError(self._reason)
                # Issuing challenges alone never refreshes liveness.
                return token
            except Exception as exc:
                self._stop('challenge_failed')
                raise MonitorError(self._reason) from exc

    def accept(self, envelope):
        with self._operation_lock:
            if not self.poll():
                raise MonitorError(self._reason)
            try:
                # Freeze caller-owned containers before verification and use the
                # very same bytes for diagnostics afterward.
                frozen = D.strict_json(D.canonical(envelope))
                acknowledgment = self.session.accept(frozen)
                if not self.poll():
                    raise MonitorError(self._reason)
                doc = D.strict_json(base64.b64decode(frozen['message_b64'], validate=True))
                payload = doc['payload']
                report = H.assess(payload['host'], payload['guest'], self._previous,
                                  now=self.wall_clock(), phase='monitor', baseline=self._baseline)
                if not report['candidate_observations_pass']:
                    self._stop('candidate_observations_refused')
                self.session.record_monitor_decision(report)
                if not self.poll():
                    raise MonitorError(self._reason)
                self._renew_deadline(payload)
                with self._state_lock:
                    if self._reason is not None:
                        raise MonitorError(self._reason)
                    self._previous = D.strict_json(D.canonical(payload))
                    self._count += 1
                return dict(sequence=acknowledgment['sequence'], diagnostic_continue=True,
                            scope='DEVELOPMENT_ONLY', formal_admission='BLOCKED',
                            qualification_authorized=False, target_execution_authorized=False)
            except Exception as exc:
                self._stop('signed_observation_or_persistence_failed')
                raise MonitorError(self._reason) from exc

    def start_watchdog(self, tick_seconds=0.25):
        if type(tick_seconds) not in (float, int) or not 0.01 <= tick_seconds <= 1:
            raise MonitorError('watchdog polling interval must be 0.01..1 seconds')
        with self._state_lock:
            if self._thread is not None or not self.poll():
                raise MonitorError('watchdog is already started or monitor is stopped')
            def watch():
                while not self._shutdown.wait(tick_seconds):
                    if not self.poll():
                        return
            self._thread = threading.Thread(target=watch, name='p309-development-watchdog', daemon=True)
            self._thread.start()

    def status(self):
        with self._state_lock:
            return dict(stop_requested=self._reason is not None, reason=self._reason,
                        watchdog_active=self._thread is not None and self._thread.is_alive(),
                        valid_observations=self._count, scope='DEVELOPMENT_ONLY',
                        formal_admission='BLOCKED', qualification_authorized=False,
                        target_execution_authorized=False)

    def close(self):
        self._stop('closed_by_caller')
        if self._thread is not None:
            self._thread.join(timeout=2)
            if self._thread.is_alive():
                raise MonitorError('watchdog did not stop')
        # Operations must have returned before cleanup; the caller must bound
        # its transport. close does not attempt unsafe thread cancellation.
        with self._operation_lock:
            self.session.close()
