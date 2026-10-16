# Ordinary-owner packaging of already built, digest-bound artifacts. No native entry execution.
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.ToString() -notlike '5.1.*'){throw 'Windows PowerShell 5.1 required'}
$private='C:\Users\Lenovo\P309-InstallationFacts-build-20261016-v3'
$sourceCommit='28fd11c9c8398f5fbd85d4836970918a6ad5c711'
$payload=@(
 @{file='NativeEntry.exe';source='D:\ReBaseGuard-309\records\p309-post-root-continuation-20261016-v1\p309-readiness-repair-staging-v3\production-build-stage\NativeEntry.exe';sha256='469efadffe76e5a66bd6997cb215042f74f0030c3ced819e1c1e4c2eccc65816'},
 @{file='NativeEntry.c';source='D:\ReBaseGuard-309\records\p309-post-root-continuation-20261016-v1\p309-readiness-repair-staging-v3\production-build-stage\NativeEntry.c';sha256='20eebd6407b745cffe79c5d0d9f6fc0ffb53013727f0e72f293fad7c8bf0e17e'},
 @{file='Read-InstallationFacts.ps1';source='D:\ReBaseGuard-309\records\p309-post-root-continuation-20261016-v1\p309-readiness-repair-staging-v3\production-build-stage\Read-InstallationFacts.ps1';sha256='4ea4e224a876f6a1c0d42144f8f5edf819172992329a7231bf2d6fca8e561054'},
 @{file='Trusted-Entry.template.ps1';source='D:\ReBaseGuard-309\records\p309-post-root-continuation-20261016-v1\p309-readiness-repair-staging-v3\production-build-stage\Trusted-Entry.template.ps1';sha256='124f526c266910a40b4614aa66994e18287db33e8e5c48cf37b62939d1df135c'},
 @{file='Launch-Approved.ps1';source='D:\ReBaseGuard-309\records\p309-post-root-continuation-20261016-v1\p309-readiness-repair-staging-v3\Launch-Approved.final-candidate.ps1';sha256='9b89849c5e5636b219b29ad633f4dda43a6268bdd3a8858b4b0fc73ae9119d09'}
)
function HashBytes([byte[]]$b){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($b)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
$id=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner packaging only'}
try{[void][IO.File]::GetAttributes($private);$exists=$true}catch{$hr=$_.Exception.GetBaseException().HResult;if($hr -notin @(-2147024894,-2147024893)){throw};$exists=$false}
if($exists){throw 'fresh private target required; no overwrite/adoption'}
$profileExpected='O:SYG:SYD:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;S-1-5-21-1923243488-1610499346-3556306727-1001)(A;;0x100020;;;S-1-15-3-65536-599108337-2355189375-1353122160-3480128286-3345335107-485756383-4087318168-230526575)'
if(([IO.DirectoryInfo]::new('C:\Users\Lenovo')).GetAccessControl().GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access') -cne $profileExpected){throw 'profile custody differs'}
foreach($p in @('C:\','C:\Users','C:\Users\Lenovo')){if(([IO.File]::GetAttributes($p)-band[IO.FileAttributes]::ReparsePoint)-ne 0){throw 'reparse parent'}}
$held=[Collections.Generic.List[IO.FileStream]]::new();$bytes=@{}
try{
 foreach($row in $payload){$f=[IO.FileStream]::new($row.source,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$held.Add($f);$m=[IO.MemoryStream]::new();try{$f.CopyTo($m);$b=$m.ToArray()}finally{$m.Dispose()};if((HashBytes $b)-cne$row.sha256){throw 'archived payload digest differs'};$bytes[$row.file]=$b}
 $acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetAccessRuleProtection($true,$false);$acl.SetOwner($id.User)
 foreach($sid in @($id.User,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'),[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))){$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))}
 $dir=[IO.Directory]::CreateDirectory($private,$acl);$actual=$dir.GetAccessControl()
 if(($dir.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0-or-not$actual.AreAccessRulesProtected-or$actual.GetOwner([Security.Principal.SecurityIdentifier]).Value-cne$id.User.Value-or$actual.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)-cne$acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)){throw 'new private root custody differs'}
 function WriteNew([string]$name,[byte[]]$data){$f=[IO.FileStream]::new((Join-Path $private $name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($data,0,$data.Length);$f.Flush($true)}finally{$f.Dispose()}}
 function JsonNew([string]$name,$data){WriteNew $name ([Text.Encoding]::UTF8.GetBytes(($data|ConvertTo-Json -Depth 10)))}
 foreach($row in $payload){WriteNew $row.file $bytes[$row.file];if((HashBytes ([IO.File]::ReadAllBytes((Join-Path $private $row.file))))-cne$row.sha256){throw 'private copy differs'}}
 $env:TEMP=$private;$env:TMP=$private
 $preflight=& ([ScriptBlock]::Create([Text.Encoding]::UTF8.GetString($bytes['Launch-Approved.ps1']))) -ReadOnlyPreflight
 WriteNew 'readonly-entry-pins.json' ([Text.Encoding]::UTF8.GetBytes(($preflight -join [Environment]::NewLine)))
 $parses=@();foreach($row in $payload|Where-Object {$_.file.EndsWith('.ps1')}){$tok=$null;$err=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $private $row.file),[ref]$tok,[ref]$err);if($err.Count){throw 'copied source parse failed'};$parses+=@{file=$row.file;errors=0}}
 $result=@{utc=[DateTime]::UtcNow.ToString('o');scope='BYTE_EXACT_PRIVATE_BUILD_ARTIFACT_COPY_AND_READONLY_FILE_PREFLIGHT';input_source_commit=$sourceCommit;payload=$payload;copied=$payload.Count;private_root=$private;private_root_sddl=$actual.Sddl;parse=$parses;unchanged_tests_not_repeated=$true;compiler_reexecuted=$false;uac_requests=0;native_entry_executions=0;harness_executions=0;trace_starts=0;vm_starts=0;human_approval_received=$false;admission='BLOCKED';I1_I7='OPEN'}
 JsonNew 'PRIVATE_BINDING.json' $result
 $manifest=@(Get-ChildItem -LiteralPath $private -File|ForEach-Object{@{file=$_.Name;bytes=$_.Length;sha256=(HashBytes ([IO.File]::ReadAllBytes($_.FullName)))}})
 JsonNew 'SHA256SUMS.json' $manifest
 $result|ConvertTo-Json -Depth 10
}finally{foreach($f in $held){$f.Dispose()}}
