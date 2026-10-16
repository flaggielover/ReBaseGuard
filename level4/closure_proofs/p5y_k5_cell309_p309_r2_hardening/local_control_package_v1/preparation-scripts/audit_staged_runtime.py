import hashlib, json, os, pathlib, re, subprocess, sys
BASE=pathlib.Path('/home/suzhe/p309/builds/guest-runtime-stage-stable-20261016')
PREFIX=BASE/'stage/opt/rebaseguard-p309/cpython-3.11.15'
RECORD=pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01/runtime-inventory-v2')
RECORD.mkdir()
def digest(p):
    with open(p,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,obj):
    with open(RECORD/name,'x') as f: json.dump(obj,f,indent=2); f.write('\n')
files=[]; elf=[]; symlinks=[]; directories=[]
for root,dirs,names in os.walk(PREFIX,followlinks=False):
    for name in dirs+names:
        p=pathlib.Path(root)/name;st=p.lstat();rel=str(p.relative_to(PREFIX))
        if p.is_symlink():
            target=p.resolve(strict=True)
            if not target.is_relative_to(PREFIX): raise RuntimeError('escaping prefix link: '+str(p))
            symlinks.append(dict(path=rel,target=os.readlink(p)))
        elif p.is_dir(): directories.append(dict(path=rel,mode=oct(st.st_mode & 0o7777),uid=st.st_uid,gid=st.st_gid))
        elif p.is_file():
            files.append(dict(path=rel,size=st.st_size,sha256=digest(p),mode=oct(st.st_mode & 0o7777)))
            with p.open('rb') as f:
                header=f.read(20)
                if header[:4]==b'\x7fELF':
                    if header[4:6]!=b'\x02\x01': raise RuntimeError('unexpected ELF ABI')
                    elf_type=int.from_bytes(header[16:18],'little')
                    # ET_REL (python.o in the development config) has no runtime
                    # dependency resolution. Keep it in the complete file pin.
                    if elf_type in (2,3): elf.append(p)
                    elif elf_type!=1: raise RuntimeError('unexpected ELF type')
        else: raise RuntimeError('unexpected prefix object '+str(p))
save('prefix-manifest.json',dict(scope='UNPRIVILEGED_STAGE_NOT_DEPLOYED',root=str(PREFIX),files=files,links=symlinks,directories=directories))
dependencies={};ldd=[]
for p in elf:
    out=subprocess.run(['/usr/bin/ldd',str(p)],capture_output=True,text=True,timeout=10,check=True)
    if 'not found' in out.stdout: raise RuntimeError('missing ELF dependency '+str(p))
    ldd.append(dict(path=str(p.relative_to(PREFIX)),stdout=out.stdout,stderr=out.stderr))
    for dep in re.findall(r'(?:=>\s+)?(/[^\s()]+)',out.stdout):
        q=pathlib.Path(dep); resolved=q.resolve(strict=True)
        if str(resolved) not in dependencies:
            owner=subprocess.run(['/usr/bin/dpkg-query','-S',str(q)],capture_output=True,text=True,timeout=10)
            if owner.returncode:
                owner=subprocess.run(['/usr/bin/dpkg-query','-S',str(resolved)],capture_output=True,text=True,timeout=10)
            dependencies[str(resolved)]=dict(loader_path=str(q),sha256=digest(resolved),size=resolved.stat().st_size,
                dpkg_query_exit=owner.returncode,dpkg_owner=owner.stdout.strip(),dpkg_error=owner.stderr.strip())
save('elf-dependencies.json',dict(elf_count=len(elf),ldd=ldd,dependencies=dependencies,
    limit='Build-host resolver facts only. Guest package presence, actual mappings and protected ancestors still require real guest validation.'))
old=pathlib.Path('/home/suzhe/p309/runtime/cpython-3.11.15/bin/python3.11')
oldhash=digest(old)
assert oldhash=='b21d680e5061c20ee39c75f0c6edf8db4220f327de45e52ab2040e15ca0cf194'
save('summary.json',dict(scope='STAGE_INVENTORY_NOT_GUEST_ACCEPTANCE',files=len(files),elf_files=len(elf),dependency_files=len(dependencies),
    original_private_interpreter_sha256=oldhash,stage_interpreter_sha256=digest(PREFIX/'bin/python3.11'),
    archive_sha256=digest(BASE/'cpython-3.11.15-guest-stage.tar.gz'),formal_admission='BLOCKED'))
print((RECORD/'summary.json').read_text())
