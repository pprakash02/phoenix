import docker
import os
from pydantic import Field
from agent_framework import tool

@tool
def run_legacy_code_in_sandbox(
    file_path: str = Field(description="The absolute or relative path to the legacy Python file."),
    input_args: str = Field(default="", description="Command line arguments to pass to the script.")
) -> str:
    """
    Executes a legacy Python script securely inside an isolated, air-gapped Docker container.
    Returns the raw terminal output (stdout/stderr) for the Analyst to review.
    """
    try:
        # Connects to the local Docker daemon
        client = docker.from_env()
    except docker.errors.DockerException:
        return "System Error: Docker daemon is not running on the host. Please start Docker."

    # Resolve paths to mount the volume correctly
    abs_path = os.path.abspath(file_path)
    dir_name = os.path.dirname(abs_path)
    file_name = os.path.basename(abs_path)

    print(f"\n[SYSTEM] Spinning up secure Phoenix sandbox for {file_name}...")

    try:
        # Execute the container with strict security boundaries
        raw_logs = client.containers.run(
            image="python:3.10-slim",  # Fast, lightweight base image
            command=f"python /workspace/{file_name} {input_args}",
            volumes={
                dir_name: {'bind': '/workspace', 'mode': 'ro'}  # CRITICAL: Read-Only mount
            },
            remove=True,  # Auto-destroy container after run
            network_disabled=True,  # Air-gapped to prevent data leaks
            mem_limit="256m",  # Prevent memory bomb crashes
            cpu_period=100000,
            cpu_quota=50000  # Throttle to 50% CPU
        )

        # The Docker SDK returns bytes, so we decode them into a standard text string
        logs_str = raw_logs.decode('utf-8') if isinstance(raw_logs, bytes) else str(raw_logs)
        return f"Execution Successful. Output Logs:\n{logs_str}"

    except docker.errors.ContainerError as e:
        # The SDK stores crash traces in the stderr attribute as bytes
        error_msg = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e.stderr)
        return f"Execution Failed with Exit Code {e.exit_status}.\nError Logs:\n{error_msg}"
    except Exception as e:
        # Captures Docker-level system faults
        return f"Sandbox Fault: Could not execute environment. {str(e)}"