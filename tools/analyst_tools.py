import json
from typing import List, Dict, Any
from pydantic import Field
from agent_framework import tool


@tool
def parse_runtime_logs(
    raw_output: str = Field(
        description="Raw terminal output containing JSON runtime logs from the Observer."
    )
) -> List[Dict[str, Any]]:
    """
    Extract JSON objects from terminal output safely.
    Assumes logs may contain text mixed with JSON lines.
    """

    parsed_entries: List[Dict[str, Any]] = []

    for line in raw_output.splitlines():

        line = line.strip()

        if not line.startswith("{"):
            continue

        try:
            obj = json.loads(line)

            if "function" in obj:
                parsed_entries.append(obj)

        except json.JSONDecodeError:
            continue

    return parsed_entries


@tool
def detect_function(
    parsed_logs: List[Dict[str, Any]] = Field(
        description="Parsed runtime log dictionaries."
    )
) -> str:
    """
    Detect the primary function under test from logs.
    Returns the most common function name.
    """

    functions = [
        entry.get("function")
        for entry in parsed_logs
        if entry.get("function") is not None
    ]

    if not functions:
        return "unknown"

    return max(set(functions), key=functions.count)


@tool
def summarize_execution_results(
    parsed_logs: List[Dict[str, Any]] = Field(
        description="Parsed execution dictionaries."
    )
) -> Dict[str, Any]:
    """
    Aggregate results into successful mappings and crash reports.
    """

    summary = {
        "successful_mappings": [],
        "crashes": []
    }

    for entry in parsed_logs:

        inputs = entry.get("inputs", {})
        args = inputs.get("args", [])

        input_val = args[0] if args else None

        if entry.get("status") == "success":

            summary["successful_mappings"].append({
                "input": input_val,
                "output": entry.get("output")
            })

        else:

            summary["crashes"].append({
                "input": input_val,
                "error": entry.get("error"),
                "traceback": entry.get("traceback")
            })

    return summary