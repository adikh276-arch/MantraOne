from __future__ import annotations
import base64
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config.settings import settings
from core.contracts.encryption import IEncryptionProvider

_DEV_KEY = b"mantraone-dev-key-00000000000000"

class EncryptionService(IEncryptionProvider):
    def __init__(self) -> None:
        if settings.encryption_key:
            raw = base64.b64decode(settings.encryption_key.encode())
            if len(raw) != 32:
                raise ValueError("Encryption key must be exactly 32 bytes (256 bits)")
            self._aesgcm = AESGCM(raw)
        else:
            self._aesgcm = AESGCM(_DEV_KEY)

    def encrypt(self, plaintext: str) -> str:
        if not plaintext: return plaintext
        nonce = os.urandom(12)
        ct = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return base64.b64encode(nonce + ct).decode("ascii")

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext: return ciphertext
        raw = base64.b64decode(ciphertext.encode("ascii"))
        nonce, ct = raw[:12], raw[12:]
        return self._aesgcm.decrypt(nonce, ct, None).decode("utf-8")

    def encrypt_optional(self, value: str | None) -> str | None:
        return self.encrypt(value) if value else None

    def decrypt_optional(self, value: str | None) -> str | None:
        return self.decrypt(value) if value else None

    def encrypt_json(self, data: dict) -> str:
        return self.encrypt(json.dumps(data, default=str))

    def decrypt_json(self, ciphertext: str) -> dict:
        if not ciphertext: return {}
        return json.loads(self.decrypt(ciphertext))
