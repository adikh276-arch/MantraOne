from abc import ABC, abstractmethod

class IEncryptionProvider(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> str: pass
    @abstractmethod
    def decrypt(self, ciphertext: str) -> str: pass
    @abstractmethod
    def encrypt_optional(self, value: str | None) -> str | None: pass
    @abstractmethod
    def decrypt_optional(self, value: str | None) -> str | None: pass
    @abstractmethod
    def encrypt_json(self, data: dict) -> str: pass
    @abstractmethod
    def decrypt_json(self, ciphertext: str) -> dict: pass
