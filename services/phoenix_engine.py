# services/phoenix_engine.py
"""
Phoenix orchestration engine — refactored for per-file sequential processing.
Each file gets its own GroupChat: Observer → QA → Critic (→ fix loop) → Doc_Writer.
This guarantees every file completes fully, regardless of repo size.
"""

import os
import ast
import glob
import json
import shutil
import asyncio
from datetime import datetime, timezone


GENERATED_TESTS_BASE = os.path.abspath("generated_tests")


def discover_python_files(repo_dir: str) -> list[str]:
    """Discover all Python files in a repository directory."""
    pattern = os.path.join(repo_dir, "**", "*.py")
    abs_paths = glob.glob(pattern, recursive=True)
    return sorted(
        p for p in abs_paths
        if "__pycache__" not in p
        and os.path.basename(p) != "__init__.py"
        and ".venv" not in p
        and "node_modules" not in p
    )


def extract_functions(file_path: str) -> list[dict]:
    """Parse a Python file's AST to extract function definitions."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    functions = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            uses_input = any(
                isinstance(n, ast.Call)
                and isinstance(getattr(n, "func", None), ast.Name)
                and n.func.id == "input"
                for n in ast.walk(node)
            )
            functions.append({
                "name": node.name,
                "args": args,
                "testable": not uses_input,
                "reason": "uses input()" if uses_input else "ok",
            })

    return functions


def prepare_workspace(session_id: str, repo_dir: str) -> str:
    """
    Prepare the legacy_workspace for a session by symlinking/copying
    repo files into a session-specific workspace.
    """
    workspace_dir = os.path.join(GENERATED_TESTS_BASE, session_id, "workspace")
    output_dir = os.path.join(GENERATED_TESTS_BASE, session_id, "output")
    os.makedirs(workspace_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Copy Python files from the repo to the workspace
    py_files = discover_python_files(repo_dir)
    for src_path in py_files:
        rel = os.path.relpath(src_path, repo_dir)
        dst_path = os.path.join(workspace_dir, rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

    # Also copy non-Python data files that might be needed
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ("__pycache__", "venv", ".venv", "node_modules")]
        for fname in files:
            if fname.endswith((".txt", ".csv", ".json", ".yaml", ".yml", ".cfg", ".ini")):
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, repo_dir)
                dst = os.path.join(workspace_dir, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)

    return workspace_dir


def build_single_file_briefing(file_path: str, file_context: str = "") -> str:
    """Generate a mission briefing for a SINGLE file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    funcs = extract_functions(file_path)
    testable = [fn for fn in funcs if fn["testable"]]
    skipped = [fn for fn in funcs if not fn["testable"]]

    func_list = ""
    for fn in testable:
        args_str = ", ".join(fn["args"])
        func_list += f"       - {fn['name']}({args_str})  [TESTABLE]\n"
    for fn in skipped:
        args_str = ", ".join(fn["args"])
        func_list += f"       - {fn['name']}({args_str})  [SKIP: {fn['reason']}]\n"

    context_block = f"\n    [HUMAN INSTRUCTIONS FOR THIS FILE]:\n    {file_context}\n" if file_context else ""

    mod_name = os.path.basename(file_path).replace(".py", "")

    return f"""
    Team Phoenix,

    We need to modernize the following undocumented legacy script.
    The source code and function list are provided below — do NOT waste tool calls reading files.

    === {file_path} ==={context_block}
    Functions found:
{func_list}
    Source code:
    ```python
{source}
    ```

    Workflow:
    1. Observer:
       - Call `observe_file` ONCE for this file.
       - Just pass the file path: observe_file("{file_path}")
       - The tool handles test input generation and runtime capture automatically.
       - Write a summary of what was captured.

    2. QA Engineer:
       - Call `generate_tests` for this module:
         generate_tests(module_name="{mod_name}", legacy_file_path="{file_path}")
       - Write a summary listing what test files were generated.

    3. Critic:
       - Call `verify_all_tests(dummy="")` to run the test suite in the sandbox.
       - If all pass, end your message with: PHOENIX_APPROVED
       - If any fail, describe what needs fixing for the QA Engineer.

    4. Doc_Writer (after Critic approves):
       - Call `generate_docs` for this file:
         generate_docs(legacy_file_path="{file_path}")
       - Write a summary of what documentation was generated.
       - End your message with: PHOENIX_DOCS_COMPLETE
    """


async def run_pipeline(
    session_id: str,
    repo_dir: str,
    file_contexts: dict,
    llm_model: str,
    socketio=None,
    db=None,
):
    """
    Run the full Phoenix multi-agent pipeline.
    Processes each file through its own GroupChat sequentially.
    Emits WebSocket events to track progress.
    """
    from agents.observer import observer_agent
    from agents.qa_engineer import qa_engineer_agent
    from agents.critic import critic_agent
    from agents.doc_writer import doc_writer_agent
    from agent_framework.orchestrations import GroupChatBuilder, GroupChatState

    def emit(event: str, data: dict):
        if socketio:
            socketio.emit(event, {**data, "session_id": session_id})

    def update_db(updates: dict):
        if db:
            try:
                db.update_session(session_id, updates)
            except Exception as e:
                print(f"[DB] Warning: {e}")

    emit("agent_progress", {
        "stage": "preparing",
        "message": "Preparing workspace and analyzing files...",
        "progress": 5,
    })

    # Prepare workspace
    workspace_dir = prepare_workspace(session_id, repo_dir)
    legacy_files = discover_python_files(workspace_dir)
    output_dir = os.path.join(GENERATED_TESTS_BASE, session_id, "output")

    if not legacy_files:
        emit("pipeline_error", {"message": "No Python files found in the repository."})
        update_db({"status": "error", "error": "No Python files found"})
        return

    # Filter to files that have testable functions
    files_to_process = []
    for fpath in legacy_files:
        funcs = extract_functions(fpath)
        testable = [fn for fn in funcs if fn["testable"]]
        if testable:
            files_to_process.append(fpath)
        else:
            print(f"[SYSTEM] Skipping {os.path.basename(fpath)} — no testable functions")

    if not files_to_process:
        emit("pipeline_error", {"message": "No testable functions found in any Python files."})
        update_db({"status": "error", "error": "No testable functions found"})
        return

    total_files = len(files_to_process)
    emit("agent_progress", {
        "stage": "analyzing",
        "message": f"Found {total_files} Python files with testable functions",
        "files": [os.path.relpath(f, workspace_dir) for f in files_to_process],
        "progress": 10,
    })

    # Clear old captures
    captures_file = os.path.join(output_dir, "observer_captures.json")
    if os.path.exists(captures_file):
        os.remove(captures_file)

    update_db({"status": "running", "started_at": datetime.now(timezone.utc).isoformat()})

    # ─── Per-file sequential processing ─────────────────────────────────
    all_test_files = {}
    all_doc_files = {}
    all_conversation_log = []

    for file_idx, file_path in enumerate(files_to_process):
        file_name = os.path.basename(file_path)
        file_num = file_idx + 1
        base_progress = 10 + int(85 * file_idx / total_files)

        print(f"\n{'='*60}")
        print(f"[SYSTEM] Processing file {file_num}/{total_files}: {file_name}")
        print(f"{'='*60}\n")

        emit("agent_progress", {
            "stage": "processing",
            "message": f"Processing file {file_num}/{total_files}: {file_name}",
            "current_file": file_name,
            "file_index": file_idx,
            "total_files": total_files,
            "progress": base_progress,
        })

        # Build single-file mission briefing
        file_context = file_contexts.get(file_path, "")
        mission_briefing = build_single_file_briefing(file_path, file_context)

        # ─── Router for this file's GroupChat ───────────────────────────
        def make_router(fname):
            """Create a router closure for one file."""
            def round_robin_router(state: GroupChatState):
                order = ["Observer", "QA_Engineer", "Critic"]

                if state.current_round < len(order):
                    agent = order[state.current_round]
                    stage_map = {
                        "Observer": ("observing", f"[{fname}] Observer capturing runtime behavior...", base_progress + 5),
                        "QA_Engineer": ("generating", f"[{fname}] QA Engineer generating tests (LLM)...", base_progress + 10),
                        "Critic": ("validating", f"[{fname}] Critic validating tests in sandbox...", base_progress + 15),
                    }
                    stage, msg, prog = stage_map.get(agent, ("running", f"{agent} working...", base_progress + 10))
                    emit("agent_progress", {"stage": stage, "agent": agent, "message": msg, "progress": prog})
                    return agent

                # Check for critic approval → hand off to Doc_Writer
                for msg in reversed(state.conversation):
                    text = getattr(msg, "text", None) or getattr(msg, "content", None) or ""
                    if "PHOENIX_APPROVED" in text:
                        emit("agent_progress", {
                            "stage": "documenting",
                            "agent": "Doc_Writer",
                            "message": f"[{fname}] Critic approved! Generating documentation...",
                            "progress": base_progress + 18,
                        })
                        return "Doc_Writer"

                # Otherwise keep looping QA_Engineer ↔ Critic
                iteration = (state.current_round - len(order)) % 2
                agent = "QA_Engineer" if iteration == 0 else "Critic"
                emit("agent_progress", {
                    "stage": "fixing",
                    "agent": agent,
                    "message": f"[{fname}] Fix iteration — {agent} working...",
                    "progress": base_progress + 12,
                })
                return agent
            return round_robin_router

        def should_terminate(messages: list) -> bool:
            if not messages:
                return False
            for msg in reversed(messages):
                author = getattr(msg, "author_name", None) or getattr(msg, "name", "")
                if not author or author == "System":
                    continue
                text = getattr(msg, "text", None) or getattr(msg, "content", None) or ""
                if "PHOENIX_DOCS_COMPLETE" in text:
                    return True
                return False
            return False

        workflow = GroupChatBuilder(
            participants=[observer_agent, qa_engineer_agent, critic_agent, doc_writer_agent],
            selection_func=make_router(file_name),
            termination_condition=should_terminate,
            max_rounds=10,
        ).build()

        # Run with retry for rate limits
        import time
        max_retries = 2
        result = None
        for attempt in range(max_retries + 1):
            try:
                result = await workflow.run(mission_briefing)
                break
            except Exception as err:
                err_str = str(err)
                if ("429" in err_str or "RateLimitReached" in err_str or "rate limit" in err_str.lower()):
                    if attempt < max_retries:
                        wait_secs = 65 * (attempt + 1)
                        print(f"[SYSTEM] Rate limit for {file_name} — waiting {wait_secs}s...")
                        emit("agent_progress", {
                            "stage": "waiting",
                            "message": f"Rate limit reached on {file_name}. Retrying in {wait_secs}s...",
                            "progress": base_progress,
                        })
                        time.sleep(wait_secs)
                        continue
                print(f"[ERROR] Pipeline failed for {file_name}: {err}")
                break

        # Collect conversation from this file's GroupChat
        if result:
            for messages in result.get_outputs():
                for msg in messages:
                    author = getattr(msg, "author_name", None) or getattr(msg, "name", "Agent")
                    content = getattr(msg, "text", None) or getattr(msg, "content", None)

                    if not content and hasattr(msg, "contents") and msg.contents:
                        parts = []
                        for c in msg.contents:
                            t = getattr(c, "text", None) or getattr(c, "value", None) or str(c)
                            if t:
                                parts.append(str(t))
                        content = "\n".join(parts) if parts else None

                    if content:
                        all_conversation_log.append({
                            "author": author,
                            "file": file_name,
                            "content": content,
                        })

        # Collect generated test files after this file's processing
        for tf in glob.glob(os.path.join(GENERATED_TESTS_BASE, "test_*.py")):
            fname_test = os.path.basename(tf)
            if fname_test not in all_test_files:
                with open(tf, "r") as f:
                    all_test_files[fname_test] = f.read()

        for tf in glob.glob(os.path.join(output_dir, "test_*.py")):
            fname_test = os.path.basename(tf)
            if fname_test not in all_test_files:
                with open(tf, "r") as f:
                    all_test_files[fname_test] = f.read()

        # Collect generated doc files
        for df in glob.glob(os.path.join(GENERATED_TESTS_BASE, "docs_*.md")):
            fname_doc = os.path.basename(df)
            if fname_doc not in all_doc_files:
                with open(df, "r") as f:
                    all_doc_files[fname_doc] = f.read()

        for df in glob.glob(os.path.join(output_dir, "docs_*.md")):
            fname_doc = os.path.basename(df)
            if fname_doc not in all_doc_files:
                with open(df, "r") as f:
                    all_doc_files[fname_doc] = f.read()

        print(f"[SYSTEM] ✓ Completed {file_name} ({file_num}/{total_files})")

    # ─── Fallback: Generate docs for any files that didn't get docs ──────
    mod_names_with_docs = {f.replace("docs_", "").replace(".md", "") for f in all_doc_files}
    for file_path in files_to_process:
        mod_name = os.path.basename(file_path).replace(".py", "")
        if mod_name not in mod_names_with_docs:
            print(f"[SYSTEM] Running fallback doc generation for {mod_name}...")
            emit("agent_progress", {
                "stage": "documenting",
                "message": f"Generating documentation for {mod_name} (fallback)...",
                "progress": 92,
            })
            try:
                from tools.doc_tools import generate_docs as _generate_docs_tool
                _generate_docs_tool.func(legacy_file_path=file_path)
            except Exception as doc_err:
                print(f"[SYSTEM] Doc generation failed for {file_path}: {doc_err}")

    # Re-collect doc files after fallback
    for df in glob.glob(os.path.join(GENERATED_TESTS_BASE, "docs_*.md")):
        fname_doc = os.path.basename(df)
        if fname_doc not in all_doc_files:
            with open(df, "r") as f:
                all_doc_files[fname_doc] = f.read()

    results = {
        "session_id": session_id,
        "status": "completed",
        "test_files": all_test_files,
        "doc_files": all_doc_files,
        "conversation_log": all_conversation_log,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    update_db({
        "status": "completed",
        "completed_at": results["completed_at"],
        "artifacts": {"test_files": all_test_files, "doc_files": all_doc_files},
    })

    emit("pipeline_complete", results)
    emit("agent_progress", {
        "stage": "complete",
        "message": f"Pipeline complete! Processed {total_files} files — {len(all_test_files)} test suites, {len(all_doc_files)} docs.",
        "progress": 100,
    })

    return results
