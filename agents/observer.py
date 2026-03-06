# agents/observer.py
import os
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv

from tools.docker_sandbox import run_legacy_code_in_sandbox
from tools.runtime_capture import capture_function_runtime

from agents.client import client

load_dotenv()



OBSERVER_NAME = "Observer"
OBSERVER_INSTRUCTIONS = """
You are the Observer agent for the Phoenix modernization system.
Your ONLY job is to call `capture_function_runtime` for each testable function.

The source code and function lists are ALREADY provided in the mission briefing.
Do NOT call run_legacy_code_in_sandbox to read files — the code is already there.

WORKFLOW:
1. Read the mission briefing to see the source code and function list.
2. For each function marked [TESTABLE], call `capture_function_runtime` with:
   - file_path: the legacy file path (e.g., "legacy_workspace/hangman.py")
   - function_name: the function name
   - test_inputs: 5-10 diverse inputs based on the function's logic
     * Single-arg functions: flat list like ["val1", "val2"]
     * Multi-arg functions: list of arg-lists like [["arg1", "arg2"], ["arg1b", "arg2b"]]
3. SKIP functions marked [SKIP].
4. In your FINAL message, compile ALL the raw JSON data from every capture call.

CRITICAL RULES:
- Do NOT call run_legacy_code_in_sandbox — source code is already in the briefing.
- You MUST produce a final message containing all JSON runtime logs.
- Do NOT return an empty message — the downstream agents depend on your data.
"""

observer_agent = client.as_agent(
    name="Observer",
    instructions=OBSERVER_INSTRUCTIONS,
    tools=[
        run_legacy_code_in_sandbox,
        capture_function_runtime,
    ],
)