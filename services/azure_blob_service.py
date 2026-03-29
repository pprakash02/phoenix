# services/azure_blob_service.py
"""Azure Blob Storage service for pipeline artifact storage.

Falls back to local filesystem storage when Azure is not configured.
"""

import os
import io
import json
import zipfile
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Try to import azure-storage-blob; fall back to local store if not available
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    BLOB_AVAILABLE = True
except ImportError:
    BLOB_AVAILABLE = False


CONTAINER_NAME = "phoenix-artifacts"
LOCAL_ARTIFACTS_DIR = os.path.abspath("generated_tests")


class LocalArtifactStore:
    """Fallback: stores artifacts on the local filesystem under generated_tests/."""

    def __init__(self):
        os.makedirs(LOCAL_ARTIFACTS_DIR, exist_ok=True)

    def upload_artifact(self, session_id: str, filename: str, content: str) -> str:
        """Write a single artifact file. Returns the local path."""
        session_dir = os.path.join(LOCAL_ARTIFACTS_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        path = os.path.join(session_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def download_artifact(self, session_id: str, filename: str) -> str | None:
        """Read a single artifact file. Returns content or None."""
        path = os.path.join(LOCAL_ARTIFACTS_DIR, session_id, filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def list_artifacts(self, session_id: str) -> list[str]:
        """List filenames for a session."""
        session_dir = os.path.join(LOCAL_ARTIFACTS_DIR, session_id)
        if not os.path.isdir(session_dir):
            return []
        return sorted(os.listdir(session_dir))

    def upload_batch(self, session_id: str, files: dict[str, str]) -> None:
        """Upload multiple artifacts at once."""
        for fname, content in files.items():
            self.upload_artifact(session_id, fname, content)

    def get_download_zip(self, session_id: str, test_files: dict, doc_files: dict) -> bytes | None:
        """Build a zip file in memory and return the bytes."""
        if not test_files and not doc_files:
            return None
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname, content in test_files.items():
                zf.writestr(f"tests/{fname}", content)
            for fname, content in doc_files.items():
                zf.writestr(f"docs/{fname}", content)
        return buf.getvalue()


class AzureBlobArtifactStore:
    """Azure Blob Storage artifact store."""

    def __init__(self):
        conn_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        self.blob_service = BlobServiceClient.from_connection_string(conn_str)
        # Create the container if it doesn't exist
        try:
            self.container = self.blob_service.create_container(CONTAINER_NAME)
        except Exception:
            self.container = self.blob_service.get_container_client(CONTAINER_NAME)

    def _blob_name(self, session_id: str, filename: str) -> str:
        return f"{session_id}/{filename}"

    def upload_artifact(self, session_id: str, filename: str, content: str) -> str:
        """Upload a single artifact to blob storage. Returns the blob URL."""
        blob_name = self._blob_name(session_id, filename)
        blob_client = self.container.get_blob_client(blob_name) if hasattr(self.container, 'get_blob_client') else self.blob_service.get_blob_client(CONTAINER_NAME, blob_name)

        content_type = "text/x-python" if filename.endswith(".py") else "text/markdown"
        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url

    def download_artifact(self, session_id: str, filename: str) -> str | None:
        """Download a single artifact from blob storage."""
        blob_name = self._blob_name(session_id, filename)
        blob_client = self.blob_service.get_blob_client(CONTAINER_NAME, blob_name)
        try:
            data = blob_client.download_blob().readall()
            return data.decode("utf-8")
        except Exception:
            return None

    def list_artifacts(self, session_id: str) -> list[str]:
        """List artifact filenames for a session."""
        container_client = self.blob_service.get_container_client(CONTAINER_NAME)
        prefix = f"{session_id}/"
        blobs = container_client.list_blobs(name_starts_with=prefix)
        return sorted(b.name.replace(prefix, "") for b in blobs)

    def upload_batch(self, session_id: str, files: dict[str, str]) -> None:
        """Upload multiple artifacts at once."""
        for fname, content in files.items():
            self.upload_artifact(session_id, fname, content)

    def get_download_zip(self, session_id: str, test_files: dict, doc_files: dict) -> bytes | None:
        """Build a zip file in memory and return the bytes."""
        if not test_files and not doc_files:
            return None
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname, content in test_files.items():
                zf.writestr(f"tests/{fname}", content)
            for fname, content in doc_files.items():
                zf.writestr(f"docs/{fname}", content)
        return buf.getvalue()


# ─── Factory ────────────────────────────────────────────────────────────

_store = None


def get_artifact_store():
    """Get the singleton artifact store instance."""
    global _store
    if _store is not None:
        return _store

    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "").strip()
    if BLOB_AVAILABLE and conn_str:
        print("[BLOB] Using Azure Blob Storage for artifacts")
        _store = AzureBlobArtifactStore()
    else:
        print("[BLOB] Using local filesystem for artifacts (Azure Blob not configured)")
        _store = LocalArtifactStore()
    return _store
