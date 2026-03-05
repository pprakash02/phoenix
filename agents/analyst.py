import os

from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv
from client import client

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

Your job is to convert raw runtime logs from the Observer into a
structured specification for QA testing.

Steps:

1. Use parse_runtime_logs to extract execution logs.
2. Use detect_function to identify the function under test.
3. Use summarize_execution_results to separate successes and crashes.
4. Infer business logic from the successful mappings.
5. Identify edge cases and exceptions.

Rules:

• Only reason from the logs.
• Do NOT invent behavior not seen in logs.
• Every test_spec must correspond to an observed runtime case.

Return ONLY the structured JSON output matching the provided schema.
"""


analyst_agent = client.as_agent(
    name="Analyst",
    instructions=ANALYST_INSTRUCTIONS,
    tools=[
        parse_runtime_logs,
        detect_function,
        summarize_execution_results,
    ],
    output_schema=AnalystOutput
)