param([Parameter(Mandatory=$true)][string]$InputManifestSha256)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.Major-ne 5-or$PSVersionTable.PSVersion.Minor-ne 1){throw 'WinPS 5.1 required'}
$build='C:\Users\Lenovo\P309-FactsRepair-build-20261016-v1'
function HashBytes([byte[]]$b){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($b)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
function HashFile([string]$p){HashBytes ([IO.File]::ReadAllBytes($p))}
$mb=[IO.File]::ReadAllBytes((Join-Path $PSScriptRoot 'INPUT_SOURCES.json'))
if($InputManifestSha256-notmatch'^[0-9a-f]{64}$'-or(HashBytes $mb)-cne$InputManifestSha256){throw 'input manifest differs'}
$manifest=[Text.Encoding]::UTF8.GetString($mb)|ConvertFrom-Json
$inputs=@{};foreach($f in $manifest.files){if($f.file-notmatch'^[A-Za-z0-9_.-]+$'){throw 'invalid input leaf'};$b=[IO.File]::ReadAllBytes((Join-Path $PSScriptRoot $f.file));if((HashBytes $b)-cne$f.sha256){throw ('source differs: '+$f.file)};$inputs[$f.file]=$b}
$required=@('NativeEntry.c','Launch-Approved.ps1','Trusted-Entry.template.ps1','Read-FactsRepair.ps1','FactsReadCore.cs','Test-FactsReadCore.ps1','Test-FactsSummary.ps1')
foreach($name in $required){if(-not$inputs.ContainsKey($name)){throw 'required source missing'}}
$id=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner build only'}
try{$null=[IO.File]::GetAttributes($build);$exists=$true}catch{$hr=$_.Exception.GetBaseException().HResult;if($hr-notin@(-2147024894,-2147024893)){throw};$exists=$false}
if($exists){throw 'fresh private build required; preserve old directories'}
$profileExpected='O:SYG:SYD:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;S-1-5-21-1923243488-1610499346-3556306727-1001)(A;;0x100020;;;S-1-15-3-65536-599108337-2355189375-1353122160-3480128286-3345335107-485756383-4087318168-230526575)'
if(([IO.DirectoryInfo]::new('C:\Users\Lenovo')).GetAccessControl().GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]'Owner,Group,Access')-cne$profileExpected){throw 'profile custody differs'}
foreach($p in @('C:\','C:\Users','C:\Users\Lenovo')){if(([IO.File]::GetAttributes($p)-band[IO.FileAttributes]::ReparsePoint)-ne 0){throw 'reparse ancestor'}}
$acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetAccessRuleProtection($true,$false);$acl.SetOwner($id.User)
foreach($sid in @($id.User,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'),[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))){$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))}
$dir=[IO.Directory]::CreateDirectory($build,$acl);$actual=$dir.GetAccessControl()
if(($dir.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0-or-not$actual.AreAccessRulesProtected-or$actual.GetOwner([Security.Principal.SecurityIdentifier]).Value-cne$id.User.Value-or$actual.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)-cne$acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)){throw 'new private build custody differs'}
function WriteNew([string]$Name,[byte[]]$Bytes){$f=[IO.FileStream]::new((Join-Path $build $Name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}}
function TextNew([string]$Name,[string]$Text){WriteNew $Name ([Text.Encoding]::UTF8.GetBytes($Text))}
$held=[Collections.Generic.List[IO.FileStream]]::new()
function Seal([string]$Name){$held.Add([IO.FileStream]::new((Join-Path $build $Name),[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read))}
$vc='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207'
$tool=$vc+'\bin\Hostx64\x64';$sdk='C:\Program Files (x86)\Windows Kits\10'
$toolPins=@{'cl.exe'='6aa39ae173cb8563d796359930b332a08b2fdc1745b70e5a4caa48a9779fdd07';'link.exe'='7a9b2527a183361329b0a6d85da13680467152c3b7bbe14470e7c74383e3b0a1';'dumpbin.exe'='db64bcb6f17a61f0d64ecc016b90faf9b83134d41fcb1b4fc6db9e347fdbd674'}
foreach($leaf in $toolPins.Keys){if((HashFile (Join-Path $tool $leaf))-cne$toolPins[$leaf]){throw 'compiler tool differs'}}
$commands=[Collections.Generic.List[object]]::new()
function Tool([string]$Exe,[string[]]$Arguments,[string]$Label){
 $si=[Diagnostics.ProcessStartInfo]::new();$si.FileName=$Exe;$si.Arguments=($Arguments|ForEach-Object {'"'+$_+'"'})-join' ';$si.WorkingDirectory=$build
 $si.UseShellExecute=$false;$si.CreateNoWindow=$true;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true
 $si.EnvironmentVariables.Clear();foreach($name in @('SystemRoot','WINDIR')){$si.EnvironmentVariables[$name]='C:\Windows'}
 $si.EnvironmentVariables['PATH']=$sdk+'\bin\10.0.26100.0\x64;C:\Windows\System32';$si.EnvironmentVariables['TEMP']=$build;$si.EnvironmentVariables['TMP']=$build
 $p=[Diagnostics.Process]::Start($si);$out=$p.StandardOutput.ReadToEndAsync();$err=$p.StandardError.ReadToEndAsync()
 if(-not$p.WaitForExit(60000)){throw ('owned build tool timeout: '+$Label+'; preserve/no retry')}
 TextNew ($Label+'.stdout.txt') $out.Result;TextNew ($Label+'.stderr.txt') $err.Result
 $commands.Add(@{executable=$Exe;sha256=(HashFile $Exe);arguments=$Arguments;exit_code=$p.ExitCode;environment='FIVE_FIXED_VARIABLES';pid=$p.Id})
 if($p.ExitCode-ne 0){throw ('build/test failed: '+$Label)}
}
try{
 WriteNew 'FactsReadCore.cs' $inputs['FactsReadCore.cs'];Seal 'FactsReadCore.cs';$coreHash=HashFile (Join-Path $build 'FactsReadCore.cs')
 $harness=[Text.Encoding]::UTF8.GetString($inputs['Read-FactsRepair.ps1']).Replace('__CORE_SHA256__',$coreHash)
 TextNew 'Read-FactsRepair.ps1' $harness;Seal 'Read-FactsRepair.ps1';$hHash=HashFile (Join-Path $build 'Read-FactsRepair.ps1')
 $template=[Text.Encoding]::UTF8.GetString($inputs['Trusted-Entry.template.ps1']).Replace('__HARNESS_SHA256__',$hHash).Replace('__CORE_SHA256__',$coreHash)
 TextNew 'Trusted-Entry.template.ps1' $template;Seal 'Trusted-Entry.template.ps1';$tHash=HashFile (Join-Path $build 'Trusted-Entry.template.ps1')
 $native=[Text.Encoding]::UTF8.GetString($inputs['NativeEntry.c']).Replace('__TEMPLATE_SHA256__',$tHash)
 TextNew 'NativeEntry.c' $native;Seal 'NativeEntry.c'
 $inc=@(('/I'+$vc+'\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'))
 Tool (Join-Path $tool 'cl.exe') (@('/nologo','/c','/GS-','/O1','/Oi-','/Zl','/D_WIN32_WINNT=0x0602')+$inc+@('/FoNativeEntry.obj','NativeEntry.c')) 'native-compile'
 Seal 'NativeEntry.obj'
 Tool (Join-Path $tool 'link.exe') @('/NOLOGO','/NODEFAULTLIB','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='requireAdministrator' uiAccess='false'",'/ENTRY:Entry','/OUT:NativeEntry.exe','NativeEntry.obj',($sdk+'\Lib\10.0.26100.0\um\x64\kernel32.lib')) 'native-link'
 Seal 'NativeEntry.exe';$nHash=HashFile (Join-Path $build 'NativeEntry.exe')
 $launcher=[Text.Encoding]::UTF8.GetString($inputs['Launch-Approved.ps1']).Replace('__NATIVE_SHA256__',$nHash)
 TextNew 'Launch-Approved.ps1' $launcher;Seal 'Launch-Approved.ps1'
 foreach($name in @('Test-FactsReadCore.ps1','Test-FactsSummary.ps1')){WriteNew $name $inputs[$name];Seal $name}
 Tool (Join-Path $tool 'dumpbin.exe') @('/headers','/imports','NativeEntry.exe') 'native-pe'
 foreach($name in @('Test-FactsReadCore.ps1','Test-FactsSummary.ps1')){Tool 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' @('-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',(Join-Path $build $name)) $name.Replace('.ps1','')}
 $parse=@();foreach($name in @('Read-FactsRepair.ps1','Trusted-Entry.template.ps1','Launch-Approved.ps1')){$t=$null;$e=$null;$null=[Management.Automation.Language.Parser]::ParseInput([IO.File]::ReadAllText((Join-Path $build $name),[Text.Encoding]::UTF8),[ref]$t,[ref]$e);if($e.Count){throw ('parse failed: '+$name)};$parse+=@{file=$name;errors=0}}
 $preflight=& ([ScriptBlock]::Create($launcher)) -ReadOnlyPreflight;TextNew 'readonly-entry-pins.json' ($preflight-join[Environment]::NewLine)
 $result=@{utc=[DateTime]::UtcNow.ToString('o');scope='ORDINARY_OWNER_BUILD_AND_SYNTHETIC_TESTS_ONLY';source_commit=$manifest.source_commit;input_manifest_sha256=$InputManifestSha256;input_files=$manifest.files;commands=$commands.ToArray();parse=$parse;core_sha256=$coreHash;harness_sha256=$hHash;template_sha256=$tHash;native_sha256=$nHash;launcher_sha256=(HashFile (Join-Path $build 'Launch-Approved.ps1'));private_root=$build;private_root_sddl=$actual.Sddl;uac_requests=0;native_entry_executions=0;host_queries=0;vm_starts=0;admission='BLOCKED';I1_I7='OPEN';whole_task_complete=$false}
 TextNew 'BUILD_RESULT_PRIVATE.json' ($result|ConvertTo-Json -Depth 14)
 $sums=@(Get-ChildItem -LiteralPath $build -File|ForEach-Object{@{file=$_.Name;bytes=$_.Length;sha256=(HashFile $_.FullName)}})
 TextNew 'SHA256SUMS.json' ($sums|ConvertTo-Json -Depth 8)
 @{build_complete=$true;native_sha256=$nHash;core_sha256=$coreHash;harness_sha256=$hHash;uac=0;host_queries=0;admission='BLOCKED'}|ConvertTo-Json
}finally{foreach($f in $held){$f.Dispose()}}
