"""New entry failure paths only; fake Popen, self-owned temp files, no ETL access."""
import ast, hashlib, json, pathlib, subprocess, tempfile, unittest
from unittest.mock import patch
SOURCE=pathlib.Path(__file__).with_name('p309-run-saved-extended-reviewed-20261016.py')
EXPECTED='27e7e9604f57f31b74330308bb5d05ef9ff3df63d5fa0854a1c50829bf58060d'
DATA=SOURCE.read_bytes()
if hashlib.sha256(DATA).hexdigest()!=EXPECTED:raise RuntimeError('test source binding differs')
NS={'__name__':'entry_fault_tests_not_main','__file__':str(SOURCE),'__verified_caller_sha256__':EXPECTED}
exec(compile(DATA,str(SOURCE),'exec'),NS)

class FakeProcess:
    pid=424242
    def __init__(self,mode):self.mode=mode;self.returncode=None;self.kills=0;self.waits=[]
    def poll(self):return self.returncode
    def kill(self):
        self.kills+=1
        if self.mode in ('kill_error','kill_wait_error'):raise PermissionError('injected owned-handle kill failure')
    def wait(self,timeout):
        self.waits.append(timeout)
        if timeout==2:
            if self.mode=='kill_wait_error':raise subprocess.TimeoutExpired('fake-owned-decoder',2)
            self.returncode=-1;return self.returncode
        if self.mode in ('wait_error','kill_error','kill_wait_error'):raise OSError('injected wait failure')
        self.returncode=0;return 0

class EntryFaults(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='p309-v8-entry-unit-')
        self.out=pathlib.Path(self.temp.name);NS['OUT']=self.out
    def tearDown(self):self.temp.cleanup()
    def result(self):return json.loads((self.out/'PROCESS_RESULT.json').read_bytes())
    def run_fake(self,mode,record_fail=False):
        p=FakeProcess(mode);original=NS['record']
        def record(path,value):
            if record_fail and path.name=='OWNED_PROCESS_STARTED.json':raise OSError('injected started-record I/O failure')
            return original(path,value)
        with patch.object(NS['subprocess'],'Popen',return_value=p),patch.dict(NS,{'record':record}):
            if mode=='success' and not record_fail:r=NS['run_owned_decoder'](['FIXTURE_ONLY']);self.assertEqual(r['exit'],0)
            else:
                with self.assertRaises((OSError,PermissionError)):NS['run_owned_decoder'](['FIXTURE_ONLY'])
        return p
    def test_success_uses_no_kill(self):
        p=self.run_fake('success');self.assertEqual(p.kills,0);self.assertFalse(self.result()['cleanup_unknown'])
    def test_started_record_failure_stops_exact_owned_object(self):
        p=self.run_fake('success',True);self.assertEqual(p.kills,1);self.assertIn(2,p.waits);self.assertIn('started-record',self.result()['original_error'])
    def test_wait_failure_still_kills_once_and_records(self):
        p=self.run_fake('wait_error');self.assertEqual(p.kills,1);self.assertEqual(p.waits[-1],2);self.assertTrue(self.result()['exited'])
    def test_failed_kill_still_attempts_bounded_wait(self):
        p=self.run_fake('kill_error');r=self.result();self.assertEqual(p.kills,1);self.assertEqual(p.waits[-1],2);self.assertTrue(r['cleanup_unknown']);self.assertIn('PermissionError',r['kill_error'])
    def test_failed_kill_and_wait_preserve_unknown(self):
        p=self.run_fake('kill_wait_error');r=self.result();self.assertEqual(p.kills,1);self.assertFalse(r['exited']);self.assertIsNone(r['exit']);self.assertTrue(r['cleanup_unknown']);self.assertIn('TimeoutExpired',r['wait_error'])
    def test_stdout_close_failure_is_not_success(self):
        p=FakeProcess('success');original=pathlib.Path.open
        class BadClose:
            def __init__(self,file):self.file=file
            def __enter__(self):return self.file
            def __exit__(self,*args):self.file.close();raise OSError('injected stdout close failure')
        def opened(path,*args,**kwargs):
            f=original(path,*args,**kwargs)
            return BadClose(f) if path.name=='stdout.bin' else f
        with patch.object(NS['subprocess'],'Popen',return_value=p),patch.object(pathlib.Path,'open',opened):
            with self.assertRaises(OSError):NS['run_owned_decoder'](['FIXTURE_ONLY'])
        r=self.result();self.assertEqual(p.kills,0);self.assertIn('close failure',r['original_error']);self.assertEqual(r['exit'],0)
    def test_old_partial_attempt_directory_is_never_written(self):
        prior=self.out/'prior-partial';prior.mkdir();(prior/'unchanged.txt').write_bytes(b'keep-original')
        NS['OUT']=prior;NS['ATTEMPT_OWNED']=True
        before={p.name:p.read_bytes() for p in prior.iterdir()}
        main_guard=ast.parse(DATA).body[-1]
        self.assertIsInstance(main_guard,ast.If)
        with patch.dict(NS,{'__name__':'__main__'}):
            with self.assertRaises(FileExistsError):exec(compile(ast.Module(body=[main_guard],type_ignores=[]),str(SOURCE),'exec'),NS)
        self.assertFalse(NS['ATTEMPT_OWNED']);self.assertEqual(before,{p.name:p.read_bytes() for p in prior.iterdir()})

if __name__=='__main__':unittest.main(verbosity=2)
