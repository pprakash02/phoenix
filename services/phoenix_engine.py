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
from services.blob_service import get_blob, CONTAINER_REPOS, CONTAINER_ARTIFACTS


GENERATED_TESTS_BASE = os.path.abspath("generated_tests")


COBOL_EXTENSIONS = ('.cob', '.cbl', '.cpy')
C_EXTENSIONS = ('.c', '.h')


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


def discover_cobol_files(repo_dir: str) -> list[str]:
    """Discover all COBOL files in a repository directory (case-insensitive)."""
    cobol_files = []
    for root, dirs, filenames in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ("__pycache__", "venv", ".venv", "node_modules", "env")]
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() in COBOL_EXTENSIONS:
                cobol_files.append(os.path.join(root, fname))
    return sorted(cobol_files)


def discover_c_files(repo_dir: str) -> list[str]:
    """Discover all C source files in a repository directory (case-insensitive)."""
    c_files = []
    for root, dirs, filenames in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ("__pycache__", "venv", ".venv", "node_modules", "env",
                    "build", "cmake-build-debug", "cmake-build-release")]
        for fname in filenames:
            if os.path.splitext(fname)[1].lower() in C_EXTENSIONS:
                c_files.append(os.path.join(root, fname))
    return sorted(c_files)


def extract_c_functions(file_path: str) -> list[dict]:
    """Extract C function definitions from a source file using regex.
    Returns a list of dicts with name, args, return_type, testable."""
    import re
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    # Remove single-line and multi-line comments to avoid false matches
    source_clean = re.sub(r'//.*?$', '', source, flags=re.MULTILINE)
    source_clean = re.sub(r'/\*.*?\*/', '', source_clean, flags=re.DOTALL)

    functions = []
    seen = set()

    # Match C function definitions: return_type name(params) {
    # Handles: int foo(int a, char *b) {
    # Avoids: if(...), while(...), for(...), switch(...), #define, etc.
    c_keywords = {'if', 'else', 'while', 'for', 'switch', 'return', 'sizeof',
                  'typedef', 'struct', 'enum', 'union', 'case', 'do'}

    pattern = re.compile(
        r'^\s*'
        r'((?:(?:static|extern|inline|const|unsigned|signed|long|short|volatile|register)\s+)*'
        r'(?:void|int|char|float|double|long|short|unsigned|signed|size_t|ssize_t|'
        r'bool|_Bool|int8_t|int16_t|int32_t|int64_t|uint8_t|uint16_t|uint32_t|uint64_t|'
        r'FILE|struct\s+\w+|enum\s+\w+|\w+_t)'
        r'(?:\s*\*+)?\s+)'
        r'(\w+)'
        r'\s*\(([^)]*)\)'
        r'\s*\{',
        re.MULTILINE
    )

    for match in pattern.finditer(source_clean):
        return_type = match.group(1).strip()
        func_name = match.group(2)
        params_str = match.group(3).strip()

        if func_name in c_keywords or func_name in seen:
            continue
        if func_name.startswith('_') and func_name.startswith('__'):
            continue

        seen.add(func_name)

        # Parse parameters
        args = []
        if params_str and params_str != 'void':
            for param in params_str.split(','):
                param = param.strip()
                if param:
                    # Extract just the parameter name (last word)
                    parts = param.replace('*', ' ').split()
                    if parts:
                        args.append(parts[-1] if len(parts) > 1 else param)

        # main() is not testable in the usual sense
        is_main = (func_name == 'main')

        functions.append({
            "name": func_name,
            "args": args,
            "return_type": return_type,
            "testable": not is_main,
            "type": "function",
        })

    return functions



# All standard COBOL reserved words, verbs, and division/section names to exclude
COBOL_RESERVED_WORDS = frozenset({
    # Divisions and sections
    'IDENTIFICATION', 'ENVIRONMENT', 'DATA', 'PROCEDURE',
    'FILE', 'WORKING-STORAGE', 'LINKAGE', 'SCREEN', 'REPORT',
    'INPUT-OUTPUT', 'CONFIGURATION', 'FILE-CONTROL', 'I-O-CONTROL',
    'LOCAL-STORAGE', 'COMMUNICATION',
    # Standard verbs / statements
    'ACCEPT', 'ADD', 'ALTER', 'CALL', 'CANCEL', 'CLOSE', 'COMPUTE',
    'CONTINUE', 'DELETE', 'DISPLAY', 'DIVIDE', 'ENTRY', 'EVALUATE',
    'EXIT', 'GENERATE', 'GO', 'GOBACK', 'IF', 'INITIALIZE', 'INITIATE',
    'INSPECT', 'MERGE', 'MOVE', 'MULTIPLY', 'OPEN', 'PERFORM',
    'READ', 'RELEASE', 'RETURN', 'REWRITE', 'SEARCH', 'SET',
    'SORT', 'START', 'STOP', 'STRING', 'SUBTRACT', 'TERMINATE',
    'UNSTRING', 'USE', 'WRITE', 'EXEC', 'END-EXEC',
    # Control / scope terminators
    'END-IF', 'END-EVALUATE', 'END-PERFORM', 'END-READ', 'END-WRITE',
    'END-COMPUTE', 'END-SEARCH', 'END-CALL', 'END-DELETE',
    'END-MULTIPLY', 'END-DIVIDE', 'END-ADD', 'END-SUBTRACT',
    'END-STRING', 'END-UNSTRING', 'END-RETURN', 'END-REWRITE',
    'END-START', 'END-ACCEPT', 'END-DISPLAY',
    # Common reserved words
    'PROGRAM-ID', 'AUTHOR', 'DATE-WRITTEN', 'DATE-COMPILED',
    'SECURITY', 'REMARKS', 'INSTALLATION',
    'SECTION', 'DIVISION', 'PARAGRAPH', 'COPY', 'REPLACE',
    'FD', 'SD', 'RD', 'CD', 'PIC', 'PICTURE', 'VALUE', 'VALUES',
    'REDEFINES', 'RENAMES', 'OCCURS', 'DEPENDING', 'ASCENDING',
    'DESCENDING', 'INDEXED', 'FILLER', 'SPACES', 'ZEROS', 'ZEROES',
    'HIGH-VALUES', 'LOW-VALUES', 'QUOTES', 'ALL',
    'WHEN', 'OTHER', 'THRU', 'THROUGH', 'GIVING', 'REMAINDER',
    'ROUNDED', 'SIZE', 'ERROR', 'OVERFLOW', 'NOT',
    'TRUE', 'FALSE', 'ALSO', 'ANY',
    'CORRESPONDING', 'CORR', 'TALLYING', 'REPLACING', 'LEADING',
    'TRAILING', 'FIRST', 'INITIAL', 'REFERENCE', 'CONTENT',
    'BY', 'INTO', 'FROM', 'TO', 'UNTIL', 'VARYING', 'AFTER',
    'BEFORE', 'WITH', 'TEST', 'POINTER', 'DELIMITED',
    'ON', 'OFF', 'OPTIONAL', 'STANDARD', 'NATIVE',
    'SELECT', 'ASSIGN', 'ORGANIZATION', 'ACCESS', 'MODE',
    'SEQUENTIAL', 'RANDOM', 'DYNAMIC', 'RELATIVE', 'STATUS',
    'RECORD', 'RECORDS', 'BLOCK', 'CONTAINS', 'LABEL',
    'OMITTED', 'DATA', 'IS', 'ARE', 'THAN', 'EQUAL',
    'GREATER', 'LESS', 'POSITIVE', 'NEGATIVE', 'NUMERIC',
    'ALPHABETIC', 'ALPHABETIC-LOWER', 'ALPHABETIC-UPPER',
    'CLASS', 'CONDITION', 'UPON', 'ADVANCING', 'PAGE',
    'LINE', 'LINES', 'AT', 'END', 'OF',
    'RUN', 'STOP-RUN',
})


def extract_cobol_paragraphs(file_path: str) -> list[dict]:
    """Extract user-defined COBOL paragraph and section names from a COBOL source file.
    Filters out all standard COBOL reserved words, verbs, and built-in constructs."""
    import re
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    paragraphs = []
    seen = set()

    # Match sections (e.g. "MAIN-LOGIC SECTION.")
    for match in re.finditer(r'^\s{0,7}([A-Z0-9][A-Z0-9-]{0,29})\s+(SECTION)\s*\.', source, re.MULTILINE | re.IGNORECASE):
        name = match.group(1).upper()
        if name not in COBOL_RESERVED_WORDS and name not in seen:
            seen.add(name)
            paragraphs.append({"name": match.group(1), "args": [], "testable": True, "type": "section"})

    # Match paragraphs (label on its own line ending with a period)
    for match in re.finditer(r'^\s{7,11}([A-Z0-9][A-Z0-9-]{0,29})\s*\.\s*$', source, re.MULTILINE | re.IGNORECASE):
        name = match.group(1).upper()
        if name not in COBOL_RESERVED_WORDS and name not in seen:
            seen.add(name)
            paragraphs.append({"name": match.group(1), "args": [], "testable": True, "type": "paragraph"})

    return paragraphs



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
    Also uploads repo source files to Azure Blob Storage.
    """
    workspace_dir = os.path.join(GENERATED_TESTS_BASE, session_id, "workspace")
    output_dir = os.path.join(GENERATED_TESTS_BASE, session_id, "output")
    os.makedirs(workspace_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    blob = get_blob()

    # Copy source files from the repo to the workspace
    py_files = discover_python_files(repo_dir)
    cobol_files_list = discover_cobol_files(repo_dir)
    c_files_list = discover_c_files(repo_dir)
    all_source_files = py_files + cobol_files_list + c_files_list
    for src_path in all_source_files:
        rel = os.path.relpath(src_path, repo_dir)
        dst_path = os.path.join(workspace_dir, rel)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        # Upload to blob storage
        try:
            with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
                blob.upload_text(CONTAINER_REPOS, f"{session_id}/{rel}", f.read())
        except Exception as e:
            print(f"[BLOB] Warning: failed to upload {rel}: {e}")

    # Also copy non-Python data files that might be needed
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ("__pycache__", "venv", ".venv", "node_modules")]
        for fname in files:
            if fname.endswith((".txt", ".csv", ".json", ".yaml", ".yml", ".cfg", ".ini", ".h", ".makefile")):
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, repo_dir)
                dst = os.path.join(workspace_dir, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                try:
                    with open(src, "r", encoding="utf-8", errors="ignore") as f:
                        blob.upload_text(CONTAINER_REPOS, f"{session_id}/{rel}", f.read())
                except Exception as e:
                    print(f"[BLOB] Warning: failed to upload {rel}: {e}")

    return workspace_dir


def build_single_file_briefing(file_path: str, file_context: str = "") -> str:
    """Generate a mission briefing for a SINGLE Python file."""
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


def build_single_cobol_briefing(file_path: str, file_context: str = "") -> str:
    """Generate a mission briefing for a SINGLE COBOL file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    paragraphs = extract_cobol_paragraphs(file_path)
    para_list = ""
    for p in paragraphs:
        para_list += f"       - {p['name']}  [{p.get('type', 'paragraph').upper()}]\n"

    context_block = f"\n    [HUMAN INSTRUCTIONS FOR THIS FILE]:\n    {file_context}\n" if file_context else ""

    mod_name = os.path.splitext(os.path.basename(file_path))[0]

    return f"""
    Team Phoenix,

    We need to modernize and document the following COBOL legacy program.
    The source code and structure are provided below.

    === {file_path} ==={context_block}
    COBOL Paragraphs/Sections found:
{para_list}
    Source code:
    ```cobol
{source}
    ```

    Workflow for COBOL files:
    1. Observer:
       - COBOL files cannot be executed directly. Skip runtime capture.
       - Analyze the source code structure and write a detailed summary of:
         * The program's purpose and main data flow
         * Each SECTION and PARAGRAPH's role
         * Data division variables and their usage
         * Any COPY or CALL statements
       - End your message with the analysis summary.

    2. QA Engineer:
       - Call `generate_cobol_tests` for this COBOL module:
         generate_cobol_tests(module_name="{mod_name}", legacy_file_path="{file_path}")
       - This generates a comprehensive test specification document from the COBOL source.
       - Do NOT call `generate_tests` — it requires observer captures which don't exist for COBOL.
       - Write a summary of what was generated.

    3. Critic:
       - Review the test specification for completeness.
       - Verify it covers all paragraphs and data flows.
       - End your message with: PHOENIX_APPROVED

    4. Doc_Writer (after Critic approves):
       - Call `generate_docs` for this file:
         generate_docs(legacy_file_path="{file_path}")
       - Write a summary of what documentation was generated.
       - End your message with: PHOENIX_DOCS_COMPLETE
    """


def build_single_c_briefing(file_path: str, file_context: str = "") -> str:
    """Generate a mission briefing for a SINGLE C source file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    functions = extract_c_functions(file_path)
    func_list = ""
    for fn in functions:
        args_str = ", ".join(fn["args"])
        status = "TESTABLE" if fn["testable"] else "SKIP: main()"
        func_list += f"       - {fn['return_type']} {fn['name']}({args_str})  [{status}]\n"

    context_block = f"\n    [HUMAN INSTRUCTIONS FOR THIS FILE]:\n    {file_context}\n" if file_context else ""

    mod_name = os.path.splitext(os.path.basename(file_path))[0]

    return f"""
    Team Phoenix,

    We need to modernize and test the following C source file.
    The source code and function list are provided below.

    === {file_path} ==={context_block}
    C Functions found:
{func_list}
    Source code:
    ```c
{source}
    ```

    Workflow for C files:
    1. Observer:
       - C files cannot be executed directly like Python. Skip runtime capture.
       - Analyze the source code structure and write a detailed summary of:
         * The program's purpose and main logic flow
         * Each function's role, parameters, and return values
         * Data structures and global variables used
         * Any #include dependencies or external function calls
       - End your message with the analysis summary.

    2. QA Engineer:
       - Call `generate_c_tests` for this C module:
         generate_c_tests(module_name="{mod_name}", legacy_file_path="{file_path}")
       - This generates a comprehensive C test file using assert.h.
       - Do NOT call `generate_tests` — that is for Python only.
       - Write a summary of what was generated.

    3. Critic:
       - Review the generated C test file for completeness.
       - Verify it covers all testable functions with appropriate test cases.
       - End your message with: PHOENIX_APPROVED

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

    if file_contexts is None:
        file_contexts = {}

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
    python_files = discover_python_files(workspace_dir)
    cobol_files = discover_cobol_files(workspace_dir)
    c_files = discover_c_files(workspace_dir)
    output_dir = os.path.join(GENERATED_TESTS_BASE, session_id, "output")

    if not python_files and not cobol_files and not c_files:
        emit("pipeline_error", {"message": "No Python, COBOL, or C files found in the repository."})
        update_db({"status": "error", "error": "No source files found"})
        return

    # Filter Python files to those with testable functions
    files_to_process = []  # list of (path, language)
    for fpath in python_files:
        funcs = extract_functions(fpath)
        testable = [fn for fn in funcs if fn["testable"]]
        if testable:
            files_to_process.append((fpath, 'python'))
        else:
            print(f"[SYSTEM] Skipping {os.path.basename(fpath)} — no testable functions")

    # All COBOL files are processable (documentation + test specs)
    for fpath in cobol_files:
        files_to_process.append((fpath, 'cobol'))

    # Filter C files to those with testable functions
    # Deduplicate: skip .h files if a matching .c file exists (avoids double-processing)
    c_basenames = {os.path.splitext(os.path.basename(f))[0] for f in c_files
                   if f.lower().endswith('.c')}
    for fpath in c_files:
        fname = os.path.basename(fpath)
        base, ext = os.path.splitext(fname)
        # Skip .h files when a matching .c exists (they share the same module)
        if ext.lower() == '.h' and base in c_basenames:
            print(f"[SYSTEM] Skipping {fname} — matching .c file exists")
            continue
        funcs = extract_c_functions(fpath)
        testable = [fn for fn in funcs if fn["testable"]]
        if testable:
            files_to_process.append((fpath, 'c'))
        else:
            print(f"[SYSTEM] Skipping {fname} — no testable C functions")

    if not files_to_process:
        emit("pipeline_error", {"message": "No processable files found."})
        update_db({"status": "error", "error": "No processable files found"})
        return

    total_files = len(files_to_process)
    py_count = sum(1 for _, lang in files_to_process if lang == 'python')
    cob_count = sum(1 for _, lang in files_to_process if lang == 'cobol')
    c_count = sum(1 for _, lang in files_to_process if lang == 'c')
    lang_summary = []
    if py_count: lang_summary.append(f"{py_count} Python")
    if cob_count: lang_summary.append(f"{cob_count} COBOL")
    if c_count: lang_summary.append(f"{c_count} C")

    emit("agent_progress", {
        "stage": "analyzing",
        "message": f"Found {total_files} source files ({', '.join(lang_summary)})",
        "files": [os.path.relpath(f, workspace_dir) for f, _ in files_to_process],
        "progress": 10,
    })

    # Clear old captures and artifacts from previous runs
    captures_file = os.path.join(output_dir, "observer_captures.json")
    if os.path.exists(captures_file):
        os.remove(captures_file)

    for old_test in glob.glob(os.path.join(GENERATED_TESTS_BASE, "test_*.py")):
        os.remove(old_test)
    for old_doc in glob.glob(os.path.join(GENERATED_TESTS_BASE, "docs_*.md")):
        os.remove(old_doc)

    update_db({"status": "running", "started_at": datetime.now(timezone.utc).isoformat()})

    # ─── Per-file sequential processing ─────────────────────────────────
    all_test_files = {}
    all_doc_files = {}
    all_conversation_log = []

    for file_idx, (file_path, file_language) in enumerate(files_to_process):
        file_name = os.path.basename(file_path)
        file_num = file_idx + 1
        base_progress = 10 + int(85 * file_idx / total_files)
        file_progress_cap = 10 + int(85 * (file_idx + 1) / total_files) - 1  # never exceed this for current file
        lang_label = file_language.upper()

        print(f"\n{'='*60}")
        print(f"[SYSTEM] Processing {lang_label} file {file_num}/{total_files}: {file_name}")
        print(f"{'='*60}\n")

        emit("agent_progress", {
            "stage": "processing",
            "message": f"Processing {lang_label} file {file_num}/{total_files}: {file_name}",
            "current_file": file_name,
            "file_index": file_idx,
            "total_files": total_files,
            "progress": min(base_progress, 95),
        })

        # Build single-file mission briefing based on language
        file_context = file_contexts.get(file_path, "")
        if file_language == 'cobol':
            mission_briefing = build_single_cobol_briefing(file_path, file_context)
        elif file_language == 'c':
            mission_briefing = build_single_c_briefing(file_path, file_context)
        else:
            mission_briefing = build_single_file_briefing(file_path, file_context)

        # ─── Router for this file's GroupChat ───────────────────────────
        # C files use a streamlined route: QA_Engineer → Critic → Doc_Writer
        # (Observer is skipped because C has no runtime capture)
        # Python/COBOL: Observer → QA_Engineer → Critic → Doc_Writer
        is_c_file = (file_language == 'c')

        def make_router(fname, c_mode=is_c_file):
            """Create a router closure for one file."""
            def round_robin_router(state: GroupChatState):
                if c_mode:
                    # C streamlined: skip Observer, go QA → Critic → Doc_Writer
                    order = ["QA_Engineer", "Critic"]
                else:
                    order = ["Observer", "QA_Engineer", "Critic"]

                if state.current_round < len(order):
                    agent = order[state.current_round]
                    stage_map = {
                        "Observer": ("observing", f"[{fname}] Observer analyzing source code...", min(base_progress + 5, file_progress_cap)),
                        "QA_Engineer": ("generating", f"[{fname}] QA Engineer generating tests (LLM)...", min(base_progress + 10, file_progress_cap)),
                        "Critic": ("validating", f"[{fname}] Critic validating tests...", min(base_progress + 15, file_progress_cap)),
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
                            "progress": min(base_progress + 18, file_progress_cap),
                        })
                        return "Doc_Writer"

                # Otherwise keep looping QA_Engineer ↔ Critic
                iteration = (state.current_round - len(order)) % 2
                agent = "QA_Engineer" if iteration == 0 else "Critic"
                emit("agent_progress", {
                    "stage": "fixing",
                    "agent": agent,
                    "message": f"[{fname}] Fix iteration — {agent} working...",
                    "progress": min(base_progress + 12, file_progress_cap),
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

        # C files use fewer rounds (no Observer, Critic approves quickly)
        file_max_rounds = 5 if is_c_file else 10

        workflow = GroupChatBuilder(
            participants=[observer_agent, qa_engineer_agent, critic_agent, doc_writer_agent],
            selection_func=make_router(file_name),
            termination_condition=should_terminate,
            max_rounds=file_max_rounds,
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
                            "progress": min(base_progress, 95),
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

        for tf in glob.glob(os.path.join(GENERATED_TESTS_BASE, "test_*.c")):
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

    # ─── Fallback: Generate basic docs for any files that didn't get docs ──────
    # This is a SYNCHRONOUS, non-LLM fallback to avoid deadlocking the event loop.
    mod_names_with_docs = {f.replace("docs_", "").replace(".md", "") for f in all_doc_files}
    for fpath, flang in files_to_process:
        ext = os.path.splitext(os.path.basename(fpath))[1]
        mod_name = os.path.basename(fpath).replace(ext, "")
        if mod_name not in mod_names_with_docs:
            print(f"[SYSTEM] Generating basic fallback docs for {mod_name}...")
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()

                lang_label = "COBOL" if flang == "cobol" else "Python"
                doc_content = f"# Module: `{mod_name}`\n\n"
                doc_content += f"> {lang_label} source file: `{os.path.basename(fpath)}`\n\n"
                doc_content += f"## Source Code\n\n```{flang}\n{source}\n```\n\n"
                doc_content += f"*Documentation auto-generated by Phoenix (fallback — LLM pass skipped).*\n"

                os.makedirs(GENERATED_TESTS_BASE, exist_ok=True)
                doc_file = os.path.join(GENERATED_TESTS_BASE, f"docs_{mod_name}.md")
                with open(doc_file, "w", encoding="utf-8") as f:
                    f.write(doc_content)

                all_doc_files[f"docs_{mod_name}.md"] = doc_content
                print(f"[SYSTEM] ✓ Fallback docs saved for {mod_name}")
            except Exception as doc_err:
                print(f"[SYSTEM] Fallback doc generation failed for {fpath}: {doc_err}")

    # Re-collect doc files after fallback
    for df in glob.glob(os.path.join(GENERATED_TESTS_BASE, "docs_*.md")):
        fname_doc = os.path.basename(df)
        if fname_doc not in all_doc_files:
            with open(df, "r") as f:
                all_doc_files[fname_doc] = f.read()

    # ─── Upload artifacts to Azure Blob Storage ─────────────────────────
    blob = get_blob()
    blob_test_refs = {}
    blob_doc_refs = {}

    for fname, content in all_test_files.items():
        try:
            ref = blob.upload_text(CONTAINER_ARTIFACTS, f"{session_id}/tests/{fname}", content)
            blob_test_refs[fname] = ref
        except Exception as e:
            print(f"[BLOB] Warning: failed to upload test {fname}: {e}")

    for fname, content in all_doc_files.items():
        try:
            ref = blob.upload_text(CONTAINER_ARTIFACTS, f"{session_id}/docs/{fname}", content)
            blob_doc_refs[fname] = ref
        except Exception as e:
            print(f"[BLOB] Warning: failed to upload doc {fname}: {e}")

    # Upload conversation log
    try:
        blob.upload_text(
            CONTAINER_ARTIFACTS,
            f"{session_id}/conversation_log.json",
            json.dumps(all_conversation_log, indent=2),
        )
    except Exception as e:
        print(f"[BLOB] Warning: failed to upload conversation log: {e}")

    results = {
        "session_id": session_id,
        "status": "completed",
        "test_files": all_test_files,
        "doc_files": all_doc_files,
        "conversation_log": all_conversation_log,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    # Store blob references in DB (not raw content — avoids 2MB limit)
    update_db({
        "status": "completed",
        "completed_at": results["completed_at"],
        "artifacts": {
            "test_files": all_test_files,
            "doc_files": all_doc_files,
        },
        "blob_refs": {
            "test_files": blob_test_refs,
            "doc_files": blob_doc_refs,
            "conversation_log": f"{session_id}/conversation_log.json",
        },
    })

    emit("pipeline_complete", results)
    emit("agent_progress", {
        "stage": "complete",
        "message": f"Pipeline complete! Processed {total_files} files — {len(all_test_files)} test suites, {len(all_doc_files)} docs.",
        "progress": 100,
    })

    return results
