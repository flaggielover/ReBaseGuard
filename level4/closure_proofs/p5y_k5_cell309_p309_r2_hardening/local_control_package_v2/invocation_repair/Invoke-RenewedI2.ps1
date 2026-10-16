param([switch]$LibraryOnly,[byte[]]$RenewedConsentBytes,[string]$RenewedConsentDigest)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest

function Assert-I2EvidenceSpace([long]$AvailableBytes) {
    if($AvailableBytes -lt 1073741824) {throw 'insufficient evidence space before UAC; minimum 1073741824 bytes'}
}
function Invoke-I2RecordedOperation([scriptblock]$Operation,[scriptblock]$RecordOutput) {
    $state=[ordered]@{completed=$false;output_count=0;failure=$null}
    try {
        & $Operation | ForEach-Object {
            $null=& $RecordOutput $_
            $state.output_count++
        }
        $state.completed=$true
    } catch {$state.failure=$_.Exception.Message}
    [pscustomobject]$state
}
# Test imports define only the two functions above. No host APIs/files/processes.
if($LibraryOnly) {return}
if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) {throw 'Windows PowerShell 5.1 required'}
if($null -eq $RenewedConsentBytes -or $RenewedConsentDigest -notmatch '^[0-9a-f]{64}$') {throw 'separate renewed human consent required'}
function Hash-I2Bytes([byte[]]$b) {
    $sha=[Security.Cryptography.SHA256]::Create()
    try{[BitConverter]::ToString($sha.ComputeHash($b)).Replace('-','').ToLowerInvariant()}finally{$sha.Dispose()}
}
if((Hash-I2Bytes $RenewedConsentBytes) -cne $RenewedConsentDigest){throw 'renewed consent byte digest differs'}
$consent=[Text.Encoding]::UTF8.GetString($RenewedConsentBytes)|ConvertFrom-Json
$original='54d366f2bb2a2f39199028193fd4a30e4357c4abc9abc55661f8766ac4483f38'
if($consent.scope -cne 'P309_I2_ONE_RENEWED_ATTEMPT_V3' -or $consent.attempt_count -ne 1 -or
   $consent.source_commit -cne '02c8fd500e643bfffd553ac0aa78c54670e2099f' -or
   $consent.original_approval_sha256 -cne $original -or
   [string]::IsNullOrWhiteSpace($consent.human_message_reference)){throw 'renewed consent scope differs'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner only'}
$private='C:\Users\Lenovo\P309-I2-build-20261016-v4'
$source=[IO.File]::ReadAllBytes((Join-Path $private 'Launch-Approved.ps1'))
if((Hash-I2Bytes $source) -cne '2da80a3b3b4b666b9e40c145bad82106084b22025e03f6ea20203ff2eed47563'){throw 'immutable launcher differs'}
$originalBytes=[IO.File]::ReadAllBytes('D:\ReBaseGuard-309\records\p309-i2-v2-human-approval.json')
if((Hash-I2Bytes $originalBytes) -cne $original){throw 'original approval history differs'}
# Read-only early check. Elevated harness retains its independent same threshold.
$available=[IO.DriveInfo]::new('C').AvailableFreeSpace
Assert-I2EvidenceSpace $available
if([IO.Directory]::Exists('C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v2') -or
   [IO.File]::Exists('C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v2')){throw 'capture root collision; no adoption or retry'}
$attempt=Join-Path $private 'renewed-attempt-v3'
if([IO.Directory]::Exists($attempt) -or [IO.File]::Exists($attempt)){throw 'attempt already recorded; no retry'}
$null=[IO.Directory]::CreateDirectory($attempt)
function Write-I2New([string]$Name,[byte[]]$Bytes) {
    $f=[IO.FileStream]::new((Join-Path $attempt $Name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
    try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}
}
function Write-I2Json([string]$Name,$Value) {Write-I2New $Name ([Text.Encoding]::UTF8.GetBytes(($Value|ConvertTo-Json -Depth 8)))}
Write-I2New 'renewed-human-consent-used.json' $RenewedConsentBytes
Write-I2Json 'ATTEMPT.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');original_approval_sha256=$original;renewed_consent_sha256=$RenewedConsentDigest;available_evidence_bytes=$available;attempt_count=1;automatic_retry=$false;admission='BLOCKED'})
$block=[ScriptBlock]::Create([Text.Encoding]::UTF8.GetString($source))
$cursor=[pscustomobject]@{Index=0}
$operation={& $block -ApprovalDigest $original}
$sink={
    param($Item)
    $name=('launcher-output-{0:D3}.json' -f $cursor.Index)
    Write-I2New $name ([Text.Encoding]::UTF8.GetBytes([string]$Item))
    $cursor.Index++
}
# Persist each output before a subsequent terminating error can discard an assignment.
$result=Invoke-I2RecordedOperation $operation $sink
Write-I2Json 'COMPLETION.json' ([ordered]@{utc=[DateTime]::UtcNow.ToString('o');operation=$result;admission='BLOCKED';I1_I7='OPEN'})
if(-not $result.completed){throw $result.failure}
$result
