"""Bounded test-only pipe client. No production trust or credential provisioning."""
import base64
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import tempfile
import time

MAX_MESSAGE = 1_048_576
MAX_RESPONSE = 1_500_000


class WindowsSyntheticSigner:
    def __init__(self, bits=2048):
        if bits not in (2048, 3072, 4096):
            raise ValueError('unsupported synthetic RSA size')
        executable = os.environ.get('P309_WINDOWS_PWSH', '')
        if not executable or not Path(executable).is_file():
            raise RuntimeError('P309_WINDOWS_PWSH must name the existing Windows pwsh.exe through /mnt/c')
        script = Path(__file__).with_name('synthetic_windows_signer.ps1').resolve()
        windows_script = subprocess.check_output(['wslpath', '-w', str(script)], timeout=10, text=True).strip()
        quoted = windows_script.replace("'", "''")
        command = ("& ([scriptblock]::Create([IO.File]::ReadAllText('" + quoted +
                   "'))) -SyntheticOnly -KeyBits " + str(bits))
        self.errors = tempfile.TemporaryFile()
        self.process = None
        self.buffer = b''
        try:
            self.process = subprocess.Popen([executable, '-NoLogo', '-NoProfile', '-NonInteractive',
                                             '-Command', command], stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=self.errors, bufsize=0)
            self.hello = self.receive()
            if (self.hello.get('schema') != 'P309_SYNTHETIC_WINDOWS_SIGNER/1'
                    or self.hello.get('scope') != 'SYNTHETIC_ONLY'
                    or self.hello.get('algorithm') != 'RSA-PKCS1-v1_5-SHA256'
                    or self.hello.get('key_bits') != bits
                    or self.hello.get('key_ephemeral') is not True
                    or self.hello.get('key_name') is not None):
                raise RuntimeError('unexpected synthetic helper handshake')
            self.public = base64.b64decode(self.hello['public_key_b64'], validate=True)
            if not self.public.startswith(b'-----BEGIN PUBLIC KEY-----') or len(self.public) > 16384:
                raise RuntimeError('invalid synthetic public PEM')
            # Fixture pinning only. This is not independent production trust.
            self.pin = hashlib.sha256(self.public).hexdigest()
        except Exception:
            self.close()
            raise

    def receive(self, timeout=30):
        deadline = time.monotonic() + timeout
        while b'\n' not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.process.stdout], [], [], remaining)[0]:
                raise RuntimeError('Windows helper response timeout')
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                self.errors.seek(0)
                detail = self.errors.read(4096).decode('utf-8', errors='replace')
                raise RuntimeError('Windows helper closed without response: ' + detail)
            self.buffer += chunk
            if len(self.buffer) > MAX_RESPONSE:
                raise RuntimeError('Windows helper response budget exceeded')
        line, self.buffer = self.buffer.split(b'\n', 1)
        value = json.loads(line.decode('utf-8'))
        if not isinstance(value, dict):
            raise RuntimeError('Windows helper returned a non-object')
        return value

    def request(self, value):
        raw = json.dumps(value, separators=(',', ':'), allow_nan=False).encode('ascii') + b'\n'
        if len(raw) > 1_400_000:
            raise ValueError('synthetic transport budget exceeded')
        # WSL pipes can short-write. Bound writes as well as reads; a blocked
        # signer must not hang the verification process indefinitely.
        fd = self.process.stdin.fileno()
        os.set_blocking(fd, False)
        deadline = time.monotonic() + 30
        try:
            view = memoryview(raw)
            while view:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not select.select([], [fd], [], remaining)[1]:
                    raise RuntimeError('Windows helper write timeout')
                try:
                    count = os.write(fd, view)
                except BlockingIOError:
                    continue
                if count <= 0:
                    raise RuntimeError('Windows helper pipe short write')
                view = view[count:]
        finally:
            os.set_blocking(fd, True)
        return self.receive()

    def sign(self, message):
        if type(message) is not bytes or not 0 < len(message) <= MAX_MESSAGE:
            raise ValueError('synthetic message must be 1..1048576 bytes')
        result = self.request({'synthetic': True, 'message_b64': base64.b64encode(message).decode('ascii')})
        if set(result) != {'message_b64', 'signature_b64'}:
            raise RuntimeError('unexpected signature envelope fields')
        if base64.b64decode(result['message_b64'], validate=True) != message:
            raise RuntimeError('Windows helper changed the signed bytes')
        signature = base64.b64decode(result['signature_b64'], validate=True)
        if len(signature) * 8 != self.hello['key_bits']:
            raise RuntimeError('unexpected RSA signature size')
        return result

    def metadata(self):
        return {k: v for k, v in dict(self.hello, public_pem_sha256=self.pin).items()
                if k != 'public_key_b64'}

    def close(self):
        code = None
        if self.process is not None:
            if self.process.stdin and not self.process.stdin.closed:
                self.process.stdin.close()
            try:
                code = self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()  # Only this owned synthetic helper.
                code = self.process.wait(timeout=10)
            self.process.stdout.close()
        self.errors.close()
        return code

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
