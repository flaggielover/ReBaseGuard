param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9-]{1,48}$')][string]$RunName)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$stage=$PSScriptRoot
$build=Join-Path $stage ('build-'+$RunName)
if(Test-Path -LiteralPath $build){throw 'Fresh ordinary build name required; preserve previous artifacts'}
$null=[IO.Directory]::CreateDirectory($build)
$vc='C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207'
$sdk='C:\Program Files (x86)\Windows Kits\10'
$sdkVersion='10.0.26100.0'
$tool=Join-Path $vc 'bin\Hostx64\x64'
$sdkBin=Join-Path $sdk ('bin\'+$sdkVersion+'\x64')
$compiler=Join-Path $tool 'cl.exe'
$expectedCompiler='6aa39ae173cb8563d796359930b332a08b2fdc1745b70e5a4caa48a9779fdd07'
$held=[Collections.Generic.List[IO.FileStream]]::new()
$commands=[Collections.Generic.List[object]]::new()
$inputs=[Collections.Generic.List[object]]::new()
function Hash([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
function NewBytes([string]$Leaf,[byte[]]$Bytes){$f=[IO.FileStream]::new((Join-Path $build $Leaf),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}}
function NewText([string]$Leaf,[string]$Text){NewBytes $Leaf ([Text.UTF8Encoding]::new($false,$true).GetBytes($Text))}
function Pin([string]$Path,[string]$Kind){$f=[IO.FileStream]::new($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read);$held.Add($f);$item=[ordered]@{path=$Path;kind=$Kind;bytes=$f.Length;sha256=(Hash $Path);hash_command=('Get-FileHash -LiteralPath '''+$Path+''' -Algorithm SHA256')};$inputs.Add($item);return $item}
function QuoteArgument([string]$Value){if($Value.Contains('"')-or$Value.EndsWith('\')){throw 'Build argument requires a different quoting policy'};return '"'+$Value+'"'}
function Tool([string]$Exe,[string[]]$Arguments,[string]$Label){
 $nativeArguments=($Arguments|ForEach-Object{QuoteArgument $_})-join' '
 $command=[ordered]@{exe=$Exe;exe_sha256=(Hash $Exe);arguments=$Arguments;working_directory=$build;environment='SystemRoot,WINDIR,PATH,TEMP,TMP,VSLANG_FIXED';stdout_stderr_each_max_raw_bytes=1048576;timeout_ms=60000;owned_process_kill_wait_ms=2000;operation_scope='ORDINARY_BUILD_OR_MEMORY_TEST_ONLY'}
 NewText ($Label+'.command.json') ($command|ConvertTo-Json -Depth 8)
 $r=[P309V8BuildToolRunner]::Run($Exe,$nativeArguments,$build,$tool,$sdkBin)
 foreach($name in @('Stdout','Stderr')){$stream=$r.$name;NewBytes ($Label+'.'+$name.ToLowerInvariant()+'.bin') $stream.Bytes;NewText ($Label+'.'+$name.ToLowerInvariant()+'.txt') ([string]$stream.Text)}
 NewText ($Label+'.result.json') ($r|ConvertTo-Json -Depth 6)
 $command['exit_code']=$r.ExitCode;$command['unknown']=$r.Unknown;$command['timed_out']=$r.TimedOut;$commands.Add($command)
 if($r.Unknown-or$r.TimedOut-or$r.ExitCode-ne 0){throw ($Label+' failed/UNKNOWN; preserve this ordinary build; no automatic retry')}
 return [string]$r.Stdout.Text
}
try{
 foreach($leaf in @('SavedExtendedData.cpp','BuildToolRunner.cs','Build-Only.ps1')){
  $original=Join-Path $stage $leaf;$bytes=[IO.File]::ReadAllBytes($original);NewBytes $leaf $bytes;$null=Pin (Join-Path $build $leaf) 'SAME_BYTES_BUILD_SNAPSHOT'
 }
 foreach($leaf in @('cl.exe','link.exe','dumpbin.exe','c1xx.dll','c2.dll','mspdbcore.dll')){$null=Pin (Join-Path $tool $leaf) 'MSVC_TOOLCHAIN_FILE'}
 if((Hash $compiler)-cne$expectedCompiler){throw 'Fixed MSVC compiler SHA256 mismatch'}
 $libraries=@(
  (Join-Path $vc 'lib\x64\libcmt.lib'),(Join-Path $vc 'lib\x64\libcpmt.lib'),(Join-Path $vc 'lib\x64\libvcruntime.lib'),(Join-Path $vc 'lib\x64\oldnames.lib'),
  (Join-Path $sdk ('Lib\'+$sdkVersion+'\ucrt\x64\libucrt.lib')),(Join-Path $sdk ('Lib\'+$sdkVersion+'\um\x64\kernel32.lib')),
  (Join-Path $sdk ('Lib\'+$sdkVersion+'\um\x64\advapi32.lib')),(Join-Path $sdk ('Lib\'+$sdkVersion+'\um\x64\bcrypt.lib'))
 )
 foreach($library in $libraries){$null=Pin $library 'EXPLICIT_STATIC_OR_IMPORT_LIBRARY'}
 $previousTemp=$env:TEMP;$previousTmp=$env:TMP
 try{$env:TEMP=$build;$env:TMP=$build;Add-Type -TypeDefinition ([IO.File]::ReadAllText((Join-Path $build 'BuildToolRunner.cs'))) -Language CSharp}finally{$env:TEMP=$previousTemp;$env:TMP=$previousTmp}
 $includes=@(('/I'+$vc+'\include'),('/I'+$sdk+'\Include\'+$sdkVersion+'\ucrt'),('/I'+$sdk+'\Include\'+$sdkVersion+'\um'),('/I'+$sdk+'\Include\'+$sdkVersion+'\shared'))
 $compile=Tool $compiler (@('/nologo','/c','/std:c++17','/Zc:__cplusplus','/O2','/MT','/EHsc','/GS','/guard:cf','/W4','/WX','/showIncludes')+$includes+@('/FoSavedExtendedData.obj','SavedExtendedData.cpp')) 'compile'
 $headerPaths=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 foreach($match in [regex]::Matches($compile,'(?im)^\s*(?:Note: including file:|\u6ce8\u610f:\s*\u5305\u542b\u6587\u4ef6:)\s*(.+?)\s*$')){$path=$match.Groups[1].Value.Trim();if(-not($path.StartsWith(($vc+'\include\'),[StringComparison]::OrdinalIgnoreCase)-or$path.StartsWith(($sdk+'\Include\'+$sdkVersion+'\'),[StringComparison]::OrdinalIgnoreCase))){throw 'Included header escaped fixed SDK/MSVC roots'};$null=$headerPaths.Add($path)}
 if($headerPaths.Count-lt 3){throw 'Compiler did not provide a usable English or observed CP936 Chinese include dependency inventory'}
 foreach($path in ($headerPaths|Sort-Object)){$null=Pin $path 'TRANSITIVE_HEADER_OBSERVED_AFTER_COMPILE'}
 $null=Tool (Join-Path $tool 'link.exe') (@('/NOLOGO','/NODEFAULTLIB','/SUBSYSTEM:CONSOLE','/DYNAMICBASE','/HIGHENTROPYVA','/NXCOMPAT','/guard:cf','/MANIFEST:EMBED',"/MANIFESTUAC:level='asInvoker' uiAccess='false'",'/OUT:SavedExtendedData.exe','SavedExtendedData.obj')+$libraries) 'link'
 $exe=Join-Path $build 'SavedExtendedData.exe';$binary=Pin $exe 'BUILT_EXECUTABLE'
 $null=Tool (Join-Path $tool 'dumpbin.exe') @('/headers','/imports','SavedExtendedData.exe') 'pe'
 $memory=Tool $exe @('--self-test') 'memory-checks'
 if($memory-notmatch '"result":"PASS"'-or$memory-notmatch '"actual_etl_reads":0'-or$memory-notmatch '"open_trace_calls":0'){throw 'Missing memory-only PASS summary'}
 if((Hash $compiler)-cne$expectedCompiler){throw 'Compiler binding drift'}
 $result=[ordered]@{schema='P309_SAVED_EXTENDED_V8_BUILD';scope='ORDINARY_BUILD_AND_SYNTHETIC_MEMORY_TESTS_ONLY';source_sha256=(Hash (Join-Path $build 'SavedExtendedData.cpp'));exe_sha256=$binary.sha256;compiler_sha256=$expectedCompiler;inputs=$inputs.ToArray();commands=$commands.ToArray();transitive_headers='OBSERVED_AND_HASHED_AFTER_COMPILE_THEN_HELD;NOT_AN_IMMUTABLE_PREBUILD_SDK_SNAPSHOT';actual_etl_reads=0;open_trace_calls=0;live_trace=0;host_queries=0;uac=0;vm=0;wsl=0;installation=0;all_I1_I7='OPEN';admission='BLOCKED';actual_scan_authorized_by_this_script=$false}
 NewText 'BUILD_RESULT.json' ($result|ConvertTo-Json -Depth 10)
 [ordered]@{result='PASS';build=$build;source_sha256=$result.source_sha256;exe_sha256=$result.exe_sha256;compiler_sha256=$expectedCompiler;actual_etl_reads=0;open_trace_calls=0;admission='BLOCKED'}|ConvertTo-Json
}catch{
 try{NewText 'BUILD_FAILURE.json' ([ordered]@{scope='ORDINARY_BUILD_ONLY';result='FAIL_OR_UNKNOWN';error_type=$_.Exception.GetType().FullName;error_message=$_.Exception.Message;commands=$commands.ToArray();actual_etl_reads=0;automatic_retry=$false;admission='BLOCKED'}|ConvertTo-Json -Depth 8)}catch{}
 throw
}finally{foreach($f in $held){$f.Dispose()}}
