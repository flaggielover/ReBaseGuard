param([string]$Invoker)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
. $Invoker -LibraryOnly
$pass=0
Assert-RootEvidenceSpace 2147483648;$pass++
Assert-RootEvidenceSpace 4294967296;$pass++
Assert-ArchiveSpace 12884901888;$pass++
$refused=$false;try{Assert-ArchiveSpace 12884901887}catch{$refused=$true};if(-not $refused){throw 'archive low space accepted'};$pass++
$refused=$false;try{Assert-RootEvidenceSpace 2147483647}catch{$refused=$true};if(-not $refused){throw 'low space accepted'};$pass++
$refused=$false;try{Assert-RootEvidenceSpace -1}catch{$refused=$true};if(-not $refused){throw 'negative space accepted'};$pass++
$saved=[Collections.Generic.List[object]]::new();$sink={param($v)$saved.Add($v)}
$r=Invoke-RootRecordedOperation { 'before-error';throw 'exit 1' } $sink
if($r.completed -or $r.output_count -ne 1 -or $saved[0] -cne 'before-error' -or $r.failure -cne 'exit 1'){throw 'lost failure/output'};$pass++
$r=Invoke-RootRecordedOperation {'ok'} $sink;if(-not $r.completed -or $r.output_count -ne 1){throw 'success state'};$pass++
$r=Invoke-RootRecordedOperation {throw 'early'} $sink;if($r.completed -or $r.output_count -ne 0){throw 'early throw lost'};$pass++
$r=Invoke-RootRecordedOperation {'data'} {throw 'sink failed'};if($r.completed -or $r.failure -cne 'sink failed'){throw 'storage failure accepted'};$pass++
@{scope='PURE_INVOKER_MEMORY_CHECKS_NO_HOST_APIS';passed=$pass;winps=$PSVersionTable.PSVersion.ToString();admission='BLOCKED'}|ConvertTo-Json
