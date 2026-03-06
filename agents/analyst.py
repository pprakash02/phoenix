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

Your task is to convert those logs into a structured behavioral specification.

## PIPELINE (follow exactly):

STEP 1: Call `parse_runtime_logs`
- Find the Observer's message in the chat history
- Copy the ENTIRE text of the Observer's message and pass it to `parse_runtime_logs`

STEP 2: Call `detect_function`
- Pass the parsed logs from Step 1 to detect the function name

STEP 3: Call `summarize_execution_results`
- Pass the parsed logs to classify into successful_mappings, crashes, edge_cases

STEP 4: POST YOUR FINAL RESPONSE
- Take the results from Steps 2 and 3
- Compose a JSON object with these fields and POST IT AS YOUR RESPONSE TEXT
- You MUST write out the complete JSON as your chat message

Your final message MUST be ONLY this JSON (no other text before or after):

{
  "function_name": "<from detect_function result>",
  "business_logic_summary": "<one-line description>",
  "successful_mappings": [<from summarize_execution_results>],
  "crashes": [<from summarize_execution_results>],
  "edge_cases": [<from summarize_execution_results>]
}

## CRITICAL RULES:
- You MUST write the JSON as your final chat message. Do NOT just call tools and stop.
- Do NOT invent data. Use ONLY what the tools return.
- Include ALL entries from summarize_execution_results — do not omit any.
- The function_name must be the LEGACY function name (e.g. "process_transaction").
- Output ONLY the JSON. No markdown, no code fences, no explanations.
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