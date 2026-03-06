# tools/critic_tools.py
import os
import docker
from typing import Annotated
from pydantic import Field
from agent_framework import tool

GENERATED_TESTS_DIR = os.path.abspath("generated_tests")
LEGACY_WORKSPACE = os.path.abspath("legacy_workspace")

@tool(approval_mode="never_require")
def verify_test_results(
    test_file_name: Annotated[str, Field(description="The name of the test file saved in 'generated_tests'.")],
    legacy_file_path: Annotated[str, Field(description="Path to the original legacy code.")]
) -> str:
    """
    Runs the generated test suite in the Docker sandbox to confirm it passes.
    Uses Docker directly with network enabled so pytest can be installed.
    """
    test_path = os.path.join(GENERATED_TESTS_DIR, test_file_name)
    legacy_dir = os.path.dirname(os.path.abspath(legacy_file_path))

    if not os.path.isfile(test_path):
        return f"ERROR: Test file not found: {test_path}"

    print(f"\n[SYSTEM] Running test verification for {test_file_name}...\n")

    docker_client = docker.from_env()

    volumes = {
        GENERATED_TESTS_DIR: {'bind': '/workspace', 'mode': 'ro'},
        legacy_dir: {'bind': '/legacy', 'mode': 'ro'},
    }

    cmd = f"sh -c 'pip install --quiet pytest && pytest /workspace/{test_file_name} -v'"

    try:
        output = docker_client.containers.run(
            image="python:3.10-slim",
            command=cmd,
            volumes=volumes,
            environment={'PYTHONPATH': '/legacy'},
            remove=True,
            network_disabled=False,  # network ON to install pytest
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000
        )
        return output.decode("utf-8", errors="replace")
    except docker.errors.ContainerError as e:
        return f"Execution Failed with Exit Code {e.exit_status}.\n{e.stderr.decode('utf-8', errors='replace') if e.stderr else str(e)}"
    except Exception as e:
        return f"Docker Error: {str(e)}"


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