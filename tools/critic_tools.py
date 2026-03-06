# tools/critic_tools.py
import os
import io
import docker
from typing import Annotated
from pydantic import Field
from agent_framework import tool

GENERATED_TESTS_DIR = os.path.abspath("generated_tests")
LEGACY_WORKSPACE = os.path.abspath("legacy_workspace")

TEST_RUNNER_IMAGE = "phoenix-test-runner"
TEST_RUNNER_DOCKERFILE = b"FROM python:3.10-slim\nRUN pip install --no-cache-dir pytest\n"

def _ensure_test_runner_image(docker_client: docker.DockerClient) -> None:
    """Build the phoenix-test-runner image if it doesn't already exist."""
    try:
        docker_client.images.get(TEST_RUNNER_IMAGE)
    except docker.errors.ImageNotFound:
        print(f"[SYSTEM] Building {TEST_RUNNER_IMAGE} Docker image (first time only)...")
        docker_client.images.build(
            fileobj=io.BytesIO(TEST_RUNNER_DOCKERFILE),
            tag=TEST_RUNNER_IMAGE,
            rm=True,
            network_mode="host"
        )
        print(f"[SYSTEM] {TEST_RUNNER_IMAGE} image built successfully.")


@tool(approval_mode="never_require")
def verify_test_results(
    test_file_name: Annotated[str, Field(description="The name of the test file saved in 'generated_tests'.")],
    legacy_file_path: Annotated[str, Field(description="Path to the original legacy code.")]
) -> str:
    """
    Runs the generated test suite in the Docker sandbox to confirm it passes.
    Uses a custom Docker image with pytest pre-installed. Auto-builds the image if missing.
    Returns the full pytest output (stdout + stderr) regardless of pass/fail.
    """
    test_path = os.path.join(GENERATED_TESTS_DIR, test_file_name)
    # Mount the project root so `from legacy_workspace.legacy_billing import ...` resolves
    project_root = os.path.abspath(".")

    if not os.path.isfile(test_path):
        return f"ERROR: Test file not found: {test_path}"

    print(f"\n[SYSTEM] Running test verification for {test_file_name}...\n")

    try:
        docker_client = docker.from_env()
    except docker.errors.DockerException:
        return "System Error: Docker daemon is not running on the host. Please start Docker."

    try:
        _ensure_test_runner_image(docker_client)
    except Exception as e:
        return f"Docker Error: Failed to build test-runner image: {str(e)}"

    volumes = {
        GENERATED_TESTS_DIR: {'bind': '/workspace', 'mode': 'ro'},
        project_root: {'bind': '/project', 'mode': 'ro'},
    }

    cmd = f"pytest /workspace/{test_file_name} -v --tb=short"

    try:
        container = docker_client.containers.create(
            image=TEST_RUNNER_IMAGE,
            command=cmd,
            volumes=volumes,
            environment={'PYTHONPATH': '/project'},
            network_disabled=True,
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000
        )
        container.start()
        result = container.wait(timeout=60)
        logs = container.logs(stdout=True, stderr=True)
        container.remove()

        output = logs.decode("utf-8", errors="replace")
        exit_code = result.get("StatusCode", -1)

        if exit_code == 0:
            return f"ALL TESTS PASSED.\n\n{output}"
        else:
            return f"TESTS FAILED (exit code {exit_code}).\n\n{output}"
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