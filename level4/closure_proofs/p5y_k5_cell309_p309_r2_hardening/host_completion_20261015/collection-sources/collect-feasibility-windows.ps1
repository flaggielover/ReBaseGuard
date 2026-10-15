param([Parameter(Mandatory=$true)][string]$OutFile)
$ErrorActionPreference='Stop'
$records=[System.Collections.Generic.List[object]]::new()
function HashText([string]$Text) { [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($Text))).ToLowerInvariant() }
function Query([string]$Id,[scriptblock]$Body,[string]$Limit) {
  $r=[ordered]@{id=$Id;utc=[DateTime]::UtcNow.ToString('o');query=$Body.ToString().Trim();scope='READ_ONLY_FEASIBILITY';limitation=$Limit}
  try { $r.result=& $Body; $r.status='OBSERVED'; $r.query_exit=0 }
  catch { $r.status='UNKNOWN_OR_DENIED'; $r.query_exit=1; $r.error_type=$_.Exception.GetType().FullName; $r.error_hresult=$_.Exception.HResult; $r.error_id=$_.FullyQualifiedErrorId }
  $records.Add($r)
}
Query 'windows_token' {
  $id=[Security.Principal.WindowsIdentity]::GetCurrent()
  $principal=[Security.Principal.WindowsPrincipal]::new($id)
  $privs=& "$env:SystemRoot\System32\whoami.exe" /priv /fo csv /nh
  $rc=$LASTEXITCODE
  [ordered]@{sid_sha256=HashText $id.User.Value;effective_token_is_administrator=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator);impersonation_level=$id.ImpersonationLevel.ToString();privileges_query='whoami.exe /priv /fo csv /nh';privileges_exit=$rc;privileges_csv=@($privs);powershell_version=$PSVersionTable.PSVersion.ToString();dotnet_version=[Environment]::Version.ToString()}
} 'Token capability is not authority to change host settings; no elevation or impersonation.'
Query 'wsl_registration_owner_relation' {
  $key='HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss'
  $found=@(Get-ChildItem -LiteralPath $key | ForEach-Object {
    $v=Get-ItemProperty -LiteralPath $_.PSPath
    if ($v.DistributionName -eq 'Ubuntu-24.04') {
      $acl=Get-Acl -LiteralPath $_.PSPath
      [ordered]@{distribution=$v.DistributionName;version=$v.Version;default_uid=$v.DefaultUid;registration_in_current_user_hive=$true;registry_key_owner_sha256=HashText $acl.Owner;registry_owner_matches_current_identity=($acl.Owner -eq [Security.Principal.WindowsIdentity]::GetCurrent().Name);registration_identifier_and_basepath_exported=$false}
    }
  })
  [ordered]@{registrations=$found;windows_owner_boundary='Current-user WSL registration; no separate Windows token inferred from Linux UID';wsl_root_capability='UNTESTED'}
} 'HKCU registration/owner metadata does not prove protected observer/client isolation. No raw registry identifiers exported.'
Query 'windows_integration_config' {
  $path=Join-Path $env:USERPROFILE '.wslconfig'
  if (!(Test-Path -LiteralPath $path)) { return @{status='NOT_FOUND';path_label='CURRENT_WINDOWS_PROFILE/.wslconfig'} }
  $allowed='(?i)^\s*(processors|memory|swap|localhostForwarding|networkingMode|firewall|dnsTunneling|autoProxy|nestedVirtualization|guiApplications|vmIdleTimeout|autoMemoryReclaim|sparseVhd)\s*='
  $lines=@(Get-Content -LiteralPath $path | Where-Object {$_ -match $allowed})
  [ordered]@{path_label='CURRENT_WINDOWS_PROFILE/.wslconfig';sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant();selected_non_identity_settings=$lines;other_values_exported=$false}
} 'Configured keys only, not proof of effective enforcement. Paths and identity fields omitted.'
foreach ($provider in @('Microsoft-Windows-Kernel-Process','Microsoft-Windows-Kernel-Power','Microsoft-Windows-Hyper-V-Compute','Microsoft-Windows-Lxss','Microsoft-Windows-WMI-Activity')) {
  # Literal exact names are captured in the query; metadata only, no event records.
  $body=[scriptblock]::Create("Get-WinEvent -ListProvider '$provider' -ErrorAction Stop | Select-Object Name, Id, @{Name='Discovery';Expression={'DISCOVERED_ONLY'}}")
  Query ('provider_'+$provider) $body 'Provider metadata presence is DISCOVERED_ONLY; no trace, event reads, auditing or complete-coverage claim.'
}
Query 'collector_api_binaries' {
  @('advapi32.dll','tdh.dll','kernel32.dll','pdh.dll','wevtapi.dll') | ForEach-Object {
    $f=Get-Item -LiteralPath (Join-Path "$env:SystemRoot\System32" $_)
    [ordered]@{name=$f.Name;file_version=$f.VersionInfo.FileVersion;status='DISCOVERED_ONLY'}
  }
} 'Installed DLL versions only; API access/loss/protected-process coverage untested; no protected handles opened.'
Query 'p309_windows_services' {
  $s=@(Get-Service | Where-Object {$_.Name -match '(?i)(p309|rebaseguard)'} | Select-Object Name,Status,StartType)
  [ordered]@{matching_services=$s;match_rule='case-insensitive p309 or rebaseguard';exact_proposed_service_name='NOT_SPECIFIED_IN_PACKET'}
} 'Service metadata only. Empty name match cannot exclude differently named services; future exact service name/identity requires design.'
Query 'p309_named_pipe_names' {
  $matches=[System.Collections.Generic.List[string]]::new(); $count=0; $truncated=$false
  foreach ($p in [IO.Directory]::EnumerateFiles('\\.\pipe\')) {
    $count++; if ($count -gt 10000) {$truncated=$true;break}
    $name=[IO.Path]::GetFileName($p)
    if ($name -match '(?i)(p309|rebaseguard)') {$matches.Add($name)}
  }
  [ordered]@{matching_names=$matches.ToArray();match_rule='case-insensitive p309 or rebaseguard';bounded_enumeration_truncated=$truncated;exact_proposed_endpoint_name='NOT_SPECIFIED_IN_PACKET';connected_to_endpoints=$false}
} 'Names only, no pipe opened/connected; race-prone snapshot, not endpoint isolation or availability guarantee.'
Query 'backup_drive_presence' {
  [ordered]@{F_drive_present=[IO.Directory]::Exists('F:\');method='Directory.Exists(F:\) only';backup_rehashed=$false;backup_modified=$false;historical_vhdx_sha256='C800DB074A15C50940F5D552B185D98555911294A886557D2484F48A5AD03C54';digest_status='HISTORICAL_ONLY'}
} 'Presence alone cannot establish backup availability/integrity/recoverability; no file reads or rehash.'
$records | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath $OutFile -Encoding utf8
Write-Output ('Windows metadata queries recorded: '+$records.Count)
