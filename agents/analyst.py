import os
from dotenv import load_dotenv

from agents.client import client
from agent_framework import Agent

from tools.analyst_tools import (
    parse_runtime_logs,
    detect_function,
    summarize_execution_results
)

from schemas.test_spec import AnalystOutput

load_dotenv()


ANALYST_INSTRUCTIONS = """
You are the Analyst agent in the Phoenix autonomous code modernization system.

You receive the Observer agent's report from the chat history, which contains
runtime execution data captured from the legacy function.

Your task is to convert those logs into a structured behavioral specification
that describes how the legacy function behaves.

You MUST follow this exact pipeline:

STEP 1
Find the Observer's message in the chat history. Copy the ENTIRE text of
the Observer's message (including any JSON code blocks) and pass it to
the `parse_runtime_logs` tool. The tool handles markdown and code fences
automatically.

STEP 2
Call `detect_function` with the parsed logs to determine which function is
being analyzed.

STEP 3
Call `summarize_execution_results` to classify the runtime results into:
- successful mappings
- crashes
- edge cases

STEP 4 — CRITICAL
After you receive the results from all tool calls above, you MUST write out 
the COMPLETE behavioral specification as your final message. 

The specification MUST be a JSON object with these exact fields:

{
  "function_name": "<the actual legacy function name>",
  "business_logic_summary": "<short description of what the function does>",
  "successful_mappings": [{"input": "...", "output": ...}, ...],
  "crashes": [{"input": "...", "error": "..."}, ...],
  "edge_cases": [...]
}

IMPORTANT:
- You MUST write the full JSON as your response text. Do NOT return an empty message.
- Use the EXACT data returned by your tools. Do NOT invent data.
- The function_name must be the LEGACY function name as found in the source code,
  NOT the name of an Analyst tool.
- Include ALL entries from the tool results in your final JSON.
"""


analyst_agent: Agent = client.as_agent(
    name="Analyst",
    instructions=ANALYST_INSTRUCTIONS,
    tools=[
        parse_runtime_logs,
        detect_function,
        summarize_execution_results,
    ],
    default_options={
        "temperature": 0,
    },
)