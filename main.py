import asyncio
import os
import glob

# Import Phoenix agents
from agents.observer import observer_agent
from agents.analyst import analyst_agent
from agents.qa_engineer import qa_engineer_agent
from agents.critic import critic_agent

# Agent Framework orchestration
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState


def phoenix_router(state: GroupChatState):
    conversation = state.conversation
    if not conversation:
        return "Observer"

    # Find the last actual agent who completed a turn
    last_author = ""
    for msg in reversed(conversation):
        author = getattr(msg, "author_name", "") or getattr(msg, "name", "")
        if author in ["Observer", "Analyst", "QA_Engineer", "Critic"]:
            last_author = author
            break

    # Strictly enforce the pipeline sequence based on the last speaker
    if last_author == "Observer":
        return "Analyst"
    elif last_author == "Analyst":
        return "QA_Engineer"
    elif last_author == "QA_Engineer":
        return "Critic"
    elif last_author == "Critic":
        # Check the actual last message content for approval
        last_msg = conversation[-1]
        last_content = getattr(last_msg, "text", "") or ""
        if '"is_approved": true' in last_content:
            return None  # End the workflow
        return "QA_Engineer"  # Reject, send back to QA
    
    return "Observer"  # Default start

def is_mission_accomplished(conversation) -> bool:
    """Termination condition: Stop when Critic approves."""
    if not conversation:
        return False
    last_msg = conversation[-1]
    last_content = last_msg.text or ""
    last_author = getattr(last_msg, "author_name", "") or ""
    
    # Fallback to msg.contents for agent_framework sometimes
    if not last_content and hasattr(last_msg, "contents") and last_msg.contents:
        parts = [str(getattr(c, "text", None) or getattr(c, "value", None) or c) for c in last_msg.contents]
        last_content = "\n".join(parts)
        
    return last_author == "Critic" and '"is_approved": true' in last_content


async def run_phoenix() -> None:
    print("\n--- PHOENIX MULTI-AGENT SYSTEM INITIALIZED ---\n")

    # DYNAMICALLY FIND FILES
    target_dir = "legacy_workspace"
    if not os.path.exists(target_dir):
        print(f"[ERROR] Directory '{target_dir}' not found.")
        return

    legacy_files = [f for f in glob.glob(f"{target_dir}/*.py") if not f.endswith("__init__.py")]
    
    if not legacy_files:
        print(f"[SYSTEM] No Python files found in {target_dir}/")
        return

    for file_path in legacy_files:
        module_name = os.path.basename(file_path).replace(".py", "")
        print(f"\n{'='*60}")
        print(f"🚀 STARTING MODERNIZATION FOR: {file_path}")
        print(f"{'='*60}\n")

        # Build a FRESH group chat workflow for each file
        workflow = GroupChatBuilder(
            participants=[
                observer_agent,
                analyst_agent,
                qa_engineer_agent,
                critic_agent,
            ],
            selection_func=phoenix_router,
            max_rounds=20,
            termination_condition=is_mission_accomplished,
        ).build()

        # Inject the dynamic file name into the briefing
        mission_briefing = f"""
        Team Phoenix,

        We need to modernize the undocumented legacy script: 
        {file_path}

        Workflow:
        1. Observer: 
           - Run `run_legacy_code_in_sandbox` with `cat /workspace/{module_name}.py` to read the source code.
           - Identify a MAXIMUM of 3 primary functions to keep the scope manageable.
           - For the targeted functions, execute `capture_function_runtime`. The module name is EXACTLY `{module_name}`. Do NOT try to run directories or text files.
           - When finished, you MUST output the final JSON payload containing your results.
        2. Analyst: Parse all runtime logs to create a full behavioral specification.
        3. QA Engineer: Convert the specification into a PyTest suite (`test_{module_name}.py`).
        4. Critic: Verify the suite in the sandbox and approve.
        """

        print(f"[SYSTEM] Dispatching mission for {module_name} to Phoenix agents...\n")
        result = await workflow.run(mission_briefing)

        print(f"\n--- AGENT CONVERSATION FOR {module_name} ---\n")
        for messages in result.get_outputs():
            for msg in messages:
                author = getattr(msg, "author_name", None) or getattr(msg, "name", "Agent")
                content = getattr(msg, "text", None) or getattr(msg, "content", None)

                if not content and hasattr(msg, "contents") and msg.contents:
                    parts = [str(getattr(c, "text", None) or getattr(c, "value", None) or c) for c in msg.contents if getattr(c, "text", None) or getattr(c, "value", None) or str(c)]
                    content = "\n".join(parts) if parts else None

                if content:
                    print(f"[{author}]")
                    print(content)
                    print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_phoenix())