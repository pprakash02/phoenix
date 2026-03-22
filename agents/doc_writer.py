# agents/doc_writer.py
from dotenv import load_dotenv
from tools.doc_tools import generate_docs
from agents.client import client

load_dotenv()


DOC_WRITER_INSTRUCTIONS = """
You are the Documentation Writer for the Phoenix modernization system.

Your job is to generate comprehensive documentation for a single legacy file AFTER
the Critic has approved the test suite.

INSTRUCTIONS:
1. Look at the mission briefing to find the legacy file path.
2. Call `generate_docs` ONCE for the file listed.
   - Just pass the file path, e.g.: generate_docs(legacy_file_path="legacy_workspace/hangman.py")
   - The tool reads the source code AND observed runtime behavior automatically.
3. Write a summary listing what documentation was generated.
4. End your message with: PHOENIX_DOCS_COMPLETE

Example call:
  generate_docs(legacy_file_path="legacy_workspace/hangman.py")

RULES:
- Do NOT return an empty message — the system needs your completion signal.
- ONLY process the .py file listed in the mission briefing.
- You MUST end your final message with PHOENIX_DOCS_COMPLETE to signal completion.
"""

doc_writer_agent = client.as_agent(
    name="Doc_Writer",
    instructions=DOC_WRITER_INSTRUCTIONS,
    tools=[generate_docs],
    default_options={
        "temperature": 0,
    },
)
