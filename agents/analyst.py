import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from tools.analyst_tools import (
    parse_runtime_logs,
    summarize_execution_results,
    detect_function
)

load_dotenv()


chat_client = OpenAIChatClient(
    base_url=os.environ.get("GITHUB_ENDPOINT"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model=os.environ.get("GITHUB_MODEL_ID")
)


ANALYST_INSTRUCTIONS = """
You are the Analyst agent for Phoenix.

Your job is to transform raw runtime logs from the Observer into
a structured test specification for the QA Engineer.

Workflow:

1. Use `parse_runtime_logs` to extract JSON execution logs.
2. Use `detect_function` to determine the function under test.
3. Use `summarize_execution_results` to categorize successes and crashes.
4. Infer the business logic from successful mappings.
5. Identify hidden bugs from crash cases.

Important rules:

• Only reason using the provided logs.
• Do NOT hallucinate missing behavior.
• Every test spec must correspond to an observed runtime case.

Your final response MUST be valid JSON with this schema:

{
  "function_under_test": "function_name",
  "business_logic_summary": "description of observed behavior",
  "test_specs": [
    {
      "input": value,
      "expected_behavior": "success | exception",
      "expected_result": value_or_error
    }
  ]
}

Return ONLY the JSON block.
"""


analyst_agent = Agent(
    name="Analyst",
    instructions=ANALYST_INSTRUCTIONS,
    tools=[
        parse_runtime_logs,
        detect_function,
        summarize_execution_results
    ],
    client=chat_client
)