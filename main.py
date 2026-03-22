import asyncio
import ast
import glob
import os

# Import Phoenix agents
from agents.observer import observer_agent
from agents.qa_engineer import qa_engineer_agent
from agents.critic import critic_agent
from agents.doc_writer import doc_writer_agent

# Agent Framework orchestration
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState

LEGACY_WORKSPACE = os.path.abspath("legacy_workspace")


def discover_legacy_files() -> list[str]:
    """
    Scan legacy_workspace/ for all .py files and return their relative paths.
    Excludes __init__.py and __pycache__ files.
    """
    pattern = os.path.join(LEGACY_WORKSPACE, "**", "*.py")
    abs_paths = glob.glob(pattern, recursive=True)
    return sorted(
        os.path.relpath(p) for p in abs_paths
        if "__pycache__" not in p and os.path.basename(p) != "__init__.py"
    )


def extract_functions(file_path: str) -> list[dict]:
    """
    Parse a Python file's AST to extract function definitions.
    Returns a list of dicts with name, args, and whether the function is testable.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    functions = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]

            # Check if function uses input() — not testable
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


def build_single_file_briefing(file_path: str, file_context: str = "") -> str:
    """Generate a mission briefing for a SINGLE file."""
    with open(file_path, "r", encoding="utf-8") as f:
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


def make_router(file_name: str):
    """Create a round-robin router closure for a single file."""
    def round_robin_router(state: GroupChatState):
        order = ["Observer", "QA_Engineer", "Critic"]

        if state.current_round < len(order):
            return order[state.current_round]

        # Check if the Critic has approved — if so, hand off to Doc_Writer
        for msg in reversed(state.conversation):
            text = getattr(msg, "text", None) or getattr(msg, "content", None) or ""
            if "PHOENIX_APPROVED" in text:
                return "Doc_Writer"

        # Otherwise keep looping QA_Engineer ↔ Critic
        iteration = (state.current_round - len(order)) % 2
        return "QA_Engineer" if iteration == 0 else "Critic"

    return round_robin_router


def should_terminate(messages: list) -> bool:
    """Stop the conversation when the Doc_Writer signals completion."""
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


async def run_phoenix() -> None:
    print("\n--- PHOENIX MULTI-AGENT SYSTEM INITIALIZED ---\n")

    # Discover legacy files
    legacy_files = discover_legacy_files()

    if not legacy_files:
        print("[ERROR] No Python files found in legacy_workspace/. "
              "Place your legacy .py files there and re-run.")
        return

    # Filter to files with testable functions
    files_to_process = []
    for f in legacy_files:
        funcs = extract_functions(f)
        testable = [fn for fn in funcs if fn["testable"]]
        skipped = [fn for fn in funcs if not fn["testable"]]
        print(f"         → {f}  ({len(testable)} testable, {len(skipped)} skipped)")
        if testable:
            files_to_process.append(f)

    print(f"\n[SYSTEM] {len(files_to_process)} files with testable functions.\n")

    if not files_to_process:
        print("[ERROR] No testable functions found in any files.")
        return

    # --- HUMAN IN THE LOOP: PROVIDE CONTEXT ---
    print("\n--- HUMAN IN THE LOOP: PROVIDE CONTEXT ---")
    file_contexts = {}
    for f in files_to_process:
        print(f"\nTarget File: {f}")
        print("Provide context or specific test case requirements (e.g., 'Focus on edge cases for negative numbers').")
        user_input = input("Your instructions (press Enter to skip): ").strip()
        if user_input:
            file_contexts[f] = user_input
    print("\n------------------------------------------")

    # Clear old observer captures from previous runs
    captures_file = os.path.join(os.path.abspath("generated_tests"), "observer_captures.json")
    if os.path.exists(captures_file):
        os.remove(captures_file)

    # --- Per-file sequential processing ---
    total_files = len(files_to_process)

    for file_idx, file_path in enumerate(files_to_process):
        file_name = os.path.basename(file_path)
        file_num = file_idx + 1

        print(f"\n{'='*60}")
        print(f"[SYSTEM] Processing file {file_num}/{total_files}: {file_name}")
        print(f"{'='*60}\n")

        mission_briefing = build_single_file_briefing(
            file_path, file_contexts.get(file_path, "")
        )

        workflow = GroupChatBuilder(
            participants=[
                observer_agent,
                qa_engineer_agent,
                critic_agent,
                doc_writer_agent,
            ],
            selection_func=make_router(file_name),
            termination_condition=should_terminate,
            max_rounds=10,
        ).build()

        print(f"[SYSTEM] Dispatching mission for {file_name}...\n")

        try:
            result = await workflow.run(mission_briefing)

            print(f"\n--- CONVERSATION FOR {file_name} ---\n")
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
                        print(f"[{author}]")
                        print(content)
                        print("\n" + "-" * 60 + "\n")
        except Exception as e:
            print(f"[ERROR] Pipeline failed for {file_name}: {e}")

        print(f"[SYSTEM] ✓ Completed {file_name} ({file_num}/{total_files})")

    print(f"\n{'='*60}")
    print(f"[SYSTEM] All {total_files} files processed successfully!")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(run_phoenix())