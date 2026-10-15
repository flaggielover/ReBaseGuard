"""Pure bytes/dictionary tests, compatible with private CPython 3.11.15.

No tar extraction, subprocess, Windows query, helper, VM, network or installation.
"""
import struct
import unittest

from prepare_archives import QEMU_HASH, ROOT, resolve
from runtime_bundle import imports


def package(name, version="1.2-1", dependencies=(), provides=()):
    return {"NAME": [name], "VERSION": [version], "FILENAME": [name + "-1.pkg.tar.zst"],
            "SHA256SUM": ["1" * 64], "CSIZE": ["1"], "ISIZE": ["2"],
            "DEPENDS": list(dependencies), "PROVIDES": list(provides)}


def database(dependencies=()):
    root = package(ROOT, "11.1.2-1", dependencies)
    root["SHA256SUM"] = [QEMU_HASH]
    return {ROOT: root}


def pe_fixture():
    data = bytearray(2048)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HH", data, 0x84, 0x8664, 1)
    struct.pack_into("<H", data, 0x94, 240)
    opt = 0x98
    struct.pack_into("<H", data, opt, 0x20B)
    struct.pack_into("<Q", data, opt + 24, 0x140000000)
    struct.pack_into("<IIII", data, opt + 240 + 8, 1024, 0x1000, 1024, 512)
    struct.pack_into("<II", data, opt + 120, 0x1000, 40)
    struct.pack_into("<IIIII", data, 512, 1, 0, 0, 0x1080, 1)
    data[640:653] = b"KERNEL32.dll\0"
    return data


class DependencyTests(unittest.TestCase):
    def test_cycle_terminates_with_one_package_per_name(self):
        db = database(["a"])
        db["a"] = package("a", dependencies=[ROOT])
        self.assertEqual(len(resolve(db)), 2)

    def test_missing_provider_rejected(self):
        with self.assertRaises(ValueError):
            resolve(database(["missing"]))

    def test_ambiguous_virtual_provider_rejected(self):
        db = database(["v"])
        db.update({n: package(n, provides=["v"]) for n in ("a", "b")})
        with self.assertRaises(ValueError):
            resolve(db)

    def test_exact_dependency_drift_rejected(self):
        db = database(["a=2.0-1"])
        db["a"] = package("a", "2.0-2")
        with self.assertRaises(ValueError):
            resolve(db)

    def test_upstream_minimum_excludes_package_revision(self):
        db = database(["a>=2.1"])
        db["a"] = package("a", "2.1-4")
        self.assertEqual(len(resolve(db)), 2)

    def test_old_version_rejected(self):
        db = database(["a>=2.1"])
        db["a"] = package("a", "2.0-99")
        with self.assertRaises(ValueError):
            resolve(db)

    def test_unknown_version_semantics_rejected(self):
        db = database(["a>=2.1"])
        db["a"] = package("a", "2.1rc1-1")
        with self.assertRaises(ValueError):
            resolve(db)

    def test_qemu_pin_drift_rejected(self):
        db = database()
        db[ROOT]["SHA256SUM"] = ["0" * 64]
        with self.assertRaises(ValueError):
            resolve(db)

    def test_path_escape_rejected(self):
        db = database()
        db[ROOT]["FILENAME"] = ["../other.pkg.tar.zst"]
        with self.assertRaises(ValueError):
            resolve(db)


class ImportTests(unittest.TestCase):
    def test_valid_fixture(self):
        self.assertEqual(imports(pe_fixture()), ["kernel32.dll"])

    def test_non_pe_rejected(self):
        with self.assertRaises(ValueError):
            imports(b"no")

    def test_wrong_architecture_rejected(self):
        data = pe_fixture()
        struct.pack_into("<H", data, 0x84, 0x14C)
        with self.assertRaises(ValueError):
            imports(data)

    def test_out_of_file_rva_rejected(self):
        data = pe_fixture()
        struct.pack_into("<I", data, 512 + 12, 0x4000)
        with self.assertRaises(ValueError):
            imports(data)

    def test_import_traversal_rejected(self):
        data = pe_fixture()
        data[640:653] = b"../other.dll\0"
        with self.assertRaises(ValueError):
            imports(data)

    def test_windows_drv_import_is_not_misclassified(self):
        data = pe_fixture()
        data[640:653] = b"winspool.drv\0"
        self.assertEqual(imports(data), ["winspool.drv"])

    def test_delay_import_included(self):
        data = pe_fixture()
        struct.pack_into("<II", data, 0x98 + 112 + 13 * 8, 0x1100, 64)
        struct.pack_into("<IIIIIIII", data, 768, 1, 0x1180, 0, 0, 0, 0, 0, 0)
        data[896:906] = b"other.dll\0"
        self.assertEqual(imports(data), ["kernel32.dll", "other.dll"])


if __name__ == "__main__":
    unittest.main()
