import os

from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv
from agents.client import client

from tools.analyst_tools import (
    parse_runtime_logs,
    summarize_execution_results,
    detect_function
)

from schemas.test_spec import AnalystOutput

load_dotenv()


# chat_client = AzureOpenAIChatClient(
#     azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
#     deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
#     api_version=os.environ.get("AZURE_OPENAI_API_VERSION")
# )

ANALYST_INSTRUCTIONS = """
You are the Analyst agent for Phoenix.

You will receive raw runtime logs from the Observer.

Your job is to convert them into a structured JSON specification.

IMPORTANT:
1. FIRST call the tool `parse_runtime_logs`.
2. THEN call `detect_function`.
3. THEN call `summarize_execution_results`.

Finally produce a JSON specification containing:

{
  "function_name": "...",
  "successful_mappings": [...],
  "crashes": [...],
  "edge_cases": [...]
}

Return ONLY valid JSON.
"""


analyst_agent = client.as_agent(
    name="Analyst",
    instructions=ANALYST_INSTRUCTIONS,
    tools=[
        parse_runtime_logs,
        detect_function,
        summarize_execution_results,
    ],
    # output_schema=AnalystOutput
)