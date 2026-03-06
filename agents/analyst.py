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

You receive RAW runtime logs produced by the Observer agent.

Your task is to convert those logs into a structured behavioral specification
that describes how the legacy function behaves.

You MUST follow this exact pipeline:

STEP 1
Call the tool `parse_runtime_logs` with the raw runtime output.

STEP 2
Call `detect_function` to determine which function is being analyzed.

STEP 3
Call `summarize_execution_results` to classify the runtime results into:
- successful mappings
- crashes
- edge cases

STEP 4
Return the final structured JSON specification.

The JSON MUST contain the following fields:

{
  "function_name": "...",
  "successful_mappings": [...],
  "crashes": [...],
  "edge_cases": [...]
}

Rules:
- Always use the provided tools.
- Do NOT invent outputs.
- The final response MUST be valid JSON.
- Do NOT include explanations.
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
        "response_format": AnalystOutput,
        "temperature": 0,
    },
)