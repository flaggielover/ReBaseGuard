$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.Major -ne 5){throw 'Windows PowerShell 5.1 required'}
$build='C:\Users\Lenovo\P309-I2-root-build-20261016-v1'
$repo='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v3'
$sourceCommit='5eb6cbb6532d852dcf6c7f0e2686023ced64ef0a'
$pins=[ordered]@{
 'EtwCapture.cs'='844b2101b1fca769bf784aaf778b60cff32ffca4e6e051b9f4ff81d189feca37'
 'WhpCounterProbe.cpp'='4825afaa110c62b835a2eb7edfd2368b319183c707e6865a40fa558ce81f5b8a'
 'Run-I2Feasibility.ps1'='b588f8c575c90e891b34bc4dd22137f7bb64ec0e91ab096e669ba4cee4e5f30c'
 'Trusted-Entry.template.ps1'='7cf746b26343ef88f3296c8cb34bf6ca9b750890db14a86a014ef1b18d34a826'
 'NativeEntry.c'='61cca8c4bc864a7cbc65079eeda987f3b4854c4e5bc8b316f53ce3e94fea7dae'
 'Launch-Approved.ps1'='3efb4a5b927df90aa041da6643b6b49c3afcd116f317ccf721390d34134b14c0'
 'Test-FixtureAssessment.ps1'='65f8ea9612ca9873fc78c14119db2e28a44689012a644ae03c0928efef282891'
}
function HashBytes([byte[]]$b){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($b)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
function HashFile([string]$p){HashBytes ([IO.File]::ReadAllBytes($p))}
$inputBytes=@{}
foreach($n in $pins.Keys){$b=[IO.File]::ReadAllBytes((Join-Path $repo $n));if((HashBytes $b) -cne $pins[$n]){throw "input mismatch $n"};$inputBytes[$n]=$b}
$id=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner build only'}
if([IO.Directory]::Exists($build) -or [IO.File]::Exists($build)){throw 'fresh private build required'}
$profileExpected='O:SYG:SYD:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;S-1-5-21-1923243488-1610499346-3556306727-1001)(A;;0x100020;;;S-1-15-3-65536-599108337-2355189375-1353122160-3480128286-3345335107-485756383-4087318168-230526575)'
if(([IO.DirectoryInfo]::new('C:\Users\Lenovo')).GetAccessControl().GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access') -cne $profileExpected){throw 'profile custody differs'}
foreach($p in @('C:\','C:\Users','C:\Users\Lenovo')){if(([IO.File]::GetAttributes($p) -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'reparse parent'}}
$acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetAccessRuleProtection($true,$false);$acl.SetOwner($id.User)
foreach($sid in @($id.User,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'),[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))){$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl',[Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit','None','Allow'))}
$dir=[IO.Directory]::CreateDirectory($build,$acl);$got=$dir.GetAccessControl()
if(($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $got.GetOwner([Security.Principal.SecurityIdentifier]).Value -cne $id.User.Value -or -not $got.AreAccessRulesProtected -or $got.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access) -cne $acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)){throw 'private ACL differs'}
function WriteNew([string]$name,[string]$value){$f=[IO.FileStream]::new((Join-Path $build $name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$b=[Text.UTF8Encoding]::new($false).GetBytes($value);$f.Write($b,0,$b.Length);$f.Flush($true)}finally{$f.Dispose()}}
$held=[Collections.Generic.List[IO.FileStream]]::new()
function Seal([string]$n){$held.Add([IO.FileStream]::new((Join-Path $build $n),[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read))}
$tool='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64'
$vc='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207'
$sdk='C:\Program Files (x86)\Windows Kits\10'
$commands=[Collections.Generic.List[object]]::new()
function Tool([string]$exe,[string[]]$arguments,[string]$label){
 $si=[Diagnostics.ProcessStartInfo]::new();$si.FileName=$exe;$si.Arguments=($arguments|ForEach-Object {'"'+$_+'"'}) -join ' '
 $si.WorkingDirectory=$build;$si.UseShellExecute=$false;$si.CreateNoWindow=$true;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true
 $si.EnvironmentVariables.Clear();$si.EnvironmentVariables['SystemRoot']='C:\Windows';$si.EnvironmentVariables['WINDIR']='C:\Windows'
 $si.EnvironmentVariables['PATH']=$sdk+'\bin\10.0.26100.0\x64;C:\Windows\System32';$si.EnvironmentVariables['TEMP']=$build;$si.EnvironmentVariables['TMP']=$build
 $digest=HashFile $exe;$p=[Diagnostics.Process]::Start($si);$o=$p.StandardOutput.ReadToEndAsync();$e=$p.StandardError.ReadToEndAsync()
 if(-not $p.WaitForExit(60000)){throw "owned build tool timeout: $label; no automatic retry"}
 WriteNew ($label+'.stdout.txt') $o.Result;WriteNew ($label+'.stderr.txt') $e.Result
 $commands.Add([ordered]@{exe=$exe;sha256=$digest;arguments=$arguments;exit_code=$p.ExitCode;environment='FIVE_FIXED_PROCESS_VARIABLES'})
 if($p.ExitCode -ne 0){throw "build failed $label"}
}
try {
 foreach($n in @('EtwCapture.cs','WhpCounterProbe.cpp','Test-FixtureAssessment.ps1')){WriteNew $n ([Text.Encoding]::UTF8.GetString($inputBytes[$n]));Seal $n}
 Tool 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe' @('/nologo','/platform:x64','/target:exe','/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Web.Extensions.dll','/out:EtwCapture-v3.exe','EtwCapture.cs') 'etw-compile'
 Seal 'EtwCapture-v3.exe';$etwHash=HashFile (Join-Path $build 'EtwCapture-v3.exe')
 Tool (Join-Path $build 'EtwCapture-v3.exe') @('--layout-check') 'etw-memory-layout'
 $inc=@(('/I'+$vc+'\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'))
 Tool (Join-Path $tool 'cl.exe') (@('/nologo','/c','/O2','/MT','/EHsc','/GS','/std:c++17')+$inc+@('/FoWhpCounterProbe.obj','WhpCounterProbe.cpp')) 'whp-compile'
 Seal 'WhpCounterProbe.obj'
 $libs=@(('/LIBPATH:'+$vc+'\lib\x64'),('/LIBPATH:'+$sdk+'\Lib\10.0.26100.0\ucrt\x64'),('/LIBPATH:'+$sdk+'\Lib\10.0.26100.0\um\x64'))
 Tool (Join-Path $tool 'link.exe') (@('/NOLOGO','/SUBSYSTEM:CONSOLE','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='asInvoker' uiAccess='false'",'/OUT:WhpCounterProbe.exe','WhpCounterProbe.obj','kernel32.lib')+$libs) 'whp-link'
 Seal 'WhpCounterProbe.exe';$whpHash=HashFile (Join-Path $build 'WhpCounterProbe.exe')
 Tool (Join-Path $build 'WhpCounterProbe.exe') @('--layout-check') 'whp-memory-layout'
 $h=[Text.Encoding]::UTF8.GetString($inputBytes['Run-I2Feasibility.ps1']).Replace('__ETW_SHA256__',$etwHash).Replace('__WHP_SHA256__',$whpHash)
 WriteNew 'Run-I2Feasibility.ps1' $h;Seal 'Run-I2Feasibility.ps1';$hHash=HashFile (Join-Path $build 'Run-I2Feasibility.ps1')
 $t=[Text.Encoding]::UTF8.GetString($inputBytes['Trusted-Entry.template.ps1']).Replace('__HARNESS_SHA256__',$hHash)
 WriteNew 'Trusted-Entry.template.ps1' $t;Seal 'Trusted-Entry.template.ps1';$tHash=HashFile (Join-Path $build 'Trusted-Entry.template.ps1')
 $n=[Text.Encoding]::UTF8.GetString($inputBytes['NativeEntry.c']).Replace('__TEMPLATE_SHA256__',$tHash)
 WriteNew 'NativeEntry.c' $n;Seal 'NativeEntry.c'
 Tool (Join-Path $tool 'cl.exe') (@('/nologo','/c','/GS-','/O1','/Oi-','/Zl','/D_WIN32_WINNT=0x0602')+$inc+@('/FoNativeEntry.obj','NativeEntry.c')) 'native-compile'
 Seal 'NativeEntry.obj'
 Tool (Join-Path $tool 'link.exe') @('/NOLOGO','/NODEFAULTLIB','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='requireAdministrator' uiAccess='false'",'/ENTRY:Entry','/OUT:NativeEntry.exe','NativeEntry.obj',($sdk+'\Lib\10.0.26100.0\um\x64\kernel32.lib')) 'native-link'
 Seal 'NativeEntry.exe';$nativeHash=HashFile (Join-Path $build 'NativeEntry.exe')
 $l=[Text.Encoding]::UTF8.GetString($inputBytes['Launch-Approved.ps1']).Replace('__NATIVE_SHA256__',$nativeHash)
 WriteNew 'Launch-Approved.ps1' $l;Seal 'Launch-Approved.ps1'
 foreach($leaf in @('NativeEntry.exe','WhpCounterProbe.exe')){Tool (Join-Path $tool 'dumpbin.exe') @('/headers','/imports',$leaf) ($leaf+'-pe')}
 Tool 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' @('-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',(Join-Path $build 'Test-FixtureAssessment.ps1'),'-Source',(Join-Path $build 'Run-I2Feasibility.ps1'),'-HistoricalGuard','D:\ReBaseGuard-309\records\p309-i2-renewed-attempt-v3\capture\guard.jsonl') 'fixture-assessment-tests'
 $parse=@();foreach($leaf in @('Run-I2Feasibility.ps1','Trusted-Entry.template.ps1','Launch-Approved.ps1')){$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $build $leaf),[ref]$tokens,[ref]$errors);if($errors.Count){throw 'parse failed'};$parse+=@{file=$leaf;errors=0}}
 # ReadOnlyPreflight pins a file; it does not dispatch the native entry/UAC.
 $preflight=& ([ScriptBlock]::Create($l)) -ReadOnlyPreflight
 WriteNew 'readonly-entry-pins.json' ($preflight -join [Environment]::NewLine)
 $result=[ordered]@{source_commit=$sourceCommit;input_pins=$pins;commands=$commands.ToArray();parse=$parse;root=$build;root_sddl=$got.Sddl;profile_sddl=$profileExpected;source_and_objects_read_locked=$true;etw_sha256=$etwHash;whp_sha256=$whpHash;native_sha256=$nativeHash;harness_sha256=$hHash;template_sha256=$tHash;launcher_sha256=(HashFile (Join-Path $build 'Launch-Approved.ps1'));unit_tests=17;uac=0;trace=0;fixture=0;vm=0;admission='BLOCKED';winps=$PSVersionTable.PSVersion.ToString()}
 WriteNew 'BUILD_RESULT.json' ($result | ConvertTo-Json -Depth 10)
 $manifest=@(Get-ChildItem -LiteralPath $build -File | ForEach-Object {@{name=$_.Name;bytes=$_.Length;sha256=(HashFile $_.FullName)}})
 WriteNew 'SHA256SUMS.json' ($manifest | ConvertTo-Json -Depth 6)
 $result | ConvertTo-Json -Depth 10
} finally {foreach($f in $held){$f.Dispose()}}
