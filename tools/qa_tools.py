import os
import json
import asyncio
from typing import Annotated
from pydantic import Field
from agent_framework import tool
from agent_framework._types import Message
from agents.client import client


CAPTURES_FILE = os.path.abspath("generated_tests/observer_captures.json")
OUTPUT_DIR = os.path.abspath("generated_tests")


def _load_captures_for_module(module_name: str) -> list[dict]:
    """Load capture records for a specific module."""
    if not os.path.exists(CAPTURES_FILE):
        return []
    with open(CAPTURES_FILE, "r") as f:
        all_records = json.load(f)
    return [r for r in all_records if r.get("module") == module_name]


def _read_source(file_path: str) -> str:
    """Read source code from a file."""
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        return ""
    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _build_capture_context(records: list[dict]) -> str:
    """Build a human-readable summary of observed I/O for the LLM prompt."""
    if not records:
        return "No runtime captures available."

    lines = []
    by_function = {}
    for r in records:
        func = r.get("function", "unknown")
        if func not in by_function:
            by_function[func] = {"successes": [], "crashes": []}
        if r.get("status") == "success":
            by_function[func]["successes"].append(r)
        else:
            by_function[func]["crashes"].append(r)

    for func_name, data in by_function.items():
        lines.append(f"\n### Function: `{func_name}`")
        if data["successes"]:
            lines.append("Successful calls:")
            for r in data["successes"]:
                args = r.get("inputs", {}).get("args", [])
                output = r.get("output")
                lines.append(f"  Input: {args} → Output: {repr(output)}")
        if data["crashes"]:
            lines.append("Crashed calls:")
            for r in data["crashes"]:
                args = r.get("inputs", {}).get("args", [])
                error = r.get("error", "unknown")
                lines.append(f"  Input: {args} → Error: {error}")

    return "\n".join(lines)


def _generate_tests_via_llm(module_name: str, legacy_path: str,
                            source_code: str, records: list[dict]) -> str:
    """Use the LLM to generate an intelligent, comprehensive pytest suite."""
    capture_context = _build_capture_context(records)

    # Build import path: legacy_workspace/hangman.py -> legacy_workspace.hangman
    import_module = legacy_path.replace("/", ".").replace(".py", "")

    prompt = f"""You are an expert Python test engineer. Generate a comprehensive pytest regression test suite for the following module.

Module name: {module_name}
Import path: {import_module}
Source file: {legacy_path}

Source code:
```python
{source_code}
```

Observed runtime behavior (from automated captures):
{capture_context}

INSTRUCTIONS:
1. Generate a COMPLETE, runnable pytest file.
2. Import from `{import_module}` (e.g., `from {import_module} import func_name`).
3. For EACH testable function (no input() calls), generate tests covering:
   - All observed success cases as regression tests (exact input→output assertions)
   - All observed crash/exception cases (pytest.raises)
   - Additional edge cases you can infer from the code (empty inputs, boundary values, type errors)
   - For float results, use `pytest.approx()`
   - For non-deterministic functions (e.g., random choice), assert membership instead of exact value
4. Use descriptive test names like `test_<func>_<scenario>`.
5. Include docstrings explaining what each test verifies.
6. If a function's output is very large (e.g., loading a word list), just assert `result is not None`.

RULES:
- Return ONLY the Python code, no markdown fences, no explanation.
- Start with imports: `import pytest` and function imports.
- Every test must be a standalone function (no classes needed).
- Do NOT test functions that use `input()`.
"""

    print(f"\n[SYSTEM] Generating intelligent tests for {module_name} via LLM...\n")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(1) as pool:
            def run_sync():
                return asyncio.run(client.get_response(
                    messages=[Message("user", [prompt])],
                    default_options={"temperature": 0.1}
                ))
            response = pool.submit(run_sync).result()
    else:
        response = asyncio.run(client.get_response(
            messages=[Message("user", [prompt])],
            default_options={"temperature": 0.1}
        ))

    test_code = response.messages[-1].text

    # Strip markdown fences if the LLM wrapped the code
    if test_code.startswith("```python"):
        test_code = test_code[len("```python"):].strip()
    if test_code.startswith("```"):
        test_code = test_code[3:].strip()
    if test_code.endswith("```"):
        test_code = test_code[:-3].strip()

    return test_code


def _format_value(val) -> str:
    """Format a Python value for use in test code (fallback generator)."""
    if val is None:
        return "None"
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, str):
        return repr(val)
    if isinstance(val, (int, float)):
        if isinstance(val, float):
            import math
            if math.isnan(val):
                return "float('nan')"
            if math.isinf(val):
                return "float('inf')" if val > 0 else "float('-inf')"
        return repr(val)
    if isinstance(val, list):
        items = ", ".join(_format_value(v) for v in val)
        return f"[{items}]"
    if isinstance(val, dict):
        items = ", ".join(f"{_format_value(k)}: {_format_value(v)}" for k, v in val.items())
        return "{" + items + "}"
    return repr(val)


def _generate_test_code_fallback(module_name: str, legacy_path: str, records: list[dict]) -> tuple[str, int]:
    """Fallback: generate a template-based pytest file from capture records."""
    by_function = {}
    for r in records:
        func = r.get("function", "unknown")
        if func not in by_function:
            by_function[func] = {"successes": [], "crashes": []}
        if r.get("status") == "success":
            by_function[func]["successes"].append(r)
        else:
            by_function[func]["crashes"].append(r)

    import_module = legacy_path.replace("/", ".").replace(".py", "")
    all_funcs = list(by_function.keys())
    imports = ", ".join(all_funcs)

    lines = []
    lines.append(f"# Auto-generated test suite for {module_name}")
    lines.append(f"# Source: {legacy_path}")
    lines.append(f"# Generated by Phoenix QA Engineer (template fallback)")
    lines.append("")
    lines.append("import pytest")
    lines.append("import math")
    lines.append(f"from {import_module} import {imports}")
    lines.append("")
    lines.append("")

    test_count = 0
    for func_name, data in by_function.items():
        for i, record in enumerate(data["successes"]):
            args = record.get("inputs", {}).get("args", [])
            output = record.get("output")
            output_str = str(output)
            args_str = ", ".join(_format_value(a) for a in args)

            if output_str.startswith("[list of ") or "[truncated]" in output_str or len(output_str) > 500:
                lines.append(f"def test_{func_name}_success_{i}():")
                lines.append(f"    result = {func_name}({args_str})")
                lines.append(f"    assert result is not None")
                lines.append("")
                lines.append("")
                test_count += 1
                continue

            expected = _format_value(output)
            lines.append(f"def test_{func_name}_success_{i}():")
            lines.append(f"    result = {func_name}({args_str})")
            if isinstance(output, float):
                lines.append(f"    assert result == pytest.approx({expected})")
            else:
                lines.append(f"    assert result == {expected}")
            lines.append("")
            lines.append("")
            test_count += 1

        for i, record in enumerate(data["crashes"]):
            args = record.get("inputs", {}).get("args", [])
            error = record.get("error", "")
            error_type = "Exception"
            if ": " in error:
                error_type = error.split(":")[0].strip()
            elif error:
                error_type = error.strip()
            args_str = ", ".join(_format_value(a) for a in args)
            lines.append(f"def test_{func_name}_crash_{i}():")
            lines.append(f"    with pytest.raises({error_type}):")
            lines.append(f"        {func_name}({args_str})")
            lines.append("")
            lines.append("")
            test_count += 1

    return "\n".join(lines), test_count


@tool(approval_mode="never_require")
def generate_tests(
    module_name: Annotated[str, Field(description="The module name to generate tests for, e.g. 'hangman' or 'legacy_billing'.")],
    legacy_file_path: Annotated[str, Field(description="The path to the legacy file, e.g. 'legacy_workspace/hangman.py'.")]
) -> str:
    """
    Generate an intelligent PyTest regression suite for a legacy module using LLM.
    Reads the captured runtime data from observer_captures.json and the source code,
    then uses the LLM to generate comprehensive tests with edge cases.
    Falls back to template-based generation if LLM fails.
    Saves the test file to generated_tests/test_<module_name>.py.

    Call this ONCE per module.
    """
    records = _load_captures_for_module(module_name)
    if not records:
        return f"ERROR: No capture records found for module '{module_name}'."

    source_code = _read_source(legacy_file_path)

    # Primary: LLM-based intelligent test generation
    try:
        test_code = _generate_tests_via_llm(module_name, legacy_file_path, source_code, records)
        generation_method = "LLM"
    except Exception as e:
        print(f"[SYSTEM] LLM test generation failed for {module_name}: {e}")
        print(f"[SYSTEM] Falling back to template-based generation...")
        test_code, _ = _generate_test_code_fallback(module_name, legacy_file_path, records)
        generation_method = "template fallback"

    # Save the test file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    test_file = os.path.join(OUTPUT_DIR, f"test_{module_name}.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_code)

    # Count tests in the generated code
    test_count = test_code.count("\ndef test_") + (1 if test_code.startswith("def test_") else 0)

    return (
        f"Generated test_{module_name}.py with {test_count} test cases ({generation_method}).\n"
        f"Saved to: {test_file}\n"
        f"Tests cover observed successes, crashes, and LLM-inferred edge cases."
    )


@tool(approval_mode="never_require")
def save_test_suite(
        code: Annotated[str, Field(description="The complete, raw Python pytest code to save.")],
        file_name: Annotated[str, Field(description="The name of the test file (e.g., test_my_module.py).")]
) -> str:
    """
    Saves a manually written PyTest suite to the local 'generated_tests' directory.
    Use generate_tests instead for automatic generation from captures.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, file_name)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        return f"SUCCESS: Test suite successfully saved to {file_path}"
    except Exception as e:
        return f"ERROR: Failed to save test suite. {str(e)}"