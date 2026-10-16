using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;
using Microsoft.Win32.SafeHandles;

namespace P309HostAnchorV10
{
    public sealed class RecoveryUnknownException : IOException
    {
        public string State { get { return "RECOVERY_UNKNOWN"; } }
        internal RecoveryUnknownException(string message, Exception inner) : base(message, inner) { }
    }
    public sealed class AnchorSnapshot
    {
        public readonly long Sequence; public readonly string HeadSha256, State, Generation, Epoch, BindingSha256;
        public readonly bool StopLatched, ProductionFactoryVerifiedAtOpen; public readonly string PersistedState;
        internal AnchorSnapshot(long seq, string head, string state, string persisted, Binding binding, bool stop, bool production)
        { Sequence = seq; HeadSha256 = head; State = state; PersistedState = persisted; Generation = binding.G; Epoch = binding.Epoch; BindingSha256 = binding.Hash; StopLatched = stop; ProductionFactoryVerifiedAtOpen = production; }
    }
    internal sealed class Binding
    {
        internal string Hash, EnrollmentHash, G, PermitId, Epoch, Checkpoint, JournalIdentity, CoreHash, ControllerHash, Source, Guest, Runtime, Policy, HostBoot, AckPublic, AckKeyIdentity, GuestRootPublic, Approval;
        internal long GuestSequence, HostEpochSequence; internal byte[] Bytes;
        internal static readonly string[] Keys = { "schema", "version", "scope", "source", "guest", "runtime", "policy", "monitor", "permit_id", "epoch", "host_epoch_seq", "checkpoint", "guest_sequence", "journal_identity", "core", "controller", "ack_public", "ack_key_identity", "guest_root_public_spki", "approval" };
        internal static Binding Parse(byte[] bytes, VerifiedVmReservation vm)
        {
            if (bytes.Length == 0 || bytes.Length > 4096) throw new IOException("Enrollment length bound");
            string s = new UTF8Encoding(false, true).GetString(bytes); string[] lines = s.Split('\n');
            if (lines.Length != Keys.Length + 1 || lines[lines.Length - 1] != "" || s.IndexOf('\r') >= 0) throw new IOException("Canonical enrollment required");
            Dictionary<string, string> v = new Dictionary<string, string>(StringComparer.Ordinal);
            for (int i = 0; i < Keys.Length; i++) { string prefix = Keys[i] + "="; if (!lines[i].StartsWith(prefix, StringComparison.Ordinal)) throw new IOException("Enrollment key/order mismatch"); v.Add(Keys[i], lines[i].Substring(prefix.Length)); }
            if (v["schema"] != "P309_HOST_ANCHOR_V10" || v["version"] != "3" || v["scope"] != "DEVELOPMENT_IDLE_ONCE") throw new IOException("Not the fixed development schema");
            foreach (string key in new string[] { "source", "guest", "runtime", "policy", "monitor", "checkpoint", "core", "controller", "ack_public", "ack_key_identity", "guest_root_public_spki", "approval" }) Hex(v[key], 64);
            Hex(v["permit_id"], 32); Hex(v["epoch"], 32); if (vm == null) throw new IOException("Verified pre-start VM authority required before opening anchor");
            string ji = v["journal_identity"]; if (ji.Length != 25 || ji[8] != ':') throw new IOException("Journal identity format"); Hex(ji.Substring(0, 8), 8); Hex(ji.Substring(9), 16);
            long seq; if (!Int64.TryParse(v["guest_sequence"], NumberStyles.None, CultureInfo.InvariantCulture, out seq) || seq < 0 || seq.ToString(CultureInfo.InvariantCulture) != v["guest_sequence"]) throw new IOException("Guest sequence format");
            long epochSeq; if (!Int64.TryParse(v["host_epoch_seq"], NumberStyles.None, CultureInfo.InvariantCulture, out epochSeq) || epochSeq <= 0 || epochSeq.ToString(CultureInfo.InvariantCulture) != v["host_epoch_seq"]) throw new IOException("Host epoch sequence format");
            string enrollmentHash = NativeFile.Hash(bytes);
            byte[] bound = Encoding.ASCII.GetBytes("P309_HOST_ANCHOR_BINDING/3\nenrollment_sha256=" + enrollmentHash + "\nG=" + vm.Generation + "\nprestart_proof_sha256=" + vm.RootPrestartProofSha256 + "\nhost_boot=" + vm.HostBoot + "\nguest_boot=" + vm.GuestBoot + "\nchallenge=" + vm.Challenge + "\nvm_lifetime_sha256=" + vm.VmLifetimeSha256 + "\n");
            Binding result = new Binding { Bytes = bytes, Hash = NativeFile.Hash(bound), EnrollmentHash = enrollmentHash, G = vm.Generation, PermitId = v["permit_id"], Epoch = v["epoch"], Checkpoint = v["checkpoint"], GuestSequence = seq, JournalIdentity = ji, CoreHash = v["core"], ControllerHash = v["controller"], Source = v["source"], Guest = v["guest"], Runtime = v["runtime"], Policy = v["policy"], HostBoot = vm.HostBoot, HostEpochSequence = epochSeq, AckPublic = v["ack_public"], AckKeyIdentity = v["ack_key_identity"], GuestRootPublic = v["guest_root_public_spki"], Approval = v["approval"] };
            vm.Revalidate(result); return result;
        }
        private static void Hex(string x, int length) { if (x.Length != length) throw new IOException("Binding hex length"); foreach (char c in x) if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f')) throw new IOException("Binding hex syntax"); }
    }
    internal sealed class JournalRecord
    {
        internal const int Size = 512, Payload = 480; internal long Sequence; internal string State, Previous, BindingHash, Reason, Hash; internal string EvidenceHash = new string('0', 64);
        internal static string Zero = new string('0', 64);
        internal byte[] Encode()
        {
            string text = "P309HA10|2|" + Sequence.ToString(CultureInfo.InvariantCulture) + "|" + State + "|" + Previous + "|" + BindingHash + "|" + Reason + "|" + EvidenceHash + "\n";
            byte[] p = Encoding.ASCII.GetBytes(text); if (p.Length > Payload) throw new IOException("Record overflow"); byte[] b = new byte[Size]; Buffer.BlockCopy(p, 0, b, 0, p.Length);
            byte[] content = new byte[Payload]; Buffer.BlockCopy(b, 0, content, 0, Payload); string hash = NativeFile.Hash(content); byte[] h = new byte[32]; for (int i = 0; i < 32; i++) h[i] = Byte.Parse(hash.Substring(i * 2, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
            Buffer.BlockCopy(h, 0, b, Payload, 32); Hash = hash; return b;
        }
        internal static JournalRecord Decode(byte[] b)
        {
            if (b.Length != Size) throw new IOException("Partial record"); byte[] payload = new byte[Payload], stored = new byte[32]; Buffer.BlockCopy(b, 0, payload, 0, Payload); Buffer.BlockCopy(b, Payload, stored, 0, 32);
            if (NativeFile.Hash(payload) != NativeFile.Hex(stored)) throw new IOException("Journal digest mismatch");
            int end = Array.IndexOf(payload, (byte)10); if (end < 0) throw new IOException("No canonical record terminator");
            for (int i = end + 1; i < Payload; i++) if (payload[i] != 0) throw new IOException("Nonzero record padding");
            for (int i = 0; i < end; i++) if (payload[i] < 32 || payload[i] > 126) throw new IOException("Non-ASCII record");
            string[] p = Encoding.ASCII.GetString(payload, 0, end).Split('|'); long seq;
            if (p.Length != 8 || p[0] != "P309HA10" || p[1] != "2" || !Int64.TryParse(p[2], NumberStyles.None, CultureInfo.InvariantCulture, out seq) || seq.ToString(CultureInfo.InvariantCulture) != p[2]) throw new IOException("Journal schema/sequence");
            AckCanonical.Hex(p[7], 64); return new JournalRecord { Sequence = seq, State = p[3], Previous = p[4], BindingHash = p[5], Reason = p[6], EvidenceHash = p[7], Hash = NativeFile.Hex(stored) };
        }
    }
    public sealed class HostAnchor : IDisposable
    {
        public const string InstalledRoot = "C:\\ProgramData\\ReBaseGuardP309\\Controller\\HostAnchor\\v10";
        public const string InstalledEnrollment = "C:\\Program Files\\ReBaseGuardP309\\Controller\\anchor-enrollment.v10.txt";
        public const string InstalledCore = "C:\\Program Files\\ReBaseGuardP309\\Controller\\P309HostAnchorV10.dll";
        private readonly object writer = new object(); private readonly List<SafeFileHandle> held = new List<SafeFileHandle>();
        private readonly string root; private readonly Binding binding; private readonly IIdentityLease identity; private readonly VerifiedVmReservation initialVm; private SafeFileHandle journal;
        private JournalRecord head; private int gate, disposed; private string memoryState;
        // gate: 0=unreserved, 2=reserve ACK linearized, 3=bind ACK linearized, 1=irreversible stop.
#if P309_TESTS
        internal Action<string> Fault;
        internal void Hit(string point) { if (Fault != null) Fault(point); }
#else
        private void Hit(string point) { }
#endif
        private HostAnchor(string fixedRoot, Binding b, IIdentityLease lease, VerifiedVmReservation vm) { root = fixedRoot; binding = b; identity = lease; initialVm = vm; }
        public static HostAnchor OpenInstalled(VerifiedVmReservation vm)
        {
            ServiceIdentityLease lease = null; HostAnchor anchor = null; List<SafeFileHandle> temporary = new List<SafeFileHandle>();
            try
            {
                if (vm == null) throw new ArgumentNullException("vm"); lease = ServiceIdentityLease.Create();
                temporary.AddRange(NativeFile.PinDirectories(Path.GetDirectoryName(InstalledEnrollment), true, "NO_SERVICE_WRITE_ALLOWED"));
                SafeFileHandle enrollment = NativeFile.Open(InstalledEnrollment, NativeFile.Read, NativeFile.ShareRead, NativeFile.OpenExisting, false); temporary.Add(enrollment);
                NativeFile.Custody(enrollment, "NO_SERVICE_WRITE_ALLOWED", true, true, true); Binding b = Binding.Parse(NativeFile.ReadAll(enrollment, 4096), vm);
                if (!String.Equals(Assembly.GetExecutingAssembly().Location, InstalledCore, StringComparison.OrdinalIgnoreCase)) throw new IOException("Only the fixed installed library may open a production anchor");
                foreach (string path in new string[] { InstalledCore, ServiceIdentityLease.Image })
                {
                    SafeFileHandle image = NativeFile.Open(path, NativeFile.Read, NativeFile.ShareRead, NativeFile.OpenExisting, false); temporary.Add(image); NativeFile.Custody(image, "NO_SERVICE_WRITE_ALLOWED", true, false, true);
                    string expected = path == InstalledCore ? b.CoreHash : b.ControllerHash;
                    if (NativeFile.HashHeld(image, 32 * 1024 * 1024) != expected) throw new IOException("Installed code binding mismatch");
                }
                anchor = new HostAnchor(InstalledRoot, b, lease, vm); lease = null; anchor.held.AddRange(temporary); temporary.Clear(); anchor.OpenAndClaim(); return anchor;
            }
            catch (Exception e) { if (anchor != null) anchor.Dispose(); if (lease != null) lease.Dispose(); foreach (SafeFileHandle h in temporary) h.Dispose(); throw new RecoveryUnknownException("Production anchor refused; preserve installation/epoch and stop independently", e); }
        }
        private void OpenAndClaim()
        {
            held.AddRange(NativeFile.PinDirectories(root, identity.Production, ServiceIdentityLease.Sid));
            journal = NativeFile.Open(Path.Combine(root, "anchor.journal"), NativeFile.Read | NativeFile.Write, 0, NativeFile.OpenExisting, false);
            NativeFile.Info info = NativeFile.Facts(journal, false); NativeFile.Ntfs(journal);
            if (identity.Production) NativeFile.Custody(journal, ServiceIdentityLease.Sid, true, true, false);
            if (NativeFile.Identity(info) != binding.JournalIdentity) throw new IOException("Installer-registered journal file identity changed");
            identity.Revalidate(); head = ReadChain(); memoryState = head.State;
            // No missing-file initialization, continuation, even historical terminal restart, or session adoption.
            if (head.Sequence != 0 || head.State != "ENROLLED") throw new IOException("Already claimed/prior epoch: RECOVERY_UNKNOWN; administrative reconciliation is separate");
            Append("SESSION_CLAIMED", "FIXED_CONTROLLER_BOOT", NativeFile.Hash(initialVm.CanonicalBinding()));
        }
        private JournalRecord ReadChain()
        {
            byte[] all = NativeFile.ReadAll(journal, JournalRecord.Size * 8);
            // Installer writes the whole fixed 4096-byte allocation. Runtime never truncates/extends it.
            // Logical append uses previously zero slots; even record-aligned physical truncation is rejected.
            if (all.Length != JournalRecord.Size * 8) throw new IOException("Missing/truncated/fixed allocation mismatch");
            JournalRecord previous = null;
            for (int offset = 0; offset < all.Length; offset += JournalRecord.Size)
            {
                byte[] one = new byte[JournalRecord.Size]; Buffer.BlockCopy(all, offset, one, 0, one.Length);
                bool zero = true; foreach (byte value in one) if (value != 0) { zero = false; break; }
                if (zero)
                {
                    if (previous == null) throw new IOException("Missing enrolled header");
                    for (int tail = offset; tail < all.Length; tail++) if (all[tail] != 0) throw new IOException("Record after empty slot");
                    return previous;
                }
                JournalRecord r = JournalRecord.Decode(one);
                if (r.Sequence != offset / JournalRecord.Size || r.BindingHash != (previous == null ? binding.EnrollmentHash : binding.Hash) || r.Previous != (previous == null ? JournalRecord.Zero : previous.Hash)) throw new IOException("Sequence/hash/binding chain mismatch");
                if (!Allowed(previous == null ? null : previous.State, r.State) || !ReasonAllowed(r.State, r.Reason)) throw new IOException("Illegal fixed transition/reason"); previous = r;
            }
            return previous;
        }
        private static bool Allowed(string from, string to)
        {
            return (from == null && to == "ENROLLED") || (from == "ENROLLED" && to == "SESSION_CLAIMED") || (from == "SESSION_CLAIMED" && to == "RESERVED") || (from == "RESERVED" && to == "CONSUMED_BOUND") || ((from == "SESSION_CLAIMED" || from == "RESERVED" || from == "CONSUMED_BOUND") && (to == "STOP_REQUESTED" || to == "RECOVERY_UNKNOWN")) || (from == "STOP_REQUESTED" && to == "RECOVERY_UNKNOWN");
        }
        private static bool ReasonAllowed(string state, string reason)
        { return (state == "ENROLLED" && reason == "INSTALLER_FIXED_IDLE_ONCE") || (state == "SESSION_CLAIMED" && reason == "FIXED_CONTROLLER_BOOT") || (state == "RESERVED" && reason == "FIXED_IDLE_RESERVE") || (state == "CONSUMED_BOUND" && reason == "VERIFIED_BLOCKED_INVOCATION") || (state == "STOP_REQUESTED" && reason == "IRREVERSIBLE_STOP_LATCH") || (state == "RECOVERY_UNKNOWN" && reason == "INTERNAL_UNCERTAINTY"); }
        private void Append(string state, string reason, string evidenceHash)
        {
            if (!Allowed(head.State, state) || !ReasonAllowed(state, reason)) throw new IOException("No reset/rearm/terminal transition");
            identity.Revalidate(); NativeFile.Info info = NativeFile.Facts(journal, false);
            if (NativeFile.Identity(info) != binding.JournalIdentity) throw new IOException("Held journal identity drift");
            if (identity.Production) NativeFile.Custody(journal, ServiceIdentityLease.Sid, true, true, false);
            JournalRecord actual = ReadChain(); if (actual.Sequence != head.Sequence || actual.Hash != head.Hash) throw new IOException("Journal CAS/head drift");
            JournalRecord next = new JournalRecord { Sequence = head.Sequence + 1, State = state, Previous = head.Hash, BindingHash = binding.Hash, Reason = reason, EvidenceHash = evidenceHash }; byte[] bytes = next.Encode();
            Hit("before-journal-write"); NativeFile.WriteAt(journal, (head.Sequence + 1) * JournalRecord.Size, bytes); Hit("after-journal-write-before-flush"); NativeFile.Flush(journal); Hit("after-journal-flush");
            // Verify precisely the bytes just flushed, through the still-exclusive same handle.
            JournalRecord saved = ReadChain(); if (saved.Sequence != next.Sequence || saved.Hash != next.Hash) throw new IOException("Journal readback mismatch");
            head = next; memoryState = state;
        }
        public AnchorSnapshot Snapshot()
        { lock (writer) { EnsureOpen(); bool stop = Volatile.Read(ref gate) == 1; string state = stop && memoryState != "RECOVERY_UNKNOWN" ? "STOP_REQUESTED" : memoryState; return new AnchorSnapshot(head.Sequence, head.Hash, state, head.State, binding, stop, identity.Production); } }
        public RecordedReservation ReserveOnce(long expectedSequence, string expectedHeadSha256, string expectedGeneration, VerifiedVmReservation vm)
        {
            lock (writer)
            {
                EnsureOpen(); if (expectedGeneration != binding.G || expectedSequence != head.Sequence || expectedHeadSha256 != head.Hash) throw new InvalidOperationException("CAS_OR_GENERATION_MISMATCH");
                if (head.State != "SESSION_CLAIMED" || Volatile.Read(ref gate) != 0) throw new InvalidOperationException("CONSUMPTION_REFUSED");
                try
                {
                    if (vm == null) throw new ArgumentNullException("vm"); vm.Revalidate(binding); initialVm.Revalidate(binding);
                    if (!NativeFile.Equal(initialVm.CanonicalBinding(), vm.CanonicalBinding())) throw new IOException("Cannot rebind first claim to another pre-start proof/G");
                    Append("RESERVED", "FIXED_IDLE_RESERVE", NativeFile.Hash(vm.CanonicalBinding()));
                    if (Volatile.Read(ref gate) == 1) { memoryState = "RECOVERY_UNKNOWN"; throw new IOException("Stop occurred during consumption; late completion is not a live ACK"); }
                    PublishReceipt("reserve-receipt"); identity.Revalidate(); vm.Revalidate(binding);
                    // The final CAS is the ACK linearization. RequestStop never takes writer or waits for I/O.
                    if (Interlocked.CompareExchange(ref gate, 2, 0) != 0) throw new IOException("Stop won ACK linearization");
                    return new RecordedReservation(this, binding, head.Sequence, head.Hash, vm);
                }
                catch (Exception e) { RequestStop(); memoryState = "RECOVERY_UNKNOWN"; throw new RecoveryUnknownException("Consume failed/uncertain; no retry or OS start", e); }
            }
        }
        public RecordedConsumption BindOnce(RecordedReservation reservation, VerifiedVmBinding vm)
        {
            lock (writer)
            {
                EnsureOpen(); if (reservation == null || reservation.Owner != this || head.State != "RESERVED" || head.Sequence != reservation.Sequence || head.Hash != reservation.JournalHeadSha256 || Volatile.Read(ref gate) != 2) throw new InvalidOperationException("BIND_CAS_REFUSED");
                try
                {
                    reservation.ClaimBindAttempt(); reservation.Vm.Revalidate(binding); if (vm == null) throw new ArgumentNullException("vm"); vm.Revalidate(binding, reservation.Vm);
                    Append("CONSUMED_BOUND", "VERIFIED_BLOCKED_INVOCATION", vm.BlockedProofSha256);
                    if (Volatile.Read(ref gate) == 1) throw new IOException("Stop during bind");
                    PublishReceipt("consume-receipt"); identity.Revalidate(); vm.Revalidate(binding, reservation.Vm);
                    if (Interlocked.CompareExchange(ref gate, 3, 2) != 2) throw new IOException("Stop won final ACK linearization");
                    return new RecordedConsumption(this, binding, head.Sequence, head.Hash, vm, reservation.Vm);
                }
                catch (Exception e) { RequestStop(); memoryState = "RECOVERY_UNKNOWN"; throw new RecoveryUnknownException("Bind failed/uncertain; same permit cannot resume", e); }
            }
        }
        private void PublishReceipt(string leaf)
        {
            string temp = Path.Combine(root, leaf + ".pending"), final = Path.Combine(root, leaf + ".bin");
            using (SafeFileHandle h = NativeFile.Open(temp, NativeFile.Read | NativeFile.Write | NativeFile.Delete, 0, NativeFile.CreateNew, false))
            {
                NativeFile.Facts(h, false); if (identity.Production) NativeFile.Custody(h, ServiceIdentityLease.Sid, true, false, false);
                byte[] receipt = head.Encode(); NativeFile.WriteAt(h, 0, receipt); NativeFile.Flush(h); Hit("before-receipt-publish");
                NativeFile.PublishNoReplace(h, final); Hit("after-receipt-publish");
                if (!NativeFile.Equal(NativeFile.ReadAll(h, JournalRecord.Size), receipt)) throw new IOException("Published same-handle receipt differs");
            }
        }
        public void RequestStop() { Interlocked.Exchange(ref gate, 1); }
        public void PersistStopRequest()
        {
            RequestStop(); lock (writer)
            {
                EnsureOpen(); if (head.State == "STOP_REQUESTED" || head.State == "RECOVERY_UNKNOWN") return;
                try { Append("STOP_REQUESTED", "IRREVERSIBLE_STOP_LATCH", JournalRecord.Zero); }
                catch (Exception e) { memoryState = "RECOVERY_UNKNOWN"; throw new RecoveryUnknownException("Stop latched, persistence uncertain; continue independent owned-instance stop", e); }
            }
        }
        public void MarkRecoveryUnknown()
        {
            RequestStop(); lock (writer)
            {
                EnsureOpen(); if (head.State == "RECOVERY_UNKNOWN") return;
                try { Append("RECOVERY_UNKNOWN", "INTERNAL_UNCERTAINTY", JournalRecord.Zero); }
                catch (Exception e) { memoryState = "RECOVERY_UNKNOWN"; throw new RecoveryUnknownException("Uncertainty latch retained despite persistence failure", e); }
            }
        }
        public bool CompareGuestCheckpoint(string generation, long sequence, string checkpointSha256)
        {
            // Guest/IPC values are comparisons only; they never advance/rewrite the host binding or mint authority.
            bool match = generation == binding.G && sequence == binding.GuestSequence && checkpointSha256 == binding.Checkpoint;
            if (!match) RequestStop(); return match && Volatile.Read(ref gate) != 1 && Volatile.Read(ref disposed) == 0;
        }
        internal bool RecordCurrent(RecordedConsumption receipt)
        { return Volatile.Read(ref disposed) == 0 && Volatile.Read(ref gate) == 3 && receipt.Owner == this && receipt.Sequence == 3; }
        internal bool ReservationCurrent(RecordedReservation receipt)
        { return Volatile.Read(ref disposed) == 0 && Volatile.Read(ref gate) == 2 && receipt.Owner == this && receipt.Sequence == 2; }
        internal void RevalidateAck(RecordedConsumption r) { lock (writer) { EnsureOpen(); if (!RecordCurrent(r) || head.Hash != r.JournalHeadSha256) throw new IOException("Final ACK no longer current"); identity.Revalidate(); r.Vm.Revalidate(binding, r.Reservation); if (Interlocked.CompareExchange(ref gate, 3, 3) != 3) throw new IOException("Stop won final ACK revalidation"); } }
        internal void RevalidateReservationAck(RecordedReservation r) { lock (writer) { EnsureOpen(); if (!ReservationCurrent(r) || head.Hash != r.JournalHeadSha256) throw new IOException("Reserve ACK no longer current"); identity.Revalidate(); r.Vm.Revalidate(binding); if (Interlocked.CompareExchange(ref gate, 2, 2) != 2) throw new IOException("Stop won reserve ACK revalidation"); } }
        private void EnsureOpen() { if (Volatile.Read(ref disposed) != 0) throw new ObjectDisposedException("HostAnchor"); }
        public void Dispose()
        {
            RequestStop(); lock (writer)
            {
                if (Interlocked.Exchange(ref disposed, 1) != 0) return;
                if (journal != null) journal.Dispose(); foreach (SafeFileHandle h in held) h.Dispose(); identity.Dispose();
            }
        }
#if P309_TESTS
        internal static HostAnchor OpenFixture(string fixtureRoot, Action<string> fault)
        {
            return OpenFixture(fixtureRoot, fault, VerifiedVmReservation.FromVerifiedLifetimeAuthority(new FixtureVmLease()));
        }
        internal static HostAnchor OpenFixture(string fixtureRoot, Action<string> fault, VerifiedVmReservation vm)
        {
            Binding b = Binding.Parse(File.ReadAllBytes(Path.Combine(fixtureRoot, "test-enrollment.txt")), vm);
            HostAnchor a = new HostAnchor(fixtureRoot, b, new FixtureIdentity(), vm); a.Fault = fault;
            try { a.OpenAndClaim(); return a; } catch (Exception e) { a.Dispose(); throw new RecoveryUnknownException("Fixture refused", e); }
        }
        private sealed class FixtureIdentity : IIdentityLease { public bool Production { get { return false; } } public void Revalidate() { } public void Dispose() { } }
        private sealed class FixtureVmLease : IVerifiedVmReservationLease
        {
            public void Revalidate() { } public void Dispose() { } private string H { get { return new string('a',64); } }
            public string HostBoot { get { return new string('d',32); } } public string GuestBoot { get { return new string('e',32); } }
            public string Challenge { get { return H; } } public string GuestHash { get { return H; } } public string RuntimeHash { get { return H; } }
            public string PolicyHash { get { return H; } } public string PackageHash { get { return H; } } public string Generation { get { return new string('b',32); } }
            public long HostEpochSequence { get { return 1; } } public string VmLifetimeSha256 { get { return new string('3',64); } } public string GuestRootPublicSpkiSha256 { get { return new string('4',64); } }
            public string RootPrestartProofSha256 { get { return new string('5',64); } } public string ApprovalSha256 { get { return new string('6',64); } }
        }
#endif
    }
}
