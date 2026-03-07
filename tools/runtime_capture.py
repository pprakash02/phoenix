# tools/runtime_capture.py
import os
import json
from typing import Annotated, Any
from pydantic import Field
from agent_framework import tool
from tools.docker_sandbox import run_legacy_code_in_sandbox


@tool(approval_mode="never_require")
def capture_module_runtime(
    file_path: Annotated[str, Field(description="Path to the legacy Python file (e.g., 'legacy_workspace/hangman.py').")],
    functions: Annotated[list[dict], Field(description="""A list of function specs to capture. Each spec is a dict with:
- "name": the function name (string)
- "test_inputs": list of test inputs for that function
  * Single-arg: each element is the value, e.g. ["val1", "val2"]
  * Multi-arg: each element is a LIST of args, e.g. [["arg1", "arg2"], ["arg1b", "arg2b"]]

Example:
[
  {"name": "unique_letters", "test_inputs": ["hello", "aaa", ""]},
  {"name": "has_player_won", "test_inputs": [["cat", ["c","a","t"]], ["cat", ["c"]]]}
]""")]
) -> str:
    """
    Captures runtime behavior for MULTIPLE functions in a single legacy file.
    This is a batch operation — call once per file to capture all testable functions.
    Each function is instrumented with a decorator that logs inputs, outputs, and exceptions.
    """
    abs_path = os.path.abspath(file_path)
    dir_name = os.path.dirname(abs_path)
    module_name = os.path.basename(abs_path).replace(".py", "")
    harness_path = os.path.join(dir_name, "phoenix_harness.py")

    # Build function specs as JSON
    functions_json = json.dumps(functions)

    harness_code = f"""
import sys
import json
import traceback

sys.path.append('/workspace')

import {module_name}

def runtime_logger(func_name, func):
    def wrapper(*args, **kwargs):
        capture_data = {{
            "function": func_name,
            "inputs": {{"args": list(args), "kwargs": dict(kwargs)}},
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
            print(json.dumps(capture_data, default=str))
    return wrapper

# Load function specs
functions = json.loads('''{functions_json}''')

for func_spec in functions:
    func_name = func_spec["name"]
    test_inputs = func_spec["test_inputs"]

    if not hasattr({module_name}, func_name):
        print(json.dumps({{"error": f"Function {{func_name}} not found."}}))
        continue

    # Instrument the function
    original_func = getattr({module_name}, func_name)
    instrumented = runtime_logger(func_name, original_func)

    # Run each test input
    for inp in test_inputs:
        try:
            if isinstance(inp, (list, tuple)):
                instrumented(*inp)
            else:
                instrumented(inp)
        except BaseException:
            pass

    # Restore original function for next iteration
    setattr({module_name}, func_name, original_func)
"""

    with open(harness_path, "w") as f:
        f.write(harness_code)

    func_names = [f["name"] for f in functions]
    print(f"\n[SYSTEM] Capturing runtime for {len(functions)} functions in {os.path.basename(file_path)}: {func_names}")

    try:
        logs = run_legacy_code_in_sandbox(file_path=harness_path, input_args="")

        # --- Persist results to shared file for downstream agents ---
        captures_dir = os.path.abspath("generated_tests")
        os.makedirs(captures_dir, exist_ok=True)
        captures_file = os.path.join(captures_dir, "observer_captures.json")

        # Parse JSON lines from the output
        new_records = []
        successes = 0
        crashes = 0
        for line in logs.split("\n"):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    record = json.loads(line)
                    # Truncate huge outputs (e.g., load_words returning 55K items)
                    output = record.get("output")
                    if output is not None:
                        output_str = json.dumps(output, default=str)
                        if len(output_str) > 500:
                            if isinstance(output, list):
                                record["output"] = f"[list of {len(output)} items]"
                            else:
                                record["output"] = str(output)[:200] + "... [truncated]"
                    record["module"] = module_name
                    new_records.append(record)
                    if record.get("status") == "success":
                        successes += 1
                    else:
                        crashes += 1
                except json.JSONDecodeError:
                    pass

        # Load existing captures and append
        existing = []
        if os.path.exists(captures_file):
            try:
                with open(captures_file, "r") as cf:
                    existing = json.load(cf)
            except (json.JSONDecodeError, IOError):
                existing = []

        # Remove old records for this module (in case of re-run)
        existing = [r for r in existing if r.get("module") != module_name]
        existing.extend(new_records)

        with open(captures_file, "w") as cf:
            json.dump(existing, cf, indent=2, default=str)

        print(f"[SYSTEM] Saved {len(new_records)} capture records to observer_captures.json")

        # Return a SHORT summary (not the full raw output)
        summary = f"Captured {len(new_records)} records for {module_name}.py ({len(functions)} functions): {successes} success, {crashes} crashed."
        summary += f"\nFunctions captured: {', '.join(func_names)}"
        summary += "\nFull data saved to observer_captures.json."
        return summary
    finally:
        if os.path.exists(harness_path):
            os.remove(harness_path)


# ─────────────────────────────────────────────
#  Simple wrapper for Observer agent
# ─────────────────────────────────────────────

import ast as _ast
import re as _re
import json as _json
import asyncio as _asyncio
from agent_framework._types import Message as _Message
from agents.client import client as _client


# ── LLM-based test input generation ──────────────────────────────

def _normalize_inputs(raw_inputs: list, num_args: int) -> list:
    """Ensure every element is a list of positional args matching function arity.
    
    The LLM may return:
      - [[1], [2]]          → correct for 1-arg
      - [1, 2, 3]           → flat values for 1-arg, needs wrapping
      - [[1, "a"], [2, "b"]] → correct for 2-arg
    This function normalises all forms into list-of-lists.
    """
    if not raw_inputs:
        return []

    normalised = []
    for item in raw_inputs:
        if isinstance(item, list):
            if len(item) == num_args:
                # Already correctly shaped, e.g. [5] for 1-arg or [1, "a"] for 2-arg
                normalised.append(item)
            elif num_args == 1:
                # The item IS the single argument (e.g. a list argument)
                normalised.append([item])
            else:
                # Best effort: use as-is
                normalised.append(item)
        else:
            # Flat scalar value — wrap for single-arg functions
            if num_args == 1:
                normalised.append([item])
            else:
                # Can't auto-fix multi-arg from scalar; skip
                continue
    return normalised


def _generate_inputs_via_llm(func_node: _ast.FunctionDef, source_code: str) -> list:
    """Use an LLM to synthesize realistic test inputs for the given function."""
    args = [a.arg for a in func_node.args.args]
    if not args:
        return [[]]
        
    client = _client
    num_args = len(args)
    
    # Extract the function's source code roughly
    func_source = _ast.unparse(func_node) if hasattr(_ast, 'unparse') else f"def {func_node.name}(...)"
    
    prompt = f"""
You are an expert software fuzzer. Your job is to generate a diverse set of valid and edge-case inputs for a Python function.

Function name: {func_node.name}
Arguments: {args}
Number of arguments: {num_args}

Here is the function's source code:
```python
{func_source}
```

For context, here is the full file source code:
```python
{source_code}
```

Please generate 5-10 distinct combinations of inputs to test this function thoroughly.
Return the results as a JSON object with a key "test_inputs" whose value is an array of arrays.
Each inner array MUST have exactly {num_args} element(s), one per argument.

For a function with 1 argument like `def foo(x)`, return:
{{"test_inputs": [[5], [0], [-1], [100]]}}

For a function with 2 arguments like `def bar(a, b)`, return:
{{"test_inputs": [["hello", 42], ["", 0], ["edge", -1]]}}

Return ONLY valid JSON. Do not include markdown code blocks or any other explanation.
"""
    
    try:
        try:
            loop = _asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(1) as pool:
                def run_sync():
                    return _asyncio.run(client.get_response(
                        messages=[_Message("user", [prompt])],
                        default_options={"temperature": 0.2, "response_format": {"type": "json_object"}}
                    ))
                response = pool.submit(run_sync).result()
        else:
            response = _asyncio.run(client.get_response(
                messages=[_Message("user", [prompt])],
                default_options={"temperature": 0.2, "response_format": {"type": "json_object"}}
            ))

        text = response.messages[-1].text
        
        # Strip potential markdown formatting if the model disobeys
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        parsed = _json.loads(text.strip())
        
        # Extract the list of inputs from various response shapes
        raw_inputs = None
        if isinstance(parsed, dict):
            # Look for "test_inputs" key first, then any list value
            raw_inputs = parsed.get("test_inputs")
            if raw_inputs is None:
                for val in parsed.values():
                    if isinstance(val, list):
                        raw_inputs = val
                        break
        elif isinstance(parsed, list):
            raw_inputs = parsed
        
        if raw_inputs:
            return _normalize_inputs(raw_inputs, num_args)
    except Exception as e:
        print(f"Warning: Failed to generate LLM fuzzing inputs for {func_node.name}: {e}")
        
    # Fallback: generate simple default inputs based on arg count
    print(f"[SYSTEM] Using fallback inputs for {func_node.name}")
    return [[0 for _ in args], [1 for _ in args], [-1 for _ in args]]

def _extract_testable_functions(file_path: str) -> list[dict]:
    """Parse a Python file's AST to extract testable function definitions."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = _ast.parse(source)
    except SyntaxError:
        return []

    functions = []
    for node in _ast.iter_child_nodes(tree):
        if isinstance(node, _ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            uses_input = any(
                isinstance(n, _ast.Call)
                and isinstance(getattr(n, "func", None), _ast.Name)
                and n.func.id == "input"
                for n in _ast.walk(node)
            )
            if not uses_input:
                functions.append({"name": node.name, "args": args, "node": node})
    return functions


@tool(approval_mode="never_require")
def observe_file(
    file_path: Annotated[str, Field(description="Path to the legacy Python file, e.g. 'legacy_workspace/hangman.py'.")]
) -> str:
    """
    Observe a legacy Python file: automatically discovers all testable functions,
    generates diverse test inputs, and captures their runtime behavior.
    Returns a short summary. Full data is saved to observer_captures.json for
    downstream agents to read.
    Call this ONCE per .py file.
    """
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}"

    functions = _extract_testable_functions(file_path)
    if not functions:
        return f"No testable functions found in {file_path}."

    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    function_specs = [
        {"name": fn["name"], "test_inputs": _generate_inputs_via_llm(fn.get("node"), source_code)}
        for fn in functions
    ]

    result = capture_module_runtime.func(
        file_path=file_path,
        functions=function_specs,
    )
    return result