# app.py
"""Phoenix Web Application — Flask + SocketIO backend."""

import os
import uuid
import asyncio
import threading
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from services.github_service import clone_repo, analyze_repo_files, create_pull_request, parse_repo_url
from services.llm_service import get_available_models
from services.azure_db_service import get_db
from services import phoenix_engine

app = Flask(__name__, static_folder="web/dist", static_url_path="/")
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

db = get_db()

# In-memory storage for active pipeline sessions
active_sessions = {}


# ─── REST Endpoints ─────────────────────────────────────────────────────


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "version": "v2.5.0-WEB"})


@app.route("/api/models", methods=["GET"])
def list_models():
    """Return available LLM models."""
    models = get_available_models()
    return jsonify({"models": models})


@app.route("/api/start-project", methods=["POST"])
def start_project():
    """
    Start a new project analysis.
    Expects: { repo_url, llm_model, global_context }
    Returns: { session_id, files[] }
    """
    data = request.json
    repo_url = data.get("repo_url", "").strip()
    llm_model = data.get("llm_model", "gpt-4o")
    global_context = data.get("global_context", "")

    if not repo_url:
        return jsonify({"error": "Repository URL is required"}), 400

    # Validate URL
    try:
        parse_repo_url(repo_url)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Create session
    session_id = f"PX-{str(uuid.uuid4())[:8].upper()}"
    session = db.create_session({
        "id": session_id,
        "repo_url": repo_url,
        "llm_model": llm_model,
        "global_context": global_context,
        "status": "cloning",
    })

    # Clone the repo
    try:
        repo_dir = clone_repo(repo_url)
    except Exception as e:
        db.update_session(session_id, {"status": "error", "error": str(e)})
        return jsonify({"error": f"Failed to clone repository: {str(e)}"}), 500

    # Analyze files
    files = analyze_repo_files(repo_dir)

    db.update_session(session_id, {
        "status": "analyzing",
        "repo_dir": repo_dir,
        "files": files,
    })

    active_sessions[session_id] = {
        "repo_dir": repo_dir,
        "llm_model": llm_model,
        "global_context": global_context,
        "files": files,
        "file_contexts": {},
    }

    return jsonify({
        "session_id": session_id,
        "files": files,
        "total_functions": sum(f["function_count"] for f in files),
        "total_testable": sum(f["testable_count"] for f in files),
    })


@app.route("/api/submit-context", methods=["POST"])
def submit_context():
    """
    Submit per-file context and start the pipeline.
    Expects: { session_id, file_contexts: { path: context_string } }
    """
    data = request.json
    session_id = data.get("session_id")
    file_contexts = data.get("file_contexts", {})

    if not session_id or session_id not in active_sessions:
        return jsonify({"error": "Invalid session ID"}), 400

    session = active_sessions[session_id]
    session["file_contexts"] = file_contexts

    db.update_session(session_id, {
        "status": "pipeline_running",
        "file_contexts": file_contexts,
    })

    # Start pipeline in background thread
    def run_bg():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                phoenix_engine.run_pipeline(
                    session_id=session_id,
                    repo_dir=session["repo_dir"],
                    file_contexts=file_contexts,
                    llm_model=session["llm_model"],
                    socketio=socketio,
                    db=db,
                )
            )
            active_sessions[session_id]["result"] = result
        except Exception as e:
            print(f"[ERROR] Pipeline failed: {e}")
            socketio.emit("pipeline_error", {
                "session_id": session_id,
                "error": str(e),
            })
            db.update_session(session_id, {"status": "error", "error": str(e)})
        finally:
            loop.close()

    thread = threading.Thread(target=run_bg, daemon=True)
    thread.start()

    return jsonify({"status": "pipeline_started", "session_id": session_id})


@app.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id):
    """Get session status and data."""
    session = db.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)


@app.route("/api/approve", methods=["POST"])
def approve_tests():
    """User approves the generated tests."""
    data = request.json
    session_id = data.get("session_id")

    if not session_id:
        return jsonify({"error": "Session ID required"}), 400

    db.update_session(session_id, {"status": "approved", "user_approved": True})
    return jsonify({"status": "approved"})


@app.route("/api/reject", methods=["POST"])
def reject_tests():
    """User rejects with comments — triggers re-generation."""
    data = request.json
    session_id = data.get("session_id")
    comments = data.get("comments", "")

    if not session_id:
        return jsonify({"error": "Session ID required"}), 400

    db.update_session(session_id, {
        "status": "revision_requested",
        "user_comments": comments,
    })

    # TODO: Re-trigger pipeline with user comments as additional context
    return jsonify({"status": "revision_requested", "comments": comments})


@app.route("/api/download/<session_id>", methods=["GET"])
def download_artifacts(session_id):
    """Download generated test files and docs as a zip."""
    import zipfile
    import tempfile

    session = active_sessions.get(session_id)
    result = session.get("result", {}) if session else {}

    test_files = result.get("test_files", {})
    doc_files = result.get("doc_files", {})

    if not test_files and not doc_files:
        return jsonify({"error": "No artifacts found"}), 404

    # Create zip file
    zip_path = os.path.join(tempfile.gettempdir(), f"phoenix_{session_id}.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for fname, content in test_files.items():
            zf.writestr(f"tests/{fname}", content)
        for fname, content in doc_files.items():
            zf.writestr(f"docs/{fname}", content)

    return send_file(zip_path, as_attachment=True, download_name=f"phoenix_{session_id}.zip")


@app.route("/api/create-pr", methods=["POST"])
def create_pr():
    """Create a GitHub PR with the generated test suite and docs."""
    data = request.json
    session_id = data.get("session_id")
    github_token = data.get("github_token")
    branch_name = data.get("branch_name", f"phoenix/test-suite-{session_id}")

    if not session_id or not github_token:
        return jsonify({"error": "Session ID and GitHub token required"}), 400

    session_data = db.get_session(session_id)
    if not session_data:
        return jsonify({"error": "Session not found"}), 404

    session = active_sessions.get(session_id, {})
    result = session.get("result", {})

    test_files = result.get("test_files", {})
    doc_files = result.get("doc_files", {})

    if not test_files:
        return jsonify({"error": "No test files to push"}), 400

    # Build file dict for PR
    files = {}
    for fname, content in test_files.items():
        files[f"tests/{fname}"] = content
    for fname, content in doc_files.items():
        files[f"docs/{fname}"] = content

    try:
        pr_result = create_pull_request(
            repo_url=session_data["repo_url"],
            token=github_token,
            branch_name=branch_name,
            title=f"🔥 Phoenix: Auto-generated regression test suite",
            body=(
                f"## Phoenix Test Suite\n\n"
                f"Auto-generated by Phoenix multi-agent system.\n\n"
                f"**Session:** `{session_id}`\n"
                f"**Test files:** {len(test_files)}\n"
                f"**Documentation files:** {len(doc_files)}\n\n"
                f"### Files included:\n"
                + "\n".join(f"- `{f}`" for f in files.keys())
            ),
            files=files,
        )
        return jsonify({"status": "pr_created", **pr_result})
    except Exception as e:
        return jsonify({"error": f"Failed to create PR: {str(e)}"}), 500


@app.route("/api/results/<session_id>", methods=["GET"])
def get_results(session_id):
    """Get the pipeline results for a session."""
    session = active_sessions.get(session_id, {})
    result = session.get("result")
    if not result:
        db_session = db.get_session(session_id)
        if db_session and "artifacts" in db_session:
            return jsonify(db_session["artifacts"])
        return jsonify({"error": "Results not ready yet"}), 404
    return jsonify(result)


# ─── WebSocket Events ───────────────────────────────────────────────────


@socketio.on("connect")
def handle_connect():
    print(f"[WS] Client connected: {request.sid}")
    emit("connected", {"message": "Connected to Phoenix server"})


@socketio.on("disconnect")
def handle_disconnect():
    print(f"[WS] Client disconnected: {request.sid}")


@socketio.on("join_session")
def handle_join_session(data):
    session_id = data.get("session_id")
    if session_id:
        print(f"[WS] Client joined session: {session_id}")
        emit("session_joined", {"session_id": session_id})


# ─── Main ───────────────────────────────────────────────────────────────

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path.startswith("api/") or path.startswith("socket.io"):
        return jsonify({"error": "Not Found"}), 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    import os as _os
    print("\n╔══════════════════════════════════════════════╗")
    print("║   PHOENIX WEB SERVER — v2.5.0-WEB           ║")
    print("║   http://localhost:5000                      ║")
    print("╚══════════════════════════════════════════════╝\n")

    # Exclude generated_tests/ and /tmp/ from the auto-reloader so that
    # writing test/doc files doesn't restart the server and wipe active_sessions.
    exclude = [
        _os.path.abspath("generated_tests") + "/*",
        "/tmp/*",
    ]
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True,
        use_reloader=True,
        reloader_type="stat",
        exclude_patterns=exclude,
    )
