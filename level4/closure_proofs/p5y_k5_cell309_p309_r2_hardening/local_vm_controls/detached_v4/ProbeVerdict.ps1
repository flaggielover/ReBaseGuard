# Pure evidence evaluation. No native calls, filesystem writes, admission or authorization effects.
function Get-ProbeVerdict {
 param([Parameter(Mandatory)][object[]]$Rows,[ValidateSet('deadline','guard-exit')][string]$Case,
       [int]$GuardExit,[uint32]$ChildWait)
 $bad=[Collections.Generic.List[string]]::new()
 function One([string]$event,[string]$stage=''){
  $found=@($Rows|Where-Object {$_.event -eq $event -and (-not $stage -or $_.stage -eq $stage)})
  if($found.Count -ne 1){$bad.Add("missing_or_duplicate:$event/$stage");return $null};return $found[0]
 }
 $start=One 'owned_start'
 if(-not $start -or $start.atomic_job_assignment -ne $true -or $start.handle_inheritance -ne $false -or $start.pid -le 0 -or $start.creation_filetime -le 0){$bad.Add('invalid_owned_start')}
 foreach($stage in @('before_creation','alive_at_5s')){
  $v=One 'limits_readback' $stage
  if(-not $v -or $v.match -ne $true -or $v.flags -ne 8968 -or $v.active_limit -ne 1 -or $v.process_memory -ne 805306368 -or $v.job_memory -ne 805306368){$bad.Add("limits:$stage")}
 }
 if(@($Rows|Where-Object event -eq 'limits_readback').Count -ne 2){$bad.Add('unexpected_limit_rows')}
 $stages=@('empty_before_creation','suspended_child','alive_at_5s')
 if($Case -eq 'deadline'){$stages+= 'after_stop'}
 if(@($Rows|Where-Object event -eq 'job_snapshot').Count -ne $stages.Count){$bad.Add('unexpected_snapshot_count')}
 foreach($stage in $stages){
  $s=One 'job_snapshot' $stage
  if(-not $s -or $s.pid_query_error -ne 0 -or $null -ne $s.pid_parse_error){$bad.Add("snapshot_unknown:$stage");continue}
  $want=if($stage -in @('suspended_child','alive_at_5s')){1}else{0}
  if($s.active -ne $want -or @($s.members).Count -ne $want -or $s.terminated -ne 0){$bad.Add("member_count:$stage")}
  try{
   $raw=[Convert]::FromBase64String($s.pid_buffer_base64)
   if($raw.Length -ne 136 -or $s.pid_returned_bytes -ne (8+8*$want) -or
      [BitConverter]::ToUInt32($raw,0) -ne $want -or [BitConverter]::ToUInt32($raw,4) -ne $want){throw 'Raw PID count mismatch'}
   for($i=0;$i -lt $want;$i++){if([BitConverter]::ToUInt64($raw,8+8*$i) -ne $s.members[$i].pid){throw 'Raw PID identity mismatch'}}
  }catch{$bad.Add("raw_pid_binding:$stage")}
  $total=if($stage -eq 'empty_before_creation'){0}else{1}
  if($s.total -ne $total){$bad.Add("unexpected_lifetime_member:$stage")}
  foreach($member in @($s.members)){
   if($member.pid -ne $start.pid -or $member.creation_filetime -ne $start.creation_filetime -or $member.job_membership -ne $true -or
      $member.wait -ne 258 -or $member.image_error -ne 0 -or $member.image -ine 'D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3\ucrt64\bin\qemu-system-x86_64.exe'){$bad.Add("member_identity:$stage")}
  }
 }
 $alive=One 'alive_at_5s'
 if(-not $alive -or $alive.active_job_processes -ne 1){$bad.Add('five_second_count')}
 $stopMs=$null;$observedMs=$null
 if($Case -eq 'deadline'){
  if($GuardExit -ne 0 -or $ChildWait -ne 0){$bad.Add('deadline_exit')}
  $c=One 'cleanup';$t=One 'stop_timing'
  if(-not $c -or $c.cleanup_proven -ne $true -or $c.active_job_processes -ne 0 -or $c.wait -ne 0 -or $c.final_wait -ne 0 -or $c.exit_code -ne 777 -or $c.terminate_error -ne 0){$bad.Add('cleanup')}
  if(-not $t -or $t.started_tick_ms -ne $start.started_tick_ms){$bad.Add('timing_binding')}else{
   $stopMs=$t.stop_tick_ms-$t.started_tick_ms;$observedMs=$t.observed_tick_ms-$t.started_tick_ms
   if($stopMs -lt 14500 -or $stopMs -gt 15000 -or $observedMs -lt $stopMs -or $observedMs -gt 15000){$bad.Add('fifteen_second_ceiling')}
  }
 }else{
  if($GuardExit -ne 86 -or $ChildWait -ne 0){$bad.Add('abrupt_exit_or_child_not_exited')}
  $exit=One 'about_to_exit_guard'
  if(-not $exit -or $exit.cleanup_proven -ne $false){$bad.Add('missing_abrupt_marker')}
  if(@($Rows|Where-Object event -eq 'cleanup').Count -ne 0){$bad.Add('unexpected_graceful_cleanup')}
 }
 [pscustomobject]@{case=$Case;scoped_probe_pass=($bad.Count -eq 0);failures=$bad.ToArray();stop_requested_ms=$stopMs;cleanup_observed_ms=$observedMs;
   guard_exit=$GuardExit;child_wait=$ChildWait;formal_admission='BLOCKED';proves_guest_boot=$false;proves_I1_I6_closure=$false}
}
