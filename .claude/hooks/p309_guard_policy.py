"""Policy constants for the P309 Q11 recovery session guard (shared by the PreToolUse guard, the PostToolUse
tripwire and the SessionEnd audit).  Stdlib only.  Changing this file changes the enforced policy; its sha256 is
recorded in every audit line, so a change is visible after the fact."""
from __future__ import annotations

import os
import re
from pathlib import Path

HOOK_DIR = Path(__file__).resolve().parent
DEFAULT_REPO = HOOK_DIR.parents[1]


def repo_root() -> Path:
    """the repository under guard: P309_GUARD_REPO (tests only), else CLAUDE_PROJECT_DIR, else this file's repo"""
    for k in ("P309_GUARD_REPO", "CLAUDE_PROJECT_DIR"):
        v = os.environ.get(k)
        if v:
            return Path(v).resolve()
    return DEFAULT_REPO


def audit_dir() -> Path:
    v = os.environ.get("P309_GUARD_AUDIT_DIR")
    return Path(v) if v else repo_root() / ".claude" / "audit"


# the only branch this session may commit to or push
ALLOWED_BRANCH = "claude/p309-q11-recovery-20261005"
ALLOWED_REMOTE = "origin"
BASE_COMMIT = "c902fe2fe33003ac7e4e61f29c10c81682fc940c"      # r1 HEAD at session start (the branch point)

# the write-set: repository-relative prefixes this session may create or change.  Everything else in the repository
# (every live evidence namespace, the r1 and r2 campaigns, cells 306-308, r5, status documents) is protected.
NEW_NS = "level4/closure_proofs/p5y_k5_cell309_q11_recovery/"
WRITE_ALLOW = (NEW_NS, ".claude/hooks/", ".claude/settings.json", ".claude/audit/", ".claude/.gitignore")
# files under these prefixes may name prohibited identifiers as data (the guard's own rules and test vectors)
CONTENT_SCAN_EXEMPT = (".claude/hooks/",)

# --------------------------------------------------------------------------------------------------- patterns
# (1) target evaluation: the frozen drivers' target / grant modes and the functions that reach target inputs
TARGET_MODE_RE = re.compile(
    r"p309_driver(?:\.py)?\b[^\n;|&]*?\s(?:execute|seal-only|validate-grant)\b", re.I)
TARGET_CALL_RE = re.compile(
    r"\b(?:run_execute|evaluate_target|run_seal_only|cell_inputs|historical_control|after_marker|_arm_marker|"
    r"_persist_pending|persist_emergency|premarker_admission|check_grant|validate_grant)\b")
TARGET_TOOL_RE = re.compile(
    r"\b(?:p309_launch|p309_qualify|make_proposed_authorization|p309_postexec|p309_host|p309_topology_drill|"
    r"checkpoint_push_p309)(?:\.py)?\b", re.I)
# other cells' campaigns: executing anything from them is refused (reading with git show/log/cat is not execution)
OTHER_CELL_RE = re.compile(
    r"(?:p5y_k5_cell30[678]|cell[_-]?30[678]\b|rlr307|mbs308|streams/C_30[678]|C_30[678]/)", re.I)

# (2) grant / adoption / status / r5 / r6 / exactly-once refs
GRANT_RE = re.compile(r"(?:P309_GRANT|/authorization(?:/|\b)|GRANT\.json|target-consumed|pending-result|"
                      r"P309_RESULT|p309-emergency-result|p309-run-nonce)", re.I)
R5R6_RE = re.compile(r"(?:COVERAGE_MAP_R5|COVERAGE_MAP_R6|K5_COVERAGE_MAP|_R6\.json|\br6/)", re.I)
ADOPT_RE = re.compile(r"(?:adopt(?:ion|ed)?[_-]?(?:record|status|cell)|adoption)", re.I)
PROTECTED_REF_RE = re.compile(r"refs/(?:p5y-k5-cell30|p309-cell309|rlr-tail/|p309-test/)", re.I)

# (5) remote and paid compute: commands (at command position) and identifiers anywhere in code handed to an
# interpreter
REMOTE_CMDS = {"aws", "aws2", "vultr", "vultr-cli", "ssh", "scp", "sftp", "mosh", "ssh-copy-id", "ssh-keygen",
               "ssh-agent", "ssh-add", "doctl", "linode-cli", "hcloud", "gcloud", "az", "terraform", "pulumi",
               "ansible", "ansible-playbook", "kubectl", "eksctl", "sam", "cdk", "systemd-run", "autossh", "sshpass",
               "rclone", "s3cmd"}
REMOTE_TEXT_RE = re.compile(
    r"(?:amazonaws\.com|api\.vultr\.com|vultr|\bboto3\b|\bbotocore\b|\bparamiko\b|\bfabric\b|\basyncssh\b|"
    r"ec2-instance-connect|ssm\s+start-session|R2_AWS_SESSION|\bAWS_(?:ACCESS|SECRET|SESSION|PROFILE)|"
    r"\bssh://|\bgit@[\w.-]+:)", re.I)
PRIVATE_HOME_RE = re.compile(r"(?:~|\$HOME|/root|/home/[^/\s]+)/\.(?:aws|ssh|config/gcloud|vultr)", re.I)

# a live canary: proves in the transcript that the hook is active (always refused)
CANARY = "P309_GUARD_CANARY_7f3a"

# git subcommands that rewrite history, discard work or merge
GIT_ALWAYS_BLOCK = {"rebase", "filter-branch", "filter-repo", "replace", "merge", "pull", "am", "notes", "prune",
                    "reflog", "update-ref", "symbolic-ref", "worktree", "remote", "submodule", "lfs"}
FORCE_PUSH_FLAGS = {"-f", "--force", "--force-with-lease", "--force-if-includes", "--mirror", "--all", "--tags",
                    "--delete", "-d", "--prune", "--follow-tags", "--no-verify", "-o", "--push-option"}

# interpreters whose inline code (-c, heredoc, stdin) is scanned
INTERPRETERS = re.compile(r"^(?:python[\d.]*|pypy[\d.]*|bash|sh|zsh|dash|node|perl|ruby)$")

# write-type shell commands: every path argument must lie inside the write-set when it is in the repository
WRITE_CMDS = {"cp", "mv", "rm", "rmdir", "mkdir", "touch", "truncate", "install", "ln", "chmod", "chown", "tee",
              "dd", "rsync", "unlink", "shred", "patch", "tar", "unzip", "sed", "perl", "git-apply"}
