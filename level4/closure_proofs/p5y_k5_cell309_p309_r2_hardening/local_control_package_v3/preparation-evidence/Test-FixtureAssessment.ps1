param([Parameter(Mandatory=$true)][string]$Source,[Parameter(Mandatory=$true)][string]$HistoricalGuard)
$ErrorActionPreference='Stop';Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.Major -ne 5) {throw 'Windows PowerShell 5.1 required'}
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($Source,[ref]$tokens,[ref]$errors)
if($errors.Count) {throw 'parse'}
$fn=@($ast.FindAll({param($a) $a -is [Management.Automation.Language.FunctionDefinitionAst] -and $a.Name -ceq 'Get-FixtureSummary'},$true))
if($fn.Count -ne 1){throw 'unique assessment function required'}
# Extract this pure function only; never execute the harness top level.
. ([ScriptBlock]::Create($fn[0].Extent.Text))
$actual=@(Get-Content -LiteralPath $HistoricalGuard | ForEach-Object {$_ | ConvertFrom-Json} | Where-Object {$_.PSObject.Properties.Name -contains 'job_total'})
$names=[Collections.Generic.List[string]]::new()
function Check([string]$name,[scriptblock]$body){& $body;$names.Add($name)}
function Clone($v){$v | ConvertTo-Json -Depth 8 | ConvertFrom-Json}
function Reject($rows){$rejected=$false;try{$null=Get-FixtureSummary $rows}catch{$rejected=$true};if(-not $rejected){throw 'accepted invalid evidence'}}
Check 'actual three Jobs survive missing guard-clean without claiming WHP success' {
 $v=Get-FixtureSummary $actual;if(-not $v.native_fixture_clean -or $v.whp_fixture_clean -or $v.admission -cne 'BLOCKED'){throw 'actual regression'}
}
$whp=Clone $actual[0];$whp.scope='OWNED_WHP_COUNTER_FIXTURE_ONLY';$whp.pid=999999
$all=@($actual)+@($whp)
Check 'synthetic four complete records stay BLOCKED' {$v=Get-FixtureSummary $all;if(-not $v.native_fixture_clean -or -not $v.whp_fixture_clean -or $v.admission -cne 'BLOCKED'){throw 'baseline'}}
Check 'missing native record not clean' {$v=Get-FixtureSummary @($actual[0],$actual[1],$whp);if($v.native_fixture_clean){throw 'missing'}}
Check 'duplicate generation rejected' {Reject (@($all)+@($actual[0]))}
Check 'unknown scope rejected' {$r=Clone $whp;$r.scope='OTHER';Reject (@($actual)+@($r))}
Check 'active process rejected' {$r=Clone $whp;$r.job_active=1;Reject (@($actual)+@($r))}
Check 'extra Job member rejected' {$r=Clone $whp;$r.job_total=2;Reject (@($actual)+@($r))}
Check 'nonzero child exit rejected' {$r=Clone $whp;$r.exit_code=92;Reject (@($actual)+@($r))}
Check 'negative PID rejected' {$r=Clone $whp;$r.pid=-1;Reject (@($actual)+@($r))}
Check 'reversed lifetime rejected' {$r=Clone $whp;$r.exit_filetime=$r.creation_filetime-1;Reject (@($actual)+@($r))}
Check 'missing identity rejected' {$r=Clone $whp;$r.PSObject.Properties.Remove('creation_filetime');Reject (@($actual)+@($r))}
Check 'string numeric rejected' {$r=Clone $whp;$r.pid='999999';Reject (@($actual)+@($r))}
Check 'string bool rejected' {$r=Clone $whp;$r.atomic_job_assignment='true';Reject (@($actual)+@($r))}
Check 'inherited handles rejected' {$r=Clone $whp;$r.handle_inheritance=$true;Reject (@($actual)+@($r))}
Check 'non-atomic assignment rejected' {$r=Clone $whp;$r.atomic_job_assignment=$false;Reject (@($actual)+@($r))}
Check 'missing kill-on-close rejected' {$r=Clone $whp;$r.kill_on_close=$false;Reject (@($actual)+@($r))}
Check 'no records no success' {$v=Get-FixtureSummary @();if($v.native_fixture_clean -or $v.whp_fixture_clean){throw 'empty'}}
@{scope='PURE_SAVED_DATA_ASSESSMENT_NO_LIVE_CALLS';passed=$names.Count;tests=$names.ToArray();winps=$PSVersionTable.PSVersion.ToString();admission='BLOCKED'} | ConvertTo-Json -Depth 5
