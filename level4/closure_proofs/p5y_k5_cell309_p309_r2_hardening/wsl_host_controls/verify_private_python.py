"""Bounded stdlib / multiprocessing smoke; never imports project runtime code."""
import ast
import datetime
import hashlib
import importlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import sys

EXPECTED = '3.11.15'
MODULES = ['ssl','_ssl','_hashlib','hashlib','zlib','bz2','_bz2','lzma','_lzma',
 'sqlite3','_sqlite3','ctypes','_ctypes','multiprocessing','_multiprocessing',
 'multiprocessing.shared_memory','_posixshmem','concurrent.futures','decimal','fractions',
 'json','pickle','queue','resource','signal','fcntl','select','socket','urllib.request',
 'venv','ensurepip','readline','curses','dbm.gnu','dbm.ndbm','tkinter','uuid','_uuid']


def echo_child(connection):
    try:
        connection.send({'value': 7 * 7, 'version': platform.python_version()})
    finally:
        connection.close()


def verify():
    if platform.python_implementation() != 'CPython' or platform.python_version() != EXPECTED:
        raise RuntimeError('Exact CPython 3.11.15 is required; no version substitution')
    exe = Path(sys.executable).resolve()
    if str(exe) != '/home/suzhe/p309/runtime/cpython-3.11.15/bin/python3.11':
        raise RuntimeError('Not the intended private interpreter')
    report = {'schema':'P309_PRIVATE_RUNTIME_PREPARATION/1','scope':'DEVELOPMENT_ONLY',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'version':platform.python_version(),
        'implementation':platform.python_implementation(),'installation_path':sys.prefix,
        'executable':str(exe),'interpreter_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),
        'glibc':os.confstr('CS_GNU_LIBC_VERSION'), 'modules':{},'multiprocessing':{},
        'system_python_path':str(Path('/usr/bin/python3').resolve()),
        'system_python_sha256':hashlib.sha256(Path('/usr/bin/python3.12').read_bytes()).hexdigest()}
    # Static inventory only, never import P309 launchers/drivers/guards/evaluators.
    code = Path(__file__).resolve().parents[2]/'p5y_k5_cell309_p309_r2/code'
    required=set(MODULES)
    for path in code.glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            names = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else (
                [node.module.split('.')[0]] if isinstance(node, ast.ImportFrom) and node.module else [])
            required.update(n for n in names if n in sys.stdlib_module_names)
    for name in sorted(required):
        try:
            importlib.import_module(name)
            report['modules'][name]='PASS'
        except Exception as exc:
            report['modules'][name]=type(exc).__name__+': '+str(exc)
    import bz2, lzma, zlib, ssl, sqlite3, ctypes
    sample=b'p309-private-runtime-synthetic-check'*8
    assert all(m.decompress(m.compress(sample)) == sample for m in (bz2,lzma,zlib))
    assert hashlib.sha256(b'abc').hexdigest() == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    ssl.create_default_context()
    ctypes.CDLL(None)
    with sqlite3.connect(':memory:') as db:
        assert db.execute('select 1 + 1').fetchone() == (2,)
    report['openssl']=ssl.OPENSSL_VERSION
    report['compression_hash_ssl_sqlite_ctypes']='PASS'
    for method in ('fork','spawn','forkserver'):
        if method not in mp.get_all_start_methods():
            report['multiprocessing'][method]='UNAVAILABLE'
            continue
        ctx=mp.get_context(method)
        recv,send=ctx.Pipe(duplex=False)
        p=ctx.Process(target=echo_child,args=(send,))
        try:
            p.start();send.close()
            if not recv.poll(10): raise RuntimeError('child response timeout')
            result=recv.recv();p.join(10)
            if p.exitcode != 0 or result != {'value':49,'version':EXPECTED}:
                raise RuntimeError('child result/exit mismatch')
            lock=ctx.Lock()
            with lock: pass
            report['multiprocessing'][method]='PASS'
        except Exception as exc:
            report['multiprocessing'][method]=type(exc).__name__+': '+str(exc)
        finally:
            if p.pid and p.is_alive(): p.terminate();p.join(5)
            recv.close();send.close()
            if p.pid and not p.is_alive(): p.close()
    from multiprocessing import shared_memory
    shm=shared_memory.SharedMemory(create=True,size=8)
    try:
        shm.buf[:4]=b'P309'
        assert bytes(shm.buf[:4]) == b'P309'
        report['shared_memory']='PASS'
    finally:
        shm.close();shm.unlink()
    report['passed']=all(v=='PASS' for v in report['modules'].values()) and all(
        v=='PASS' for v in report['multiprocessing'].values())
    report.update(formal_admission='BLOCKED',qualification_authorized=False,target_execution_authorized=False)
    return report


if __name__=='__main__':
    result=verify()
    print(json.dumps(result,indent=2))
    sys.exit(0 if result['passed'] else 1)
