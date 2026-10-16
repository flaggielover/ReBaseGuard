param([Parameter(Mandatory=$true)][string]$ApprovalRecord)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
# Prepared entry point. A human reply is recorded only AFTER concrete consent.
# Does not elevate itself, grant privileges, install a service or start a VM.
$root='C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v1'
$archive='D:\ReBaseGuard-309\records\p309-i2-native-capture-v1'
$candidate='D:\ReBaseGuard-309\records\p309-local-control-package-preparation-20261016-01\EtwCapture-i2-final.exe'
$pins=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'I2_BINARY_BINDING.json') -Raw | ConvertFrom-Json
$approval=Get-Content -LiteralPath $ApprovalRecord -Raw | ConvertFrom-Json
if($approval.scope -cne 'P309_I2_SINGLE_NATIVE_FEASIBILITY_V1' -or
   $approval.capture_count -ne 1 -or
   $approval.binary_sha256 -cne $pins.binary_sha256 -or
   $approval.harness_sha256 -cne (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant() -or
   [string]::IsNullOrWhiteSpace($approval.human_message_reference)) {throw 'approval binding refused'}
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(-not ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'explicit UAC-approved elevated entry required'}
if((Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins.binary_sha256) {throw 'binary changed'}
if((Get-Volume -DriveLetter C).SizeRemaining -lt 1GB -or (Get-Volume -DriveLetter D).SizeRemaining -lt 1GB) {throw 'insufficient evidence space'}
foreach($path in @($root,$archive)) {
    if(Test-Path -LiteralPath $path) {throw "collision; never adopt: $path"}
    $p=Get-Item -LiteralPath (Split-Path -Parent $path)
    while($null -ne $p) {
        if(($p.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {throw 'reparse parent'}
        $p=$p.Parent
    }
}
# Both paths are new. All mutable/admin-executed artifacts have protected ACLs.
# The enrolled owner may READ without elevation to inspect/decode the evidence.
$acl=[Security.AccessControl.DirectorySecurity]::new()
$acl.SetAccessRuleProtection($true,$false)
$admins=[Security.Principal.SecurityIdentifier]::new('S-1-5-32-544')
$system=[Security.Principal.SecurityIdentifier]::new('S-1-5-18')
$acl.SetOwner($admins)
$inherit=[Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit'
foreach($sid in @($admins,$system)) {
    $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl',$inherit,'None','Allow'))
}
$acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($identity.User,'ReadAndExecute',$inherit,'None','Allow'))
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
public static class ReBaseGuardP309AtomicDirectory {
    [StructLayout(LayoutKind.Sequential)] struct SA {public int length;public IntPtr descriptor;public int inherit;}
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,ExactSpelling=true,SetLastError=true)]
    static extern bool CreateDirectoryW(string path,ref SA security);
    public static void Create(string path,byte[] descriptor) {
        var pin=GCHandle.Alloc(descriptor,GCHandleType.Pinned);
        try {
            SA sa=new SA();sa.length=Marshal.SizeOf(typeof(SA));sa.descriptor=pin.AddrOfPinnedObject();
            if(!CreateDirectoryW(path,ref sa)) throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
        } finally {pin.Free();}
    }
}
'@
foreach($path in @($root,$archive)) {
    [ReBaseGuardP309AtomicDirectory]::Create($path,$acl.GetSecurityDescriptorBinaryForm())
    $check=Get-Acl -LiteralPath $path
    if(-not $check.AreAccessRulesProtected -or $check.Owner -ne $admins.Translate([Security.Principal.NTAccount]).Value) {throw 'new directory ACL failed'}
}
Copy-Item -LiteralPath $ApprovalRecord -Destination (Join-Path $root 'approval-used.json')
Copy-Item -LiteralPath $candidate -Destination (Join-Path $root 'EtwCapture.exe')
if((Get-FileHash -LiteralPath (Join-Path $root 'EtwCapture.exe') -Algorithm SHA256).Hash.ToLowerInvariant() -cne $pins.binary_sha256) {throw 'protected copy changed'}
[ordered]@{utc=[DateTime]::UtcNow.ToString('o');root_sddl=(Get-Acl -LiteralPath $root).Sddl;archive_sddl=(Get-Acl -LiteralPath $archive).Sddl;scope=$approval.scope;admission='BLOCKED'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'preflight.json') -Encoding UTF8

function Start-Owned([string]$mode,[string]$label) {
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=Join-Path $root 'EtwCapture.exe'
    $psi.Arguments=$mode
    $psi.UseShellExecute=$false;$psi.CreateNoWindow=$true;$psi.WorkingDirectory=$root
    $psi.RedirectStandardOutput=$true;$psi.RedirectStandardError=$true
    $process=[Diagnostics.Process]::Start($psi)
    # Retain the exact native process handle, not a later PID lookup.
    $held=$process.Handle
    [pscustomobject]@{P=$process;Handle=$held;Label=$label;Out=$process.StandardOutput.ReadToEndAsync();Err=$process.StandardError.ReadToEndAsync()}
}
function Save-Owned($owned) {
    if(-not $owned.P.HasExited) {return}
    [IO.File]::WriteAllText((Join-Path $root ($owned.Label+'.stdout.txt')),$owned.Out.Result)
    [IO.File]::WriteAllText((Join-Path $root ($owned.Label+'.stderr.txt')),$owned.Err.Result)
}
$guard=$null;$capture=$null;$cleanup=$null;$query=$null;$prequery=$null;$failure=$null;$captureStarted=$false
try {
    $prequery=Start-Owned '--query-own' 'preexisting-session-check'
    if(-not $prequery.P.WaitForExit(5000)) {throw 'preexisting session query UNKNOWN; no capture'}
    Save-Owned $prequery
    if($prequery.P.ExitCode -ne 0) {throw 'preexisting/unknown session; no capture or adoption'}
    $guard=Start-Owned '--watchdog-approved' 'watchdog'
    $ready=[Diagnostics.Stopwatch]::StartNew()
    while(-not (Test-Path -LiteralPath (Join-Path $root 'watchdog.ready'))) {
        if($guard.P.HasExited -or $ready.ElapsedMilliseconds -gt 4000) {throw 'watchdog readiness failed; capture not dispatched'}
        Start-Sleep -Milliseconds 50
    }
    $capture=Start-Owned '--capture-approved' 'capture'
    $captureStarted=$true
    if(-not $capture.P.WaitForExit(70000)) {throw 'controller timeout; independent watchdog retained'}
    Save-Owned $capture
    if($capture.P.ExitCode -ne 0) {throw "controller failed: $($capture.P.ExitCode)"}
} catch { $failure=$_.Exception.Message }
finally {
    # No second capture. Query and emergency stop are cleanup, not test retries.
    if($null -ne $guard) {
        if(-not $guard.P.WaitForExit(85000)) {$failure='watchdog did not exit; cleanup UNKNOWN'}
        Save-Owned $guard
        if($guard.P.HasExited -and $guard.P.ExitCode -ne 0) {$failure='watchdog emergency/error; feasibility not passed'}
    }
    $query=Start-Owned '--query-own' 'query-before-recovery'
    if($query.P.WaitForExit(5000)) {
        Save-Owned $query
        if($query.P.ExitCode -eq 3 -and $captureStarted) {
            $cleanup=Start-Owned '--stop-own-approved' 'emergency-cleanup'
            if(-not $cleanup.P.WaitForExit(10000)) {$failure='native cleanup timeout; UNKNOWN'}
            Save-Owned $cleanup
            $failure='emergency cleanup required; feasibility not passed'
        } elseif($query.P.ExitCode -ne 0) {$failure='session identity/query UNKNOWN'}
    } else {$failure='session query timeout; UNKNOWN'}
    $final=Start-Owned '--query-own' 'final-session-query'
    $absent=$final.P.WaitForExit(5000) -and $final.P.ExitCode -eq 0
    Save-Owned $final
    # An outstanding StartTrace call is never treated as quiescence merely
    # because a momentary query found no session. Retain the helper for diagnosis.
    $helpersExited=$true
    foreach($owned in @($capture,$guard,$query,$cleanup,$final,$prequery)) {
        if($null -ne $owned -and -not $owned.P.HasExited) {$helpersExited=$false}
    }
    if(-not $absent -or -not $helpersExited) {$failure='owned helper/session cleanup UNKNOWN; retain controls'}
    if($null -ne $capture) {Save-Owned $capture}
    [ordered]@{utc=[DateTime]::UtcNow.ToString('o');capture_dispatched=$captureStarted;capture_count=([int]$captureStarted);scope_result=$(if($null -eq $failure){'CAPTURE_COMPLETED_REQUIRES_OFFLINE_ANALYSIS'}else{'FAILED_OR_UNKNOWN'});failure=$failure;session_absence_observed=$absent;owned_helpers_exited=$helpersExited;coverage_complete=$false;admission='BLOCKED';I1_I7='OPEN_RETAINED'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'RESULT.json') -Encoding UTF8
    $manifest=foreach($file in Get-ChildItem -LiteralPath $root -File) {
        [ordered]@{file=$file.Name;size=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $root 'SHA256SUMS.json') -Encoding UTF8
    # Enumerate explicitly; never delete/move.
    foreach($file in Get-ChildItem -LiteralPath $root -File) {Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $archive $file.Name) -ErrorAction Stop}
}
if($null -ne $failure) {throw $failure}
