#requires -Version 7.0
param([Parameter(Mandatory)][string]$ScratchDirectory)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $ScratchDirectory){throw 'Scratch collision'}
New-Item -ItemType Directory -Path $ScratchDirectory|Out-Null
$cases=@(
 @{scope='P309_LOCAL_VM_FEASIBILITY_V1';fixed_probe_batch=$true;human_message_reference='synthetic';maximum_launches=2},
 @{scope='P309_LOCAL_VM_DETACHED_V4';fixed_probe_batch=$false;human_message_reference='synthetic';maximum_launches=2},
 @{scope='P309_LOCAL_VM_DETACHED_V4';fixed_probe_batch=$true;human_message_reference='';maximum_launches=2},
 @{scope='P309_LOCAL_VM_DETACHED_V4';fixed_probe_batch=$true;human_message_reference='synthetic';maximum_launches=3}
)
$count=0
foreach($case in $cases){
 $count++
 $path=Join-Path $ScratchDirectory "rejected-$count.json"
 $case|ConvertTo-Json|Set-Content -LiteralPath $path
 $rejected=$false
 try {& (Join-Path $PSScriptRoot 'Run-ApprovedDetached.ps1') -ApprovalRecord $path -EvidenceDirectory 'D:\ReBaseGuard-309\records\never-launched-by-unit-tests'}
 catch {if($_.Exception.Message -eq 'New exact detached-batch approval required'){$rejected=$true}else{throw}}
 if(-not $rejected){throw "Gate case $count accepted unexpectedly"}
}
"Approval-gate checks passed: $count; rejected before host queries/native execution"
