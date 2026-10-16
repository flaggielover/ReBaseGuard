$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot 'Invoke-RenewedI2.ps1') -LibraryOnly
$checks=[Collections.Generic.List[string]]::new()
foreach($amount in @(0L,1073741823L)){
 $rejected=$false;try{Assert-I2EvidenceSpace $amount}catch{$rejected=$true}
 if(-not $rejected){throw 'space under threshold accepted'}
 $checks.Add('reject-space-'+$amount)
}
Assert-I2EvidenceSpace 1073741824L
$checks.Add('accept-original-space-boundary')
$rows=[Collections.Generic.List[string]]::new()
$state=Invoke-I2RecordedOperation { '{"pid":123,"exit_code":1}';throw 'synthetic native failure' } {param($row)$rows.Add([string]$row)}
if($state.completed -or $state.output_count -ne 1 -or $rows.Count -ne 1 -or $rows[0] -cne '{"pid":123,"exit_code":1}' -or $state.failure -cne 'synthetic native failure'){throw 'output-before-throw lost'}
$checks.Add('retain-exit-json-before-terminating-error')
$state=Invoke-I2RecordedOperation {throw 'synthetic early failure'} {param($row)throw 'unexpected sink'}
if($state.completed -or $state.output_count -ne 0 -or $state.failure -cne 'synthetic early failure'){throw 'early failure misreported'}
$checks.Add('failure-with-no-output-remains-failed')
$rows.Clear()
$state=Invoke-I2RecordedOperation {'one';'two'} {param($row)$rows.Add([string]$row)}
if(-not $state.completed -or $state.output_count -ne 2 -or $rows.Count -ne 2){throw 'successful output recording differs'}
$checks.Add('successful-output-sequence')
$count=[pscustomobject]@{Value=0}
$state=Invoke-I2RecordedOperation {$count.Value++;'before';throw 'fail'} {param($row)$null}
if($count.Value -ne 1 -or $state.completed){throw 'operation retried'}
$checks.Add('failure-never-retries-operation')
$state=Invoke-I2RecordedOperation {'result'} {param($row)throw 'synthetic persistence failure'}
if($state.completed -or $state.output_count -ne 0 -or $state.failure -cne 'synthetic persistence failure'){throw 'persistence failure marked completed'}
$checks.Add('persistence-failure-is-not-success')
[ordered]@{scope='PURE_MEMORY_INVOKER_REGRESSIONS';winps=$PSVersionTable.PSVersion.ToString();passed=$checks.Count;checks=@($checks.ToArray());production_invocations=0;uac=0;trace=0;fixture=0;admission='BLOCKED'}|ConvertTo-Json -Depth 5
