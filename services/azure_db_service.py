# services/azure_db_service.py
"""Azure Cosmos DB service for session persistence and artifact storage."""

import os
import uuid
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Try to import azure-cosmos; fall back to in-memory store if not configured
try:
    from azure.cosmos import CosmosClient, PartitionKey, exceptions
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False


class InMemoryStore:
    """Fallback in-memory store when Cosmos DB is not configured."""

    def __init__(self):
        self.sessions = {}

    def create_session(self, session_data: dict) -> dict:
        session_id = session_data.get("id", str(uuid.uuid4())[:8].upper())
        session_data["id"] = session_id
        session_data["created_at"] = datetime.now(timezone.utc).isoformat()
        session_data["updated_at"] = session_data["created_at"]
        self.sessions[session_id] = session_data
        return session_data

    def get_session(self, session_id: str) -> dict | None:
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, updates: dict) -> dict:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        self.sessions[session_id].update(updates)
        self.sessions[session_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self.sessions[session_id]

    def store_artifacts(self, session_id: str, artifacts: dict) -> None:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        existing = self.sessions[session_id].get("artifacts", {})
        existing.update(artifacts)
        self.sessions[session_id]["artifacts"] = existing
        self.sessions[session_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

    def list_sessions(self) -> list[dict]:
        return sorted(
            self.sessions.values(),
            key=lambda s: s.get("created_at", ""),
            reverse=True,
        )


class CosmosDBStore:
    """Azure Cosmos DB session store."""

    def __init__(self):
        endpoint = os.environ["AZURE_COSMOS_ENDPOINT"]
        key = os.environ["AZURE_COSMOS_KEY"]
        db_name = os.environ.get("AZURE_COSMOS_DB_NAME", "phoenix")

        self.client = CosmosClient(endpoint, key)
        self.database = self.client.create_database_if_not_exists(db_name)
        self.container = self.database.create_container_if_not_exists(
            id="sessions",
            partition_key=PartitionKey(path="/id"),
        )

    def create_session(self, session_data: dict) -> dict:
        session_id = session_data.get("id", str(uuid.uuid4())[:8].upper())
        session_data["id"] = session_id
        session_data["created_at"] = datetime.now(timezone.utc).isoformat()
        session_data["updated_at"] = session_data["created_at"]
        self.container.create_item(session_data)
        return session_data

    def get_session(self, session_id: str) -> dict | None:
        try:
            return self.container.read_item(session_id, partition_key=session_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def update_session(self, session_id: str, updates: dict) -> dict:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session.update(updates)
        session["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.container.upsert_item(session)
        return session

    def store_artifacts(self, session_id: str, artifacts: dict) -> None:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        existing = session.get("artifacts", {})
        existing.update(artifacts)
        session["artifacts"] = existing
        session["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.container.upsert_item(session)

    def list_sessions(self) -> list[dict]:
        items = list(self.container.query_items(
            query="SELECT * FROM c ORDER BY c.created_at DESC",
            enable_cross_partition_query=True,
        ))
        return items


def get_store():
    """Get the appropriate store backend."""
    cosmos_endpoint = os.environ.get("AZURE_COSMOS_ENDPOINT")
    cosmos_key = os.environ.get("AZURE_COSMOS_KEY")

    if COSMOS_AVAILABLE and cosmos_endpoint and cosmos_key:
        print("[DB] Using Azure Cosmos DB store")
        return CosmosDBStore()
    else:
        print("[DB] Using in-memory store (Cosmos DB not configured)")
        return InMemoryStore()


# Singleton store instance
_store = None


def get_db():
    """Get the singleton DB store instance."""
    global _store
    if _store is None:
        _store = get_store()
    return _store
