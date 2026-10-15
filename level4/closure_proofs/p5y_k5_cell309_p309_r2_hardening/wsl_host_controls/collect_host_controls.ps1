param([ValidateRange(1,60)][int]$SampleSeconds=60,[string]$Distribution='Ubuntu-24.04')
# Development-only observation. No state-setting APIs, command lines or names emitted.
$ErrorActionPreference='Stop'
if(-not ('P309ReadOnlyNative' -as [type])) {
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class P309ReadOnlyNative {
 [DllImport("kernel32.dll")] public static extern bool QueryUnbiasedInterruptTime(out ulong value);
 [DllImport("powrprof.dll")] public static extern uint PowerGetActiveScheme(IntPtr root, out IntPtr guid);
 [DllImport("powrprof.dll")] public static extern uint PowerReadACValueIndex(IntPtr root, ref Guid scheme, ref Guid group, ref Guid setting, out uint value);
 [DllImport("powrprof.dll")] public static extern uint PowerReadDCValueIndex(IntPtr root, ref Guid scheme, ref Guid group, ref Guid setting, out uint value);
 [DllImport("kernel32.dll")] public static extern IntPtr LocalFree(IntPtr value);
}
'@
}
function HashText([string]$text) {
 $sha=[Security.Cryptography.SHA256]::Create()
 try { return [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($text))).Replace('-','').ToLowerInvariant() }
 finally { $sha.Dispose() }
}
function ClockSnapshot {
 $os=Get-CimInstance Win32_OperatingSystem
 $machine=(Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Cryptography').MachineGuid
 [ulong]$active=0
 $ok=[P309ReadOnlyNative]::QueryUnbiasedInterruptTime([ref]$active)
 [ordered]@{wall_s=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()/1000.0;
   uptime_s=[Environment]::TickCount64/1000.0; active_s=$(if($ok){$active/1e7}else{$null});
   host_id_sha256=(HashText $machine); boot_id_sha256=(HashText ($machine+'|'+$os.LastBootUpTime.ToUniversalTime().ToString('o')))}
}
function ProcessSnapshot {
 $map=@{}
 foreach($p in @(Get-CimInstance Win32_Process -Property ProcessId,CreationDate,KernelModeTime,UserModeTime)) {
   if($p.ProcessId -eq 0){continue} # OS Idle pseudo-process is not executing work.
   $created=if($null -ne $p.CreationDate){$p.CreationDate.ToUniversalTime().ToString('o')}else{$null}
   $cpu=if($null -ne $p.KernelModeTime -and $null -ne $p.UserModeTime){([double]$p.KernelModeTime+[double]$p.UserModeTime)/1e7}else{$null}
   $map[[int]$p.ProcessId]=@{created=$created;cpu=$cpu}
 }
 return $map
}
function MeasureProcesses($s0,$s1,[double]$elapsed) {
 $rows=@();$unreadable=0
 foreach($key in @($s1.Keys | Sort-Object)) {
  $current=$s1[$key];$fraction=$null
  if($s0.ContainsKey($key) -and $current.created -and $current.created -eq $s0[$key].created -and
    $null -ne $current.cpu -and $null -ne $s0[$key].cpu -and $current.cpu -ge $s0[$key].cpu -and $elapsed -gt 0) {
   $fraction=($current.cpu-$s0[$key].cpu)/$elapsed
  }
  if($null -eq $fraction){$unreadable++}
  $rows+=@{pid=$key;creation_sha256=$(if($current.created){HashText $current.created}else{$null});cpu_fraction=$fraction}
 }
 return @{rows=$rows;unreadable_count=$unreadable;
  disappeared_count=@($s0.Keys | Where-Object { -not $s1.ContainsKey($_) }).Count}
}
function PowerFacts {
 $result=[ordered]@{power_query_ok=$false;sleep_ac_s=$null;sleep_dc_s=$null;hibernate_ac_s=$null;hibernate_dc_s=$null;scheme_sha256=$null}
 $ptr=[IntPtr]::Zero
 try {
  if([P309ReadOnlyNative]::PowerGetActiveScheme([IntPtr]::Zero,[ref]$ptr) -ne 0){return $result}
  $scheme=[Runtime.InteropServices.Marshal]::PtrToStructure($ptr,[type][Guid])
  $group=[Guid]'238c9fa8-0aad-41ed-83f4-97be242c8f20'
  $result.scheme_sha256=HashText $scheme.ToString()
  $ok=$true
  foreach($pair in @(@('sleep','29f6c1db-86da-48c5-9fdb-f2b67b1f44da'),@('hibernate','9d7815a6-7ee4-497e-8888-515a05f02364'))) {
   $setting=[Guid]$pair[1]; [uint32]$ac=0;[uint32]$dc=0
   $rc1=[P309ReadOnlyNative]::PowerReadACValueIndex([IntPtr]::Zero,[ref]$scheme,[ref]$group,[ref]$setting,[ref]$ac)
   $rc2=[P309ReadOnlyNative]::PowerReadDCValueIndex([IntPtr]::Zero,[ref]$scheme,[ref]$group,[ref]$setting,[ref]$dc)
   if($rc1 -eq 0){$result[$pair[0]+'_ac_s']=[int64]$ac}else{$ok=$false}
   if($rc2 -eq 0){$result[$pair[0]+'_dc_s']=[int64]$dc}else{$ok=$false}
  }
  $result.power_query_ok=$ok
 } catch { $result.power_query_ok=$false }
 finally { if($ptr -ne [IntPtr]::Zero){[void][P309ReadOnlyNative]::LocalFree($ptr)} }
 return $result
}
function PolicyFingerprint($policy) {
 # Hash the exact emitted power facts. Never re-query power policy for its hash.
 $power=[ordered]@{}
 foreach($key in @('power_query_ok','sleep_ac_s','sleep_dc_s','hibernate_ac_s','hibernate_dc_s','scheme_sha256')) {
  $power[$key]=$policy[$key]
 }
 $tasks=@($policy.update_task_states | Sort-Object identity_sha256 | ForEach-Object {
  [ordered]@{identity_sha256=$_.identity_sha256;state=$_.state;next_run_utc=$_.next_run_utc}
 })
 $updates=[ordered]@{}
 foreach($key in @($policy.update_policy_values.Keys | Sort-Object)){$updates[$key]=$policy.update_policy_values[$key]}
 return HashText (([ordered]@{power=$power;update=$updates;tasks=$tasks}) | ConvertTo-Json -Depth 6 -Compress)
}
$start=ClockSnapshot
$s0=ProcessSnapshot
$firstQueryEnd=[Environment]::TickCount64/1000.0
Start-Sleep -Seconds $SampleSeconds
$secondQueryStart=[Environment]::TickCount64/1000.0
$s1=ProcessSnapshot
$end=ClockSnapshot
# Lower-bound denominator is conservative for non-atomic CIM queries.
$elapsed=$secondQueryStart-$firstQueryEnd
$measurement=MeasureProcesses $s0 $s1 $elapsed
$rows=$measurement.rows;$unreadable=$measurement.unreadable_count;$disappeared=$measurement.disappeared_count
$policy=PowerFacts
$policy.pending_reboot=$null
$policy.pending_reboot_indicators=@()
try {
 $wu=Test-Path -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
 $cbs=Test-Path -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'
 $session=Get-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager'
 if($wu){$policy.pending_reboot_indicators+='WindowsUpdateRebootRequired'}
 if($cbs){$policy.pending_reboot_indicators+='ComponentServicingRebootPending'}
 if($session.PendingFileRenameOperations){$policy.pending_reboot_indicators+='PendingFileRenameOperations'}
 $policy.pending_reboot=$policy.pending_reboot_indicators.Count -gt 0
} catch { $policy.pending_reboot=$null }
$policy.update_policy_known=$false
$policy.maintenance_window_approved=$false
$policy.update_policy_values=@{}
try {
 $path='HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
 if(Test-Path -LiteralPath $path) {
  $au=Get-ItemProperty -LiteralPath $path
  foreach($key in @('NoAutoUpdate','AUOptions','NoAutoRebootWithLoggedOnUsers')) {
   if($null -ne $au.$key){$policy.update_policy_values[$key]=$au.$key}
  }
 }
} catch { $policy.update_read_error=$true }
$policy.scheduled_tasks_query_ok=$false
$policy.update_task_states=@()
try {
 $tasks=@(Get-ScheduledTask | Where-Object { $_.TaskPath -like '\Microsoft\Windows\UpdateOrchestrator\*' -or $_.TaskPath -like '\Microsoft\Windows\WindowsUpdate\*' } | Sort-Object TaskPath,TaskName)
 $policy.update_task_states=@($tasks | ForEach-Object {
  $info=Get-ScheduledTaskInfo -TaskPath $_.TaskPath -TaskName $_.TaskName
  @{identity_sha256=(HashText ($_.TaskPath+$_.TaskName));state=$_.State.ToString();
    next_run_utc=$(if($info.NextRunTime.Year -gt 2000){$info.NextRunTime.ToUniversalTime().ToString('o')}else{$null})}
 })
 $policy.scheduled_tasks_query_ok=$true
} catch { $policy.scheduled_tasks_query_ok=$false }
$policy.event_query_ok=$false
$policy.event_window_covers_sample=$false
$policy.event_log_cleared=$null
$policy.events_since_start=@()
try {
 # An unfiltered bounded window plus oldest-record check detects truncation.
 $events=@(Get-WinEvent -LogName System -MaxEvents 2048)
 $since=[DateTimeOffset]::FromUnixTimeMilliseconds([int64]($start.wall_s*1000)).UtcDateTime
 $policy.event_window_covers_sample=$events.Count -gt 0 -and $events[-1].TimeCreated.ToUniversalTime() -le $since
 $relevant=@($events | Where-Object { $_.TimeCreated.ToUniversalTime() -ge $since -and
  (($_.ProviderName -eq 'Microsoft-Windows-Kernel-Power' -and $_.Id -in @(41,42,107,506,507)) -or
   ($_.ProviderName -eq 'Microsoft-Windows-Power-Troubleshooter' -and $_.Id -eq 1) -or
   ($_.ProviderName -eq 'User32' -and $_.Id -eq 1074) -or
   ($_.ProviderName -eq 'EventLog' -and $_.Id -in @(6005,6006,6008)) -or
   ($_.ProviderName -eq 'Microsoft-Windows-Eventlog' -and $_.Id -eq 104)) })
 $policy.events_since_start=@($relevant | ForEach-Object { @{event_id=$_.Id;record_id=$_.RecordId;provider=$_.ProviderName;utc=$_.TimeCreated.ToUniversalTime().ToString('o')} })
 $policy.event_log_cleared=@($relevant | Where-Object { $_.Id -eq 104 }).Count -gt 0
 $policy.event_query_ok=$true
} catch { $policy.event_query_ok=$false }
# Serialize stable ordered records from the emitted facts, without a second power query.
$policy.policy_sha256=PolicyFingerprint $policy
$os=Get-CimInstance Win32_OperatingSystem
$reg=@(Get-ChildItem -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' | Get-ItemProperty | Where-Object DistributionName -eq $Distribution)
if($reg.Count -ne 1){throw 'Distribution registration ambiguous'}
$path=$reg[0].BasePath
$prefix=[string]::Concat([char]92,[char]92,'?',[char]92)
if($path.StartsWith($prefix)){$path=$path.Substring(4)}
$drive=[IO.Path]::GetPathRoot($path).TrimEnd([char]92)
if($drive -notmatch '^[A-Za-z]:$'){throw 'Backing volume unknown'}
$volume=Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$drive'"
[ordered]@{schema='P309_WINDOWS_CONTROL_SAMPLE/1';scope='DEVELOPMENT_ONLY';start=$start;end=$end;
 process_observation=@{coverage='BEST_EFFORT';protected_process_coverage=$false;process_lifetime_events_complete=$false;
  observed_count=$rows.Count;unreadable_count=$unreadable;disappeared_count=$disappeared;cpu_elapsed_lower_bound_s=$elapsed;rows=$rows};policy=$policy;
 resources=@{available_memory_bytes=[int64]$os.FreePhysicalMemory*1024;backing_free_bytes=[int64]$volume.FreeSpace};
 limitations=@('CIM cannot attest complete protected/short-lived process coverage.','All activity conservatively unattributed; no VM workload exemption.','Registry/task observations do not prove maintenance control.')} | ConvertTo-Json -Depth 12
