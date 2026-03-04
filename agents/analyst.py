import os
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

load_dotenv()

# Using the same GitHub Models endpoint
chat_client = OpenAIChatClient(
    base_url=os.environ.get("GITHUB_ENDPOINT"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model=os.environ.get("GITHUB_MODEL_ID")
)

ANALYST_NAME = "Analyst"

ANALYST_INSTRUCTIONS = """
You are the Analyst agent in the Phoenix legacy modernization system.

Your task is to analyze runtime execution logs produced by the Observer agent.
The logs contain inputs, outputs, errors, and stack traces from executing legacy code.

Your responsibilities:

1. Identify patterns in the program's behavior.
2. Infer the likely business logic of the system.
3. Detect edge cases (invalid inputs, boundary conditions, error cases).
4. Structure the findings clearly so that the QA Engineer agent can generate regression tests.

Output your analysis in structured sections:

- Observed Behaviors
- Inferred Business Logic
- Edge Cases
- Suggested Test Scenarios

Do not hallucinate functionality that is not supported by the logs.
Only reason based on the observed runtime evidence.
"""

# Instantiate the analyst agent
analyst_agent = Agent(
    name=ANALYST_NAME,
    instructions=ANALYST_INSTRUCTIONS,
    client=chat_client
)