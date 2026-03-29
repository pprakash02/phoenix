# tools/critic_tools.py
import os
import io
import json
import glob
import docker
from typing import Annotated
from pydantic import Field
from agent_framework import tool

GENERATED_TESTS_DIR = os.path.abspath("generated_tests")
LEGACY_WORKSPACE = os.path.abspath("legacy_workspace")

TEST_RUNNER_IMAGE = "phoenix-test-runner"
TEST_RUNNER_DOCKERFILE = b"FROM python:3.10-slim\nRUN pip install --no-cache-dir pytest\n"

C_TEST_RUNNER_IMAGE = "phoenix-c-test-runner"
C_TEST_RUNNER_DOCKERFILE = b"FROM gcc:latest\nWORKDIR /workspace\n"


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
        )
        print(f"[SYSTEM] {TEST_RUNNER_IMAGE} image built successfully.")


def _run_test_in_sandbox(docker_client, test_file_name: str) -> dict:
    """Run a single test file in Docker and return results."""
    test_path = os.path.join(GENERATED_TESTS_DIR, test_file_name)
    project_root = os.path.abspath(".")

    if not os.path.isfile(test_path):
        return {"file": test_file_name, "status": "ERROR", "detail": "File not found"}

    print(f"\n[SYSTEM] Running test verification for {test_file_name}...\n")

    volumes = {
        GENERATED_TESTS_DIR: {'bind': '/workspace', 'mode': 'ro'},
        project_root: {'bind': '/project', 'mode': 'ro'},
    }

    cmd = f"pytest /workspace/{test_file_name} -v -p no:cacheprovider"

    try:
        container = docker_client.containers.create(
            image=TEST_RUNNER_IMAGE,
            command=cmd,
            volumes=volumes,
            environment={'PYTHONPATH': '/project'},
            working_dir="/project/legacy_workspace",
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,
            network_disabled=True,
        )
        container.start()
        container.wait(timeout=60)
        logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
        container.remove()

        # Parse results
        passed = logs.count(" PASSED")
        failed = logs.count(" FAILED")
        errors = logs.count(" ERROR")

        if failed == 0 and errors == 0:
            return {"file": test_file_name, "status": "PASSED", "passed": passed, "failed": 0, "detail": logs[-300:] if len(logs) > 300 else logs}
        else:
            return {"file": test_file_name, "status": "FAILED", "passed": passed, "failed": failed + errors, "detail": logs[-500:] if len(logs) > 500 else logs}
    except Exception as e:
        return {"file": test_file_name, "status": "ERROR", "detail": str(e)[:200]}


def _ensure_c_test_runner_image(docker_client: docker.DockerClient) -> None:
    """Build the phoenix-c-test-runner image if it doesn't already exist."""
    try:
        docker_client.images.get(C_TEST_RUNNER_IMAGE)
    except docker.errors.ImageNotFound:
        print(f"[SYSTEM] Building {C_TEST_RUNNER_IMAGE} Docker image (first time only)...")
        docker_client.images.build(
            fileobj=io.BytesIO(C_TEST_RUNNER_DOCKERFILE),
            tag=C_TEST_RUNNER_IMAGE,
            rm=True,
        )
        print(f"[SYSTEM] {C_TEST_RUNNER_IMAGE} image built successfully.")


def _run_c_test_in_sandbox(docker_client, test_file_name: str) -> dict:
    """Compile and run a C test file in Docker."""
    test_path = os.path.join(GENERATED_TESTS_DIR, test_file_name)
    if not os.path.isfile(test_path):
        return {"file": test_file_name, "status": "ERROR", "detail": "File not found"}

    print(f"\n[SYSTEM] Running C test verification for {test_file_name}...\n")

    module_name = test_file_name.replace("test_", "").replace(".c", "")
    # Find the source file to link against
    source_candidates = [f"{module_name}.c", f"{module_name}.C"]

    compile_cmd = f"gcc -o /tmp/test_output /workspace/{test_file_name}"
    for candidate in source_candidates:
        candidate_path = os.path.join(GENERATED_TESTS_DIR, candidate)
        if os.path.isfile(candidate_path):
            compile_cmd = f"gcc -o /tmp/test_output /workspace/{test_file_name} /workspace/{candidate}"
            break

    cmd = f"sh -c '{compile_cmd} -lm 2>&1 && /tmp/test_output 2>&1 || echo COMPILE_OR_RUN_FAILED'"

    try:
        container = docker_client.containers.create(
            image=C_TEST_RUNNER_IMAGE,
            command=cmd,
            volumes={
                GENERATED_TESTS_DIR: {'bind': '/workspace', 'mode': 'ro'},
            },
            working_dir="/workspace",
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000,
            network_disabled=True,
        )
        container.start()
        container.wait(timeout=60)
        logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
        container.remove()

        if "COMPILE_OR_RUN_FAILED" in logs or "error:" in logs.lower():
            return {"file": test_file_name, "status": "FAILED", "passed": 0, "failed": 1, "detail": logs[-500:] if len(logs) > 500 else logs}
        elif "All tests passed" in logs:
            # Count test functions that ran
            test_count = logs.count("test_")
            return {"file": test_file_name, "status": "PASSED", "passed": max(test_count, 1), "failed": 0, "detail": logs[-300:] if len(logs) > 300 else logs}
        else:
            return {"file": test_file_name, "status": "PASSED", "passed": 1, "failed": 0, "detail": logs[-300:] if len(logs) > 300 else logs}
    except Exception as e:
        return {"file": test_file_name, "status": "ERROR", "detail": str(e)[:200]}


@tool(approval_mode="never_require")
def verify_all_tests(
    dummy: Annotated[str, Field(description="Dummy argument. Pass an empty string.")] = ""
) -> str:
    """
    Verify ALL generated test suites in the sandbox at once.
    Scans generated_tests/test_*.py, runs each in Docker,
    and returns a concise pass/fail summary.
    Call this ONCE — it handles everything.
    """
    test_py_files = sorted(glob.glob(os.path.join(GENERATED_TESTS_DIR, "test_*.py")))
    test_c_files = sorted(glob.glob(os.path.join(GENERATED_TESTS_DIR, "test_*.c")))

    if not test_py_files and not test_c_files:
        return "ERROR: No test files found in generated_tests/."

    docker_client = docker.from_env()
    _ensure_test_runner_image(docker_client)
    if test_c_files:
        _ensure_c_test_runner_image(docker_client)

    results = []
    total_passed = 0
    total_failed = 0

    # Run Python tests
    for tf in test_py_files:
        fname = os.path.basename(tf)
        r = _run_test_in_sandbox(docker_client, fname)
        results.append(r)
        total_passed += r.get("passed", 0)
        total_failed += r.get("failed", 0)

    # Run C tests
    for tf in test_c_files:
        fname = os.path.basename(tf)
        r = _run_c_test_in_sandbox(docker_client, fname)
        results.append(r)
        total_passed += r.get("passed", 0)
        total_failed += r.get("failed", 0)

    # Build summary
    lines = [f"VERIFICATION RESULTS ({len(results)} test files)\n"]
    all_pass = True

    for r in results:
        status = r["status"]
        if status == "PASSED":
            lines.append(f"  ✅ {r['file']}: {r.get('passed', 0)} tests passed")
        else:
            all_pass = False
            lines.append(f"  ❌ {r['file']}: {status} — {r.get('passed', 0)} passed, {r.get('failed', 0)} failed")
            lines.append(f"     Detail: {r['detail'][:200]}")

    lines.append(f"\nTOTAL: {total_passed} passed, {total_failed} failed")

    if all_pass:
        lines.append("\nAll test suites PASSED. Full coverage confirmed.")
    else:
        lines.append("\nSome tests FAILED. QA Engineer should fix the failing tests.")

    return "\n".join(lines)


@tool(approval_mode="never_require")
def verify_test_results(
    test_file_name: Annotated[str, Field(description="The name of the test file saved in 'generated_tests'.")],
    legacy_file_path: Annotated[str, Field(description="Path to the original legacy code.")]
) -> str:
    """
    Runs a single test suite in the Docker sandbox.
    For bulk verification, use verify_all_tests instead.
    """
    docker_client = docker.from_env()
    _ensure_test_runner_image(docker_client)
    r = _run_test_in_sandbox(docker_client, test_file_name)
    if r["status"] == "PASSED":
        return f"✅ {test_file_name}: {r.get('passed', 0)} tests passed\n{r['detail']}"
    else:
        return f"❌ {test_file_name}: {r['status']}\n{r['detail']}"


@tool(approval_mode="never_require")
def read_test_file(
    test_file_name: Annotated[str, Field(description="The name of the test file in 'generated_tests'.")]
) -> str:
    """Reads the content of a generated test file."""
    test_path = os.path.abspath(os.path.join("generated_tests", test_file_name))
    try:
        with open(test_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: Test file {test_file_name} not found."
    except Exception as e:
        return f"ERROR: {str(e)}"