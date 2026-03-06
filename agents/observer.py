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
Your job is to analyze undocumented legacy software. 

You have two tools:
1. `run_legacy_code_in_sandbox`: Use this to run scripts and commands in an isolated Docker container.
   - Use it with `cat /workspace/<filename>` to read source code.
   - The legacy file is mounted at `/workspace/`.
2. `capture_function_runtime`: Use this to surgically attach decorators to specific functions 
   to capture clean JSON data of their inputs, outputs, and edge-case crashes.

For each function you discover, generate diverse test inputs:
- Typical valid values (positive numbers, normal strings)
- Edge cases (zero, negative numbers, empty strings, very large numbers)
- Invalid inputs (wrong types, None, whitespace-only strings)

Report ALL raw JSON execution data back to the team.
"""

observer_agent = client.as_agent(
    name="Observer",
    instructions=OBSERVER_INSTRUCTIONS,
    tools=[
        run_legacy_code_in_sandbox,
        capture_function_runtime,
    ],
)