$ErrorActionPreference='Stop'
$source='D:\ReBaseGuard-309\records\p309-facts-repair-v1-invocation-20261016-01\protected-evidence'
$public='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v6_facts_repair\execution_20261016_v1\EVIDENCE_MANIFEST.json'
$out='D:\ReBaseGuard-309\records\p309-saved-directory-acl-interpretation-20261016-02'
if(Test-Path -LiteralPath $out){throw 'Fresh output required'}
$manifest=Get-Content -LiteralPath ($source+'\SHA256SUMS.json') -Raw | ConvertFrom-Json
$published=Get-Content -LiteralPath $public -Raw | ConvertFrom-Json
$published=$published.protected_evidence
$rows=@()
foreach($number in 0..3){
  $name='directory-'+$number+'.json'
  $path=Join-Path $source $name
  $row=@($manifest|Where-Object file -eq $name)
  $pub=@($published|Where-Object file -eq $name)
  $hash=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
  if($row.Count-ne 1-or$pub.Count-ne 1-or$hash-ne$row[0].sha256-or$hash-ne$pub[0].sha256){throw ('Source binding mismatch '+$name)}
  $data=(Get-Content -LiteralPath $path -Raw|ConvertFrom-Json).data
  $sd=[System.Security.AccessControl.RawSecurityDescriptor]::new($data.sddl)
  $owner=if($sd.Owner.Value-eq'S-1-5-18'){'SYSTEM'}elseif($sd.Owner.Value-eq'S-1-5-32-544'){'BUILTIN_ADMINISTRATORS'}elseif($sd.Owner.Value-eq'S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464'){'TRUSTED_INSTALLER'}else{'OTHER_OWNER_REDACTED'}
  $aces=@()
  foreach($ace in $sd.DiscretionaryAcl){
    if($ace-isnot[System.Security.AccessControl.CommonAce]){throw 'Unsupported ACE for this offline display'}
    $mask=[BitConverter]::ToUInt32([BitConverter]::GetBytes([int]$ace.AccessMask),0)
    $sid=$ace.SecurityIdentifier.Value
    $role=switch($sid){'S-1-5-18'{'SYSTEM'} 'S-1-5-32-544'{'BUILTIN_ADMINISTRATORS'} 'S-1-5-32-545'{'BUILTIN_USERS'} 'S-1-5-11'{'AUTHENTICATED_USERS'} 'S-1-3-0'{'CREATOR_OWNER'} 'S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464'{'TRUSTED_INSTALLER'} default{'OTHER_SID_REDACTED'}}
    $wide=[uint64]$mask
    $aces+= [ordered]@{role=$role;qualifier=[string]$ace.AceQualifier;flags=[string]$ace.AceFlags;mask_hex=('0x{0:x8}'-f$mask);inherit_only=(([int]$ace.AceFlags -band [int][System.Security.AccessControl.AceFlags]::InheritOnly)-ne 0);object_delete=(($wide -band [uint64]0x10000)-ne 0);delete_child=(($wide -band [uint64]0x40)-ne 0);write_dac=(($wide -band [uint64]0x40000)-ne 0);write_owner=(($wide -band [uint64]0x80000)-ne 0)}
  }
  $rows+=[ordered]@{source=$name;source_sha256=$hash;path=$data.path;owner=$owner;aces=$aces}
}
$result=[ordered]@{scope='OFFLINE_INTERPRETATION_OF_SAVED_APPROVED_FACTS_NO_HOST_API_QUERY';interpreter_version=[string]$PSVersionTable.PSVersion;source_manifest_sha256=(Get-FileHash -LiteralPath ($source+'\SHA256SUMS.json')).Hash.ToLowerInvariant();published_manifest_sha256=(Get-FileHash -LiteralPath $public).Hash.ToLowerInvariant();directories=$rows;actual_effective_access_tested=$false;installed_custody_verified=$false;I1_I7='OPEN';admission='BLOCKED'}
[void](New-Item -ItemType Directory -Path $out)
$json=$result|ConvertTo-Json -Depth 12
[IO.File]::WriteAllText((Join-Path $out 'SAVED_ACL_INTERPRETATION.json'),$json+"`n",[Text.UTF8Encoding]::new($false))
Write-Output ('Saved offline interpretation: '+$out)
