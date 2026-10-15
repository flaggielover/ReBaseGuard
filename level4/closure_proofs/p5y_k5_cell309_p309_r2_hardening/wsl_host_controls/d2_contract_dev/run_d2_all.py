"""One normal development-runner entrypoint; libraries remain free of I/O.

Run all pure D2 suites once in CPython3.11.15 and write additive external logs.
This is not a host audit, helper/service, admission command or P309 launcher.
"""
import argparse
import json
from pathlib import Path
import sys
import time
import unittest

MODULES = ('test_d2_wire', 'test_d2_model', 'test_d2_memory_dispatch',
           'test_d2_ingress', 'test_d2_complete')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, help='new external development log directory')
    args = parser.parse_args()
    if sys.implementation.name != 'cpython' or sys.version_info[:3] != (3, 11, 15):
        parser.error('this aggregate validation requires CPython3.11.15')
    destination = Path(args.output_dir).absolute()
    for parent in (destination, *destination.parents):
        if (parent / '.git').exists():
            parser.error('test logs must be outside a Git checkout')
    destination.mkdir(parents=True, exist_ok=False)
    cases = []

    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            cases.append(dict(id=test.id(), outcome='ok'))
            super().addSuccess(test)

        def addFailure(self, test, err):
            cases.append(dict(id=test.id(), outcome='failed'))
            super().addFailure(test, err)

        def addError(self, test, err):
            cases.append(dict(id=test.id(), outcome='error'))
            super().addError(test, err)

        def addSkip(self, test, reason):
            cases.append(dict(id=test.id(), outcome='skipped', reason=reason))
            super().addSkip(test, reason)

    suite = unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    started = time.monotonic()
    with (destination / 'unittest.log').open('w', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    report = dict(scope='D2_PURE_MEMORY_AGGREGATE_DEVELOPMENT_VALIDATION_ONLY',
                  modules=MODULES, sys_version=sys.version, sys_executable=sys.executable,
                  version_info=list(sys.version_info[:3]), dont_write_bytecode=sys.dont_write_bytecode,
                  tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  skipped=len(result.skipped), successful=result.wasSuccessful() and not result.skipped,
                  elapsed_seconds=time.monotonic() - started, invocations=1, test_cases=cases,
                  suite_counts={name: sum(c['id'].startswith(name + '.') for c in cases) for name in MODULES},
                  public_rsa_known_answer_cases=54, public_rsa_positive_cases=9,
                  positive_session_crypto_boundary='EXPLICIT_SYNTHETIC_MOCK; NOT_SIGNED_HOST_E2E',
                  formal_admission='BLOCKED', deployment_authorized=False,
                  execution_authorized=False, qualification_authorized=False,
                  target_execution_authorized=False)
    (destination / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'test_cases'}, indent=2))
    if not report['successful']:
        print((destination / 'unittest.log').read_text(encoding='utf-8'), file=sys.stderr)
    return 0 if report['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
