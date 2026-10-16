$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$dir=$PSScriptRoot
$source=[IO.Path]::GetFullPath((Join-Path $dir '..\package\NativeEntry.c'))
$expected='427198611682bc9aee89eace595dbb93cb1913ab8da24d9c547432879bfe28ae'
function Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
if((Hash $source) -cne $expected){throw 'patched source binding differs'}
$vc='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207'
$sdk='C:\Program Files (x86)\Windows Kits\10'
$tool=Join-Path $vc 'bin\Hostx64\x64'
$commands=[Collections.Generic.List[object]]::new()
function Run([string]$exe,[string[]]$arguments,[string]$label){
 $si=[Diagnostics.ProcessStartInfo]::new();$si.FileName=$exe
 $si.Arguments=($arguments|ForEach-Object {'"'+$_+'"'}) -join ' '
 $si.WorkingDirectory=$dir;$si.UseShellExecute=$false;$si.CreateNoWindow=$true
 $si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true
 $si.EnvironmentVariables.Clear();$si.EnvironmentVariables['SystemRoot']='C:\Windows';$si.EnvironmentVariables['WINDIR']='C:\Windows'
 $si.EnvironmentVariables['PATH']=$sdk+'\bin\10.0.26100.0\x64;C:\Windows\System32'
 $si.EnvironmentVariables['TEMP']=$dir;$si.EnvironmentVariables['TMP']=$dir
 $p=[Diagnostics.Process]::Start($si);$o=$p.StandardOutput.ReadToEndAsync();$e=$p.StandardError.ReadToEndAsync()
 if(-not $p.WaitForExit(60000)){throw "owned tool timeout $label"}
 $utf8=[Text.UTF8Encoding]::new($false)
 [IO.File]::WriteAllText((Join-Path $dir ($label+'.stdout.txt')),$o.Result,$utf8)
 [IO.File]::WriteAllText((Join-Path $dir ($label+'.stderr.txt')),$e.Result,$utf8)
 $commands.Add([ordered]@{exe=$exe;sha256=(Hash $exe);arguments=$arguments;exit_code=$p.ExitCode;temp_tmp=$dir;environment='FIVE_FIXED_PROCESS_VARIABLES'})
 if($p.ExitCode -ne 0){throw "tool failed $label"}
 return $o.Result
}
$held=[Collections.Generic.List[IO.FileStream]]::new()
try {
 foreach($p in @($source,(Join-Path $dir 'test_native_ownership.c'))){$held.Add([IO.FileStream]::new($p,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read))}
 $inc=@(('/I'+$vc+'\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'))
 $null=Run (Join-Path $tool 'cl.exe') (@('/nologo','/c','/TC','/std:c17','/O2','/MT','/GS','/Gy','/W3')+$inc+@('/Fotest_native_ownership.obj','test_native_ownership.c')) 'native-test-compile'
 $libs=@(('/LIBPATH:'+$vc+'\lib\x64'),('/LIBPATH:'+$sdk+'\Lib\10.0.26100.0\ucrt\x64'),('/LIBPATH:'+$sdk+'\Lib\10.0.26100.0\um\x64'))
 $null=Run (Join-Path $tool 'link.exe') (@('/NOLOGO','/SUBSYSTEM:CONSOLE','/DYNAMICBASE','/NXCOMPAT','/OPT:REF','/MANIFEST:EMBED',"/MANIFESTUAC:level='asInvoker' uiAccess='false'",'/OUT:test_native_ownership.exe','test_native_ownership.obj','kernel32.lib')+$libs) 'native-test-link'
 $pe=Run (Join-Path $tool 'dumpbin.exe') @('/headers','/imports','test_native_ownership.exe') 'native-test-pe'
 if($pe -match '(?im)^\s*(advapi32|bcrypt)\.dll\s*$'){throw 'test unexpectedly imports real token/CNG DLL'}
 $result=(Run (Join-Path $dir 'test_native_ownership.exe') @() 'native-test-run') | ConvertFrom-Json
 if(-not $result.passed -or $result.cases -ne 19 -or $result.entry_invocations -ne 0 -or $result.real_token_cng_queries -ne 0){throw 'test result differs'}
 $record=[ordered]@{patched_source_sha256=(Hash $source);test_source_sha256=(Hash (Join-Path $dir 'test_native_ownership.c'));runner_sha256=(Hash $PSCommandPath);executable_sha256=(Hash (Join-Path $dir 'test_native_ownership.exe'));commands=$commands.ToArray();result=$result;scope='PURE_MEMORY_SYNTHETIC_API_FAILURE_OWNERSHIP';limitation='Does not establish actual Win32 failure output behavior, production isolation, real token/CNG access, or formal admission';uac=0;trace=0;vm=0;services=0;production_keys=0;admission='BLOCKED'}
 [IO.File]::WriteAllText((Join-Path $dir 'NATIVE_OWNERSHIP_RESULT.json'),($record|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))
 $record|ConvertTo-Json -Depth 10
} finally {foreach($f in $held){$f.Dispose()}}
