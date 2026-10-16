$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$source=Join-Path $root 'Launch-Approved.final-candidate.ps1'
$bytes=[IO.File]::ReadAllBytes($source)
$h=[Security.Cryptography.SHA256]::Create();try{$digest=[BitConverter]::ToString($h.ComputeHash($bytes)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}
if($digest -cne '9b89849c5e5636b219b29ad633f4dda43a6268bdd3a8858b4b0fc73ae9119d09'){throw 'fixed final launcher differs'}
$text=[Text.Encoding]::UTF8.GetString($bytes)
$old='C:\Users\Lenovo\P309-InstallationFacts-build-20261016-v3\NativeEntry.exe'
$new=Join-Path $root 'production-build-stage\NativeEntry.exe'
if(($text.Split(@($old),[StringSplitOptions]::None)).Count-ne 2){throw 'unique staging path override required'}
$block=[ScriptBlock]::Create($text.Replace($old,$new))
$env:TEMP=$PSScriptRoot;$env:TMP=$PSScriptRoot
& $block -ReadOnlyPreflight
@{scope='STAGING_PATH_OVERRIDE_FILE_PRECHECK_NOT_PRIVATE_TARGET_VALIDATION';reviewed_launcher_sha256=$digest;candidate_path=$new;private_target_preflight_executed=$false;uac=0;entry_executions=0;admission='BLOCKED'}|ConvertTo-Json