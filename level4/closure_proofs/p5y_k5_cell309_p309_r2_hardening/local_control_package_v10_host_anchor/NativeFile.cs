using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using Microsoft.Win32.SafeHandles;

namespace P309HostAnchorV10
{
    internal static class NativeFile
    {
        internal const uint Read = 0x80000000, Write = 0x40000000, Delete = 0x10000;
        internal const uint ShareRead = 1, OpenExisting = 3, CreateNew = 1;
        internal const uint Normal = 0x80, Reparse = 0x400, Directory = 0x10;
        internal const uint OpenReparse = 0x00200000, BackupSemantics = 0x02000000, WriteThrough = 0x80000000;
        [StructLayout(LayoutKind.Sequential)] internal struct Info
        {
            internal uint Attributes; internal System.Runtime.InteropServices.ComTypes.FILETIME Created, Accessed, Written;
            internal uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
            internal ulong Id { get { return ((ulong)IndexHigh << 32) | IndexLow; } }
            internal long Size { get { return ((long)SizeHigh << 32) | SizeLow; } }
        }
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        internal static extern SafeFileHandle CreateFileW(string path, uint access, uint share, IntPtr sa, uint creation, uint flags, IntPtr template);
        [DllImport("kernel32.dll", SetLastError = true)] internal static extern bool GetFileInformationByHandle(SafeFileHandle h, out Info info);
        [DllImport("kernel32.dll", SetLastError = true)] internal static extern bool FlushFileBuffers(SafeFileHandle h);
        [DllImport("kernel32.dll", SetLastError = true)] internal static extern bool SetFilePointerEx(SafeFileHandle h, long offset, out long result, uint method);
        [DllImport("kernel32.dll", SetLastError = true)] internal static extern bool ReadFile(SafeFileHandle h, byte[] b, uint n, out uint count, IntPtr overlap);
        [DllImport("kernel32.dll", SetLastError = true)] internal static extern bool WriteFile(SafeFileHandle h, byte[] b, uint n, out uint count, IntPtr overlap);
        [DllImport("kernel32.dll", SetLastError = true)] internal static extern bool SetFileInformationByHandle(SafeFileHandle h, int cls, IntPtr data, uint size);
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)] internal static extern uint GetFinalPathNameByHandleW(SafeFileHandle h, StringBuilder path, uint capacity, uint flags);
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        internal static extern bool GetVolumeInformationByHandleW(SafeFileHandle h, StringBuilder name, uint n, out uint serial, out uint max, out uint flags, StringBuilder fs, uint fsn);
        [DllImport("advapi32.dll", SetLastError = true)] internal static extern uint GetSecurityInfo(SafeFileHandle h, int type, uint parts, out IntPtr owner, out IntPtr group, out IntPtr dacl, out IntPtr sacl, out IntPtr sd);
        [DllImport("advapi32.dll")] internal static extern uint GetSecurityDescriptorLength(IntPtr sd);
        [DllImport("kernel32.dll")] internal static extern IntPtr LocalFree(IntPtr p);
        internal static Exception Error(string op) { int rc = Marshal.GetLastWin32Error(); return new Win32Exception(rc, op + " [Win32=" + rc + "]"); }
        internal static SafeFileHandle Open(string p, uint access, uint share, uint creation, bool dir)
        {
            SafeFileHandle h = CreateFileW(p, access, share, IntPtr.Zero, creation, OpenReparse | (dir ? BackupSemantics : Normal) | ((access & Write) != 0 ? WriteThrough : 0), IntPtr.Zero);
            if (h.IsInvalid) { int rc = Marshal.GetLastWin32Error(); h.Dispose(); throw new Win32Exception(rc, "CreateFileW: " + Path.GetFileName(p)); }
            return h;
        }
        internal static Info Facts(SafeFileHandle h, bool directory)
        {
            Info i; if (!GetFileInformationByHandle(h, out i)) throw Error("GetFileInformationByHandle");
            if ((i.Attributes & Reparse) != 0 || ((i.Attributes & Directory) != 0) != directory) throw new IOException("Unexpected file type/reparse point");
            if (!directory && i.Links != 1) throw new IOException("Hard-linked anchor object refused");
            if (!directory && (i.Attributes & (0x200U | 0x800U)) != 0) throw new IOException("Sparse/compressed anchor object refused");
            return i;
        }
        internal static void Ntfs(SafeFileHandle h)
        {
            uint a, b, c; StringBuilder fs = new StringBuilder(64);
            if (!GetVolumeInformationByHandleW(h, null, 0, out a, out b, out c, fs, 64)) throw Error("GetVolumeInformationByHandleW");
            if (fs.ToString() != "NTFS") throw new IOException("NTFS required");
        }
        internal static void Seek(SafeFileHandle h, long n) { long actual; if (!SetFilePointerEx(h, n, out actual, 0) || actual != n) throw Error("SetFilePointerEx"); }
        internal static byte[] ReadAll(SafeFileHandle h, int maximum)
        {
            Info i = Facts(h, false); if (i.Size < 0 || i.Size > maximum) throw new IOException("Object length outside fixed bound");
            byte[] b = new byte[(int)i.Size]; Seek(h, 0); uint got;
            if (b.Length != 0 && (!ReadFile(h, b, (uint)b.Length, out got, IntPtr.Zero) || got != b.Length)) throw new IOException("Incomplete fixed-object read");
            return b;
        }
        internal static void WriteAt(SafeFileHandle h, long position, byte[] b)
        {
            Seek(h, position); uint written;
            if (!WriteFile(h, b, (uint)b.Length, out written, IntPtr.Zero) || written != b.Length) throw new IOException("Incomplete journal write; never retry this epoch");
        }
        internal static void Flush(SafeFileHandle h) { if (!FlushFileBuffers(h)) throw Error("FlushFileBuffers(file)"); }
        internal static string Hash(byte[] b) { using (SHA256 s = SHA256.Create()) return Hex(s.ComputeHash(b)); }
        internal static string Hex(byte[] b) { return BitConverter.ToString(b).Replace("-", "").ToLowerInvariant(); }
        internal static bool Equal(byte[] a, byte[] b)
        { if (a.Length != b.Length) return false; int x = 0; for (int i = 0; i < a.Length; i++) x |= a[i] ^ b[i]; return x == 0; }
        internal static string HashHeld(SafeFileHandle h, int bound) { return Hash(ReadAll(h, bound)); }
        internal static string Identity(Info i) { return i.Volume.ToString("x8") + ":" + i.Id.ToString("x16"); }
        internal static void Custody(SafeFileHandle h, string serviceSid, bool strict, bool protectedDacl, bool root)
        {
            IntPtr owner, group, dacl, sacl, sd; uint rc = GetSecurityInfo(h, 1, 7, out owner, out group, out dacl, out sacl, out sd);
            if (rc != 0) throw new Win32Exception((int)rc, "GetSecurityInfo");
            try
            {
                uint length = GetSecurityDescriptorLength(sd); if (length == 0 || length > 65536) throw new IOException("Invalid security descriptor length");
                byte[] b = new byte[length]; Marshal.Copy(sd, b, 0, (int)length); RawSecurityDescriptor r = new RawSecurityDescriptor(b, 0);
                string o = r.Owner == null ? "" : r.Owner.Value;
                string ti = "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464";
                if (o != "S-1-5-18" && o != "S-1-5-32-544" && !(root == false && strict && o == serviceSid) && !(strict == false && o == ti)) throw new IOException("Untrusted owner");
                if (r.DiscretionaryAcl == null || (protectedDacl && (r.ControlFlags & ControlFlags.DiscretionaryAclProtected) == 0)) throw new IOException("Missing/unprotected required DACL");
                // Ancestors may allow new child directories (APPEND_DATA=4), but not data/EA/attribute
                // mutation, child deletion, DELETE, WRITE_DAC/WRITE_OWNER or generic mutation rights.
                uint forbidden = strict ? 0x500D0156U : 0x500D0152U;
                foreach (GenericAce ace in r.DiscretionaryAcl)
                {
                    CommonAce c = ace as CommonAce; if (c == null || c.IsCallback) throw new IOException("Unsupported ACL ACE type");
                    if (c.AceQualifier == AceQualifier.AccessDenied) continue;
                    if (c.AceQualifier != AceQualifier.AccessAllowed) throw new IOException("Unsupported DACL ACE");
                    if ((c.AceFlags & AceFlags.InheritOnly) != 0) continue;
                    string s = c.SecurityIdentifier.Value;
                    if (s != "S-1-5-18" && s != "S-1-5-32-544" && s != ti && !(strict && s == serviceSid) && (((uint)c.AccessMask & forbidden) != 0)) throw new IOException("Untrusted mutating ACE");
                }
            }
            finally { if (sd != IntPtr.Zero) LocalFree(sd); }
        }
        internal static List<SafeFileHandle> PinDirectories(string root, bool production, string sid)
        {
            string p = Path.GetFullPath(root);
            if (p.Length < 4 || p[1] != ':' || p[2] != '\\' || p.StartsWith("\\") || p.IndexOf(':', 2) >= 0 || p != root.TrimEnd('\\')) throw new IOException("Canonical local fixed path required");
            List<SafeFileHandle> held = new List<SafeFileHandle>();
            try
            {
                string current = p.Substring(0, 3); string[] pieces = p.Substring(3).Split('\\');
                for (int n = -1; n < pieces.Length; n++)
                {
                    if (n >= 0) { if (pieces[n].Length == 0 || pieces[n].EndsWith(".") || pieces[n].EndsWith(" ")) throw new IOException("Noncanonical path component"); current = Path.Combine(current, pieces[n]); }
                    // Retain no-share-delete identity pins. FILE_SHARE_WRITE is required for legitimate
                    // child namespace operations (including rename); custody, not sharing, excludes foreign writers.
                    SafeFileHandle h = Open(current, Read, ShareRead | 2U, OpenExisting, true); held.Add(h); Facts(h, true); Ntfs(h);
                    if (production) Custody(h, sid, n == pieces.Length - 1, n == pieces.Length - 1, n == pieces.Length - 1);
                }
                return held;
            }
            catch { foreach (SafeFileHandle h in held) h.Dispose(); throw; }
        }
        internal static void PublishNoReplace(SafeFileHandle h, string fixedDestination)
        {
            // FILE_RENAME_INFO: BOOLEAN at 0, pointer aligned to pointer size, DWORD then UTF16 name.
            int ptr = IntPtr.Size, rootOffset = ptr, lengthOffset = rootOffset + ptr, nameOffset = lengthOffset + 4;
            byte[] name = Encoding.Unicode.GetBytes(fixedDestination); int size = nameOffset + name.Length + 2;
            IntPtr p = Marshal.AllocHGlobal(size);
            try
            {
                byte[] zero = new byte[size]; Marshal.Copy(zero, 0, p, size); Marshal.WriteIntPtr(p, rootOffset, IntPtr.Zero);
                Marshal.WriteInt32(p, lengthOffset, name.Length); Marshal.Copy(name, 0, IntPtr.Add(p, nameOffset), name.Length);
                if (!SetFileInformationByHandle(h, 3, p, (uint)size)) throw Error("SetFileInformationByHandle(FileRenameInfo,no-replace)");
                Flush(h);
                StringBuilder actual = new StringBuilder(32768); uint length = GetFinalPathNameByHandleW(h, actual, 32768, 0);
                if (length == 0 || length >= 32768 || !String.Equals(actual.ToString(), "\\\\?\\" + fixedDestination, StringComparison.OrdinalIgnoreCase)) throw new IOException("Published handle's final path differs from the fixed destination");
            }
            finally { Marshal.FreeHGlobal(p); }
        }
    }
}
