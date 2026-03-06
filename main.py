# import asyncio

# # Import Phoenix agents
# from agents.observer import observer_agent
# from agents.analyst import analyst_agent
# from agents.qa_engineer import qa_engineer_agent
# from agents.critic import critic_agent

# # Agent Framework orchestration
# from agent_framework.orchestrations import GroupChatBuilder, GroupChatState

# def round_robin_router(state: GroupChatState):
#     order = ["Observer", "Analyst", "QA_Engineer", "Critic"]

#     if state.current_round < len(order):
#         return order[state.current_round]

#     return GroupChatBuilder.END

# async def run_phoenix() -> None:
#     print("\n--- PHOENIX MULTI-AGENT SYSTEM INITIALIZED ---\n")

#     # Use the GroupChatBuilder class to create a workflow.
#     # Pass participants directly into the constructor to satisfy validation.
#     workflow = GroupChatBuilder(
#         participants=[
#             observer_agent,
#             analyst_agent,
#             qa_engineer_agent,
#             critic_agent,
#         ],
#         selection_func=round_robin_router
#     ).build()

#     mission_briefing = """
# Team Phoenix,

# We need to modernize the undocumented legacy script:
# legacy_workspace/legacy_billing.py

# Workflow:
# 1. Observer: Capture runtime behavior of `process_transaction` with inputs ['100', '-50', '0', '500'].
# 2. Analyst: Parse runtime logs and generate structured JSON specification.
# 3. QA Engineer: Convert JSON specification into a PyTest suite and save it.
# 4. Critic: Validate coverage, run the tests, and approve or reject the generated suite.
# """

#     print("[SYSTEM] Dispatching mission to Phoenix agents...\n")

#     # Call the workflow's run method with the task or input you want the agents to work on[cite: 3937].
#     conversation = await workflow.run(
#         mission_briefing,
#         options={"parallel_tool_calls": False}
#     )
#     print("\n--- AGENT CONVERSATION ---\n")

#     for message in conversation:
#         author = getattr(
#             message,
#             "speaker",
#             getattr(message, "name", getattr(message, "author_name", "Agent")),
#         )
#         text = getattr(message, "text", getattr(message, "content", ""))

#         if text:
#             print(f"[{author}]")
#             print(text)
#             print("\n" + "-" * 60 + "\n")

# if __name__ == "__main__":
#     asyncio.run(run_phoenix())
import asyncio

# Import Phoenix agents
from agents.observer import observer_agent
from agents.analyst import analyst_agent
from agents.qa_engineer import qa_engineer_agent
from agents.critic import critic_agent

# Agent Framework orchestration
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState


def round_robin_router(state: GroupChatState):
    """
    Controls which agent speaks next.

    Order:
    0 → Observer
    1 → Analyst
    2 → QA Engineer
    3 → Critic
    """

    order = ["Observer", "Analyst", "QA_Engineer", "Critic"]

    if state.current_round < len(order):
        return order[state.current_round]

    # Fallback — max_rounds should prevent reaching here
    return order[-1]


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
        selection_func=round_robin_router,
        max_rounds=10,  # enough headroom for 4 agents plus any retries
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

            if content:
                print(f"[{author}]")
                print(content)
                print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_phoenix())