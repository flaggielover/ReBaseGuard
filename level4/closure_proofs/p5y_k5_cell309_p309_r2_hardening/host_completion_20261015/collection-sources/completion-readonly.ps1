param([Parameter(Mandatory=$true)][string]$RecordDir)
$ErrorActionPreference='Stop'
$rows=[Collections.Generic.List[object]]::new()
function Query([string]$Id,[scriptblock]$Body){
 $r=[ordered]@{id=$Id;utc=[DateTime]::UtcNow.ToString('o');command=$Body.ToString();scope='READ_ONLY_METADATA_NO_SAMPLING'}
 try{$r.result=& $Body;$r.status='OBSERVED'}catch{$r.status='UNKNOWN_OR_DENIED';$r.error_type=$_.Exception.GetType().FullName;$r.hresult=$_.Exception.HResult}
 $rows.Add($r)
}
Query 'power_policy' { & "$env:SystemRoot\System32\powercfg.exe" /query SCHEME_CURRENT SUB_SLEEP; if($LASTEXITCODE -ne 0){throw 'powercfg read failed'} }
Query 'power_availability' { & "$env:SystemRoot\System32\powercfg.exe" /a; if($LASTEXITCODE -ne 0){throw 'powercfg /a failed'} }
Query 'pending_reboot' {
 $session=Get-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager'
 @{windows_update=(Test-Path -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired');component_servicing=(Test-Path -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending');pending_file_renames=[bool]$session.PendingFileRenameOperations;other_indicators='NOT_EXHAUSTIVE'}
}
Query 'update_policy_selected_values' {
 foreach($path in @('HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate','HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU','HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings')){
  if(!(Test-Path -LiteralPath $path)){@{path=$path;status='NOT_CONFIGURED'};continue}
  $v=Get-ItemProperty -LiteralPath $path
  $selected=[ordered]@{path=$path;status='SELECTED_VALUES_ONLY'}
  foreach($n in @('NoAutoUpdate','AUOptions','NoAutoRebootWithLoggedOnUsers','SetActiveHours','ActiveHoursStart','ActiveHoursEnd','PauseUpdatesExpiryTime','PauseQualityUpdatesEndTime','PauseFeatureUpdatesEndTime')){if($null -ne $v.$n){$selected[$n]=$v.$n}}
  $selected
 }
}
Query 'exact_collisions' {
 @{paths=@('C:\Program Files\ReBaseGuard-P309','C:\ProgramData\ReBaseGuard-P309','D:\ReBaseGuard-309\WSL\ReBaseGuard-P309') | ForEach-Object {@{path=$_;exists=(Test-Path -LiteralPath $_)}};service=@(Get-Service -Name ReBaseGuardP309Observer -ErrorAction SilentlyContinue | Select-Object Name,Status,StartType);distro=@(Get-ChildItem -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' | Get-ItemProperty | Where-Object DistributionName -eq ReBaseGuard-P309 | Select-Object DistributionName,Version);key_collision='NOT_QUERIED'}
}
Query 'build_tool_metadata' {
 @('C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe','C:\Program Files\dotnet\dotnet.exe') | ForEach-Object {if(Test-Path -LiteralPath $_){$f=Get-Item -LiteralPath $_;@{path=$_;version=$f.VersionInfo.FileVersion;exists=$true}}else{@{path=$_;exists=$false}}}
}
$rows | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $RecordDir 'windows-policy-and-build-metadata.json')
