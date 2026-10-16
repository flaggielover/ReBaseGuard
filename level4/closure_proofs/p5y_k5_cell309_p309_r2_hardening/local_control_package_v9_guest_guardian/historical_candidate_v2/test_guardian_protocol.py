import unittest
import guardian_protocol as P

G = "a"*32

class ProtocolTests(unittest.TestCase):
    def test_all_canonical_packets_and_exact_handoff_count(self):
        for verb in P.VERBS:
            raw=P.packet(verb,G)
            self.assertEqual(P.parse(raw),(verb,G))
        self.assertEqual(P.parse(P.packet("BIND",G),descriptor_count=5,allow_handoff=True),("BIND",G))
        for count in (0,1,4,6,16):
            with self.assertRaises(ValueError):
                P.parse(P.packet("BIND",G),descriptor_count=count,allow_handoff=True)

    def test_ancillary_data_never_enters_gate_or_receipts(self):
        for verb in ("READY","RELEASE","GATE_READY","STOP","LOCAL_QUIESCENT"):
            with self.assertRaises(ValueError):
                P.parse(P.packet(verb,G),descriptor_count=1)
            with self.assertRaises(ValueError):
                P.parse(P.packet(verb,G),allow_handoff=True,descriptor_count=5)

    def test_truncation_concatenation_unknown_and_bad_encoding(self):
        raw=P.packet("READY",G)
        for bad in (raw[:-1],raw+b"x",raw+raw,raw.replace(b"a",b"A"),b"READY "+b"\xff"*32+b"\n",b"START "+G.encode()+b"\n"):
            with self.assertRaises(ValueError): P.parse(bad)
        with self.assertRaises(ValueError): P.parse(raw,truncated=True)

    def test_stale_ready_permanently_refuses_tracker(self):
        t=P.ReceiptTracker(G)
        with self.assertRaises(ValueError): t.receive(P.packet("READY","b"*32))
        with self.assertRaises(ValueError): t.receive(P.packet("READY",G))

    def test_ready_is_not_authority_and_stop_is_not_cleanup(self):
        t=P.ReceiptTracker(G)
        for verb in ("READY","STOP_REQUESTED","LOCAL_QUIESCENT","RETIRING"):
            receipt=t.receive(P.packet(verb,G))
            self.assertFalse(receipt["manager_cleanup_proven"])
            self.assertFalse(receipt["formal_run_authority"])
        with self.assertRaises(ValueError): t.receive(P.packet("READY",G))

    def test_stop_before_ready_never_reenters_ready(self):
        t=P.ReceiptTracker(G)
        t.receive(P.packet("STOP_REQUESTED",G))
        with self.assertRaises(ValueError): t.receive(P.packet("READY",G))

    def test_failed_stop_cannot_claim_quiescence(self):
        t=P.ReceiptTracker(G)
        t.receive(P.packet("STOP_WRITE_UNKNOWN",G))
        with self.assertRaises(ValueError): t.receive(P.packet("LOCAL_QUIESCENT",G))

    def test_no_quiescence_or_retire_without_prior_stop(self):
        for verb in ("LOCAL_QUIESCENT","RETIRING"):
            t=P.ReceiptTracker(G);t.receive(P.packet("READY",G))
            with self.assertRaises(ValueError): t.receive(P.packet(verb,G))

if __name__ == "__main__": unittest.main()
