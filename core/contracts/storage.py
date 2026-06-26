from abc import ABC, abstractmethod
from uuid import UUID

class IStorageProvider(ABC):
    @abstractmethod
    async def upload(self, content: bytes, family_id: UUID, member_id: UUID, document_type: str, file_uuid: UUID, extension: str) -> str: pass
    @abstractmethod
    async def download(self, gcs_path: str) -> bytes: pass
    @abstractmethod
    async def generate_signed_url(self, gcs_path: str, expires_seconds: int = 900) -> str: pass
    @abstractmethod
    async def delete(self, gcs_path: str) -> None: pass
