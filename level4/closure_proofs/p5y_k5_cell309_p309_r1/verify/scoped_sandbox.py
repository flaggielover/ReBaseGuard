#!/usr/bin/env python3
"""
FC2 sandbox helper for the verifier variant's tests and harness (FNS/fc2/FC2_SPEC_R2.md section 6), written by the
verifier's author.

* A sandbox is a `git clone --shared --no-checkout` of this repository under the scratchpad directory
  .../scratchpad/fc2_sandbox_verifier/, with `origin` removed.  It is never pushed and no remote is ever added.
* Commits are made in the sandbox only.  The index is populated from HEAD with `git read-tree` (no checkout), so a
  fixture commit changes exactly the paths it writes.
* Hard guards on every mutating call:
  * the target must be a sandbox under SANDBOX_BASE whose top level and git common dir differ from this repository's;
  * no ref under the production ref namespace is ever created, updated or deleted (only refs/p309-test/*,
    refs/heads/* and refs/tags/* are allowed);
  * the production grant path, and any path named like the production grant file, is never written.
"""
import datetime
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import uuid

HERE = os.path.dirname(os.path.realpath(__file__))
SANDBOX_BASE = '/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/fc2_sandbox_verifier'
_ALLOWED_REF_PREFIXES = ('refs/p309-test/', 'refs/heads/', 'refs/tags/')
_FORBIDDEN_REF_PREFIX = 'refs/p5y-k5-cell309-p309-r1/'  # q309: literal-ok (production ref namespace, used ONLY to refuse)
_PROD_GRANT_BASENAME = 'P309_GRANT.json'  # compared only, to REFUSE any write of such a path
_ENV = dict(os.environ, LC_ALL='C', GIT_PAGER='cat', GIT_TERMINAL_PROMPT='0',
            GIT_AUTHOR_NAME='fc2-sandbox', GIT_AUTHOR_EMAIL='fc2-sandbox@invalid',
            GIT_COMMITTER_NAME='fc2-sandbox', GIT_COMMITTER_EMAIL='fc2-sandbox@invalid')

TEST_GRANT_PATH = 'TEST_ONLY/P309_TEST_GRANT.json'
TEST_MANIFEST_PATH = 'TEST_ONLY/P309_TEST_FREEZE_MANIFEST.json'
TEST_RESULT_PATH = 'TEST_ONLY/P309_TEST_RESULT.json'
TEST_MARKER = 'refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER'


def _git(cwd, *args, check=True, binary=False):
    p = subprocess.run(['git', '-C', cwd] + list(args), capture_output=True, env=_ENV, timeout=600)
    if check and p.returncode != 0:
        raise RuntimeError('git %s failed: %s' % (' '.join(args[:2]), p.stderr.decode('utf-8', 'replace')[:300]))
    return p.stdout if binary else p.stdout.decode('utf-8', 'replace')


def own_repo():
    return os.path.realpath(_git(HERE, 'rev-parse', '--show-toplevel').strip())


def _common_dir(repo):
    return os.path.realpath(_git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir').strip())


def local_host_id_sha256():
    with open('/etc/machine-id', 'rb') as fh:
        mid = fh.read().strip()
    return hashlib.sha256(b'machine-id:' + mid + b'\nhostname:' + socket.gethostname().encode()).hexdigest()


class Sandbox(object):
    """One sandbox clone.  Use as a context manager (torn down on exit)."""

    def __init__(self, tag):
        os.makedirs(SANDBOX_BASE, exist_ok=True)
        self.root = os.path.join(SANDBOX_BASE, '%s-%s' % (tag, uuid.uuid4().hex[:10]))
        src = own_repo()
        subprocess.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', src, self.root], check=True,
                       capture_output=True, env=_ENV, timeout=900)
        self._assert_sandbox()
        _git(self.root, 'remote', 'remove', 'origin')
        if _git(self.root, 'remote').strip():
            raise RuntimeError('sandbox still has a remote')
        _git(self.root, 'read-tree', 'HEAD')
        if _git(self.root, 'for-each-ref', '--format=%(refname)', _FORBIDDEN_REF_PREFIX).strip():
            raise RuntimeError('sandbox clone carries a production-namespace ref')
        self.base = self.head()

    # -- guards -----------------------------------------------------------------------------------------------------
    def _assert_sandbox(self):
        root = os.path.realpath(self.root)
        if not root.startswith(os.path.realpath(SANDBOX_BASE) + os.sep):
            raise RuntimeError('refusing: %s is not under the sandbox base' % root)
        top = os.path.realpath(_git(root, 'rev-parse', '--show-toplevel').strip())
        mine = own_repo()
        if top != root or top == mine or _common_dir(top) == _common_dir(mine):
            raise RuntimeError('refusing: %s is not an isolated sandbox' % root)

    @staticmethod
    def _assert_ref(ref):
        if ref.startswith(_FORBIDDEN_REF_PREFIX) or not ref.startswith(_ALLOWED_REF_PREFIXES):
            raise RuntimeError('refusing to touch ref %r' % ref)

    @staticmethod
    def _assert_path(path):
        if os.path.basename(path) == _PROD_GRANT_BASENAME or 'authorization/' in path or path.startswith('/') or \
                '..' in path.split('/'):
            raise RuntimeError('refusing to write path %r' % path)

    # -- operations -------------------------------------------------------------------------------------------------
    def head(self):
        return _git(self.root, 'rev-parse', 'HEAD').strip()

    def commit(self, files, message, parents=None):
        """Commit {path: bytes|str|None} (None deletes) on top of HEAD (or on explicit parents, without moving HEAD
        when parents is given).  Returns the commit id."""
        self._assert_sandbox()
        for path, content in files.items():
            self._assert_path(path)
        if parents is not None:
            # build a commit object from the tree of parents[0] plus the files; HEAD is not moved
            idx = os.path.join(self.root, '.git', 'fc2_tmp_index')
            env = dict(_ENV, GIT_INDEX_FILE=idx)
            subprocess.run(['git', '-C', self.root, 'read-tree', parents[0]], check=True, env=env, capture_output=True)
            self._stage(files, env)
            tree = subprocess.run(['git', '-C', self.root, 'write-tree'], check=True, env=env,
                                  capture_output=True).stdout.decode().strip()
            args = ['git', '-C', self.root, 'commit-tree', tree]
            for p in parents:
                args += ['-p', p]
            args += ['-m', message]
            c = subprocess.run(args, check=True, env=env, capture_output=True).stdout.decode().strip()
            os.remove(idx)
            return c
        self._stage(files, _ENV)
        subprocess.run(['git', '-C', self.root, 'commit', '--quiet', '--allow-empty', '-m', message], check=True,
                       env=_ENV, capture_output=True)
        return self.head()

    def _stage(self, files, env):
        for path, content in files.items():
            if content is None:
                subprocess.run(['git', '-C', self.root, 'rm', '--cached', '--quiet', '--', path], check=True,
                               env=env, capture_output=True)
                continue
            data = content.encode('utf-8') if isinstance(content, str) else content
            blob = subprocess.run(['git', '-C', self.root, 'hash-object', '-w', '--stdin'], input=data, check=True,
                                  env=env, capture_output=True).stdout.decode().strip()
            subprocess.run(['git', '-C', self.root, 'update-index', '--add', '--cacheinfo', '100644,%s,%s'
                            % (blob, path)], check=True, env=env, capture_output=True)

    def update_ref(self, ref, target):
        self._assert_sandbox()
        self._assert_ref(ref)
        _git(self.root, 'update-ref', ref, target)

    def delete_ref(self, ref):
        self._assert_sandbox()
        self._assert_ref(ref)
        _git(self.root, 'update-ref', '-d', ref)

    def reset_hard_index(self, commit):
        """Move the current branch and the index to `commit` (no working tree files)."""
        self._assert_sandbox()
        cur = _git(self.root, 'symbolic-ref', 'HEAD').strip()
        self._assert_ref(cur)
        _git(self.root, 'update-ref', cur, commit)
        _git(self.root, 'read-tree', commit)

    def teardown(self):
        root = os.path.realpath(self.root)
        if root.startswith(os.path.realpath(SANDBOX_BASE) + os.sep) and os.path.isdir(root):
            shutil.rmtree(root)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.teardown()
        return False


# ----------------------------------------------------------------------------------------------------------------------
# section 6 fixtures
def manifest_bytes(pins):
    return (json.dumps({'schema': 'P309_TEST_FREEZE_MANIFEST/1', 'code_pins': pins}, sort_keys=True, indent=1)
            + '\n').encode('utf-8')


def test_grant(frozen_commit, manifest_sha, verifier_id, over=None):
    g = {
        'schema': 'P309_TEST_GRANT/1',
        'campaign': 'TEST_ONLY_DO_NOT_EXECUTE',
        'cell': 'TEST_ONLY_DO_NOT_EXECUTE',
        'geometry': {'h': '3', 'k': '1/2'},
        'cell_interval': ['1/3', '20/51'],
        'drift_hull_Ew': ['341/1024', '201/512'],
        'frozen_commit': frozen_commit,
        'frozen_manifest_sha256': manifest_sha,
        'verifier_id': verifier_id,
        'guard_id': 'sha256:' + hashlib.sha256(b'TEST_ONLY_DO_NOT_EXECUTE guard placeholder').hexdigest(),
        'execution_host': {'host_id_sha256': local_host_id_sha256()},
        'runtime': {'python': platform.python_version()},
        'marker_ref': TEST_MARKER,
        'not_after_utc': (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
                          ).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    for k, v in (over or {}).items():
        if v is _DELETE:
            g.pop(k, None)
        else:
            g[k] = v
    return g


class _Delete(object):
    pass


_DELETE = _Delete()
DELETE = _DELETE


def grant_bytes(g):
    return (json.dumps(g, sort_keys=True, indent=1) + '\n').encode('utf-8')


def build_valid(sb, own_rel, own_sha, *, pins=None, grant_over=None, grant_raw=None, extra_files=None,
                set_marker=True):
    """Manifest commit, then the test grant commit (HEAD), then the TEST marker at the grant commit.
    Returns (frozen_commit, grant_commit, manifest_sha)."""
    mb = manifest_bytes(pins if pins is not None else [{'path': own_rel, 'sha256': own_sha}])
    fc = sb.commit({TEST_MANIFEST_PATH: mb}, 'TEST_ONLY frozen manifest')
    msha = hashlib.sha256(mb).hexdigest()
    if grant_raw is None:
        grant_raw = grant_bytes(test_grant(fc, msha, 'sha256:' + own_sha, over=grant_over))
    files = {TEST_GRANT_PATH: grant_raw}
    files.update(extra_files or {})
    gc = sb.commit(files, 'TEST_ONLY grant')
    if set_marker:
        sb.update_ref(TEST_MARKER, gc)
    return fc, gc, msha
