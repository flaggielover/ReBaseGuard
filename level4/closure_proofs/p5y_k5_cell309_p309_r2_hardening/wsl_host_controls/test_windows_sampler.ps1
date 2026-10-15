# Pure synthetic data; load only two function definitions, never execute collector.
param([string]$CollectorPath=(Join-Path $PSScriptRoot 'collect_host_controls.ps1'))
$ErrorActionPreference='Stop'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($CollectorPath,[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'Collector parse error'}
foreach($node in $ast.FindAll({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -in @('HashText','MeasureProcesses','PolicyFingerprint')},$true)) {
 . ([scriptblock]::Create($node.Extent.Text))
}
$cases=[ordered]@{}
$a=@{10=@{created='one';cpu=1.0}}
$b=@{10=@{created='one';cpu=4.0}}
$r=MeasureProcesses $a $b 60
$cases.exact_cpu_fraction=$r.rows[0].cpu_fraction -eq 0.05
$cases.no_raw_creation=$r.rows[0].creation_sha256 -match '^[0-9a-f]{64}$'
$b[10].created='reused'
$cases.pid_reuse_unknown=$null -eq (MeasureProcesses $a $b 60).rows[0].cpu_fraction
$b[10].created='one';$b[10].cpu=0.5
$cases.regressed_counter_unknown=$null -eq (MeasureProcesses $a $b 60).rows[0].cpu_fraction
$b[10].cpu=$null
$cases.unreadable_counter_unknown=(MeasureProcesses $a $b 60).unreadable_count -eq 1
$b=@{11=@{created='new';cpu=0.0}}
$r=MeasureProcesses $a $b 60
$cases.new_process_unknown=$null -eq $r.rows[0].cpu_fraction
$cases.exited_process_counted=$r.disappeared_count -eq 1
$cases.zero_duration_unknown=$null -eq (MeasureProcesses $a $a 0).rows[0].cpu_fraction
$policy=[ordered]@{power_query_ok=$true;sleep_ac_s=0;sleep_dc_s=0;hibernate_ac_s=0;hibernate_dc_s=0;scheme_sha256=('a'*64);
 update_policy_values=@{AUOptions=2;NoAutoUpdate=1};update_task_states=@(@{identity_sha256=('b'*64);state='Disabled';next_run_utc=$null})}
$first=PolicyFingerprint $policy
$policy.sleep_dc_s=600
$cases.emitted_power_is_bound=(PolicyFingerprint $policy) -ne $first
$policy.sleep_dc_s=0
$policy.update_policy_values=[ordered]@{NoAutoUpdate=1;AUOptions=2}
$cases.update_key_order_is_stable=(PolicyFingerprint $policy) -eq $first
$policy.update_task_states[0].state='Ready'
$cases.emitted_task_state_is_bound=(PolicyFingerprint $policy) -ne $first
$pass=@($cases.Values | Where-Object {$_ -ne $true}).Count -eq 0
@{scope='SYNTHETIC_ONLY';cases=$cases;passed=$pass} | ConvertTo-Json -Depth 4
if(-not $pass){throw 'Synthetic sampler test failed'}
