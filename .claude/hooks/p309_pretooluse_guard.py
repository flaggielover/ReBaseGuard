#!/usr/bin/env python3
"""PreToolUse guard for the P309 Q11 recovery session (enforcement; CLAUDE.md is not relied upon).

Reads the hook JSON on stdin.  Exit 0 lets the call go on to the normal permission flow; exit 2 refuses it (the
reason goes to stderr, which the harness shows to the model).  ANY internal error refuses (fail closed).
Every decision is appended to the session's audit log (.claude/audit/<session>.jsonl).

Refused:
  R1 target evaluation: the frozen drivers' execute / seal-only / validate-grant modes, the official qualification
     runner and launcher, the grant-proposal tool, the host and drill tools, the checkpoint pusher, inline code that
     calls a target-reaching function, and executing another cell's (306-308) campaign code;
  R2 grant / adoption / status / r5 / r6 mutation and any exactly-once / production ref;
  R3 force push, push of anything but the one allowed branch to origin, push to main, reset --hard, destructive
     clean, rebase / merge / filter / amend / branch deletion and other history rewriting;
  R4 AWS, Vultr, SSH and other remote or paid compute;
  R5 writes into the repository outside the declared write-set (every live evidence namespace is outside it), and
     commits whose staged paths leave the write-set or that are not on the allowed branch.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p309_guard_policy as P  # noqa: E402


class Refuse(Exception):
    def __init__(self, rule: str, why: str):
        super().__init__(f"{rule}: {why}")
        self.rule, self.why = rule, why


# ------------------------------------------------------------------------------------------------ helpers
def _sha_file(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return "missing"


def policy_hash() -> str:
    h = hashlib.sha256()
    for name in ("p309_guard_policy.py", "p309_pretooluse_guard.py"):
        h.update(_sha_file(P.HOOK_DIR / name).encode())
    return h.hexdigest()


def rel_in_repo(path: str, cwd: str | None) -> str | None:
    """repository-relative path of `path` if it lies in the repository, else None"""
    if not path:
        return None
    p = os.path.expanduser(os.path.expandvars(path))
    base = Path(cwd) if cwd else P.repo_root()
    q = Path(p) if os.path.isabs(p) else base / p
    try:
        q = Path(os.path.normpath(str(q)))
        root = P.repo_root()
        if q == root:
            return "."
        return str(q.relative_to(root))
    except ValueError:
        return None


def in_write_set(rel: str) -> bool:
    rel = rel.replace(os.sep, "/")
    if rel == ".":
        return False
    for a in P.WRITE_ALLOW:
        if a.endswith("/"):
            if rel == a.rstrip("/") or rel.startswith(a):
                return True
        elif rel == a:
            return True
    return False


def check_write_path(path: str, cwd: str | None, how: str) -> None:
    if P.PRIVATE_HOME_RE.search(path):
        raise Refuse("R4_REMOTE", f"{how} into a credential directory: {path}")
    rel = rel_in_repo(path, cwd)
    if rel is None:
        return                                      # outside the repository (scratchpad, /tmp): not live evidence
    if rel == ".git" or rel.startswith(".git/"):
        raise Refuse("R3_HISTORY", f"{how} inside .git: {path}")
    if not in_write_set(rel):
        raise Refuse("R5_PROTECTED_WRITE", f"{how} outside the declared write-set: {rel}")


def git_out(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(P.repo_root()), *args], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise Refuse("GUARD_GIT", f"git {' '.join(args[:2])} failed: {r.stderr.strip()[:200]}")
    return r.stdout


# ------------------------------------------------------------------------------------------- shell parsing
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def split_heredocs(cmd: str) -> tuple[str, list[tuple[str, str]]]:
    """remove heredoc bodies; return (command text without bodies, [(line that opened it, body)])"""
    lines = cmd.split("\n")
    out, bodies, i = [], [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        tags = [m.group(2) for m in HEREDOC_RE.finditer(line)]
        i += 1
        for tag in tags:
            body = []
            while i < len(lines) and lines[i].strip() != tag:
                body.append(lines[i])
                i += 1
            i += 1                                   # the terminator
            bodies.append((line, "\n".join(body)))
    return "\n".join(out), bodies


SEP = {";", "&&", "||", "|", "&", "\n", "(", ")", "|&", ";;"}


def unquoted_newlines_to_semicolons(text: str) -> str:
    """a newline separates commands only outside quotes (a multi-line quoted argument stays one argument)"""
    out, q, esc = [], None, False
    for ch in text:
        if esc:
            out.append(ch)
            esc = False
            continue
        if ch == "\\" and q != "'":
            esc = True
        elif q:
            if ch == q:
                q = None
        elif ch in ("'", '"'):
            q = ch
        elif ch == "\n":
            out.append(" ; ")
            continue
        out.append(ch)
    return "".join(out)


FD_DUP_RE = re.compile(r"(?<![\w/])\d*[<>]&(?:\d+|-)")
REDIR_TOKEN_RE = re.compile(r"^(\d*>>?|\d*<<?<?)(.*)$")


def segments_with_redirects(text: str) -> list[tuple[list[str], list[str]]]:
    """simple commands as (argv, output-redirect targets): shell operators split, fd duplications (2>&1) dropped,
    redirections removed from argv; command substitutions are scanned as commands too"""
    extra = re.findall(r"\$\(([^()]*)\)", text) + re.findall(r"`([^`]*)`", text)
    out = []
    for chunk in [text] + extra:
        chunk = FD_DUP_RE.sub(" ", unquoted_newlines_to_semicolons(chunk)).replace("&>", ">")
        lex = shlex.shlex(chunk, posix=True, punctuation_chars=";&|()")
        lex.whitespace_split = True
        lex.commenters = ""
        try:
            toks = list(lex)
        except ValueError as exc:
            raise Refuse("GUARD_PARSE", f"the command cannot be parsed safely ({exc})") from None
        cur: list[str] = []
        red: list[str] = []
        pending = None
        for t in toks:
            if t in SEP or set(t) <= set(";&|()"):
                if cur or red:
                    out.append((cur, red))
                cur, red, pending = [], [], None
                continue
            if pending is not None:
                if ">" in pending:
                    red.append(t)
                pending = None
                continue
            m = REDIR_TOKEN_RE.match(t)
            if m:
                op, rest = m.group(1), m.group(2)
                if rest:
                    if ">" in op:
                        red.append(rest)
                else:
                    pending = op
                continue
            cur.append(t)
        if cur or red:
            out.append((cur, red))
    return out


def segments(text: str) -> list[list[str]]:
    return [argv for argv, _ in segments_with_redirects(text)]


ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
WRAPPERS = {"sudo", "env", "nohup", "timeout", "nice", "ionice", "stdbuf", "setsid", "time", "command", "exec",
            "xargs", "watch", "chronic", "unbuffer", "caffeinate", "flock"}


def strip_prefix(seg: list[str]) -> list[str]:
    """drop env assignments and wrapper programs (with their options) so seg[0] is the real program"""
    s = list(seg)
    with_value = {"timeout": {"-s", "--signal", "-k", "--kill-after"}, "nice": {"-n", "--adjustment"},
                  "ionice": {"-c", "-n", "-p"}, "flock": {"-w", "--timeout", "-E"}, "stdbuf": {"-i", "-o", "-e"},
                  "env": {"-u", "--unset", "-C", "--chdir", "-S"}, "xargs": {"-n", "-P", "-I", "-L", "-d", "-a"},
                  "sudo": {"-u", "-g", "-C", "-D"}, "watch": {"-n", "-d"}}
    while s:
        if ENV_ASSIGN.match(s[0]):
            s.pop(0)
            continue
        w = os.path.basename(s[0])
        if w not in WRAPPERS:
            break
        s.pop(0)
        while s and s[0].startswith("-") and s[0] != "--":
            opt = s.pop(0)
            if opt in with_value.get(w, ()) and s:
                s.pop(0)
        if s and s[0] == "--":
            s.pop(0)
        if w == "timeout" and s and re.match(r"^\d", s[0]):
            s.pop(0)
        if w == "flock" and s:
            s.pop(0)                                    # the lock file or descriptor
    return s


REDIR_RE = re.compile(r"(?:^|[^0-9&<>])(?:[0-9]?>>?|&>>?)\s*([^\s;&|<>()]+)")


def redirect_targets(text: str) -> list[str]:
    out = []
    for m in REDIR_RE.finditer(text):
        t = m.group(1).strip("'\"")
        if t.startswith("&") or t in ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty"):
            continue
        out.append(t)
    return out


# --------------------------------------------------------------------------------------------- the rules
CODE_DANGER_RE = re.compile(
    r"push[^\n]{0,80}?(?:--force|--mirror|--delete|\s-f\b|\s\+\S)|reset[^\n]{0,40}--hard|"
    r"clean[^\n]{0,20}\s-[a-zA-Z]*f|filter-branch|rebase\b|commit[^\n]{0,40}--amend|update-ref|"
    r"[\"'](?:aws|ssh|scp|sftp|vultr|vultr-cli|gcloud|systemd-run|rsync)[\"']")


def scan_code(code: str, where: str) -> None:
    """code handed to an interpreter (python -c, heredoc to python/bash, ...)"""
    m = CODE_DANGER_RE.search(code)
    if m:
        raise Refuse("R3_HISTORY" if "aws" not in m.group(0) and "ssh" not in m.group(0) else "R4_REMOTE",
                     f"{where} contains a refused git / remote operation ({m.group(0)[:60]})")
    if P.TARGET_CALL_RE.search(code):
        raise Refuse("R1_TARGET_EVAL", f"{where} calls a target-reaching function "
                                       f"({P.TARGET_CALL_RE.search(code).group(0)})")
    if P.TARGET_MODE_RE.search(code):
        raise Refuse("R1_TARGET_EVAL", f"{where} invokes a driver target / grant mode")
    if P.TARGET_TOOL_RE.search(code):
        raise Refuse("R1_TARGET_EVAL", f"{where} invokes a refused campaign tool ({P.TARGET_TOOL_RE.search(code).group(0)})")
    if P.REMOTE_TEXT_RE.search(code):
        raise Refuse("R4_REMOTE", f"{where} references remote compute ({P.REMOTE_TEXT_RE.search(code).group(0)})")
    if P.GRANT_RE.search(code) and re.search(r"\b(open|write|mkdir|rename|replace|unlink|symlink|update-ref|"
                                             r"update_ref|write_text|write_bytes)\b", code):
        raise Refuse("R2_GRANT", f"{where} may write a grant / exactly-once / result object")
    if P.PROTECTED_REF_RE.search(code) and re.search(r"update-ref|update_ref|\btag\b|\bpush\b", code):
        raise Refuse("R2_GRANT", f"{where} may create or move a protected ref")


def check_git(argv: list[str], cwd: str | None, raw: str) -> None:
    i, git_c = 1, None
    while i < len(argv) and argv[i].startswith("-"):
        if argv[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path") and i + 1 < len(argv):
            if argv[i] == "-C":
                git_c = argv[i + 1]
            if argv[i] == "-c" and re.search(r"(alias|hook|sshcommand|core\.hookspath|url\.)", argv[i + 1], re.I):
                raise Refuse("R3_HISTORY", f"git -c {argv[i + 1]} (alias / hook / ssh / url rewrite)")
            i += 2
        else:
            if argv[i].startswith(("--git-dir=", "--work-tree=")):
                raise Refuse("R3_HISTORY", "git with an explicit --git-dir / --work-tree")
            i += 1
    if i >= len(argv):
        return
    sub, rest = argv[i], argv[i + 1:]
    where = git_c if git_c else cwd
    target_repo = rel_in_repo(git_c, cwd) if git_c else rel_in_repo(cwd or ".", None)
    in_main_repo = target_repo is not None
    joined = " ".join(rest)
    if P.PROTECTED_REF_RE.search(joined) and sub not in ("log", "show", "for-each-ref", "rev-parse", "ls-remote",
                                                         "cat-file", "rev-list", "diff", "show-ref", "grep"):
        raise Refuse("R2_GRANT", f"git {sub} on a protected (exactly-once / production / test) ref")
    if sub in P.GIT_ALWAYS_BLOCK:
        if sub == "reflog" and (not rest or rest[0] in ("show", "list")):
            return
        if sub == "remote" and (not rest or rest[0] in ("-v", "show", "get-url")):
            return
        if sub == "worktree" and rest and rest[0] == "list":
            return
        raise Refuse("R3_HISTORY", f"git {sub} (history rewrite, merge, ref surgery or remote change) is refused")
    if sub == "push":
        flags = [a for a in rest if a.startswith("-")]
        bad = [f for f in flags if f.split("=")[0] in P.FORCE_PUSH_FLAGS]
        if bad:
            raise Refuse("R3_FORCE_PUSH", f"git push {' '.join(bad)} is refused")
        allowed_flags = {"-u", "--set-upstream", "--porcelain", "-q", "--quiet", "-v", "--verbose", "--dry-run", "-n"}
        other = [f for f in flags if f not in allowed_flags]
        if other:
            raise Refuse("R3_FORCE_PUSH", f"git push with unreviewed flags {other}")
        pos = [a for a in rest if not a.startswith("-")]
        if len(pos) != 2 or pos[0] != P.ALLOWED_REMOTE:
            raise Refuse("R3_PUSH_TARGET", f"push only as `git push -u {P.ALLOWED_REMOTE} {P.ALLOWED_BRANCH}`")
        spec = pos[1]
        ok = {P.ALLOWED_BRANCH, f"{P.ALLOWED_BRANCH}:{P.ALLOWED_BRANCH}",
              f"HEAD:refs/heads/{P.ALLOWED_BRANCH}", f"refs/heads/{P.ALLOWED_BRANCH}"}
        if spec not in ok:
            raise Refuse("R3_PUSH_TARGET", f"refspec {spec!r} is not the allowed branch {P.ALLOWED_BRANCH}")
        if not in_main_repo:
            raise Refuse("R3_PUSH_TARGET", "push only from the session repository")
        return
    if sub == "reset":
        if any(a in ("--hard", "--merge", "--keep") for a in rest):
            raise Refuse("R3_RESET_HARD", f"git reset {joined}")
        if in_main_repo and [a for a in rest if not a.startswith("-") and a != "--"]:
            raise Refuse("R3_HISTORY", "git reset that moves HEAD or touches paths in the session repository")
        return
    if sub == "clean":
        if any(re.match(r"^-[a-zA-Z]*[fxXd]", a) or a in ("--force",) for a in rest):
            raise Refuse("R3_CLEAN", f"destructive git clean {joined}")
        return
    if sub == "branch":
        if any(a in ("-D", "-d", "--delete", "-f", "--force", "-M", "-m", "--move", "-C", "-c", "--copy",
                     "-u", "--set-upstream-to", "--unset-upstream") for a in rest):
            raise Refuse("R3_HISTORY", f"git branch {joined}")
        if [a for a in rest if not a.startswith("-")] and in_main_repo:
            raise Refuse("R3_HISTORY", "creating extra branches in the session repository is refused")
        return
    if sub in ("checkout", "switch", "restore", "stash"):
        if not in_main_repo:
            return
        if sub == "stash" and rest and rest[0] in ("drop", "clear", "pop"):
            raise Refuse("R3_HISTORY", f"git stash {rest[0]}")
        if sub in ("checkout", "switch"):
            # the one admitted branch creation: the task branch, from r2's exact head, never from anything else
            if [a for a in rest if a not in ("-q", "--quiet")] in (["-b", P.ALLOWED_BRANCH, P.R2_HEAD],
                                                                  ["-c", P.ALLOWED_BRANCH, P.R2_HEAD]):
                if subprocess.run(["git", "-C", str(P.repo_root()), "rev-parse", "-q", "--verify",
                                   "refs/heads/" + P.ALLOWED_BRANCH], capture_output=True).returncode == 0:
                    raise Refuse("R3_HISTORY", f"{P.ALLOWED_BRANCH} already exists; it is created only once")
                return
            if any(a in ("-B", "-C", "-f", "--force", "--orphan", "--discard-changes", "--detach", "-b", "-c")
                   for a in rest):
                raise Refuse("R3_HISTORY", f"git {sub} {joined}")
            pos = [a for a in rest if not a.startswith("-")]
            if "--" in rest or (pos and pos[0] != P.ALLOWED_BRANCH):
                raise Refuse("R3_HISTORY", f"git {sub} away from {P.ALLOWED_BRANCH} or over working-tree paths")
            return
        if sub == "restore":
            for a in rest:
                if not a.startswith("-"):
                    check_write_path(a, git_c or cwd, "git restore")
        return
    if sub in ("tag",):
        if [a for a in rest if not a.startswith("-")] or any(a in ("-d", "-f", "-a", "-s") for a in rest):
            raise Refuse("R3_HISTORY", "creating, moving or deleting tags is refused")
        return
    if sub in ("gc", "repack", "fsck") and any("prune" in a for a in rest):
        raise Refuse("R3_HISTORY", f"git {sub} with pruning")
    if sub in ("apply", "mv", "rm"):
        for a in rest:
            if not a.startswith("-"):
                if sub == "apply":
                    continue
                check_write_path(a, git_c or cwd, f"git {sub}")
        if sub == "apply" and "--check" not in rest and "--stat" not in rest and in_main_repo:
            raise Refuse("R5_PROTECTED_WRITE", "git apply in the session repository (write with the Edit tool)")
        return
    if sub == "commit":
        if not in_main_repo:
            return                                  # scratch clones and sandboxes: never pushed by this session
        if any(a in ("--amend", "--no-verify", "-n", "--fixup", "--squash", "--allow-empty") or
               a.startswith(("--fixup=", "--squash=", "--reuse-message", "-C", "-c")) for a in rest):
            raise Refuse("R3_HISTORY", f"git commit {joined}")
        branch = git_out("symbolic-ref", "-q", "--short", "HEAD").strip()
        if branch != P.ALLOWED_BRANCH:
            raise Refuse("R3_PUSH_TARGET", f"commit only on {P.ALLOWED_BRANCH} (HEAD is on {branch or 'detached'})")
        staged = git_out("diff", "--cached", "--name-only", "-z").split("\0")
        if any(a in ("-a", "--all") or re.match(r"^-[a-zA-Z]*a", a) for a in rest):
            staged += git_out("diff", "--name-only", "-z").split("\0")
        pathspec = [a for a in rest if not a.startswith("-")]
        if "--" in rest or "-o" in rest or "--only" in rest or "-i" in rest:
            staged += pathspec
        bad = sorted({s for s in staged if s and not in_write_set(s)})
        if bad:
            raise Refuse("R5_PROTECTED_WRITE", f"the commit would touch protected paths: {bad[:5]}")
        return
    if sub == "config" and in_main_repo and not any(a in ("--get", "--list", "-l", "--get-all", "--get-regexp")
                                                    for a in rest):
        raise Refuse("R3_HISTORY", "changing git configuration of the session repository")
    if sub in ("fetch",) and any(a.startswith("+") or ":" in a for a in rest if not a.startswith("-")):
        raise Refuse("R3_HISTORY", "git fetch with a refspec that writes local refs")
    if sub == "clone" and any(P.REMOTE_TEXT_RE.search(a) for a in rest):
        raise Refuse("R4_REMOTE", "clone over ssh")


READ_ONLY = {"grep", "rg", "egrep", "fgrep", "cat", "less", "more", "head", "tail", "ls", "wc", "sha256sum",
             "md5sum", "diff", "cmp", "file", "stat", "find", "echo", "printf", "jq", "sort", "uniq", "cut", "awk",
             "tr", "column", "nl", "true", "false", "test", "["}


def check_segment(seg: list[str], cwd: str | None, raw: str) -> None:
    s = strip_prefix(seg)
    if not s:
        return
    prog = os.path.basename(s[0])
    if prog in P.REMOTE_CMDS:
        raise Refuse("R4_REMOTE", f"`{prog}` (remote / paid compute) is refused")
    if prog == "rsync" and any(re.match(r"^[^/\s]+:", a) for a in s[1:]):
        raise Refuse("R4_REMOTE", "rsync to a remote host")
    if prog in ("curl", "wget", "http", "nc", "ncat", "socat", "telnet") and P.REMOTE_TEXT_RE.search(" ".join(s)):
        raise Refuse("R4_REMOTE", f"{prog} to a cloud / remote-compute endpoint")
    if prog == "git":
        check_git(s, cwd, raw)
        return
    text = " ".join(s)
    if prog not in READ_ONLY and P.REMOTE_TEXT_RE.search(" ".join(seg)):
        raise Refuse("R4_REMOTE", f"remote-compute identifier in `{prog}` ({P.REMOTE_TEXT_RE.search(' '.join(seg)).group(0)})")
    if P.TARGET_MODE_RE.search(text):
        raise Refuse("R1_TARGET_EVAL", "a driver target / grant mode (execute, seal-only, validate-grant)")
    if P.INTERPRETERS.match(prog):
        args = s[1:]
        scripts = [a for a in args if not a.startswith("-")]
        for a in scripts[:1]:
            if P.TARGET_TOOL_RE.search(a):
                raise Refuse("R1_TARGET_EVAL", f"running {os.path.basename(a)} is refused in this session")
            if P.OTHER_CELL_RE.search(a):
                raise Refuse("R1_OTHER_CELL", f"executing another cell's campaign code: {a}")
        if "-c" in args:
            code = args[args.index("-c") + 1] if args.index("-c") + 1 < len(args) else ""
            scan_code(code, f"{prog} -c")
        if "-m" in args:
            mod = args[args.index("-m") + 1] if args.index("-m") + 1 < len(args) else ""
            if P.TARGET_TOOL_RE.search(mod) or re.search(r"p309_driver", mod):
                raise Refuse("R1_TARGET_EVAL", f"{prog} -m {mod}")
    elif P.TARGET_TOOL_RE.search(s[0]):
        raise Refuse("R1_TARGET_EVAL", f"running {prog} is refused in this session")
    elif P.OTHER_CELL_RE.search(s[0]):
        raise Refuse("R1_OTHER_CELL", f"executing another cell's campaign code: {s[0]}")
    if prog == "find" and any(a in ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls")
                              for a in s[1:]):
        roots = []
        for a in s[1:]:
            if a.startswith("-") or a in ("(", "!"):
                break
            roots.append(a)
        for pth in roots or ["."]:
            check_write_path(pth, cwd, "find -delete / -exec")
    # write-type commands: path arguments inside the repository must be in the write-set
    if prog in P.WRITE_CMDS or (prog == "sed" and any(a.startswith("-i") or a == "--in-place" for a in s[1:])):
        if prog == "sed" and not any(a.startswith("-i") or a.startswith("--in-place") for a in s[1:]):
            return
        if prog == "tar" and not any(re.match(r"^-?[a-zA-Z]*x", a) for a in s[1:2]):
            return
        if prog == "perl" and not any(a.startswith("-i") for a in s[1:]):
            return
        paths = [a for a in s[1:] if not a.startswith("-")]
        if prog == "dd":
            paths = [a[3:] for a in s[1:] if a.startswith("of=")]
        if prog in ("tar", "unzip"):
            cdir = [s[k + 1] for k, a in enumerate(s[:-1]) if a in ("-C", "-d", "--directory")]
            paths = cdir or ["."]
        if prog == "sed":
            paths = paths[1:] if not any(a in ("-e", "-f") for a in s[1:]) else paths
        for pth in paths:
            if P.GRANT_RE.search(pth) or P.R5R6_RE.search(pth) or P.ADOPT_RE.search(pth):
                raise Refuse("R2_GRANT", f"{prog} on a grant / adoption / result / r5 / r6 path: {pth}")
            check_write_path(pth, cwd, prog)


SHELLS = re.compile(r"^(?:bash|sh|zsh|dash|ksh)$")


def check_bash(cmd: str, cwd: str | None, depth: int = 0) -> None:
    if depth > 4:
        raise Refuse("GUARD_PARSE", "nested shell code too deep")
    if P.CANARY in cmd:
        raise Refuse("CANARY", "the live guard canary (this refusal proves the PreToolUse hook is active)")
    head, bodies = split_heredocs(cmd)
    for opener, body in bodies:
        pre = opener.split("<<")[0]
        segs = segments(pre)
        first = strip_prefix(segs[-1]) if segs else []
        prog = os.path.basename(first[0]) if first else ""
        if SHELLS.match(prog) or prog in ("source", ".", "eval"):
            check_bash(body, cwd, depth + 1)
        elif P.INTERPRETERS.match(prog) or prog == "xargs":
            scan_code(body, f"heredoc to {prog}")
    if P.PRIVATE_HOME_RE.search(head):
        raise Refuse("R4_REMOTE", "access to a credential directory (.aws / .ssh / gcloud / vultr)")
    eff = cwd
    for seg, reds in segments_with_redirects(head):
        s = strip_prefix(seg)
        if s and s[0] in ("cd", "pushd"):
            dest = next((a for a in s[1:] if not a.startswith("-")), os.path.expanduser("~"))
            dest = os.path.expanduser(os.path.expandvars(dest))
            eff = os.path.normpath(dest if os.path.isabs(dest) else os.path.join(eff or str(P.repo_root()), dest))
            continue
        for t in [r for r in reds if r not in ("/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty")]:
            if P.GRANT_RE.search(t) or P.R5R6_RE.search(t):
                raise Refuse("R2_GRANT", f"redirect into a grant / result / r5 / r6 path: {t}")
            check_write_path(t, eff, "shell redirect")
        if s and (SHELLS.match(os.path.basename(s[0])) and "-c" in s):
            k = s.index("-c")
            check_bash(s[k + 1] if k + 1 < len(s) else "", eff, depth + 1)
            continue
        if s and s[0] == "eval":
            check_bash(" ".join(s[1:]), eff, depth + 1)
            continue
        check_segment(seg, eff, cmd)
    # redirects that shlex folded into tokens (e.g. `echo x>file`) are caught on the raw text as well
    for t in redirect_targets(head):
        if P.GRANT_RE.search(t) or P.R5R6_RE.search(t):
            raise Refuse("R2_GRANT", f"redirect into a grant / result / r5 / r6 path: {t}")
        if os.path.isabs(os.path.expanduser(t)):
            check_write_path(t, cwd, "shell redirect")


def check_file_tool(tool: str, ti: dict, cwd: str | None) -> None:
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    if P.GRANT_RE.search(path) or P.R5R6_RE.search(path) or P.ADOPT_RE.search(path):
        raise Refuse("R2_GRANT", f"{tool} on a grant / adoption / result / r5 / r6 path: {path}")
    if re.search(r"(?:^|/)\.claude/settings(?:\.local)?\.json$", path) or path.endswith("/.claude.json"):
        content = json.dumps(ti)
        if "disableAllHooks" in content:
            raise Refuse("R5_PROTECTED_WRITE", "disabling hooks is refused")
    home_settings = os.path.expanduser("~/.claude/")
    if os.path.abspath(os.path.expanduser(path)).startswith(home_settings):
        raise Refuse("R5_PROTECTED_WRITE", "user-level Claude settings are outside this session's write-set")
    check_write_path(path, cwd, tool)
    rel = rel_in_repo(path, cwd) or ""
    if path.endswith((".py", ".sh", ".bash")) and not rel.startswith(P.CONTENT_SCAN_EXEMPT):
        body = ti.get("content") or ti.get("new_string") or ti.get("new_source") or ""
        for e in ti.get("edits") or []:
            body += "\n" + str(e.get("new_string", ""))
        m = re.search(P.TARGET_CALL_RE.pattern + r"\s*\(", body)
        if m:
            raise Refuse("R1_TARGET_EVAL", f"code that calls a target-reaching function ({m.group(0)})")
        if P.REMOTE_TEXT_RE.search(body):
            raise Refuse("R4_REMOTE", f"code that references remote compute ({P.REMOTE_TEXT_RE.search(body).group(0)})")


REFUSED_TOOLS = re.compile(
    r"^mcp__github__(?:push_files|create_or_update_file|delete_file|merge_pull_request|create_pull_request|"
    r"create_branch|update_pull_request_branch|enable_pr_auto_merge|fork_repository|create_repository|"
    r"actions_run_trigger|update_pull_request)$|"
    r"^mcp__claude-code-remote__(?:create_session|send_message|create_trigger|fire_trigger|update_trigger|"
    r"archive_session|unarchive_session|interrupt_session)$")


def decide(event: dict) -> None:
    tool = event.get("tool_name", "")
    ti = event.get("tool_input") or {}
    cwd = event.get("cwd")
    if REFUSED_TOOLS.match(tool):
        if tool.startswith("mcp__claude-code-remote__"):
            raise Refuse("R4_REMOTE", f"{tool} starts or steers other (remote) compute; refused")
        raise Refuse("R3_PUSH_TARGET", f"{tool} writes to GitHub outside the one allowed branch push; refused")
    if tool == "Bash":
        check_bash(str(ti.get("command", "")), cwd)
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        check_file_tool(tool, ti, cwd)


def log(event: dict, decision: str, rule: str, why: str) -> None:
    try:
        d = P.audit_dir()
        d.mkdir(parents=True, exist_ok=True)
        ti = event.get("tool_input") or {}
        rec = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
               "hook": "PreToolUse", "session_id": event.get("session_id"), "tool": event.get("tool_name"),
               "decision": decision, "rule": rule, "why": why[:400], "policy_sha256": policy_hash(),
               "command": str(ti.get("command", ""))[:4000] if "command" in ti else None,
               "file_path": ti.get("file_path") or ti.get("notebook_path"), "cwd": event.get("cwd")}
        name = f"{event.get('session_id') or 'nosession'}.jsonl"
        with open(d / name, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    except Exception:  # noqa: BLE001 - logging never turns a refusal into an allowance
        if decision == "allow":
            raise


def main() -> int:
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        print("P309 GUARD REFUSED: unreadable hook input (fail closed)", file=sys.stderr)
        return 2
    try:
        decide(event)
    except Refuse as r:
        log(event, "deny", r.rule, r.why)
        print(f"P309 GUARD REFUSED [{r.rule}]: {r.why}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - fail closed
        log(event, "deny", "GUARD_ERROR", f"{type(exc).__name__}: {exc}")
        print(f"P309 GUARD REFUSED [GUARD_ERROR]: {type(exc).__name__}: {exc} (fail closed)", file=sys.stderr)
        return 2
    try:
        log(event, "allow", "-", "")
    except Exception as exc:  # noqa: BLE001 - an unlogged allowance is not allowed
        print(f"P309 GUARD REFUSED [AUDIT_LOG]: cannot record the decision ({exc}); fail closed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
