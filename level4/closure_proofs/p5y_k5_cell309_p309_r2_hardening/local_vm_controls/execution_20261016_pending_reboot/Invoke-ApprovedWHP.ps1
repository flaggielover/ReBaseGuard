$ErrorActionPreference='Stop'
$run=Split-Path -Parent $MyInvocation.MyCommand.Path
$transcript=$false
$ok=$false
try {
 Start-Transcript -Path (Join-Path $run 'whp-elevated-transcript.txt') -NoClobber | Out-Null
 $transcript=$true
 $script=Join-Path $run 'approved-source\Enable-ApprovedWHP.ps1'
 $expected='ab1a4698fc7865a105da7877df4f70b0fd5f4565b1c59dfe4d9827bfb54eb857'
 if((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected){throw 'Approved source binding changed'}
 & $script -ApprovalRecord (Join-Path $run 'APPROVAL.json') -EvidenceDirectory (Join-Path $run 'feature')
 $ok=$true
} catch {
 $_ | Out-String | Set-Content -LiteralPath (Join-Path $run 'whp-elevated-error.txt') -Encoding UTF8
} finally {
 [ordered]@{success=$ok;completed_utc=[DateTime]::UtcNow.ToString('o');automatic_restart=$false;
   formal_admission='BLOCKED'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $run 'whp-elevated-completion.json') -Encoding UTF8
 if($transcript){Stop-Transcript | Out-Null}
}
if($ok){exit 0}else{exit 1}
