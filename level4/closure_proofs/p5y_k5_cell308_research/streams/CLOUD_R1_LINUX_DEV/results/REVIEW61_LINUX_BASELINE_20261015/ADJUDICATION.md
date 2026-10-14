# Independent Linux replay of revision 3

GitHub run: https://github.com/flaggielover/ReBaseGuard/actions/runs/38634165248
Input commit: d423c7aacc4d1cc15f3c7d77aecb5257a0175392. Control commit: fa70a59155fb685d242004671f1313e8d1c9b720.

The unmodified 75-test baseline passed on Ubuntu/Python 3.12.3 with ResourceWarning treated as an error. All input hashes remained unchanged. Complete test names, counts and stdout/stderr are preserved in validation.json.

64 mutants produced named assertion failures with the same test count and no errors. M29 produced one error, requiring separate adjudication: its full trace is exactly KeyError('launched_by_systemd') in test_launch_record_fields_are_verified. This is the required gate removed by M29. That specific error demonstrates the intended weakening, not a loader, syntax or host failure. The revised test asserts the required gate exists before indexing it, so future runs require an assertion failure rather than crediting arbitrary errors.

The independent code review also found additional defects and two new coverage gaps. Replaying the original mutation set does not establish that revision 3 is fail-closed, nor that proposed governance is accepted. This is synthetic validation only, with zero new target evaluations.
