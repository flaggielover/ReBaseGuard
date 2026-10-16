$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.ToString() -notlike '5.1.*' -or [IntPtr]::Size -ne 8){throw 'Windows PowerShell 5.1 x64 required'}
# Compile the source and synthetic fixtures together. No production overload,
# real ETW/SCM/LSA function or real process runner is invoked by these tests.
$source=Join-Path $PSScriptRoot 'FactsReadCore.cs'
$bytes=[IO.File]::ReadAllBytes($source)
$tests=@'
namespace P309ReadinessV6.SyntheticTests
{
    using System;
    using System.Collections.Generic;
    using System.Runtime.InteropServices;
    using System.Reflection;
    using System.Security.AccessControl;
    using System.Text;

    public sealed class Report
    {
        public int Cases, Assertions;
        public bool Passed;
        public string Scope = "SYNTHETIC_INJECTED_READ_CORE_ONLY";
        public int RealEtwCalls = 0, RealScmCalls = 0, RealLsaCalls = 0, RealProcessStarts = 0, Uac = 0;
        public string Admission = "BLOCKED";
    }

    public static class Suite
    {
        static int cases, assertions;
        static string current;
        const string GuidText = "9e814aad-3204-11d2-9a82-006008a86939";
        const string Service = "ReBaseGuardP309Observer";
        const string Sid = "S-1-5-80-1932864767-2148301307-763792368-432637623-2158176663";
        const uint Denied = 0xC0000022, Missing = 0xC0000034;
        static void Case(string name) { current = name; ++cases; }
        internal static void Check(bool condition, string explanation)
        { ++assertions; if (!condition) throw new InvalidOperationException(current + ": " + explanation); }

        static void AbiCase()
        {
            Case("x64 LSA ABI without any native call");
            Check(IntPtr.Size == 8 && Marshal.SizeOf(typeof(LsaUnicodeString)) == 16, "pointer and unicode-string ABI");
            Type native = typeof(Core).GetNestedType("NativeLsaApi", BindingFlags.NonPublic);
            Check(native != null, "native adapter type exists");
            Type attributes = native.GetNestedType("ObjectAttributes", BindingFlags.NonPublic);
            Check(attributes != null && Marshal.SizeOf(attributes) == 48, "object-attributes ABI");
        }

        sealed class FakeEtw
        {
            internal int ProbeCalls, FetchCalls;
            internal uint ProbeCode = 234, FetchCode;
            internal uint? ProbeSize, FetchSize;
            internal bool InvalidDescriptor, FetchThrows;
            readonly byte[] descriptor;
            internal FakeEtw()
            {
                RawSecurityDescriptor sd = new RawSecurityDescriptor("O:SYG:SYD:(A;;GR;;;SY)");
                descriptor = new byte[sd.BinaryLength]; sd.GetBinaryForm(descriptor, 0);
            }
            internal uint Query(ref Guid guid, IntPtr memory, ref uint size)
            {
                Check(guid.ToString() == GuidText, "fixed GUID");
                if (memory == IntPtr.Zero)
                { ++ProbeCalls; Check(size == 0, "zero-size probe"); size = ProbeSize ?? (uint)descriptor.Length; return ProbeCode; }
                ++FetchCalls; Check(FetchCalls == 1, "no fetch retry");
                Check(size == descriptor.Length, "capacity equals successful probe size");
                byte[] data = InvalidDescriptor ? new byte[descriptor.Length] : descriptor;
                Marshal.Copy(data, 0, memory, data.Length);
                size = FetchSize ?? (uint)descriptor.Length;
                if (FetchThrows) throw new InvalidOperationException("synthetic fetch exception");
                return FetchCode;
            }
        }

        static void EtwCases()
        {
            Case("actual ERROR_MORE_DATA probe reaches a single fetch");
            FakeEtw api = new FakeEtw(); EtwResult r = Core.ReadEtw(GuidText, api.Query);
            Check(r.State == "OBSERVED" && r.ProbeRc == 234 && r.FetchRc == 0, "real defect regression");
            Check(r.FetchAttempted && api.ProbeCalls == 1 && api.FetchCalls == 1, "two calls only");
            Check(r.RequiredSize == r.Capacity && r.Capacity == r.ReturnedSize, "phase sizes");
            Check(r.DescriptorBytes.Length > 0 && r.DescriptorBase64 != null && r.Sddl != null &&
                r.DescriptorSha256.Length == 64, "exact bytes, digest and parsed descriptor retained");

            Case("probe rejection never invents a fetch return");
            foreach (uint code in new uint[] { 5, 122, 0 })
            {
                api = new FakeEtw(); api.ProbeCode = code; r = Core.ReadEtw(GuidText, api.Query);
                Check(r.State == "UNKNOWN" && !r.FetchAttempted && r.FetchRc == null && r.ReturnedSize == null, "unattempted fetch nullable");
                Check(api.FetchCalls == 0 && r.NotAttempted.Contains("fetch"), "no secondary query");
            }
            Case("zero and excessive allocation requests rejected");
            foreach (uint size in new uint[] { 0, 65537 })
            {
                api = new FakeEtw(); api.ProbeSize = size; r = Core.ReadEtw(GuidText, api.Query);
                Check(r.State == "UNKNOWN" && api.FetchCalls == 0 && r.Capacity == null, "size bound before allocation/fetch");
            }
            Case("fetch failure preserves actual stage status");
            api = new FakeEtw(); api.FetchCode = 5; r = Core.ReadEtw(GuidText, api.Query);
            Check(r.State == "UNKNOWN" && r.FetchAttempted && r.FetchRc == 5 && r.DescriptorBytes == null, "failed fetch does not publish SD");
            Case("any fetch size change is not retried");
            foreach (uint size in new uint[] { 0, 65536 })
            {
                api = new FakeEtw(); api.FetchSize = size; r = Core.ReadEtw(GuidText, api.Query);
                Check(r.State == "UNKNOWN" && r.ReturnedSize == size && api.FetchCalls == 1, "changed size receipt");
            }
            Case("unparseable descriptor retains UNKNOWN");
            api = new FakeEtw(); api.InvalidDescriptor = true; r = Core.ReadEtw(GuidText, api.Query);
            Check(r.State == "UNKNOWN" && r.Error != null && r.DescriptorBase64 == null, "no success after parse failure");
            Case("fetch exception preserves attempted and returned-size evidence");
            api = new FakeEtw(); api.FetchThrows = true; r = Core.ReadEtw(GuidText, api.Query);
            Check(r.State == "UNKNOWN" && r.FetchAttempted && r.FetchRc == null && r.ReturnedSize != null, "exception receipt");
        }

        sealed class FakeService : IServiceApi
        {
            internal int ManagerError, ServiceError;
            internal bool ThrowOpen, FailServiceClose;
            internal int ManagerCalls, ServiceCalls;
            internal readonly List<IntPtr> Closed = new List<IntPtr>();
            public IntPtr OpenManager(uint access, out int error)
            { ++ManagerCalls; Check(access == 1, "SC_MANAGER_CONNECT only"); error = ManagerError; return error == 0 ? new IntPtr(11) : IntPtr.Zero; }
            public IntPtr OpenService(IntPtr manager, string name, uint access, out int error)
            {
                ++ServiceCalls; Check(manager == new IntPtr(11) && access == 4, "SERVICE_QUERY_STATUS only");
                Check(String.Equals(name, Service, StringComparison.OrdinalIgnoreCase), "complete fixed name");
                error = ServiceError; if (ThrowOpen) throw new InvalidOperationException("synthetic OpenService exception");
                return error == 0 ? new IntPtr(22) : IntPtr.Zero;
            }
            public bool Close(IntPtr handle, out int error)
            {
                Check(handle == new IntPtr(11) || handle == new IntPtr(22), "only owned handles closed");
                Check(!Closed.Contains(handle), "exactly once close"); Closed.Add(handle);
                error = FailServiceClose && handle == new IntPtr(22) ? 6 : 0; return error == 0;
            }
        }

        static void ServiceCases()
        {
            Case("exact service success and reverse cleanup");
            FakeService api = new FakeService(); ServiceResult r = Core.ReadService(Service.ToLowerInvariant(), api);
            Check(r.State == "PRESENT" && api.Closed.Count == 2, "PRESENT from exact open");
            Check(api.Closed[0] == new IntPtr(22) && api.Closed[1] == new IntPtr(11), "service before SCM");
            Case("only service error 1060 is ABSENT");
            api = new FakeService(); api.ServiceError = 1060; r = Core.ReadService(Service, api);
            Check(r.State == "ABSENT" && api.Closed.Count == 1 && !r.ServiceClose.Attempted, "no fictitious service handle");
            Case("SCM error 1060 is still UNKNOWN");
            api = new FakeService(); api.ManagerError = 1060; r = Core.ReadService(Service, api);
            Check(r.State == "UNKNOWN" && !r.ServiceOpen.Attempted && r.ServiceOpen.Win32 == null && api.Closed.Count == 0, "stage-specific absence rule");
            Case("access failure is not absence");
            api = new FakeService(); api.ServiceError = 5; r = Core.ReadService(Service, api);
            Check(r.State == "UNKNOWN" && r.ServiceOpen.Win32 == 5 && api.Closed.Count == 1, "deny preserves UNKNOWN");
            Case("OpenService exception still closes owned manager");
            api = new FakeService(); api.ThrowOpen = true; r = Core.ReadService(Service, api);
            Check(r.State == "UNKNOWN" && r.ServiceOpen.Attempted && r.ServiceOpen.Win32 == null && api.Closed.Count == 1, "exception cleanup");
            Case("cleanup failure does not erase observed existence");
            api = new FakeService(); api.FailServiceClose = true; r = Core.ReadService(Service, api);
            Check(r.State == "PRESENT" && r.CleanupErrors.Count == 1 && api.Closed.Count == 2, "keep result and cleanup error");
            Case("prefix names cannot become a production object");
            api = new FakeService(); r = Core.ReadService(Service + "Extra", api);
            Check(r.State == "UNKNOWN" && api.ManagerCalls == 0, "reject before API");
        }

        sealed class FakeLsa : ILsaApi
        {
            internal uint OpenStatus = 0, QueryStatus = 0, FreeStatus = 0, CloseStatus = 0;
            internal bool OpenPoison, QueryPoison, Malformed, ExcessiveCount, ThrowConversion;
            internal string[] Names = new string[0];
            internal int OpenCalls, QueryCalls, FreeCalls, CloseCalls;
            IntPtr allocation = IntPtr.Zero;
            readonly List<IntPtr> strings = new List<IntPtr>();
            public uint OpenPolicy(uint access, out IntPtr policy)
            {
                ++OpenCalls; Check(access == 0x801, "fixed read-only policy access");
                policy = OpenStatus == 0 ? new IntPtr(11) : (OpenPoison ? new IntPtr(0xDEAD) : IntPtr.Zero);
                return OpenStatus;
            }
            public uint EnumerateRights(IntPtr policy, IntPtr sid, out IntPtr rights, out uint count)
            {
                ++QueryCalls; Check(policy == new IntPtr(11) && sid != IntPtr.Zero, "owned policy and serialized SID");
                if (QueryStatus != 0) { rights = QueryPoison ? new IntPtr(0xDEAD) : IntPtr.Zero; count = 9; return QueryStatus; }
                count = ExcessiveCount ? 257U : (uint)Names.Length;
                if (count == 0) { rights = IntPtr.Zero; return 0; }
                int stride = Marshal.SizeOf(typeof(LsaUnicodeString));
                allocation = Marshal.AllocHGlobal(ExcessiveCount ? 1 : stride * Names.Length); rights = allocation;
                if (!ExcessiveCount)
                    for (int i = 0; i < Names.Length; ++i)
                    {
                        IntPtr text = Marshal.StringToHGlobalUni(Names[i]); strings.Add(text);
                        LsaUnicodeString name = new LsaUnicodeString();
                        name.Length = (ushort)(Names[i].Length * 2); name.MaximumLength = (ushort)(name.Length + 2);
                        name.Buffer = text; if (Malformed) name.Length = 1;
                        Marshal.StructureToPtr(name, IntPtr.Add(allocation, stride * i), false);
                    }
                return 0;
            }
            public uint StatusToWin32(uint status)
            { if (ThrowConversion) throw new InvalidOperationException("synthetic conversion exception"); return status == 0 ? 0U : (status == Missing ? 2U : 5U); }
            public uint FreeRights(IntPtr rights)
            {
                ++FreeCalls; Check(FreeCalls == 1 && rights == allocation && rights != IntPtr.Zero, "only successful owned rights freed once");
                foreach (IntPtr text in strings) Marshal.FreeHGlobal(text); strings.Clear();
                Marshal.FreeHGlobal(allocation); allocation = IntPtr.Zero; return FreeStatus;
            }
            public uint ClosePolicy(IntPtr policy)
            { ++CloseCalls; Check(CloseCalls == 1 && policy == new IntPtr(11), "only successful owned policy closed once"); return CloseStatus; }
        }

        static void RightsCases()
        {
            Case("successful empty enumeration is direct only");
            FakeLsa api = new FakeLsa(); RightsResult r = Core.ReadRights(Sid, api);
            Check(r.State == "OBSERVED" && r.Rights.Length == 0 && r.DirectRightsEnumerated && !r.EffectiveRightsInferred, "empty direct enum scope");
            Check(r.Open.NtStatus == 0 && r.Query.NtStatus == 0 && r.Close.NtStatus == 0 && !r.Free.Attempted && r.Free.Win32 == null, "no default-zero fictitious free");
            Case("failed open poison output is not owned");
            api = new FakeLsa(); api.OpenStatus = Denied; api.OpenPoison = true; r = Core.ReadRights(Sid, api);
            Check(r.State == "UNKNOWN" && r.Open.NtStatus == Denied && r.Open.Win32 == 5 && api.CloseCalls == 0 && api.QueryCalls == 0, "raw status and no poison cleanup");
            Check(!r.Query.Attempted && r.Query.NtStatus == null && r.Query.Win32 == null, "not attempted differs from zero success");
            Case("missing direct rights remain not enumerated");
            api = new FakeLsa(); api.QueryStatus = Missing; api.QueryPoison = true; r = Core.ReadRights(Sid, api);
            Check(r.State == "NOT_FOUND_DIRECT_RIGHTS_NOT_ENUMERATED" && r.Rights == null && !r.DirectRightsEnumerated && !r.EffectiveRightsInferred, "Win32 2 is not empty grant");
            Check(r.Query.NtStatus == Missing && r.Query.Win32 == 2 && api.FreeCalls == 0 && api.CloseCalls == 1, "failed query poison not freed");
            Case("other failed enumeration remains UNKNOWN");
            api = new FakeLsa(); api.QueryStatus = Denied; r = Core.ReadRights(Sid, api);
            Check(r.State == "UNKNOWN" && r.Query.Win32 == 5 && api.FreeCalls == 0 && api.CloseCalls == 1, "failed query cleanup");
            Case("successful list retains exact names and cleanup");
            api = new FakeLsa(); api.Names = new string[] { "SeSystemProfilePrivilege", "SeChangeNotifyPrivilege" }; r = Core.ReadRights(Sid, api);
            Check(r.State == "OBSERVED" && r.Rights.Length == 2 && r.Rights[0] == api.Names[0] && api.FreeCalls == 1 && api.CloseCalls == 1, "successful owned result");
            Case("malformed successful list still has cleanup ownership");
            api = new FakeLsa(); api.Names = new string[] { "X" }; api.Malformed = true; r = Core.ReadRights(Sid, api);
            Check(r.State == "UNKNOWN" && r.Rights == null && api.FreeCalls == 1 && api.CloseCalls == 1, "parse failure cleanup");
            Case("excessive successful count is rejected before decoding");
            api = new FakeLsa(); api.ExcessiveCount = true; r = Core.ReadRights(Sid, api);
            Check(r.State == "UNKNOWN" && r.ReturnedCount == 257 && api.FreeCalls == 1 && api.CloseCalls == 1, "bounded list");
            Case("free failure preserves list and does not skip policy close");
            api = new FakeLsa(); api.Names = new string[] { "SeSystemProfilePrivilege" }; api.FreeStatus = Denied; r = Core.ReadRights(Sid, api);
            Check(r.State == "OBSERVED" && r.Rights.Length == 1 && r.CleanupErrors.Count == 1 && api.CloseCalls == 1 && r.Free.NtStatus == Denied, "cleanup error separately blocks");
            Case("status conversion exception cannot lose successful handle ownership");
            api = new FakeLsa(); api.ThrowConversion = true; r = Core.ReadRights(Sid, api);
            Check(r.State == "UNKNOWN" && r.Open.NtStatus == 0 && r.Open.Win32 == null && api.QueryCalls == 0 && api.CloseCalls == 1, "ownership established before conversion");
        }

        sealed class FakePower : IPowerRunner
        {
            internal bool Throws;
            internal PowerRunSnapshot Value = Success();
            internal static PowerRunSnapshot Success()
            {
                PowerRunSnapshot result = new PowerRunSnapshot { StartAttempted = true, Started = true, ExitObserved = true,
                    StopConfirmed = true, ExitCode = 0, ProcessId = 17, StdoutComplete = true,
                    StderrComplete = true };
                result.SetStdoutRaw(Encoding.UTF8.GetBytes("synthetic saved scheme/subgroup output"), 65001);
                result.SetStderrRaw(new byte[0], 65001); return result;
            }
            public PowerRunSnapshot Run(PowerCommand command)
            {
                Check(command.FileName == @"C:\Windows\System32\powercfg.exe" &&
                    command.Arguments == "/query SCHEME_CURRENT SUB_SLEEP", "fixed command has no caller options");
                Check(!command.UseShellExecute && command.CreateNoWindow &&
                    command.WorkingDirectory == @"C:\Windows\System32", "no shell/window");
                Check(command.TimeoutMilliseconds == 20000 && command.KillWaitMilliseconds == 2000 &&
                    command.StreamCharacterLimit == 65536 && command.StreamByteLimit == 131072, "fixed time and capture budgets");
                if (Throws) throw new InvalidOperationException("synthetic runner failure");
                return Value;
            }
        }

        static void PowerCases()
        {
            Case("explicit successful exit needs no LASTEXITCODE variable");
            FakePower runner = new FakePower(); PowerResult r = Core.ReadPower(runner);
            Check(r.State == "OBSERVED" && r.Run.ExitCode == 0 && r.CleanupErrors.Count == 0, "explicit process result");
            Check(r.Run.StdoutStrictDecode && r.Run.StdoutCodePage == 65001 &&
                r.Run.StdoutRawBase64 != null && r.Run.StdoutCapturedSha256.Length == 64, "raw and explicit strict decoder receipts");
            Case("nonzero exit remains UNKNOWN with captured output");
            runner = new FakePower(); runner.Value.ExitCode = 5;
            runner.Value.SetStderrRaw(Encoding.UTF8.GetBytes("synthetic failure"), 65001); r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN" && r.Run.Stdout.Length != 0 && r.Run.Stderr.Length != 0, "failure evidence retained");
            Case("timeout stays UNKNOWN even after confirmed owned-process stop");
            runner = new FakePower(); runner.Value.TimedOut = true; runner.Value.KillRequested = true;
            runner.Value.KillCallSucceeded = true; r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN" && r.CleanupErrors.Count == 0 && r.Run.StopConfirmed, "kill is not policy success");
            Case("unconfirmed termination is an explicit cleanup error");
            runner = new FakePower(); runner.Value.ExitObserved = false; runner.Value.ExitCode = null;
            runner.Value.StopConfirmed = false; runner.Value.TimedOut = true; runner.Value.KillRequested = true;
            runner.Value.ProcessRetained = true; r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN" && r.CleanupErrors.Count == 1 && r.Run.ProcessId == 17 && r.Run.ProcessRetained, "scene identity retained");
            Case("incomplete stream is not silently accepted");
            runner = new FakePower(); runner.Value.StderrComplete = false; r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN", "both EOF receipts required");
            Case("decoded character capture is bounded and rejected");
            runner = new FakePower(); runner.Value.SetStdoutRaw(Encoding.UTF8.GetBytes(new string('x', 65537)), 65001);
            runner.Value.SetStderrRaw(Encoding.UTF8.GetBytes(new string('y', 65537)), 65001);
            r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN" && r.Run.Stdout.Length == 65536 && r.Run.Stderr.Length == 65536 &&
                r.Run.StdoutTruncated && r.Run.StderrTruncated, "separate 64Ki character bounds");
            Case("raw stream limit retains only a digestible prefix");
            runner = new FakePower(); runner.Value.SetStdoutRaw(new byte[131073], 65001); r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN" && r.Run.StdoutRawTruncated && r.Run.StdoutCapturedBytes == 131072 &&
                Convert.FromBase64String(r.Run.StdoutRawBase64).Length == 131072, "raw prefix bound and preserved bytes");
            Case("invalid UTF-8 is not replaced with successful text");
            runner = new FakePower(); runner.Value.SetStdoutRaw(new byte[] { 0xc3, 0x28 }, 65001); r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN" && r.Run.StdoutStrictDecode && !r.Run.StdoutDecodeSucceeded &&
                r.Run.StdoutDecodeError != null && r.Run.StdoutRawBase64 == "wyg=", "invalid original bytes retained");
            Case("BOM records explicit decoder selection without changing raw evidence");
            runner = new FakePower(); runner.Value.SetStdoutRaw(new byte[] { 0xff, 0xfe, 0x41, 0 }, 65001); r = Core.ReadPower(runner);
            Check(r.State == "OBSERVED" && r.Run.Stdout == "A" && r.Run.StdoutCodePage == 1200 &&
                r.Run.StdoutRawBase64 == "//5BAA==", "BOM selection and exact raw bytes");
            Case("bounded raw collector drains a long line without retaining excess");
            BoundedByteCapture capture = new BoundedByteCapture(131072); byte[] data = new byte[131073];
            capture.Append(data, data.Length); capture.Append(data, data.Length);
            Check(capture.Snapshot().Length == 131072 && capture.Truncated &&
                capture.ObservedBytes == 262146, "bounded raw accumulator independent of lines");
            Case("runner exception remains an object result");
            runner = new FakePower(); runner.Throws = true; r = Core.ReadPower(runner);
            Check(r.State == "UNKNOWN" && r.Error != null, "one failure cannot throw away sibling results");
        }

        static void SummaryCase()
        {
            Case("summary retains not-enumerated and cleanup separately");
            FakeLsa missing = new FakeLsa(); missing.QueryStatus = Missing;
            FakeService close = new FakeService(); close.FailServiceClose = true;
            FactSummary summary = Core.Summarize(new FactResult[] {
                Core.ReadRights(Sid, missing), Core.ReadService(Service, close), null });
            Check(summary.Unknown.Count == 2 && summary.CleanupErrors.Count == 1 &&
                summary.NotAttempted.Count != 0 && !summary.ProductionReadinessProven &&
                summary.Admission == "BLOCKED", "no successful metadata implies readiness");
        }

        public static Report Run()
        {
            cases = assertions = 0;
            AbiCase(); EtwCases(); ServiceCases(); RightsCases(); PowerCases(); SummaryCase();
            return new Report { Cases = cases, Assertions = assertions, Passed = true };
        }
    }
}
'@
$combined=[Text.Encoding]::UTF8.GetString($bytes)+[Environment]::NewLine+$tests
Add-Type -TypeDefinition $combined -Language CSharp
$result=[P309ReadinessV6.SyntheticTests.Suite]::Run()
$h=[Security.Cryptography.SHA256]::Create()
try{$sourceDigest=[BitConverter]::ToString($h.ComputeHash($bytes)).Replace('-','').ToLowerInvariant()}finally{$h.Dispose()}
[ordered]@{scope='INJECTED_FACTS_CORE_REGRESSIONS_ONLY';source_sha256=$sourceDigest;result=$result;production_calls=0;uac=0;admission='BLOCKED';I1_I7='OPEN'}|ConvertTo-Json -Depth 7
