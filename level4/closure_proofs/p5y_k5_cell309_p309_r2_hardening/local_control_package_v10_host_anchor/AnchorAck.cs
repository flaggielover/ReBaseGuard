using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using Microsoft.Win32.SafeHandles;

namespace P309HostAnchorV10
{
    // Only HostAnchor constructs this after its final consumption ACK CAS. No public constructor.
    public sealed class RecordedConsumption
    {
        internal readonly HostAnchor Owner; internal readonly Binding Binding; internal readonly VerifiedVmBinding Vm; internal readonly VerifiedVmReservation Reservation; private int ackAttempted;
        public readonly long Sequence; public readonly string JournalHeadSha256;
        internal RecordedConsumption(HostAnchor owner, Binding binding, long sequence, string head, VerifiedVmBinding vm, VerifiedVmReservation reservation) { Owner = owner; Binding = binding; Sequence = sequence; JournalHeadSha256 = head; Vm = vm; Reservation = reservation; }
        public bool IsCurrentAtRead { get { return Owner.RecordCurrent(this); } }
        internal void ClaimAckAttempt() { if (Interlocked.CompareExchange(ref ackAttempted, 1, 0) != 0) throw new InvalidOperationException("ACK_ALREADY_ATTEMPTED; no resend/retry"); Owner.RevalidateAck(this); }
    }
    // Authority boundary, NOT a caller DTO. No public factory accepts VM/guest/invocation strings.
    // The future independently reviewed held-VM/authenticated-broker adapter is compiled inside this
    // trust boundary and must supply this lease; this package does not invent an authenticated VM.
    public sealed class RecordedReservation
    {
        internal readonly HostAnchor Owner; internal readonly Binding Binding; internal readonly VerifiedVmReservation Vm; private int bindAttempted, ackAttempted, ackIssued, contextAttempted;
        public readonly long Sequence; public readonly string JournalHeadSha256;
        internal RecordedReservation(HostAnchor owner, Binding binding, long sequence, string head, VerifiedVmReservation vm) { Owner = owner; Binding = binding; Sequence = sequence; JournalHeadSha256 = head; Vm = vm; }
        public bool IsCurrentAtRead { get { return Owner.ReservationCurrent(this); } }
        internal void ClaimAckAttempt() { if (Interlocked.CompareExchange(ref ackAttempted, 1, 0) != 0) throw new IOException("RESERVE_ACK_ALREADY_ATTEMPTED"); Owner.RevalidateReservationAck(this); }
        internal void ClaimBindAttempt() { if (Volatile.Read(ref ackIssued) != 1) throw new IOException("SIGNED_RESERVE_ACK_REQUIRED"); if (Interlocked.CompareExchange(ref bindAttempted, 1, 0) != 0) throw new IOException("BIND_ALREADY_ATTEMPTED"); }
        internal void MarkReserveAckIssued() { Owner.RevalidateReservationAck(this); Interlocked.Exchange(ref ackIssued, 1); }
        internal void ClaimContextAttempt() { if (Interlocked.CompareExchange(ref contextAttempted, 1, 0) != 0) throw new IOException("SESSION_CONTEXT_ALREADY_ATTEMPTED"); Owner.RevalidateReservationAck(this); }
#if P309_TESTS
        internal void RecordSyntheticReserveAckForTests() { Interlocked.Exchange(ref ackIssued, 1); }
#endif
    }
    internal interface IVerifiedVmReservationLease : IDisposable
    {
        void Revalidate(); string HostBoot { get; } string GuestBoot { get; } string Challenge { get; } string GuestHash { get; }
        string RuntimeHash { get; } string PolicyHash { get; } string PackageHash { get; } string Generation { get; } long HostEpochSequence { get; }
        string VmLifetimeSha256 { get; } string GuestRootPublicSpkiSha256 { get; }
        string RootPrestartProofSha256 { get; } string ApprovalSha256 { get; }
    }
    internal interface IVerifiedVmLifetimeLease : IVerifiedVmReservationLease
    { string WorkerInvocation { get; } string BrokerInvocation { get; } string BlockedProofSha256 { get; } }
    public sealed class VerifiedVmReservation : IDisposable
    {
        private readonly IVerifiedVmReservationLease lease; private bool disposed;
        internal readonly string HostBoot, GuestBoot, Challenge, GuestHash, RuntimeHash, PolicyHash, PackageHash, Generation, VmLifetimeSha256, GuestRootPublicSpkiSha256, RootPrestartProofSha256, ApprovalSha256; internal readonly long HostEpochSequence;
        private VerifiedVmReservation(IVerifiedVmReservationLease v)
        {
            lease = v; v.Revalidate(); HostBoot = v.HostBoot; GuestBoot = v.GuestBoot; Challenge = v.Challenge; GuestHash = v.GuestHash;
            RuntimeHash = v.RuntimeHash; PolicyHash = v.PolicyHash; PackageHash = v.PackageHash; Generation = v.Generation; HostEpochSequence = v.HostEpochSequence; VmLifetimeSha256 = v.VmLifetimeSha256; GuestRootPublicSpkiSha256 = v.GuestRootPublicSpkiSha256;
            RootPrestartProofSha256 = v.RootPrestartProofSha256; ApprovalSha256 = v.ApprovalSha256;
            foreach (string x in new string[] { HostBoot, GuestBoot, Generation }) AckCanonical.Hex(x, 32);
            foreach (string x in new string[] { Challenge, GuestHash, RuntimeHash, PolicyHash, PackageHash, VmLifetimeSha256, GuestRootPublicSpkiSha256, RootPrestartProofSha256, ApprovalSha256 }) AckCanonical.Hex(x, 64);
            if (HostEpochSequence <= 0) throw new IOException("Host epoch sequence");
        }
        internal static VerifiedVmReservation FromVerifiedLifetimeAuthority(IVerifiedVmReservationLease lease)
        { if (lease == null) throw new ArgumentNullException("lease"); return new VerifiedVmReservation(lease); }
        internal byte[] CanonicalBinding()
        { return Encoding.ASCII.GetBytes("P309_HOST_RESERVATION_BINDING/1\n" + Generation + "\n" + HostEpochSequence.ToString(System.Globalization.CultureInfo.InvariantCulture) + "\n" + HostBoot + "\n" + GuestBoot + "\n" + PackageHash + "\n" + GuestHash + "\n" + RuntimeHash + "\n" + PolicyHash + "\n" + Challenge + "\n" + VmLifetimeSha256 + "\n" + GuestRootPublicSpkiSha256 + "\n" + RootPrestartProofSha256 + "\n" + ApprovalSha256 + "\n"); }
        internal void Revalidate(Binding b)
        {
            if (disposed) throw new ObjectDisposedException("VerifiedVmReservation"); lease.Revalidate();
            if (lease.HostBoot != HostBoot || lease.GuestBoot != GuestBoot || lease.Challenge != Challenge || lease.GuestHash != GuestHash || lease.RuntimeHash != RuntimeHash || lease.PolicyHash != PolicyHash || lease.PackageHash != PackageHash || lease.Generation != Generation || lease.HostEpochSequence != HostEpochSequence || lease.VmLifetimeSha256 != VmLifetimeSha256 || lease.GuestRootPublicSpkiSha256 != GuestRootPublicSpkiSha256 || lease.RootPrestartProofSha256 != RootPrestartProofSha256 || lease.ApprovalSha256 != ApprovalSha256) throw new IOException("Lifetime authority changed reservation fields");
            if (Generation != b.G || GuestHash != b.Guest || RuntimeHash != b.Runtime || PolicyHash != b.Policy || PackageHash != b.Source || HostEpochSequence != b.HostEpochSequence || HostBoot != b.HostBoot || GuestRootPublicSpkiSha256 != b.GuestRootPublic || ApprovalSha256 != b.Approval) throw new IOException("Lifetime does not match installer binding");
        }
        public void Dispose() { if (disposed) return; disposed = true; lease.Dispose(); }
    }
    public sealed class VerifiedVmBinding : IDisposable
    {
        private readonly IVerifiedVmLifetimeLease lease; private bool disposed;
        internal readonly VerifiedVmReservation Reservation; internal readonly string WorkerInvocation, BrokerInvocation, BlockedProofSha256;
        private VerifiedVmBinding(IVerifiedVmLifetimeLease v)
        { lease = v; Reservation = VerifiedVmReservation.FromVerifiedLifetimeAuthority(v); WorkerInvocation = v.WorkerInvocation; BrokerInvocation = v.BrokerInvocation; BlockedProofSha256 = v.BlockedProofSha256; AckCanonical.Hex(WorkerInvocation, 32); AckCanonical.Hex(BrokerInvocation, 32); AckCanonical.Hex(BlockedProofSha256, 64); }
        // Only same-assembly trusted integration can construct; never exposed as an IPC deserializer.
        internal static VerifiedVmBinding FromVerifiedLifetimeAuthority(IVerifiedVmLifetimeLease lease)
        { if (lease == null) throw new ArgumentNullException("lease"); lease.Revalidate(); return new VerifiedVmBinding(lease); }
        internal void Revalidate(Binding binding, VerifiedVmReservation reservation)
        {
            if (disposed) throw new ObjectDisposedException("VerifiedVmBinding"); Reservation.Revalidate(binding); reservation.Revalidate(binding);
            if (!NativeFile.Equal(Reservation.CanonicalBinding(), reservation.CanonicalBinding()) || lease.WorkerInvocation != WorkerInvocation || lease.BrokerInvocation != BrokerInvocation || lease.BlockedProofSha256 != BlockedProofSha256) throw new IOException("Blocked proof/lifetime drift");
        }
        public void Dispose() { if (disposed) return; disposed = true; Reservation.Dispose(); }
    }
    public sealed class SignedAnchorAck
    {
        private readonly byte[] canonical, signature, publicDer;
        public byte[] CanonicalBytes { get { return (byte[])canonical.Clone(); } }
        public byte[] Signature { get { return (byte[])signature.Clone(); } }
        public byte[] PublicKeySpkiDer { get { return (byte[])publicDer.Clone(); } }
        public readonly string Algorithm = "RSA-SHA256-PKCS1-v1_5";
        internal SignedAnchorAck(byte[] body, byte[] sig, byte[] der) { canonical = (byte[])body.Clone(); signature = (byte[])sig.Clone(); publicDer = (byte[])der.Clone(); }
    }
    internal static class AckCanonical
    {
        internal static void Hex(string value, int n) { if (value == null || value.Length != n) throw new IOException("ACK field length"); foreach (char c in value) if (!(c >= '0' && c <= '9') && !(c >= 'a' && c <= 'f')) throw new IOException("ACK field syntax"); }
        internal static byte[] Encode(RecordedConsumption r)
        {
            r.Vm.Revalidate(r.Binding, r.Reservation); VerifiedVmReservation v = r.Reservation;
            string s = "protocol=P309_HOST_ANCHOR_ACK/1\nscope=DEV_FIXED_IDLE_ONLY\nG=" + r.Binding.G +
                "\nhost_epoch_seq=" + r.Binding.HostEpochSequence.ToString(System.Globalization.CultureInfo.InvariantCulture) +
                "\nhost_boot=" + v.HostBoot + "\nguest_boot=" + v.GuestBoot + "\npackage=" + r.Binding.Source +
                "\nguest=" + r.Binding.Guest + "\nruntime=" + r.Binding.Runtime + "\npolicy=" + r.Binding.Policy +
                "\nworkerInv=" + r.Vm.WorkerInvocation + "\nbrokerInv=" + r.Vm.BrokerInvocation + "\nchallenge=" + v.Challenge + "\nblocked_proof_sha256=" + r.Vm.BlockedProofSha256 +
                "\nhost_record_seq=" + r.Sequence.ToString(System.Globalization.CultureInfo.InvariantCulture) + "\nhost_record_sha256=" + r.JournalHeadSha256 +
                "\nanchor_binding_sha256=" + r.Binding.Hash + "\ncheckpoint=" + r.Binding.Checkpoint + "\n";
            return new UTF8Encoding(false, true).GetBytes(s);
        }
        internal static byte[] EncodeReservation(RecordedReservation r)
        {
            r.Vm.Revalidate(r.Binding); VerifiedVmReservation v = r.Vm;
            string s = "protocol=P309_HOST_ANCHOR_RESERVE_ACK/1\nscope=DEV_FIXED_IDLE_ONLY\nG=" + r.Binding.G +
                "\nhost_epoch_seq=" + r.Binding.HostEpochSequence.ToString(System.Globalization.CultureInfo.InvariantCulture) + "\nhost_boot=" + v.HostBoot + "\nguest_boot=" + v.GuestBoot +
                "\npackage=" + r.Binding.Source + "\nguest=" + r.Binding.Guest + "\nruntime=" + r.Binding.Runtime + "\npolicy=" + r.Binding.Policy + "\nchallenge=" + v.Challenge +
                "\nhost_record_seq=" + r.Sequence.ToString(System.Globalization.CultureInfo.InvariantCulture) + "\nhost_record_sha256=" + r.JournalHeadSha256 + "\nanchor_binding_sha256=" + r.Binding.Hash + "\ncheckpoint=" + r.Binding.Checkpoint + "\n";
            return Encoding.ASCII.GetBytes(s);
        }
        internal static byte[] EncodeSessionContext(RecordedReservation r)
        {
            string reserve = Encoding.ASCII.GetString(EncodeReservation(r));
            string common = reserve.Replace("protocol=P309_HOST_ANCHOR_RESERVE_ACK/1\n", "protocol=P309_HOST_VM_SESSION/1\n");
            return Encoding.ASCII.GetBytes(common + "vm_lifetime_sha256=" + r.Vm.VmLifetimeSha256 + "\nguest_root_public_spki_sha256=" + r.Vm.GuestRootPublicSpkiSha256 + "\nack_public_spki_sha256=" + r.Binding.AckPublic + "\n");
        }
        internal static byte[] Spki(RSAParameters p)
        {
            byte[] key = Wrap(0x30, Concat(Integer(p.Modulus), Integer(p.Exponent)));
            byte[] algorithm = new byte[] { 0x30, 0x0d, 0x06, 0x09, 0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x01, 0x05, 0x00 };
            return Wrap(0x30, Concat(algorithm, Wrap(3, Concat(new byte[] { 0 }, key))));
        }
        private static byte[] Integer(byte[] b) { if (b == null || b.Length == 0) throw new IOException("Invalid RSA public integer"); return Wrap(2, (b[0] & 128) != 0 ? Concat(new byte[] { 0 }, b) : b); }
        private static byte[] Concat(byte[] a, byte[] b) { byte[] c = new byte[a.Length + b.Length]; Buffer.BlockCopy(a, 0, c, 0, a.Length); Buffer.BlockCopy(b, 0, c, a.Length, b.Length); return c; }
        private static byte[] Wrap(byte tag, byte[] b)
        {
            byte[] length = b.Length < 128 ? new byte[] { (byte)b.Length } : (b.Length < 256 ? new byte[] { 0x81, (byte)b.Length } : new byte[] { 0x82, (byte)(b.Length >> 8), (byte)b.Length });
            return Concat(Concat(new byte[] { tag }, length), b);
        }
    }
    public sealed class AnchorAckSigner : IDisposable
    {
        public const string KeyName = "ReBaseGuardP309.Controller.AnchorAck.v1";
        public const string ProviderName = "Microsoft Software Key Storage Provider";
        private readonly CngKey key; private readonly RSACng rsa; private readonly ServiceIdentityLease identity; private readonly string uniqueHash, publicHash; private bool disposed; private readonly object signing = new object();
        [DllImport("ncrypt.dll", CharSet = CharSet.Unicode)] private static extern int NCryptGetProperty(SafeNCryptKeyHandle key, string property, byte[] output, int capacity, out int required, int flags);
        private AnchorAckSigner(CngKey k, RSACng r, ServiceIdentityLease i, string unique, string pub) { key = k; rsa = r; identity = i; uniqueHash = unique; publicHash = pub; }
        public static AnchorAckSigner OpenInstalled()
        {
            ServiceIdentityLease identity = null; CngKey key = null; RSACng rsa = null;
            try
            {
                identity = ServiceIdentityLease.Create();
                // OPEN only. No Create/overwrite/import/private-export fallback exists.
                key = CngKey.Open(KeyName, new CngProvider(ProviderName), CngKeyOpenOptions.MachineKey | CngKeyOpenOptions.Silent);
                if (!key.IsMachineKey || key.IsEphemeral || key.KeyName != KeyName || key.Provider.Provider != ProviderName || key.Algorithm.Algorithm != "RSA" || key.ExportPolicy != CngExportPolicies.None || key.KeyUsage != CngKeyUsages.Signing) throw new IOException("Fixed existing ACK key policy mismatch");
                CheckKeyCustody(key); rsa = new RSACng(key); if (rsa.KeySize != 3072) throw new IOException("ACK RSA3072 required");
                string u = NativeFile.Hash(Encoding.UTF8.GetBytes(key.UniqueName)), p = NativeFile.Hash(AckCanonical.Spki(rsa.ExportParameters(false)));
                AnchorAckSigner result = new AnchorAckSigner(key, rsa, identity, u, p); key = null; rsa = null; identity = null; return result;
            }
            catch { if (rsa != null) rsa.Dispose(); if (key != null) key.Dispose(); if (identity != null) identity.Dispose(); throw; }
        }
        private static void CheckKeyCustody(CngKey key)
        {
            using (SafeNCryptKeyHandle handle = key.Handle)
            {
                int needed; int rc = NCryptGetProperty(handle, "Security Descr", null, 0, out needed, 5 | 0x40);
                if (rc != 0 || needed <= 0 || needed > 65536) throw new IOException("Cannot read ACK key owner/DACL");
                byte[] b = new byte[needed]; rc = NCryptGetProperty(handle, "Security Descr", b, b.Length, out needed, 5 | 0x40);
                if (rc != 0 || needed > b.Length) throw new IOException("Incomplete ACK key descriptor"); RawSecurityDescriptor sd = new RawSecurityDescriptor(b, 0);
                if (sd.Owner == null || (sd.Owner.Value != "S-1-5-18" && sd.Owner.Value != "S-1-5-32-544") || sd.DiscretionaryAcl == null || (sd.ControlFlags & ControlFlags.DiscretionaryAclProtected) == 0) throw new IOException("ACK key custody/protection mismatch");
                foreach (GenericAce item in sd.DiscretionaryAcl)
                {
                    CommonAce a = item as CommonAce; if (a == null || a.IsCallback) throw new IOException("Unsupported ACK key ACE"); if (a.AceQualifier == AceQualifier.AccessDenied) continue;
                    if (a.AceQualifier != AceQualifier.AccessAllowed) throw new IOException("Unexpected ACK key ACE");
                    string sid = a.SecurityIdentifier.Value; uint mask = (uint)a.AccessMask;
                    if (sid == "S-1-5-18" || sid == "S-1-5-32-544") continue;
                    if (sid != ServiceIdentityLease.Sid || (mask & ~0x80020001U) != 0) throw new IOException("ACK key has foreign use/manage grant");
                }
            }
        }
        public SignedAnchorAck SignConsumption(RecordedConsumption record) { lock (signing) { return SignConsumptionCore(record); } }
        private SignedAnchorAck SignConsumptionCore(RecordedConsumption record)
        {
            if (record == null) throw new ArgumentNullException("record");
            try
            {
                record.ClaimAckAttempt();
                if (disposed) throw new ObjectDisposedException("AnchorAckSigner"); identity.Revalidate(); record.Vm.Revalidate(record.Binding, record.Reservation); CheckKeyCustody(key);
                if (uniqueHash != record.Binding.AckKeyIdentity || publicHash != record.Binding.AckPublic) throw new IOException("Installer ACK key identity/public pin mismatch");
                byte[] canonical = AckCanonical.Encode(record); byte[] signature = rsa.SignData(canonical, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                // Stop does not wait for CNG; a late CNG completion must never be released as a live ACK.
                identity.Revalidate(); record.Owner.RevalidateAck(record);
                return new SignedAnchorAck(canonical, signature, AckCanonical.Spki(rsa.ExportParameters(false)));
            }
            catch { record.Owner.RequestStop(); throw; }
        }
        public SignedAnchorAck SignReservation(RecordedReservation record) { lock (signing) { return SignReservationCore(record); } }
        private SignedAnchorAck SignReservationCore(RecordedReservation record)
        {
            if (record == null) throw new ArgumentNullException("record");
            try
            {
                record.ClaimAckAttempt();
                if (disposed) throw new ObjectDisposedException("AnchorAckSigner"); identity.Revalidate(); CheckKeyCustody(key);
                if (uniqueHash != record.Binding.AckKeyIdentity || publicHash != record.Binding.AckPublic) throw new IOException("Installer ACK key mismatch");
                byte[] canonical = AckCanonical.EncodeReservation(record), signature = rsa.SignData(canonical, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                identity.Revalidate(); record.MarkReserveAckIssued(); return new SignedAnchorAck(canonical, signature, AckCanonical.Spki(rsa.ExportParameters(false)));
            }
            catch { record.Owner.RequestStop(); throw; }
        }
        public SignedAnchorAck SignSessionContext(RecordedReservation record)
        {
            lock (signing)
            {
                if (record == null) throw new ArgumentNullException("record");
                try
                {
                    record.ClaimContextAttempt(); if (disposed) throw new ObjectDisposedException("AnchorAckSigner"); identity.Revalidate(); CheckKeyCustody(key);
                    if (uniqueHash != record.Binding.AckKeyIdentity || publicHash != record.Binding.AckPublic) throw new IOException("Installer ACK key mismatch");
                    byte[] canonical = AckCanonical.EncodeSessionContext(record), signature = rsa.SignData(canonical, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                    identity.Revalidate(); record.Owner.RevalidateReservationAck(record); return new SignedAnchorAck(canonical, signature, AckCanonical.Spki(rsa.ExportParameters(false)));
                }
                catch { record.Owner.RequestStop(); throw; }
            }
        }
        public void Dispose() { lock (signing) { if (disposed) return; disposed = true; rsa.Dispose(); key.Dispose(); identity.Dispose(); } }
    }
}
