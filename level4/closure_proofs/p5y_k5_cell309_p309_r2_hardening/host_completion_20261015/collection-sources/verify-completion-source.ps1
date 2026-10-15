param([Parameter(Mandatory=$true)][string]$RecordDir)
$ErrorActionPreference='Stop'
$repo='D:\ReBaseGuard-309\workspace\p309-host-completion-20261015'
$commit='47118d4837ab2dd5a4ff03e66263c82754769c36'
$prefix='level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/wsl_host_controls/d2_contract_dev/'
function Blob([string]$Spec) {
 $si=[Diagnostics.ProcessStartInfo]::new('git');$si.UseShellExecute=$false;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true;$si.CreateNoWindow=$true
 foreach($a in @('-C',$repo,'cat-file','blob',$Spec)) {$si.ArgumentList.Add($a)}
 $p=[Diagnostics.Process]::Start($si);$ms=[IO.MemoryStream]::new();$p.StandardOutput.BaseStream.CopyTo($ms);$err=$p.StandardError.ReadToEnd();$p.WaitForExit()
 if($p.ExitCode -ne 0){throw "Cannot read $Spec : $err"};$b=$ms.ToArray();$p.Dispose();$ms.Dispose();return ,$b
}
function Hash([byte[]]$b){[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()}
function Json([string]$s){[Text.Encoding]::UTF8.GetString((Blob $s)) | ConvertFrom-Json -AsHashtable -DateKind String}
if((git -C $repo rev-parse HEAD) -ne $commit){throw 'HEAD mismatch'}
$m=Json ($commit+':'+$prefix+'D2_REREVIEW_SOURCE_SHA256.json')
$checks=[ordered]@{}
foreach($path in $m.reviewed_current_sha256.Keys){
 $b=Blob ($commit+':'+$path);$h=Hash $b
 if($h -ne $m.reviewed_current_sha256[$path]){throw "Current mismatch $path"}
 $raw=[IO.File]::ReadAllBytes((Join-Path $repo $path))
 $norm=[Text.Encoding]::UTF8.GetBytes([Text.Encoding]::UTF8.GetString($raw).Replace("`r`n","`n"))
 if((Hash $norm) -ne $h){throw "Worktree mismatch $path"}
 $checks[$path]=@{canonical_sha256=$h;worktree_sha256=(Hash $raw);crlf_normalized_match=$true}
}
foreach($path in $m.new_record_sha256.Keys){if((Hash (Blob ($commit+':'+$prefix+$path))) -ne $m.new_record_sha256[$path]){throw "New record mismatch $path"}}
foreach($path in $m.protected20_sha256.Keys){if((Hash (Blob ($commit+':'+$path))) -ne $m.protected20_sha256[$path]){throw "Protected mismatch $path"}}
$historical=Blob $m.historical_manifest_reference.git_spec
if((Hash $historical) -ne $m.historical_manifest_reference.canonical_sha256){throw 'Historical manifest mismatch'}
$hm=[Text.Encoding]::UTF8.GetString($historical) | ConvertFrom-Json -AsHashtable
foreach($s in $hm.historical_reference_sha256.Keys){if((Hash (Blob $s)) -ne $hm.historical_reference_sha256[$s]){throw "History mismatch $s"}}
$remote=git -C $repo ls-remote --heads origin codex/p309-d2-rereview-record-20261015
if($LASTEXITCODE -ne 0 -or $remote -notmatch ('^'+$commit+'\s')){throw 'Remote exact binding changed'}
$refs=@(git -C $repo for-each-ref '--format=%(refname) %(objectname)' refs/heads)
[ordered]@{utc=[DateTime]::UtcNow.ToString('o');source_commit=$commit;remote=$remote;result='MATCH';current_count=$checks.Count;new_records=$m.new_record_sha256.Count;protected_count=$m.protected20_sha256.Count;historical_count=$hm.historical_reference_sha256.Count;current=$checks;existing_local_branches=$refs;formal_admission='BLOCKED'} | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $RecordDir 'source-verification.json')
Write-Output "MATCH: $($checks.Count) current, $($m.new_record_sha256.Count) rereview records, $($m.protected20_sha256.Count) protected, $($hm.historical_reference_sha256.Count) historical"
