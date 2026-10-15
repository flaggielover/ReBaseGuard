#requires -Version 7.0
param([Parameter(Mandatory=$true)][string]$ApprovalRecord,
      [Parameter(Mandatory=$true)][string]$EvidenceDirectory)
# Two fixed, paused, diskless 128 MiB VM probes; no Linux/P309 workload.
# This script is not run during source validation. Do not elevate it.
$ErrorActionPreference='Stop'
$a=Get-Content -LiteralPath $ApprovalRecord -Raw | ConvertFrom-Json
if($a.scope -ne 'P309_LOCAL_VM_FEASIBILITY_V1' -or $a.real_vm_probes -ne $true -or
   -not $a.human_message_reference){throw 'Human real-validation approval reference is required'}
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'VM probes must run without elevation'}
$state=Get-CimInstance Win32_OptionalFeature -Filter "Name='HypervisorPlatform'"
if($state.InstallState -ne 1){throw 'WHP is not reported enabled; no fallback or pending-reboot launch'}
$os=Get-CimInstance Win32_OperatingSystem
$preparation=Get-Content -LiteralPath $a.feature_preparation_result -Raw | ConvertFrom-Json
if($preparation.restart_needed -isnot [bool] -or -not $preparation.boot_before){throw 'Missing actual feature preparation result'}
if($preparation.restart_needed -and $os.LastBootUpTime.ToUniversalTime().ToString('o') -eq $preparation.boot_before){
 throw 'Required manual reboot has not occurred; do not launch the VM'
}
$available=$os.FreePhysicalMemory * 1KB
if($available -lt (8000000000L + 805306368L)){throw 'Host memory headroom is below 8 GB plus probe cap'}
$evidence=[IO.Path]::GetFullPath($EvidenceDirectory)
if(-not $evidence.StartsWith('D:\ReBaseGuard-309\records\',[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected evidence root'}
if(Test-Path -LiteralPath $evidence){throw 'Evidence collision; no overwrite/automatic retry'}
New-Item -ItemType Directory -Path $evidence | Out-Null
$guard='D:\ReBaseGuard-309\records\p309-local-vm-preparation-20261016-162345\OwnedVmProbe-v4.exe'
if((Get-FileHash -LiteralPath $guard).Hash.ToLowerInvariant() -ne $a.guard_sha256){throw 'Guard source/build approval binding differs'}
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
public static class P309ProbeObservation {
 [DllImport("kernel32.dll", SetLastError=true)] public static extern IntPtr OpenProcess(uint access, bool inherit, uint pid);
 [DllImport("kernel32.dll", SetLastError=true)] public static extern bool GetProcessTimes(IntPtr p, out long c, out long e, out long k, out long u);
 [DllImport("kernel32.dll", SetLastError=true)] public static extern uint WaitForSingleObject(IntPtr p, uint ms);
 [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr p);
}
'@
foreach($case in @('deadline','guard-exit')) {
 $log=Join-Path $evidence "$case.jsonl"
 $info=[Diagnostics.ProcessStartInfo]::new($guard)
 $info.UseShellExecute=$false; $info.CreateNoWindow=$true
 $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
 foreach($arg in @('--approved-feasibility-only','D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1',
   'D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1.sha256',$a.runtime_hashlist_sha256,$log,$case)){$info.ArgumentList.Add($arg)}
 $process=[Diagnostics.Process]::Start($info)
 $stdout=$process.StandardOutput.ReadToEndAsync(); $stderr=$process.StandardError.ReadToEndAsync()
 $handle=[IntPtr]::Zero; $bound=$false
 try {
  $deadline=[Diagnostics.Stopwatch]::StartNew()
  while($deadline.Elapsed.TotalSeconds -lt 40 -and -not $process.HasExited) {
   if(Test-Path -LiteralPath $log) {
    $first=Get-Content -LiteralPath $log -First 1 -ErrorAction SilentlyContinue
    if($first) {
     try{$start=$first | ConvertFrom-Json}catch{$start=$null}
     if($start -and $start.event -eq 'owned_start') {
      # Observe only the exact child, with synchronize/query rights; never terminate by PID.
      $handle=[P309ProbeObservation]::OpenProcess(0x00101000,$false,[uint32]$start.pid)
      if($handle -eq [IntPtr]::Zero){throw 'Unable to bind live child handle'}
      [long]$c=0;[long]$e=0;[long]$k=0;[long]$u=0
      if(-not [P309ProbeObservation]::GetProcessTimes($handle,[ref]$c,[ref]$e,[ref]$k,[ref]$u) -or
         $c -ne [long]$start.creation_filetime){throw 'PID generation mismatch'}
      $bound=$true;break
     }
    }
   }
   Start-Sleep -Milliseconds 25
  }
  if(-not $bound){throw 'No exact owned child binding; cannot claim cleanup'}
  if(-not $process.WaitForExit(30000)){throw 'Guard completion unknown; retain control/evidence, do not start another probe'}
  $childWait=[P309ProbeObservation]::WaitForSingleObject($handle,5000)
  $expected=if($case -eq 'deadline'){0}else{86}
  $rows=@(Get-Content -LiteralPath $log | ForEach-Object {$_ | ConvertFrom-Json})
  $alive=@($rows | Where-Object {$_.event -eq 'alive_at_5s' -and $_.active_job_processes -eq 1}).Count -eq 1
  $cleanup=if($case -eq 'deadline'){@($rows|Where-Object {$_.event -eq 'cleanup' -and $_.cleanup_proven -eq $true}).Count -eq 1}else{$true}
  $ok=$alive -and $cleanup -and $process.ExitCode -eq $expected -and $childWait -eq 0
  @{case=$case;guard_exit=$process.ExitCode;bound_creation_filetime=$c;child_wait=$childWait;
    scoped_probe_pass=$ok;formal_admission='BLOCKED';proves_guest_boot=$false;proves_I1_I6_closure=$false} |
    ConvertTo-Json | Set-Content (Join-Path $evidence "$case-observation.json")
  if(-not $ok){throw 'Real probe failed; no automatic retry or progression'}
 } finally {
  if($handle -ne [IntPtr]::Zero){[void][P309ProbeObservation]::CloseHandle($handle)}
  if($process.HasExited){
   $stdout.GetAwaiter().GetResult() | Set-Content (Join-Path $evidence "$case.stdout.txt")
   $stderr.GetAwaiter().GetResult() | Set-Content (Join-Path $evidence "$case.stderr.txt")
  }
  $process.Dispose()
 }
}
