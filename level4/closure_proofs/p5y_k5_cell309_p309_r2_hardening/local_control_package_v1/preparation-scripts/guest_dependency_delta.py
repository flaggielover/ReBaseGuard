import json,pathlib,re
r=pathlib.Path('/mnt/d/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01')
inv=json.loads((r/'runtime-inventory-v2/elf-dependencies.json').read_text())
image={a.split(':')[0]:b for a,b in (line.split('\t') for line in (r/'guest-inputs/ubuntu-24.04-minimal-cloudimg-amd64.manifest').read_text().splitlines())}
build={parts[0]:parts[1] for parts in (line.split('\t') for line in (r/'runtime-stage-stable/build-host-packages-after.tsv').read_text().splitlines())}
rows=[];diversions=[]
for path,dep in inv['dependencies'].items():
    if dep['dpkg_query_exit']:
        rows.append(dict(path=path,status='PACKAGE_OWNER_UNRESOLVED',error=dep['dpkg_error']));continue
    for owner in dep['dpkg_owner'].splitlines():
        if owner.startswith('diversion by '):
            diversions.append(dict(path=path,dpkg_fact=owner));continue
        pkg=owner.split(': ',1)[0]; name=pkg.split(':',1)[0]
        if not re.fullmatch(r'[a-z0-9][a-z0-9+.-]*(?::[a-z0-9-]+)?',pkg):
            raise ValueError('unrecognized package owner: '+owner)
        rows.append(dict(path=path,package=pkg,build_host_version=build.get(name),
            signed_image_manifest_version=image.get(name),status='PRESENT_IN_SIGNED_MANIFEST_NOT_GUEST_VERIFIED' if name in image else 'ABSENT_FROM_SIGNED_MANIFEST'))
with (r/'runtime-inventory-v2/guest-package-delta-final.json').open('x') as f:
    json.dump(dict(scope='STATIC_MANIFEST_COMPARISON_NOT_GUEST_INSPECTION',dependencies=rows,diversions=diversions,
        supersedes_invalid=['guest-package-delta.json: reserved PowerShell Host variable caused incomplete output',
            'guest-package-delta-corrected.json: dpkg diversion metadata incorrectly classified as packages; now separate'],formal_admission='BLOCKED'),f,indent=2);f.write('\n')
print(json.dumps([x for x in rows if x['status']!='PRESENT_IN_SIGNED_MANIFEST_NOT_GUEST_VERIFIED'],indent=2))
