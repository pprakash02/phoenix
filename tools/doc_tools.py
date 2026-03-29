# tools/doc_tools.py
import os
import re
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


def _extract_cobol_structure(file_path: str) -> list[dict]:
    """Extract user-defined COBOL paragraphs, sections, and their source from a COBOL file.
    Filters out all standard COBOL reserved words and built-in constructs."""
    from services.phoenix_engine import COBOL_RESERVED_WORDS

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    structures = []
    lines = source.splitlines()
    seen = set()

    # Find user-defined sections
    for match in re.finditer(r'^\s{0,7}([A-Z0-9][A-Z0-9-]{0,29})\s+(SECTION)\s*\.', source, re.MULTILINE | re.IGNORECASE):
        name = match.group(1).upper()
        if name in COBOL_RESERVED_WORDS or name in seen:
            continue
        seen.add(name)
        start_line = source[:match.start()].count('\n')
        chunk = lines[start_line:min(start_line + 20, len(lines))]
        structures.append({
            "name": f"{match.group(1)} SECTION",
            "args": [],
            "source": "\n".join(chunk),
        })

    # Find user-defined paragraphs
    for match in re.finditer(r'^\s{7,11}([A-Z0-9][A-Z0-9-]{0,29})\s*\.\s*$', source, re.MULTILINE | re.IGNORECASE):
        name = match.group(1).upper()
        if name in COBOL_RESERVED_WORDS or name in seen:
            continue
        seen.add(name)
        start_line = source[:match.start()].count('\n')
        chunk = lines[start_line:min(start_line + 15, len(lines))]
        structures.append({
            "name": match.group(1),
            "args": [],
            "source": "\n".join(chunk),
        })

    # If no user-defined structures found, treat the whole program as one block
    if not structures:
        structures.append({
            "name": "MAIN-PROGRAM",
            "args": [],
            "source": source[:3000] if len(source) > 3000 else source,
        })

    return structures


def _is_cobol_file(file_path: str) -> bool:
    """Check if a file is a COBOL source file by extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ('.cob', '.cbl', '.cpy')


def _is_c_file(file_path: str) -> bool:
    """Check if a file is a C source file by extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ('.c', '.h')


def _extract_c_structure(file_path: str) -> list[dict]:
    """Extract C functions and their source for documentation."""
    from services.phoenix_engine import extract_c_functions
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()

    functions = extract_c_functions(file_path)
    source_lines = source.splitlines()

    # Try to extract each function's source using brace matching
    result = []
    for fn in functions:
        # Find the function definition line
        func_source = ""
        pattern = re.compile(rf'\b{re.escape(fn["name"])}\s*\(')
        for i, line in enumerate(source_lines):
            if pattern.search(line):
                # Found it — extract until closing brace
                brace_count = 0
                started = False
                end_line = i
                for j in range(i, min(i + 200, len(source_lines))):
                    brace_count += source_lines[j].count('{')
                    if brace_count > 0:
                        started = True
                    brace_count -= source_lines[j].count('}')
                    if started and brace_count <= 0:
                        end_line = j + 1
                        break
                func_source = "\n".join(source_lines[i:end_line])
                break

        if not func_source:
            func_source = f"/* Function {fn['name']} — source not extracted */"

        result.append({
            "name": fn["name"],
            "args": fn["args"],
            "return_type": fn.get("return_type", "void"),
            "source": func_source,
        })

    return result


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


async def _generate_docs_via_llm(module_name: str, source_path: str,
                           functions: list[dict], records: list[dict],
                           is_cobol: bool = False, is_c: bool = False) -> str:
    """Use the LLM to generate comprehensive markdown documentation."""
    if is_cobol:
        return await _generate_cobol_docs_via_llm(module_name, source_path, functions)
    if is_c:
        return await _generate_c_docs_via_llm(module_name, source_path, functions)

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
- Do NOT use markdown tables. Use bullet lists instead for parameters and return values.
"""

    response = await client.get_response(
        messages=[Message("user", [prompt])],
        default_options={"temperature": 0.1}
    )

    return response.messages[-1].text


async def _generate_cobol_docs_via_llm(module_name: str, source_path: str,
                                       structures: list[dict]) -> str:
    """Use the LLM to generate COBOL-specific markdown documentation."""
    struct_sections = []
    for s in structures:
        struct_sections.append(f"""
### {s['name']}

Source code:
```cobol
{s['source']}
```
""")

    all_struct_context = "\n".join(struct_sections)

    prompt = f"""You are a COBOL technical documentation writer. Generate comprehensive, professional Markdown documentation for the following COBOL program.

Program name: {module_name}
Source file: {source_path}

User-defined paragraphs/sections found:
{all_struct_context}

Generate documentation with this EXACT structure:

# COBOL Program: `{module_name}`

> Brief program summary paragraph describing its purpose.

## Program Structure

Describe the overall structure: which DIVISIONS are present, the program flow.

## Data Division

Document the key data items defined in WORKING-STORAGE SECTION, LINKAGE SECTION, etc.
For each significant variable group or record structure:
- Variable name, PIC clause, initial VALUE
- Purpose/usage in the program

## Procedure Division

For EACH user-defined paragraph or section, generate:

### `PARAGRAPH-NAME`

**Purpose**: Clear explanation of what this paragraph does.

**Data Items Used**: List the key variables read/modified.

**Control Flow**: Describe any PERFORM, GO TO, CALL, or conditional logic.

**Business Logic**: Describe the business rules implemented.

---

RULES:
- Document ONLY user-defined paragraphs and sections, NOT built-in COBOL verbs.
- Focus on the business logic and data transformations.
- Describe the PERFORM hierarchy (which paragraphs call which).
- Note any COPY statements, CALL to external programs, or file I/O operations.
- Be concise but thorough.
- Return ONLY the Markdown documentation, no preamble.
- Do NOT use markdown tables. Use bullet lists instead.
"""

    response = await client.get_response(
        messages=[Message("user", [prompt])],
        default_options={"temperature": 0.1}
    )

    return response.messages[-1].text


async def _generate_c_docs_via_llm(module_name: str, source_path: str,
                                   functions: list[dict]) -> str:
    """Use the LLM to generate C-specific markdown documentation."""
    func_sections = []
    for fn in functions:
        args = ", ".join(fn.get("args", []))
        ret = fn.get("return_type", "void")
        func_sections.append(f"""
### `{ret} {fn['name']}({args})`

Source code:
```c
{fn['source']}
```
""")

    all_func_context = "\n".join(func_sections)

    prompt = f"""You are a C technical documentation writer. Generate comprehensive, professional Markdown documentation for the following C module.

Module name: {module_name}
Source file: {source_path}

Functions found:
{all_func_context}

Generate documentation with this EXACT structure:

# C Module: `{module_name}`

> Brief module summary paragraph describing its purpose.

## Overview

Describe the overall purpose, key data structures, and #include dependencies.

## Functions

For EACH function, generate:

### `return_type function_name(params)`

**Description**: Clear explanation of what the function does.

**Parameters**:
- `param_name` (*type*): description

**Returns**: What the function returns, with type.

**Algorithm / Logic**: Describe the key logic steps.

**Edge Cases / Notes**:
- Any known limitations or special behaviors.

---

RULES:
- Document ALL functions found in the source.
- Be concise but thorough about the algorithm and business logic.
- Describe any global variables or structs used.
- Note any pointer parameters and whether they are input, output, or both.
- Return ONLY the Markdown documentation, no preamble.
- Do NOT use markdown tables. Use bullet lists instead for parameters and return values.
"""

    response = await client.get_response(
        messages=[Message("user", [prompt])],
        default_options={"temperature": 0.1}
    )

    return response.messages[-1].text


@tool(approval_mode="never_require")
async def generate_docs(
    legacy_file_path: Annotated[str, Field(
        description="Path to the legacy source file, e.g. 'legacy_workspace/hangman.py' or 'legacy_workspace/billing.cob'."
    )]
) -> str:
    """
    Generate comprehensive Markdown documentation for a legacy module (Python or COBOL).
    Reads the source code and observer runtime captures, then uses an LLM to
    produce professional documentation with descriptions, parameter tables,
    examples (from real observed I/O), and edge-case notes.

    Saves the documentation to generated_tests/docs_<module>.md.
    Call this ONCE per legacy file, AFTER the Critic has approved.
    """
    abs_path = os.path.abspath(legacy_file_path)
    if not os.path.exists(abs_path):
        return f"ERROR: File not found: {legacy_file_path}"

    # Determine language
    is_cobol = _is_cobol_file(abs_path)
    is_c = _is_c_file(abs_path)
    ext = os.path.splitext(os.path.basename(abs_path))[1]
    module_name = os.path.basename(abs_path).replace(ext, "")

    # Extract structure based on language
    if is_cobol:
        functions = _extract_cobol_structure(abs_path)
    elif is_c:
        functions = _extract_c_structure(abs_path)
    else:
        functions = _extract_functions_source(abs_path)

    if not functions:
        return f"No functions/structures found in {legacy_file_path}."

    # Load observer captures (may be empty for COBOL/C)
    records = _load_captures_for_module(module_name)

    lang_label = "COBOL" if is_cobol else ("C" if is_c else "Python")
    item_label = "paragraphs" if is_cobol else "functions"
    print(f"\n[SYSTEM] Generating {lang_label} documentation for {module_name} "
          f"({len(functions)} {item_label}, {len(records)} capture records)...\n")

    # Generate docs via LLM
    markdown = await _generate_docs_via_llm(module_name, legacy_file_path, functions, records,
                                           is_cobol=is_cobol, is_c=is_c)

    # Save markdown
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc_file = os.path.join(OUTPUT_DIR, f"docs_{module_name}.md")
    with open(doc_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    # Auto-generate PDF from the markdown
    pdf_file = os.path.join(OUTPUT_DIR, f"docs_{module_name}.pdf")
    pdf_status = _convert_md_to_pdf(doc_file, pdf_file)

    item_names = [fn["name"] for fn in functions]
    return (
        f"Generated documentation for {module_name}{ext} — {len(functions)} {item_label} documented.\n"
        f"{item_label.title()}: {', '.join(item_names)}\n"
        f"Markdown: {doc_file}\n"
        f"PDF: {pdf_status}\n"
        f"Documentation includes descriptions, parameter descriptions, examples, and edge-case notes."
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

