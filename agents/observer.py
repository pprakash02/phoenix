# agents/observer.py
import os
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv

from tools.runtime_capture import observe_file

from agents.client import client

load_dotenv()


OBSERVER_NAME = "Observer"
OBSERVER_INSTRUCTIONS = """
You are the Observer agent for the Phoenix modernization system.
Your job is to capture runtime behavior from a single legacy Python file.

INSTRUCTIONS:
1. Look at the mission briefing to find the legacy file path.
2. Call `observe_file` ONCE for the file listed.
   - Just pass the file path. The tool handles everything else automatically.
3. After the call completes, write a summary listing what was captured.

Example:
- Call: observe_file(file_path="legacy_workspace/hangman.py")
- Then write: "Captured runtime data for hangman.py (7 functions)."

RULES:
- Do NOT read files or construct JSON — the tool does that for you.
- Do NOT return an empty message — downstream agents need your summary.
- ONLY process the .py file in the mission briefing.
"""

observer_agent = client.as_agent(
    name="Observer",
    instructions=OBSERVER_INSTRUCTIONS,
    tools=[
        observe_file,
    ],
    default_options={
        "temperature": 0,
    },
)