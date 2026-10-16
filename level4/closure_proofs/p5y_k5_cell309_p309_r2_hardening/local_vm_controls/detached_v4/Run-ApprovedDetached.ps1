#requires -Version 7.0
param([Parameter(Mandatory)][string]$ApprovalRecord,
      [Parameter(Mandatory)][string]$EvidenceDirectory)
$ErrorActionPreference='Stop'
$a=Get-Content -LiteralPath $ApprovalRecord -Raw|ConvertFrom-Json
if($a.scope -ne 'P309_LOCAL_VM_DETACHED_V4' -or $a.fixed_probe_batch -ne $true -or
   -not $a.human_message_reference -or $a.maximum_launches -ne 2){throw 'New exact detached-batch approval required'}
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Ordinary non-elevated execution required'}
$os=Get-CimInstance Win32_OperatingSystem
if((Get-CimInstance Win32_OptionalFeature -Filter "Name='HypervisorPlatform'").InstallState -ne 1){throw 'WHP must be enabled'}
if($os.LastBootUpTime.ToUniversalTime().ToString('o') -eq '2026-10-09T06:18:21.6613670Z'){throw 'Original pending boot'}
if($os.FreePhysicalMemory*1KB -lt 8805306368L){throw 'Insufficient memory headroom'}
$guard='D:\ReBaseGuard-309\records\p309-local-vm-detached-preparation-20261016-0850\OwnedVmDetached-v4.exe'
$hashlist='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3.sha256'
if((Get-FileHash -LiteralPath $guard).Hash.ToLowerInvariant() -ne $a.guard_sha256){throw 'Guard pin mismatch'}
if((Get-FileHash -LiteralPath $hashlist).Hash.ToLowerInvariant() -ne $a.runtime_hashlist_sha256){throw 'Runtime list pin mismatch'}
if((Get-FileHash -LiteralPath $PSCommandPath).Hash.ToLowerInvariant() -ne $a.harness_sha256){throw 'Harness pin mismatch'}
$preflight=Join-Path $PSScriptRoot 'RuntimePreflight.ps1'
if((Get-FileHash -LiteralPath $preflight).Hash.ToLowerInvariant() -ne $a.preflight_sha256){throw 'Preflight source pin mismatch'}
. $preflight
$runtimePlan=Get-BoundRuntime -Root 'D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3' -HashList $hashlist -ExpectedListHash $a.runtime_hashlist_sha256
if($runtimePlan.file_count -ne 222 -or $runtimePlan.extra_files.Count -ne 0){throw 'Full runtime preflight rejected before launch reservation'}
$verdictFile=Join-Path $PSScriptRoot 'ProbeVerdict.ps1'
if((Get-FileHash -LiteralPath $verdictFile).Hash.ToLowerInvariant() -ne $a.verdict_sha256){throw 'Verdict source mismatch'}
. $verdictFile
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
$batchRoot=$evidence
foreach($case in @('deadline','guard-exit')) {
 $currentOS=Get-CimInstance Win32_OperatingSystem
 if($currentOS.LastBootUpTime -ne $os.LastBootUpTime -or $currentOS.FreePhysicalMemory*1KB -lt 8805306368L){throw 'Boot or memory precondition changed'}
 $fresh=Get-BoundRuntime -Root 'D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3' -HashList $hashlist -ExpectedListHash $a.runtime_hashlist_sha256
 if($fresh.file_count -ne 222){throw 'Runtime changed between cases'}
 $evidence=Join-Path $batchRoot $case
 New-Item -ItemType Directory -Path $evidence|Out-Null
 $log=Join-Path $evidence 'events.jsonl'
$info=[Diagnostics.ProcessStartInfo]::new($guard)
$info.UseShellExecute=$false;$info.CreateNoWindow=$true
$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
foreach($arg in @('--approved-diagnostic-only','D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3',$hashlist,$a.runtime_hashlist_sha256,$log,$case)){$info.ArgumentList.Add($arg)}
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
 $verdict=Get-ProbeVerdict -Rows $rows -Case $case -GuardExit $process.ExitCode -ChildWait $childWait
 $verdict|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $evidence 'observation.json')
 if(-not $verdict.scoped_probe_pass){throw 'Strict probe verdict failed; no second case or retry'}
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

}
