param([Parameter(Mandatory=$true)][string]$ApprovalRecord,
      [Parameter(Mandatory=$true)][string]$PreparedRecords)
# Portable materialization only. Never runs pacman, an installer hook or QEMU.
$ErrorActionPreference='Stop'
$a=Get-Content -LiteralPath $ApprovalRecord -Raw | ConvertFrom-Json
if($a.scope -ne 'P309_LOCAL_VM_FEASIBILITY_V1' -or $a.materialize_runtime -ne $true -or
   -not $a.human_message_reference){throw 'Human installation approval reference is required'}
$r=[IO.Path]::GetFullPath($PreparedRecords)
if($r -ne 'D:\ReBaseGuard-309\records\p309-local-vm-preparation-20261016-162345'){throw 'Unexpected prepared evidence path'}
$bundle=Join-Path $r 'runtime-bundle.json'
if((Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash.ToLowerInvariant() -ne $a.runtime_bundle_sha256){throw 'Approved bundle binding differs'}
$target='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1'
if(Test-Path -LiteralPath $target){throw 'Installation collision; retain it and investigate'}
$plan=Get-Content -LiteralPath $bundle -Raw | ConvertFrom-Json
$drive=Get-PSDrive -Name D
if($drive.Free -lt (40000000000L + [long]$plan.bytes + 1073741824L)){throw 'Insufficient D: backing space including retained 40 GB floor'}
& 'C:\Python314\python.exe' -B (Join-Path $PSScriptRoot 'runtime_bundle.py') (Join-Path $r 'downloads') `
  (Join-Path $r 'archive-signatures.json') $bundle --materialize-after-human-approval $target
if($LASTEXITCODE -ne 0){throw 'Materialization failed; retain partial tree, do not auto-resume/delete'}
$hashes='D:\ReBaseGuard-309\local-vm-feasibility\candidate-v1.sha256'
if(Test-Path -LiteralPath $hashes){throw 'Hash-list collision'}
$lines=foreach($file in $plan.files){$file.sha256+'  '+$file.path}
[IO.File]::WriteAllText($hashes,([string]::Join("`n",[string[]]$lines)+"`n"),[Text.UTF8Encoding]::new($false))
if((Get-FileHash -LiteralPath $hashes).Hash.ToLowerInvariant() -ne $a.runtime_hashlist_sha256){throw 'Hash list differs from approval'}
@{installed_path=$target;file_count=$plan.files.Count;runtime_bundle_sha256=$a.runtime_bundle_sha256;
  admission='BLOCKED';qemu_started=$false;services_created=$false;policies_changed=$false} |
 ConvertTo-Json | Set-Content 'D:\ReBaseGuard-309\local-vm-feasibility\materialization.json'
