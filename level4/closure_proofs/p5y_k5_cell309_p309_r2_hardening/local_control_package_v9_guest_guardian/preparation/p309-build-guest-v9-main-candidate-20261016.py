"""Compile frozen v3, then run only its bounded pure H4 parser assertions."""
import datetime, hashlib, json, os, pathlib, signal, subprocess, sys
S=pathlib.Path('/mnt/c/Users/Lenovo/Documents/Codex/2026-10-15/rebaseguard-309-windows-cpu-wsl2-ubuntu/outputs/p309-guest-guardian-v9-staging')
SRC=S/'candidate_v3_main'
OUT=pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-guest-v9-native-build-candidate-v3-20261016-01')
BUILD=pathlib.Path('/home/suzhe/p309/builds/guest-v9-native-build-candidate-v3-20261016-01')
HEADERS=pathlib.Path('/home/suzhe/p309/builds/guest-v9-build-inputs-20261016-01/include')
INPUTS=pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-guest-v9-build-inputs-20261016-01')
LIB=pathlib.Path('/usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0')
def sha(b): return hashlib.sha256(b).hexdigest()
def new(path,b):
    with path.open('xb') as f: f.write(b)
def js(path,obj): new(path,(json.dumps(obj,indent=2)+'\n').encode())
def call(name,argv,timeout=60):
    p=subprocess.Popen(argv,cwd=BUILD,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    timed=False; cleanup=[]
    try: so,se=p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed=True
        try: os.killpg(p.pid,signal.SIGKILL)
        except OSError as e: cleanup.append(repr(e))
        try: so,se=p.communicate(timeout=2)
        except subprocess.TimeoutExpired as e:
            so=e.output or b''; se=e.stderr or b''; cleanup.append('owned group cleanup not proven')
    new(OUT/(name+'.stdout.bin'),so); new(OUT/(name+'.stderr.bin'),se)
    r=dict(name=name,argv=argv,exit=p.poll(),timeout=timed,cleanup_errors=cleanup,
           stdout_sha256=sha(so),stderr_sha256=sha(se))
    js(OUT/(name+'.command.json'),r)
    return r
def main():
    if os.getuid()!=1000 or sys.version_info[:3]!=(3,11,15) or sha(pathlib.Path(sys.executable).read_bytes())!='b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194':
        raise RuntimeError('exact ordinary private Python required')
    raw=(S/'CANDIDATE_V3_SHA256.json').read_bytes()
    if sha(raw)!='9743b3eda934af27d5ff7efbbf811c4fb9b5fe0e02589ed678c714325a6e7e2c': raise RuntimeError('manifest drift')
    manifest=json.loads(raw)
    sources=[]
    for row in manifest['files']:
        name=row['path']
        if pathlib.PurePosixPath(name).name!=name or name in ('','.', '..'): raise RuntimeError('non-flat source')
        data=(SRC/name).read_bytes()
        if sha(data)!=row['sha256'] or len(data)!=row['bytes']: raise RuntimeError('source drift '+name)
        sources.append((name,data,row))
    hm=(INPUTS/'COMPLETE_HEADER_SET_ADDITION.json').read_bytes()
    for row in json.loads(hm)['headers']:
        if sha(pathlib.Path(row['file']).read_bytes())!=row['sha256']: raise RuntimeError('header drift')
    if sha(LIB.read_bytes())!='b10be60fc80ea6910df1b253658e638bd29f3d1aeeb3798006fc66972366cb94': raise RuntimeError('systemd drift')
    gcc=pathlib.Path('/usr/bin/gcc').resolve(strict=True)
    if sha(gcc.read_bytes())!='1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26': raise RuntimeError('gcc drift')
    OUT.mkdir(exist_ok=False); BUILD.mkdir(exist_ok=False)
    js(OUT/'STARTED.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(pathlib.Path(__file__).read_bytes()),scope='BUILD_AND_NEW_PURE_H4_PARSER_ONLY',admission='BLOCKED'))
    new(OUT/'CANDIDATE_V3_SHA256.json',raw)
    for name,data,_ in sources: new(BUILD/name,data)
    base=[str(gcc),'-std=c11','-O2','-Wall','-Wextra','-Wformat=2','-Werror','-pthread','-I'+str(HEADERS)]
    common=['manager_authority.c','anchor_crypto.c','anchor_transport.c']
    link=[str(LIB),'-lcrypto','-pthread','-Wl,-z,relro,-z,now']
    commands=[('guardian',base+['guardian_v9.c']+common+link+['-o','guardian-v9']),
       ('gate',base+['fixed_gate_v9.c']+common+link+['-o','fixed-gate-v9']),
       ('broker',base+['control_broker_v9.c','broker_link.c','h4_wire.c']+common+link+['-o','control-broker-v9']),
       ('idle',base+['idle_owned_v9.c','-o','idle-owned-v9']),
       ('admin-helper',base+['admin_helper_v9.c','-o','admin-helper-v9']),
       ('pure-h4-parser-build',base+['test_h4_wire.c','h4_wire.c','-o','test-h4-wire'])]
    results=[call(n,a) for n,a in commands]
    tests=[]
    if results[-1]['exit']==0: tests.append(call('pure-h4-parser-test',[str(BUILD/'test-h4-wire')],10))
    artifacts=[]; inspections=[]
    for name in ('guardian-v9','fixed-gate-v9','control-broker-v9','idle-owned-v9','admin-helper-v9','test-h4-wire'):
        path=BUILD/name
        if path.is_file():
            b=path.read_bytes(); artifacts.append(dict(path=str(path),bytes=len(b),sha256=sha(b)))
            inspections.append(call(name+'-readelf',['/usr/bin/readelf','--file-header','--dynamic','--version-info',str(path)],15))
    passed=all(x['exit']==0 and not x['timeout'] and not x['cleanup_errors'] for x in results+tests+inspections) and len(tests)==1
    result=dict(scope='ACTUAL_NATIVE_BUILD_AND_EIGHT_PURE_PARSER_ASSERTIONS_ONLY',source_manifest_sha256=sha(raw),sources=[r for _,_,r in sources],
        private_python_sha256=sha(pathlib.Path(sys.executable).read_bytes()),private_header_manifest_sha256=sha(hm),compiler=dict(path=str(gcc),sha256=sha(gcc.read_bytes())),
        library=dict(path=str(LIB),sha256=sha(LIB.read_bytes())),commands=results,parser_tests=tests,inspections=inspections,artifacts=artifacts,
        result='PASS' if passed else 'BUILD_OR_PARSER_FAILED_PRESERVED',production_binaries_invoked=0,services_started=0,keys_used=0,guest_boots=0,
        target_systemd_8_17_ABI_verified=False,I1_I7='OPEN',admission='BLOCKED')
    js(OUT/'ACTUAL_BUILD_RESULT.json',result)
    print(json.dumps(dict(result=result['result'],commands=[dict(name=r['name'],exit=r['exit']) for r in results],parser_tests=tests,artifacts=artifacts,admission='BLOCKED'),indent=2))
    return 0 if passed else 1
if __name__=='__main__': raise SystemExit(main())
