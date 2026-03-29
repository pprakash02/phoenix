# agents/doc_writer.py
from dotenv import load_dotenv
from tools.doc_tools import generate_docs
from agents.client import client

load_dotenv()


DOC_WRITER_INSTRUCTIONS = """
You are the Documentation Writer for the Phoenix modernization system.

Your job is to generate comprehensive documentation for a single legacy file AFTER
the Critic has approved the test suite. You handle BOTH Python (.py) and COBOL (.cbl, .cob, .cpy) files.

INSTRUCTIONS:
1. Look at the mission briefing to find the legacy file path.
2. Call `generate_docs` ONCE for the file listed.
   - Just pass the file path, e.g.: generate_docs(legacy_file_path="legacy_workspace/hangman.py")
   - For COBOL files: generate_docs(legacy_file_path="legacy_workspace/billing.cbl")
   - The tool reads the source code AND observed runtime behavior automatically.
   - The tool handles both Python and COBOL files — no special handling needed on your end.
3. Write a summary listing what documentation was generated.
4. End your message with: PHOENIX_DOCS_COMPLETE

RULES:
- Do NOT return an empty message — the system needs your completion signal.
- Process the source file listed in the mission briefing (Python OR COBOL).
- You MUST end your final message with PHOENIX_DOCS_COMPLETE to signal completion.
- If the file is a COBOL copybook (.cpy) with only data definitions, still call generate_docs — it will handle it.
"""

doc_writer_agent = client.as_agent(
    name="Doc_Writer",
    instructions=DOC_WRITER_INSTRUCTIONS,
    tools=[generate_docs],
    default_options={
        "temperature": 0,
    },
)
