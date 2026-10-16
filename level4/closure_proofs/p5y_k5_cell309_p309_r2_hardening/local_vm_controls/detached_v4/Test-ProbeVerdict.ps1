# Synthetic variations of saved rows; never modifies actual evidence or calls native APIs.
param([Parameter(Mandatory)][string]$ActualV3Log)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'ProbeVerdict.ps1')
$actual=@(Get-Content -LiteralPath $ActualV3Log|ForEach-Object {$_|ConvertFrom-Json})
$count=0
function Assert([bool]$value){if(-not $value){throw "Verdict test failed after $script:count checks"};$script:count++}
Assert (-not (Get-ProbeVerdict -Rows $actual -Case deadline -GuardExit 0 -ChildWait 0).scoped_probe_pass)
$synthetic=@($actual|ConvertTo-Json -Depth 12|ConvertFrom-Json)
foreach($row in $synthetic){
 if($row.event -eq 'alive_at_5s'){$row.active_job_processes=1}
 if($row.event -eq 'job_snapshot'){
  if($row.stage -ne 'empty_before_creation'){$row.total=1}
  if($row.stage -eq 'alive_at_5s'){$row.active=1;$row.members=@($row.members[0])}
  $raw=[byte[]]::new(136);$n=@($row.members).Count
  [BitConverter]::GetBytes([uint32]$n).CopyTo($raw,0);[BitConverter]::GetBytes([uint32]$n).CopyTo($raw,4)
  for($i=0;$i -lt $n;$i++){[BitConverter]::GetBytes([uint64]$row.members[$i].pid).CopyTo($raw,8+8*$i)}
  $row.pid_buffer_base64=[Convert]::ToBase64String($raw);$row.pid_returned_bytes=8+8*$n
 }
 if($row.event -eq 'stop_timing'){$row.stop_tick_ms=$row.started_tick_ms+14510;$row.observed_tick_ms=$row.started_tick_ms+14580}
}
Assert ((Get-ProbeVerdict -Rows $synthetic -Case deadline -GuardExit 0 -ChildWait 0).scoped_probe_pass)
foreach($mutation in @('late','missing','foreign','limits','reused_pid','query_error','extra_row','raw_pid','raw_count')){
 $rows=@($synthetic|ConvertTo-Json -Depth 12|ConvertFrom-Json)
 switch($mutation){
  'late'{($rows|Where-Object event -eq 'stop_timing').observed_tick_ms+=1000}
  'missing'{$rows=@($rows|Where-Object event -ne 'cleanup')}
  'foreign'{($rows|Where-Object {$_.event -eq 'job_snapshot' -and $_.stage -eq 'alive_at_5s'}).members[0].image='C:\Windows\System32\conhost.exe'}
  'limits'{($rows|Where-Object {$_.event -eq 'limits_readback' -and $_.stage -eq 'alive_at_5s'}).active_limit=2}
  'reused_pid'{($rows|Where-Object {$_.event -eq 'job_snapshot' -and $_.stage -eq 'alive_at_5s'}).members[0].creation_filetime++}
  'query_error'{($rows|Where-Object {$_.event -eq 'job_snapshot' -and $_.stage -eq 'alive_at_5s'}).pid_query_error=5}
  'extra_row'{$rows+=($rows|Where-Object event -eq 'cleanup')}
  'raw_pid'{$s=$rows|Where-Object {$_.event -eq 'job_snapshot' -and $_.stage -eq 'alive_at_5s'};$raw=[Convert]::FromBase64String($s.pid_buffer_base64);[BitConverter]::GetBytes(999UL).CopyTo($raw,8);$s.pid_buffer_base64=[Convert]::ToBase64String($raw)}
  'raw_count'{$s=$rows|Where-Object {$_.event -eq 'job_snapshot' -and $_.stage -eq 'alive_at_5s'};$s.pid_returned_bytes=24}
 }
 Assert (-not (Get-ProbeVerdict -Rows $rows -Case deadline -GuardExit 0 -ChildWait 0).scoped_probe_pass)
}
$abrupt=@($synthetic|Where-Object {$_.event -notin @('cleanup','stop_timing') -and $_.stage -ne 'after_stop'})
$abrupt+=[pscustomobject]@{event='about_to_exit_guard';cleanup_proven=$false}
Assert ((Get-ProbeVerdict -Rows $abrupt -Case guard-exit -GuardExit 86 -ChildWait 0).scoped_probe_pass)
Assert (-not (Get-ProbeVerdict -Rows $abrupt -Case guard-exit -GuardExit 0 -ChildWait 0).scoped_probe_pass)
Assert (-not (Get-ProbeVerdict -Rows $abrupt -Case guard-exit -GuardExit 86 -ChildWait 258).scoped_probe_pass)
"Verdict checks passed: $count; synthetic variations only; actual V3 remains rejected"
