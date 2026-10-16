# This template is DATA. Do not elevate this file or dot-source it.
# The approving operator/agent supplies these two data fields from the actual
# human reply. It sends the resulting exact text as -EncodedCommand to the
# absolute inbox Windows PowerShell binary, with a clean process environment.
$approvalDigest='__APPROVAL_RECORD_SHA256_AFTER_ACTUAL_HUMAN_APPROVAL__'
$approvalPath='D:\ReBaseGuard-309\records\p309-i2-v2-human-approval.json'
$scriptPath='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v2\Run-I2Feasibility.ps1'
$scriptDigest='502f211b09d17845604f048c6face9ef067a2e410c677dcfdd0ffefcc13866bf'
$ErrorActionPreference='Stop'
$PSModuleAutoLoadingPreference='None'
if($approvalDigest -notmatch '^[0-9a-f]{64}$') {throw 'No recorded human execution approval'}
if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1) {throw 'Wrong interpreter'}
# Paths are read as untrusted bytes. No script, manifest, pins or module from
# the checkout is executed before comparison to constants in this command.
$hasher=[Security.Cryptography.SHA256]::Create()
try {
    $scriptBytes=[IO.File]::ReadAllBytes($scriptPath)
    $actual=[BitConverter]::ToString($hasher.ComputeHash($scriptBytes)).Replace('-','').ToLowerInvariant()
    if($actual -cne $scriptDigest) {throw 'Harness byte binding failed'}
    $approvedBytes=[IO.File]::ReadAllBytes($approvalPath)
    $actual=[BitConverter]::ToString($hasher.ComputeHash($approvedBytes)).Replace('-','').ToLowerInvariant()
    if($actual -cne $approvalDigest) {throw 'Approval byte binding failed'}
} finally {$hasher.Dispose()}
$env:PSModulePath='C:\Windows\System32\WindowsPowerShell\v1.0\Modules'
Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1' -ErrorAction Stop
Import-Module 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Management\Microsoft.PowerShell.Management.psd1' -ErrorAction Stop
# Same bytes, no reopening mutable scriptPath. Pins are inside those bytes.
$block=[ScriptBlock]::Create([Text.Encoding]::UTF8.GetString($scriptBytes))
& $block -ApprovalBytes $approvedBytes -VerifiedHarnessSha256 $scriptDigest
