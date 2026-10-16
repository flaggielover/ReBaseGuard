param([Parameter(Mandatory=$true,ParameterSetName='Execute')][ValidatePattern('^[0-9a-f]{64}$')][string]$ApprovalDigest,
      [Parameter(Mandatory=$true,ParameterSetName='ReadOnly')][switch]$ReadOnlyPreflight)
# NORMAL-USER entry. Never elevate this mutable file. The trusted tool caller
# hashes these bytes against the reviewed constant and executes the same memory
# ScriptBlock. This script then pins NativeEntry bytes BEFORE ShellExecute/UAC.
$ErrorActionPreference='Stop'
$candidate='C:\Users\Lenovo\P309-I2-build-20261016-v4\NativeEntry.exe'
$expected='23cfc53c4b501f91f647b4c73b75ff99e53c305c1cb37bd2fc7ec32a2187881e'
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'start this launcher as the ordinary owner, not already elevated'}
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
public sealed class P309PinnedEntry : IDisposable {
    [StructLayout(LayoutKind.Sequential)] struct FT {public uint low,high;}
    [StructLayout(LayoutKind.Sequential)] struct INFO {
        public uint attributes;public FT creation,access,write;public uint volume,sizeHigh,sizeLow,links,indexHigh,indexLow;
    }
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,ExactSpelling=true,SetLastError=true)]
    static extern SafeFileHandle CreateFileW(string path,uint access,uint share,IntPtr sa,uint mode,uint flags,IntPtr template);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool GetFileInformationByHandle(SafeFileHandle handle,out INFO info);
    readonly List<SafeFileHandle> parents=new List<SafeFileHandle>();public FileStream File;
    public P309PinnedEntry(string path) {
        try {
            if(Marshal.SizeOf(typeof(INFO))!=52)throw new IOException("file identity ABI differs");
            var paths=new List<string>();var parent=new DirectoryInfo(Path.GetDirectoryName(path));
            while(parent!=null){paths.Insert(0,parent.FullName);parent=parent.Parent;}
            foreach(string p in paths) {
                // Share READ only: neither metadata/reparse writes nor rename
                // can replace a held ancestor before the elevated load.
                var h=CreateFileW(p,0,1,IntPtr.Zero,3,0x02000000|0x00200000,IntPtr.Zero);
                if(h.IsInvalid){h.Dispose();throw new Win32Exception();}
                parents.Add(h);INFO info;
                if(!GetFileInformationByHandle(h,out info)||(info.attributes&0x400)!=0)throw new IOException("reparse/unknown ancestor");
            }
            var leaf=CreateFileW(path,0x80000000,1,IntPtr.Zero,3,0x00200000,IntPtr.Zero);
            if(leaf.IsInvalid){leaf.Dispose();throw new Win32Exception();}
            File=new FileStream(leaf,FileAccess.Read);
            INFO fileInfo;
            if(!GetFileInformationByHandle(File.SafeFileHandle,out fileInfo)||(fileInfo.attributes&0x400)!=0||fileInfo.links!=1)
                throw new IOException("entry topology differs");
        }catch{Dispose();throw;}
    }
    public void Dispose(){if(File!=null){File.Dispose();File=null;}for(int i=parents.Count-1;i>=0;i--)parents[i].Dispose();parents.Clear();}
}
'@
$pin=[P309PinnedEntry]::new($candidate)
try {
    $sha=[Security.Cryptography.SHA256]::Create()
    try {$actual=[BitConverter]::ToString($sha.ComputeHash($pin.File)).Replace('-','').ToLowerInvariant()} finally {$sha.Dispose()}
    if($actual -cne $expected) {throw 'native entry fixed-byte mismatch'}
    if($ReadOnlyPreflight) {
        [ordered]@{scope='READ_ONLY_ENTRY_AND_ANCESTOR_PIN_CHECK';sha256=$actual;uac_requests=0;native_entry_executions=0;admission='BLOCKED'} | ConvertTo-Json
        return
    }
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=$candidate;$psi.Arguments=$ApprovalDigest;$psi.WorkingDirectory='C:\Windows\System32'
    $psi.UseShellExecute=$true;$psi.Verb='runas';$psi.WindowStyle=[Diagnostics.ProcessWindowStyle]::Hidden
    $process=[Diagnostics.Process]::Start($psi)
    $held=$process.Handle
    # No environment claim is made about ShellExecute: the native entry has no
    # CLR imports and constructs an explicit clean environment for CreateProcess.
    if(-not $process.WaitForExit(260000)) {throw 'native entry timeout; not killed, no retry'}
    [ordered]@{pid=$process.Id;exit_code=$process.ExitCode;entry_sha256=$actual;admission='BLOCKED'} | ConvertTo-Json
    if($process.ExitCode -ne 0) {throw 'native entry/capture failed; preserve records, no retry'}
} finally {$pin.Dispose()}
