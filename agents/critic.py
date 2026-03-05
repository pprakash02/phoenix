# agents/critic.py
import os
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from tools.critic_tools import verify_test_results, read_test_file
from schemas.validation_report import CriticReport

load_dotenv()

chat_client = OpenAIChatClient(
    base_url=os.environ.get("GITHUB_ENDPOINT"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model=os.environ.get("GITHUB_MODEL_ID")
)

CRITIC_INSTRUCTIONS = """
You are the Critic (Validation Agent) for Phoenix. 

Your goal is to cross-verify the generated test suite against the Analyst's observations.

Steps:
1. Use `read_test_file` to obtain the test code written by the QA Engineer.
2. Compare the Analyst's JSON (the 'Ground Truth', available in the chat history) with the test code.
3. Check for Hallucinations: Did the QA Engineer invent behavior not seen in the logs?
4. Check for Coverage: Are all 'successful_mappings' and 'crashes' tested?
5. Execute the tests using `verify_test_results` and inspect the output to confirm they pass.

You must return your findings in the structured CriticReport format. 
Only set 'is_approved' to True if all tests pass in the sandbox and coverage is 100%.
"""

critic_agent = Agent(
    name="Critic",
    instructions=CRITIC_INSTRUCTIONS,
    tools=[verify_test_results, read_test_file],
    client=chat_client,
    output_schema=CriticReport
)