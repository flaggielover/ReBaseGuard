param([Parameter(Mandatory=$true)][byte[]]$ApprovalBytes,
      [Parameter(Mandatory=$true)][string]$VerifiedHarnessSha256)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
# Execute only the already-hashed in-memory ScriptBlock, through the approved
# EncodedCommand. Never elevate this mutable file path or adjacent pin files.
if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) {throw 'Windows PowerShell 5.1 required'}
$root='C:\ProgramData\ReBaseGuardP309-I2-RootDiagnostic-v3'
$candidate='C:\Users\Lenovo\P309-I2-root-build-20261016-v1\EtwCapture-v3.exe'
$binarySha256='__ETW_SHA256__'
$whpCandidate='C:\Users\Lenovo\P309-I2-root-build-20261016-v1\WhpCounterProbe.exe'
$whpSha256='__WHP_SHA256__'
function Hash-Bytes([byte[]]$bytes) {
    $hash=[Security.Cryptography.SHA256]::Create()
    try { [BitConverter]::ToString($hash.ComputeHash($bytes)).Replace('-','').ToLowerInvariant() } finally {$hash.Dispose()}
}
function Get-FixtureSummary([object[]]$rows) {
    $native=0;$whp=0;$seen=[Collections.Generic.HashSet[string]]::new()
    foreach($r in $rows) {
        foreach($field in @('scope','pid','creation_filetime','exit_filetime','exit_code','job_total','job_active','atomic_job_assignment','kill_on_close','handle_inheritance')) {
            if($r.PSObject.Properties.Name -notcontains $field) {throw "missing fixture field: $field"}
        }
        foreach($field in @('pid','creation_filetime','exit_filetime','exit_code','job_total','job_active')) {
            if(($r.$field -isnot [int]) -and ($r.$field -isnot [long]) -and ($r.$field -isnot [uint32]) -and ($r.$field -isnot [uint64])) {throw 'noninteger fixture identity/accounting'}
        }
        if($r.pid -le 0 -or $r.pid -gt [uint32]::MaxValue -or $r.creation_filetime -le 0 -or
           $r.exit_filetime -lt $r.creation_filetime -or $r.exit_code -ne 0 -or $r.job_total -ne 1 -or $r.job_active -ne 0 -or
           $r.atomic_job_assignment -isnot [bool] -or $r.atomic_job_assignment -ne $true -or
           $r.kill_on_close -isnot [bool] -or $r.kill_on_close -ne $true -or
           $r.handle_inheritance -isnot [bool] -or $r.handle_inheritance -ne $false) {throw 'invalid fixture proof'}
        if(-not $seen.Add(([string]$r.pid)+':'+([string]$r.creation_filetime))) {throw 'duplicate fixture generation'}
        if($r.scope -ceq 'OWNED_SHORT_LIFETIME_CPU_FIXTURE_ONLY') {$native++}
        elseif($r.scope -ceq 'OWNED_WHP_COUNTER_FIXTURE_ONLY') {$whp++}
        else {throw 'unrecognized fixture scope'}
    }
    [pscustomobject]@{native_fixture_clean=$native -eq 3;whp_fixture_clean=$whp -eq 1;admission='BLOCKED'}
}
$approval=[Text.Encoding]::UTF8.GetString($ApprovalBytes) | ConvertFrom-Json
if($approval.scope -cne 'P309_I2_SINGLE_ROOT_DIAGNOSTIC_V3' -or $approval.capture_count -ne 1 -or $approval.whp_count -ne 1 -or
   $approval.binary_sha256 -cne $binarySha256 -or $approval.harness_sha256 -cne $VerifiedHarnessSha256 -or
   $approval.whp_sha256 -cne $whpSha256 -or
   [string]::IsNullOrWhiteSpace($approval.human_message_reference)) {throw 'approval binding refused'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(-not ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'explicit UAC-approved entry required'}
$bytes=[IO.File]::ReadAllBytes($candidate)
if((Hash-Bytes $bytes) -cne $binarySha256) {throw 'binary changed'}
$whpBytes=[IO.File]::ReadAllBytes($whpCandidate)
if((Hash-Bytes $whpBytes) -cne $whpSha256) {throw 'WHP binary changed'}
if(([IO.DriveInfo]::new('C')).AvailableFreeSpace -lt 2GB) {throw 'insufficient evidence space: 1 GiB log plus 1 GiB reserve required'}
if([IO.Directory]::Exists($root) -or [IO.File]::Exists($root)) {throw 'root collision; never adopt'}
foreach($parent in @('C:\','C:\ProgramData')) {
    if(([IO.File]::GetAttributes($parent) -band [IO.FileAttributes]::ReparsePoint) -ne 0) {throw 'reparse parent'}
}
$parentPins=@{
    'C:\'='O:S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464G:S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464D:PAI(A;;LC;;;AU)(A;OICIIO;SDGXGWGR;;;AU)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;0x1200a9;;;BU)(A;;0x1000a1;;;S-1-15-3-65536-1888954469-739942743-1668119174-2468466756-4239452838-1296943325-355587736-700089176)'
    'C:\ProgramData'='O:SYG:SYD:PAI(A;OICIIO;GA;;;CO)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;0x1200a9;;;BU)(A;CI;DCLCRPCR;;;BU)'
}
foreach($parent in $parentPins.Keys) {
    $security=[IO.DirectoryInfo]::new($parent).GetAccessControl()
    if($security.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access') -cne $parentPins[$parent]) {throw 'system parent ACL changed; no capture'}
}
$admins=[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544')
$system=[Security.Principal.SecurityIdentifier]::new('S-1-5-18')
$acl=[Security.AccessControl.DirectorySecurity]::new()
$acl.SetAccessRuleProtection($true,$false);$acl.SetOwner($admins)
$inherit=[Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit'
foreach($sid in @($admins,$system)) {
    $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl',$inherit,'None','Allow'))
}
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($identity.User,'ReadAndExecute',$inherit,'None','Allow'))
# Framework CreateDirectory supplies the security descriptor at creation; it
# never resets an existing directory's ACL. A raced user-created directory cannot
# set its owner to BUILTIN\Administrators. Reject it before writing any content.
$directory=[IO.Directory]::CreateDirectory($root,$acl)
$check=$directory.GetAccessControl()
if($check.GetOwner([Security.Principal.SecurityIdentifier]).Value -cne $admins.Value -or
   -not $check.AreAccessRulesProtected -or
   $check.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access) -cne
      $acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access) -or
   ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {throw 'fresh root security differs'}
function Write-New([string]$name,[byte[]]$content) {
    $f=[IO.FileStream]::new((Join-Path $root $name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
    try {$f.Write($content,0,$content.Length);$f.Flush($true)} finally {$f.Dispose()}
}
function Write-Json([string]$name,$value) {Write-New $name ([Text.Encoding]::UTF8.GetBytes(($value | ConvertTo-Json -Depth 10)))}
Write-New 'EtwCapture.exe' $bytes
Write-New 'WhpCounterProbe.exe' $whpBytes
Write-New 'approval-used.json' $ApprovalBytes
Write-Json 'preflight.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');root_sddl=$check.Sddl;harness_sha256=$VerifiedHarnessSha256;binary_sha256=$binarySha256;scope=$approval.scope;admission='BLOCKED'})

function Start-Owned([string]$mode,[string]$label) {
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=Join-Path $root 'EtwCapture.exe';$psi.Arguments=$mode
    $psi.UseShellExecute=$false;$psi.CreateNoWindow=$true;$psi.WorkingDirectory=$root
    $psi.RedirectStandardOutput=$true;$psi.RedirectStandardError=$true
    $psi.EnvironmentVariables.Clear()
    $psi.EnvironmentVariables['SystemRoot']='C:\Windows';$psi.EnvironmentVariables['WINDIR']='C:\Windows'
    $psi.EnvironmentVariables['PATH']='C:\Windows\System32'
    $psi.EnvironmentVariables['TEMP']=$root;$psi.EnvironmentVariables['TMP']=$root
    $process=[Diagnostics.Process]::Start($psi);$held=$process.Handle
    [pscustomobject]@{P=$process;Handle=$held;Label=$label;Out=$process.StandardOutput.ReadToEndAsync();Err=$process.StandardError.ReadToEndAsync()}
}
function Save-Owned($owned) {
    if($null -eq $owned -or -not $owned.P.HasExited) {return}
    Write-New ($owned.Label+'.stdout.txt') ([Text.Encoding]::UTF8.GetBytes($owned.Out.Result))
    Write-New ($owned.Label+'.stderr.txt') ([Text.Encoding]::UTF8.GetBytes($owned.Err.Result))
}
$guard=$null;$sampler=$null;$prequery=$null;$final=$null;$failure=$null;$dispatched=$false
try {
    $prequery=Start-Owned '--query-name-readonly' 'preexisting-session'
    if(-not $prequery.P.WaitForExit(5000) -or $prequery.P.ExitCode -ne 0) {throw 'preexisting/unknown session; no capture'}
    $guard=Start-Owned '--guard-approved' 'guard';$dispatched=$true
    $ready=[Diagnostics.Stopwatch]::StartNew()
    while(-not [IO.File]::Exists((Join-Path $root 'session-created.json'))) {
        if($guard.P.HasExited -or $ready.ElapsedMilliseconds -gt 5000) {throw 'successful creation not acknowledged'}
        Start-Sleep -Milliseconds 25
    }
    $sampler=Start-Owned '--sample-approved' 'sampler'
    if(-not $sampler.P.WaitForExit(70000)) {throw 'sampler timeout; creator deadline retained'}
    if($sampler.P.ExitCode -ne 0) {throw 'sampler failed'}
} catch {$failure=$_.Exception.Message}
finally {
    $cleanupErrors=[Collections.Generic.List[string]]::new()
    try {if($null -ne $guard -and (-not $guard.P.WaitForExit(85000) -or $guard.P.ExitCode -ne 0)) {$failure='creator/deadline failed; no name-based stop or adoption'}}
    catch {$failure='creator wait UNKNOWN';$cleanupErrors.Add($_.Exception.Message)}
    # Sampler owns no children or session. Kill only its retained exact handle
    # after the creator deadline, then require confirmed exit. Never kill guard
    # while StartTrace/StopTrace may still be in flight.
    try {if($null -ne $sampler -and -not $sampler.P.HasExited) {
        try {$sampler.P.Kill();if(-not $sampler.P.WaitForExit(5000)) {$failure='sampler cleanup UNKNOWN'}} catch {$failure='sampler cleanup UNKNOWN'}
    }} catch {$cleanupErrors.Add('sampler state: '+$_.Exception.Message)}
    $absent=$false
    try {
        $final=Start-Owned '--query-name-readonly' 'final-session-query'
        $absent=$final.P.WaitForExit(5000) -and $final.P.ExitCode -eq 0
    } catch {$cleanupErrors.Add('final query: '+$_.Exception.Message)}
    $exited=$true
    foreach($owned in @($guard,$sampler,$prequery,$final)) {
        try {if($null -ne $owned -and -not $owned.P.HasExited) {$exited=$false}} catch {$exited=$false;$cleanupErrors.Add('helper state: '+$_.Exception.Message)}
        try {Save-Owned $owned} catch {$cleanupErrors.Add('save helper: '+$_.Exception.Message)}
    }
    $fixtures=$false;$whpFixture=$false
    $creatorStop=[IO.File]::Exists((Join-Path $root 'guard-clean.json'))
    try {if([IO.File]::Exists((Join-Path $root 'guard.jsonl'))) {
        $rows=@([IO.File]::ReadAllLines((Join-Path $root 'guard.jsonl')) | ForEach-Object {$_ | ConvertFrom-Json} |
            Where-Object {$_.PSObject.Properties.Name -contains 'job_total'})
        $summary=Get-FixtureSummary $rows
        $fixtures=$summary.native_fixture_clean;$whpFixture=$summary.whp_fixture_clean
    }} catch {$cleanupErrors.Add('fixture evidence: '+$_.Exception.Message)}
    if(-not $absent -or -not $exited -or -not $fixtures -or -not $whpFixture -or -not $creatorStop) {$failure='session/helper/fixture/creator stop evidence incomplete; UNKNOWN'}
    if($cleanupErrors.Count -gt 0) {$failure='cleanup/evidence incomplete'}
    try {Write-Json 'RESULT.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');capture_dispatched=$dispatched;capture_count=([int]$dispatched);
        result=$(if($null -eq $failure){'CAPTURE_COMPLETED_REQUIRES_OFFLINE_ANALYSIS'}else{'FAILED_OR_UNKNOWN'});failure=$failure;
        session_absent=$absent;helpers_exited=$exited;all_three_fixture_jobs_empty=$fixtures;whp_fixture_job_empty=$whpFixture;
        creator_stop_receipt_present=$creatorStop;counter_unavailability_is_not_zero_load=$true;
        cleanup_errors=@($cleanupErrors.ToArray());coverage_complete=$false;admission='BLOCKED';I1_I7='OPEN_RETAINED'})
    } catch {$failure='RESULT persistence failed';$cleanupErrors.Add($_.Exception.Message)}
    try {
        if($exited) {
            $manifest=foreach($f in $directory.GetFiles()) {
                try {[ordered]@{file=$f.Name;size=$f.Length;sha256=(Hash-Bytes ([IO.File]::ReadAllBytes($f.FullName)));state='HASHED'}}
                catch {$cleanupErrors.Add('hash '+$f.Name+': '+$_.Exception.Message);[ordered]@{file=$f.Name;state='UNREADABLE_NO_DIGEST'}}
            }
            Write-Json 'SHA256SUMS.json' @($manifest)
        } else {Write-Json 'MANIFEST_INCOMPLETE.json' @{reason='HELPERS_NOT_QUIESCENT_NO_STABLE_HASH_CLAIM';admission='BLOCKED'}}
    } catch {$cleanupErrors.Add('manifest: '+$_.Exception.Message)}
    if($cleanupErrors.Count -gt 0) {
        $failure='one or more evidence stages failed; no pass'
        try {Write-Json 'EVIDENCE_FAILURE.json' @{errors=@($cleanupErrors.ToArray());admission='BLOCKED'}} catch {[Console]::Error.WriteLine('EVIDENCE_PERSISTENCE_FAILED')}
    }
    # No elevated writes under the AU-writable D: hierarchy. After completion,
    # the ordinary owner copies records there and verifies every digest.
}
if($null -ne $failure) {throw $failure}
