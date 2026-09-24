#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -IS
"""C11R LAUNCHER (review 7, N7-1 and N7-2; erratum E56) -- the ONLY supported way to start a
boundary program (the runner, the comparator, the qualifier):

    level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment/code/c11r_launch.py run
    .../c11r_launch.py compare --approved-commit <full 40-hex id>
    .../c11r_launch.py qualify --approved-commit <full 40-hex id> | --self-test

WHY A LAUNCHER. Code the interpreter runs at START-UP -- a `sitecustomize` on PYTHONPATH, a user-site
`.pth` file, a forged cache of a stdlib module it loads from disk at start-up (`encodings`,
`linecache`) under PYTHONPYCACHEPREFIX -- executes before the first statement of ANY program, so no
check inside a program can stop it. Only the way the interpreter is STARTED can. This file is
executed by the kernel through its first line: the frozen interpreter, by absolute path, with
`-IS` (isolated: every PYTHON* variable ignored, no user site, the script's directory not on
sys.path; and no `site` at all). Nothing from the environment is honoured before this code runs.

WHAT IT DOES, and nothing else:
  1. checks its OWN interpreter: the frozen executable, isolated, no site, default hash-based .pyc
     checking, no pycache prefix, no warning options, no -X option but the frozen one;
  2. checks the environment it was given: any PYTHON* variable, __PYVENV_LAUNCHER__, or DYLD_* /
     LD_* (native injection) is REFUSED (their names are printed, never their values);
  3. builds the child's environment EXPLICITLY -- the frozen allowlist, PATH set to FROZEN_PATH --
     never inheriting the rest;
  4. only then replaces itself (execve) with the frozen interpreter running the boundary program
     under CHILD_FLAGS; the program's own pre-import barrier re-checks all of it before its first
     import.
It imports `os` and `sys` (loaded by the interpreter before this file) and `_imp` (built in, found
by the built-in importer before any path): no import can be redirected. It reads no data.

NOT COVERED, stated: native code injected into the interpreter by the dynamic linker before
Python starts (DYLD_* is refused here, but it has already acted in THIS process), a replaced
interpreter binary or standard library (the host), and starting a boundary program some other
way: a direct start is refused by the program's barrier, but whatever the interpreter executed at
its own start-up has then already run.
"""
import os
import sys
import _imp

FROZEN_INTERPRETER = "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
FROZEN_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
CHILD_FLAGS = ("-I", "-S", "-B", "--check-hash-based-pycs", "default",
               "-X", "int_max_str_digits=0")
ALLOWED_XOPTIONS = {"int_max_str_digits": "0"}
# the child's ENTIRE environment: these names only (PATH frozen); the platform itself adds
# __CF_USER_TEXT_ENCODING, and CPython's locale coercion may add LC_CTYPE
ENV_ALLOWED = ("HOME", "LANG", "LC_ALL", "LC_CTYPE", "LOGNAME", "PATH", "TMPDIR", "USER",
               "__CF_USER_TEXT_ENCODING")
ENV_REFUSED_PREFIXES = ("PYTHON", "__PYVENV_LAUNCHER__", "DYLD_", "LD_")
PROGRAMS = {"run": "c11r_runs.py", "compare": "c11r_compare.py", "qualify": "c11r_qualify.py"}


def interpreter_problems(flags, hash_mode, pycache_prefix, xoptions, warnoptions,
                         executable) -> list:
    """The frozen interpreter policy, as a pure function of what the running interpreter reports
    (sys.flags, _imp.check_hash_based_pycs, sys.pycache_prefix, sys._xoptions, sys.warnoptions,
    sys.executable)."""
    p = []
    if not (flags.isolated and flags.ignore_environment and flags.no_user_site
            and flags.safe_path and flags.no_site):
        p.append("the interpreter was not started isolated and without site (-I -S)")
    if flags.optimize:
        p.append("assertions are stripped (-O)")
    if hash_mode != "default":
        p.append(f"the hash-based .pyc policy is {hash_mode!r}, not 'default' (review 7, N7-1)")
    if pycache_prefix is not None:
        p.append("a pycache prefix is set")
    if dict(xoptions) != ALLOWED_XOPTIONS and dict(xoptions):
        p.append(f"-X options {sorted(xoptions)} are not the frozen ones")
    if warnoptions:
        p.append("warning options are set")
    if os.path.realpath(executable or "") != os.path.realpath(FROZEN_INTERPRETER):
        p.append("the interpreter is not the frozen one")
    return p


def environment_problems(environ) -> list:
    """What the LAUNCHER refuses in the environment it was given (names only)."""
    bad = sorted(k for k in environ if k.startswith(ENV_REFUSED_PREFIXES))
    return [f"the environment carries {bad}: refused (review 7, N7-2)"] if bad else []


def child_env(environ) -> dict:
    """The child's environment, built EXPLICITLY: the allowlist, PATH frozen."""
    env = {k: environ[k] for k in ENV_ALLOWED if k in environ and k != "PATH"}
    env["PATH"] = FROZEN_PATH
    return env


def child_argv(program: str, args=()) -> list:
    """The exact interpreter invocation of a campaign program."""
    return [FROZEN_INTERPRETER, *CHILD_FLAGS, str(program), *args]


def main(argv) -> int:
    p = interpreter_problems(sys.flags, _imp.check_hash_based_pycs, sys.pycache_prefix,
                             sys._xoptions, sys.warnoptions, sys.executable)
    p += environment_problems(os.environ)
    if len(argv) < 2 or argv[1] not in PROGRAMS:
        p.append(f"usage: c11r_launch.py {'|'.join(PROGRAMS)} [arguments]")
    if p:
        sys.stderr.write("REFUSE (launcher): " + "; ".join(p) + "\n")
        return 2
    program = os.path.join(os.path.dirname(os.path.realpath(__file__)), PROGRAMS[argv[1]])
    if os.path.islink(program) or not os.path.isfile(program):
        sys.stderr.write("REFUSE (launcher): the boundary program is not a regular file\n")
        return 2
    sys.stdout.flush()
    os.execve(FROZEN_INTERPRETER, child_argv(program, argv[2:]), child_env(os.environ))
    return 2                                              # not reached


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
