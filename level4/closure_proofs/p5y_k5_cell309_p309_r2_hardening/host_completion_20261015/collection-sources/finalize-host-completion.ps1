param([Parameter(Mandatory=$true)][string]$RecordDir)
$ErrorActionPreference='Stop'
$wt='D:\ReBaseGuard-309\workspace\p309-host-completion-20261015'
$rel='level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/host_completion_20261015'
$dst=Join-Path $wt $rel
if(Test-Path -LiteralPath $dst){throw 'New evidence namespace already exists'}
New-Item -ItemType Directory -Path $dst | Out-Null
$before=Get-Content -LiteralPath (Join-Path $RecordDir 'preservation-before.json') -Raw | ConvertFrom-Json
$bad=@($before | Where-Object {!(Test-Path -LiteralPath $_.path) -or (Get-FileHash -LiteralPath $_.path).Hash.ToLowerInvariant() -ne $_.sha256})
if($bad.Count){throw 'Prior evidence changed'}
$src=Get-Content -LiteralPath (Join-Path $RecordDir 'source-verification.json') -Raw | ConvertFrom-Json
$heads=@(git -C $wt for-each-ref '--format=%(refname) %(objectname)' refs/heads)
if(Compare-Object @($src.existing_local_branches) $heads){throw 'Existing branch bindings changed'}
$oldChanges=@(git -C $wt diff --name-only 47118d4837ab2dd5a4ff03e66263c82754769c36)
if($LASTEXITCODE -ne 0 -or $oldChanges.Count){throw 'Tracked baseline changed'}
$blockers=(Get-Content -LiteralPath (Join-Path $wt 'level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/wsl_host_controls/isolation_contract_revision_20261015/REVISION.json') -Raw | ConvertFrom-Json).unresolved_original_blockers
$windows=Get-Content -LiteralPath (Join-Path $RecordDir 'windows-readiness.json') -Raw | ConvertFrom-Json
$linux=Get-Content -LiteralPath (Join-Path $RecordDir 'ubuntu-readiness-existing-path.json') -Raw | ConvertFrom-Json
$runtime=Get-Content -LiteralPath (Join-Path $RecordDir 'runtime-inventory.json') -Raw | ConvertFrom-Json
$followup=Get-Content -LiteralPath (Join-Path $RecordDir 'ubuntu-followup.json') -Raw | ConvertFrom-Json
$status=[ordered]@{
 schema='P309_HOST_COMPLETION_INVESTIGATION/1';utc=[DateTime]::UtcNow.ToString('o');source_commit='47118d4837ab2dd5a4ff03e66263c82754769c36';publication_branch='codex/p309-host-completion-20261015'
 overall_task_complete=$false;formal_admission='BLOCKED';independent_admission_review_performed=$false;formal_audit_8a_executed=$false;formal_verdict_8b_issued=$false
 disposition='CURRENT_WSL_DESIGN_NOT_DEPLOYABLE; NATIVE_HOST_ACCESS_AND_OPERATOR_FACTS_REQUIRED';route_recommendation='Audit originally designated native AWS worker before any mutation; not an acceptance or purchase'
 scope_limit='Vendor boundary statement plus actual container/policy/resource metadata; not a local escape exploit or proof that all possible redesigned WSL architectures are impossible'
 installation_package_ready=$false;installation_package_blocker='No accepted containment architecture or native destination facts; cannot truthfully specify actual host mutations'
 unresolved_original_blockers=$blockers;source_verification=@{current_files=141;rereview_records=2;protected_files=20;historic_bindings=624;result='MATCH'}
 windows=$windows;linux=$linux.linux;current_interpreter=$followup.interpreter;runtime_inventory=@{count=$runtime.entry_count;errors=$runtime.errors;sha256=$runtime.manifest_sha256;immutable_snapshot=$false;external_dependencies_complete=$false;fresh_installed_pin=$false}
 historical_cloud_tests=157;historical_math_fixtures=18;historical_session_chain_fixtures=12;historical_extra_time_widths=@(2048);tests_run_this_turn=0
 host_safety_sampling=0;tracing_sessions_started=0;accounts_services_keys_endpoints_units_created=0;policy_changes=0;installs=0;elevations=0;drills=0;qualifications=0;target_evaluations=0;freeze_or_grants_issued=$false
 prior_record_files_verified_unchanged=$before.Count;existing_branches_preserved=$true;backup_rehashed=$false;backup_recoverability='NOT_ESTABLISHED; F drive unavailable in this metadata observation'
 external_inputs=@('Authorized role and co-tenant/operator facts','Owner-designated host, separate P309 access/non-root user and safe credential location plus verified host fingerprint','Operator Part A and agreed five-second read-only audit time')
 next_step='Receive required external facts; audited native host then exact consolidated host-change/recovery package; no premature OD-R2-0(D) or installation approval request'
}
$status | ConvertTo-Json -Depth 18 | Set-Content -LiteralPath (Join-Path $RecordDir 'STATUS.json')
Copy-Item -LiteralPath work\P309-host-completion-review.md -Destination (Join-Path $RecordDir 'REVIEW.md')
$scripts=@('collect-feasibility-windows.ps1','collect-feasibility-ubuntu.py','feasibility-followup.ps1','completion-readonly.ps1','completion-ubuntu-readonly.py','inventory-current-runtime.py','verify-completion-source.ps1','export-reviewed-entry.ps1','finalize-host-completion.ps1')
$scriptDir=Join-Path $RecordDir 'collection-sources'
New-Item -ItemType Directory -Path $scriptDir | Out-Null
foreach($name in $scripts){Copy-Item -LiteralPath (Join-Path 'work' $name) -Destination (Join-Path $scriptDir $name)}
[ordered]@{utc=[DateTime]::UtcNow.ToString('o');checked_files=$before.Count;result='ALL_UNCHANGED';existing_local_branches='UNCHANGED_BEFORE_NEW_ADDITIVE_COMMIT';tracked_source_before_additive_record='UNCHANGED';backup_data_touched=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $RecordDir 'PRESERVATION.json')
$files=@(Get-ChildItem -LiteralPath $RecordDir -Recurse -File | ForEach-Object {@{path=[IO.Path]::GetRelativePath($RecordDir,$_.FullName).Replace('\','/');sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant();bytes=$_.Length}} | Sort-Object path)
[ordered]@{schema='P309_ADDITIVE_EVIDENCE_MANIFEST/1';source_commit=$status.source_commit;record_directory=$RecordDir;files=$files;self_hash='Excluded; pinned by enclosing Git commit and delivery archive hash'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $RecordDir 'EVIDENCE_MANIFEST.json')
foreach($name in @('STATUS.json','REVIEW.md','PRESERVATION.json','EVIDENCE_MANIFEST.json','source-verification.json','microsoft-wsl-security-provenance.json')){Copy-Item -LiteralPath (Join-Path $RecordDir $name) -Destination (Join-Path $dst $name)}
Copy-Item -LiteralPath (Join-Path $RecordDir 'reviewed-native-entry/EXPORT_BINDINGS.json') -Destination (Join-Path $dst 'NATIVE_ENTRY_BINDINGS.json')
New-Item -ItemType Directory -Path (Join-Path $dst 'collection-sources') | Out-Null
foreach($name in $scripts){Copy-Item -LiteralPath (Join-Path $scriptDir $name) -Destination (Join-Path $dst 'collection-sources' $name)}
Copy-Item -LiteralPath (Join-Path $RecordDir 'REVIEW.md') -Destination outputs\P309-host-completion-review.md
Copy-Item -LiteralPath (Join-Path $RecordDir 'STATUS.json') -Destination outputs\P309-host-completion-status.json
Compress-Archive -LiteralPath $RecordDir -DestinationPath outputs\P309-host-completion-evidence.zip -CompressionLevel Optimal -ErrorAction Stop
Get-FileHash -LiteralPath outputs\P309-host-completion-evidence.zip | Select-Object Algorithm,Hash,Path
Write-Output "Preserved $($before.Count) prior evidence files. Additive package staged in $dst; no Git commit performed by this script."
