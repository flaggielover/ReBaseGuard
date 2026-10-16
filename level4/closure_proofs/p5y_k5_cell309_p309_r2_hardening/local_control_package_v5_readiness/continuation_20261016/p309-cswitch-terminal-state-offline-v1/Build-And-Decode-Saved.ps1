$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
$dir=$PSScriptRoot
$inputEtl='D:\ReBaseGuard-309\records\p309-i2-root-v3-attempt-20261016-01\capture\capture.etl'
$expectedEtl='3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870'
$reference='D:\ReBaseGuard-309\records\p309-i2-renewed-attempt-v3\offline\REFERENCE_KernelTraceEventParser.cs'
$referenceHash='2245ccc62b0d933190068a18344bc64749a2893bd9740a79706ba7fe5e86c778'
$source=Join-Path $dir 'SavedThreadTerminal.cpp'
$vc='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207'
$sdk='C:\Program Files (x86)\Windows Kits\10'
$tool=Join-Path $vc 'bin\Hostx64\x64'
$commands=[Collections.Generic.List[object]]::new()
function Hash([string]$p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function WriteNew([string]$name,[string]$text){$s=[IO.FileStream]::new((Join-Path $dir $name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$b=[Text.UTF8Encoding]::new($false).GetBytes($text);$s.Write($b,0,$b.Length);$s.Flush($true)}finally{$s.Dispose()}}
function Run([string]$exe,[string[]]$arguments,[string]$label){
 $si=[Diagnostics.ProcessStartInfo]::new();$si.FileName=$exe;$si.Arguments=($arguments|ForEach-Object {'"'+$_+'"'}) -join ' '
 $si.WorkingDirectory=$dir;$si.UseShellExecute=$false;$si.CreateNoWindow=$true;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true
 $si.EnvironmentVariables.Clear();$si.EnvironmentVariables['SystemRoot']='C:\Windows';$si.EnvironmentVariables['WINDIR']='C:\Windows'
 $si.EnvironmentVariables['PATH']=$sdk+'\bin\10.0.26100.0\x64;C:\Windows\System32';$si.EnvironmentVariables['TEMP']=$dir;$si.EnvironmentVariables['TMP']=$dir
 $p=[Diagnostics.Process]::Start($si);$o=$p.StandardOutput.ReadToEndAsync();$e=$p.StandardError.ReadToEndAsync()
 if(-not $p.WaitForExit(120000)){throw "owned offline tool did not exit: $label; no retry"}
 WriteNew ($label+'.stdout.txt') $o.Result;WriteNew ($label+'.stderr.txt') $e.Result
 $commands.Add([ordered]@{exe=$exe;sha256=(Hash $exe);arguments=$arguments;exit_code=$p.ExitCode;temp_tmp=$dir;environment='FIVE_FIXED_PROCESS_VARIABLES'})
 if($p.ExitCode -ne 0){throw "offline tool failed: $label"};return $o.Result
}
$held=[Collections.Generic.List[IO.FileStream]]::new()
try{
 foreach($p in @($source,$reference)){$held.Add([IO.FileStream]::new($p,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read))}
 if((Hash $reference) -cne $referenceHash){throw 'fixed reference binding differs'}
 $sourceHash=Hash $source
 $inc=@(('/I'+$vc+'\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'))
 $null=Run (Join-Path $tool 'cl.exe') (@('/nologo','/c','/std:c++17','/O2','/MT','/EHsc','/GS','/W4')+$inc+@('/FoSavedThreadTerminal.obj','SavedThreadTerminal.cpp')) 'compile'
 $libs=@(('/LIBPATH:'+$vc+'\lib\x64'),('/LIBPATH:'+$sdk+'\Lib\10.0.26100.0\ucrt\x64'),('/LIBPATH:'+$sdk+'\Lib\10.0.26100.0\um\x64'))
 $null=Run (Join-Path $tool 'link.exe') (@('/NOLOGO','/SUBSYSTEM:CONSOLE','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='asInvoker' uiAccess='false'",'/OUT:SavedThreadTerminal.exe','SavedThreadTerminal.obj','kernel32.lib','advapi32.lib')+$libs) 'link'
 $exe=Join-Path $dir 'SavedThreadTerminal.exe';$exeHash=Hash $exe
 $null=Run (Join-Path $tool 'dumpbin.exe') @('/headers','/imports','SavedThreadTerminal.exe') 'pe'
 WriteNew 'BUILD_RESULT.json' (@{source_sha256=$sourceHash;reference_sha256=$referenceHash;exe_sha256=$exeHash;commands=$commands.ToArray();scope='ORDINARY_SAVED_FILE_DECODER_BUILD_ONLY';admission='BLOCKED'}|ConvertTo-Json -Depth 8)
 # Python wrapper below supplies leaf AND ancestor input/source/code pins and
 # dispatches exactly once; this PowerShell process never decodes by itself.
 $python='C:\Users\Lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
 $null=Run $python @('-B',(Join-Path $dir 'decode_once.py'),'--source-sha256',$sourceHash,'--exe-sha256',$exeHash) 'decode-dispatch'
}finally{foreach($f in $held){$f.Dispose()}}
