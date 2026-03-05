import os
from typing import Annotated
from pydantic import Field
from agent_framework import tool

@tool(approval_mode="never_require")
def save_test_suite(
    code: Annotated[str, Field(description="The complete, raw Python pytest code to save.")],
    file_name: Annotated[str, Field(description="The name of the test file.")] = "test_legacy_billing.py"
) -> str:
    """
    Saves the generated PyTest suite to the local 'generated_tests' directory.
    """
    # Ensure the output directory exists
    output_dir = os.path.abspath("generated_tests")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, file_name)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        return f"SUCCESS: Test suite successfully saved to {file_path}"
    except Exception as e:
        return f"ERROR: Failed to save test suite. {str(e)}"