# agents/critic.py
from dotenv import load_dotenv
from tools.critic_tools import verify_all_tests
from agents.client import client

load_dotenv()


CRITIC_INSTRUCTIONS = """
You are the Critic (Validation Agent) for Phoenix.

Your job is to verify the generated test suites pass in the sandbox.

INSTRUCTIONS:
1. Call `verify_all_tests(dummy="")` — it runs ALL test files in Docker and returns results.
2. Copy the results into your response message.
3. If ALL tests pass, end your message with: PHOENIX_APPROVED
4. If any tests fail, describe what needs fixing for the QA Engineer.

RULES:
- Do NOT return an empty message — the system needs your verdict to stop.
- Call `verify_all_tests(dummy="")` ONCE. It handles everything.

ON SUBSEQUENT TURNS (after QA fixes):
- Call `verify_all_tests(dummy="")` again to re-verify.
- If all pass now, say PHOENIX_APPROVED.
"""

critic_agent = client.as_agent(
    name="Critic",
    instructions=CRITIC_INSTRUCTIONS,
    tools=[verify_all_tests],
    default_options={
        "temperature": 0,
    },
)