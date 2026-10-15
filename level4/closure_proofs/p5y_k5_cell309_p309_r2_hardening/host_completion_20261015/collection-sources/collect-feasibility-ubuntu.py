import configparser, datetime, hashlib, json, os, pathlib, pwd, re, shutil, stat, subprocess, sys
out=[]
home=pathlib.Path.home()
def redact(s):
    return s.replace(str(home),'$CURRENT_LINUX_HOME')
def record(id, query, fn, limitation):
    r={'id':id,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query':query,'scope':'READ_ONLY_FEASIBILITY','limitation':limitation}
    try: r.update(status='OBSERVED',query_exit=0,result=fn())
    except OSError as e: r.update(status='UNKNOWN_OR_DENIED',query_exit=1,error={'type':type(e).__name__,'errno':e.errno,'message':redact(str(e))})
    except Exception as e: r.update(status='UNKNOWN',query_exit=1,error={'type':type(e).__name__,'message':redact(str(e))})
    out.append(r)
def cmd(args):
    t=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=12,env={**os.environ,'LC_ALL':'C','SYSTEMD_PAGER':'cat','SYSTEMD_COLORS':'0'})
        return {'utc':t,'argv':args,'exit':p.returncode,'stdout':redact(p.stdout),'stderr':redact(p.stderr)}
    except subprocess.TimeoutExpired: return {'utc':t,'argv':args,'exit':None,'status':'TIMEOUT_12S'}
def meta(p):
    p=pathlib.Path(p)
    try:
        s=p.lstat()
        return {'path':redact(str(p)),'exists':True,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'type':'symlink' if p.is_symlink() else 'directory' if p.is_dir() else 'file','current_euid_readable':os.access(p,os.R_OK,effective_ids=True),'current_euid_writable':os.access(p,os.W_OK,effective_ids=True),'current_euid_searchable_or_executable':os.access(p,os.X_OK,effective_ids=True)}
    except OSError as e: return {'path':redact(str(p)),'exists':False if e.errno==2 else None,'error_type':type(e).__name__,'errno':e.errno}
def identity():
    candidates=[{'name_sha256':hashlib.sha256(x.pw_name.encode()).hexdigest(),'uid':x.pw_uid,'gid':x.pw_gid} for x in pwd.getpwall() if re.search(r'p309|rebaseguard',x.pw_name,re.I)]
    paths=[home/'p309',home/'p309/runtime',home/'p309/runtime/cpython-3.11.15',home/'p309/runtime/cpython-3.11.15/bin/python3.11',home/'p309/workspace',home/'p309/scratch',pathlib.Path('/mnt/d/ReBaseGuard-309/workspace'),pathlib.Path('/mnt/d/ReBaseGuard-309/workspace/p309-admission-feasibility-20261015')]
    return {'uid':os.getuid(),'euid':os.geteuid(),'gid':os.getgid(),'egid':os.getegid(),'supplementary_group_ids':os.getgroups(),'current_account_name_sha256':hashlib.sha256(pwd.getpwuid(os.geteuid()).pw_name.encode()).hexdigest(),'named_p309_account_candidates':candidates,'dedicated_account_status':'NOT_FOUND_BY_NAME' if not candidates else 'CANDIDATES_REQUIRE_ROLE_CONFIRMATION','metadata':[meta(p) for p in paths],'dedicated_account_write_access':'NOT_ESTABLISHED','P309_SCRATCH_ROOT_is_set':bool(os.environ.get('P309_SCRATCH_ROOT')),'scratch_paths':'Conventional P309 path inspected; no official configured scratch binding established. No directory created.'}
record('ubuntu_identity_and_paths','Python os.getuid/geteuid/getgid/getegid/getgroups; pwd.getpwall filtered p309|rebaseguard (names hashed); lstat/os.access only enumerated P309 paths',identity,'Name-based inventory does not identify a differently named dedicated account. Writability is current EUID access metadata, no write probe; ACL/mount effects and distinct principal isolation remain unestablished. No foreign checkout inspected.')
def cgroups():
    cg=pathlib.Path('/proc/self/cgroup').read_text()
    rel=next((line.split(':',2)[2] for line in cg.splitlines() if line.startswith('0::')),None)
    result={'pid1_comm':pathlib.Path('/proc/1/comm').read_text().strip(),'process_cgroup':cg,'availability':{n:shutil.which(n) for n in ['systemctl','systemd-run']},'systemd_version':cmd(['systemctl','--version']),'affinity_cpu_count':len(os.sched_getaffinity(0)),'ancestor_metadata':[]}
    quotas=[]
    if rel is not None:
        base=pathlib.Path('/sys/fs/cgroup'); cur=base/rel.lstrip('/')
        if '..' in cur.parts: result['hierarchy_status']='UNKNOWN_PATH_OUTSIDE_VISIBLE_ROOT'; return result
        while True:
            node=meta(cur); node['controller_files']={}
            for name in ['cgroup.type','cgroup.controllers','cgroup.subtree_control','cpu.max','cpuset.cpus.effective','cpuset.mems.effective']:
                p=cur/name
                try:
                    text=p.read_text().strip(); node['controller_files'][name]={'value':text,'metadata':meta(p)}
                    if name=='cpu.max' and text.split()[0]!='max':
                        a,b=map(int,text.split()); quotas.append(a/b)
                except OSError as e: node['controller_files'][name]={'errno':e.errno,'error_type':type(e).__name__}
            result['ancestor_metadata'].append(node)
            if cur==base: break
            cur=cur.parent
        result['visible_min_finite_cpu_quota']=min(quotas) if quotas else None
        result['effective_cpu_upper_bound_current_process']=min([len(os.sched_getaffinity(0))]+quotas)
    result['existing_p309_units']=cmd(['systemctl','list-units','--all','--no-legend','--plain','--no-pager','p309-r2-*'])
    result['p309_unit_files']=cmd(['systemctl','list-unit-files','--no-legend','--no-pager','p309-r2-*'])
    names=[]
    if result['existing_p309_units'].get('exit')==0:
        names=[s.split()[0] for s in result['existing_p309_units']['stdout'].splitlines() if s.startswith('p309-r2-')]
    result['existing_unit_properties']=[]
    for name in names[:20]:
        result['existing_unit_properties'].append(cmd(['systemctl','show',name,'--no-pager','--property=Id,LoadState,ActiveState,ControlGroup,Delegate,CPUQuotaPerSecUSec,CPUQuotaPeriodUSec,MemoryMax,TasksMax,KillMode,SendSIGKILL,TimeoutStopUSec']))
    result['actual_execution_unit_effective_limits_and_containment']='NOT_ESTABLISHED'
    result['delegation_authority']='Visible controller ownership/mode only; no privileged action attempted.'
    return result
record('systemd_cgroup_metadata','Read /proc/1/comm and /proc/self/cgroup; sched_getaffinity; named cgroup ancestor control metadata; systemctl --version/list-units/list-unit-files p309-r2-*; show only existing matches',cgroups,'Query-process quota/affinity is not dedicated host capacity or a future execution-unit limit. No unit created/started/stopped/reset/attached; no cpu.stat sampling.')
def policies():
    results=[]
    for d in ['/etc/polkit-1/rules.d','/usr/share/polkit-1/rules.d','/etc/polkit-1/localauthority/50-local.d','/etc/sudoers.d']:
        r={'directory':d,'matches':[]}
        try:
            for p in pathlib.Path(d).iterdir():
                if re.search(r'p309|rebaseguard',p.name,re.I):
                    m=meta(p)
                    if p.is_file() and not p.is_symlink():
                        try: m['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
                        except OSError as e: m['hash_error']={'type':type(e).__name__,'errno':e.errno}
                    r['matches'].append(m)
            r['status']='MATCHES_FOUND' if r['matches'] else 'NOT_FOUND_BY_FILENAME'
        except OSError as e: r.update(status='DENIED' if e.errno==13 else 'NOT_FOUND' if e.errno==2 else 'UNKNOWN',errno=e.errno)
        results.append(r)
    return {'inventories':results,'exact_P309_policy':'UNKNOWN','sudo_invoked':False,'unrelated_rule_contents_read':False}
record('p309_policy_metadata','List direct filenames only in /etc/polkit-1/rules.d, /usr/share/polkit-1/rules.d, /etc/polkit-1/localauthority/50-local.d, /etc/sudoers.d; lstat/hash only p309|rebaseguard named files',policies,'Unreadable directories and unmatched generic rule names leave P309 authority UNKNOWN. No sudo invocation, generic rule dump or privilege evaluation.')
def integration():
    p=pathlib.Path('/etc/wsl.conf'); r={}
    if p.exists():
        cp=configparser.ConfigParser(interpolation=None); cp.read(p)
        allowed={'boot':['systemd'],'interop':['enabled','appendWindowsPath'],'automount':['enabled','mountFsTab'],'network':['generateHosts','generateResolvConf']}
        r['wsl_conf']={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'selected_settings':{s:{k:cp.get(s,k) for k in keys if cp.has_option(s,k)} for s,keys in allowed.items()},'default_user_matches_current':cp.get('user','default',fallback=None)==pwd.getpwuid(os.geteuid()).pw_name,'other_values_exported':False}
    else: r['wsl_conf']={'status':'NOT_FOUND'}
    p=pathlib.Path('/proc/sys/fs/binfmt_misc/WSLInterop')
    try: r['wsl_interop_binfmt']=p.read_text()
    except OSError as e: r['wsl_interop_binfmt']={'errno':e.errno,'error_type':type(e).__name__}
    r['local_endpoint_names']='NOT_SPECIFIED_IN_PACKET; no arbitrary /run or other-user data scanned'
    r['client_host_isolation']='NOT_ESTABLISHED'
    return r
record('ubuntu_integration', 'Read allowed nonidentity /etc/wsl.conf settings; /proc/sys/fs/binfmt_misc/WSLInterop metadata; no endpoint connections',integration,'WSL integration availability does not establish a separate Windows token, authenticated endpoint or key/anchor protection.')
record('clock_observation','timedatectl show --property=NTPSynchronized,NTP,CanNTP,Timezone,LocalRTC',lambda:cmd(['timedatectl','show','--property=NTPSynchronized,NTP,CanNTP,Timezone,LocalRTC']),'Point-in-time systemd state only; not independent time accuracy verification, NTP enablement, continuity or a reserved window.')
pathlib.Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'queries_recorded':len(out),'tests_run':0,'host_safety_samples':0}))
