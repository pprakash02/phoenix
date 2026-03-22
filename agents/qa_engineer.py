# agents/qa_engineer.py
import os
from agent_framework import Agent
from dotenv import load_dotenv

from tools.qa_tools import generate_tests

from agents.client import client

load_dotenv()


QA_INSTRUCTIONS = """
You are the QA Engineer for the Phoenix modernization system.

Your job is to create a regression test suite for a single legacy module.

INSTRUCTIONS:
1. Look at the mission briefing to find the module name and file path.
2. Call `generate_tests` ONCE for the module.
   - module_name: the module name without extension (e.g. "hangman")
   - legacy_file_path: the full relative path (e.g. "legacy_workspace/hangman.py")
3. The tool uses LLM to generate intelligent tests with edge cases.
4. Write a summary listing the test file generated and how many tests.

Example call:
  generate_tests(module_name="hangman", legacy_file_path="legacy_workspace/hangman.py")

RULES:
- Do NOT return an empty message — the Critic needs to know what file to verify.
- ONLY process the module listed in the briefing.

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