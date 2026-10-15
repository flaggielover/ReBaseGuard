"""Read-only inventory of the existing preparation runtime; not enrollment."""
import datetime, hashlib, json, os, pathlib, stat, sys
root = pathlib.Path('/home/suzhe/p309/runtime/cpython-3.11.15')
rows, errors = [], []
def identity(s):
    return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
for parent, dirs, files in os.walk(root, followlinks=False):
    for name in sorted(dirs + files):
        p = pathlib.Path(parent)/name
        try:
            before = p.lstat()
            row = dict(path=str(p.relative_to(root)),uid=before.st_uid,gid=before.st_gid,
                       mode=oct(stat.S_IMODE(before.st_mode)),size=before.st_size)
            if stat.S_ISLNK(before.st_mode):
                row.update(kind='symlink',target=os.readlink(p))
            elif stat.S_ISDIR(before.st_mode):
                row['kind']='directory'
            elif stat.S_ISREG(before.st_mode):
                fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
                with os.fdopen(fd,'rb') as f:
                    opened=os.fstat(f.fileno())
                    if identity(opened)!=identity(before):
                        raise RuntimeError('file changed before open')
                    h=hashlib.sha256()
                    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
                    if identity(os.fstat(f.fileno()))!=identity(opened):
                        raise RuntimeError('file changed during read')
                row.update(kind='file',sha256=h.hexdigest(),hardlinks=before.st_nlink)
            else:
                raise RuntimeError('unexpected nonregular entry')
            if identity(p.lstat())!=identity(before):raise RuntimeError('entry changed during inventory')
            rows.append(row)
        except (OSError,RuntimeError) as e:
            errors.append(dict(path=str(p.relative_to(root)),error_type=type(e).__name__,message=str(e)))
parents=[]
for p in [root,*root.parents]:
    s=p.lstat();parents.append(dict(path=str(p),uid=s.st_uid,gid=s.st_gid,mode=oct(stat.S_IMODE(s.st_mode))))
body=json.dumps(sorted(rows,key=lambda x:x['path']),sort_keys=True,separators=(',',':')).encode()
print(json.dumps(dict(schema='P309_EXISTING_PREPARATION_RUNTIME_INVENTORY/1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(root),
    entries=rows,errors=errors,parents=parents,entry_count=len(rows),manifest_sha256=hashlib.sha256(body).hexdigest(),
    provenance_scope='Existing development installation only; NO new build or admission pin',
    immutable_security_snapshot=False,external_system_dependencies_complete=False,
    limitations=['Read is not atomic across entire tree; a trusted offline snapshot is required for final enrollment.',
                 'Leaf O_NOFOLLOW/inode checks do not establish trusted parent directories or prevent adversarial ancestor replacement.',
                 'External dynamic libraries, kernel, distro image, toolchain and future lazy loading are not bounded by this prefix manifest.',
                 'UID1000 owns this runtime; it is not the root-owned future protected runtime.'],
    formal_admission='BLOCKED'),indent=2))
