# tools/docker_sandbox.py
import docker
import os
from typing import Annotated, Dict, Optional
from pydantic import Field
from agent_framework import tool


@tool(approval_mode="never_require")
def run_legacy_code_in_sandbox(
        file_path: Annotated[str, Field(description="The absolute or relative path to the legacy Python file.")],
        input_args: Annotated[str, Field(description="Command line arguments to pass to the script.")] = "",
        extra_volumes: Annotated[Dict[str, str], Field(
            description="Additional volumes to mount. Keys are host paths, values are container paths.")] = {},
        env: Annotated[Dict[str, str], Field(description="Environment variables for the container.")] = {},
        command: Annotated[Optional[str], Field(
            description="Override the default command (e.g., 'pytest /workspace/test.py').")] = None,
        network_disabled: Annotated[bool, Field(
            description="Whether to disable network access in the container.")] = True
) -> str:
    """
    Executes a legacy Python script securely inside an isolated, air-gapped Docker container.
    Returns the raw terminal output (stdout/stderr) for the Analyst to review.
    """
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        return "System Error: Docker daemon is not running on the host. Please start Docker."

    abs_path = os.path.abspath(file_path)
    dir_name = os.path.dirname(abs_path)
    file_name = os.path.basename(abs_path)

    print(f"\n[SYSTEM] Spinning up secure Phoenix sandbox for {file_name}...")

    # Build volumes: primary mount + extra volumes
    volumes = {
        dir_name: {'bind': '/workspace', 'mode': 'ro'}
    }

    # Iterate over the dictionary items instead of a list of tuples
    for host_path, container_path in extra_volumes.items():
        volumes[host_path] = {'bind': container_path, 'mode': 'ro'}

    # Determine the command to run
    if command is None:
        # default: run the file with python
        cmd = f"python /workspace/{file_name} {input_args}"
    else:
        cmd = command

    try:
        raw_logs = client.containers.run(
            image="python:3.10-slim",
            command=cmd,
            volumes=volumes,
            environment=env,
            remove=True,
            network_disabled=network_disabled,
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=50000
        )
        logs_str = raw_logs.decode('utf-8') if isinstance(raw_logs, bytes) else str(raw_logs)
        return f"Execution Successful. Output Logs:\n{logs_str}"
    except docker.errors.ContainerError as e:
        error_msg = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e.stderr)
        return f"Execution Failed with Exit Code {e.exit_status}.\nError Logs:\n{error_msg}"
    except Exception as e:
        return f"Sandbox Fault: Could not execute environment. {str(e)}"