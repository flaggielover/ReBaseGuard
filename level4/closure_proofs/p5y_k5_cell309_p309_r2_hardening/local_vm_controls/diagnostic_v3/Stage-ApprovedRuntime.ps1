#requires -Version 7.0
param([Parameter(Mandatory)][string]$ApprovalRecord)
$ErrorActionPreference='Stop'
$a=Get-Content -LiteralPath $ApprovalRecord -Raw|ConvertFrom-Json
if($a.scope -ne 'P309_LOCAL_VM_DIAGNOSTIC_V3' -or $a.stage_exact_runtime -ne $true -or -not $a.human_message_reference){throw 'New staging approval required'}
foreach($binding in @(@{file=$PSCommandPath;hash=$a.staging_sha256},@{file=(Join-Path $PSScriptRoot 'RuntimePreflight.ps1');hash=$a.preflight_sha256})){
 if((Get-FileHash -LiteralPath $binding.file).Hash.ToLowerInvariant() -ne $binding.hash){throw 'Staging source mismatch'}
}
. (Join-Path $PSScriptRoot 'RuntimePreflight.ps1')
$source='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1'
$target='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3'
$list='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1.sha256'
$newList='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3.sha256'
if((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath $newList)){throw 'Target collision; preserve partial attempt, no automatic overwrite'}
$plan=Get-BoundRuntime -Root $source -HashList $list -ExpectedListHash $a.runtime_hashlist_sha256 -AllowSourceExtras
if($plan.file_count -ne 222 -or $plan.total_bytes -ne 459552711){throw 'Unexpected runtime selection'}
if((Get-PSDrive D).Free -lt 42000000000L){throw 'Insufficient staging space'}
Assert-NoReparse ([IO.Path]::GetDirectoryName($target))
New-Item -ItemType Directory -Path $target|Out-Null
foreach($entry in $plan.selected_files){
 $destination=Join-Path $target $entry.relative
 New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($destination))|Out-Null
 Assert-NoReparse ([IO.Path]::GetDirectoryName($destination))
 Copy-Item -LiteralPath (Join-Path $source $entry.relative) -Destination $destination
}
Copy-Item -LiteralPath $list -Destination $newList
$verified=Get-BoundRuntime -Root $target -HashList $newList -ExpectedListHash $a.runtime_hashlist_sha256
@{staged_files=$verified.file_count;bytes=$verified.total_bytes;source_extra_files_preserved=$plan.extra_files;target=$target;vm_started=$false;admission='BLOCKED'}|ConvertTo-Json -Depth 5
