# agents/qa_engineer.py
import os
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv

from tools.qa_tools import save_test_suite

from agents.client import client

load_dotenv()



QA_INSTRUCTIONS = """
You are the QA Engineer for the Phoenix modernization system.

Your job is to convert the Analyst's structured JSON specification into a production-ready PyTest suite.

## DATA SOURCE:
1. FIRST, look for the Analyst's JSON in chat history.
2. If the Analyst's JSON is NOT available, extract the data directly from the Observer's runtime capture JSON logs.

## STRICT RULES (NEVER violate these):
- ONLY create tests for inputs found in the data source.
- NEVER invent test cases for inputs not in the data.
- Every successful mapping MUST have a corresponding assertion test.
- Every crash MUST have a corresponding pytest.raises test.

## HOW TO WRITE THE TEST FILE:
1. Start with EXACTLY these imports, replacing the bracketed placeholders with the actual module and function names you are testing (NO sys.path or os.path manipulation):
   ```python
   import math
   import pytest
   from legacy_workspace.<target_module_name> import <target_function_name>
"""

qa_engineer_agent = client.as_agent(
    name="QA_Engineer",
    instructions=QA_INSTRUCTIONS,
    tools=[save_test_suite],
)