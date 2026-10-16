# DATA for the fixed native entry; never elevate this mutable file.
$approvalDigest='__APPROVAL_RECORD_SHA256_AFTER_ACTUAL_HUMAN_APPROVAL__'
$approvalPath='D:\ReBaseGuard-309\records\p309-facts-repair-v1-human-approval.json'
$scriptPath='C:\Users\Lenovo\P309-FactsRepair-build-20261016-v1\Read-FactsRepair.ps1'
$scriptDigest='__HARNESS_SHA256__'
$corePath='C:\Users\Lenovo\P309-FactsRepair-build-20261016-v1\FactsReadCore.cs'
$coreDigest='__CORE_SHA256__'
$ErrorActionPreference='Stop';$PSModuleAutoLoadingPreference='None'
if($approvalDigest-notmatch'^[0-9a-f]{64}$'){throw 'no actual human execution approval'}
if($PSVersionTable.PSVersion.Major-ne 5-or$PSVersionTable.PSVersion.Minor-ne 1){throw 'wrong interpreter'}
function Hash-Input([byte[]]$Bytes){$h=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($h.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}}
$scriptBytes=[IO.File]::ReadAllBytes($scriptPath);if((Hash-Input $scriptBytes)-cne$scriptDigest){throw 'harness binding differs'}
$coreBytes=[IO.File]::ReadAllBytes($corePath);if((Hash-Input $coreBytes)-cne$coreDigest){throw 'core binding differs'}
$approvedBytes=[IO.File]::ReadAllBytes($approvalPath);if((Hash-Input $approvedBytes)-cne$approvalDigest){throw 'approval binding differs'}
$env:PSModulePath='C:\Windows\System32\WindowsPowerShell\v1.0\Modules'
Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1' -ErrorAction Stop
Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Management\Microsoft.PowerShell.Management.psd1' -ErrorAction Stop
# Both executable inputs are the same memory bytes verified above.
& ([ScriptBlock]::Create([Text.Encoding]::UTF8.GetString($scriptBytes))) -ApprovalBytes $approvedBytes -VerifiedHarnessSha256 $scriptDigest -CoreBytes $coreBytes
