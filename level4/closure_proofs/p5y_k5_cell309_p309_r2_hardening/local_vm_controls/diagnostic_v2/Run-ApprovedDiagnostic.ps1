#requires -Version 7.0
param([Parameter(Mandatory)][string]$ApprovalRecord,
      [Parameter(Mandatory)][string]$EvidenceDirectory)
$ErrorActionPreference='Stop'
$a=Get-Content -LiteralPath $ApprovalRecord -Raw|ConvertFrom-Json
if($a.scope -ne 'P309_LOCAL_VM_DIAGNOSTIC_V2' -or $a.single_deadline_probe -ne $true -or
   -not $a.human_message_reference -or $a.maximum_launches -ne 1){throw 'New exact diagnostic approval required'}
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Ordinary non-elevated execution required'}
$os=Get-CimInstance Win32_OperatingSystem
if((Get-CimInstance Win32_OptionalFeature -Filter "Name='HypervisorPlatform'").InstallState -ne 1){throw 'WHP must be enabled'}
if($os.LastBootUpTime.ToUniversalTime().ToString('o') -eq '2026-10-09T06:18:21.6613670Z'){throw 'Original pending boot'}
if($os.FreePhysicalMemory*1KB -lt 8805306368L){throw 'Insufficient memory headroom'}
$guard='D:\ReBaseGuard-309\records\p309-local-vm-diagnostic-preparation-20261016-0830\OwnedVmDiagnostic-v2c.exe'
$hashlist='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1.sha256'
if((Get-FileHash -LiteralPath $guard).Hash.ToLowerInvariant() -ne $a.guard_sha256){throw 'Guard pin mismatch'}
if((Get-FileHash -LiteralPath $hashlist).Hash.ToLowerInvariant() -ne $a.runtime_hashlist_sha256){throw 'Runtime list pin mismatch'}
if((Get-FileHash -LiteralPath $PSCommandPath).Hash.ToLowerInvariant() -ne $a.harness_sha256){throw 'Harness pin mismatch'}
$evidence=[IO.Path]::GetFullPath($EvidenceDirectory)
if(-not $evidence.StartsWith('D:\ReBaseGuard-309\records\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected evidence root'}
# This fixed invocation directory is part of the approval. Cannot choose another to retry.
if($evidence -ne $a.evidence_directory -or (Test-Path -LiteralPath $evidence)){throw 'Evidence collision or approval path mismatch; no retry'}
New-Item -ItemType Directory -Path $evidence|Out-Null
Copy-Item -LiteralPath $ApprovalRecord -Destination (Join-Path $evidence 'approval-used.json')
@{utc=[DateTime]::UtcNow.ToString('o');boot=$os.LastBootUpTime.ToUniversalTime().ToString('o');available_bytes=$os.FreePhysicalMemory*1KB;admission='BLOCKED'}|
 ConvertTo-Json|Set-Content -LiteralPath (Join-Path $evidence 'preflight.json')
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
public static class P309DiagnosticObservation {
 [DllImport("kernel32.dll", SetLastError=true)] public static extern IntPtr OpenProcess(uint rights,bool inherit,uint pid);
 [DllImport("kernel32.dll", SetLastError=true)] public static extern bool GetProcessTimes(IntPtr p,out long c,out long e,out long k,out long u);
 [DllImport("kernel32.dll")] public static extern uint WaitForSingleObject(IntPtr p,uint ms);
 [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr p);
}
'@
$log=Join-Path $evidence 'deadline.jsonl'
$info=[Diagnostics.ProcessStartInfo]::new($guard)
$info.UseShellExecute=$false;$info.CreateNoWindow=$true
$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
foreach($arg in @('--approved-diagnostic-only','D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1',$hashlist,$a.runtime_hashlist_sha256,$log,'deadline')){$info.ArgumentList.Add($arg)}
$process=$null;$handle=[IntPtr]::Zero;$bound=$false
try {
 $process=[Diagnostics.Process]::Start($info)
 $stdout=$process.StandardOutput.ReadToEndAsync();$stderr=$process.StandardError.ReadToEndAsync()
 $timer=[Diagnostics.Stopwatch]::StartNew()
 while($timer.Elapsed.TotalSeconds -lt 40 -and -not $process.HasExited){
  if(Test-Path -LiteralPath $log){
   foreach($line in Get-Content -LiteralPath $log){
    try{$row=$line|ConvertFrom-Json}catch{continue}
    if($row.event -eq 'owned_start'){
     $handle=[P309DiagnosticObservation]::OpenProcess(0x00101000,$false,[uint32]$row.pid)
     if($handle -eq [IntPtr]::Zero){throw 'Cannot hold exact child handle'}
     [long]$c=0;[long]$e=0;[long]$k=0;[long]$u=0
     if(-not [P309DiagnosticObservation]::GetProcessTimes($handle,[ref]$c,[ref]$e,[ref]$k,[ref]$u) -or $c -ne [long]$row.creation_filetime){throw 'Child generation mismatch'}
     $bound=$true;break
    }
   }
  }
  if($bound){break};Start-Sleep -Milliseconds 25
 }
 if(-not $bound){throw 'No exact child observation; UNKNOWN'}
 if(-not $process.WaitForExit(30000)){throw 'Guard completion UNKNOWN; do not relaunch'}
 $childWait=[P309DiagnosticObservation]::WaitForSingleObject($handle,5000)
 $rows=@(Get-Content -LiteralPath $log|ForEach-Object {$_|ConvertFrom-Json})
 $cleanup=@($rows|Where-Object {$_.event -eq 'cleanup' -and $_.cleanup_proven -eq $true}).Count -eq 1
 $single=@($rows|Where-Object {$_.event -eq 'alive_at_5s' -and $_.active_job_processes -eq 1}).Count -eq 1
 $snapshots=@($rows|Where-Object {$_.event -eq 'job_snapshot'})
 $readbacks=@($rows|Where-Object {$_.event -eq 'limits_readback' -and $_.match -eq $true})
 $unknown=@($snapshots|Where-Object {$_.pid_query_error -ne 0 -or $null -ne $_.pid_parse_error -or @($_.members|Where-Object {$_.identity -eq 'UNKNOWN' -or $_.image_error -ne 0}).Count -gt 0}).Count -gt 0
 @{guard_exit=$process.ExitCode;child_wait=$childWait;bound_creation_filetime=$c;cleanup_observed=($cleanup -and $childWait -eq 0);
   original_single_member_expectation_met=$single;unknown_member_observations=$unknown;snapshot_count=$snapshots.Count;matching_limits_readbacks=$readbacks.Count;
   diagnostic_only=$true;formal_admission='BLOCKED';automatic_second_probe=$false;proves_I1_I6_closure=$false}|
  ConvertTo-Json|Set-Content -LiteralPath (Join-Path $evidence 'observation.json')
 if($process.ExitCode -ne 0 -or -not $cleanup -or $childWait -ne 0){throw 'Cleanup not fully observed; retain UNKNOWN and investigate'}
 # Even a complete diagnostic record is not an admission/feasibility PASS.
} catch {
 @{error=$_.Exception.Message;utc=[DateTime]::UtcNow.ToString('o');admission='BLOCKED';retry_allowed=$false}|
  ConvertTo-Json|Set-Content -LiteralPath (Join-Path $evidence 'error.json')
 throw
} finally {
 if($handle -ne [IntPtr]::Zero){[void][P309DiagnosticObservation]::CloseHandle($handle)}
 if($process){
  if($process.HasExited){
   $stdout.GetAwaiter().GetResult()|Set-Content -LiteralPath (Join-Path $evidence 'guard.stdout.txt')
   $stderr.GetAwaiter().GetResult()|Set-Content -LiteralPath (Join-Path $evidence 'guard.stderr.txt')
  }
  $process.Dispose()
 }
}
