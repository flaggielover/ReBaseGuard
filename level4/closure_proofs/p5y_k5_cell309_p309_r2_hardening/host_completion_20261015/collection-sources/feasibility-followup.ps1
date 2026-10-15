param([string]$OutFile)
$ErrorActionPreference='Stop'
$r=[ordered]@{utc=[DateTime]::UtcNow.ToString('o');query='Read matching Ubuntu-24.04 HKCU Lxss registration ACL GetOwner(SecurityIdentifier); compare owner SID with current WindowsIdentity.User SID in memory; export hash and well-known role only';reason='Initial textual ACL owner/account-name comparison cannot reliably establish SID equality';scope='READ_ONLY_FEASIBILITY'}
try {
  $id=[Security.Principal.WindowsIdentity]::GetCurrent()
  $r.registrations=@(Get-ChildItem -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' | ForEach-Object {
    $v=Get-ItemProperty -LiteralPath $_.PSPath
    if($v.DistributionName -eq 'Ubuntu-24.04') {
      $owner=(Get-Acl -LiteralPath $_.PSPath).GetOwner([Security.Principal.SecurityIdentifier])
      [ordered]@{distribution=$v.DistributionName;registry_owner_sid_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($owner.Value))).ToLowerInvariant();registry_owner_sid_equals_current_user=($owner.Value -eq $id.User.Value);owner_is_builtin_administrators=$owner.IsWellKnown([Security.Principal.WellKnownSidType]::BuiltinAdministratorsSid);owner_is_local_system=$owner.IsWellKnown([Security.Principal.WellKnownSidType]::LocalSystemSid);registration_scope='CURRENT_USER_HKCU';raw_sid_exported=$false}
    }
  })
  $r.query_exit=0
} catch { $r.query_exit=1; $r.error_type=$_.Exception.GetType().FullName; $r.error_hresult=$_.Exception.HResult }
$r.limitation='Registry ACL ownership is distinct from WSL user registration scope. No DACL/isolation review or root capability test.'
$r | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutFile -Encoding utf8
