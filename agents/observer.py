# agents/observer.py
import os
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv

from tools.docker_sandbox import run_legacy_code_in_sandbox
from tools.runtime_capture import capture_function_runtime

load_dotenv()

chat_client = AzureOpenAIChatClient(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION")
)


OBSERVER_NAME = "Observer"
OBSERVER_INSTRUCTIONS = """
You are the Observer agent for the Phoenix modernization system. 
Your job is to analyze undocumented legacy software. 

You have two tools:
1. `run_legacy_code_in_sandbox`: Use this to run the entire script and see high-level terminal outputs.
2. `capture_function_runtime`: Use this to surgically attach decorators to specific functions (e.g., 'process_transaction') to capture clean JSON data of inputs, outputs, and edge-case crashes.

Pass diverse `test_inputs` (like positive numbers, negative numbers, strings, and zero) to uncover hidden bugs. Report the raw JSON execution data back to the Analyst.
"""

observer_agent = Agent(
    name=OBSERVER_NAME,
    instructions=OBSERVER_INSTRUCTIONS,
    tools=[run_legacy_code_in_sandbox, capture_function_runtime],
    client=chat_client
)