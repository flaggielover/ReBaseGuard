param([switch]$ReadOnlyPreflight,[byte[]]$ApprovalBytes,[string]$ApprovalDigest)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.Major-ne 5-or$PSVersionTable.PSVersion.Minor-ne 1){throw 'WinPS 5.1 required'}
function Hash-FactsBytes([byte[]]$Bytes){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
function Assert-FactsAbsent([string]$Path){try{$null=[IO.File]::GetAttributes($Path)}catch{$hr=$_.Exception.GetBaseException().HResult;if($hr-in@(-2147024894,-2147024893)){return};throw};throw 'collision/consumed attempt; no adoption or retry'}
function Write-NewFacts([string]$Path,[byte[]]$Bytes){$f=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner only'}
$private='C:\Users\Lenovo\P309-FactsRepair-build-20261016-v1'
$source=[IO.File]::ReadAllBytes((Join-Path $private 'Launch-Approved.ps1'))
if((Hash-FactsBytes $source)-cne'__LAUNCHER_SHA256__'){throw 'launcher binding differs'}
$available=[IO.DriveInfo]::new('C').AvailableFreeSpace;$archiveAvailable=[IO.DriveInfo]::new('D').AvailableFreeSpace
if($available-lt 536870912-or$archiveAvailable-lt 536870912){throw 'before UAC: 512 MiB C/D reserve required'}
$capture='C:\ProgramData\ReBaseGuardP309-FactsRepair-v1';$attempt=Join-Path $private 'one-approved-attempt'
foreach($path in @($capture,$attempt)){Assert-FactsAbsent $path}
$block=[ScriptBlock]::Create([Text.Encoding]::UTF8.GetString($source))
if($ReadOnlyPreflight){& $block -ReadOnlyPreflight;@{available_bytes=$available;archive_available_bytes=$archiveAvailable;fresh_paths=$true;uac=0;host_queries=0;admission='BLOCKED'}|ConvertTo-Json;return}
if($null-eq$ApprovalBytes-or$ApprovalDigest-notmatch'^[0-9a-f]{64}$'-or(Hash-FactsBytes $ApprovalBytes)-cne$ApprovalDigest){throw 'fresh actual human approval required'}
$approval=[Text.Encoding]::UTF8.GetString($ApprovalBytes)|ConvertFrom-Json
if($approval.scope-cne'P309_SINGLE_ELEVATED_READONLY_FACTS_REPAIR_V1'-or$approval.count-ne 1-or$approval.code_source_commit-cne'__INPUT_SOURCE_COMMIT__'-or$approval.native_sha256-cne'__NATIVE_SHA256__'-or$approval.harness_sha256-cne'__HARNESS_SHA256__'-or$approval.core_sha256-cne'__CORE_SHA256__'-or[string]::IsNullOrWhiteSpace($approval.human_message_reference)){throw 'approval scope/bindings differ'}
$stored=[IO.File]::ReadAllBytes('D:\ReBaseGuard-309\records\p309-facts-repair-v1-human-approval.json')
if((Hash-FactsBytes $stored)-cne$ApprovalDigest){throw 'stored approval differs'}
$null=[IO.Directory]::CreateDirectory($attempt)
Write-NewFacts (Join-Path $attempt 'human-consent-used.json') $ApprovalBytes
Write-NewFacts (Join-Path $attempt 'ATTEMPT.json') ([Text.Encoding]::UTF8.GetBytes((@{utc=[DateTime]::UtcNow.ToString('o');consent_sha256=$ApprovalDigest;available_bytes=$available;archive_available_bytes=$archiveAvailable;attempt_count=1;automatic_retry=$false;admission='BLOCKED'}|ConvertTo-Json)))
$index=0;$failure=$null
try{
 & $block -ApprovalDigest $ApprovalDigest | ForEach-Object {Write-NewFacts (Join-Path $attempt ('launcher-output-{0:D3}.json'-f$index)) ([Text.Encoding]::UTF8.GetBytes([string]$_));$index++}
}catch{$failure=$_.Exception.Message}
Write-NewFacts (Join-Path $attempt 'COMPLETION.json') ([Text.Encoding]::UTF8.GetBytes((@{utc=[DateTime]::UtcNow.ToString('o');output_count=$index;completed=($null-eq$failure);failure=$failure;automatic_retry=$false;admission='BLOCKED';I1_I7='OPEN'}|ConvertTo-Json)))
if($null-ne$failure){throw $failure}
@{completed=$true;output_count=$index;failure=$null;admission='BLOCKED'}|ConvertTo-Json
