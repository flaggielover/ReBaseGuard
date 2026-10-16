#requires -Version 7.0
param([Parameter(Mandatory)][string]$ScratchDirectory)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $ScratchDirectory){throw 'Scratch collision'}
New-Item -ItemType Directory -Path $ScratchDirectory|Out-Null
$cases=@(
 @{scope='P309_LOCAL_VM_FEASIBILITY_V1';single_deadline_probe=$true;human_message_reference='synthetic';maximum_launches=1},
 @{scope='P309_LOCAL_VM_DIAGNOSTIC_V2';single_deadline_probe=$false;human_message_reference='synthetic';maximum_launches=1},
 @{scope='P309_LOCAL_VM_DIAGNOSTIC_V2';single_deadline_probe=$true;human_message_reference='';maximum_launches=1},
 @{scope='P309_LOCAL_VM_DIAGNOSTIC_V2';single_deadline_probe=$true;human_message_reference='synthetic';maximum_launches=2}
)
$count=0
foreach($case in $cases){
 $count++
 $path=Join-Path $ScratchDirectory "rejected-$count.json"
 $case|ConvertTo-Json|Set-Content -LiteralPath $path
 $rejected=$false
 try {& (Join-Path $PSScriptRoot 'Run-ApprovedDiagnostic.ps1') -ApprovalRecord $path -EvidenceDirectory 'D:\ReBaseGuard-309\records\never-launched-by-unit-tests'}
 catch {if($_.Exception.Message -eq 'New exact diagnostic approval required'){$rejected=$true}else{throw}}
 if(-not $rejected){throw "Gate case $count accepted unexpectedly"}
}
"Approval-gate checks passed: $count; rejected before host queries/native execution"
