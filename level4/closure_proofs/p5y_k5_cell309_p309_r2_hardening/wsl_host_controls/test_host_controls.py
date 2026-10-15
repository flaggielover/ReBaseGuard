"""Synthetic diagnostics only: no project entrypoint, host monitor or evaluator."""
import ast
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import unittest
import host_controls as H


def fixture():
    start = dict(wall_s=1000.0, uptime_s=500.0, active_s=495.0,
                 host_id_sha256='a'*64, boot_id_sha256='b'*64)
    end = dict(start, wall_s=1060.0, uptime_s=560.0, active_s=555.0)
    host = dict(schema=H.SCHEMA, start=start, end=end,
        process_observation=dict(coverage='ATTESTED_COMPLETE', protected_process_coverage=True,
            process_lifetime_events_complete=True, unreadable_count=0, disappeared_count=0,
            observed_count=1, cpu_elapsed_lower_bound_s=60.0,
            rows=[dict(pid=10, creation_sha256='c'*64, cpu_fraction=0.01)]),
        policy=dict(pending_reboot=False, power_query_ok=True, sleep_ac_s=0, sleep_dc_s=0,
            hibernate_ac_s=0, hibernate_dc_s=0, update_policy_known=True,
            scheduled_tasks_query_ok=True, maintenance_window_approved=True, event_query_ok=True,
            event_window_covers_sample=True, events_since_start=[], event_log_cleared=False,
            policy_sha256='e'*64),
        resources=dict(available_memory_bytes=8_000_000_000, backing_free_bytes=40_000_000_000))
    guest = dict(schema='P309_WSL_CONTROL_FACTS/1',
        utc=dt.datetime.fromtimestamp(1060, dt.timezone.utc).isoformat(),
        available_memory_bytes=8_000_000_000, guest_disk_free_bytes=40_000_000_000,
        affinity_cpus=4, effective_cpu_quota=4, pid1='systemd', systemd_state='running',
        python_version='3.11.15', python_implementation='CPython', private_runtime=True,
        interpreter_sha256='d'*64, glibc='glibc 2.39',
        boot_id_sha256='f'*64, machine_id_sha256='a'*64)
    return host, guest


class Controls(unittest.TestCase):
    def result(self, host=None, guest=None, **kw):
        h, g = fixture()
        return H.assess(h if host is None else host, g if guest is None else guest, now=1060, **kw)

    def test_synthetic_good_never_authorizes(self):
        result = self.result()
        self.assertTrue(result['candidate_observations_pass'])
        self.assertEqual(result['formal_admission'], 'BLOCKED')
        for k in ('qualification_authorized', 'target_execution_authorized', 'route_accepted'):
            self.assertIs(result[k], False)
        self.assertEqual(len(result['proposed_aws_replacements']), 5)

    def test_invalid_top_level_and_nested_inputs_fail_closed(self):
        for value in (None, [], 'bad', True, 1, {}):
            with self.subTest(value=value):
                self.assertFalse(H.assess(value, value, now=1060)['candidate_observations_pass'])
        for key in ('start', 'end', 'resources', 'policy', 'process_observation'):
            for bad in (None, [], True, 'bad'):
                h, g = fixture(); h[key] = bad
                with self.subTest(key=key, bad=bad):
                    self.assertFalse(H.assess(h, g, now=1060)['candidate_observations_pass'])

    def test_nonfinite_negative_bool_numbers_rejected(self):
        for bad in (None, True, '8e9', -1, float('nan'), float('inf'), 10**400):
            for field in ('available_memory_bytes', 'guest_disk_free_bytes', 'effective_cpu_quota', 'affinity_cpus'):
                h, g = fixture(); g[field] = bad
                with self.subTest(field=field, bad=bad):
                    self.assertFalse(H.assess(h, g, now=1060)['candidate_observations_pass'])
            h, g = fixture(); h['process_observation']['rows'][0]['cpu_fraction'] = bad
            self.assertFalse(H.assess(h, g, now=1060)['checks']['process_rows_valid'])

    def test_resource_boundaries_and_host_minimum(self):
        for section, key, value in (('host','available_memory_bytes',7_999_999_999),
            ('host','backing_free_bytes',39_999_999_999), ('guest','available_memory_bytes',7_999_999_999),
            ('guest','guest_disk_free_bytes',39_999_999_999), ('guest','effective_cpu_quota',3.99)):
            h, g = fixture()
            (h['resources'] if section == 'host' else g)[key] = value
            self.assertFalse(H.assess(h,g,now=1060)['candidate_observations_pass'])

    def test_start_identity_is_required(self):
        for field in ('boot_id_sha256', 'machine_id_sha256'):
            h,g=fixture();g[field]=None
            self.assertFalse(H.assess(h,g,now=1060)['checks']['guest_identity_valid'])
        h,g=fixture();h['policy']['policy_sha256']=None
        self.assertFalse(H.assess(h,g,now=1060)['checks']['policy_identity_valid'])

    def test_cpu_fraction_not_divided_by_host_cpu_count(self):
        h, g = fixture()
        h['process_observation']['rows'][0]['cpu_fraction'] = 0.05
        self.assertTrue(H.assess(h,g,now=1060)['checks']['individual_cpu_quiet'])
        h['process_observation']['rows'][0]['cpu_fraction'] = 0.050001
        self.assertFalse(H.assess(h,g,now=1060)['checks']['individual_cpu_quiet'])
        h['process_observation']['rows'][0]['cpu_fraction'] = 0.5
        self.assertTrue(H.assess(h,g,now=1060,phase='monitor')['checks']['individual_cpu_quiet'])
        h['process_observation']['rows'][0]['cpu_fraction'] = 0.500001
        self.assertFalse(H.assess(h,g,now=1060,phase='monitor')['checks']['individual_cpu_quiet'])

    def test_sampling_window_cannot_be_inflated_by_query_latency(self):
        for bad in (None, True, 59.99, 60.01, float('nan')):
            h,g=fixture();h['process_observation']['cpu_elapsed_lower_bound_s']=bad
            self.assertFalse(H.assess(h,g,now=1060)['checks']['full_sample_duration'])

    def test_aggregate_and_duplicate_pid(self):
        h,g=fixture()
        h['process_observation']['rows']=[dict(pid=i,creation_sha256='c'*64,cpu_fraction=.34) for i in (1,2,3)]
        h['process_observation']['observed_count']=3
        self.assertFalse(H.assess(h,g,now=1060,phase='monitor')['checks']['aggregate_cpu_quiet'])
        h['process_observation']['rows'][1]['pid']=1
        self.assertFalse(H.assess(h,g,now=1060)['checks']['process_rows_valid'])

    def test_visibility_unknown_churn_or_truncation_refused(self):
        for key,value in (('coverage','BEST_EFFORT'),('protected_process_coverage',False),
            ('process_lifetime_events_complete',False),('unreadable_count',1),('disappeared_count',1),
            ('observed_count',0),('observed_count',True)):
            h,g=fixture();h['process_observation'][key]=value
            self.assertFalse(H.assess(h,g,now=1060)['checks']['visibility_complete'])
        for rows in ([],None,[None],[dict(pid=10,creation_sha256=None,cpu_fraction=0.0)]):
            h,g=fixture();h['process_observation']['rows']=rows
            self.assertFalse(H.assess(h,g,now=1060)['checks']['process_rows_valid'])

    def test_stale_future_naive_guest_timestamp(self):
        for now in (1059,1166,True,float('nan')):
            h,g=fixture();self.assertFalse(H.assess(h,g,now=now)['checks']['freshness'])
        for value in ('not a date','1970-01-01T00:17:40',None):
            h,g=fixture();g['utc']=value
            self.assertFalse(H.assess(h,g,now=1060)['checks']['freshness'])

    def test_reboot_suspend_time_regression_and_short_sample(self):
        for key,value in (('boot_id_sha256','e'*64),('host_id_sha256','e'*64),('active_s',549.9),
            ('wall_s',1066),('uptime_s',499),('active_s',494),('active_s',600)):
            h,g=fixture();h['end'][key]=value
            self.assertFalse(H.assess(h,g,now=1060)['checks']['sample_continuity'])
        h,g=fixture();h['end'].update(wall_s=1059,uptime_s=559,active_s=554)
        self.assertFalse(H.assess(h,g,now=1060)['checks']['full_sample_duration'])

    def test_policy_unknown_not_equivalent_to_false(self):
        for key,value in (('pending_reboot',None),('pending_reboot',True),('sleep_ac_s',1),
            ('sleep_dc_s',True),('hibernate_dc_s',3600),('update_policy_known',False),
            ('scheduled_tasks_query_ok',False),('maintenance_window_approved',False),
            ('event_query_ok',False),('event_window_covers_sample',False),
            ('events_since_start',[{'event_id':42}]),('event_log_cleared',True)):
            h,g=fixture();h['policy'][key]=value
            self.assertFalse(H.assess(h,g,now=1060)['candidate_observations_pass'])

    def test_private_runtime_exact_version(self):
        for key,value in (('python_version','3.11.14'),('python_version','3.12.3'),
            ('python_implementation','PyPy'),('private_runtime',False),('interpreter_sha256',''),('glibc',None)):
            h,g=fixture();g[key]=value
            self.assertFalse(H.assess(h,g,now=1060)['checks']['private_runtime'])

    def test_monitor_prior_checkpoint_is_required(self):
        self.assertFalse(self.result(phase='monitor')['checks']['prior_checkpoint_continuity'])
        h,g=fixture(); old=copy.deepcopy(h)
        old['end'].update(wall_s=999,uptime_s=499,active_s=494)
        previous={'host':old,'guest':copy.deepcopy(g)}
        baseline=copy.deepcopy(previous)
        baseline['host']['start'].update(wall_s=939,uptime_s=439,active_s=434)
        self.assertTrue(H.assess(h,g,previous,now=1060,phase='monitor',baseline=baseline)['candidate_observations_pass'])
        for key in ('boot_id_sha256','machine_id_sha256','interpreter_sha256','glibc'):
            altered=copy.deepcopy(previous);altered['guest'][key]='changed'
            self.assertFalse(H.assess(h,g,altered,now=1060,phase='monitor')['checks']['same_guest_runtime'])
        previous['host']['end'].update(wall_s=894,uptime_s=394,active_s=389)
        self.assertFalse(H.assess(h,g,previous,now=1060,phase='monitor')['checks']['prior_checkpoint_continuity'])

    def test_cumulative_suspend_against_baseline(self):
        h,g=fixture();base=copy.deepcopy(h)
        base['start'].update(wall_s=900,uptime_s=400,active_s=400)
        h['start']['active_s']=494;h['end']['active_s']=554
        result=H.assess(h,g,now=1060,phase='monitor',baseline={'host':base,'guest':g})
        self.assertTrue(result['checks']['sample_continuity'])
        self.assertFalse(result['checks']['baseline_continuity'])

    def test_thresholds_match_untouched_r2(self):
        path=Path(__file__).resolve().parents[2]/'p5y_k5_cell309_p309_r2/code/p309_host.py'
        tree=ast.parse(path.read_text())
        defaults=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
                      and any(isinstance(t,ast.Name) and t.id=='DEFAULTS' for t in n.targets))
        for k,v in H.THRESHOLDS.items(): self.assertEqual(v,defaults[k],k)

    def test_protected_sources_unchanged(self):
        root=Path(__file__).resolve().parents[2]
        manifest=json.loads(Path(__file__).with_name('protected_sources.json').read_text())
        for relative,expected in manifest.items():
            data=(root/relative).read_bytes().replace(b'\r\n',b'\n')
            self.assertEqual(hashlib.sha256(data).hexdigest(),expected,relative)

    def test_candidate_has_no_execution_imports(self):
        tree=ast.parse(Path(H.__file__).read_text())
        imports=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
            if isinstance(n,ast.ImportFrom):imports.append(n.module)
        self.assertEqual(set(imports),{'argparse','datetime','json','math','re','time'})


if __name__=='__main__': unittest.main(verbosity=2)
