"""Single fixed saved-file decode, not live collection or P309 execution.
The caller must verify and compile the exact bytes of this file before dispatch.
"""
import ctypes, datetime, hashlib, json, pathlib, subprocess, sys, time
ROOT = pathlib.Path(r'C:\Users\Lenovo\Documents\Codex\2026-10-15\rebaseguard-309-windows-cpu-wsl2-ubuntu')
STAGE = ROOT/'outputs/p309-saved-extended-v8-staging'
BUILD = STAGE/'build-ordinary-04'
OUT = pathlib.Path(r'D:\ReBaseGuard-309\records\p309-saved-extended-v8-20261016-01')
PIN_SOURCE = pathlib.Path(r'D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v7_interval_partition\driver\run_verified_partition.py')
PINS = {
    STAGE/'SavedExtendedData.cpp': 'e493c3dc93ff99c948ac344bd8326129ef5b9648cdb11078398a96fb9e7c81cf',
    STAGE/'SOURCE_BINDINGS.json': 'ef1fc6d61c24dbc1db3752eebbf2b4d40b7d830ef89286e6967438dbde62277d',
    BUILD/'SavedExtendedData.cpp': 'e493c3dc93ff99c948ac344bd8326129ef5b9648cdb11078398a96fb9e7c81cf',
    BUILD/'SavedExtendedData.exe': 'a9a8f84d64051d11743f9c7d4a0cdbb56b21eb6b599026d50cd7ade91f3e903d',
    BUILD/'BUILD_RESULT.json': 'ddfad5408bf374e09b72cf373d39e22ef8fd9957ad0a10a1eb6334bb2d394890',
    PIN_SOURCE: '85e9300a2864f83503035f223d7d264190e44f40eca7e9a25920338629dc80b0',
}
ATTEMPT = 'readonly-20261016-01'
ATTEMPT_OWNED = False
def sha(b): return hashlib.sha256(b).hexdigest()
def fresh(path, data):
    with path.open('xb') as f: f.write(data); f.flush()
def record(path, value):
    fresh(path, (json.dumps(value, indent=2, allow_nan=False)+'\n').encode('utf-8'))
def strict(data):
    def pairs(items):
        d={}
        for k,v in items:
            if k in d: raise ValueError('duplicate JSON field')
            d[k]=v
        return d
    return json.loads(data.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))

def run_owned_decoder(argv):
    started=time.monotonic(); p=None; original=None
    result=dict(launch_attempted=False,launched=False,pid=None,exit=None,exited=False,
                timed_out=False,kill_requested=False,kill_error=None,wait_error=None,
                poll_error=None,original_error=None,cleanup_unknown=True,admission='BLOCKED')
    try:
        with (OUT/'stdout.bin').open('xb') as stdout,(OUT/'stderr.bin').open('xb') as stderr:
            result['launch_attempted']=True
            p=subprocess.Popen(argv,cwd=BUILD,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                env={'SystemRoot':r'C:\Windows','WINDIR':r'C:\Windows','PATH':r'C:\Windows\System32',
                     'TEMP':str(OUT),'TMP':str(OUT)},creationflags=0x08000000,close_fds=True)
            result.update(launched=True,pid=p.pid)
            record(OUT/'OWNED_PROCESS_STARTED.json',dict(pid=p.pid,
                identity_authority='this exact successful Popen process handle; PID is diagnostic only',
                argv=argv,source_sha256=globals()['__verified_caller_sha256__']))
            while True:
                remaining=180-(time.monotonic()-started)
                if remaining<=0:
                    result['timed_out']=True
                    raise RuntimeError('saved decoder exceeded fixed 180 second wait budget')
                try: p.wait(timeout=min(20,remaining)); break
                except subprocess.TimeoutExpired: continue
    except BaseException as exc:
        original=exc;result['original_error']=repr(exc)
    finally:
        # This covers started-record I/O, wait, kill and output close failures.
        # At most one kill request, always followed by a bounded wait attempt,
        # even if kill fails. Never reopen/adopt a diagnostic PID.
        if p is not None:
            try: already_exited=p.poll() is not None
            except BaseException as exc:
                already_exited=False;result['poll_error']=repr(exc)
            if not already_exited:
                result['kill_requested']=True
                try: p.kill()
                except BaseException as exc: result['kill_error']=repr(exc)
                try: p.wait(timeout=2)
                except BaseException as exc: result['wait_error']=repr(exc)
            result.update(exit=p.returncode,exited=p.returncode is not None)
        else:
            # No successful Popen means no owned child to terminate.
            result['exited']=True
        result['cleanup_unknown']=(not result['exited'] or any(result[k] is not None
            for k in ('poll_error','kill_error','wait_error')))
        result['elapsed_seconds']=time.monotonic()-started
        # A write error here propagates to outer FAILED/UNKNOWN. It cannot
        # produce an ACTUAL_RESULT_PUBLIC or a successful wrapper completion.
        record(OUT/'PROCESS_RESULT.json',result)
    if original is not None: raise original
    if not result['launched'] or result['exit']!=0 or result['timed_out'] or result['cleanup_unknown']:
        raise RuntimeError('saved decoder failed/UNKNOWN; preserve output; no automatic retry')
    return result

def main():
    global ATTEMPT_OWNED
    ATTEMPT_OWNED=False
    if sys.platform!='win32' or sys.flags.optimize or not sys.flags.isolated:
        raise RuntimeError('isolated unoptimized Windows offline driver required')
    executed_digest=globals().get('__verified_caller_sha256__')
    if not isinstance(executed_digest,str) or len(executed_digest)!=64:
        raise RuntimeError('verified same-byte bootstrap entry required')
    OUT.mkdir(exist_ok=False)
    ATTEMPT_OWNED=True
    record(OUT/'ATTEMPT_STARTED.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='FIXED_SAVED_ETL_EXTENSION_AGGREGATION_NO_HOST_COLLECTION',
        auto_retry=False, admission='BLOCKED'))
    # Bootstrap the previously reviewed pin implementation from verified bytes,
    # never import it through a mutable source path/module search.
    pin_bytes=PIN_SOURCE.read_bytes()
    if sha(pin_bytes)!=PINS[PIN_SOURCE]: raise RuntimeError('pin helper differs')
    ns={'__name__':'bound_v7_pin_helper_not_main','__file__':str(PIN_SOURCE)}
    exec(compile(pin_bytes,str(PIN_SOURCE),'exec'),ns)
    Base=ns['PinnedInputs']
    class DispatchPins(Base):
        def __enter__(self):
            directories={parent for path in self.files for parent in path.parents}
            ordered=[(p,True) for p in sorted(directories,key=lambda p:(len(p.parts),str(p).lower()))]
            ordered += [(p,False) for p in sorted(set(self.files),key=lambda p:str(p).lower())]
            try:
                for path,directory in ordered:
                    # Ancestors deny deletion/rename; permit legitimate child namespace
                    # operations. Leaf inputs deny ordinary Win32 data-write/delete shares.
                    h=self.api.CreateFileW(str(path),0x80000000,3 if directory else 1,None,3,0x02200000,None)
                    if h==ctypes.c_void_p(-1).value: raise ctypes.WinError(ctypes.get_last_error())
                    self.handles.append(h); info=self.info_type()
                    if not self.api.GetFileInformationByHandle(h,ctypes.byref(info)): raise ctypes.WinError(ctypes.get_last_error())
                    if info.attributes&0x400 or bool(info.attributes&0x10)!=directory: raise ValueError('reparse/type refused')
                    self.identities.append(dict(path=str(path),directory=directory,volume_serial=info.volume,file_index=(info.index_high<<32)|info.index_low))
                return self
            except BaseException:
                self.__exit__(None,None,None); raise
    source=pathlib.Path(__file__)
    with DispatchPins(list(PINS)+[source]) as pins:
        snapshots={path:pins.small_bytes(path) for path in PINS}
        for path,digest in PINS.items():
            if sha(snapshots[path])!=digest: raise RuntimeError('fixed input changed: '+path.name)
        source_bytes=pins.small_bytes(source)
        if sha(source_bytes)!=executed_digest: raise RuntimeError('caller path bytes differ from compiled bytes')
        fresh(OUT/'CALLER_AS_EXECUTED.py',source_bytes)
        record(OUT/'INPUT_BINDINGS.json',dict(files=[dict(path=str(p),sha256=PINS[p],bytes=len(snapshots[p])) for p in PINS],
            caller_sha256=sha(source_bytes),identity_pins=pins.identities,
            ancestor_sharing='READ_AND_WRITE_BUT_NO_DELETE',leaf_sharing='READ_ONLY',
            limits='ordinary sharing pins; not protection against administrator/kernel or all metadata changes'))
        argv=[str(BUILD/'SavedExtendedData.exe'),'--scan-saved',ATTEMPT]
        record(OUT/'INVOCATION.json',dict(argv=argv,cwd=str(BUILD),timeout_seconds=180,owned_kill_wait_seconds=2,
            python=sys.version,python_sha256=sha(pathlib.Path(sys.executable).read_bytes()),
            wrapper_binding='caller verifies and compiles same bytes; helpers compiled from pinned snapshots',admission='BLOCKED'))
        result=run_owned_decoder(argv);elapsed=result['elapsed_seconds']
        for path,digest in PINS.items():
            if sha(pins.small_bytes(path))!=digest: raise RuntimeError('post-dispatch source/binary drift')
        scan=BUILD/('scan-'+ATTEMPT)
        raw={name:(scan/name).read_bytes() for name in ('STARTED.txt','aggregate.json','completion.json')}
        for name,data in raw.items(): fresh(OUT/name,data)
        agg=strict(raw['aggregate.json']); done=strict(raw['completion.json'])
        stdout=(OUT/'stdout.bin').read_bytes(); final=strict(stdout)
        if (done.get('schema')!='P309_SAVED_EXTENDED_V8_COMPLETION' or done.get('version')!=1 or
            done.get('complete') is not True or done.get('scan_complete') is not True or
            done.get('aggregate_sha256')!=sha(raw['aggregate.json']) or done.get('aggregate_bytes')!=len(raw['aggregate.json']) or
            done.get('aggregate_written_bytes')!=len(raw['aggregate.json']) or
            any(done.get(k)!=0 for k in ('aggregate_write_error','aggregate_flush_error','aggregate_close_error')) or
            final.get('result')!='COMPLETE' or final.get('exit_code')!=0 or final.get('aggregate_io_ok') is not True or
            any(final.get(k)!=0 for k in ('completion_write_error','completion_flush_error','completion_close_error','output_directory_close_error')) or
            agg.get('schema')!='P309_SAVED_EXTENDED_V8' or agg.get('version')!=1 or agg['status'].get('scan_complete') is not True):
            raise RuntimeError('native/receipt/aggregate completion or digest mismatch')
        totals={name:sum(row[name] for row in agg['events']) for name in (
            'events','declared_items','inspected_items','no_extended_items','malformed_events',
            'psk_absent','psk_candidate','psk_unknown_duplicate','psk_unknown_malformed','psk_unknown_uninspectable')}
        if totals['events']!=agg['counts']['event_callbacks']: raise RuntimeError('aggregate event conservation mismatch')
        public=dict(scope='ACTUAL_FIXED_SAVED_ETL_EXTENSION_AGGREGATION_ONLY',result='COMPLETE',
            source_sha256=PINS[STAGE/'SavedExtendedData.cpp'],binary_sha256=PINS[BUILD/'SavedExtendedData.exe'],
            caller_sha256=sha(source_bytes),input_sha256=agg['expected_input_sha256'],input_bytes=agg['expected_input_bytes'],
            aggregate_sha256=sha(raw['aggregate.json']),aggregate_bytes=len(raw['aggregate.json']),
            elapsed_seconds=elapsed,status=agg['status'],counts=agg['counts'],totals=totals,loss=agg['loss'],
            event_groups=agg['events'],psk_semantics=agg['psk_semantics'],
            capture_coverage_complete=False,cpu_attribution_changed=False,new_live_trace=0,new_host_samples=0,
            uac=0,vm=0,install=0,I1_I7='OPEN',admission='BLOCKED')
    # Completion is published only after every retained dispatch pin closed
    # successfully. Native completion alone cannot certify this outer call.
    record(OUT/'ACTUAL_RESULT_PUBLIC.json',public)
    record(OUT/'WRAPPER_COMPLETION.json',dict(result='COMPLETE',source_and_binary_posthashes_match=True,
        dispatch_pin_closes_succeeded=True,aggregate_sha256=sha(raw['aggregate.json']),
        valid_only_with_zero_wrapper_exit=True,admission='BLOCKED'))
    print(json.dumps(dict(result='COMPLETE',counts=agg['counts'],totals=totals,admission='BLOCKED'),indent=2))
    return 0
if __name__=='__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        if ATTEMPT_OWNED and not (OUT/'WRAPPER_COMPLETION.json').exists():
            record(OUT/'WRAPPER_COMPLETION.json',dict(result='FAILED_OR_UNKNOWN',error=repr(exc),
                automatic_retry=False,admission='BLOCKED'))
        raise
