using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace P309HostAnchorV10
{
    internal interface IIdentityLease : IDisposable { void Revalidate(); bool Production { get; } }
    internal sealed class ServiceIdentityLease : IIdentityLease
    {
        internal const string Name = "ReBaseGuardP309Controller";
        internal const string Sid = "S-1-5-80-1389429364-2543163971-322551805-3183066981-1946276422";
        internal const string Account = "NT SERVICE\\ReBaseGuardP309Controller";
        internal const string Image = "C:\\Program Files\\ReBaseGuardP309\\Controller\\ReBaseGuardP309Controller.exe";
        private IntPtr scm, service, process, token;
        private ulong originalTokenId, originalAuthId; private uint pid; private bool disposed;
        public bool Production { get { return true; } }
        [StructLayout(LayoutKind.Sequential)] private struct Luid { internal uint Low; internal int High; internal ulong Value { get { return ((ulong)(uint)High << 32) | Low; } } }
        [StructLayout(LayoutKind.Sequential)] private struct Statistics
        { internal Luid TokenId, AuthenticationId; internal long Expiration; internal int TokenType, ImpersonationLevel; internal uint DynamicCharged, DynamicAvailable, GroupCount, PrivilegeCount; internal Luid ModifiedId; }
        [StructLayout(LayoutKind.Sequential)] private struct SidAttributes { internal IntPtr Sid; internal uint Attributes; }
        [StructLayout(LayoutKind.Sequential)] private struct GroupsFirst { internal uint Count; internal SidAttributes First; }
        [StructLayout(LayoutKind.Sequential)] private struct Privilege { internal Luid Id; internal uint Attributes; }
        [StructLayout(LayoutKind.Sequential)] private struct PrivilegesFirst { internal uint Count; internal Privilege First; }
        [StructLayout(LayoutKind.Sequential)] private struct ServiceStatus
        { internal uint Type, State, ControlsAccepted, Win32Exit, SpecificExit, Checkpoint, WaitHint, Pid, Flags; }
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)] private struct Config
        { internal uint Type, Start, Error; internal IntPtr Binary, Group; internal uint Tag; internal IntPtr Dependencies, StartName, Display; }
        [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)] private static extern IntPtr OpenSCManagerW(string machine, string database, uint access);
        [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)] private static extern IntPtr OpenServiceW(IntPtr manager, string name, uint access);
        [DllImport("advapi32.dll", SetLastError = true)] private static extern bool CloseServiceHandle(IntPtr h);
        [DllImport("advapi32.dll", SetLastError = true)] private static extern bool QueryServiceConfigW(IntPtr h, IntPtr data, uint size, out uint required);
        [DllImport("advapi32.dll", SetLastError = true)] private static extern bool QueryServiceConfig2W(IntPtr h, uint level, IntPtr data, uint size, out uint required);
        [DllImport("advapi32.dll", SetLastError = true)] private static extern bool QueryServiceStatusEx(IntPtr h, int level, out ServiceStatus data, uint size, out uint required);
        [DllImport("kernel32.dll")] private static extern uint GetCurrentProcessId();
        [DllImport("kernel32.dll", SetLastError = true)] private static extern IntPtr OpenProcess(uint access, bool inherit, uint pid);
        [DllImport("kernel32.dll")] private static extern IntPtr GetCurrentThread();
        [DllImport("kernel32.dll", SetLastError = true)] private static extern bool CloseHandle(IntPtr h);
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)] private static extern uint GetModuleFileNameW(IntPtr module, StringBuilder path, uint capacity);
        [DllImport("advapi32.dll", SetLastError = true)] private static extern bool OpenProcessToken(IntPtr process, uint access, out IntPtr token);
        [DllImport("advapi32.dll", SetLastError = true)] private static extern bool OpenThreadToken(IntPtr thread, uint access, bool self, out IntPtr token);
        [DllImport("advapi32.dll", SetLastError = true)] private static extern bool GetTokenInformation(IntPtr token, int cls, IntPtr data, uint length, out uint required);
        [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)] private static extern bool LookupPrivilegeNameW(string system, ref Luid luid, StringBuilder name, ref uint size);
        private static IntPtr TokenData(IntPtr t, int cls)
        {
            uint n; bool ok = GetTokenInformation(t, cls, IntPtr.Zero, 0, out n); int error = Marshal.GetLastWin32Error();
            if (ok || error != 122 || n == 0 || n > 65536) throw new IOException("Unexpected token probe");
            IntPtr p = Marshal.AllocHGlobal((int)n);
            if (!GetTokenInformation(t, cls, p, n, out n)) { Marshal.FreeHGlobal(p); throw NativeFile.Error("GetTokenInformation"); }
            return p;
        }
        private static Statistics InspectToken(IntPtr t)
        {
            IntPtr p = TokenData(t, 1);
            try { SidAttributes a = (SidAttributes)Marshal.PtrToStructure(p, typeof(SidAttributes)); if (new SecurityIdentifier(a.Sid).Value != Sid) throw new IOException("TokenUser is not the fixed virtual account"); }
            finally { Marshal.FreeHGlobal(p); }
            CheckGroup(t, 2, true); CheckGroup(t, 11, false);
            p = TokenData(t, 3);
            try
            {
                uint count = (uint)Marshal.ReadInt32(p); if (count != 1) throw new IOException("Anchor token requires the exact one-privilege allowlist");
                int offset = (int)Marshal.OffsetOf(typeof(PrivilegesFirst), "First"); int size = Marshal.SizeOf(typeof(Privilege));
                for (int i = 0; i < count; i++)
                {
                    Privilege x = (Privilege)Marshal.PtrToStructure(IntPtr.Add(p, offset + i * size), typeof(Privilege));
                    uint n = 128; StringBuilder name = new StringBuilder(128);
                    if (!LookupPrivilegeNameW(null, ref x.Id, name, ref n)) throw NativeFile.Error("LookupPrivilegeNameW");
                    if (name.ToString() != "SeChangeNotifyPrivilege") throw new IOException("Token privilege outside exact anchor allowlist (even disabled)");
                }
            }
            finally { Marshal.FreeHGlobal(p); }
            p = TokenData(t, 10); try { Statistics s = (Statistics)Marshal.PtrToStructure(p, typeof(Statistics)); if (s.TokenType != 1) throw new IOException("Primary token required"); return s; } finally { Marshal.FreeHGlobal(p); }
        }
        private static void CheckGroup(IntPtr t, int cls, bool enabled)
        {
            IntPtr p = TokenData(t, cls);
            try
            {
                uint count = (uint)Marshal.ReadInt32(p); if (count > 1024) throw new IOException("Group bound");
                int offset = (int)Marshal.OffsetOf(typeof(GroupsFirst), "First"), size = Marshal.SizeOf(typeof(SidAttributes)); bool found = false;
                for (int i = 0; i < count; i++)
                {
                    SidAttributes a = (SidAttributes)Marshal.PtrToStructure(IntPtr.Add(p, offset + i * size), typeof(SidAttributes)); string s = new SecurityIdentifier(a.Sid).Value;
                    if (s == Sid && (!enabled || ((a.Attributes & 4) != 0 && (a.Attributes & 16) == 0))) found = true;
                    if (enabled && s == "S-1-5-32-544" && (a.Attributes & 4) != 0 && (a.Attributes & 16) == 0) throw new IOException("Enabled administrators group refused");
                }
                if (!found) throw new IOException(enabled ? "Missing enabled service SID" : "Missing restricted service SID");
            }
            finally { Marshal.FreeHGlobal(p); }
        }
        private static void NoImpersonation()
        {
            IntPtr t; if (OpenThreadToken(GetCurrentThread(), 8, true, out t)) { CloseHandle(t); throw new IOException("Impersonating thread refused"); }
            if (Marshal.GetLastWin32Error() != 1008) throw NativeFile.Error("OpenThreadToken");
        }
        private void ServiceConfig()
        {
            uint n; bool ok = QueryServiceConfigW(service, IntPtr.Zero, 0, out n); int error = Marshal.GetLastWin32Error();
            if (ok || error != 122 || n == 0 || n > 65536) throw new IOException("Unexpected SCM config probe");
            IntPtr p = Marshal.AllocHGlobal((int)n);
            try
            {
                if (!QueryServiceConfigW(service, p, n, out n)) throw NativeFile.Error("QueryServiceConfigW");
                Config c = (Config)Marshal.PtrToStructure(p, typeof(Config));
                if (c.Type != 0x10 || !String.Equals(Marshal.PtrToStringUni(c.StartName), Account, StringComparison.OrdinalIgnoreCase) || !String.Equals(Marshal.PtrToStringUni(c.Binary), "\"" + Image + "\"", StringComparison.OrdinalIgnoreCase)) throw new IOException("SCM fixed account/OWN_PROCESS/image mismatch");
            }
            finally { Marshal.FreeHGlobal(p); }
            p = Marshal.AllocHGlobal(4);
            try { if (!QueryServiceConfig2W(service, 5, p, 4, out n)) throw NativeFile.Error("QueryServiceConfig2W(SERVICE_CONFIG_SERVICE_SID_INFO)"); if (Marshal.ReadInt32(p) != 3) throw new IOException("SERVICE_SID_TYPE_RESTRICTED required"); }
            finally { Marshal.FreeHGlobal(p); }
            CheckRequiredPrivileges();
            ServiceStatus st;
            if (!QueryServiceStatusEx(service, 0, out st, (uint)Marshal.SizeOf(typeof(ServiceStatus)), out n)) throw NativeFile.Error("QueryServiceStatusEx");
            if (st.Type != 0x10 || st.State != 4 || st.Pid != pid || st.Flags != 0) throw new IOException("SCM running owned-process identity mismatch");
        }
        private void CheckRequiredPrivileges()
        {
            uint needed; bool ok = QueryServiceConfig2W(service, 6, IntPtr.Zero, 0, out needed); int error = Marshal.GetLastWin32Error();
            if (ok || error != 122 || needed < IntPtr.Size + 4 || needed > 65536) throw new IOException("RequiredPrivileges config probe");
            IntPtr p = Marshal.AllocHGlobal((int)needed);
            try
            {
                uint capacity = needed; if (!QueryServiceConfig2W(service, 6, p, capacity, out needed) || needed > capacity) throw NativeFile.Error("QueryServiceConfig2W(REQUIRED_PRIVILEGES)");
                IntPtr text = Marshal.ReadIntPtr(p); long offset = text.ToInt64() - p.ToInt64(); if (offset < IntPtr.Size || offset > capacity - 4 || offset % 2 != 0) throw new IOException("RequiredPrivileges pointer outside buffer");
                int limit = ((int)capacity - (int)offset) / 2; StringBuilder value = new StringBuilder(); bool terminated = false;
                for (int i = 0; i < limit; i++) { char c = (char)Marshal.ReadInt16(text, i * 2); if (c == 0) { if (i + 1 < limit && Marshal.ReadInt16(text, (i + 1) * 2) == 0) terminated = true; break; } value.Append(c); }
                if (!terminated || value.ToString() != "SeChangeNotifyPrivilege") throw new IOException("SCM RequiredPrivileges must exactly match the one-privilege allowlist");
            }
            finally { Marshal.FreeHGlobal(p); }
        }
        internal static ServiceIdentityLease Create()
        {
            ServiceIdentityLease x = new ServiceIdentityLease();
            try
            {
                NoImpersonation(); x.pid = GetCurrentProcessId(); x.process = OpenProcess(0x1000, false, x.pid); if (x.process == IntPtr.Zero) throw NativeFile.Error("OpenProcess(self)");
                IntPtr openedToken; if (!OpenProcessToken(x.process, 8, out openedToken)) throw NativeFile.Error("OpenProcessToken"); x.token = openedToken;
                Statistics s = InspectToken(x.token); x.originalTokenId = s.TokenId.Value; x.originalAuthId = s.AuthenticationId.Value;
                x.scm = OpenSCManagerW(null, null, 1); if (x.scm == IntPtr.Zero) throw NativeFile.Error("OpenSCManagerW");
                x.service = OpenServiceW(x.scm, Name, 5); if (x.service == IntPtr.Zero) throw NativeFile.Error("OpenServiceW(fixed)");
                StringBuilder image = new StringBuilder(32768); uint n = GetModuleFileNameW(IntPtr.Zero, image, 32768);
                if (n == 0 || n >= 32768 || !String.Equals(image.ToString(), Image, StringComparison.OrdinalIgnoreCase)) throw new IOException("Current service image path mismatch");
                x.Revalidate(); return x;
            }
            catch { x.Dispose(); throw; }
        }
        public void Revalidate()
        {
            if (disposed) throw new ObjectDisposedException("ServiceIdentityLease"); NoImpersonation(); ServiceConfig();
            IntPtr t; if (!OpenProcessToken(process, 8, out t)) throw NativeFile.Error("OpenProcessToken(revalidate)");
            try { Statistics s = InspectToken(t); if (s.TokenId.Value != originalTokenId || s.AuthenticationId.Value != originalAuthId) throw new IOException("Primary token replaced"); }
            finally { CloseHandle(t); }
        }
        public void Dispose()
        {
            if (disposed) return; disposed = true;
            if (token != IntPtr.Zero) CloseHandle(token); if (process != IntPtr.Zero) CloseHandle(process);
            if (service != IntPtr.Zero) CloseServiceHandle(service); if (scm != IntPtr.Zero) CloseServiceHandle(scm);
        }
    }
}
