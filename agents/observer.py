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
1. `run_legacy_code_in_sandbox`: Use this to run the entire script and see high-level terminal outputs.
2. `capture_function_runtime`: Use this to surgically attach decorators to specific functions (e.g., 'process_transaction') to capture clean JSON data of inputs, outputs, and edge-case crashes.

Pass diverse `test_inputs` (like positive numbers, negative numbers, strings, and zero) to uncover hidden bugs. 

CRITICAL REQUIREMENT:
When you are done executing your tools, you MUST write a final chat message containing the raw JSON execution data. Do NOT just stop after the tool runs. The Analyst cannot see your internal tool logs—you must explicitly print the final JSON data in your text response so the pipeline can continue!
"""

observer_agent = client.as_agent(
    name="Observer",
    instructions=OBSERVER_INSTRUCTIONS,
    tools=[
        run_legacy_code_in_sandbox,
        capture_function_runtime,
    ],
)