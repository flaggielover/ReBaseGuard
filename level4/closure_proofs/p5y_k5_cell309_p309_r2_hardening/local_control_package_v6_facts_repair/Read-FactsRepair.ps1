param([switch]$LibraryOnly,[byte[]]$ApprovalBytes,[string]$VerifiedHarnessSha256,[byte[]]$CoreBytes)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest

# These helpers accept supplied values only. LibraryOnly does not query the host.
function Get-FactsSummary([string[]]$ExpectedIds,[object[]]$Items){
 $seen=@{};$unknown=[Collections.Generic.List[string]]::new();$cleanup=[Collections.Generic.List[object]]::new();$stages=[Collections.Generic.List[object]]::new()
 foreach($item in $Items){
  if($seen.ContainsKey($item.id)){throw 'duplicate observation id'};$seen[$item.id]=$true
  if($item.state -eq 'UNKNOWN' -or $item.state -eq 'NOT_FOUND_DIRECT_RIGHTS_NOT_ENUMERATED'){$unknown.Add($item.id)}
  if($item.state -notin @('UNKNOWN','NOT_FOUND_DIRECT_RIGHTS_NOT_ENUMERATED','OBSERVED','PRESENT','ABSENT')){throw 'unrecognized observation state'}
  foreach($e in $item.cleanup_errors){$cleanup.Add(@{id=$item.id;error=$e})}
  if($item.PSObject.Properties['data'] -and $item.data.Contains('native') -and $item.data.native.PSObject.Properties['NotAttempted']){foreach($stage in $item.data.native.NotAttempted){$stages.Add(@{id=$item.id;stage=$stage})}}
 }
 $unexpected=@($seen.Keys|Where-Object {$_ -notin $ExpectedIds})
 if($unexpected.Count){throw 'unexpected observation id'}
 $missing=@($ExpectedIds|Where-Object {-not $seen.ContainsKey($_)})
 [ordered]@{expected_items=$ExpectedIds.Count;completed_items=$Items.Count;unknown_items=$unknown.ToArray();not_attempted_items=$missing;native_not_attempted_stages=$stages.ToArray();cleanup_errors=$cleanup.ToArray();evidence_set_complete=($missing.Count-eq 0);installation_ready=$false;formal_admission='BLOCKED';I1_I7='OPEN'}
}
function Get-RecordedPathState([int]$HResult){if($HResult -in @(-2147024894,-2147024893)){'ABSENT'}else{'UNKNOWN'}}
function Get-ExpectedFactIds{@('etw-0','etw-1','lsa-0','lsa-1','lsa-2','etw-registry-0-0','etw-registry-0-1','etw-registry-1-0','etw-registry-1-1','service-0','service-1','service-2','directory-0','directory-1','directory-2','directory-3','space','path-0','path-1','path-2','power','update-0','update-1','update-2','update-3','device-guard','maintenance-0','maintenance-1')}
function Receive-PartialFact([Collections.IDictionary]$Data,[string]$Key,[scriptblock]$Producer){
 $Data[$Key]=[Collections.Generic.List[object]]::new();$Data[$Key+'_complete']=$false
 & $Producer|ForEach-Object {$Data[$Key].Add($_)}
 $Data[$Key+'_complete']=$true
}
function Invoke-FactObservation([string]$Id,[scriptblock]$Read){
 $data=[ordered]@{};$state='OBSERVED';$errorText=$null;$cleanup=@()
 try{
  $native=& $Read $data
  if($null-ne$native){$data.native=$native;$state=$native.State;$cleanup=@($native.CleanupErrors)}
 }catch{$state='UNKNOWN';$errorText=$_.Exception.Message;$data.exception_hresult=$_.Exception.GetBaseException().HResult}
 [pscustomobject]@{id=$Id;utc=[DateTime]::UtcNow.ToString('o');state=$state;data=$data;error=$errorText;cleanup_errors=$cleanup;admission='BLOCKED'}
}
if($LibraryOnly){return}
if($PSVersionTable.PSVersion.Major-ne 5-or$PSVersionTable.PSVersion.Minor-ne 1){throw 'WinPS 5.1 required'}
function HashBytes([byte[]]$Bytes){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
if($null-eq$CoreBytes-or(HashBytes $CoreBytes)-cne'__CORE_SHA256__'){throw 'core bytes differ'}
$approval=[Text.Encoding]::UTF8.GetString($ApprovalBytes)|ConvertFrom-Json
if($approval.scope-cne'P309_SINGLE_ELEVATED_READONLY_FACTS_REPAIR_V1'-or$approval.count-ne 1-or$approval.harness_sha256-cne$VerifiedHarnessSha256-or$approval.core_sha256-cne'__CORE_SHA256__'-or[string]::IsNullOrWhiteSpace($approval.human_message_reference)){throw 'fresh approval binding refused'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(-not([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'approved elevated entry required'}
$root='C:\ProgramData\ReBaseGuardP309-FactsRepair-v1'
try{$null=[IO.File]::GetAttributes($root);$exists=$true}catch{$hr=$_.Exception.GetBaseException().HResult;if($hr-notin@(-2147024894,-2147024893)){throw};$exists=$false}
if($exists){throw 'fresh evidence root required; no adoption/retry'}
if(([IO.DriveInfo]::new('C')).AvailableFreeSpace-lt 536870912){throw '512 MiB evidence reserve unavailable'}
$parents=@{
 'C:\'='O:S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464G:S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464D:PAI(A;;LC;;;AU)(A;OICIIO;SDGXGWGR;;;AU)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;0x1200a9;;;BU)(A;;0x1000a1;;;S-1-15-3-65536-1888954469-739942743-1668119174-2468466756-4239452838-1296943325-355587736-700089176)'
 'C:\ProgramData'='O:SYG:SYD:PAI(A;OICIIO;GA;;;CO)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;0x1200a9;;;BU)(A;CI;DCLCRPCR;;;BU)'
}
foreach($p in $parents.Keys){if(([IO.File]::GetAttributes($p)-band[IO.FileAttributes]::ReparsePoint)-ne 0-or([IO.DirectoryInfo]::new($p)).GetAccessControl().GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access')-cne$parents[$p]){throw 'parent custody differs'}}
$acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetAccessRuleProtection($true,$false)
$admins=[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544');$acl.SetOwner($admins)
foreach($sid in @($admins,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'))){$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))}
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($identity.User,'ReadAndExecute','ContainerInherit,ObjectInherit','None','Allow'))
$dir=[IO.Directory]::CreateDirectory($root,$acl);$actual=$dir.GetAccessControl()
if(($dir.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0-or-not$actual.AreAccessRulesProtected-or$actual.GetOwner([Security.Principal.SecurityIdentifier]).Value-cne$admins.Value-or$actual.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)-cne$acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)){throw 'new evidence root custody differs'}
function WriteNew([string]$Name,[byte[]]$Bytes){if($Bytes.Length-gt 2097152){throw 'evidence item too large'};$f=[IO.FileStream]::new((Join-Path $root $Name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}}
function SaveJson([string]$Name,$Value){WriteNew $Name ([Text.Encoding]::UTF8.GetBytes(($Value|ConvertTo-Json -Depth 18)))}
WriteNew 'approval-used.json' $ApprovalBytes
$env:TEMP=$root;$env:TMP=$root
Add-Type -TypeDefinition ([Text.Encoding]::UTF8.GetString($CoreBytes))
$items=[Collections.Generic.List[object]]::new()
function Observe([string]$Id,[scriptblock]$Read){
 $item=Invoke-FactObservation $Id $Read
 SaveJson ($Id+'.json') $item;$items.Add($item)
}
$guids=@('9e814aad-3204-11d2-9a82-006008a86939','b47309d4-5e53-4a10-a67a-202610160001')
$sids=@('S-1-5-80-1932864767-2148301307-763792368-432637623-2158176663','S-1-5-80-1389429364-2543163971-322551805-3183066981-1946276422','S-1-5-80-2549398394-424828454-1189152689-2921672270-2793605460')
$services=@('ReBaseGuardP309Observer','ReBaseGuardP309Controller','ReBaseGuardP309Relay')
$expected=@(Get-ExpectedFactIds)
function RunFact([string]$Id,[scriptblock]$Read){if($Id-notin$expected){throw 'unexpected fixed fact'};Observe $Id $Read}
for($i=0;$i-lt$guids.Count;$i++){$g=$guids[$i];RunFact ('etw-'+$i) {param($d) [P309ReadinessV6.Core]::ReadEtw($g)}}
for($i=0;$i-lt$sids.Count;$i++){$s=$sids[$i];RunFact ('lsa-'+$i) {param($d) [P309ReadinessV6.Core]::ReadRights($s)}}
for($i=0;$i-lt$guids.Count;$i++){
 foreach($braced in @($false,$true)){
  $valueName=if($braced){'{'+$guids[$i]+'}'}else{$guids[$i]}
  RunFact ('etw-registry-'+$i+'-'+[int]$braced) {param($d)
   $d.name=$valueName;$key=[Microsoft.Win32.Registry]::LocalMachine.OpenSubKey('SYSTEM\CurrentControlSet\Control\WMI\Security',$false)
   try{
    if($null-eq$key){throw 'security registry key unavailable'}
    $present=$valueName -in $key.GetValueNames();$d.present=$present
    if($present){$d.kind=[string]$key.GetValueKind($valueName);$v=$key.GetValue($valueName,$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames);if($v-is[byte[]]){if($v.Length-gt 65536){throw 'registry bytes too large'};$d.binary_base64=[Convert]::ToBase64String($v);$d.sha256=HashBytes $v}else{$d.raw_value=$v}}
   }finally{if($null-ne$key){$key.Dispose()}}
  }
 }
}
for($i=0;$i-lt$services.Count;$i++){$service=$services[$i];RunFact ('service-'+$i) {param($d) [P309ReadinessV6.Core]::ReadService($service)}}
$paths=@('C:\Program Files','C:\ProgramData','D:\','D:\ReBaseGuard-309')
for($i=0;$i-lt$paths.Count;$i++){$path=$paths[$i];RunFact ('directory-'+$i) {param($d) $d.path=$path;$attrs=[IO.File]::GetAttributes($path);$d.attributes=[string]$attrs;$d.sddl=([IO.DirectoryInfo]::new($path)).GetAccessControl().GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access');if(($attrs-band[IO.FileAttributes]::ReparsePoint)-ne 0){throw 'reparse production custody unresolved'}}}
RunFact 'space' {param($d) $d.C_available=[IO.DriveInfo]::new('C').AvailableFreeSpace;$d.D_available=[IO.DriveInfo]::new('D').AvailableFreeSpace;$d.D_format=[IO.DriveInfo]::new('D').DriveFormat}
$proposed=@('C:\Program Files\ReBaseGuardP309','C:\ProgramData\ReBaseGuardP309','D:\ReBaseGuardP309Private')
for($i=0;$i-lt$proposed.Count;$i++){$path=$proposed[$i];RunFact ('path-'+$i) {param($d)
 $d.path=$path
 try{$d.attributes=[string][IO.File]::GetAttributes($path);[pscustomobject]@{State='PRESENT';CleanupErrors=@()}}
 catch{$d.hresult=$_.Exception.GetBaseException().HResult;$d.error_type=$_.Exception.GetBaseException().GetType().FullName;[pscustomobject]@{State=(Get-RecordedPathState $d.hresult);CleanupErrors=@()}}
}}
RunFact 'power' {param($d) [P309ReadinessV6.Core]::ReadPower()}
$updatePaths=@('SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate','SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU','SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired','SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending')
for($i=0;$i-lt$updatePaths.Count;$i++){$path=$updatePaths[$i];RunFact ('update-'+$i) {param($d)
 $d.path=$path;$key=[Microsoft.Win32.Registry]::LocalMachine.OpenSubKey($path,$false)
 try{$d.exists=$null-ne$key;$d.absence_is_not_no_maintenance=$true;$d.selected_values=@();if($null-ne$key){foreach($n in @('NoAutoUpdate','AUOptions','AlwaysAutoRebootAtScheduledTime','NoAutoRebootWithLoggedOnUsers','ScheduledInstallDay','ScheduledInstallTime','SetActiveHours','ActiveHoursStart','ActiveHoursEnd')){if($n -in $key.GetValueNames()){$d.selected_values+=@{name=$n;value=$key.GetValue($n,$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames);kind=[string]$key.GetValueKind($n)}}}}}finally{if($null-ne$key){$key.Dispose()}}
}}
RunFact 'device-guard' {param($d)
 Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\CimCmdlets\CimCmdlets.psd1' -ErrorAction Stop
 Receive-PartialFact $d 'metadata' {Get-CimInstance -Namespace root\Microsoft\Windows\DeviceGuard -ClassName Win32_DeviceGuard -OperationTimeoutSec 20|Select-Object VirtualizationBasedSecurityStatus,SecurityServicesConfigured,SecurityServicesRunning,AvailableSecurityProperties,RequiredSecurityProperties}
}
$taskPaths=@('\Microsoft\Windows\UpdateOrchestrator\','\Microsoft\Windows\WindowsUpdate\')
for($i=0;$i-lt$taskPaths.Count;$i++){$path=$taskPaths[$i];RunFact ('maintenance-'+$i) {param($d)
 $d.path=$path;Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\ScheduledTasks\ScheduledTasks.psd1' -ErrorAction Stop
 Receive-PartialFact $d 'selected_metadata' {Get-ScheduledTask -TaskPath $path -ErrorAction Stop|Select-Object TaskPath,TaskName,State,@{Name='Enabled';Expression={$_.Settings.Enabled}},@{Name='WakeToRun';Expression={$_.Settings.WakeToRun}}}
 $d.not_complete_schedule=$true
}}
$summary=Get-FactsSummary $expected $items.ToArray()
SaveJson 'RESULT.json' @{utc=[DateTime]::UtcNow.ToString('o');scope='ADMINISTRATOR_READONLY_FACTS_REPAIR';summary=$summary;configuration_changes=0;trace_starts=0;vm_starts=0;services_accounts_keys_created=0;P309_workloads=0;automatic_retry=$false;formal_coverage_proven=$false;admission='BLOCKED';I1_I7='OPEN'}
$manifest=@(Get-ChildItem -LiteralPath $root -File|Where-Object {$_.Extension-eq'.json'}|ForEach-Object{@{file=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
SaveJson 'SHA256SUMS.json' $manifest
