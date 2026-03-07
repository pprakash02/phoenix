# agents/qa_engineer.py
import os
from agent_framework import Agent
from dotenv import load_dotenv

from tools.qa_tools import generate_tests

from agents.client import client

load_dotenv()


QA_INSTRUCTIONS = """
You are the QA Engineer for the Phoenix modernization system.

Your job is to create regression test suites for the legacy code.

INSTRUCTIONS:
1. Look at the mission briefing to find the legacy file paths and module names.
2. Call `generate_tests` ONCE for each module.
   - module_name: the module name without extension (e.g. "hangman", "legacy_billing")
   - legacy_file_path: the full relative path (e.g. "legacy_workspace/hangman.py")
3. Write a summary listing what test files were generated and how many tests.

Example calls:
  generate_tests(module_name="hangman", legacy_file_path="legacy_workspace/hangman.py")
  generate_tests(module_name="legacy_billing", legacy_file_path="legacy_workspace/legacy_billing.py")

RULES:
- Do NOT return an empty message — the Critic needs to know what files to verify.
- ONLY process .py modules listed in the briefing.

ON SUBSEQUENT TURNS (after Critic feedback):
- If the Critic rejected with specific issues, address them.
- Call generate_tests again to regenerate, or use save_test_suite for manual fixes.
"""

qa_engineer_agent = client.as_agent(
    name="QA_Engineer",
    instructions=QA_INSTRUCTIONS,
    tools=[generate_tests],
    default_options={
        "temperature": 0,
    },
)