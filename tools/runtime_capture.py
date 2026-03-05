# tools/runtime_capture.py
import os
import json
from pydantic import Field
from agent_framework import tool

# Import the existing sandbox tool to run our instrumented code securely
from tools.docker_sandbox import run_legacy_code_in_sandbox


@tool(approval_mode="never_require")
def capture_function_runtime(
        file_path: str = Field(description="The absolute or relative path to the legacy Python file."),
        function_name: str = Field(description="The specific function to instrument (e.g., process_transaction)."),
        test_inputs: list[str] = Field(description="A list of string inputs to pass to the function.")
) -> str:
    """
    Dynamically attaches a decorator to a legacy function to capture its exact inputs,
    outputs, and exceptions. Runs the instrumented code securely in the Docker sandbox.
    """
    abs_path = os.path.abspath(file_path)
    dir_name = os.path.dirname(abs_path)
    module_name = os.path.basename(abs_path).replace(".py", "")

    # We create a temporary script inside the legacy workspace
    harness_path = os.path.join(dir_name, "phoenix_harness.py")

    # This Python script injects the decorator into the legacy code at runtime
    harness_code = f"""
import sys
import json
import traceback

sys.path.append('/workspace')
import {module_name}

# The decorator that captures live runtime data
def runtime_logger(func):
    def wrapper(*args, **kwargs):
        capture_data = {{
            "function": "{function_name}",
            "inputs": {{"args": args, "kwargs": kwargs}},
            "status": "success",
            "output": None,
            "error": None
        }}
        try:
            result = func(*args, **kwargs)
            capture_data["output"] = result
            return result
        except Exception as e:
            capture_data["status"] = "crashed"
            capture_data["error"] = f"{{type(e).__name__}}: {{str(e)}}"
            capture_data["traceback"] = traceback.format_exc()
        finally:
            print(json.dumps(capture_data))
    return wrapper

# Monkey-patch the legacy module with the decorator
if hasattr({module_name}, "{function_name}"):
    original_func = getattr({module_name}, "{function_name}")
    setattr({module_name}, "{function_name}", runtime_logger(original_func))
else:
    print(json.dumps({{"error": "Function {function_name} not found."}}))
    sys.exit(1)

# Execute the test inputs provided by the Observer
for inp in {test_inputs}:
    try:
        getattr({module_name}, "{function_name}")(inp)
    except BaseException:
        pass
"""

    with open(harness_path, "w") as f:
        f.write(harness_code)

    print(f"\n[SYSTEM] Attaching Observer runtime decorators to '{function_name}'...")

    try:
        # We trigger the sandbox, but target our dynamic harness instead of the raw file
        logs = run_legacy_code_in_sandbox(file_path=harness_path, input_args="")
        return f"Runtime Capture for {function_name}:\n{logs}"
    finally:
        # Clean up the harness so we don't pollute the user's legacy repository
        if os.path.exists(harness_path):
            os.remove(harness_path)