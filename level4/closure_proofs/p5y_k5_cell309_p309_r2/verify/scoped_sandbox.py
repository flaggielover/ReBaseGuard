#!/usr/bin/env python3
"""
FC2 sandbox helper for the verifier variant's tests and harness (FNS/fc2/FC2_SPEC_R2.md section 6), written by the
verifier's author.

* A sandbox is a LIGHT sandbox (FC2 erratum E1-6; review R4 NB12) under the sandbox base directory
  <P309_SCRATCH_ROOT>/fc2_sandbox_verifier/ (r2 V4; plan condition P7): `git init`, a read-only
  `objects/info/alternates` link to this repository's object store and a copy of its `shallow` boundary file.  It has
  no remote, is never pushed, and writes objects only into itself.
* Its branch refs/heads/fc2-sandbox starts at the sandbox BASE COMMIT (r2 V3; plan conditions P6(b)/(e)), chosen by
  sandbox_base_commit():
  * this repository's HEAD history holds this namespace's freeze record (<FNS>/ledger/FREEZE_RECORD.json): the base is
    the recorded freeze commit F.  The record must have exactly one valid shape: exactly one commit in HEAD's history
    touches the record, that commit touches only the record, and its only parent equals the record's `freeze_commit`.
    Any other shape raises FreezeRecordError: the failure is loud, not shaped like a refusal;
  * otherwise (development): the base is HEAD.
  Precondition: the base's history holds 0 commits touching the record.  Postcondition: after construction, and again
  after the fixtures (build_valid, and on leaving the context), the sandbox holds exactly the number of record commits
  the flow expects (expect_freeze_records, 0 unless a flow builds one deliberately).  sandbox_base_commit() is the only
  read of this repository's HEAD that is used as a sandbox base (static check in tests/test_verify_scoped.py).
* P309_SCRATCH_ROOT is checked on every sandbox construction (scratch_sandbox_base).  A violation raises
  ScratchRootError; there is no fallback path.
* Commits are made in the sandbox only.  The index is populated from the base with `git read-tree` (no checkout), so a
  fixture commit changes exactly the paths it writes.
* Hard guards on every mutating call:
  * the target must be a sandbox under the sandbox base directory whose top level and git common dir differ from this
    repository's;
  * no ref under EITHER production ref namespace, r1's or r2's (r2 V2; plan addendum 2 F1), is ever created, updated
    or deleted (only refs/p309-test/*, refs/heads/* and refs/tags/* are allowed);
  * the production grant path, and any path named like the production grant file, is never written.
"""
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import uuid

HERE = os.path.dirname(os.path.realpath(__file__))
FNS_DIR = os.path.dirname(HERE)             # this file's formal namespace (the record path is derived from it)
FREEZE_RECORD_LEAF = 'ledger/FREEZE_RECORD.json'
SCRATCH_ENV = 'P309_SCRATCH_ROOT'           # r2 V4 (P7): the sandbox base directory is <P309_SCRATCH_ROOT>/SANDBOX_DIRNAME
FOREIGN_ENV = 'P309_FOREIGN_ROOTS'          # optional; os.pathsep-separated absolute paths (the cell-308 roots)
SANDBOX_DIRNAME = 'fc2_sandbox_verifier'
_HEX40 = re.compile(r'^[0-9a-f]{40}$')
_ALLOWED_REF_PREFIXES = ('refs/p309-test/', 'refs/heads/', 'refs/tags/')
_FORBIDDEN_REF_PREFIX_R1 = 'refs/p5y-k5-cell309-p309-r1/'  # q309: literal-ok (r1's production ref namespace, used ONLY to refuse)
_FORBIDDEN_REF_PREFIX_R2 = 'refs/p5y-k5-cell309-p309-r2/'  # q309: literal-ok (r2's production ref namespace, used ONLY to refuse)
_FORBIDDEN_REF_PREFIX = (_FORBIDDEN_REF_PREFIX_R1, _FORBIDDEN_REF_PREFIX_R2)   # both, always (r2 V2; addendum 2 F1)
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


# ----------------------------------------------------------------------------------------------------------------------
# r2 V4 (plan condition P7): the sandbox base directory, from P309_SCRATCH_ROOT; loud refusal, never a fallback
class ScratchRootError(RuntimeError):
    """P309_SCRATCH_ROOT or P309_FOREIGN_ROOTS violates r2 V4 (P7).  Raised; there is no fallback path."""


def _within(path, root):
    """path is root or lies under it (both absolute and normalised)"""
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def scratch_sandbox_base(environ=None, repo=None):
    """<P309_SCRATCH_ROOT>/fc2_sandbox_verifier.  Raises ScratchRootError if P309_SCRATCH_ROOT is unset or empty, not
    absolute, differs from its own realpath, is not an existing directory, lies inside the repository, or overlaps
    (equals, contains or lies inside) any path in P309_FOREIGN_ROOTS (optional; os.pathsep-separated; every entry must
    be absolute)."""
    env = os.environ if environ is None else environ
    root = env.get(SCRATCH_ENV)
    if not root:
        raise ScratchRootError('%s is unset or empty (no fallback)' % SCRATCH_ENV)
    if not os.path.isabs(root):
        raise ScratchRootError('%s=%r is not absolute' % (SCRATCH_ENV, root))
    if os.path.realpath(root) != root:
        raise ScratchRootError('%s=%r differs from its realpath %r' % (SCRATCH_ENV, root, os.path.realpath(root)))
    if not os.path.isdir(root):
        raise ScratchRootError('%s=%r is not an existing directory' % (SCRATCH_ENV, root))
    repo = os.path.realpath(own_repo() if repo is None else repo)
    if _within(root, repo):
        raise ScratchRootError('%s=%r lies inside the repository %r' % (SCRATCH_ENV, root, repo))
    foreign = env.get(FOREIGN_ENV)
    if foreign is not None:
        for entry in foreign.split(os.pathsep):
            if not os.path.isabs(entry):
                raise ScratchRootError('%s entry %r is not absolute' % (FOREIGN_ENV, entry))
            for g in sorted({os.path.normpath(entry), os.path.realpath(entry)}):
                if _within(root, g) or _within(g, root):
                    raise ScratchRootError('%s=%r overlaps the %s entry %r' % (SCRATCH_ENV, root, FOREIGN_ENV, entry))
    return os.path.join(root, SANDBOX_DIRNAME)


# ----------------------------------------------------------------------------------------------------------------------
# r2 V3 (plan conditions P6(b)/(e), plan section 4): the sandbox base commit
class FreezeRecordError(RuntimeError):
    """The freeze record in HEAD's history has a shape other than the single valid one, or a record-count pre- or
    postcondition fails.  Raised loudly; this is never a refusal."""


def freeze_record_rel(repo=None):
    """this namespace's freeze record, <FNS>/ledger/FREEZE_RECORD.json, relative to the repository top level"""
    repo = os.path.realpath(own_repo() if repo is None else repo)
    rel = os.path.relpath(FNS_DIR, repo)
    if rel in (os.curdir, os.pardir) or rel.startswith(os.pardir + os.sep) or os.path.isabs(rel):
        raise FreezeRecordError('the namespace %r is not inside the repository %r' % (FNS_DIR, repo))
    return rel.replace(os.sep, '/') + '/' + FREEZE_RECORD_LEAF


def _record_touching(repo, rev, record_rel):
    """the commits in rev's history that touch record_rel (git's default history simplification for a path, as
    `git log -- <path>`; in a linear history these are exactly the commits that change the record)"""
    return _git(repo, 'rev-list', '--end-of-options', rev, '--', record_rel).split()


def sandbox_base_commit(repo=None, record_rel=None):
    """(base commit, mode) for a sandbox of `repo` (default: this repository): ('<F>', 'post-freeze') if HEAD's history
    holds the freeze record, ('<HEAD>', 'development') if it holds none.  Any other record shape raises
    FreezeRecordError.  This is the only read of the repository's HEAD that is used as a sandbox base."""
    repo = os.path.realpath(own_repo() if repo is None else repo)
    record_rel = freeze_record_rel(repo) if record_rel is None else record_rel
    head = _git(repo, 'rev-parse', '--verify', 'HEAD^{commit}').strip()
    touching = _record_touching(repo, head, record_rel)
    if not touching:
        base, mode = head, 'development'
    elif len(touching) != 1:
        raise FreezeRecordError('%d commits in HEAD\'s history touch %s; exactly one is required (%s)'
                                % (len(touching), record_rel, ' '.join(c[:12] for c in touching[:5])))
    else:
        rc = touching[0]
        parents = _git(repo, 'rev-list', '--parents', '-n', '1', '--end-of-options', rc).split()[1:]
        if len(parents) != 1:
            raise FreezeRecordError('the record commit %s has %d parents; exactly one is required' % (rc, len(parents)))
        changed = [p for p in _git(repo, 'diff-tree', '-r', '--name-only', '--no-commit-id', '--end-of-options',
                                   parents[0], rc).split('\n') if p]
        if changed != [record_rel]:
            raise FreezeRecordError('the record commit %s touches %r, not only %s' % (rc, changed[:5], record_rel))
        raw = _git(repo, 'cat-file', 'blob', '--end-of-options', '%s:%s' % (rc, record_rel), binary=True)
        try:
            record = json.loads(raw.decode('utf-8'))
        except ValueError as exc:                                     # UnicodeDecodeError is a ValueError
            raise FreezeRecordError('the freeze record at %s is not JSON: %s' % (rc, exc))
        fc = record.get('freeze_commit') if isinstance(record, dict) else None
        if not isinstance(fc, str) or not _HEX40.match(fc):
            raise FreezeRecordError('the freeze record at %s has no 40-hex freeze_commit (%r)' % (rc, fc))
        if fc != parents[0]:
            raise FreezeRecordError('the freeze record\'s freeze_commit %s is not its commit\'s only parent %s'
                                    % (fc, parents[0]))
        base, mode = fc, 'post-freeze'
    if _record_touching(repo, base, record_rel):                      # P6(b) precondition: 0 records in the base
        raise FreezeRecordError('the base %s has a commit touching %s in its history' % (base, record_rel))
    return base, mode


class Sandbox(object):
    """One light sandbox (FC2 erratum E1-6).  Use as a context manager (torn down on exit)."""

    def __init__(self, tag, expect_freeze_records=0):
        self.sandbox_base = scratch_sandbox_base()                      # r2 V4: raises, never falls back
        src = own_repo()
        self.record_rel = freeze_record_rel(src)
        self.base_commit, self.base_mode = sandbox_base_commit(src, self.record_rel)   # r2 V3: raises on a bad record
        self.expect_freeze_records = expect_freeze_records
        os.makedirs(self.sandbox_base, exist_ok=True)
        if os.path.realpath(self.sandbox_base) != self.sandbox_base:
            raise ScratchRootError('the sandbox base directory %r is not its own realpath' % self.sandbox_base)
        self.root = os.path.join(self.sandbox_base, '%s-%s' % (tag, uuid.uuid4().hex[:10]))
        subprocess.run(['git', 'init', '--quiet', self.root], check=True, capture_output=True, env=_ENV, timeout=120)
        try:
            self._assert_sandbox()
            src_objects = os.path.realpath(_git(src, 'rev-parse', '--path-format=absolute', '--git-path',
                                                'objects').strip())
            src_shallow = _git(src, 'rev-parse', '--path-format=absolute', '--git-path', 'shallow').strip()
            gitdir = os.path.realpath(_git(self.root, 'rev-parse', '--path-format=absolute', '--git-dir').strip())
            if not gitdir.startswith(os.path.realpath(self.root) + os.sep):
                raise RuntimeError('refusing: sandbox git dir outside the sandbox')
            with open(os.path.join(gitdir, 'objects', 'info', 'alternates'), 'w') as fh:   # read-only object link
                fh.write(src_objects + '\n')
            if os.path.exists(src_shallow):
                shutil.copyfile(src_shallow, os.path.join(gitdir, 'shallow'))
            _git(self.root, 'config', 'gc.auto', '0')                                       # sandbox-local config
            if _git(self.root, 'remote').strip():
                raise RuntimeError('sandbox has a remote')
            self.update_ref('refs/heads/fc2-sandbox', self.base_commit)
            _git(self.root, 'symbolic-ref', 'HEAD', 'refs/heads/fc2-sandbox')
            _git(self.root, 'read-tree', 'HEAD')
            self.assert_no_production_refs()
            self.check_freeze_records(0)                                 # P6(b): a new sandbox holds no record commit
            self.base = self.head()
            if self.base != self.base_commit:
                raise FreezeRecordError('the sandbox branch is at %s, not at the base %s' % (self.base, self.base_commit))
        except BaseException:
            self.teardown()
            raise

    # -- guards -----------------------------------------------------------------------------------------------------
    def assert_no_production_refs(self):
        """the sandbox holds no ref under either production namespace (r2 V2)"""
        for ns in _FORBIDDEN_REF_PREFIX:
            if _git(self.root, 'for-each-ref', '--format=%(refname)', ns).strip():
                raise RuntimeError('sandbox carries a production-namespace ref (%s)' % ns)

    def freeze_record_commits(self):
        """the commits reachable from the sandbox's refs or HEAD that touch this namespace's freeze record"""
        return sorted(set(_git(self.root, 'rev-list', '--all', 'HEAD', '--', self.record_rel).split()))

    def check_freeze_records(self, expected=None):
        """P6(b) postcondition: the sandbox holds exactly the number of record commits the flow expects"""
        want = self.expect_freeze_records if expected is None else expected
        got = self.freeze_record_commits()
        if len(got) != want:
            raise FreezeRecordError('the sandbox holds %d commits touching %s; the flow expects %d'
                                    % (len(got), self.record_rel, want))

    def _assert_sandbox(self):
        root = os.path.realpath(self.root)
        if not root.startswith(os.path.realpath(self.sandbox_base) + os.sep):
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
            subprocess.run(['git', '-C', self.root, 'read-tree', '--end-of-options', parents[0]], check=True, env=env,
                           capture_output=True)
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
        _git(self.root, 'update-ref', '--end-of-options', ref, target)

    def delete_ref(self, ref):
        self._assert_sandbox()
        self._assert_ref(ref)
        _git(self.root, 'update-ref', '-d', ref)

    def reset_hard_index(self, commit):
        """Move the current branch and the index to `commit` (no working tree files)."""
        self._assert_sandbox()
        cur = _git(self.root, 'symbolic-ref', 'HEAD').strip()
        self._assert_ref(cur)
        _git(self.root, 'update-ref', '--end-of-options', cur, commit)
        _git(self.root, 'read-tree', '--end-of-options', commit)

    def teardown(self):
        root = os.path.realpath(self.root)
        if root.startswith(os.path.realpath(self.sandbox_base) + os.sep) and os.path.isdir(root):
            shutil.rmtree(root)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.assert_no_production_refs()
                self.check_freeze_records()
        finally:
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
    sb.check_freeze_records()                                            # P6(b) postcondition after the fixture
    return fc, gc, msha
