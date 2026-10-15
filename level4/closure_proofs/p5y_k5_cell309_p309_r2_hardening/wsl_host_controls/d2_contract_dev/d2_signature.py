"""Development-only, public RSA verification; no key generation/signing or I/O.

Strict EMSA-PKCS1-v1_5/SHA256 comparison, with bounded public numbers. This is a
reference verifier, not a reviewed production crypto backend or trust bootstrap.
"""
from dataclasses import dataclass
import hashlib
import hmac

MAX_MESSAGE_BYTES = 1_048_576
SHA256_DIGEST_INFO = bytes.fromhex('3031300d060960864801650304020105000420')


@dataclass(frozen=True)
class PublicNumbers:
    n: int
    e: int

    def __post_init__(self):
        if (type(self.n) is not int or self.n <= 0 or self.n.bit_length() not in (2048, 3072, 4096)
                or self.n % 2 != 1 or type(self.e) is not int
                or not 3 <= self.e <= 0xffffffff or self.e % 2 != 1):
            raise ValueError('bounded RSA public numbers required')

    def fingerprint(self):
        """Development domain-separated public-number pin, NOT a PEM/SPKI pin."""
        width = self.n.bit_length() // 8
        return hashlib.sha256(b'P309_D2_RSA_PUBLIC_NUMBERS/1\0' +
                              self.n.to_bytes(width, 'big') + self.e.to_bytes(4, 'big')).hexdigest()

    def verify(self, message, signature):
        if (type(message) is not bytes or not 0 < len(message) <= MAX_MESSAGE_BYTES
                or type(signature) is not bytes):
            return False
        width = self.n.bit_length() // 8
        if len(signature) != width:
            return False
        value = int.from_bytes(signature, 'big')
        if value >= self.n:
            return False
        encoded = pow(value, self.e, self.n).to_bytes(width, 'big')
        digest_info = SHA256_DIGEST_INFO + hashlib.sha256(message).digest()
        expected = b'\0\1' + b'\xff' * (width - len(digest_info) - 3) + b'\0' + digest_info
        return hmac.compare_digest(encoded, expected)
