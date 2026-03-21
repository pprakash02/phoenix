# tools/doc_tools.py
import os
import ast
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
    """Load observer capture records for a specific module."""
    if not os.path.exists(CAPTURES_FILE):
        return []
    with open(CAPTURES_FILE, "r") as f:
        all_records = json.load(f)
    return [r for r in all_records if r.get("module") == module_name]


def _extract_functions_source(file_path: str) -> list[dict]:
    """Parse a Python file and extract function names, signatures, and source."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    functions = []
    source_lines = source.splitlines()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            # Extract the function's source lines
            start = node.lineno - 1
            end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start + 1
            func_source = "\n".join(source_lines[start:end])
            functions.append({
                "name": node.name,
                "args": args,
                "source": func_source,
            })
    return functions


def _build_capture_summary(records: list[dict], func_name: str) -> str:
    """Build a human-readable summary of observed I/O for a function."""
    func_records = [r for r in records if r.get("function") == func_name]
    if not func_records:
        return "No runtime captures available."

    lines = []
    successes = [r for r in func_records if r.get("status") == "success"]
    crashes = [r for r in func_records if r.get("status") != "success"]

    for i, r in enumerate(successes[:5]):  # Limit to 5 examples
        args = r.get("inputs", {}).get("args", [])
        output = r.get("output")
        lines.append(f"  Input: {args} → Output: {output}")

    if crashes:
        lines.append(f"  Crashes observed: {len(crashes)}")
        for r in crashes[:3]:
            args = r.get("inputs", {}).get("args", [])
            error = r.get("error", "unknown")
            lines.append(f"  Input: {args} → Error: {error}")

    return "\n".join(lines) if lines else "No captures."


def _generate_docs_via_llm(module_name: str, source_path: str,
                           functions: list[dict], records: list[dict]) -> str:
    """Use the LLM to generate comprehensive markdown documentation."""
    # Build context for each function
    func_sections = []
    for func in functions:
        capture_summary = _build_capture_summary(records, func["name"])
        func_sections.append(f"""
### Function: `{func['name']}({', '.join(func['args'])})`

Source code:
```python
{func['source']}
```

Observed runtime behavior:
{capture_summary}
""")

    all_func_context = "\n".join(func_sections)

    prompt = f"""You are a technical documentation writer. Generate comprehensive, professional Markdown documentation for the following Python module.

Module name: {module_name}
Source file: {source_path}

{all_func_context}

Generate documentation with this EXACT structure:

# Module: `{module_name}`

> Brief module summary paragraph.

## Functions

For EACH function, generate:

### `function_name(args)`

**Description**: Clear explanation of what it does.

**Parameters**:
- `param_name` (*inferred_type*): description

**Returns**: What the function returns, with inferred type.

**Examples**:
```python
# Based on observed runtime behavior
result = function_name(input)  # → output
```

**Edge Cases / Notes**:
- Any observed crashes or special behavior.

---

RULES:
- Infer types from the observed runtime captures.
- Include ALL functions, even if no captures exist (describe based on source code analysis).
- Use the observed inputs/outputs as real examples in the documentation.
- Be concise but thorough.
- Return ONLY the Markdown documentation, no preamble.
"""

    # Run LLM call (handle running event loop)
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

    return response.messages[-1].text


@tool(approval_mode="never_require")
def generate_docs(
    legacy_file_path: Annotated[str, Field(
        description="Path to the legacy Python file, e.g. 'legacy_workspace/hangman.py'."
    )]
) -> str:
    """
    Generate comprehensive Markdown documentation for a legacy Python module.
    Reads the source code and observer runtime captures, then uses an LLM to
    produce professional documentation with descriptions, parameter tables,
    examples (from real observed I/O), and edge-case notes.

    Saves the documentation to generated_tests/docs_<module>.md.
    Call this ONCE per legacy file, AFTER the Critic has approved.
    """
    abs_path = os.path.abspath(legacy_file_path)
    if not os.path.exists(abs_path):
        return f"ERROR: File not found: {legacy_file_path}"

    module_name = os.path.basename(abs_path).replace(".py", "")

    # Extract function source code
    functions = _extract_functions_source(abs_path)
    if not functions:
        return f"No functions found in {legacy_file_path}."

    # Load observer captures
    records = _load_captures_for_module(module_name)

    print(f"\n[SYSTEM] Generating documentation for {module_name} "
          f"({len(functions)} functions, {len(records)} capture records)...\n")

    # Generate docs via LLM
    markdown = _generate_docs_via_llm(module_name, legacy_file_path, functions, records)

    # Save markdown
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc_file = os.path.join(OUTPUT_DIR, f"docs_{module_name}.md")
    with open(doc_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    # Auto-generate PDF from the markdown
    pdf_file = os.path.join(OUTPUT_DIR, f"docs_{module_name}.pdf")
    pdf_status = _convert_md_to_pdf(doc_file, pdf_file)

    func_names = [fn["name"] for fn in functions]
    return (
        f"Generated documentation for {module_name}.py — {len(functions)} functions documented.\n"
        f"Functions: {', '.join(func_names)}\n"
        f"Markdown: {doc_file}\n"
        f"PDF: {pdf_status}\n"
        f"Documentation includes descriptions, parameter descriptions, examples from runtime captures, and edge-case notes."
    )


def _convert_md_to_pdf(md_path: str, pdf_path: str) -> str:
    """Convert a markdown file to PDF with proper table rendering.

    Uses: markdown (with tables extension) → styled HTML → PDF via pymupdf.
    """
    try:
        import markdown
        import pymupdf
    except ImportError as e:
        return f"SKIPPED — missing dependency: {e}. Install with: pip install markdown pymupdf"

    # Read the markdown source
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert markdown → HTML with table support
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc"],
        extension_configs={
            "codehilite": {"css_class": "code", "guess_lang": False},
        },
    )

    # Professional CSS for clean PDF output
    css = """
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 11px;
        line-height: 1.6;
        color: #1a1a1a;
        max-width: 100%;
        padding: 20px 30px;
    }
    h1 {
        font-size: 22px;
        font-weight: 700;
        color: #0d1117;
        border-bottom: 2px solid #0969da;
        padding-bottom: 8px;
        margin-top: 24px;
        margin-bottom: 16px;
    }
    h2 {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
        border-bottom: 1px solid #d1d9e0;
        padding-bottom: 6px;
        margin-top: 20px;
        margin-bottom: 12px;
    }
    h3 {
        font-size: 14px;
        font-weight: 600;
        color: #24292f;
        margin-top: 16px;
        margin-bottom: 8px;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
        font-size: 10px;
    }
    th, td {
        border: 1px solid #d1d9e0;
        padding: 6px 10px;
        text-align: left;
    }
    th {
        background-color: #f0f3f6;
        font-weight: 600;
        color: #1a1a1a;
    }
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    code {
        background-color: #eff1f3;
        padding: 1px 5px;
        border-radius: 3px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 10px;
    }
    pre {
        background-color: #f6f8fa;
        border: 1px solid #d1d9e0;
        border-radius: 6px;
        padding: 12px;
        overflow-x: auto;
        font-size: 10px;
        line-height: 1.5;
    }
    pre code {
        background-color: transparent;
        padding: 0;
        font-size: 10px;
    }
    blockquote {
        border-left: 4px solid #0969da;
        margin: 12px 0;
        padding: 8px 16px;
        color: #57606a;
        background-color: #f6f8fa;
    }
    hr {
        border: none;
        border-top: 1px solid #d1d9e0;
        margin: 16px 0;
    }
    strong {
        font-weight: 600;
    }
    ul, ol {
        padding-left: 24px;
    }
    li {
        margin-bottom: 4px;
    }
    """

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    try:
        # Use weasyprint for robust HTML → PDF rendering
        from weasyprint import HTML
        HTML(string=full_html).write_pdf(pdf_path)

        size_kb = os.path.getsize(pdf_path) / 1024
        return f"{pdf_path} ({size_kb:.0f} KB)"

    except Exception as e:
        # Fallback: try mdpdf if weasyprint fails
        import subprocess
        import shutil

        mdpdf_path = shutil.which("mdpdf")
        if not mdpdf_path:
            venv_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".venv", "bin")
            candidate = os.path.join(venv_dir, "mdpdf")
            if os.path.exists(candidate):
                mdpdf_path = candidate

        if mdpdf_path:
            try:
                result = subprocess.run(
                    [mdpdf_path, "-o", pdf_path, md_path],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0 and os.path.exists(pdf_path):
                    size_kb = os.path.getsize(pdf_path) / 1024
                    return f"{pdf_path} ({size_kb:.0f} KB) [mdpdf fallback]"
            except Exception:
                pass

        return f"FAILED — {str(e)[:300]}"

