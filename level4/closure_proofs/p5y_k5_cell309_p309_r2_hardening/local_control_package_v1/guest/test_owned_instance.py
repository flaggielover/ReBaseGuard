"""New adapter contract tests only; no cgroup/service/process termination."""
import os
import unittest
from unittest.mock import patch
from owned_instance import (parse_properties, parse_cgroup_events, OwnershipUnknown,
                            StartedIdentity, BoundInstance)

RAW = (b'Id=p309-dev-owned-check.service\nInvocationID=' + b'a'*32 +
       b'\nMainPID=123\nExecMainPID=123\nControlGroup=/system.slice/p309-dev-owned-check.service'
       b'\nActiveState=active\nSubState=running\nResult=success\nJob=\n')

class AdapterContract(unittest.TestCase):
    def test_strict_manager_fields(self):
        self.assertEqual(parse_properties(RAW)['MainPID'],123)
        for bad in (RAW+b'Job=1\n', RAW+b'Unknown=1\n',RAW.replace(b'Job=\n',b''),
                    RAW.replace(b'MainPID=123',b'MainPID=-1'),b'x'*16385):
            with self.subTest(bad=bad[-30:]), self.assertRaises(OwnershipUnknown):
                parse_properties(bad)

    def test_kernel_populated_must_be_known(self):
        self.assertEqual(parse_cgroup_events(b'populated 0\nfrozen 0\n'),{'populated':0,'frozen':0})
        for bad in (b'',b'populated 0\n',b'populated 0\npopulated 1\nfrozen 0\n',
                    b'populated 2\nfrozen 0\n',b'populated false\nfrozen 0\n'):
            with self.subTest(raw=bad), self.assertRaises(OwnershipUnknown):
                parse_cgroup_events(bad)

    def test_receipt_is_typed(self):
        base=dict(generation='a'*32,invocation='b'*32,pid=123,start_ticks=42,
                  boot_id='11111111-1111-1111-1111-111111111111')
        StartedIdentity(**base).validate()
        for key,value in [('pid',True),('start_ticks',0),('generation','x'*32),('invocation','A'*32),
                          ('boot_id','-'*36),('boot_id','a'*36)]:
            with self.subTest(key=key), self.assertRaises(OwnershipUnknown):
                StartedIdentity(**dict(base,**{key:value})).validate()

    def test_latch_precedes_owned_fd_write(self):
        # Pipe stands in for a held descriptor. This is not a cgroup proof.
        rd,wr=os.pipe()
        try:
            obj=BoundInstance.__new__(BoundInstance)
            obj.killfd=wr;obj.stop_latched=False;obj.stop_write_error=None
            real_write=os.write
            def checked(fd,data):
                self.assertTrue(obj.stop_latched)
                self.assertEqual(fd,wr)
                return real_write(fd,data)
            with patch('owned_instance.os.write',side_effect=checked):
                self.assertTrue(obj.request_stop())
            self.assertEqual(os.read(rd,2),b'1\n')
        finally:
            os.close(rd);os.close(wr)

    def test_write_failure_retains_latch(self):
        obj=BoundInstance.__new__(BoundInstance)
        obj.killfd=123;obj.stop_latched=False;obj.stop_write_error=None
        with patch('owned_instance.os.write',side_effect=OSError('injected')):
            self.assertFalse(obj.request_stop())
        self.assertTrue(obj.stop_latched)
        self.assertIsNotNone(obj.stop_write_error)

    def test_closed_binding_cannot_acknowledge(self):
        obj=BoundInstance.__new__(BoundInstance)
        obj.killfd=None;obj.stop_latched=False;obj.stop_write_error=None
        self.assertFalse(obj.request_stop())
        self.assertTrue(obj.stop_latched)

    def test_cannot_drop_binding_before_cleanup(self):
        obj=BoundInstance.__new__(BoundInstance)
        obj.cleanup_confirmed=False
        with self.assertRaises(OwnershipUnknown): obj.close()

if __name__ == '__main__': unittest.main()
