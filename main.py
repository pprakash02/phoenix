import asyncio
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
    # Return paths relative to CWD, excluding non-code files
    return sorted(
        os.path.relpath(p) for p in abs_paths
        if "__pycache__" not in p and os.path.basename(p) != "__init__.py"
    )


def build_mission_briefing(legacy_files: list[str]) -> str:
    """
    Generate a dynamic mission briefing listing all discovered legacy files.
    """
    file_list = "\n".join(f"    - {f}" for f in legacy_files)

    return f"""
    Team Phoenix,

    We need to modernize the following undocumented legacy scripts:
{file_list}

    Workflow:
    1. Observer:
       - For EACH legacy file listed above:
         a. Run `run_legacy_code_in_sandbox` with `cat /workspace/<filename>` to read its source code.
         b. Identify ALL functions defined in the file.
         c. For each function, generate 5-10 diverse test inputs including edge cases
            (negatives, zero, empty strings, large numbers, None, whitespace) based on
            your analysis of the function's logic.
         d. Execute `capture_function_runtime` for each function using your generated inputs.
       - Report ALL raw JSON runtime data.

    2. Analyst: Parse all runtime logs to create a full behavioral specification
       for every function in every file.

    3. QA Engineer: Convert the entire specification into production-ready PyTest suites
       covering all identified functions. Save one test file per legacy module
       (e.g., legacy_billing.py → test_legacy_billing.py).

    4. Critic: Verify the suites in the sandbox, ensure 100% coverage of ALL observed
       behavior, and approve or reject with specific feedback.
    """


def round_robin_router(state: GroupChatState):
    """
    Controls which agent speaks next.

    Initial pipeline (rounds 0-3):
        Observer → Analyst → QA_Engineer → Critic

    Iterative fix loop (rounds 4+):
        QA_Engineer → Critic → QA_Engineer → Critic → ...
        (so QA can fix tests based on Critic feedback)
    """
    order = ["Observer", "Analyst", "QA_Engineer", "Critic"]

    if state.current_round < len(order):
        return order[state.current_round]

    # After initial pipeline, alternate QA_Engineer ↔ Critic
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
        print(f"         → {f}")
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
        max_rounds=12,  # 4 initial + up to 4 QA↔Critic iterations
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