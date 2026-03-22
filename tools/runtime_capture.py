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

    # Build function specs as JSON, then base64-encode to avoid
    # string-escaping issues when embedding inside Python triple-quotes.
    import base64
    functions_json = json.dumps(functions)
    functions_b64 = base64.b64encode(functions_json.encode()).decode()
    # Build the file path as it will appear inside the sandbox container
    sandbox_file_path = f"/workspace/{os.path.basename(abs_path)}"
    # Base64-encode the path to avoid quoting issues (apostrophes, etc.)
    filepath_b64 = base64.b64encode(sandbox_file_path.encode()).decode()

    harness_code = f"""
import sys
import json
import traceback
import base64
import importlib.util

sys.path.append('/workspace')

# Decode function specs from base64 (avoids quoting/escaping issues)
functions = json.loads(base64.b64decode('{functions_b64}').decode())

# Decode file path from base64 (handles filenames with apostrophes/special chars)
_module_file = base64.b64decode('{filepath_b64}').decode()
_module_name = '_legacy_module'
try:
    _spec = importlib.util.spec_from_file_location(_module_name, _module_file)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_module_name] = _mod
    _spec.loader.exec_module(_mod)
except Exception as e:
    print(json.dumps({{"error": f"Failed to import {{_module_file}}: {{type(e).__name__}}: {{str(e)}}"}}))
    sys.exit(1)

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

for func_spec in functions:
    func_name = func_spec["name"]
    test_inputs = func_spec["test_inputs"]

    if not hasattr(_mod, func_name):
        print(json.dumps({{"error": f"Function {{func_name}} not found."}}))
        continue

    # Instrument the function
    original_func = getattr(_mod, func_name)
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
    setattr(_mod, func_name, original_func)
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

        # Diagnostic: log sandbox output if no records were captured
        if not new_records:
            print(f"[SYSTEM] WARNING: 0 records captured. Sandbox output preview:")
            preview = logs[:500] if len(logs) > 500 else logs
            print(preview)

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
    """Generate test inputs for the given function.
    
    Strategy: Use fast heuristic-based input generation by default (instant, no LLM).
    Only falls back to LLM for complex functions where heuristics produce uncertain results.
    This avoids rate limits and is much faster (~0ms vs ~2-5s per function).
    """
    args = [a.arg for a in func_node.args.args]
    if not args:
        return [[]]

    # Primary: fast heuristic-based inputs (instant, no API call)
    inputs = _smart_fallback_inputs(func_node, source_code)
    if inputs:
        return inputs
    
    # Absolute fallback: generic inputs
    print(f"[SYSTEM] Using generic fallback inputs for {func_node.name}")
    return [[0], [1], [-1], ["test"], [""], [True]]


def _smart_fallback_inputs(func_node: _ast.FunctionDef, source_code: str) -> list:
    """Generate type-aware fallback inputs by inspecting the function's AST and arg names."""
    args = [a.arg for a in func_node.args.args]
    if not args:
        return [[]]

    func_source = _ast.unparse(func_node) if hasattr(_ast, 'unparse') else ""

    def _infer_input_for_arg(arg_name: str) -> list:
        """Return a list of candidate values for a single argument based on heuristics."""
        name = arg_name.lower()

        # List/collection heuristics
        if any(hint in name for hint in ["list", "words", "items", "array", "elements",
                                          "letters", "guessed", "choices", "options"]):
            return [
                ["apple", "banana", "cherry"],
                ["a", "b", "c", "d", "e"],
                [],
                ["hello"],
                ["test", "word", "example", "data", "value"],
            ]

        # String heuristics
        if any(hint in name for hint in ["word", "string", "text", "name", "letter",
                                          "char", "secret", "message", "path", "file"]):
            return ["hello", "test", "", "a", "abcdef", "python"]

        # Boolean heuristics
        if any(hint in name for hint in ["flag", "is_", "has_", "with_", "enable",
                                          "should", "allow", "help"]):
            return [True, False]

        # Numeric heuristics
        if any(hint in name for hint in ["num", "count", "amount", "size", "length",
                                          "index", "val", "price", "total", "n"]):
            return [0, 1, -1, 10, 100, 0.5]

        # Also check how the arg is used in the function body
        if func_source:
            # If it's iterated over or indexed, probably a list/str
            if f"for " in func_source and f" in {arg_name}" in func_source:
                return ["hello", "test", "", "abcde"]
            if f"{arg_name}[" in func_source:
                return [["a", "b", "c"], ["test"], [1, 2, 3]]
            if f"len({arg_name})" in func_source:
                return ["hello", "test", "", [1, 2, 3]]

        # Default: try multiple types
        return [0, 1, -1, "test", "", True]

    # Generate combinations
    per_arg_values = [_infer_input_for_arg(a) for a in args]
    num_args = len(args)

    if num_args == 1:
        return [[v] for v in per_arg_values[0]]

    # For multi-arg functions, zip across the candidate lists
    max_len = max(len(vals) for vals in per_arg_values)
    inputs = []
    for i in range(min(max_len, 8)):
        combo = []
        for vals in per_arg_values:
            combo.append(vals[i % len(vals)])
        inputs.append(combo)
    return inputs

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