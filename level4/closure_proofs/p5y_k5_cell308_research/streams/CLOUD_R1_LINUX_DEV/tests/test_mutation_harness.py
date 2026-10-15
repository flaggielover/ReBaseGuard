"""Pure harness controls: synthetic reports and mocked subprocesses; no evaluator or host reader."""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import run_mutants as H


METHOD = "test_property"
NAME = f"{METHOD} (test_fixture.TestProperty.{METHOD})"


def report(*, failures=0, errors=0, skipped=0, ran=2, exception="AssertionError", name=NAME):
    blocks = ""
    if failures:
        blocks = "=" * 70 + f"\nFAIL: {name}\n" + "-" * 70 + "\n" \
            + f'Traceback (most recent call last):\n  File "fixture.py", line 1, in {METHOD}\n    assert False\n{exception}: property\n\n'
    if errors:
        blocks += "=" * 70 + f"\nERROR: {name}\n" + "-" * 70 + "\nRuntimeError: invalid\n\n"
    counts = [f"{key}={value}" for key, value in (("failures", failures), ("errors", errors), ("skipped", skipped)) if value]
    summary = "FAILED (" + ", ".join(counts) + ")" if failures or errors else ("OK (skipped=1)" if skipped else "OK")
    return blocks + "-" * 70 + f"\nRan {ran} tests in 0.001s\n\n{summary}\n"


def metadata_for(stderr, *, exception="AssertionError"):
    count = re.search(r"^Ran (\d+) tests? in", stderr, re.MULTILINE)
    events = []
    for kind, label in (("failure", "FAIL"), ("error", "ERROR")):
        for name in re.findall(rf"^{label}: (.+)$", stderr, re.MULTILINE):
            method, owner = re.match(r"([^ ]+) \(([^)]+)\)", name).groups()
            parent = owner if owner.endswith("." + method) else owner + "." + method
            exception_type = exception.rsplit("\n", 1)[-1].split(":", 1)[0] if kind == "failure" else "RuntimeError"
            events.append({"kind": kind, "test_id": parent, "parent_test_id": parent, "description": name,
                           "exception_type": "builtins." + exception_type,
                           "is_exact_assertion_error": exception_type == "AssertionError",
                           "traceback_frames": [{"file": "fixture.py", "line": 1, "function": METHOD}]})
    ran = int(count[1]) if count else 2
    executed = ["test_fixture.TestProperty.test_property", "test_fixture.Other.test_other"]
    return {"schema": "CELL308_CONTROLLED_UNITTEST_RESULT_V1", "ran": ran,
            "successful": "\nOK" in stderr, "events": events,
            "executed_test_ids": executed[:ran] + [f"test_fixture.Extra.test_{i}" for i in range(2, ran)],
            "skipped": int(re.search(r"skipped=(\d+)", stderr)[1]) if "skipped=" in stderr else 0,
            "expected_failures": int(re.search(r"expected failures=(\d+)", stderr)[1])
            if "expected failures=" in stderr else 0,
            "unexpected_successes": int(re.search(r"unexpected successes=(\d+)", stderr)[1])
            if "unexpected successes=" in stderr else 0}


def suite(*, returncode=None, stdout="", stderr=None, **counts):
    stderr = report(**counts) if stderr is None else stderr
    return H._suite_record(["python", "synthetic"], {}, returncode=(1 if counts.get("failures") or counts.get("errors")
                           else 0) if returncode is None else returncode,
                           stdout=stdout, stderr=stderr, elapsed_s=0.001,
                           result_metadata=metadata_for(stderr, exception=counts.get("exception", "AssertionError")))


class TestStrictReportClassification(unittest.TestCase):
    def setUp(self):
        self.base = suite()

    def classify(self, record):
        return H.classify_mutant(record, self.base, [METHOD])

    def test_only_a_full_count_named_assertion_is_killed(self):
        killed = suite(failures=1)
        self.assertEqual(self.classify(killed), ("KILLED", []))
        self.assertEqual(killed["assertion_failure_names"], [NAME])
        self.assertEqual(killed["stderr"], report(failures=1))
        self.assertEqual(self.classify(suite()), ("SURVIVED", []))

    def test_four_historical_error_only_shapes_are_errors(self):
        for mutant, errors in (("M29", 2), ("N04", 1), ("Y09", 1), ("Z09", 1)):
            with self.subTest(mutant=mutant):
                record = suite(errors=errors)
                self.assertEqual(self.classify(record)[0], "ERROR")
                self.assertIn("UNITTEST_ERRORS", record["invalid_reasons"])

    def test_failure_header_may_include_a_unittest_docstring(self):
        stderr = report(failures=1).replace(f"FAIL: {NAME}\n", f"FAIL: {NAME}\nIntended property documentation.\n")
        self.assertEqual(self.classify(suite(stderr=stderr, returncode=1)), ("KILLED", []))

    def test_runtime_exception_in_a_failure_block_is_invalid(self):
        for exception in ("RuntimeError", "AssertionError: quoted text\nRuntimeError"):
            record = suite(failures=1, exception=exception)
            self.assertEqual(self.classify(record)[0], "ERROR")
            self.assertIn("FAILURE_WITHOUT_ASSERTIONERROR_TRACE", record["invalid_reasons"])

    def test_unrelated_assertion_has_no_intended_property_credit(self):
        record = suite(failures=1, name="test_other (test_fixture.Other.test_other)")
        self.assertEqual(self.classify(record), ("ERROR", ["NO_INTENDED_PROPERTY_ASSERTION"]))

    def test_missing_or_changed_count_is_invalid(self):
        self.assertIn("TEST_COUNT_DIFFERS_FROM_BASELINE", self.classify(suite(failures=1, ran=1))[1])
        self.assertEqual(self.classify(suite(stderr="import failed\n", returncode=1))[0], "ERROR")

    def test_errors_skips_and_expected_outcomes_are_invalid(self):
        for record in (suite(failures=1, errors=1), suite(skipped=1),
                       suite(stderr=report().replace("OK", "OK (expected failures=1)"))):
            with self.subTest(summary=record["summary"]):
                self.assertEqual(self.classify(record)[0], "ERROR")

    def test_warnings_in_either_stream_are_invalid(self):
        for stdout, suffix in (("UserWarning: synthetic\n", ""), ("", "ResourceWarning: synthetic\n"),
                               ("", "Exception ignored in: synthetic\n")):
            record = suite(failures=1, stdout=stdout, stderr=report(failures=1) + suffix)
            self.assertEqual(self.classify(record)[0], "ERROR")
            self.assertIn("UNRAISABLE_OR_WARNING", record["invalid_reasons"])

    def test_exit_summary_and_named_outcomes_must_agree(self):
        for record in (suite(failures=1, returncode=0), suite(failures=1, returncode=2),
                       suite(failures=1, returncode=-9),
                       suite(stderr=report(failures=1).replace("failures=1", "failures=2"), returncode=1),
                       suite(stderr=report() + "OK\n"),
                       suite(stderr=report(failures=1).replace("failures=1", "failures=1, other=1"), returncode=1)):
            with self.subTest(summary=record["summary"], rc=record["returncode"]):
                self.assertEqual(self.classify(record)[0], "ERROR")

    def test_failed_baseline_never_credits_a_mutant(self):
        self.base = suite(failures=1)
        self.assertEqual(self.classify(suite(failures=1)), ("ERROR", ["BASELINE_NOT_PASS"]))

    def test_multiple_assertion_traces_are_retained(self):
        first = report(failures=1).split("-" * 70 + "\nRan", 1)[0]
        second = first.replace(NAME, "test_other (test_fixture.Other.test_other)")
        stderr = first + second + "-" * 70 + "\nRan 2 tests in 0.001s\n\nFAILED (failures=2)\n"
        record = suite(stderr=stderr, returncode=1)
        self.assertEqual(self.classify(record), ("KILLED", []))
        self.assertEqual(len(record["assertion_failure_names"]), 2)

    def test_runtime_error_with_quoted_assertion_suffix_has_no_credit(self):
        stderr = report(failures=1, exception="RuntimeError: actual error\nAssertionError")
        record = suite(stderr=stderr, returncode=1, exception="RuntimeError")
        self.assertEqual(self.classify(record)[0], "ERROR")
        self.assertIn("FAILURE_IS_NOT_ASSERTIONERROR", record["invalid_reasons"])

    def test_fake_traceback_marker_without_real_frame_has_no_credit(self):
        stderr = report(failures=1).replace('  File "fixture.py", line 1, in test_property\n    assert False\n', "")
        record = suite(stderr=stderr, returncode=1)
        self.assertEqual(self.classify(record)[0], "ERROR")
        self.assertIn("FAILURE_WITHOUT_ASSERTIONERROR_TRACE", record["invalid_reasons"])

    def test_duplicate_identical_failure_records_have_no_credit(self):
        first = report(failures=1).split("-" * 70 + "\nRan", 1)[0]
        stderr = first + first + "-" * 70 + "\nRan 2 tests in 0.001s\n\nFAILED (failures=2)\n"
        record = suite(stderr=stderr, returncode=1)
        self.assertEqual(self.classify(record)[0], "ERROR")
        self.assertIn("DUPLICATE_FAILURE_TEST_ID", record["invalid_reasons"])
        self.assertIn("DUPLICATE_FAILURE_DESCRIPTION", record["invalid_reasons"])
        metadata = metadata_for(report(failures=1))
        metadata["executed_test_ids"] = [metadata["executed_test_ids"][0]] * 2
        record = H._suite_record([], {}, returncode=1, stdout="", stderr=report(failures=1), elapsed_s=0.001,
                                 result_metadata=metadata)
        self.assertIn("DUPLICATE_EXECUTED_TEST_ID", record["invalid_reasons"])

    def test_missing_or_corrupt_runner_metadata_has_no_credit(self):
        for metadata in (None, {}, ["not", "object"], "metadata", 1, True,
                         dict(metadata_for(report()), schema="unknown"),
                         dict(metadata_for(report()), ran=True), dict(metadata_for(report()), events="invalid")):
            record = H._suite_record([], {}, returncode=1, stdout="", stderr=report(failures=1),
                                     elapsed_s=0.001, result_metadata=metadata)
            self.assertEqual(self.classify(record)[0], "ERROR")
            self.assertIn("MISSING_OR_INVALID_CONTROLLED_RUNNER_METADATA", record["invalid_reasons"])

    def test_assertion_metadata_requires_an_anchored_terminal_exception_line(self):
        stderr = report(failures=1).replace("AssertionError: property\n", "")
        record = suite(stderr=stderr, returncode=1)
        self.assertEqual(self.classify(record)[0], "ERROR")
        self.assertIn("FAILURE_WITHOUT_ASSERTIONERROR_TRACE", record["invalid_reasons"])

    def test_event_identity_must_match_its_description(self):
        stderr = report(failures=1)
        metadata = metadata_for(stderr)
        event = metadata["events"][0]
        event["test_id"] = event["parent_test_id"] = metadata["executed_test_ids"][1]
        record = H._suite_record([], {}, returncode=1, stdout="", stderr=stderr, elapsed_s=0.001,
                                 result_metadata=metadata)
        self.assertEqual(self.classify(record)[0], "ERROR")
        self.assertIn("OUTCOME_IDENTITY_AND_DESCRIPTION_DISAGREE", record["invalid_reasons"])


class TestHarnessExecutionControls(unittest.TestCase):
    def test_controlled_runner_records_actual_exception_identity_and_frames(self):
        with tempfile.TemporaryDirectory() as directory:
            tests = Path(directory, "tests")
            tests.mkdir()
            Path(tests, "test_fixture.py").write_text(
                'import unittest\nclass TestFixture(unittest.TestCase):\n'
                '    failureException = RuntimeError\n'
                '    def test_property(self):\n'
                '        raise RuntimeError("actual error\\nAssertionError: quoted suffix")\n')
            with mock.patch.object(H, "HERE", tests):
                record = H.run_suite({})
        self.assertIn("FAILURE_IS_NOT_ASSERTIONERROR", record["invalid_reasons"])
        event = record["controlled_runner_metadata"]["events"][0]
        self.assertEqual(event["exception_type"], "builtins.RuntimeError")
        self.assertFalse(event["is_exact_assertion_error"])
        self.assertTrue(event["traceback_frames"])

    def test_timeout_and_launch_failure_are_recorded_without_credit(self):
        for error, expected in ((subprocess.TimeoutExpired("synthetic", 1, b"partial", b"tail"), "TIMEOUT"),
                                (OSError("unavailable"), "SUBPROCESS_LAUNCH_ERROR")):
            with mock.patch.object(H.subprocess, "run", side_effect=error):
                record = H.run_suite({}, timeout_s=0.001)
            self.assertIn(expected, record["invalid_reasons"])
            self.assertFalse(H.suite_passed(record))

    def test_all_warnings_are_errors_and_raw_streams_are_preserved(self):
        completed = subprocess.CompletedProcess([], 0, "raw stdout", report())
        with mock.patch.object(H.subprocess, "run", return_value=completed) as run:
            record = H.run_suite({"LX_PLATFORM_DIR": "/synthetic/mutant"})
        args, kwargs = run.call_args
        self.assertIn("error", args[0])
        self.assertEqual(kwargs["env"]["PYTHONWARNINGS"], "error")
        self.assertEqual(kwargs["env"]["PYTHONDONTWRITEBYTECODE"], "1")
        self.assertEqual(record["stdout"], "raw stdout")
        self.assertEqual(record["stderr"], report())

    def test_mutation_anchor_and_syntax_refusals(self):
        self.assertEqual(H.apply_mutation("x = 1\n", [("absent", "x")])[2], "ANCHOR_NOT_UNIQUE")
        self.assertEqual(H.apply_mutation("x = 1\nx = 1\n", [("x = 1", "x = 2")])[2], "ANCHOR_NOT_UNIQUE")
        self.assertIn("MUTATED_SOURCE_SYNTAX_ERROR", H.apply_mutation("x = 1\n", [("x = 1", "x = (")])[2])
        self.assertEqual(H.apply_mutation("x = 1\n", [("x = 1", "x = 2")]), ("x = 2\n", [1], None))

    def main_fixture(self, baseline=None, hash_change=False):
        baseline = suite() if baseline is None else baseline
        src = H.SRC.read_text()
        hashes = H.input_hashes()
        after = dict(hashes)
        if hash_change:
            after[next(iter(after))] = "changed"
        one_mutation = ("M01", "synthetic fixture", [(src, src + "\n# synthetic copy\n")])
        with mock.patch.object(H, "validate_registry", return_value={"M01"}), \
                mock.patch.object(H, "MUTANTS", [one_mutation]), \
                mock.patch.object(H, "PROPERTY_WITNESSES", {"M01": [METHOD]}), \
                mock.patch.object(H, "expected_test_count", return_value=2), \
                mock.patch.object(H, "input_hashes", side_effect=[hashes, after]), \
                mock.patch.object(H, "run_suite", side_effect=[baseline, suite(failures=1)]) as run, \
                mock.patch.dict(os.environ, {"LX_PLATFORM_DIR": "/must-not-reach-baseline"}), \
                mock.patch("builtins.print") as printed:
            rc = H.main(None)
        return rc, json.loads(printed.call_args.args[0]), run.call_args_list

    def test_baseline_runs_first_without_inherited_mutant_directory(self):
        rc, rec, calls = self.main_fixture()
        self.assertEqual(rc, 0)
        self.assertNotIn("LX_PLATFORM_DIR", calls[0].args[0])
        self.assertIn("LX_PLATFORM_DIR", calls[1].args[0])
        self.assertEqual(rec["total"], 1)
        self.assertTrue(rec["full_registry_completed"])

    def test_baseline_failure_prevents_any_mutant_subprocess(self):
        rc, rec, calls = self.main_fixture(baseline=suite(failures=1))
        self.assertEqual(rc, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(rec["mutants"][0]["status"], "ERROR")
        self.assertEqual(rec["killed"], 0)

    def test_changed_input_hashes_fail_the_final_summary(self):
        rc, rec, _ = self.main_fixture(hash_change=True)
        self.assertEqual(rc, 1)
        self.assertFalse(rec["inputs_unchanged"])
        self.assertFalse(rec["pass"])

    def test_registry_witnesses_and_complete_input_hashes(self):
        self.assertEqual(len(H.validate_registry()), 196)
        hashes = H.input_hashes()
        for filename in ("lx_platform.py", "lx_inventory.py", "lx_verified.py", "tests/test_lx_platform.py",
                         "tests/test_sync_boundaries.py", "tests/test_lx_verified.py", "tests/test_mutation_harness.py",
                         "tests/run_mutants.py"):
            self.assertTrue(any(key.endswith("/" + filename) for key in hashes), filename)
        self.assertIn(".github/workflows/cell-308-r5-integration.yml", hashes)


if __name__ == "__main__":
    unittest.main()
