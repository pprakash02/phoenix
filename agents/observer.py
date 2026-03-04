import os
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

# Import the custom Docker sandbox tool we built
from tools.docker_sandbox import run_legacy_code_in_sandbox

load_dotenv()

# Utilizing the GitHub Models endpoint you configured for prototyping
chat_client = OpenAIChatClient(
    base_url=os.environ.get("GITHUB_ENDPOINT"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model=os.environ.get("GITHUB_MODEL_ID")
)

OBSERVER_NAME = "Observer"
OBSERVER_INSTRUCTIONS = """
You are the Observer agent for the Phoenix modernization system. 
Your primary job is to analyze undocumented legacy software by executing it securely. 
Use the `run_legacy_code_in_sandbox` tool to run the target legacy files. 
Pass different `input_args` to test how the program reacts to various inputs, 
and report the runtime outputs, errors, and stack traces back to the Analyst.
Do not make assumptions about the code; only report the raw execution data.
"""

# Instantiate the agent equipped strictly with the secure sandbox tool
observer_agent = Agent(
    name=OBSERVER_NAME,
    instructions=OBSERVER_INSTRUCTIONS,
    tools=[run_legacy_code_in_sandbox],
    client=chat_client
)