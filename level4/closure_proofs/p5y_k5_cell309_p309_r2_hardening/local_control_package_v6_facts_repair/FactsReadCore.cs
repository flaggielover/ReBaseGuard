// Explicit production entry points are separate from injected, synthetic-test entry points.
// Loading/compiling this file does not query ETW, SCM, LSA, or start a process.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using System.Threading.Tasks;

namespace P309ReadinessV6
{
    public class FactResult
    {
        public string ObjectIdentity;
        public string State = "UNKNOWN";
        public string Error;
        public readonly List<string> CleanupErrors = new List<string>();
        public readonly List<string> NotAttempted = new List<string>();
        public string Admission = "BLOCKED";
    }

    public sealed class EtwResult : FactResult
    {
        public bool ProbeAttempted, FetchAttempted;
        public uint? ProbeRc, FetchRc, RequiredSize, Capacity, ReturnedSize;
        public byte[] DescriptorBytes;
        public string DescriptorBase64, DescriptorSha256, Sddl;
    }

    public delegate uint EtwQuery(ref Guid guid, IntPtr buffer, ref uint size);

    public sealed class Win32Stage
    {
        public bool Attempted;
        public bool? Succeeded;
        public int? Win32;
        public string Error;
    }

    public sealed class ServiceResult : FactResult
    {
        public readonly Win32Stage ManagerOpen = new Win32Stage();
        public readonly Win32Stage ServiceOpen = new Win32Stage();
        public readonly Win32Stage ServiceClose = new Win32Stage();
        public readonly Win32Stage ManagerClose = new Win32Stage();
    }

    public interface IServiceApi
    {
        IntPtr OpenManager(uint access, out int error);
        IntPtr OpenService(IntPtr manager, string name, uint access, out int error);
        bool Close(IntPtr handle, out int error);
    }

    public sealed class NtStage
    {
        public bool Attempted;
        public uint? NtStatus, Win32;
        public string Error;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct LsaUnicodeString
    {
        public ushort Length, MaximumLength;
        public IntPtr Buffer;
    }

    public sealed class RightsResult : FactResult
    {
        public readonly NtStage Open = new NtStage();
        public readonly NtStage Query = new NtStage();
        public readonly NtStage Free = new NtStage();
        public readonly NtStage Close = new NtStage();
        public uint? ReturnedCount;
        public bool? OpenOutputNonzero, QueryOutputNonzero;
        public string[] Rights;
        public bool DirectRightsEnumerated;
        public bool EffectiveRightsInferred = false;
    }

    public interface ILsaApi
    {
        uint OpenPolicy(uint access, out IntPtr policy);
        uint EnumerateRights(IntPtr policy, IntPtr sid, out IntPtr rights, out uint count);
        uint StatusToWin32(uint status);
        uint FreeRights(IntPtr rights);
        uint ClosePolicy(IntPtr policy);
    }

    public sealed class PowerCommand
    {
        public readonly string FileName = @"C:\Windows\System32\powercfg.exe";
        public readonly string Arguments = "/query SCHEME_CURRENT SUB_SLEEP";
        public readonly string WorkingDirectory = @"C:\Windows\System32";
        public readonly int TimeoutMilliseconds = 20000;
        public readonly int KillWaitMilliseconds = 2000;
        public readonly int StreamCharacterLimit = 65536;
        public readonly int StreamByteLimit = 131072;
        public readonly bool UseShellExecute = false, CreateNoWindow = true;
        internal PowerCommand() { }
    }

    public sealed class PowerRunSnapshot
    {
        public bool StartAttempted, Started, ExitObserved, StopConfirmed, TimedOut;
        public bool KillRequested, ProcessRetained;
        public bool? KillCallSucceeded;
        public int? ProcessId, ExitCode;
        public bool StdoutComplete, StderrComplete, StdoutTruncated, StderrTruncated;
        public bool StdoutRawTruncated, StderrRawTruncated;
        public bool StdoutDecodeAttempted, StderrDecodeAttempted, StdoutStrictDecode, StderrStrictDecode;
        public bool StdoutDecodeSucceeded, StderrDecodeSucceeded;
        public int? StdoutCodePage, StderrCodePage;
        public string StdoutEncoding, StderrEncoding, StdoutEncodingSource, StderrEncodingSource;
        public string StdoutDecodeError, StderrDecodeError;
        public string StdoutRawBase64, StderrRawBase64, StdoutCapturedSha256, StderrCapturedSha256;
        public int StdoutCapturedBytes, StderrCapturedBytes;
        public long StdoutObservedBytes, StderrObservedBytes;
        public string Stdout = "", Stderr = "", Error, KillError, DisposeError;
        // Raw payload is published as base64, avoiding huge JSON integer arrays.
        internal byte[] StdoutBytes, StderrBytes;
        public void SetStdoutRaw(byte[] bytes, int codePage)
        { StdoutBytes = bytes == null ? null : (byte[])bytes.Clone(); StdoutCodePage = codePage;
          StdoutObservedBytes = bytes == null ? 0 : bytes.Length; StdoutEncodingSource = "Injected explicit encoding"; }
        public void SetStderrRaw(byte[] bytes, int codePage)
        { StderrBytes = bytes == null ? null : (byte[])bytes.Clone(); StderrCodePage = codePage;
          StderrObservedBytes = bytes == null ? 0 : bytes.Length; StderrEncodingSource = "Injected explicit encoding"; }
        public byte[] GetStdoutRawBytes() { return StdoutBytes == null ? null : (byte[])StdoutBytes.Clone(); }
        public byte[] GetStderrRawBytes() { return StderrBytes == null ? null : (byte[])StderrBytes.Clone(); }
        public string OutputSemantics = "Captured command output only; decoder/code page is recorded, policy format/meaning is not established.";
        public long ElapsedMilliseconds;
        public string TimingLimitation =
            "20s plus a 2s owned-process stop wait are requested budgets; OS Start/Wait/Kill/IO calls cannot be hard-preempted.";
    }

    public interface IPowerRunner
    {
        PowerRunSnapshot Run(PowerCommand command);
    }

    public sealed class PowerResult : FactResult
    {
        public PowerRunSnapshot Run;
    }

    public sealed class FactSummary
    {
        public readonly List<string> Unknown = new List<string>();
        public readonly List<string> NotAttempted = new List<string>();
        public readonly List<string> CleanupErrors = new List<string>();
        public bool ProductionReadinessProven = false;
        public string Admission = "BLOCKED";
    }

    public static class Core
    {
        const uint MoreData = 234, ScManagerConnect = 1, ServiceQueryStatus = 4, PolicyRead = 0x801;
        const uint MaximumDescriptorBytes = 65536;
        static readonly string[] Guids = {
            "9e814aad-3204-11d2-9a82-006008a86939", "b47309d4-5e53-4a10-a67a-202610160001" };
        static readonly string[] Services = {
            "ReBaseGuardP309Observer", "ReBaseGuardP309Controller", "ReBaseGuardP309Relay" };
        static readonly string[] Sids = {
            "S-1-5-80-1932864767-2148301307-763792368-432637623-2158176663",
            "S-1-5-80-1389429364-2543163971-322551805-3183066981-1946276422",
            "S-1-5-80-2549398394-424828454-1189152689-2921672270-2793605460" };

        static bool Allowed(string value, string[] values, StringComparison comparison)
        {
            foreach (string expected in values)
                if (String.Equals(value, expected, comparison)) return true;
            return false;
        }
        static string Describe(Exception error) { return error.GetType().FullName + ": " + error.Message; }
        static string Digest(byte[] bytes)
        {
            using (SHA256 hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        // These four overloads are the ONLY production dispatch entry points.
        public static EtwResult ReadEtw(string guid) { return ReadEtw(guid, NativeEtwQuery); }
        public static ServiceResult ReadService(string name) { return ReadService(name, new NativeServiceApi()); }
        public static RightsResult ReadRights(string sid) { return ReadRights(sid, new NativeLsaApi()); }
        public static PowerResult ReadPower() { return ReadPower(new BoundedPowerRunner()); }

        // All tests use the following injected overloads; none fall back to native APIs.
        public static EtwResult ReadEtw(string text, EtwQuery query)
        {
            EtwResult result = new EtwResult(); result.ObjectIdentity = text;
            IntPtr memory = IntPtr.Zero;
            try
            {
                if (!Allowed(text, Guids, StringComparison.OrdinalIgnoreCase) || query == null)
                    throw new ArgumentException("Only a fixed GUID and an explicit query delegate are accepted.");
                Guid guid = new Guid(text); uint size = 0;
                result.ProbeAttempted = true;
                try { result.ProbeRc = query(ref guid, IntPtr.Zero, ref size); }
                finally { result.RequiredSize = size; }
                if (result.ProbeRc != MoreData || size == 0 || size > MaximumDescriptorBytes)
                { result.Error = "Probe did not return ERROR_MORE_DATA with a bounded positive size."; return result; }
                result.Capacity = size;
                memory = Marshal.AllocHGlobal((int)size);
                result.FetchAttempted = true;
                try { result.FetchRc = query(ref guid, memory, ref size); }
                finally { result.ReturnedSize = size; }
                if (result.FetchRc != 0 || size != result.Capacity.Value)
                { result.Error = "Fetch failed or descriptor size changed; no retry."; return result; }
                byte[] bytes = new byte[(int)size]; Marshal.Copy(memory, bytes, 0, bytes.Length);
                RawSecurityDescriptor descriptor = new RawSecurityDescriptor(bytes, 0);
                if ((descriptor.ControlFlags & ControlFlags.SelfRelative) == 0)
                    throw new InvalidDataException("A self-relative descriptor was not returned.");
                string sddl = descriptor.GetSddlForm(AccessControlSections.All);
                result.DescriptorBytes = bytes;
                result.DescriptorBase64 = Convert.ToBase64String(bytes);
                result.DescriptorSha256 = Digest(bytes); result.Sddl = sddl;
                result.State = "OBSERVED";
            }
            catch (Exception error) { result.Error = Describe(error); }
            finally
            {
                if (memory != IntPtr.Zero) Marshal.FreeHGlobal(memory);
                if (!result.ProbeAttempted) result.NotAttempted.Add("probe");
                if (!result.FetchAttempted) result.NotAttempted.Add("fetch");
            }
            return result;
        }

        public static ServiceResult ReadService(string name, IServiceApi api)
        {
            ServiceResult result = new ServiceResult(); result.ObjectIdentity = name;
            IntPtr manager = IntPtr.Zero, service = IntPtr.Zero;
            bool managerOwned = false, serviceOwned = false;
            try
            {
                if (!Allowed(name, Services, StringComparison.OrdinalIgnoreCase) || api == null)
                    throw new ArgumentException("Only a complete fixed service name and an explicit API are accepted.");
                int error; result.ManagerOpen.Attempted = true;
                manager = api.OpenManager(ScManagerConnect, out error);
                managerOwned = manager != IntPtr.Zero;
                result.ManagerOpen.Succeeded = managerOwned; result.ManagerOpen.Win32 = managerOwned ? 0 : error;
                if (!managerOwned) { result.Error = "SCM open failed; service existence remains UNKNOWN."; return result; }
                result.ServiceOpen.Attempted = true;
                service = api.OpenService(manager, name, ServiceQueryStatus, out error);
                serviceOwned = service != IntPtr.Zero;
                result.ServiceOpen.Succeeded = serviceOwned; result.ServiceOpen.Win32 = serviceOwned ? 0 : error;
                if (serviceOwned) result.State = "PRESENT";
                else if (error == 1060) result.State = "ABSENT";
                else result.Error = "Service open failed without ERROR_SERVICE_DOES_NOT_EXIST.";
            }
            catch (Exception error) { result.Error = Describe(error); }
            finally
            {
                if (serviceOwned) CloseService(api, service, result.ServiceClose, result, "service");
                if (managerOwned) CloseService(api, manager, result.ManagerClose, result, "SCM");
                AddNotAttempted(result.NotAttempted, "SCM open", result.ManagerOpen.Attempted);
                AddNotAttempted(result.NotAttempted, "service open", result.ServiceOpen.Attempted);
                AddNotAttempted(result.NotAttempted, "service close (no owned handle)", result.ServiceClose.Attempted);
                AddNotAttempted(result.NotAttempted, "SCM close (no owned handle)", result.ManagerClose.Attempted);
            }
            return result;
        }

        static void AddNotAttempted(List<string> list, string name, bool attempted)
        { if (!attempted) list.Add(name); }
        static void CloseService(IServiceApi api, IntPtr handle, Win32Stage stage, FactResult result, string name)
        {
            stage.Attempted = true;
            try
            {
                int error; bool ok = api.Close(handle, out error);
                stage.Succeeded = ok; stage.Win32 = ok ? 0 : error;
                if (!ok) result.CleanupErrors.Add(name + " CloseServiceHandle failed: " + error);
            }
            catch (Exception error) { stage.Error = Describe(error); result.CleanupErrors.Add(name + ": " + stage.Error); }
        }

        public static RightsResult ReadRights(string sidText, ILsaApi api)
        {
            RightsResult result = new RightsResult(); result.ObjectIdentity = sidText;
            IntPtr policy = IntPtr.Zero, rights = IntPtr.Zero, sidMemory = IntPtr.Zero;
            bool policyOwned = false, rightsOwned = false;
            try
            {
                if (!Allowed(sidText, Sids, StringComparison.Ordinal) || api == null)
                    throw new ArgumentException("Only a fixed SID and an explicit API are accepted.");
                result.Open.Attempted = true;
                uint status = api.OpenPolicy(PolicyRead, out policy);
                policyOwned = status == 0 && policy != IntPtr.Zero;
                result.Open.NtStatus = status; result.OpenOutputNonzero = policy != IntPtr.Zero;
                result.Open.Win32 = api.StatusToWin32(status);
                if (status != 0) { result.Error = "Policy open failed; no rights query was attempted."; return result; }
                if (!policyOwned) throw new InvalidDataException("Successful policy open returned a null handle.");
                SecurityIdentifier sid = new SecurityIdentifier(sidText);
                byte[] sidBytes = new byte[sid.BinaryLength]; sid.GetBinaryForm(sidBytes, 0);
                sidMemory = Marshal.AllocHGlobal(sidBytes.Length); Marshal.Copy(sidBytes, 0, sidMemory, sidBytes.Length);
                uint count; result.Query.Attempted = true;
                status = api.EnumerateRights(policy, sidMemory, out rights, out count);
                rightsOwned = status == 0 && rights != IntPtr.Zero;
                result.Query.NtStatus = status; result.QueryOutputNonzero = rights != IntPtr.Zero;
                result.ReturnedCount = count; result.Query.Win32 = api.StatusToWin32(status);
                if (status != 0)
                {
                    if (result.Query.Win32 == 2) result.State = "NOT_FOUND_DIRECT_RIGHTS_NOT_ENUMERATED";
                    result.Error = "Direct rights were not enumerated; effective rights are not inferred.";
                    return result;
                }
                if (count > 256 || (count != 0 && rights == IntPtr.Zero))
                    throw new InvalidDataException("Invalid successful rights response.");
                string[] names = new string[(int)count]; int stride = Marshal.SizeOf(typeof(LsaUnicodeString));
                for (int i = 0; i < names.Length; ++i)
                {
                    LsaUnicodeString name = (LsaUnicodeString)Marshal.PtrToStructure(
                        IntPtr.Add(rights, checked(i * stride)), typeof(LsaUnicodeString));
                    if (name.Length == 0 || name.Length > name.MaximumLength ||
                        (name.Length & 1) != 0 || name.Buffer == IntPtr.Zero)
                        throw new InvalidDataException("Malformed successful LSA_UNICODE_STRING.");
                    names[i] = Marshal.PtrToStringUni(name.Buffer, name.Length / 2);
                }
                result.Rights = names; result.DirectRightsEnumerated = true; result.State = "OBSERVED";
            }
            catch (Exception error) { result.Error = Describe(error); }
            finally
            {
                if (rightsOwned) CleanupLsa(api, rights, true, result.Free, result);
                if (policyOwned) CleanupLsa(api, policy, false, result.Close, result);
                if (sidMemory != IntPtr.Zero) Marshal.FreeHGlobal(sidMemory);
                AddNotAttempted(result.NotAttempted, "policy open", result.Open.Attempted);
                AddNotAttempted(result.NotAttempted, "rights query", result.Query.Attempted);
                AddNotAttempted(result.NotAttempted, "rights free (no successful owned result)", result.Free.Attempted);
                AddNotAttempted(result.NotAttempted, "policy close (no successful owned handle)", result.Close.Attempted);
            }
            return result;
        }

        static void CleanupLsa(ILsaApi api, IntPtr pointer, bool free, NtStage stage, FactResult result)
        {
            stage.Attempted = true;
            try
            {
                uint status = free ? api.FreeRights(pointer) : api.ClosePolicy(pointer);
                stage.NtStatus = status; stage.Win32 = api.StatusToWin32(status);
                if (status != 0) result.CleanupErrors.Add((free ? "LsaFreeMemory" : "LsaClose") +
                    " failed: NTSTATUS=" + status + ", Win32=" + stage.Win32);
            }
            catch (Exception error) { stage.Error = Describe(error); result.CleanupErrors.Add(stage.Error); }
        }

        public static PowerResult ReadPower(IPowerRunner runner)
        {
            PowerResult result = new PowerResult(); result.ObjectIdentity = "SCHEME_CURRENT/SUB_SLEEP";
            try
            {
                if (runner == null) throw new ArgumentNullException("runner");
                result.Run = runner.Run(new PowerCommand());
                PowerRunSnapshot run = result.Run;
                if (run == null) throw new InvalidDataException("Runner returned no observation.");
                // Decode exact bounded raw bytes, never a StreamReader replacement-character transcript.
                DecodeCapture(run, true); DecodeCapture(run, false);
                if (!run.StartAttempted) result.NotAttempted.Add("process start");
                if (!run.Started) result.NotAttempted.Add("process wait/capture");
                if (!run.KillRequested) result.NotAttempted.Add("owned-process kill (not required/requested)");
                if (run.Started && !run.StopConfirmed)
                    result.CleanupErrors.Add("Owned process exit is unconfirmed; retain its identity and scene, no automatic retry.");
                if (run.DisposeError != null) result.CleanupErrors.Add(run.DisposeError);
                if (run.StartAttempted && run.Started && run.ExitObserved && run.StopConfirmed && !run.TimedOut &&
                    run.ExitCode == 0 && run.StdoutComplete && run.StderrComplete &&
                    !run.StdoutRawTruncated && !run.StderrRawTruncated &&
                    run.StdoutDecodeSucceeded && run.StderrDecodeSucceeded &&
                    !run.StdoutTruncated && !run.StderrTruncated && run.Error == null && run.Stdout.Length != 0)
                    result.State = "OBSERVED";
                else result.Error = "Power query/capture was incomplete, failed, timed out, or truncated; inspect Run.";
            }
            catch (Exception error) { result.Error = Describe(error); }
            return result;
        }

        static void DecodeCapture(PowerRunSnapshot run, bool stdout)
        {
            byte[] bytes = stdout ? run.StdoutBytes : run.StderrBytes;
            int? selected = stdout ? run.StdoutCodePage : run.StderrCodePage;
            string source = stdout ? run.StdoutEncodingSource : run.StderrEncodingSource;
            string text = "", error = null, encodingName = null; bool attempted = false, success = false, truncated = false;
            if (bytes != null && bytes.Length > 131072)
            {
                byte[] bounded = new byte[131072]; Buffer.BlockCopy(bytes, 0, bounded, 0, bounded.Length); bytes = bounded;
                if (stdout) run.StdoutRawTruncated = true; else run.StderrRawTruncated = true;
            }
            if (bytes != null)
            {
                string base64 = Convert.ToBase64String(bytes), sha256 = Digest(bytes);
                if (stdout) { run.StdoutBytes = bytes; run.StdoutRawBase64 = base64; run.StdoutCapturedSha256 = sha256; run.StdoutCapturedBytes = bytes.Length; }
                else { run.StderrBytes = bytes; run.StderrRawBase64 = base64; run.StderrCapturedSha256 = sha256; run.StderrCapturedBytes = bytes.Length; }
                try
                {
                    int skip = 0;
                    if (bytes.Length >= 4 && bytes[0] == 0xff && bytes[1] == 0xfe && bytes[2] == 0 && bytes[3] == 0)
                    { selected = 12000; skip = 4; source = "UTF-32LE BOM"; }
                    else if (bytes.Length >= 4 && bytes[0] == 0 && bytes[1] == 0 && bytes[2] == 0xfe && bytes[3] == 0xff)
                    { selected = 12001; skip = 4; source = "UTF-32BE BOM"; }
                    else if (bytes.Length >= 3 && bytes[0] == 0xef && bytes[1] == 0xbb && bytes[2] == 0xbf)
                    { selected = 65001; skip = 3; source = "UTF-8 BOM"; }
                    else if (bytes.Length >= 2 && bytes[0] == 0xff && bytes[1] == 0xfe)
                    { selected = 1200; skip = 2; source = "UTF-16LE BOM"; }
                    else if (bytes.Length >= 2 && bytes[0] == 0xfe && bytes[1] == 0xff)
                    { selected = 1201; skip = 2; source = "UTF-16BE BOM"; }
                    if (!selected.HasValue) throw new InvalidDataException("No selected output decoder was recorded.");
                    attempted = true;
                    Encoding encoding = Encoding.GetEncoding(selected.Value, EncoderFallback.ExceptionFallback, DecoderFallback.ExceptionFallback);
                    encodingName = encoding.WebName;
                    text = encoding.GetString(bytes, skip, bytes.Length - skip); success = true;
                    if (text.Length > 65536) { text = text.Substring(0, 65536); truncated = true; }
                }
                catch (Exception exception) { error = Describe(exception); }
            }
            else error = "No raw capture was returned.";
            if (stdout)
            {
                run.Stdout = text; run.StdoutCodePage = selected; run.StdoutEncoding = encodingName; run.StdoutEncodingSource = source;
                run.StdoutDecodeAttempted = attempted; run.StdoutStrictDecode = attempted; run.StdoutDecodeSucceeded = success;
                run.StdoutDecodeError = error; run.StdoutTruncated = run.StdoutTruncated || truncated;
            }
            else
            {
                run.Stderr = text; run.StderrCodePage = selected; run.StderrEncoding = encodingName; run.StderrEncodingSource = source;
                run.StderrDecodeAttempted = attempted; run.StderrStrictDecode = attempted; run.StderrDecodeSucceeded = success;
                run.StderrDecodeError = error; run.StderrTruncated = run.StderrTruncated || truncated;
            }
        }

        public static FactSummary Summarize(FactResult[] facts)
        {
            FactSummary summary = new FactSummary();
            if (facts == null) { summary.Unknown.Add("No result array supplied."); return summary; }
            foreach (FactResult fact in facts)
            {
                if (fact == null) { summary.Unknown.Add("Missing per-object result."); continue; }
                string prefix = fact.ObjectIdentity + ": ";
                if (fact.State != "OBSERVED" && fact.State != "PRESENT" && fact.State != "ABSENT")
                    summary.Unknown.Add(prefix + fact.State);
                foreach (string stage in fact.NotAttempted) summary.NotAttempted.Add(prefix + stage);
                foreach (string error in fact.CleanupErrors) summary.CleanupErrors.Add(prefix + error);
            }
            return summary;
        }

        [DllImport(@"C:\Windows\System32\advapi32.dll", ExactSpelling = true)]
        static extern uint EventAccessQuery(ref Guid guid, IntPtr buffer, ref uint size);
        static uint NativeEtwQuery(ref Guid guid, IntPtr buffer, ref uint size)
        { return EventAccessQuery(ref guid, buffer, ref size); }

        sealed class NativeServiceApi : IServiceApi
        {
            [DllImport(@"C:\Windows\System32\advapi32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
            static extern IntPtr OpenSCManagerW(string machine, string database, uint access);
            [DllImport(@"C:\Windows\System32\advapi32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
            static extern IntPtr OpenServiceW(IntPtr manager, string name, uint access);
            [DllImport(@"C:\Windows\System32\advapi32.dll", ExactSpelling = true, SetLastError = true)]
            [return: MarshalAs(UnmanagedType.Bool)]
            static extern bool CloseServiceHandle(IntPtr handle);
            public IntPtr OpenManager(uint access, out int error)
            { IntPtr handle = OpenSCManagerW(null, null, access); error = handle == IntPtr.Zero ? Marshal.GetLastWin32Error() : 0; return handle; }
            public IntPtr OpenService(IntPtr manager, string name, uint access, out int error)
            { IntPtr handle = OpenServiceW(manager, name, access); error = handle == IntPtr.Zero ? Marshal.GetLastWin32Error() : 0; return handle; }
            public bool Close(IntPtr handle, out int error)
            { bool ok = CloseServiceHandle(handle); error = ok ? 0 : Marshal.GetLastWin32Error(); return ok; }
        }

        sealed class NativeLsaApi : ILsaApi
        {
            [StructLayout(LayoutKind.Sequential)]
            struct ObjectAttributes { public uint Length; public IntPtr Root, Name; public uint Attributes; public IntPtr Security, Qos; }
            [DllImport(@"C:\Windows\System32\advapi32.dll", ExactSpelling = true)]
            static extern uint LsaOpenPolicy(IntPtr system, ref ObjectAttributes attributes, uint access, out IntPtr policy);
            [DllImport(@"C:\Windows\System32\advapi32.dll", ExactSpelling = true)]
            static extern uint LsaEnumerateAccountRights(IntPtr policy, IntPtr sid, out IntPtr rights, out uint count);
            [DllImport(@"C:\Windows\System32\advapi32.dll", ExactSpelling = true)]
            static extern uint LsaNtStatusToWinError(uint status);
            [DllImport(@"C:\Windows\System32\advapi32.dll", ExactSpelling = true)]
            static extern uint LsaFreeMemory(IntPtr memory);
            [DllImport(@"C:\Windows\System32\advapi32.dll", ExactSpelling = true)]
            static extern uint LsaClose(IntPtr policy);
            public uint OpenPolicy(uint access, out IntPtr policy)
            { ObjectAttributes attributes = new ObjectAttributes(); attributes.Length = (uint)Marshal.SizeOf(typeof(ObjectAttributes)); return LsaOpenPolicy(IntPtr.Zero, ref attributes, access, out policy); }
            public uint EnumerateRights(IntPtr policy, IntPtr sid, out IntPtr rights, out uint count)
            { return LsaEnumerateAccountRights(policy, sid, out rights, out count); }
            public uint StatusToWin32(uint status) { return LsaNtStatusToWinError(status); }
            public uint FreeRights(IntPtr rights) { return LsaFreeMemory(rights); }
            public uint ClosePolicy(IntPtr policy) { return LsaClose(policy); }
        }
    }

    // Asynchronous raw reads retain at most Limit bytes while continuing to drain excess.
    // No StreamReader decoding or unbounded line buffer participates in the capture.
    internal sealed class BoundedByteCapture
    {
        readonly object gate = new object();
        readonly byte[] bytes;
        int length;
        internal bool Complete, Truncated;
        internal long ObservedBytes;
        internal string Error;
        internal BoundedByteCapture(int maximum) { bytes = new byte[maximum]; }
        internal void Append(byte[] input, int count)
        {
            lock (gate) { int take = Math.Min(bytes.Length - length, count);
                if (take > 0) { Buffer.BlockCopy(input, 0, bytes, length, take); length += take; }
                ObservedBytes += count; if (take != count) Truncated = true; }
        }
        internal byte[] Snapshot()
        { lock (gate) { byte[] copy = new byte[length]; Buffer.BlockCopy(bytes, 0, copy, 0, length); return copy; } }
        internal async Task Drain(Stream reader)
        {
            try { byte[] buffer = new byte[4096]; int read;
                while ((read = await reader.ReadAsync(buffer, 0, buffer.Length).ConfigureAwait(false)) != 0) Append(buffer, read);
                Complete = true;
            } catch (Exception error) { Error = error.GetType().FullName + ": " + error.Message; }
        }
    }

    internal sealed class BoundedPowerRunner : IPowerRunner
    {
        // If exit cannot be confirmed, retain the owned Process/streams instead of claiming cleanup.
        static readonly List<Process> retained = new List<Process>();
        static int Remaining(Stopwatch clock, int budget)
        { long left = budget - clock.ElapsedMilliseconds; return left <= 0 ? 0 : (int)left; }
        static void ObserveExit(Process process, PowerRunSnapshot result)
        { result.ExitCode = process.ExitCode; result.ExitObserved = true; result.StopConfirmed = true; }
        public PowerRunSnapshot Run(PowerCommand command)
        {
            PowerRunSnapshot result = new PowerRunSnapshot(); Stopwatch clock = Stopwatch.StartNew();
            Process process = new Process(); BoundedByteCapture output = new BoundedByteCapture(command.StreamByteLimit);
            BoundedByteCapture error = new BoundedByteCapture(command.StreamByteLimit);
            Task outputTask = null, errorTask = null;
            try
            {
                ProcessStartInfo start = new ProcessStartInfo();
                start.FileName = command.FileName; start.Arguments = command.Arguments;
                start.WorkingDirectory = command.WorkingDirectory; start.UseShellExecute = false;
                start.CreateNoWindow = true; start.WindowStyle = ProcessWindowStyle.Hidden;
                start.RedirectStandardOutput = true; start.RedirectStandardError = true;
                start.EnvironmentVariables.Clear(); start.EnvironmentVariables["SystemRoot"] = @"C:\Windows";
                start.EnvironmentVariables["WINDIR"] = @"C:\Windows"; start.EnvironmentVariables["PATH"] = @"C:\Windows\System32";
                process.StartInfo = start; result.StartAttempted = true; result.Started = process.Start();
                if (!result.Started) throw new IOException("Process.Start returned false.");
                result.ProcessId = process.Id;
                StreamReader stdout = process.StandardOutput, stderr = process.StandardError;
                result.StdoutCodePage = stdout.CurrentEncoding.CodePage; result.StderrCodePage = stderr.CurrentEncoding.CodePage;
                result.StdoutEncodingSource = "Process.StandardOutput initial decoder; not proof of CLI output format";
                result.StderrEncodingSource = "Process.StandardError initial decoder; not proof of CLI output format";
                // Schedule both raw drains before waiting; even synchronously completed ReadAsync
                // operations must not let one continuously readable stream starve the other.
                outputTask = Task.Run(delegate { return output.Drain(stdout.BaseStream); });
                errorTask = Task.Run(delegate { return error.Drain(stderr.BaseStream); });
                if (process.WaitForExit(Remaining(clock, command.TimeoutMilliseconds))) ObserveExit(process, result);
                else
                {
                    result.TimedOut = true; result.KillRequested = true; Stopwatch stopClock = Stopwatch.StartNew();
                    try { process.Kill(); result.KillCallSucceeded = true; }
                    catch (Exception killError) { result.KillCallSucceeded = false; result.KillError = killError.GetType().FullName + ": " + killError.Message; }
                    if (process.WaitForExit(Remaining(stopClock, command.KillWaitMilliseconds))) ObserveExit(process, result);
                    if (result.StopConfirmed)
                        Task.WaitAll(new Task[] { outputTask, errorTask }, Remaining(stopClock, command.KillWaitMilliseconds));
                }
                if (!result.TimedOut && !Task.WaitAll(new Task[] { outputTask, errorTask }, Remaining(clock, command.TimeoutMilliseconds)))
                { result.TimedOut = true; result.Error = "The total read budget elapsed before both streams reached EOF."; }
            }
            catch (Exception exception) { result.Error = exception.GetType().FullName + ": " + exception.Message; }
            finally
            {
                // An exception after Start also gets one owned-process termination attempt, never a retry.
                if (result.Started && !result.StopConfirmed && !result.KillRequested)
                {
                    result.KillRequested = true; Stopwatch stopClock = Stopwatch.StartNew();
                    try { process.Kill(); result.KillCallSucceeded = true; }
                    catch (Exception killError) { result.KillCallSucceeded = false; result.KillError = killError.GetType().FullName + ": " + killError.Message; }
                    try { if (process.WaitForExit(Remaining(stopClock, command.KillWaitMilliseconds))) ObserveExit(process, result); }
                    catch (Exception waitError) { result.Error = (result.Error ?? "") + "; stop wait: " + waitError.Message; }
                }
                if (result.Started && !result.StopConfirmed)
                { lock (retained) { retained.Add(process); } result.ProcessRetained = true; }
                else
                {
                    try { process.Dispose(); }
                    catch (Exception disposeError) { result.DisposeError = "Owned Process.Dispose: " + disposeError.Message; }
                }
                result.StdoutBytes = output.Snapshot(); result.StderrBytes = error.Snapshot();
                result.StdoutComplete = output.Complete; result.StderrComplete = error.Complete;
                result.StdoutRawTruncated = output.Truncated; result.StderrRawTruncated = error.Truncated;
                result.StdoutObservedBytes = output.ObservedBytes; result.StderrObservedBytes = error.ObservedBytes;
                if (output.Error != null || error.Error != null)
                    result.Error = (result.Error ?? "") + "; stream errors: " + output.Error + "; " + error.Error;
                result.ElapsedMilliseconds = clock.ElapsedMilliseconds;
            }
            return result;
        }
    }
}
