# services/blob_service.py
"""Azure Blob Storage service for storing repo files, generated tests, and docs."""

import os
import io
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    BLOB_AVAILABLE = True
except ImportError:
    BLOB_AVAILABLE = False

AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")

# Container names
CONTAINER_REPOS = "repos"
CONTAINER_ARTIFACTS = "artifacts"


class InMemoryBlobStore:
    """Fallback in-memory blob store for local development."""

    def __init__(self):
        self._blobs = {}  # key: "container/path" -> bytes

    def _key(self, container, path):
        return f"{container}/{path}"

    def upload_text(self, container: str, path: str, content: str) -> str:
        key = self._key(container, path)
        self._blobs[key] = content.encode("utf-8")
        return key

    def upload_bytes(self, container: str, path: str, data: bytes) -> str:
        key = self._key(container, path)
        self._blobs[key] = data
        return key

    def download_text(self, container: str, path: str) -> str | None:
        key = self._key(container, path)
        data = self._blobs.get(key)
        return data.decode("utf-8") if data else None

    def download_bytes(self, container: str, path: str) -> bytes | None:
        key = self._key(container, path)
        return self._blobs.get(key)

    def list_blobs(self, container: str, prefix: str = "") -> list[str]:
        full_prefix = f"{container}/{prefix}"
        return [
            k[len(container) + 1:]  # strip "container/"
            for k in self._blobs
            if k.startswith(full_prefix)
        ]

    def delete_blobs(self, container: str, prefix: str = "") -> int:
        full_prefix = f"{container}/{prefix}"
        to_delete = [k for k in self._blobs if k.startswith(full_prefix)]
        for k in to_delete:
            del self._blobs[k]
        return len(to_delete)


class AzureBlobStore:
    """Azure Blob Storage client."""

    def __init__(self):
        self.client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )
        # Ensure containers exist
        for name in [CONTAINER_REPOS, CONTAINER_ARTIFACTS]:
            try:
                self.client.create_container(name)
            except Exception:
                pass  # Already exists

    def upload_text(self, container: str, path: str, content: str) -> str:
        blob = self.client.get_blob_client(container, path)
        blob.upload_blob(
            content,
            overwrite=True,
            content_settings=ContentSettings(content_type="text/plain; charset=utf-8"),
        )
        return f"{container}/{path}"

    def upload_bytes(self, container: str, path: str, data: bytes) -> str:
        blob = self.client.get_blob_client(container, path)
        blob.upload_blob(data, overwrite=True)
        return f"{container}/{path}"

    def download_text(self, container: str, path: str) -> str | None:
        try:
            blob = self.client.get_blob_client(container, path)
            return blob.download_blob().readall().decode("utf-8")
        except Exception:
            return None

    def download_bytes(self, container: str, path: str) -> bytes | None:
        try:
            blob = self.client.get_blob_client(container, path)
            return blob.download_blob().readall()
        except Exception:
            return None

    def list_blobs(self, container: str, prefix: str = "") -> list[str]:
        container_client = self.client.get_container_client(container)
        return [b.name for b in container_client.list_blobs(name_starts_with=prefix)]

    def delete_blobs(self, container: str, prefix: str = "") -> int:
        container_client = self.client.get_container_client(container)
        blobs = list(container_client.list_blobs(name_starts_with=prefix))
        for b in blobs:
            container_client.delete_blob(b.name)
        return len(blobs)


def get_blob_store():
    """Get the appropriate blob store backend."""
    if BLOB_AVAILABLE and AZURE_STORAGE_CONNECTION_STRING:
        print("[BLOB] Using Azure Blob Storage")
        return AzureBlobStore()
    else:
        print("[BLOB] Using in-memory blob store (Azure Storage not configured)")
        return InMemoryBlobStore()


# Singleton
_blob_store = None


def get_blob():
    """Get the singleton blob store instance."""
    global _blob_store
    if _blob_store is None:
        _blob_store = get_blob_store()
    return _blob_store
