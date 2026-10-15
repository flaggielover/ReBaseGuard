param(
 [Parameter(Mandatory=$true)][string]$ApprovalRecord,
 [Parameter(Mandatory=$true)][string]$EvidenceDirectory
)
# This is a separately approved Windows mutation, NEVER a preparation/test command.
# A local JSON file is only a transcript reference; it cannot grant formal authority.
$ErrorActionPreference='Stop'
$approval=Get-Content -LiteralPath $ApprovalRecord -Raw | ConvertFrom-Json
if($approval.scope -ne 'P309_LOCAL_VM_FEASIBILITY_V1' -or $approval.whp_feature_enable -ne $true -or
   -not $approval.human_message_reference){throw 'Explicit human approval reference is required'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
$principal=[Security.Principal.WindowsPrincipal]::new($identity)
if(-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Run only through approved UAC elevation'}
$evidence=[IO.Path]::GetFullPath($EvidenceDirectory)
$base='D:\ReBaseGuard-309\records\'
if(-not $evidence.StartsWith($base,[StringComparison]::OrdinalIgnoreCase)){throw 'Evidence must remain under records'}
if(Test-Path -LiteralPath $evidence){throw 'Evidence directory exists; choose a fresh attempt, never overwrite'}
New-Item -ItemType Directory -Path $evidence | Out-Null
$before=Get-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform
$before | Select-Object FeatureName,State,RestartRequired | ConvertTo-Json | Set-Content "$evidence\feature-before.json"
if($before.State.ToString() -eq 'Enabled'){
 @{changed=$false;restart_performed=$false;admission='BLOCKED'} | ConvertTo-Json | Set-Content "$evidence\result.json"
 return
}
if($before.State.ToString() -ne 'Disabled'){throw 'Pending/removed/unknown feature state requires investigation, not blind enable'}
try {
 # No payload download, no automatic restart, no change to WSL/VMP/power/update policy.
 $result=Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform -NoRestart -LimitAccess
 $result | Select-Object Online,RestartNeeded | ConvertTo-Json | Set-Content "$evidence\servicing-result.json"
} catch {
 $_ | Out-String | Set-Content "$evidence\servicing-error.txt"
 throw
} finally {
 Get-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform |
  Select-Object FeatureName,State,RestartRequired | ConvertTo-Json | Set-Content "$evidence\feature-after.json"
}
@{changed=$true;restart_performed=$false;admission='BLOCKED';
  note='If RestartNeeded or pending state, return to user for the approved manual restart; do not run VM yet'} |
 ConvertTo-Json | Set-Content "$evidence\result.json"
