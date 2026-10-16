param([switch]$LibraryOnly,[switch]$ReadOnlyPreflight,[byte[]]$ApprovalBytes,[string]$ApprovalDigest)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
function Assert-RootEvidenceSpace([long]$AvailableBytes) {
 if($AvailableBytes -lt 2147483648){throw 'before UAC: 1 GiB ETL plus 1 GiB reserve required'}
}
function Assert-ArchiveSpace([long]$AvailableBytes) {
 if($AvailableBytes -lt 12884901888){throw 'before UAC: 12 GiB D: archive/expanded offline output reserve required'}
}
function Invoke-RootRecordedOperation([scriptblock]$Operation,[scriptblock]$RecordOutput) {
 $state=[ordered]@{completed=$false;output_count=0;failure=$null}
 try {& $Operation | ForEach-Object {$null=& $RecordOutput $_;$state.output_count++};$state.completed=$true}
 catch {$state.failure=$_.Exception.Message}
 [pscustomobject]$state
}
if($LibraryOnly){return}
if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1){throw 'WinPS 5.1 required'}
function Hash-RootBytes([byte[]]$b){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($b)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
$id=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'ordinary owner only'}
$private='C:\Users\Lenovo\P309-I2-root-build-20261016-v2'
$source=[IO.File]::ReadAllBytes((Join-Path $private 'Launch-Approved.ps1'))
if((Hash-RootBytes $source) -cne '0eeabd344ede7bd1247e1cecb9222c66198285e969b419eb9ef68dbb9eb99e20'){throw 'launcher binding differs'}
$available=[IO.DriveInfo]::new('C').AvailableFreeSpace;Assert-RootEvidenceSpace $available
$archiveAvailable=[IO.DriveInfo]::new('D').AvailableFreeSpace;Assert-ArchiveSpace $archiveAvailable
$capture='C:\ProgramData\ReBaseGuardP309-I2-RootDiagnostic-v3'
$attempt=Join-Path $private 'one-approved-attempt'
foreach($path in @($capture,$attempt)){if([IO.Directory]::Exists($path)-or[IO.File]::Exists($path)){throw 'collision/consumed attempt; no adoption or retry'}}
$block=[ScriptBlock]::Create([Text.Encoding]::UTF8.GetString($source))
if($ReadOnlyPreflight){& $block -ReadOnlyPreflight;[pscustomobject]@{available_bytes=$available;archive_available_bytes=$archiveAvailable;fresh_paths=$true;uac=0;trace=0;vm=0;admission='BLOCKED'};return}
if($null -eq $ApprovalBytes -or $ApprovalDigest -notmatch '^[0-9a-f]{64}$' -or (Hash-RootBytes $ApprovalBytes) -cne $ApprovalDigest){throw 'fresh human approval required'}
$approval=[Text.Encoding]::UTF8.GetString($ApprovalBytes)|ConvertFrom-Json
if($approval.scope -cne 'P309_I2_SINGLE_ROOT_DIAGNOSTIC_V3' -or $approval.capture_count -ne 1 -or $approval.whp_count -ne 1 -or
 $approval.code_source_commit -cne 'f02cddf88aaedaa3733f93daa5458612bca29990' -or
 $approval.binary_sha256 -cne '52a0c03ff26661407893e850f1e09220c46edfd58ab101fc6c2e69f96d19e96e' -or
 $approval.whp_sha256 -cne 'ea119dd56371ea265a575cdcca8ee096482c896472aabd0890a9ea4ed853657c' -or
 $approval.harness_sha256 -cne '776f9b9e890ab797382df825a5f0c921de710463dae05f0f9146093f64a61166' -or
 [string]::IsNullOrWhiteSpace($approval.human_message_reference)){throw 'approval scope/bindings differ'}
$stored=[IO.File]::ReadAllBytes('D:\ReBaseGuard-309\records\p309-i2-root-v3-human-approval.json')
if((Hash-RootBytes $stored) -cne $ApprovalDigest){throw 'stored approval differs'}
$null=[IO.Directory]::CreateDirectory($attempt)
function Write-RootNew([string]$Name,[byte[]]$Bytes){$f=[IO.FileStream]::new((Join-Path $attempt $Name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);try{$f.Write($Bytes,0,$Bytes.Length);$f.Flush($true)}finally{$f.Dispose()}}
function Write-RootJson([string]$Name,$Value){Write-RootNew $Name ([Text.Encoding]::UTF8.GetBytes(($Value|ConvertTo-Json -Depth 8)))}
Write-RootNew 'human-consent-used.json' $ApprovalBytes
Write-RootJson 'ATTEMPT.json' @{utc=[DateTime]::UtcNow.ToString('o');consent_sha256=$ApprovalDigest;available_bytes=$available;archive_available_bytes=$archiveAvailable;attempt_count=1;automatic_retry=$false;admission='BLOCKED'}
$cursor=[pscustomobject]@{Index=0}
$operation={& $block -ApprovalDigest $ApprovalDigest}
$sink={param($item) Write-RootNew ('launcher-output-{0:D3}.json' -f $cursor.Index) ([Text.Encoding]::UTF8.GetBytes([string]$item));$cursor.Index++}
$result=Invoke-RootRecordedOperation $operation $sink
Write-RootJson 'COMPLETION.json' @{utc=[DateTime]::UtcNow.ToString('o');operation=$result;admission='BLOCKED';I1_I7='OPEN'}
if(-not $result.completed){throw $result.failure}
$result
