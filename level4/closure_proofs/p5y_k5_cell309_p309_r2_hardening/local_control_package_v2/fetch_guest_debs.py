import datetime,hashlib,json,pathlib,re,subprocess,urllib.request,shutil
r=pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01')
out=r/'guest-offline-debs';out.mkdir()
lists=pathlib.Path('/var/lib/apt/lists')
sha=lambda b:hashlib.sha256(b).hexdigest()
plan=(r/'guest-dependency-plan/apt-simulation.stdout.txt').read_text()
wanted={}
for line in plan.splitlines():
    m=re.match(r'Inst (\S+)(?: \[[^]]+\])? \((\S+)',line)
    if m:wanted[m[1]]=m[2]
assert len(wanted)==19,(len(wanted),wanted)
key=pathlib.Path('/usr/share/keyrings/ubuntu-archive-keyring.gpg')
(out/key.name).write_bytes(key.read_bytes())
found={};releases=[];indexes=[]
for release in sorted(lists.glob('*InRelease')):
    if not release.name.startswith(('archive.ubuntu.com_ubuntu_dists_','security.ubuntu.com_ubuntu_dists_')):continue
    signed=out/release.name;signed.write_bytes(release.read_bytes())
    payload=out/(release.name+'.verified')
    command=['gpgv','--status-fd','1','--keyring',str(out/key.name),'--output',str(payload),str(signed)]
    p=subprocess.run(command,capture_output=True,timeout=30)
    (out/(release.name+'.gpgv.stdout')).write_bytes(p.stdout)
    (out/(release.name+'.gpgv.stderr')).write_bytes(p.stderr)
    if p.returncode:raise RuntimeError('Release signature rejected '+release.name)
    text=payload.read_text();pins={};in_sha=False
    for line in text.splitlines():
        if line=='SHA256:':in_sha=True;continue
        if in_sha and not line.startswith(' '):break
        if in_sha:
            digest,size,path=line.split();pins[path]=(digest,int(size))
    valid_until=re.search(r'^Valid-Until: (.+)$',text,re.M)
    if valid_until:
        from email.utils import parsedate_to_datetime
        if parsedate_to_datetime(valid_until[1])<datetime.datetime.now(datetime.timezone.utc):raise RuntimeError('Expired signed index')
    rel={'file':signed.name,'sha256':sha(signed.read_bytes()),'command':command,'gpgv_exit':p.returncode,'valid_until':valid_until[1] if valid_until else None}
    releases.append(rel)
    prefix=release.name[:-len('InRelease')]
    for component in ['main','universe']:
        path=lists/(prefix+component+'_binary-amd64_Packages')
        if not path.exists():continue
        data=path.read_bytes();pin=pins[component+'/binary-amd64/Packages']
        if (sha(data),len(data))!=pin:raise RuntimeError('Local Packages not bound to signed release '+path.name)
        selected=[]
        for para in data.decode().split('\n\n'):
            lines=para.splitlines();fields={}
            for line in lines:
                if line and not line[0].isspace() and ': ' in line:
                    k,v=line.split(': ',1);fields[k]=v
            name=fields.get('Package')
            if name in wanted and fields.get('Version')==wanted[name] and fields.get('Architecture') in ('amd64','all'):
                record={k:fields[k] for k in ('Package','Version','Architecture','Filename','Size','SHA256')}
                record['index']=path.name;record['index_sha256']=pin[0];record['release']=signed.name
                record['url']='https://'+('security.ubuntu.com' if release.name.startswith('security.') else 'archive.ubuntu.com')+'/ubuntu/'+fields['Filename']
                if name in found and found[name]['SHA256']!=record['SHA256']:raise RuntimeError('Same-version package hash ambiguity')
                found[name]=record;selected.append(para)
        if selected:
            # Exact full index preserves the signature -> index -> stanza chain.
            (out/path.name).write_bytes(data)
            indexes.append({'file':path.name,'sha256':pin[0],'size':pin[1],'release':signed.name})
if set(found)!=set(wanted):raise RuntimeError('Missing signed exact versions '+repr(set(wanted)-set(found)))
for name,record in sorted(found.items()):
    dest=out/pathlib.PurePosixPath(record['Filename']).name
    req=urllib.request.Request(record['url'],headers={'User-Agent':'P309-source-preparation/1'})
    with urllib.request.urlopen(req,timeout=60) as response:
        if urllib.parse.urlparse(response.geturl()).hostname not in ('archive.ubuntu.com','security.ubuntu.com'):raise RuntimeError('Unapproved redirect')
        with dest.open('xb') as file:shutil.copyfileobj(response,file)
    if dest.stat().st_size!=int(record['Size']) or sha(dest.read_bytes())!=record['SHA256']:raise RuntimeError('Downloaded deb digest differs '+name)
    record['local_file']=dest.name
    print(name,record['Version'],record['SHA256'],flush=True)
result={'scope':'OFFLINE_INPUTS_ONLY_NO_INSTALL_NO_GUEST_BOOT','trust_root':'Existing Ubuntu archive keyring (OS trust root), copied and hash recorded',
 'keyring_sha256':sha(key.read_bytes()),'releases':releases,'indexes':indexes,'packages':list(found.values()),
 'limits':['APT plan uses manifest-derived synthetic installed state, not actual guest dpkg metadata.',
 'sysvinit-utils is proposed as same-version reinstall; do NOT install automatically. Full actual guest dependency resolution required.',
 'Downloaded package files do not prove interpreter linkage or runtime provenance inside the unbooted guest.'],
 'package_installations':0,'guest_boots':0,'admission':'BLOCKED'}
(out/'VERIFIED_INPUTS.json').write_text(json.dumps(result,indent=2)+'\n')
print('VERIFIED_PACKAGE_COUNT',len(found),flush=True)
