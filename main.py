# main.py
import asyncio

# Import the specialized agents
from agents.observer import observer_agent
from agents.analyst import analyst_agent
from agents.qa_engineer import qa_engineer_agent
from agents.critic import critic_agent

# Import the framework's updated orchestration builder and state typing
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState

def round_robin_manager(state: GroupChatState) -> str | None:
    """
    A deterministic routing function that controls speaker selection.
    Uses the built-in current_round to route linearly and terminate.
    """
    if state.current_round == 0:
        return "Observer"     # 1. Start with the Observer
    elif state.current_round == 1:
        return "Analyst"      # 2. Hand off to the Analyst
    elif state.current_round == 2:
        return "QA_Engineer"  # 3. Pass requirements to QA
    elif state.current_round == 3:
        return "Critic"       # 4. QA passes code to Critic
    else:
        return None           # 5. Terminate the chat (Returning None stops the workflow)

async def run_phoenix():
    print("--- PHOENIX MULTI-AGENT ORCHESTRATION INITIALIZED ---\n")

    # Build the group chat workflow using the updated constructor parameters
    workflow = GroupChatBuilder(
        participants=[observer_agent, analyst_agent, qa_engineer_agent, critic_agent],
        selection_func=round_robin_manager # Pass the function here directly
    ).build()

    # Define the kickoff task for the team
    mission_briefing = """
    Team, we need to modernize the undocumented script at 'legacy_workspace/legacy_billing.py'.

    1. Observer: Use your `capture_function_runtime` tool on the 'process_transaction' function. 
       Pass the following test_inputs: ['100', '-50', '0', '500'].
    2. Analyst: Parse the runtime logs and output the strict JSON test specification.
    3. QA Engineer: Use the Analyst's JSON to write a robust PyTest suite and save it using your tool.
    4. Critic: Review the saved PyTest code. Approve it if the coverage is complete, or reject it with feedback.
    """


    print("[SYSTEM] Task dispatched to the team. Stand by for agent collaboration (this may take a minute)...\n")

    # Await the workflow to finish and capture the entire conversation history
    final_conversation = await workflow.run(mission_briefing)

    # Iterate through the returned list of messages and print them
    for message in final_conversation:
        # Check if the message has text content
        text_content = getattr(message, "text", getattr(message, "content", None))

        if text_content:
            author = getattr(message, "speaker", getattr(message, "name", getattr(message, "author_name", "Agent")))
            print(f"[{author}]:\n{text_content}\n")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_phoenix())