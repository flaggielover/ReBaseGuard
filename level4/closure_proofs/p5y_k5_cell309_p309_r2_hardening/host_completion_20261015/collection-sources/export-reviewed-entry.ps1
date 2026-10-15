param([Parameter(Mandatory=$true)][string]$RecordDir)
$ErrorActionPreference='Stop'
$repo='D:\ReBaseGuard-309\workspace\p309-host-completion-20261015'
$start='47118d4837ab2dd5a4ff03e66263c82754769c36'
$native='501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853'
$packet='level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/host_side_packet_501f48cb/'
$ns='level4/closure_proofs/p5y_k5_cell309_p309_r2/'
function Blob([string]$spec){
 $si=[Diagnostics.ProcessStartInfo]::new('git');$si.UseShellExecute=$false;$si.RedirectStandardOutput=$true;$si.RedirectStandardError=$true;$si.CreateNoWindow=$true
 foreach($a in @('-C',$repo,'cat-file','blob',$spec)){$si.ArgumentList.Add($a)}
 $p=[Diagnostics.Process]::Start($si);$s=[IO.MemoryStream]::new();$p.StandardOutput.BaseStream.CopyTo($s);$err=$p.StandardError.ReadToEnd();$p.WaitForExit()
 if($p.ExitCode -ne 0){throw "Cannot read $spec : $err"};$b=$s.ToArray();$p.Dispose();$s.Dispose();return ,$b
}
function Hash([byte[]]$b){[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()}
$out=Join-Path $RecordDir 'reviewed-native-entry'
New-Item -ItemType Directory -Path $out -ErrorAction Stop | Out-Null
$manifest=[Text.Encoding]::UTF8.GetString((Blob ($start+':'+$packet+'PACKET_MANIFEST.json'))) | ConvertFrom-Json -AsHashtable
$bindings=[Collections.Generic.List[object]]::new()
function ExportBlob([string]$commit,[string]$source,[string]$relative,[string]$expected=''){
 $b=Blob ($commit+':'+$source);$h=Hash $b
 if($expected -and $h -ne $expected){throw "Mismatch $source"}
 $path=Join-Path $out $relative
 New-Item -ItemType Directory -Path (Split-Path $path -Parent) -Force | Out-Null
 [IO.File]::WriteAllBytes($path,$b)
 $bindings.Add(@{source_commit=$commit;source_path=$source;exported_path=$relative;sha256=$h})
}
foreach($name in $manifest.files.Keys){ExportBlob $start ($packet+$name) ('packet/'+$name) $manifest.files[$name]}
ExportBlob $start ($packet+'PACKET_MANIFEST.json') 'packet/PACKET_MANIFEST.json'
ExportBlob $native ($ns+'code/p309_host.py') 'native-audit/p309_host.py' 'ec9c8416159cf9e2e7372f97ce179a290def987007dc144591833615ca251f65'
foreach($name in @('OWNER_INSTRUCTIONS_R2_VERBATIM.md','OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md','OWNER_DECISIONS_R2_MSG5_VERBATIM.md','OWNER_DECISIONS_R2_MSG6_VERBATIM.md','R2_HOST_REQUIREMENTS.md','R2_AWS_SESSION_INSTRUCTIONS.md','R2_BOOTSTRAP.md','OWNER_DECISION_PACKET_R2.md')){ExportBlob $native ($ns+'governance/'+$name) ('governance/'+$name)}
$remote=@(git -C $repo ls-remote origin refs/heads/claude/p5y-k5-cell309-p309-r2 'refs/p5y-k5-cell309/*')
if($LASTEXITCODE -ne 0 -or $remote.Count -ne 1 -or $remote[0] -notmatch ('^'+$native+'\s')){throw 'Official branch or protected remote namespace changed; review required'}
[ordered]@{schema='P309_REVIEWED_NATIVE_ENTRY_EXPORT/1';utc=[DateTime]::UtcNow.ToString('o');preparation_commit=$start;official_runtime_commit=$native;remote_ref_snapshot=$remote;entries=$bindings;scope='Source/document export only; NO remote connection, audit execution, installation, drill or grant';host_change_package_ready=$false;reason='Actual native host access/facts and operator forms not supplied; do not infer exact changes';formal_admission='BLOCKED'} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $out 'EXPORT_BINDINGS.json')
Write-Output "Exported $($bindings.Count) verified documents/audit source. No code executed."
