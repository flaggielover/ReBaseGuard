using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using Microsoft.Win32.SafeHandles;
using P309HostAnchorV10;

internal static class AnchorTests
{
    private static string runRoot; private static int passed; private static List<string> results = new List<string>();
    private static string H = new string('a', 64), G = new string('b', 32), Epoch = new string('c', 32);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)] private static extern bool CreateHardLinkW(string link, string target, IntPtr attributes);
    private static void Assert(bool ok, string message) { if (!ok) throw new Exception(message); }
    private static void Refuses(Action action, string message) { bool failed = false; try { action(); } catch (Exception) { failed = true; } Assert(failed, message); }
    private static void Case(string name, Action test) { test(); passed++; results.Add(name); Console.WriteLine("PASS " + name); }
    private static string Fixture(string name)
    {
        string root = Path.Combine(runRoot, name); if (Directory.Exists(root)) throw new Exception("Fresh fixture required"); Directory.CreateDirectory(root);
        string journal = Path.Combine(root, "anchor.journal"); string id;
        using (SafeFileHandle h = NativeFile.Open(journal, NativeFile.Read | NativeFile.Write, 0, NativeFile.CreateNew, false))
        { NativeFile.WriteAt(h, 0, new byte[4096]); NativeFile.Flush(h); id = NativeFile.Identity(NativeFile.Facts(h, false)); }
        string text = "schema=P309_HOST_ANCHOR_V10\nversion=3\nscope=DEVELOPMENT_IDLE_ONCE\nsource=" + H + "\nguest=" + H + "\nruntime=" + H + "\npolicy=" + H + "\nmonitor=" + H + "\npermit_id=" + new string('7',32) + "\nepoch=" + Epoch + "\nhost_epoch_seq=1\ncheckpoint=" + H + "\nguest_sequence=7\njournal_identity=" + id + "\ncore=" + H + "\ncontroller=" + H + "\nack_public=" + H + "\nack_key_identity=" + H + "\nguest_root_public_spki=" + new string('4',64) + "\napproval=" + new string('6',64) + "\n";
        byte[] enrollment = new UTF8Encoding(false, true).GetBytes(text); File.WriteAllBytes(Path.Combine(root, "test-enrollment.txt"), enrollment);
        JournalRecord first = new JournalRecord { Sequence = 0, State = "ENROLLED", Previous = JournalRecord.Zero, BindingHash = NativeFile.Hash(enrollment), Reason = "INSTALLER_FIXED_IDLE_ONCE" };
        using (SafeFileHandle h = NativeFile.Open(journal, NativeFile.Read | NativeFile.Write, 0, NativeFile.OpenExisting, false)) { NativeFile.WriteAt(h, 0, first.Encode()); NativeFile.Flush(h); }
        return root;
    }
    private sealed class FakeVm : IVerifiedVmLifetimeLease
    {
        public bool Drift; public string GenerationValue = G; public void Revalidate() { if (Drift) throw new IOException("Synthetic lifetime drift"); } public void Dispose() { }
        public string HostBoot { get { return new string('d', 32); } } public string GuestBoot { get { return new string('e', 32); } }
        public string Challenge { get { return H; } } public string GuestHash { get { return H; } } public string RuntimeHash { get { return H; } }
        public string PolicyHash { get { return H; } } public string PackageHash { get { return H; } } public string Generation { get { return GenerationValue; } }
        public long HostEpochSequence { get { return 1; } } public string WorkerInvocation { get { return new string('f', 32); } }
        public string BrokerInvocation { get { return new string('1', 32); } } public string BlockedProofSha256 { get { return new string('2', 64); } }
        public string VmLifetimeSha256 { get { return new string('3',64); } } public string GuestRootPublicSpkiSha256 { get { return new string('4',64); } }
        public string RootPrestartProofSha256 { get { return new string('5',64); } } public string ApprovalSha256 { get { return new string('6',64); } }
    }
    private static VerifiedVmReservation FakeReservation() { return VerifiedVmReservation.FromVerifiedLifetimeAuthority(new FakeVm()); }
    private static VerifiedVmBinding FakeBlocked() { return VerifiedVmBinding.FromVerifiedLifetimeAuthority(new FakeVm()); }
    private static RecordedReservation Reserve(HostAnchor a) { AnchorSnapshot s = a.Snapshot(); return a.ReserveOnce(s.Sequence, s.HeadSha256, s.Generation, FakeReservation()); }
    private static RecordedConsumption Consume(HostAnchor a) { RecordedReservation r = Reserve(a); r.RecordSyntheticReserveAckForTests(); return a.BindOnce(r, FakeBlocked()); }
    private static void CrashChild(string root)
    {
        using (HostAnchor a = HostAnchor.OpenFixture(root, null))
        {
            a.Fault = delegate(string point) { if (point == "after-journal-write-before-flush") Environment.Exit(73); };
            Consume(a);
        }
        Environment.Exit(74);
    }
    public static int Main(string[] args)
    {
        try
        {
            if (args.Length == 2 && args[0] == "--crash-fixture") { CrashChild(args[1]); return 74; }
            if (args.Length == 1 && args[0] == "--runner-overflow") { Console.Out.Write(new string('O',200000)); Console.Error.Write(new string('E',200000)); return 0; }
            if (args.Length == 1 && args[0] == "--runner-hang") { Thread.Sleep(10000); return 75; }
            if (args.Length != 1) throw new Exception("Pass a fresh self-owned test-runs directory; never production paths");
            runRoot = Path.GetFullPath(args[0]); if (Directory.Exists(runRoot)) throw new Exception("Test run directory already exists; preserve evidence and use an explicit fresh ordinary test run"); Directory.CreateDirectory(runRoot);
            Case("native-layout-and-production-api-separation", delegate {
                Assert(IntPtr.Size == 8, "x64 required"); Assert(Marshal.SizeOf(typeof(NativeFile.Info)) == 52, "BY_HANDLE_FILE_INFORMATION layout");
                MethodInfo m = typeof(HostAnchor).GetMethod("OpenInstalled"); Assert(m != null && m.GetParameters().Length == 1 && m.GetParameters()[0].ParameterType == typeof(VerifiedVmReservation), "No arbitrary production path");
                foreach (MethodInfo api in typeof(HostAnchor).GetMethods(BindingFlags.Public | BindingFlags.Static)) Assert(api.Name != "OpenFixture", "Fixture opener not public");
                Assembly production = Assembly.ReflectionOnlyLoadFrom(Path.Combine(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location), "P309HostAnchorV10.dll"));
                Assert(production.GetType("P309HostAnchorV10.HostAnchor").GetMethod("OpenFixture", BindingFlags.Static | BindingFlags.NonPublic) == null, "Production binary excludes fixture opener");
            });
            Case("native-create-new-no-overwrite", delegate {
                string p = Path.Combine(Fixture("new"), "new.bin"); using (SafeFileHandle h = NativeFile.Open(p, NativeFile.Write, 0, NativeFile.CreateNew, false)) { NativeFile.WriteAt(h, 0, new byte[] { 9 }); NativeFile.Flush(h); }
                Refuses(delegate { using (SafeFileHandle h = NativeFile.Open(p, NativeFile.Write, 0, NativeFile.CreateNew, false)) { } }, "CREATE_NEW must refuse existing"); Assert(File.ReadAllBytes(p)[0] == 9, "Existing bytes retained");
            });
            Case("single-consume-same-handle-publish-stop-invalidates", delegate {
                string root = Fixture("consume"); using (HostAnchor a = HostAnchor.OpenFixture(root, null)) {
                    AnchorSnapshot before = a.Snapshot(); Assert(before.State == "SESSION_CLAIMED" && before.Sequence == 1 && !before.ProductionFactoryVerifiedAtOpen, "Fixture is not production");
                    RecordedConsumption receipt = Consume(a); Assert(receipt.IsCurrentAtRead, "One current receipt"); Assert(File.Exists(Path.Combine(root, "consume-receipt.bin")) && !File.Exists(Path.Combine(root, "consume-receipt.pending")), "No-replace native publish");
                    Refuses(delegate { Consume(a); }, "No second consume"); a.RequestStop(); Assert(!receipt.IsCurrentAtRead, "Stop invalidates old receipt"); a.PersistStopRequest(); AnchorSnapshot stopped = a.Snapshot(); Assert(stopped.State == "STOP_REQUESTED", "Not STOPPED/cleanup proven"); a.PersistStopRequest(); Assert(a.Snapshot().Sequence == stopped.Sequence, "Idempotent terminal stop record"); }
                Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "Restart never re-arms");
            });
            Case("exclusive-writer-and-directory-identity-pinned", delegate {
                string root = Fixture("exclusive"); using (HostAnchor a = HostAnchor.OpenFixture(root, null)) {
                    Refuses(delegate { using (SafeFileHandle h = NativeFile.Open(Path.Combine(root, "anchor.journal"), NativeFile.Read, NativeFile.ShareRead, NativeFile.OpenExisting, false)) { } }, "share0 blocks second reader/writer");
                    Refuses(delegate { Directory.Move(root, root + "-replacement"); }, "No-share-delete ancestor prevents rename"); }
            });
            Case("cas-race-has-one-winner", delegate {
                string root = Fixture("cas"); using (HostAnchor a = HostAnchor.OpenFixture(root, null)) {
                    AnchorSnapshot s = a.Snapshot(); int win = 0, refuse = 0; Exception unexpected = null;
                    ThreadStart work = delegate { try { a.ReserveOnce(s.Sequence, s.HeadSha256, s.Generation, FakeReservation()); Interlocked.Increment(ref win); } catch (InvalidOperationException) { Interlocked.Increment(ref refuse); } catch (Exception e) { unexpected = e; } };
                    Thread x = new Thread(work), y = new Thread(work); x.Start(); y.Start(); Assert(x.Join(5000) && y.Join(5000), "CAS workers finish"); Assert(unexpected == null && win == 1 && refuse == 1, "Exactly one CAS winner"); }
            });
            Case("wrong-cas-and-generation-cannot-select-authority", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("stale"), null)) { AnchorSnapshot s = a.Snapshot();
                    Refuses(delegate { a.ReserveOnce(s.Sequence, new string('0', 64), s.Generation, FakeReservation()); }, "Wrong head refused");
                    Refuses(delegate { a.ReserveOnce(s.Sequence, s.HeadSha256, new string('d', 32), FakeReservation()); }, "Wrong G refused");
                    Assert(a.Snapshot().Sequence == 1, "CAS refusal did not append/rearm"); Assert(Consume(a).IsCurrentAtRead, "Fixed enrolled generation still sole choice"); }
            });
            Case("stop-before-consume-does-not-write-intent", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("stop-first"), null)) { a.RequestStop(); Refuses(delegate { Consume(a); }, "Stop wins before consume"); Assert(a.Snapshot().Sequence == 1, "No consume record"); a.PersistStopRequest(); Assert(a.Snapshot().State == "STOP_REQUESTED", "Fixed stop only"); }
            });
            Case("blocked-writer-does-not-block-stop-or-return-live-ack", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("blocked-stop"), null)) {
                    ManualResetEvent entered = new ManualResetEvent(false), release = new ManualResetEvent(false); Exception error = null; RecordedConsumption receipt = null;
                    a.Fault = delegate(string point) { if (point == "after-journal-write-before-flush") { entered.Set(); if (!release.WaitOne(5000)) throw new Exception("Test barrier timeout"); } };
                    Thread consume = new Thread(delegate() { try { receipt = Consume(a); } catch (Exception e) { error = e; } }); consume.Start(); Assert(entered.WaitOne(5000), "Writer reached blocked I/O boundary");
                    Thread stop = new Thread(delegate() { a.RequestStop(); }); stop.Start(); bool stopFinished = stop.Join(1000); bool writerStillBlocked = consume.IsAlive; release.Set(); Assert(consume.Join(5000), "Consume returns after release");
                    Assert(stopFinished && writerStillBlocked, "Latch is independent of storage lock"); Assert(receipt == null && error is RecoveryUnknownException && a.Snapshot().StopLatched && a.Snapshot().State == "RECOVERY_UNKNOWN", "Late flush never creates live ACK"); entered.Dispose(); release.Dispose(); }
            });
            Case("failure-after-flush-keeps-consumption-and-refuses-restart", delegate {
                string root = Fixture("after-flush"); using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { a.Fault = delegate(string p) { if (p == "after-journal-flush") throw new IOException("Synthetic API-boundary crash"); }; Refuses(delegate { Consume(a); }, "Flush-boundary failure refused"); Assert(a.Snapshot().StopLatched, "Failure latches"); }
                Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "Consumed bytes cannot be resumed");
            });
            Case("abrupt-owned-child-exit-does-not-reopen-epoch", delegate {
                string root = Fixture("crash"); ProcessStartInfo si = new ProcessStartInfo(Assembly.GetExecutingAssembly().Location, "--crash-fixture \"" + root + "\""); si.UseShellExecute = false; si.CreateNoWindow = true;
                using (Process p = Process.Start(si)) { try { Assert(p.WaitForExit(10000), "Owned crash child bounded"); Assert(p.ExitCode == 73, "Abrupt child reached write boundary"); } finally { if (!p.HasExited) { p.Kill(); if (!p.WaitForExit(2000)) throw new Exception("Owned child stop cannot be proven; preserve process/fixture and fail"); } } }
                Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "Kernel-released handles do not renew enrollment");
            });
            Case("partial-and-record-aligned-truncation-refused", delegate {
                foreach (int length in new int[] { 0, 511, 512, 1024, 4095 }) { string root = Fixture("truncated-" + length); using (FileStream f = new FileStream(Path.Combine(root, "anchor.journal"), FileMode.Open, FileAccess.Write, FileShare.None)) { f.SetLength(length); f.Flush(true); } Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "Every truncation including whole-record tail refused"); }
            });
            Case("corruption-binding-drift-gap-and-illegal-transition-refused", delegate {
                string corrupt = Fixture("corrupt"); byte[] b = File.ReadAllBytes(Path.Combine(corrupt, "anchor.journal")); b[42] ^= 1; File.WriteAllBytes(Path.Combine(corrupt, "anchor.journal"), b); Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(corrupt, null)) { } }, "Checksum rejects corruption");
                string drift = Fixture("binding-drift"), ep = Path.Combine(drift, "test-enrollment.txt"); File.WriteAllText(ep, File.ReadAllText(ep).Replace("runtime=" + H, "runtime=" + new string('d', 64)), new UTF8Encoding(false)); Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(drift, null)) { } }, "Enrollment drift not adopted");
                string gap = Fixture("gap"); b = File.ReadAllBytes(Path.Combine(gap, "anchor.journal")); b[1024] = 1; File.WriteAllBytes(Path.Combine(gap, "anchor.journal"), b); Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(gap, null)) { } }, "Gap cannot hide a record");
                string bad = Fixture("bad-state"); string badEnrollmentHash = NativeFile.Hash(File.ReadAllBytes(Path.Combine(bad, "test-enrollment.txt"))); JournalRecord illegal = new JournalRecord { Sequence = 0, State = "STOPPED", Previous = JournalRecord.Zero, BindingHash = badEnrollmentHash, Reason = "INSTALLER_FIXED_IDLE_ONCE" }; b = File.ReadAllBytes(Path.Combine(bad, "anchor.journal")); Buffer.BlockCopy(illegal.Encode(), 0, b, 0, 512); File.WriteAllBytes(Path.Combine(bad, "anchor.journal"), b); Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(bad, null)) { } }, "Valid hash does not legalize invalid state");
            });
            Case("same-name-replacement-and-missing-file-refused", delegate {
                string root = Fixture("replacement"), journal = Path.Combine(root, "anchor.journal"); byte[] b = File.ReadAllBytes(journal); File.Move(journal, journal + ".retained"); File.WriteAllBytes(journal, b); Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "Same bytes different fileID refused");
                string missing = Fixture("missing"); File.Move(Path.Combine(missing, "anchor.journal"), Path.Combine(missing, "retained.journal")); Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(missing, null)) { } }, "Missing journal never initialized"); Assert(!File.Exists(Path.Combine(missing, "anchor.journal")), "No implicit enroll");
            });
            Case("journal-hard-link-custody-rejected", delegate {
                string root = Fixture("hardlink"), journal = Path.Combine(root, "anchor.journal");
                Assert(CreateHardLinkW(Path.Combine(root, "second-name.journal"), journal, IntPtr.Zero), "Owned NTFS hard link created");
                Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "Multiple names refuse custody even though content/fileID matches");
            });
            Case("receipt-collision-never-overwrites-or-renews", delegate {
                foreach (string leaf in new string[] { "consume-receipt.pending", "consume-receipt.bin" }) { string root = Fixture("collision-" + leaf); File.WriteAllBytes(Path.Combine(root, leaf), new byte[] { 31 }); using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { Refuses(delegate { Consume(a); }, "Receipt collision refuses after fence"); Assert(a.Snapshot().StopLatched, "Collision latches"); } Assert(File.ReadAllBytes(Path.Combine(root, leaf))[0] == 31, "Pre-existing destination retained"); Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "No retry after collision"); }
            });
            Case("guest-rollback-comparison-never-advances-host", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("guest-rollback"), null)) { Assert(a.CompareGuestCheckpoint(G, 7, H), "Exact comparison"); Assert(!a.CompareGuestCheckpoint(G, 6, H), "Rolled-back guest sequence denied"); Assert(a.Snapshot().Sequence == 1 && a.Snapshot().StopLatched, "Guest value never updates host state"); Refuses(delegate { Consume(a); }, "Rollback does not reopen permit"); }
            });
            Case("cold-start-claim-alone-and-terminal-unknown-refuse-restart", delegate {
                string root = Fixture("claim-only"); using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { }
                Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(root, null)) { } }, "Even no-consume restart needs separate reconcile");
                string unknown = Fixture("unknown"); using (HostAnchor a = HostAnchor.OpenFixture(unknown, null)) { a.MarkRecoveryUnknown(); AnchorSnapshot s = a.Snapshot(); a.MarkRecoveryUnknown(); Assert(a.Snapshot().Sequence == s.Sequence && s.State == "RECOVERY_UNKNOWN", "Unknown terminal and idempotent"); Refuses(delegate { Consume(a); }, "Unknown cannot rearm"); }
                Refuses(delegate { using (HostAnchor a = HostAnchor.OpenFixture(unknown, null)) { } }, "Unknown retained across restart");
            });
            Case("stop-followed-by-uncertainty-upgrades-and-failed-write-stays-unknown", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("stop-unknown"), null)) { a.PersistStopRequest(); a.MarkRecoveryUnknown(); Assert(a.Snapshot().State == "RECOVERY_UNKNOWN" && a.Snapshot().PersistedState == "RECOVERY_UNKNOWN", "Stop must not swallow later uncertainty"); }
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("stop-unknown-write-fail"), null)) { a.PersistStopRequest(); a.Fault = delegate(string point) { if (point == "before-journal-write") throw new IOException("Synthetic write failure"); }; Refuses(delegate { a.MarkRecoveryUnknown(); }, "Unknown persistence failure surfaced"); Assert(a.Snapshot().State == "RECOVERY_UNKNOWN" && a.Snapshot().PersistedState == "STOP_REQUESTED", "Memory/persisted state stay distinct"); }
            });
            Case("two-record-one-permit-and-purpose-canonical-ack", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("two-phase"), null)) {
                    RecordedReservation reserve = Reserve(a); Assert(reserve.Sequence == 2 && reserve.IsCurrentAtRead && a.Snapshot().PersistedState == "RESERVED", "Reserve is sole pre-start fence");
                    string wire = Encoding.UTF8.GetString(AckCanonical.EncodeReservation(reserve)); Assert(wire.StartsWith("protocol=P309_HOST_ANCHOR_RESERVE_ACK/1\nscope=DEV_FIXED_IDLE_ONLY\nG=" + G + "\n", StringComparison.Ordinal) && wire.IndexOf("workerInv=", StringComparison.Ordinal) < 0 && wire.EndsWith("checkpoint=" + H + "\n", StringComparison.Ordinal) && wire.IndexOf('\r') < 0, "Reserve purpose and canonical delimiters");
                    reserve.ClaimAckAttempt(); Refuses(delegate { reserve.ClaimAckAttempt(); }, "Reserve signing one attempt only");
                    string context = Encoding.UTF8.GetString(AckCanonical.EncodeSessionContext(reserve)); Assert(context.StartsWith("protocol=P309_HOST_VM_SESSION/1\n",StringComparison.Ordinal) && context.Contains("vm_lifetime_sha256=" + new string('3',64) + "\nguest_root_public_spki_sha256=" + new string('4',64) + "\nack_public_spki_sha256=" + H + "\n"), "Separate signed context binds VM lifetime and independently enrolled pins");
                    reserve.ClaimContextAttempt(); Refuses(delegate { reserve.ClaimContextAttempt(); }, "One context signing attempt; no general signing API");
                    reserve.RecordSyntheticReserveAckForTests(); RecordedConsumption final = a.BindOnce(reserve, FakeBlocked()); Assert(final.Sequence == 3 && final.IsCurrentAtRead && !reserve.IsCurrentAtRead, "Same permit progresses once, reserve ACK retired");
                    wire = Encoding.UTF8.GetString(AckCanonical.Encode(final)); Assert(wire.StartsWith("protocol=P309_HOST_ANCHOR_ACK/1\n", StringComparison.Ordinal) && wire.Contains("workerInv=" + new string('f',32) + "\nbrokerInv=" + new string('1',32) + "\nchallenge=" + H + "\nblocked_proof_sha256=" + new string('2',64) + "\n"), "Final ACK binds verified blocked invocation and challenge");
                    final.ClaimAckAttempt(); Refuses(delegate { final.ClaimAckAttempt(); }, "Final signing one attempt only"); Refuses(delegate { a.BindOnce(reserve, FakeBlocked()); }, "No second bind or new permit");
                    a.RequestStop(); Refuses(delegate { a.RevalidateAck(final); }, "No late ACK after stop"); }
            });
            Case("bind-without-signed-reserve-ack-is-refused", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("no-reserve-ack"), null)) { RecordedReservation r = Reserve(a); Refuses(delegate { a.BindOnce(r,FakeBlocked()); }, "Cannot bind before reserve ACK was produced"); Assert(a.Snapshot().State == "RECOVERY_UNKNOWN" && a.Snapshot().PersistedState == "RESERVED", "Missing signed reserve acknowledgement not ready"); }
            });
            Case("blocked-bind-writer-stop-prevents-final-record-ack", delegate {
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("blocked-bind"), null)) {
                    RecordedReservation r = Reserve(a); r.RecordSyntheticReserveAckForTests(); ManualResetEvent entered = new ManualResetEvent(false), release = new ManualResetEvent(false); RecordedConsumption result = null; Exception error = null;
                    a.Fault = delegate(string p) { if(p == "after-journal-write-before-flush") { entered.Set(); if(!release.WaitOne(5000)) throw new Exception("Barrier timeout"); } };
                    Thread worker = new Thread(delegate(){try{result = a.BindOnce(r,FakeBlocked());}catch(Exception e){error=e;}}); worker.Start(); Assert(entered.WaitOne(5000), "Bind blocked");
                    Thread stop = new Thread(delegate(){a.RequestStop();});stop.Start(); bool fast=stop.Join(1000);release.Set();Assert(worker.Join(5000),"Bind worker completed");Assert(fast && result==null && error is RecoveryUnknownException && a.Snapshot().StopLatched,"No late bind ACK");entered.Dispose();release.Dispose(); }
            });
            Case("vm-authority-drift-and-missing-factory-never-green", delegate {
                Assert(typeof(VerifiedVmReservation).GetConstructors().Length == 0 && typeof(VerifiedVmBinding).GetConstructors().Length == 0, "No public authoritative DTO constructor");
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("missing-authority"), null)) { AnchorSnapshot s = a.Snapshot(); Refuses(delegate { a.ReserveOnce(s.Sequence,s.HeadSha256,s.Generation,null); }, "Missing VM authority refused"); Assert(a.Snapshot().StopLatched && a.Snapshot().State == "RECOVERY_UNKNOWN", "Missing authority not ready"); }
                using (HostAnchor a = HostAnchor.OpenFixture(Fixture("drift-authority"), null)) { RecordedReservation r = Reserve(a); r.RecordSyntheticReserveAckForTests(); FakeVm fake = new FakeVm(); VerifiedVmBinding vm = VerifiedVmBinding.FromVerifiedLifetimeAuthority(fake); fake.Drift = true; Refuses(delegate { a.BindOnce(r,vm); }, "Drifted held identity refused"); Assert(a.Snapshot().StopLatched && a.Snapshot().PersistedState == "RESERVED", "No fake binding written"); }
                byte[] der = AckCanonical.Spki(new System.Security.Cryptography.RSAParameters { Modulus = new byte[] { 0x80, 1 }, Exponent = new byte[] { 1, 0, 1 } });
                Assert(NativeFile.Hex(der) == "301e300d06092a864886f70d0101010500030d00300a02030080010203010001", "Standard SPKI DER structure; pure synthetic public integers, no key created");
            });
            Case("broker-created-generation-first-claim-is-fixed-not-rebound", delegate {
                string root = Fixture("new-G"); byte[] enrollment = File.ReadAllBytes(Path.Combine(root,"test-enrollment.txt")); Assert(Encoding.UTF8.GetString(enrollment).IndexOf("\nG=",StringComparison.Ordinal)<0,"Installer fixes permit, not actual broker G");
                using(HostAnchor a=HostAnchor.OpenFixture(root,null)){Assert(a.Snapshot().Generation==G,"First verified broker G captured");}
                FakeVm next=new FakeVm();next.GenerationValue=new string('9',32);VerifiedVmReservation vm=VerifiedVmReservation.FromVerifiedLifetimeAuthority(next);
                Refuses(delegate{using(HostAnchor a=HostAnchor.OpenFixture(root,null,vm)){}},"New authenticated G still cannot rebind spent/cold journal");
            });
            Case("owned-process-runner-drains-bounded-streams-and-stops-timeout", delegate {
                string exe=Assembly.GetExecutingAssembly().Location;
                P309BuildToolRunnerV10.Result large=P309BuildToolRunnerV10.Run(exe,"--runner-overflow",runRoot,5000);
                Assert(large.Exited&&large.ExitCode==0&&large.Unknown&&large.Stdout.Complete&&large.Stderr.Complete&&large.Stdout.Truncated&&large.Stderr.Truncated&&large.Stdout.Bytes.Length==131072&&large.Stderr.Bytes.Length==131072&&large.Stdout.TotalBytes==200000&&large.Stderr.TotalBytes==200000,"Both raw streams bounded and fully drained; truncation UNKNOWN");
                P309BuildToolRunnerV10.Result timeout=P309BuildToolRunnerV10.Run(exe,"--runner-hang",runRoot,100);
                Assert(timeout.TimedOut&&timeout.KillRequested&&timeout.Exited&&timeout.ExitCode.HasValue&&timeout.Stdout.Complete&&timeout.Stderr.Complete,"Only owned timeout child stopped and bounded EOF recorded");
            });
            Console.WriteLine("RESULT PASS cases=" + passed + " scope=OWNED_TEMP_FILES_ONLY production_factory_calls=0 production_host_queries=0 UAC=0 services_changed=0 keys_created=0 VM=0 trace=0 formal_grant=0");
            File.WriteAllLines(Path.Combine(runRoot, "PASSED_CASES.txt"), results.ToArray()); return 0;
        }
        catch (Exception e) { Console.Error.WriteLine(e.ToString()); Console.Error.WriteLine("RESULT FAIL; preserve owned fixture directory; no production state was created"); return 1; }
    }
}
