# tools/critic_tools.py
import os
from typing import Annotated
from pydantic import Field
from agent_framework import tool
from tools.docker_sandbox import run_legacy_code_in_sandbox

@tool(approval_mode="never_require")
def verify_test_results(
    test_file_name: Annotated[str, Field(description="The name of the test file saved in 'generated_tests'.")],
    legacy_file_path: Annotated[str, Field(description="Path to the original legacy code.")]
) -> str:
    """
    Runs the generated test suite in the Docker sandbox to confirm it passes.
    """
    test_path = os.path.abspath(os.path.join("generated_tests", test_file_name))
    legacy_dir = os.path.dirname(os.path.abspath(legacy_file_path))

    # Command to install pytest and run the test file
    cmd = f"sh -c 'pip install --quiet pytest && pytest /workspace/{test_file_name} -v'"

    # Mount legacy directory as /legacy and set PYTHONPATH so imports work
    extra_volumes = [(legacy_dir, '/legacy')]
    env = {'PYTHONPATH': '/legacy'}

    return run_legacy_code_in_sandbox(
        file_path=test_path,
        input_args="",          # not used because we override command
        extra_volumes=extra_volumes,
        env=env,
        command=cmd
    )


@tool(approval_mode="never_require")
def read_test_file(
    test_file_name: Annotated[str, Field(description="The name of the test file in 'generated_tests'.")]
) -> str:
    """
    Reads the content of a generated test file.
    """
    test_path = os.path.abspath(os.path.join("generated_tests", test_file_name))
    try:
        with open(test_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"ERROR: Test file {test_file_name} not found in generated_tests directory."
    except Exception as e:
        return f"ERROR: Failed to read test file: {str(e)}"