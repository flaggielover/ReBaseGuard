"""Isolated tests of DEV_ONLY observation composition; no science or campaign is imported.

The canonical attestation verifier reads committed synthetic files in temporary git
repositories. Internal repository/current-machine/readers are patched only by unittest;
the observation API has no public injection or policy seams. LX_PLATFORM_DIR continues
to select the low-level module under the mutation harness while lx_verified is real.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
LXDIR = os.environ.get("LX_PLATFORM_DIR", str(HERE.parent))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, LXDIR)
import lx_platform as L  # noqa: E402
import lx_verified as V  # noqa: E402

BOOT = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
MACHINE = {"machine_id_sha256": "a" * 64, "product_uuid_sha256": "b" * 64, "hardware_bound": True}


class TestVerifiedObservation(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.repo = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.git("init", "-q")
        self.stack.enter_context(mock.patch.object(V, "_REPO_ROOT", self.repo))
        self.machine = self.stack.enter_context(mock.patch.object(L, "machine_identity", return_value=MACHINE))
        # Reader fixtures supply observations only; verification and gate logic stay canonical.
        self.stack.enter_context(mock.patch.object(L, "meminfo", return_value={"MemTotal": 1000, "MemFree": 100}))
        self.stack.enter_context(mock.patch.object(L, "memory_cgroup_chain", return_value={
            "version": "v1", "chain": [
                {"path": "/job", "limit": 700, "usage": 200, "root": False},
                {"path": "/", "limit": 900, "usage": 400, "root": True},
            ]}))
        self.stack.enter_context(mock.patch.object(L, "ns_inode", return_value=L.INIT_CGROUP_NS))
        self.stack.enter_context(mock.patch.object(L, "power_source", return_value=L.AC))
        self.stack.enter_context(mock.patch.object(L, "free_disk_bytes", return_value=L.MIN_FREE_DISK))
        self.stack.enter_context(mock.patch.object(L, "boot_id", side_effect=lambda text=None: text or BOOT))
        self.stack.enter_context(mock.patch.object(L, "auto_update_settings", return_value={
            "guest_updates_shown_disabled": True}))
        self.launch = self.stack.enter_context(mock.patch.object(L, "launched_by_systemd", return_value=self.launch_record()))

    def git(self, *args):
        return subprocess.run([
            "git", "-C", str(self.repo), "-c", "commit.gpgSign=false",
            "-c", "user.name=Synthetic dev fixture", "-c", "user.email=fixture@example.invalid", *args,
        ], check=True, capture_output=True, text=True).stdout

    @staticmethod
    def launch_record(inv="synthetic-invocation"):
        return {"systemd_pid1": True, "unit": L.CAMPAIGN_UNIT_PREFIX + "synthetic.service",
                "invocation_id": inv, "systemctl": {"MainPID": os.getpid(), "InvocationID": inv}, "pass": True}

    def fixture(self, *, commit=True, acceptance=True, raw=None, **changes):
        record = {"schema": L.ATTESTATION_SCHEMA, "reviewed": True, "accepted": True,
                  "machine": MACHINE, "root_cgroup_is_real": True,
                  "provider_image_updates": L.NO_IMAGE_CHANGE, "acceptance_record": "fixtures/review.txt"}
        record.update(changes)
        data = raw if raw is not None else (json.dumps(record, sort_keys=True) + "\n").encode()
        sha = hashlib.sha256(data).hexdigest()
        path = self.repo / "fixtures/host.json"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
        review = f"{L.ACCEPTANCE_LINE}{sha}\n" if acceptance else "SYNTHETIC_REVIEW_REJECTED\n"
        (self.repo / "fixtures/review.txt").write_text(review)
        if commit:
            self.git("add", "fixtures")
            self.git("commit", "-q", "-m", "Synthetic infrastructure fixture")
        return {"path": "fixtures/host.json", "sha256": sha}

    def assert_withheld(self, result):
        self.assertIs(result["development_only"], True)
        self.assertIs(result["operational_ready"], False)
        self.assertEqual(result["raw_memory"]["classification"], "RAW_LINUX_READINGS")
        readings = result["raw_memory"]["readings"]
        self.assertNotIn("effective_limit", readings)
        self.assertNotIn("cgroup_min_headroom", readings)
        self.assertEqual(result["raw_memory"]["withheld_quantities"], ["effective_limit", "cgroup_min_headroom"])
        self.assertEqual(result["conditions"]["A5"], "UNMET_FIXED_SCIENCE_IMPORT_LIST_AND_PIN_POINT")

    def assert_no_root(self, ref):
        result = V.observe(ref)
        self.assertIs(result["attestation"]["root_cgroup_is_real"], False)
        self.assertIs(result["raw_memory"]["readings"]["root_attested"], False)
        self.assert_withheld(result)
        return result

    def test_verified_committed_fixture_supplies_raw_root_contract(self):
        ref = self.fixture()
        with mock.patch.object(L, "memory_readings", wraps=L.memory_readings) as memory:
            result = V.observe(ref)
        self.assertIs(result["attestation"]["verified"], True)
        self.assertIs(result["attestation"]["root_cgroup_is_real"], True)
        self.assertIs(result["raw_memory"]["readings"]["root_attested"], True)
        self.assertEqual(result["attestation"]["reasons"], [])
        memory.assert_called_once_with(root_attested=True)
        self.assertEqual(result["raw_memory"]["readings"]["visible_limit_upper_bound"], 700)
        self.assert_withheld(result)

    def test_canonical_verifier_has_internal_repository_and_default_machine(self):
        ref = self.fixture()
        with mock.patch.object(L, "attestation_valid", wraps=L.attestation_valid) as verifier:
            result = V.observe(ref)
        self.assertIs(result["attestation"]["verified"], True)
        self.assertGreaterEqual(verifier.call_count, 2)
        for call in verifier.call_args_list:
            self.assertEqual(call.args, (ref,))
            self.assertEqual(call.kwargs, {"repo_root": self.repo})
        self.assertGreaterEqual(self.machine.call_count, 2)
        for call in self.machine.call_args_list:
            self.assertEqual((call.args, call.kwargs), ((), {}))

    def test_missing_reference_withholds_root_contract(self):
        self.assertIs(self.assert_no_root(None)["attestation"]["verified"], False)

    def test_malformed_references_withhold_root_contract(self):
        valid = self.fixture()
        for ref in ({}, [], "caller facts", {"path": valid["path"], "sha256": "invalid"},
                    dict(valid, root_cgroup_is_real=True), dict(valid, reviewed=True, accepted=True)):
            with self.subTest(ref=ref):
                self.assertIs(self.assert_no_root(ref)["attestation"]["verified"], False)

    def test_uncommitted_fixture_withholds_root_contract(self):
        self.assertIs(self.assert_no_root(self.fixture(commit=False))["attestation"]["verified"], False)

    def test_non_json_committed_fixture_withholds_root_contract(self):
        self.assertIs(self.assert_no_root(self.fixture(raw=b"not-json\n"))["attestation"]["verified"], False)

    def test_unreviewed_fixture_withholds_root_contract(self):
        self.assertIs(self.assert_no_root(self.fixture(reviewed=False))["attestation"]["verified"], False)

    def test_unaccepted_fixture_withholds_root_contract(self):
        self.assertIs(self.assert_no_root(self.fixture(accepted=False))["attestation"]["verified"], False)

    def test_missing_acceptance_line_withholds_root_contract(self):
        self.assertIs(self.assert_no_root(self.fixture(acceptance=False))["attestation"]["verified"], False)

    def test_wrong_sha_withholds_root_contract(self):
        ref = dict(self.fixture(), sha256="0" * 64)
        self.assertIs(self.assert_no_root(ref)["attestation"]["verified"], False)

    def test_wrong_host_withholds_root_contract(self):
        ref = self.fixture(machine=dict(MACHINE, product_uuid_sha256="c" * 64))
        self.assertIs(self.assert_no_root(ref)["attestation"]["verified"], False)

    def test_machine_id_without_hardware_binding_withholds_root_contract(self):
        ref = self.fixture(machine=dict(MACHINE, hardware_bound=False))
        self.machine.return_value = dict(MACHINE, hardware_bound=False)
        self.assertIs(self.assert_no_root(ref)["attestation"]["verified"], False)

    def test_verified_non_boolean_root_claims_withhold_root_contract(self):
        for value in (False, None, 1, "True", [], {"asserted": True}):
            with self.subTest(value=value):
                result = self.assert_no_root(self.fixture(root_cgroup_is_real=value))
                self.assertIs(result["attestation"]["verified"], True)

    def test_missing_root_claim_withholds_root_contract(self):
        data = {"schema": L.ATTESTATION_SCHEMA, "reviewed": True, "accepted": True,
                "machine": MACHINE, "acceptance_record": "fixtures/review.txt"}
        result = self.assert_no_root(self.fixture(raw=json.dumps(data).encode()))
        self.assertIs(result["attestation"]["verified"], True)

    def test_public_api_refuses_caller_selected_seams(self):
        ref = self.fixture()
        for key in ("root_attested", "root_cgroup_is_real", "repo_root", "machine", "attestation_check",
                    "launch_observer", "readings", "decided", "launched", "other_job_running"):
            with self.subTest(key=key), self.assertRaises(TypeError):
                V.observe(ref, **{key: True})

    def test_default_launch_record_is_independently_corroborated(self):
        result = V.observe(self.fixture())
        self.assertEqual(self.launch.call_count, 2)
        for call in self.launch.call_args_list:
            self.assertEqual((call.args, call.kwargs), ((), {}))
        self.assertEqual(result["preflight"]["gates"]["launched_by_systemd"], L.PASS)

    def test_changed_live_launch_observation_refuses_corroboration(self):
        self.launch.side_effect = [self.launch_record("first"), self.launch_record("second")]
        result = V.observe(self.fixture())
        self.assertEqual(result["preflight"]["gates"]["launched_by_systemd"], L.FAIL)
        self.assertIs(result["operational_ready"], False)

    def test_missing_live_launch_observation_refuses_corroboration(self):
        self.launch.side_effect = [self.launch_record(), None]
        result = V.observe(self.fixture())
        self.assertEqual(result["preflight"]["gates"]["launched_by_systemd"], L.FAIL)

    def test_open_decisions_and_unknown_campaign_detector_keep_all_modes_blocked(self):
        ref = self.fixture()
        for mode in L.MODES:
            with self.subTest(mode=mode):
                result = V.observe(ref, mode=mode)
                preflight = result["preflight"]
                self.assertEqual(preflight["mode"], mode)
                self.assertIs(preflight["pass"], False)
                for gate in ("lowpowermode_0", "thermal_pressure_0", "memory_pressure_normal",
                             "free_memory_ge_min", "host_exclusive", "host_lifetime_attested",
                             "no_automatic_os_install"):
                    self.assertEqual(preflight["gates"][gate], L.OPEN_DECISION, gate)
                self.assertEqual(preflight["gates"]["no_other_campaign_job"], L.UNKNOWN)
                self.assert_withheld(result)

    def test_preflight_composition_has_no_caller_reading_launch_or_policy_seam(self):
        ref = self.fixture()
        with mock.patch.object(L, "preflight", wraps=L.preflight) as preflight:
            V.observe(ref)
        call = preflight.call_args
        self.assertEqual(call.args, (self.repo,))
        self.assertEqual(call.kwargs["decided"], frozenset())
        self.assertIsNone(call.kwargs["other_job_running"])
        self.assertIs(call.kwargs["attestation_check"], V._committed_attestation)
        self.assertNotIn("launch_observer", call.kwargs)
        self.assertNotIn("readings", call.kwargs)

    def test_invalid_mode_is_refused_before_any_observation(self):
        with mock.patch.object(L, "attestation_valid") as verifier:
            with self.assertRaises(ValueError):
                V.observe(mode="qualification")
        verifier.assert_not_called()
        self.launch.assert_not_called()

    def test_wrapper_uses_the_same_platform_module_selected_by_harness(self):
        self.assertIs(V.L, L)
        self.assertEqual(Path(L.__file__).resolve().parent, Path(LXDIR).resolve())


if __name__ == "__main__":
    unittest.main()
