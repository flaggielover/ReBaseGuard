param([string]$Distribution = 'Ubuntu-24.04')
# Read-only Windows facts. Does not start WSL or change Windows settings.
$ErrorActionPreference = 'Stop'
$os = Get-CimInstance Win32_OperatingSystem
$processors = @(Get-CimInstance Win32_Processor)
$distributions = @(Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' |
    ForEach-Object { Get-ItemProperty $_.PSPath } |
    Where-Object { $_.DistributionName -eq $Distribution })
if ($distributions.Count -ne 1) { throw 'Distribution registration is missing or ambiguous' }
$registration = $distributions[0]
$basePath = $registration.BasePath -replace '^\\\\\?\\', ''
if ($basePath -notmatch '^([A-Za-z]:)\\') { throw 'Cannot identify the VHDX backing drive' }
$drive = $Matches[1]
$volume = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$drive'"
if ($null -eq $volume -or $null -eq $volume.FreeSpace) { throw 'Backing drive free space is unavailable' }
$vhdName = if ($registration.VhdFileName) { $registration.VhdFileName } else { 'ext4.vhdx' }
$vhdPath = Join-Path $basePath $vhdName
if (-not (Test-Path -LiteralPath $vhdPath -PathType Leaf)) { throw 'Registered VHDX was not found' }
$systemVolume = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($os.SystemDrive)'"
[ordered]@{
    schema = 'P309_WINDOWS_READONLY_FACTS/1'
    utc = [DateTime]::UtcNow.ToString('o')
    windows = @{ caption = $os.Caption; version = $os.Version; build = $os.BuildNumber }
    logical_cpus = ($processors | Measure-Object NumberOfLogicalProcessors -Sum).Sum
    total_memory_bytes = [int64]$os.TotalVisibleMemorySize * 1024
    available_memory_bytes = [int64]$os.FreePhysicalMemory * 1024
    distribution = $Distribution
    wsl_version = $registration.Version
    vhdx_registered_and_present = $true
    backing_drive = $drive
    backing_filesystem = $volume.FileSystem
    backing_free_bytes = [int64]$volume.FreeSpace
    system_drive_free_bytes = [int64]$systemVolume.FreeSpace
    host_power_and_update_policy = 'NOT_ASSESSED'
    host_workload_exclusivity = 'NOT_ASSESSED'
} | ConvertTo-Json -Depth 5
