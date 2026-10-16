"""Compile the exact v9 library candidate as an ordinary Ubuntu user; never run it."""
import datetime, hashlib, json, os, pathlib, subprocess, sys
SRC = pathlib.Path('/mnt/c/Users/Lenovo/Documents/Codex/2026-10-15/rebaseguard-309-windows-cpu-wsl2-ubuntu/outputs/p309-guest-guardian-v9-staging/candidate_v2_library')
OUT = pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-guest-v9-native-build-candidate-v2-20261016-01')
BUILD = pathlib.Path('/home/suzhe/p309/builds/guest-v9-native-build-candidate-v2-20261016-01')
HEADERS = pathlib.Path('/home/suzhe/p309/builds/guest-v9-build-inputs-20261016-01/include')
INPUTS = pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-guest-v9-build-inputs-20261016-01')
LIB = pathlib.Path('/usr/lib/x86_64-linux-gnu/libsystemd.so.0.38.0')
def sha(b): return hashlib.sha256(b).hexdigest()
def new_json(path, obj):
    with path.open('x',encoding='utf-8') as f:
        json.dump(obj,f,indent=2); f.write('\n')
def main():
    if os.getuid()!=1000 or sys.version_info[:3]!=(3,11,15) or sha(pathlib.Path(sys.executable).read_bytes())!='b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194':
        raise RuntimeError('ordinary user and exact private interpreter required')
    raw=(SRC/'CANDIDATE_V2_SHA256.json').read_bytes()
    if sha(raw)!='bc967ab14ee13b57f956218bd07defee898e2305ddb18fe7b6363fa59eb74aa3':
        raise RuntimeError('candidate manifest changed')
    manifest=json.loads(raw)
    OUT.mkdir(exist_ok=False); BUILD.mkdir(exist_ok=False)
    (OUT/'CANDIDATE_V2_SHA256.json').write_bytes(raw)
    new_json(OUT/'STARTED.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256=sha(pathlib.Path(__file__).read_bytes()),scope='COMPILE_ONLY_NO_NATIVE_EXECUTION',admission='BLOCKED'))
    inputs=[]
    for row in manifest['files']:
        name=row['path']
        if pathlib.PurePosixPath(name).name!=name or name in ('','.', '..'):
            raise RuntimeError('non-flat candidate path')
        data=(SRC/name).read_bytes()
        if len(data)!=row['bytes'] or sha(data)!=row['sha256']:
            raise RuntimeError('candidate source differs: '+name)
        with (BUILD/name).open('xb') as f: f.write(data)
        inputs.append(row)
    header_manifest=json.loads((INPUTS/'COMPLETE_HEADER_SET_ADDITION.json').read_bytes())
    for row in header_manifest['headers']:
        if sha(pathlib.Path(row['file']).read_bytes())!=row['sha256']:
            raise RuntimeError('private header drift')
    if sha(LIB.read_bytes())!='b10be60fc80ea6910df1b253658e638bd29f3d1aeeb3798006fc66972366cb94':
        raise RuntimeError('runtime libsystemd drift')
    gcc=pathlib.Path('/usr/bin/gcc').resolve(strict=True)
    if sha(gcc.read_bytes())!='1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26':
        raise RuntimeError('compiler drift')
    base=[str(gcc),'-std=c11','-O2','-Wall','-Wextra','-Wformat=2',
          '-Werror=implicit-function-declaration','-Werror=return-type','-I'+str(HEADERS)]
    common=['manager_authority.c','anchor_crypto.c','anchor_transport.c']
    link=[str(LIB),'-lcrypto','-pthread','-Wl,-z,relro,-z,now']
    commands=[('guardian',base+['guardian_v9.c']+common+link+['-o','guardian-v9']),
              ('gate',base+['fixed_gate_v9.c']+common+link+['-o','fixed-gate-v9']),
              ('idle',base+['idle_owned_v9.c','-o','idle-owned-v9']),
              ('control-library',base+['-fPIC','-shared','broker_link.c']+common+link+['-Wl,--no-undefined','-o','libp309-control-v9.so'])]
    results=[]
    for name,argv in commands:
        try:
            p=subprocess.run(argv,cwd=BUILD,stdin=subprocess.DEVNULL,capture_output=True,timeout=60,check=False)
            rc=p.returncode; so=p.stdout; se=p.stderr; error=None
        except subprocess.TimeoutExpired as exc:
            rc=None; so=exc.stdout or b''; se=exc.stderr or b''; error='owned compiler killed and waited by subprocess.run timeout'
        (OUT/(name+'.stdout.bin')).write_bytes(so); (OUT/(name+'.stderr.bin')).write_bytes(se)
        result=dict(name=name,argv=argv,exit=rc,error=error,stdout_sha256=sha(so),stderr_sha256=sha(se))
        new_json(OUT/(name+'.command.json'),result); results.append(result)
    artifacts=[]
    for name in ('guardian-v9','fixed-gate-v9','idle-owned-v9','libp309-control-v9.so'):
        p=BUILD/name
        if p.is_file():
            b=p.read_bytes(); artifacts.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
            inspect=subprocess.run(['/usr/bin/readelf','--file-header','--dynamic',str(p)],stdin=subprocess.DEVNULL,capture_output=True,timeout=15,check=False)
            (OUT/(name+'.readelf.txt')).write_bytes(inspect.stdout+inspect.stderr)
    result=dict(scope='ACTUAL_NATIVE_COMPILATION_ONLY_NO_NATIVE_EXECUTION',
        source_inputs=inputs,private_header_manifest_sha256=sha((INPUTS/'COMPLETE_HEADER_SET_ADDITION.json').read_bytes()),
        compiler=dict(path=str(gcc),sha256=sha(gcc.read_bytes())),library=dict(path=str(LIB),sha256=sha(LIB.read_bytes())),
        commands=results,artifacts=artifacts,result='PASS' if all(r['exit']==0 for r in results) else 'BUILD_FAILED_PRESERVED',
        tests_run=0,native_trials=0,services_started=0,software_installed=0,keys_used=0,
        guest_boots=0,I1_I7='OPEN',admission='BLOCKED')
    new_json(OUT/'ACTUAL_BUILD_RESULT.json',result)
    print(json.dumps(dict(result=result['result'],commands=[dict(name=r['name'],exit=r['exit']) for r in results],artifacts=artifacts,admission='BLOCKED'),indent=2))
    return 0 if result['result']=='PASS' else 1
if __name__=='__main__':
    raise SystemExit(main())
