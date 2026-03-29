# services/azure_db_service.py
"""Azure Cosmos DB service for session persistence, user management, and history."""

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
        self.users = {}
        self.repos = {}
        self.history = {}

    # ─── Sessions ────────────────────────────────────────────────────

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

    # ─── Users ───────────────────────────────────────────────────────

    def create_or_update_user(self, user_data: dict) -> dict:
        """Upsert a user by their Microsoft oid."""
        oid = user_data.get("oid", "")
        now = datetime.now(timezone.utc).isoformat()

        existing = self.users.get(oid)
        if existing:
            existing.update(user_data)
            existing["last_login"] = now
            existing["updated_at"] = now
            return existing
        else:
            user_data["id"] = oid
            user_data["created_at"] = now
            user_data["last_login"] = now
            user_data["updated_at"] = now
            self.users[oid] = user_data
            return user_data

    def get_user(self, user_id: str) -> dict | None:
        return self.users.get(user_id)

    # ─── Repos ───────────────────────────────────────────────────────

    def store_repo(self, user_id: str, repo_data: dict) -> dict:
        """Save cloned repo metadata linked to a user."""
        repo_id = repo_data.get("id", f"REPO-{str(uuid.uuid4())[:8].upper()}")
        repo_data["id"] = repo_id
        repo_data["user_id"] = user_id
        repo_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.repos[repo_id] = repo_data
        return repo_data

    def get_user_repos(self, user_id: str) -> list[dict]:
        return sorted(
            [r for r in self.repos.values() if r.get("user_id") == user_id],
            key=lambda r: r.get("created_at", ""),
            reverse=True,
        )

    def get_repo(self, repo_id: str) -> dict | None:
        return self.repos.get(repo_id)

    # ─── History ─────────────────────────────────────────────────────

    def create_history_entry(self, user_id: str, entry_data: dict) -> dict:
        """Record a pipeline run in history."""
        entry_id = entry_data.get("id", f"HIS-{str(uuid.uuid4())[:8].upper()}")
        entry_data["id"] = entry_id
        entry_data["user_id"] = user_id
        entry_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.history[entry_id] = entry_data
        return entry_data

    def get_user_history(self, user_id: str) -> list[dict]:
        return sorted(
            [h for h in self.history.values() if h.get("user_id") == user_id],
            key=lambda h: h.get("created_at", ""),
            reverse=True,
        )

    def get_history_entry(self, entry_id: str) -> dict | None:
        return self.history.get(entry_id)

    def update_history_entry(self, entry_id: str, updates: dict) -> dict:
        if entry_id not in self.history:
            raise ValueError(f"History entry {entry_id} not found")
        self.history[entry_id].update(updates)
        self.history[entry_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self.history[entry_id]


class CosmosDBStore:
    """Azure Cosmos DB session store with users, repos, and history."""

    def __init__(self):
        endpoint = os.environ["AZURE_COSMOS_ENDPOINT"]
        key = os.environ["AZURE_COSMOS_KEY"]
        db_name = os.environ.get("AZURE_COSMOS_DB_NAME", "phoenix")

        self.client = CosmosClient(endpoint, key)
        self.database = self.client.create_database_if_not_exists(db_name)

        # Containers
        self.container = self.database.create_container_if_not_exists(
            id="sessions",
            partition_key=PartitionKey(path="/id"),
        )
        self.users_container = self.database.create_container_if_not_exists(
            id="users",
            partition_key=PartitionKey(path="/id"),
        )
        self.repos_container = self.database.create_container_if_not_exists(
            id="repos",
            partition_key=PartitionKey(path="/user_id"),
        )
        self.history_container = self.database.create_container_if_not_exists(
            id="history",
            partition_key=PartitionKey(path="/user_id"),
        )

    # ─── Sessions ────────────────────────────────────────────────────

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

    # ─── Users ───────────────────────────────────────────────────────

    def create_or_update_user(self, user_data: dict) -> dict:
        oid = user_data.get("oid", "")
        now = datetime.now(timezone.utc).isoformat()

        try:
            existing = self.users_container.read_item(oid, partition_key=oid)
            existing.update(user_data)
            existing["last_login"] = now
            existing["updated_at"] = now
            self.users_container.upsert_item(existing)
            return existing
        except exceptions.CosmosResourceNotFoundError:
            user_data["id"] = oid
            user_data["created_at"] = now
            user_data["last_login"] = now
            user_data["updated_at"] = now
            self.users_container.create_item(user_data)
            return user_data

    def get_user(self, user_id: str) -> dict | None:
        try:
            return self.users_container.read_item(user_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None

    # ─── Repos ───────────────────────────────────────────────────────

    def store_repo(self, user_id: str, repo_data: dict) -> dict:
        repo_id = repo_data.get("id", f"REPO-{str(uuid.uuid4())[:8].upper()}")
        repo_data["id"] = repo_id
        repo_data["user_id"] = user_id
        repo_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.repos_container.create_item(repo_data)
        return repo_data

    def get_user_repos(self, user_id: str) -> list[dict]:
        items = list(self.repos_container.query_items(
            query="SELECT * FROM c WHERE c.user_id = @uid ORDER BY c.created_at DESC",
            parameters=[{"name": "@uid", "value": user_id}],
            partition_key=user_id,
        ))
        return items

    def get_repo(self, repo_id: str) -> dict | None:
        try:
            items = list(self.repos_container.query_items(
                query="SELECT * FROM c WHERE c.id = @id",
                parameters=[{"name": "@id", "value": repo_id}],
                enable_cross_partition_query=True,
            ))
            return items[0] if items else None
        except exceptions.CosmosResourceNotFoundError:
            return None

    # ─── History ─────────────────────────────────────────────────────

    def create_history_entry(self, user_id: str, entry_data: dict) -> dict:
        entry_id = entry_data.get("id", f"HIS-{str(uuid.uuid4())[:8].upper()}")
        entry_data["id"] = entry_id
        entry_data["user_id"] = user_id
        entry_data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.history_container.create_item(entry_data)
        return entry_data

    def get_user_history(self, user_id: str) -> list[dict]:
        items = list(self.history_container.query_items(
            query="SELECT * FROM c WHERE c.user_id = @uid ORDER BY c.created_at DESC",
            parameters=[{"name": "@uid", "value": user_id}],
            partition_key=user_id,
        ))
        return items

    def get_history_entry(self, entry_id: str) -> dict | None:
        try:
            items = list(self.history_container.query_items(
                query="SELECT * FROM c WHERE c.id = @id",
                parameters=[{"name": "@id", "value": entry_id}],
                enable_cross_partition_query=True,
            ))
            return items[0] if items else None
        except exceptions.CosmosResourceNotFoundError:
            return None

    def update_history_entry(self, entry_id: str, updates: dict) -> dict:
        entry = self.get_history_entry(entry_id)
        if not entry:
            raise ValueError(f"History entry {entry_id} not found")
        entry.update(updates)
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.history_container.upsert_item(entry)
        return entry


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

