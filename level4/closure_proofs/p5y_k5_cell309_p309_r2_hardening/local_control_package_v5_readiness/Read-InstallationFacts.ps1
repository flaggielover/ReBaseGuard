param([Parameter(Mandatory=$true)][byte[]]$ApprovalBytes,[Parameter(Mandatory=$true)][string]$VerifiedHarnessSha256)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
$root='C:\ProgramData\ReBaseGuardP309-InstallationFacts-v1'
$approval=[Text.Encoding]::UTF8.GetString($ApprovalBytes)|ConvertFrom-Json
if($approval.scope -cne 'P309_SINGLE_ELEVATED_READONLY_INSTALLATION_FACTS_V1' -or $approval.count -ne 1 -or $approval.harness_sha256 -cne $VerifiedHarnessSha256 -or [string]::IsNullOrWhiteSpace($approval.human_message_reference)){throw 'approval scope/binding refused'}
if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1){throw 'WinPS5.1 required'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(-not ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'approved elevated entry required'}
if([IO.Directory]::Exists($root)-or[IO.File]::Exists($root)){throw 'fresh evidence root required'}
if(([IO.DriveInfo]::new('C')).AvailableFreeSpace -lt 536870912){throw 'evidence reserve unavailable'}
$expected=@{
 'C:\'='O:S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464G:S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464D:PAI(A;;LC;;;AU)(A;OICIIO;SDGXGWGR;;;AU)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;0x1200a9;;;BU)(A;;0x1000a1;;;S-1-15-3-65536-1888954469-739942743-1668119174-2468466756-4239452838-1296943325-355587736-700089176)'
 'C:\ProgramData'='O:SYG:SYD:PAI(A;OICIIO;GA;;;CO)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;0x1200a9;;;BU)(A;CI;DCLCRPCR;;;BU)'
}
foreach($p in $expected.Keys){if(([IO.File]::GetAttributes($p)-band[IO.FileAttributes]::ReparsePoint)-ne 0 -or ([IO.DirectoryInfo]::new($p)).GetAccessControl().GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access') -cne $expected[$p]){throw 'parent custody differs'}}
$acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetAccessRuleProtection($true,$false)
$admins=[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544');$acl.SetOwner($admins)
foreach($sid in @($admins,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'))){$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))}
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($identity.User,'ReadAndExecute','ContainerInherit,ObjectInherit','None','Allow'))
$dir=[IO.Directory]::CreateDirectory($root,$acl);$actual=$dir.GetAccessControl()
if(($dir.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0 -or $actual.GetOwner([Security.Principal.SecurityIdentifier]).Value -cne $admins.Value -or $actual.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access) -cne $acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)){throw 'new root security differs'}
function WriteNew([string]$Name,[byte[]]$Bytes){if($Bytes.Length -gt 1048576){throw 'evidence item too large'};$f=[IO.FileStream]::new((Join-Path $root $Name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}}
function SaveJson([string]$Name,$Value){WriteNew $Name ([Text.Encoding]::UTF8.GetBytes(($Value|ConvertTo-Json -Depth 12)))}
WriteNew 'approval-used.json' $ApprovalBytes
$env:TEMP=$root;$env:TMP=$root
$results=[Collections.Generic.List[object]]::new()
function Observe([string]$Name,[scriptblock]$Read){
 try{$value=& $Read;$item=[ordered]@{name=$Name;utc=[DateTime]::UtcNow.ToString('o');query_status='RETURNED_REQUIRES_INTERPRETATION';value=$value;admission='BLOCKED'}}
 catch{$item=[ordered]@{name=$Name;utc=[DateTime]::UtcNow.ToString('o');query_status='UNKNOWN';error=$_.Exception.Message;admission='BLOCKED'}}
 SaveJson ($Name+'.json') $item;$results.Add($item)
}
$native=@'
using System;using System.Runtime.InteropServices;using System.Security.AccessControl;using System.Security.Principal;
public static class P309InstallationRead {
 [DllImport("C:\\Windows\\System32\\advapi32.dll",ExactSpelling=true)] static extern uint EventAccessQuery(ref Guid guid,IntPtr buffer,ref uint size);
 [StructLayout(LayoutKind.Sequential)] struct OA {public uint Length;public IntPtr Root,Name;public uint Attributes;public IntPtr Security,Qos;}
 [StructLayout(LayoutKind.Sequential)] struct US {public ushort Length,MaximumLength;public IntPtr Buffer;}
 [DllImport("C:\\Windows\\System32\\advapi32.dll",ExactSpelling=true)] static extern uint LsaOpenPolicy(IntPtr system,ref OA attrs,uint access,out IntPtr policy);
 [DllImport("C:\\Windows\\System32\\advapi32.dll",ExactSpelling=true)] static extern uint LsaEnumerateAccountRights(IntPtr policy,IntPtr sid,out IntPtr rights,out uint count);
 [DllImport("C:\\Windows\\System32\\advapi32.dll",ExactSpelling=true)] static extern uint LsaNtStatusToWinError(uint status);
 [DllImport("C:\\Windows\\System32\\advapi32.dll",ExactSpelling=true)] static extern uint LsaClose(IntPtr policy);
 [DllImport("C:\\Windows\\System32\\advapi32.dll",ExactSpelling=true)] static extern uint LsaFreeMemory(IntPtr memory);
 public sealed class SecurityResult {public string guid,sddl,error;public uint first_rc,final_rc,size;public string descriptor_base64;}
 public static SecurityResult Etw(string text){Guid g=Guid.Parse(text);uint n=0;var r=new SecurityResult();r.guid=text;r.first_rc=EventAccessQuery(ref g,IntPtr.Zero,ref n);r.final_rc=r.first_rc;r.size=n;
  if(r.first_rc!=122||n==0||n>65536){r.error="Unavailable; not empty/default authority";return r;}IntPtr p=Marshal.AllocHGlobal((int)n);
  try{uint cap=n;r.final_rc=EventAccessQuery(ref g,p,ref n);r.size=n;if(r.final_rc!=0||n>cap){r.error="Failed/changed size; no retry";return r;}byte[] b=new byte[n];Marshal.Copy(p,b,0,(int)n);r.sddl=new RawSecurityDescriptor(b,0).GetSddlForm(AccessControlSections.All);r.descriptor_base64=Convert.ToBase64String(b);return r;}finally{Marshal.FreeHGlobal(p);}}
 public sealed class RightsResult {public string sid;public uint open_rc,query_rc,close_rc,free_rc;public string[] rights;}
 public static RightsResult Rights(string text){var r=new RightsResult();r.sid=text;var oa=new OA();oa.Length=(uint)Marshal.SizeOf(typeof(OA));IntPtr handle=IntPtr.Zero;uint status=LsaOpenPolicy(IntPtr.Zero,ref oa,0x801,out handle);r.open_rc=LsaNtStatusToWinError(status);if(status!=0)return r;if(handle==IntPtr.Zero)throw new Exception("invalid successful policy handle");
  try{var sid=new SecurityIdentifier(text);byte[] b=new byte[sid.BinaryLength];sid.GetBinaryForm(b,0);IntPtr p=Marshal.AllocHGlobal(b.Length);try{Marshal.Copy(b,0,p,b.Length);IntPtr rights=IntPtr.Zero;uint count=0;status=LsaEnumerateAccountRights(handle,p,out rights,out count);r.query_rc=LsaNtStatusToWinError(status);if(status!=0)return r;
    try{if(count>256||(count>0&&rights==IntPtr.Zero))throw new Exception("invalid rights response");r.rights=new string[count];for(int i=0;i<count;i++){US s=(US)Marshal.PtrToStructure(IntPtr.Add(rights,i*Marshal.SizeOf(typeof(US))),typeof(US));if(s.Length>s.MaximumLength||(s.Length%2)!=0||s.Buffer==IntPtr.Zero)throw new Exception("invalid rights string");r.rights[i]=Marshal.PtrToStringUni(s.Buffer,s.Length/2);}}
    finally{if(rights!=IntPtr.Zero)r.free_rc=LsaNtStatusToWinError(LsaFreeMemory(rights));}return r;
   }finally{Marshal.FreeHGlobal(p);}}
  finally{r.close_rc=LsaNtStatusToWinError(LsaClose(handle));}}
}
'@
Add-Type -TypeDefinition $native
Observe 'etw-security' { @([P309InstallationRead]::Etw('9e814aad-3204-11d2-9a82-006008a86939'),[P309InstallationRead]::Etw('b47309d4-5e53-4a10-a67a-202610160001')) }
$sids=@('S-1-5-80-1932864767-2148301307-763792368-432637623-2158176663','S-1-5-80-1389429364-2543163971-322551805-3183066981-1946276422','S-1-5-80-2549398394-424828454-1189152689-2921672270-2793605460')
Observe 'proposed-service-rights' { @($sids|ForEach-Object {[P309InstallationRead]::Rights($_)}) }
Observe 'etw-registry-presence' {
 $key=[Microsoft.Win32.Registry]::LocalMachine.OpenSubKey('SYSTEM\CurrentControlSet\Control\WMI\Security',$false)
 try {
  if($null -eq $key){throw 'security registry unavailable'}
  foreach($guid in @('9e814aad-3204-11d2-9a82-006008a86939','b47309d4-5e53-4a10-a67a-202610160001')) {
   foreach($name in @(('{' + $guid + '}'),$guid)) {
    $v=$key.GetValue($name,$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
    @{name=$name;present=$null -ne $v;kind=$(if($null -ne $v){[string]$key.GetValueKind($name)}else{$null});binary_base64=$(if($v -is [byte[]]){[Convert]::ToBase64String($v)}else{$null})}
   }
  }
 } finally {if($null -ne $key){$key.Dispose()}}
}
Observe 'service-collisions' {$all=@(Get-Service -ErrorAction Stop);@('ReBaseGuardP309Observer','ReBaseGuardP309Controller','ReBaseGuardP309Relay')|ForEach-Object{$name=$_;$found=@($all|Where-Object {$_.Name -ceq $name});@{name=$name;exists=$found.Count -ne 0;status=@($found|ForEach-Object {[string]$_.Status})}}}
Observe 'directory-custody' {@('C:\Program Files','C:\ProgramData','D:\','D:\ReBaseGuard-309')|ForEach-Object{@{path=$_;attributes=[string][IO.File]::GetAttributes($_);sddl=([IO.DirectoryInfo]::new($_)).GetAccessControl().GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access')}}}
Observe 'space-and-collisions' {@{C_available=[IO.DriveInfo]::new('C').AvailableFreeSpace;D_available=[IO.DriveInfo]::new('D').AvailableFreeSpace;D_format=[IO.DriveInfo]::new('D').DriveFormat;proposed_code_exists=([IO.Directory]::Exists('C:\Program Files\ReBaseGuardP309') -or [IO.File]::Exists('C:\Program Files\ReBaseGuardP309'));proposed_state_exists=([IO.Directory]::Exists('C:\ProgramData\ReBaseGuardP309') -or [IO.File]::Exists('C:\ProgramData\ReBaseGuardP309'));proposed_disk_exists=([IO.Directory]::Exists('D:\ReBaseGuardP309Private') -or [IO.File]::Exists('D:\ReBaseGuardP309Private'))}}
Observe 'power-sleep-policy' {& 'C:\Windows\System32\powercfg.exe' /query SCHEME_CURRENT SUB_SLEEP;if($LASTEXITCODE-ne 0){throw 'powercfg query failed'}}
Observe 'update-policy' {
 @('SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate','SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU','SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired','SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending')|ForEach-Object {
  $path=$_;$k=[Microsoft.Win32.Registry]::LocalMachine.OpenSubKey($path,$false);try{$values=@();if($null-ne$k){foreach($n in @('NoAutoUpdate','AUOptions','AlwaysAutoRebootAtScheduledTime','NoAutoRebootWithLoggedOnUsers','ScheduledInstallDay','ScheduledInstallTime','SetActiveHours','ActiveHoursStart','ActiveHoursEnd')){$v=$k.GetValue($n,$null,[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames);if($null-ne$v){$values+=@{name=$n;value=$v;kind=[string]$k.GetValueKind($n)}}}};@{path=$path;exists=$null-ne$k;selected_values=$values;absence_is_not_no_maintenance=$true}}finally{if($null-ne$k){$k.Dispose()}}
 }
}
Observe 'device-guard-metadata' {Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\CimCmdlets\CimCmdlets.psd1' -ErrorAction Stop;Get-CimInstance -Namespace root\Microsoft\Windows\DeviceGuard -ClassName Win32_DeviceGuard -OperationTimeoutSec 20|Select-Object VirtualizationBasedSecurityStatus,SecurityServicesConfigured,SecurityServicesRunning,AvailableSecurityProperties,RequiredSecurityProperties}
Observe 'maintenance-task-metadata' {Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\ScheduledTasks\ScheduledTasks.psd1' -ErrorAction Stop;@(Get-ScheduledTask -TaskPath '\Microsoft\Windows\UpdateOrchestrator\','\Microsoft\Windows\WindowsUpdate\' -ErrorAction Stop|Select-Object TaskPath,TaskName,State,@{Name='Enabled';Expression={$_.Settings.Enabled}},@{Name='WakeToRun';Expression={$_.Settings.WakeToRun}})}
SaveJson 'RESULT.json' @{utc=[DateTime]::UtcNow.ToString('o');scope='ADMINISTRATOR_READONLY_INSTALLATION_FACTS';queries=$results.Count;unknown=@($results|Where-Object {$_.query_status-eq'UNKNOWN'}|ForEach-Object {$_.name});policy_changes=0;trace_starts=0;vm_starts=0;services_created=0;keys_created=0;formal_coverage_proven=$false;admission='BLOCKED';I1_I7='OPEN'}
$manifest=@(Get-ChildItem -LiteralPath $root -File|Where-Object {$_.Extension -eq '.json'}|ForEach-Object{@{file=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
SaveJson 'SHA256SUMS.json' $manifest
