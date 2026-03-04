# test_sandbox.py
from tools.docker_sandbox import run_legacy_code_in_sandbox

print("--- TEST 1: Normal Execution ---")
# Simulating the Observer passing a valid argument
success_log = run_legacy_code_in_sandbox(
    file_path="legacy_workspace/legacy_billing.py",
    input_args="100"
)
print(success_log)

print("\n--- TEST 2: Catching a Crash ---")
# Simulating the Observer passing an edge-case argument that triggers the ZeroDivisionError
crash_log = run_legacy_code_in_sandbox(
    file_path="legacy_workspace/legacy_billing.py",
    input_args="0"
)
print(crash_log)