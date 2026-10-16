$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$build='C:\Users\Lenovo\P309-I2-build-20261016-v4'
$repo='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v2'
if([IO.Directory]::Exists($build)){throw 'new private build path collision'}
$id=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner build only'}
$profile=[IO.DirectoryInfo]::new('C:\Users\Lenovo')
$profileAcl=$profile.GetAccessControl()
$profileExpected='O:SYG:SYD:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;S-1-5-21-1923243488-1610499346-3556306727-1001)(A;;0x100020;;;S-1-15-3-65536-599108337-2355189375-1353122160-3480128286-3345335107-485756383-4087318168-230526575)'
if($profileAcl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access') -cne $profileExpected){throw 'profile parent custody differs'}
foreach($p in @('C:\','C:\Users','C:\Users\Lenovo')){if(([IO.File]::GetAttributes($p) -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'reparse build parent'}}
$acl=[Security.AccessControl.DirectorySecurity]::new()
$acl.SetAccessRuleProtection($true,$false);$acl.SetOwner($id.User)
foreach($sid in @($id.User,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'),[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))){
 $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl',[Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit','None','Allow'))
}
$dir=[IO.Directory]::CreateDirectory($build,$acl)
$got=$dir.GetAccessControl()
if($got.GetOwner([Security.Principal.SecurityIdentifier]).Value -cne $id.User.Value -or -not $got.AreAccessRulesProtected -or
 $got.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access) -cne $acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)){throw 'new private build ACL differs'}
function HashBytes([byte[]]$b){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($b)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
function HashFile([string]$p){HashBytes ([IO.File]::ReadAllBytes($p))}
function WriteNew([string]$name,[string]$value){$f=[IO.FileStream]::new((Join-Path $build $name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$b=[Text.UTF8Encoding]::new($false).GetBytes($value);$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()}}
$pins=[ordered]@{
 'EtwCapture.cs'='0edc8e3b3eb09108089c1c2691ee7fc2e988c1b306d06f8de1a53697862a82c2'
 'Run-I2Feasibility.ps1'='1afe5fb8f38bffe4549bc3f85ee8dd31047a0815f0c06fc36d811d2cd4c1516c'
 'Trusted-Entry.template.ps1'='56658bf7349f80138e62af8f4c2bee372cc97eaf69467df22eca5db255193fb7'
 'NativeEntry.c'='467a9323a88771140540e78b273b04765a1c347d89b082922ee8226fa1a76b61'
 'Launch-Approved.ps1'='674739d438217d5e2bc3ea2ac482a9afd18bfdb12640038a8035843b75691349'
 'TestNativeEntry.c'='ef8cc3d910e195cdd6dcabd42f881161a4ff3c4270f1577fcb0c9ffbc417d576'
}
$inputBytes=@{}
foreach($name in $pins.Keys){$b=[IO.File]::ReadAllBytes((Join-Path $repo $name));if((HashBytes $b) -cne $pins[$name]){throw "reviewed input differs: $name"};$inputBytes[$name]=$b}
$tool='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64'
$sdk='C:\Program Files (x86)\Windows Kits\10'
$commands=[Collections.Generic.List[object]]::new()
function Tool([string]$exe,[string[]]$arguments,[string]$label){
 $si=[Diagnostics.ProcessStartInfo]::new();$si.FileName=$exe;$si.Arguments=($arguments|ForEach-Object {'"'+$_+'"'}) -join ' '
 $si.WorkingDirectory=$build;$si.UseShellExecute=$false;$si.CreateNoWindow=$true;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true
 $si.EnvironmentVariables.Clear();$si.EnvironmentVariables['SystemRoot']='C:\Windows';$si.EnvironmentVariables['WINDIR']='C:\Windows'
 $si.EnvironmentVariables['PATH']=$sdk+'\bin\10.0.26100.0\x64;C:\Windows\System32';$si.EnvironmentVariables['TEMP']=$build;$si.EnvironmentVariables['TMP']=$build
 $before=HashFile $exe;$p=[Diagnostics.Process]::Start($si);$o=$p.StandardOutput.ReadToEndAsync();$e=$p.StandardError.ReadToEndAsync()
 if(-not $p.WaitForExit(60000)){throw "build tool timeout: $label"}
 WriteNew ($label+'.stdout.txt') $o.Result;WriteNew ($label+'.stderr.txt') $e.Result
 $commands.Add([ordered]@{tool=$exe;tool_sha256=$before;arguments=$arguments;exit_code=$p.ExitCode;environment='FIVE_FIXED_PROCESS_VARIABLES;NO_GLOBAL_CHANGE'})
 if($p.ExitCode -ne 0){throw "build tool failed: $label"}
}
$held=[Collections.Generic.List[IO.FileStream]]::new()
function Seal([string]$name){$held.Add([IO.FileStream]::new((Join-Path $build $name),[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read))}
try{
 WriteNew 'EtwCapture.cs' ([Text.Encoding]::UTF8.GetString($inputBytes['EtwCapture.cs']));Seal 'EtwCapture.cs'
 Tool 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe' @('/nologo','/platform:x64','/target:exe','/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Web.Extensions.dll',('/out:'+$build+'\EtwCapture-v2.exe'),($build+'\EtwCapture.cs')) 'etw-compile'
 Seal 'EtwCapture-v2.exe'
 $etwHash=HashFile (Join-Path $build 'EtwCapture-v2.exe')
 Tool (Join-Path $build 'EtwCapture-v2.exe') @('--layout-check') 'etw-layout-memory-only'
 $h=[Text.Encoding]::UTF8.GetString($inputBytes['Run-I2Feasibility.ps1'])
 $h=$h.Replace('D:\ReBaseGuard-309\records\p309-local-control-package-preparation-20261016-01\i2-repair-v2\EtwCapture-v2.exe',$build+'\EtwCapture-v2.exe').Replace('416700022cb57e76e54735c8486a8bd2b90663966727c28af27fc9830d8114ad',$etwHash)
 WriteNew 'Run-I2Feasibility.ps1' $h;Seal 'Run-I2Feasibility.ps1'
 $hHash=HashFile (Join-Path $build 'Run-I2Feasibility.ps1')
 $t=[Text.Encoding]::UTF8.GetString($inputBytes['Trusted-Entry.template.ps1'])
 $t=$t.Replace($repo+'\Run-I2Feasibility.ps1',$build+'\Run-I2Feasibility.ps1').Replace($pins['Run-I2Feasibility.ps1'],$hHash)
 WriteNew 'Trusted-Entry.template.ps1' $t;Seal 'Trusted-Entry.template.ps1'
 $tHash=HashFile (Join-Path $build 'Trusted-Entry.template.ps1')
 $n=[Text.Encoding]::UTF8.GetString($inputBytes['NativeEntry.c'])
 $n=$n.Replace(($repo+'\Trusted-Entry.template.ps1').Replace('\','\\'),($build+'\Trusted-Entry.template.ps1').Replace('\','\\')).Replace($pins['Trusted-Entry.template.ps1'],$tHash)
 WriteNew 'NativeEntry.c' $n;Seal 'NativeEntry.c'
 $compile=@('/nologo','/c','/GS-','/O1','/Oi-','/Zl','/D_WIN32_WINNT=0x0602','/IC:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\include',('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'))
 Tool (Join-Path $tool 'cl.exe') ($compile+@('/FoNativeEntry.obj','NativeEntry.c')) 'native-compile'
 Seal 'NativeEntry.obj'
 $link=@('/NOLOGO','/NODEFAULTLIB','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',($sdk+'\Lib\10.0.26100.0\um\x64\kernel32.lib'))
 Tool (Join-Path $tool 'link.exe') ($link+@('/ENTRY:Entry',"/MANIFESTUAC:level='requireAdministrator' uiAccess='false'",'/OUT:NativeEntry.exe','NativeEntry.obj')) 'native-link'
 Seal 'NativeEntry.exe';$nativeHash=HashFile (Join-Path $build 'NativeEntry.exe')
 Tool (Join-Path $tool 'dumpbin.exe') @('/headers','/imports','NativeEntry.exe') 'native-pe-inspection'
 Tool (Join-Path $sdk 'bin\10.0.26100.0\x64\mt.exe') @('-nologo','-inputresource:NativeEntry.exe;#1','-out:embedded-manifest.xml') 'native-manifest-inspection'
 $l=[Text.Encoding]::UTF8.GetString($inputBytes['Launch-Approved.ps1'])
 $l=$l.Replace('D:\ReBaseGuard-309\records\p309-local-control-package-preparation-20261016-01\i2-native-entry-v3-b4\NativeEntry.exe',$build+'\NativeEntry.exe').Replace('85b57ba5d51b06761cd5e686fb9f6c5c64a8a21a508f186df047d501c4afeb6c',$nativeHash)
 WriteNew 'Launch-Approved.ps1' $l;Seal 'Launch-Approved.ps1'
 WriteNew 'TestNativeEntry.c' ([Text.Encoding]::UTF8.GetString($inputBytes['TestNativeEntry.c']));Seal 'TestNativeEntry.c'
 Tool (Join-Path $tool 'cl.exe') ($compile+@('/FoTestNativeEntry.obj','TestNativeEntry.c')) 'unit-compile';Seal 'TestNativeEntry.obj'
 Tool (Join-Path $tool 'link.exe') ($link+@('/ENTRY:TestEntry',"/MANIFESTUAC:level='asInvoker' uiAccess='false'",'/OUT:TestNativeEntry.exe','TestNativeEntry.obj')) 'unit-link';Seal 'TestNativeEntry.exe'
 Tool (Join-Path $build 'TestNativeEntry.exe') @() 'unit-ten-known-answers'
 $parse=@()
 foreach($name in @('Launch-Approved.ps1','Run-I2Feasibility.ps1','Trusted-Entry.template.ps1')){
  $tokens=$null;$errors=$null;$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $build $name),[ref]$tokens,[ref]$errors)
  if($errors.Count){throw 'parse failed'};$parse+=[ordered]@{file=$name;sha256=(HashFile (Join-Path $build $name));parse_errors=0}
 }
 $readOnly=& ([ScriptBlock]::Create($l)) -ReadOnlyPreflight
 WriteNew 'readonly-entry-pin-result.json' ($readOnly -join [Environment]::NewLine)
 $record=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');scope='ORDINARY_OWNER_PRIVATE_BUILD_NO_DEPLOYMENT';owner=$id.User.Value;build_root=$build;root_sddl=$got.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access');profile_sddl=$profileExpected;reviewed_input_revision='9e9e59a7dd0be518231c6c92c4ae14dcd329c6d6';reviewed_input_pins=$pins;inputs_locked_until_all_build_commands_exit=$true;objects_locked_before_link=$true;outputs_stay_private=$true;commands=@($commands.ToArray());winps=$PSVersionTable.PSVersion.ToString();parse=$parse;etw_sha256=$etwHash;native_entry_sha256=$nativeHash;codec_digest_checks=10;native_production_entry_executions=0;trace_count=0;uac_count=0;fixture_count=0;job_count=0;admission='BLOCKED'}
 WriteNew 'PRIVATE_BUILD_CUSTODY.json' ($record | ConvertTo-Json -Depth 10)
 $files=foreach($f in $dir.GetFiles()){[ordered]@{name=$f.Name;size=$f.Length;sha256=(HashFile $f.FullName)}}
 WriteNew 'SHA256SUMS.json' ($files | ConvertTo-Json -Depth 6)
 [ordered]@{build_root=$build;etw_sha256=$etwHash;native_entry_sha256=$nativeHash;checks=10;uac=0;trace=0} | ConvertTo-Json
}finally{foreach($f in $held){$f.Dispose()}}
