param([Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9-]{1,48}$')][string]$RunName)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
$build=Join-Path $PSScriptRoot ('build-'+$RunName)
$testRoot=Join-Path (Join-Path $PSScriptRoot 'test-runs') $RunName
if(Test-Path -LiteralPath $build){throw 'Fresh build name required; retain prior build evidence'}
if(Test-Path -LiteralPath $testRoot){throw 'Fresh test name required; retain prior fixture evidence'}
$null=[IO.Directory]::CreateDirectory($build)
$compiler='C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$sources=@('NativeFile.cs','ServiceIdentity.cs','HostAnchor.cs','AnchorAck.cs')|ForEach-Object{Join-Path $PSScriptRoot $_}
$inputs=@();$held=[Collections.Generic.List[IO.FileStream]]::new()
foreach($source in @($sources+(Join-Path $PSScriptRoot 'TestHostAnchor.cs')+(Join-Path $PSScriptRoot 'BuildToolRunner.cs')+(Join-Path $PSScriptRoot 'Build-And-Test.ps1'))){
 $bytes=[IO.File]::ReadAllBytes($source);$sha=[Security.Cryptography.SHA256]::Create();try{$hash=[BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-','').ToLowerInvariant()}finally{$sha.Dispose()}
 $leaf=[IO.Path]::GetFileName($source);$copy=Join-Path $build $leaf;$f=[IO.FileStream]::new($copy,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($bytes,0,$bytes.Length);$f.Flush($true)}finally{$f.Dispose()}
 $held.Add([IO.FileStream]::new($copy,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read));$inputs+=@([ordered]@{file=$leaf;sha256=$hash;bytes=$bytes.Length})
}
$compileSources=@($sources|ForEach-Object{Join-Path $build ([IO.Path]::GetFileName($_))})
[IO.File]::WriteAllText((Join-Path $build 'INPUT_SOURCES.json'),($inputs|ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
function Tool([string]$Exe,[string[]]$Arguments,[string]$Label){
 [IO.File]::WriteAllText((Join-Path $build ($Label+'.command.json')),(@{exe=$Exe;arguments=$Arguments}|ConvertTo-Json -Depth 4),[Text.UTF8Encoding]::new($false))
 $r=[P309BuildToolRunnerV10]::Run($Exe,(($Arguments|ForEach-Object{'"'+$_+'"'})-join' '),$build,60000)
 foreach($stream in @('Stdout','Stderr')){$v=$r.$stream;[IO.File]::WriteAllBytes((Join-Path $build ($Label+'.'+$stream.ToLowerInvariant()+'.bin')),$v.Bytes);[IO.File]::WriteAllText((Join-Path $build ($Label+'.'+$stream.ToLowerInvariant()+'.txt')),[string]$v.Text,[Text.UTF8Encoding]::new($false))}
 [IO.File]::WriteAllText((Join-Path $build ($Label+'.result.json')),($r|ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
 if($r.Unknown-or$r.TimedOut-or$r.ExitCode-ne 0){throw ($Label+' failed/UNKNOWN; preserve bounded streams and owned process state; no automatic retry')}
}
try{
$taskOriginalTemp=$env:TEMP;$taskOriginalTmp=$env:TMP
try{$env:TEMP=$build;$env:TMP=$build;Add-Type -TypeDefinition ([IO.File]::ReadAllText((Join-Path $build 'BuildToolRunner.cs'))) -Language CSharp}finally{$env:TEMP=$taskOriginalTemp;$env:TMP=$taskOriginalTmp}
Tool $compiler (@('/nologo','/target:library','/platform:x64','/optimize+','/warnaserror+',('/out:'+(Join-Path $build 'P309HostAnchorV10.dll')))+$compileSources) 'compile-production'
Tool $compiler (@('/nologo','/target:exe','/platform:x64','/optimize+','/warnaserror+','/define:P309_TESTS',('/out:'+(Join-Path $build 'TestHostAnchor.exe')))+$compileSources+(Join-Path $build 'TestHostAnchor.cs')+(Join-Path $build 'BuildToolRunner.cs')) 'compile-tests'
foreach($leaf in @('P309HostAnchorV10.dll','TestHostAnchor.exe')){$held.Add([IO.FileStream]::new((Join-Path $build $leaf),[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read))}
Tool (Join-Path $build 'TestHostAnchor.exe') @($testRoot) 'unit-tests'
$result=[ordered]@{scope='ORDINARY_BUILD_AND_OWNED_TEMP_FILE_TESTS_ONLY';inputs=$inputs;compiler=$compiler;compiler_sha256=(Get-FileHash -LiteralPath $compiler -Algorithm SHA256).Hash.ToLowerInvariant();build=$build;test_root=$testRoot;production_factory_calls=0;production_host_queries=0;owned_temp_native_file_metadata_calls=$true;uac=0;services_changed=0;production_directories_created=0;keys_created=0;vm=0;trace=0;I1_I7='OPEN';admission='BLOCKED';production_validation=$false}
[IO.File]::WriteAllText((Join-Path $build 'BUILD_TEST_RESULT.json'),($result|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
$result|ConvertTo-Json -Depth 8
}finally{foreach($handle in $held){$handle.Dispose()}}
