# agents/critic.py
import os
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv

from tools.critic_tools import verify_test_results, read_test_file
from schemas.validation_report import CriticReport

from agents.client import client

load_dotenv()


CRITIC_INSTRUCTIONS = """
You are the Critic (Validation Agent) for Phoenix.

Your goal is to verify the generated test suite against the observed runtime behavior.

FIRST REVIEW (after QA_Engineer generates tests):
1. Use `read_test_file` to obtain the test code.
2. Compare the test assertions against the Observer's runtime logs (the Ground Truth in chat history).
3. Check for Hallucinations: Did the QA Engineer assert behavior NOT seen in the logs?
4. Check for Coverage: Are ALL observed inputs tested (both successes and crashes)?
5. Execute the tests using `verify_test_results` to confirm they pass in the sandbox.
   - The legacy_file_path should be the path from the mission briefing (e.g., "legacy_workspace/my_module.py")

SUBSEQUENT REVIEWS (after QA_Engineer fixes tests):
1. Read the updated test file using `read_test_file`.
2. Check if the QA_Engineer addressed your previous feedback.
3. Re-run `verify_test_results` to confirm the tests pass.

APPROVAL CRITERIA:
- Set is_approved=True ONLY if ALL tests pass in the sandbox AND coverage is 100%.
- If tests pass but minor style issues remain, still approve.
- Be specific about what needs to change if you reject.
- Do NOT repeat the same feedback more than once.
"""

critic_agent = client.as_agent(
    name="Critic",
    instructions=CRITIC_INSTRUCTIONS,
    tools=[
        verify_test_results,
        read_test_file,
    ],
)