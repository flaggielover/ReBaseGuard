"""Independent synthetic witnesses; no collection, launch or project evaluator."""
import copy
import datetime as dt
import unittest
import host_controls as H
from test_host_controls import fixture


def monitor(duration):
    host, guest = fixture()
    previous = {'host': copy.deepcopy(host), 'guest': copy.deepcopy(guest)}
    previous['host']['end'].update(wall_s=999, uptime_s=499, active_s=494)
    baseline = copy.deepcopy(previous)
    baseline['host']['start'].update(wall_s=939, uptime_s=439, active_s=434)
    host['end'].update(wall_s=1000 + duration, uptime_s=500 + duration, active_s=495 + duration)
    host['process_observation']['cpu_elapsed_lower_bound_s'] = 60.0
    guest['utc'] = dt.datetime.fromtimestamp(1000 + duration, dt.timezone.utc).isoformat()
    return H.assess(host, guest, previous, now=1000 + duration, phase='monitor', baseline=baseline)


class ReviewRegressions(unittest.TestCase):
    def test_five_minute_monitor_sample_is_refused(self):
        result = monitor(300)
        self.assertFalse(result['candidate_observations_pass'])
        self.assertFalse(result['checks']['sample_continuity'])
        self.assertEqual(result['formal_admission'], 'BLOCKED')

    def test_monitor_gap_boundary_is_inclusive(self):
        self.assertTrue(monitor(105)['candidate_observations_pass'])
        over = monitor(105.001)
        self.assertFalse(over['candidate_observations_pass'])
        self.assertFalse(over['checks']['sample_continuity'])

    def test_normal_sixty_second_monitor_sample_still_passes_diagnostics(self):
        result = monitor(60)
        self.assertTrue(result['candidate_observations_pass'])
        self.assertFalse(result['qualification_authorized'])
        self.assertFalse(result['target_execution_authorized'])


if __name__ == '__main__':
    unittest.main()
