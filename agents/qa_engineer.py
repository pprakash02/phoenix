# agents/qa_engineer.py
import os
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from tools.qa_tools import save_test_suite

load_dotenv()

chat_client = OpenAIChatClient(
    base_url=os.environ.get("GITHUB_ENDPOINT"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model=os.environ.get("GITHUB_MODEL_ID")
)

QA_INSTRUCTIONS = """
You are the QA Engineer for the Phoenix modernization system.

Your job is to read the structured AnalystOutput JSON provided by the Analyst in the chat history, 
and convert those specifications into a robust, production-ready PyTest regression suite.

Steps:
1. Wait for the Analyst to post the structured JSON specifications.
2. Read the "successful_mappings" to write standard assertion tests.
3. Read the "crashes" and "edge_cases" to write `pytest.raises` blocks for expected exceptions.
4. Generate the complete Python script (importing pytest and the target function).
5. IMMEDIATELY use the `save_test_suite` tool to save your code to disk.

Rules:
• Do not invent test cases; strictly follow the Analyst's structured data.
• Ensure the code is syntactically correct and fully imports `pytest`.
• After you receive the SUCCESS message from the `save_test_suite` tool, report back to the team that the file is ready.
"""

qa_engineer_agent = Agent(
    name="QA_Engineer",
    instructions=QA_INSTRUCTIONS,
    tools=[save_test_suite],
    client=chat_client
)