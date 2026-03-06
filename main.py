import asyncio

# Import Phoenix agents
from agents.observer import observer_agent
from agents.analyst import analyst_agent
from agents.qa_engineer import qa_engineer_agent
from agents.critic import critic_agent

# Agent Framework orchestration
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState


def phoenix_router(state: GroupChatState):
    """
    Controls which agent speaks next with Critic↔QA feedback loops.

    Initial pass (rounds 0-3):
        Observer → Analyst → QA_Engineer → Critic

    Feedback loop (rounds 4+):
        If the Critic rejected → QA_Engineer → Critic → repeat
        If the Critic approved → END
    """
    order = ["Observer", "Analyst", "QA_Engineer", "Critic"]

    # Initial sequential pass
    if state.current_round < len(order):
        return order[state.current_round]

    # --- Feedback loop phase ---
    # Look at the last message to decide what happens next
    conversation = state.conversation
    if conversation:
        last_content = ""
        last_author = ""
        for msg in reversed(conversation):
            text = msg.text or ""
            author = msg.author_name or ""
            if text.strip():
                last_content = text
                last_author = author
                break

        # If the Critic just spoke and rejected, send to QA_Engineer to fix
        if last_author == "Critic":
            return "QA_Engineer"

        # If QA_Engineer just spoke (after a fix), send back to Critic
        if last_author == "QA_Engineer":
            return "Critic"

    # Safety fallback
    return "Observer"

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

    # Build the group chat workflow
    workflow = GroupChatBuilder(
        participants=[
            observer_agent,
            analyst_agent,
            qa_engineer_agent,
            critic_agent,
        ],
        selection_func=phoenix_router,
        max_rounds=20,  # headroom for 4 agents + up to 3 Critic↔QA retry cycles
        termination_condition=is_mission_accomplished,
    ).build()

    mission_briefing = """
    Team Phoenix,

    We need to modernize the undocumented legacy script: 
    legacy_workspace/legacy_billing.py

    Workflow:
    1. Observer: 
       - First, run `run_legacy_code_in_sandbox` with the command `cat /workspace/legacy_billing.py` to read the entire source code.
       - Identify all primary functions (like `process_transaction`).
       - For each function, generate 5-10 diverse test inputs including edge cases (negatives, zero, empty strings, large numbers) based on your analysis of the logic.
       - Execute `capture_function_runtime` for each function using your self-generated inputs.
    2. Analyst: Parse all runtime logs to create a full behavioral specification of the program.
    3. QA Engineer: Convert the entire specification into a production-ready PyTest suite covering all identified functions and save it.
    4. Critic: Verify the suite in the sandbox, ensure 100% coverage of the logic you observed, and approve.
    """

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