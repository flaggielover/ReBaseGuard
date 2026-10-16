param([switch]$LibraryOnly,[switch]$ReadOnlyPreflight,[byte[]]$ApprovalBytes,[string]$ApprovalDigest)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
function Assert-FactsEvidenceSpace([long]$AvailableBytes) {
 if($AvailableBytes -lt 536870912){throw 'before UAC: 512 MiB C: evidence reserve required'}
}
function Assert-ArchiveSpace([long]$AvailableBytes) {
 if($AvailableBytes -lt 536870912){throw 'before UAC: 512 MiB D: archive reserve required'}
}
function Invoke-FactsRecordedOperation([scriptblock]$Operation,[scriptblock]$RecordOutput) {
 $state=[ordered]@{completed=$false;output_count=0;failure=$null}
 try {& $Operation | ForEach-Object {$null=& $RecordOutput $_;$state.output_count++};$state.completed=$true}
 catch {$state.failure=$_.Exception.Message}
 [pscustomobject]$state
}
if($LibraryOnly){return}
if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1){throw 'WinPS 5.1 required'}
function Hash-FactsBytes([byte[]]$b){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($b)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
$id=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner only'}
$private='C:\Users\Lenovo\P309-InstallationFacts-build-20261016-v3'
$source=[IO.File]::ReadAllBytes((Join-Path $private 'Launch-Approved.ps1'))
if((Hash-FactsBytes $source) -cne '5fb8f21108ba8b54ac0c9929342ac7817f19da1a5423aab8da084f282cf4d1d4'){throw 'launcher binding differs'}
$available=[IO.DriveInfo]::new('C').AvailableFreeSpace;Assert-FactsEvidenceSpace $available
$archiveAvailable=[IO.DriveInfo]::new('D').AvailableFreeSpace;Assert-ArchiveSpace $archiveAvailable
$capture='C:\ProgramData\ReBaseGuardP309-InstallationFacts-v1'
$attempt=Join-Path $private 'one-approved-attempt'
foreach($path in @($capture,$attempt)){if([IO.Directory]::Exists($path)-or[IO.File]::Exists($path)){throw 'collision/consumed attempt; no adoption or retry'}}
$block=[ScriptBlock]::Create([Text.Encoding]::UTF8.GetString($source))
if($ReadOnlyPreflight){& $block -ReadOnlyPreflight;[pscustomobject]@{available_bytes=$available;archive_available_bytes=$archiveAvailable;fresh_paths=$true;uac=0;trace=0;vm=0;admission='BLOCKED'};return}
if($null -eq $ApprovalBytes -or $ApprovalDigest -notmatch '^[0-9a-f]{64}$' -or (Hash-FactsBytes $ApprovalBytes) -cne $ApprovalDigest){throw 'fresh human approval required'}
$approval=[Text.Encoding]::UTF8.GetString($ApprovalBytes)|ConvertFrom-Json
if($approval.scope -cne 'P309_SINGLE_ELEVATED_READONLY_INSTALLATION_FACTS_V1' -or $approval.count -ne 1 -or
 $approval.code_source_commit -cne 'a3a478089a9f756853efd6bc68a88d48d83909d1' -or
 $approval.native_sha256 -cne '7c8345bb9210e61b1d137754d2223c8415cd9a2623a4633c415aacfccf0cbc93' -or
 $approval.harness_sha256 -cne 'a756f9d04a418132f799be38ab5574415e7ac56dd8bf815c0eecdb951c5c52aa' -or
 [string]::IsNullOrWhiteSpace($approval.human_message_reference)){throw 'approval scope/bindings differ'}
$stored=[IO.File]::ReadAllBytes('D:\ReBaseGuard-309\records\p309-installation-facts-v1-human-approval.json')
if((Hash-FactsBytes $stored) -cne $ApprovalDigest){throw 'stored approval differs'}
$null=[IO.Directory]::CreateDirectory($attempt)
function Write-FactsNew([string]$Name,[byte[]]$Bytes){$f=[IO.FileStream]::new((Join-Path $attempt $Name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}}
function Write-FactsJson([string]$Name,$Value){Write-FactsNew $Name ([Text.Encoding]::UTF8.GetBytes(($Value|ConvertTo-Json -Depth 8)))}
Write-FactsNew 'human-consent-used.json' $ApprovalBytes
Write-FactsJson 'ATTEMPT.json' @{utc=[DateTime]::UtcNow.ToString('o');consent_sha256=$ApprovalDigest;available_bytes=$available;archive_available_bytes=$archiveAvailable;attempt_count=1;automatic_retry=$false;admission='BLOCKED'}
$cursor=[pscustomobject]@{Index=0}
$operation={& $block -ApprovalDigest $ApprovalDigest}
$sink={param($item) Write-FactsNew ('launcher-output-{0:D3}.json' -f $cursor.Index) ([Text.Encoding]::UTF8.GetBytes([string]$item));$cursor.Index++}
$result=Invoke-FactsRecordedOperation $operation $sink
Write-FactsJson 'COMPLETION.json' @{utc=[DateTime]::UtcNow.ToString('o');operation=$result;admission='BLOCKED';I1_I7='OPEN'}
if(-not $result.completed){throw $result.failure}
$result
