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

    # Prevent out-of-range errors
    if state.current_round >= len(order):
        return order[-1]

    return order[state.current_round]


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
        max_rounds=4,  # critical fix to stop workflow
    ).build()

    mission_briefing = """
Team Phoenix,

We need to modernize the undocumented legacy script:
legacy_workspace/legacy_billing.py

Workflow:
1. Observer: Capture runtime behavior of `process_transaction` with inputs ['100', '-50', '0', '500'].
2. Analyst: Parse runtime logs and generate structured JSON specification.
3. QA Engineer: Convert JSON specification into a PyTest suite and save it.
4. Critic: Validate coverage, run the tests, and approve or reject the generated suite.
"""

    print("[SYSTEM] Dispatching mission to Phoenix agents...\n")

    conversation = await workflow.run(
        mission_briefing,
        options={"parallel_tool_calls": False}
    )

    print("\n--- AGENT CONVERSATION ---\n")

    for event in conversation:

        # Only process output events
        if getattr(event, "type", None) != "output":
            continue

        messages = event.data

        for msg in messages:
            author = getattr(
                msg,
                "speaker",
                getattr(msg, "name", getattr(msg, "author_name", "Agent")),
            )

            content = getattr(msg, "content", None) or getattr(msg, "text", None)

            if content:
                print(f"[{author}]")
                print(content)
                print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_phoenix())