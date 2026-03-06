import asyncio
import ast
import glob
import os

# Import Phoenix agents
from agents.observer import observer_agent
from agents.analyst import analyst_agent
from agents.qa_engineer import qa_engineer_agent
from agents.critic import critic_agent

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


def build_mission_briefing(legacy_files: list[str]) -> str:
    """
    Generate a dynamic mission briefing with pre-read source code and function lists.
    """
    file_sections = []

    for fpath in legacy_files:
        # Read source code
        with open(fpath, "r", encoding="utf-8") as f:
            source = f.read()

        # Extract functions
        funcs = extract_functions(fpath)
        fname = os.path.basename(fpath)

        testable = [fn for fn in funcs if fn["testable"]]
        skipped = [fn for fn in funcs if not fn["testable"]]

        func_list = ""
        for fn in testable:
            args_str = ", ".join(fn["args"])
            func_list += f"       - {fn['name']}({args_str})  [TESTABLE]\n"
        for fn in skipped:
            args_str = ", ".join(fn["args"])
            func_list += f"       - {fn['name']}({args_str})  [SKIP: {fn['reason']}]\n"

        section = f"""
    === {fpath} ===
    Functions found:
{func_list}
    Source code:
    ```python
{source}
    ```
"""
        file_sections.append(section)

    all_sections = "\n".join(file_sections)

    return f"""
    Team Phoenix,

    We need to modernize the following undocumented legacy scripts.
    The source code and function lists are provided below — do NOT waste tool calls reading files.
{all_sections}

    Workflow:
    1. Observer:
       - The source code is ALREADY provided above. Do NOT call cat or read any files.
       - For each function marked [TESTABLE], call `capture_function_runtime` with 5-10
         diverse test inputs based on the source code logic.
       - For MULTI-argument functions: pass test_inputs as a list of argument LISTS, e.g.
         [["arg1", "arg2"], ["arg1b", "arg2b"]]
       - For SINGLE-argument functions: pass a flat list, e.g. ["val1", "val2"]
       - Your final message MUST include all raw JSON runtime data.

    2. Analyst: Parse the Observer's runtime logs into a behavioral specification.

    3. QA Engineer: Convert the specification into PyTest suites. Save one test file per module.

    4. Critic: Verify the suites in the sandbox, ensure 100% coverage, and approve/reject.
    """


def round_robin_router(state: GroupChatState):
    """
    Controls which agent speaks next.

    Initial pipeline (rounds 0-3):
        Observer → Analyst → QA_Engineer → Critic

    Iterative fix loop (rounds 4+):
        QA_Engineer → Critic → QA_Engineer → Critic → ...
    """
    order = ["Observer", "Analyst", "QA_Engineer", "Critic"]

    if state.current_round < len(order):
        return order[state.current_round]

    iteration = (state.current_round - len(order)) % 2
    return "QA_Engineer" if iteration == 0 else "Critic"


async def run_phoenix() -> None:
    print("\n--- PHOENIX MULTI-AGENT SYSTEM INITIALIZED ---\n")

    # Discover legacy files
    legacy_files = discover_legacy_files()

    if not legacy_files:
        print("[ERROR] No Python files found in legacy_workspace/. "
              "Place your legacy .py files there and re-run.")
        return

    print(f"[SYSTEM] Discovered {len(legacy_files)} legacy file(s):")
    for f in legacy_files:
        funcs = extract_functions(f)
        testable = [fn for fn in funcs if fn["testable"]]
        skipped = [fn for fn in funcs if not fn["testable"]]
        print(f"         → {f}  ({len(testable)} testable, {len(skipped)} skipped)")
    print()

    # Build the group chat workflow
    workflow = GroupChatBuilder(
        participants=[
            observer_agent,
            analyst_agent,
            qa_engineer_agent,
            critic_agent,
        ],
        selection_func=round_robin_router,
        max_rounds=12,
    ).build()

    mission_briefing = build_mission_briefing(legacy_files)

    print("[SYSTEM] Dispatching mission to Phoenix agents...\n")

    result = await workflow.run(mission_briefing)

    print("\n--- AGENT CONVERSATION ---\n")

    for messages in result.get_outputs():
        for msg in messages:
            author = getattr(msg, "author_name", None) or getattr(msg, "name", "Agent")
            content = getattr(msg, "text", None) or getattr(msg, "content", None)

            # Fallback: extract text from contents list (e.g., tool results)
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

if __name__ == "__main__":
    asyncio.run(run_phoenix())