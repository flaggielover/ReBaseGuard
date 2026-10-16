#requires -Version 7.0
param([Parameter(Mandatory)][string]$ScratchDirectory)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $ScratchDirectory){throw 'Fixture collision'}
New-Item -ItemType Directory -Path $ScratchDirectory|Out-Null
. (Join-Path $PSScriptRoot 'RuntimePreflight.ps1')
$root=Join-Path $ScratchDirectory 'runtime';New-Item -ItemType Directory -Path $root|Out-Null
$item=Join-Path $root 'bound.bin';[IO.File]::WriteAllText($item,'synthetic data only')
$hash=(Get-FileHash -LiteralPath $item).Hash.ToLowerInvariant()
$list=Join-Path $ScratchDirectory 'fixture.sha256'
function Write-List([string]$text){[IO.File]::WriteAllText($list,$text);(Get-FileHash -LiteralPath $list).Hash.ToLowerInvariant()}
$pin=Write-List "$hash  bound.bin`n"
$count=0
$valid=Get-BoundRuntime -Root $root -HashList $list -ExpectedListHash $pin
if($valid.file_count -ne 1){throw 'Valid fixture rejected'};$count++
[IO.File]::WriteAllText((Join-Path $root 'unexpected-cache.db'),'synthetic cache')
$rejected=$false;try{Get-BoundRuntime -Root $root -HashList $list -ExpectedListHash $pin|Out-Null}catch{if($_.Exception.Message -like 'Unlisted runtime*'){$rejected=$true}else{throw}}
if(-not $rejected){throw 'Unexpected cache accepted'};$count++
$sourcePlan=Get-BoundRuntime -Root $root -HashList $list -ExpectedListHash $pin -AllowSourceExtras
if($sourcePlan.file_count -ne 1 -or $sourcePlan.extra_files.Count -ne 1){throw 'Source selection contaminated'};$count++
foreach($case in @('digest','duplicate','escape','missing')){
 $text=switch($case){'digest'{('0'*64)+"  bound.bin`n"};'duplicate'{"$hash  bound.bin`n$hash  bound.bin`n"};'escape'{"$hash  ../outside.bin`n"};'missing'{"$hash  absent.bin`n"}}
 $pin=Write-List $text;$rejected=$false
 try{Get-BoundRuntime -Root $root -HashList $list -ExpectedListHash $pin -AllowSourceExtras|Out-Null}catch{$rejected=$true}
 if(-not $rejected){throw "Bad fixture accepted: $case"};$count++
}
"Runtime preflight regression checks passed: $count; only synthetic fixture files, no VM/native launch"
