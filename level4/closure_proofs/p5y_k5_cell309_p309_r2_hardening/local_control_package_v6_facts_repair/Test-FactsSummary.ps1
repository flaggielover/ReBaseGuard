$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
$path=Join-Path $PSScriptRoot 'Read-FactsRepair.ps1'
. ([ScriptBlock]::Create([Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($path)))) -LibraryOnly
$tests=[Collections.Generic.List[string]]::new()
function Check([string]$Name,[scriptblock]$Test){& $Test;$tests.Add($Name)}
function Assert($Value){if(-not$Value){throw 'assertion failed'}}
function Item([string]$Id,[string]$State,[string[]]$Errors=@()){[pscustomobject]@{id=$Id;state=$State;cleanup_errors=$Errors}}
Check 'partial-success-retains-unknown-and-missing' {
 $s=Get-FactsSummary @('etw','power','lsa','service') @((Item 'etw' 'OBSERVED'),(Item 'power' 'UNKNOWN'),(Item 'lsa' 'NOT_FOUND_DIRECT_RIGHTS_NOT_ENUMERATED'))
 Assert ($s.completed_items-eq 3);Assert ($s.unknown_items.Count-eq 2);Assert ($s.not_attempted_items.Count-eq 1);Assert ($s.not_attempted_items[0]-ceq'service');Assert (-not$s.installation_ready);Assert ($s.formal_admission-ceq'BLOCKED')
}
Check 'cleanup-failure-does-not-disappear' {$s=Get-FactsSummary @('x') @((Item 'x' 'OBSERVED' @('Close failed')));Assert ($s.cleanup_errors.Count-eq 1);Assert ($s.cleanup_errors[0].error-ceq'Close failed')}
Check 'duplicate-refused' {$caught=$false;try{$null=Get-FactsSummary @('x') @((Item 'x' 'OBSERVED'),(Item 'x' 'OBSERVED'))}catch{$caught=$true};Assert $caught}
Check 'unexpected-refused' {$caught=$false;try{$null=Get-FactsSummary @('x') @((Item 'y' 'OBSERVED'))}catch{$caught=$true};Assert $caught}
Check 'unrecognized-state-refused' {$caught=$false;try{$null=Get-FactsSummary @('x') @((Item 'x' 'READY'))}catch{$caught=$true};Assert $caught}
Check 'complete-observations-never-admit' {$s=Get-FactsSummary @('x') @((Item 'x' 'OBSERVED'));Assert $s.evidence_set_complete;Assert (-not$s.installation_ready);Assert ($s.I1_I7-ceq'OPEN')}
Check 'path-errors-conservative' {Assert ((Get-RecordedPathState -2147024894)-ceq'ABSENT');Assert ((Get-RecordedPathState -2147024893)-ceq'ABSENT');Assert ((Get-RecordedPathState -2147024891)-ceq'UNKNOWN')}
Check 'fixed-fact-set-does-not-follow-completed-items' {$ids=@(Get-ExpectedFactIds);Assert ($ids.Count-eq 28);$s=Get-FactsSummary $ids @((Item 'etw-0' 'OBSERVED'));Assert ($s.not_attempted_items.Count-eq 27);Assert (-not$s.evidence_set_complete)}
Check 'native-not-attempted-stages-retained' {$i=Item 'etw-0' 'UNKNOWN';$i|Add-Member NoteProperty data ([ordered]@{native=[pscustomobject]@{NotAttempted=@('fetch')}});$s=Get-FactsSummary @('etw-0') @($i);Assert ($s.native_not_attempted_stages.Count-eq 1);Assert ($s.native_not_attempted_stages[0].stage-ceq'fetch')}
Check 'production-observation-retains-partial-pipeline-on-failure' {$i=Invoke-FactObservation 'device-guard' {param($d) Receive-PartialFact $d 'metadata' {[pscustomobject]@{sample='first'};throw 'synthetic terminating failure'}};Assert ($i.state-ceq'UNKNOWN');Assert ($i.data.metadata.Count-eq 1);Assert ($i.data.metadata[0].sample-ceq'first');Assert (-not$i.data.metadata_complete);Assert ($i.error-match'synthetic terminating failure')}
Check 'production-observation-success-and-native-cleanup-preserved' {$i=Invoke-FactObservation 'service-0' {param($d) [pscustomobject]@{State='PRESENT';CleanupErrors=@('synthetic close failure');NotAttempted=@()}};Assert ($i.state-ceq'PRESENT');Assert ($i.cleanup_errors.Count-eq 1);Assert ($i.data.native.State-ceq'PRESENT')}
@{scope='PURE_SUPPLIED_VALUE_SUMMARY_TESTS';passed=$tests.Count;cases=$tests.ToArray();host_queries=0;uac=0;admission='BLOCKED'}|ConvertTo-Json -Depth 6
