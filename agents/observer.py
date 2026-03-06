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
   - Use it with command `cat /workspace/<filename>` to read source code.
   - All legacy files and data files are mounted at `/workspace/`.
2. `capture_function_runtime`: Use this to instrument specific functions and capture their 
   inputs, outputs, and exceptions as clean JSON data.

IMPORTANT TEST INPUT FORMAT:
- For SINGLE-argument functions: pass a flat list, e.g. ["100", "-50", "hello"]
- For MULTI-argument functions: pass a list of argument LISTS, e.g. 
  [["word", ["a","b"]], ["test", []]] → calls func("word", ["a","b"]) then func("test", [])

STRATEGY:
1. First read the source code of each file to understand all functions.
2. SKIP interactive functions that use input() — they cannot be tested automatically.
3. For each testable function, analyze its signature and logic to generate 5-10 diverse inputs.
4. Include edge cases: empty values, boundary conditions, large inputs, type mismatches.
5. Report ALL raw JSON execution data.
"""

observer_agent = client.as_agent(
    name="Observer",
    instructions=OBSERVER_INSTRUCTIONS,
    tools=[
        run_legacy_code_in_sandbox,
        capture_function_runtime,
    ],
)