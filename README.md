# Phoenix — Multi-Agent Legacy Code Modernization System

Phoenix is a multi-agent AI system that **automatically modernizes undocumented legacy Python code**. It discovers legacy scripts, captures their runtime behavior, generates comprehensive regression test suites, and validates them inside isolated Docker sandboxes — all without any manual intervention.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Agent Pipeline](#agent-pipeline)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Docker](#2-install-docker)
  - [3. Set Up the Python Environment](#3-set-up-the-python-environment)
  - [4. Configure Environment Variables](#4-configure-environment-variables)
  - [5. Add Legacy Code](#5-add-legacy-code)
  - [6. Run Phoenix](#6-run-phoenix)
- [How It Works](#how-it-works)
- [Output](#output)
- [Configuration](#configuration)

---

## Overview

Legacy codebases often lack documentation, tests, and clear specifications. Phoenix tackles this by deploying a team of three AI agents that work collaboratively in a group-chat orchestration pattern:

1. **Observe** the legacy code's runtime behavior by executing it with AI-generated inputs
2. **Generate** PyTest regression test suites from the captured behavior
3. **Validate** the tests in air-gapped Docker sandboxes to ensure correctness

The result is a full set of verified, production-ready regression tests that codify the existing behavior of legacy code — enabling safe refactoring and modernization.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Orchestrator)                 │
│       Discovers files → Builds mission → Runs group chat    │
└────────────────────────────┬────────────────────────────────┘
                             │
              Round-Robin Group Chat Orchestration
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌───────────┐      ┌─────────────┐     ┌───────────┐
   │  Observer  │      │ QA Engineer │     │   Critic  │
   │  Agent     │─────▶│   Agent     │────▶│   Agent   │
   └─────┬─────┘      └──────┬──────┘     └─────┬─────┘
         │                    │                   │
         ▼                    ▼                   ▼
   ┌───────────┐      ┌─────────────┐     ┌───────────┐
   │  Runtime   │      │  Test Gen   │     │  Docker   │
   │  Capture   │      │  Engine     │     │  Sandbox  │
   │  (Docker)  │      │             │     │  Runner   │
   └───────────┘      └─────────────┘     └───────────┘
         │                    │                   │
         ▼                    ▼                   ▼
   observer_captures   test_<module>.py     Verification
       .json              files              Results
```

---

## Agent Pipeline

### 1. Observer Agent
- Scans each legacy Python file's AST to discover testable functions
- Uses an LLM to generate diverse, realistic test inputs (including edge cases)
- Executes functions inside a Docker sandbox with instrumentation wrappers
- Captures input/output pairs, exceptions, and crash data
- Persists all captures to `generated_tests/observer_captures.json`

### 2. QA Engineer Agent
- Reads the Observer's captured runtime data
- Generates complete PyTest regression test suites for each module
- Handles deterministic assertions, non-deterministic outputs (e.g., random selections), crash/exception testing, float comparisons, and large output truncation
- Saves test files to `generated_tests/test_<module_name>.py`

### 3. Critic Agent
- Runs all generated test suites inside isolated Docker containers
- Returns a pass/fail report with detailed logs
- If all tests pass → emits `PHOENIX_APPROVED` to end the pipeline
- If tests fail → provides feedback; the QA Engineer regenerates and the Critic re-verifies (iterative fix loop, up to 12 rounds)

---

## Project Structure

```
phoenix/
├── main.py                      # Orchestrator: file discovery, mission briefing, group chat
├── requirements.txt             # Python dependencies
├── Dockerfile.test-runner       # Docker image for running pytest in sandbox
├── .env                         # Azure OpenAI credentials (not committed)
│
├── agents/                      # AI Agent definitions
│   ├── client.py                # Shared Azure OpenAI client configuration
│   ├── observer.py              # Observer agent (runtime capture)
│   ├── qa_engineer.py           # QA Engineer agent (test generation)
│   └── critic.py                # Critic agent (test validation)
│
├── tools/                       # Agent tooling
│   ├── runtime_capture.py       # Runtime instrumentation & LLM input generation
│   ├── qa_tools.py              # PyTest code generation from captures
│   ├── critic_tools.py          # Docker-based test verification
│   └── docker_sandbox.py        # Generic Docker sandbox executor
│
├── schemas/                     # Pydantic data models
│   ├── test_spec.py             # Test specification & analyst output schemas
│   └── validation_report.py     # Critic report & validation issue schemas
│
├── legacy_workspace/            # ⬅ Place your legacy .py files here
│   ├── hangman.py               # Example: legacy hangman game
│   ├── legacy_billing.py        # Example: legacy billing engine
│   └── words.txt                # Data file used by hangman.py
│
└── generated_tests/             # Auto-generated output
    ├── observer_captures.json   # Runtime behavior captures
    ├── test_hangman.py           # Generated test suite for hangman
    └── test_legacy_billing.py   # Generated test suite for billing
```

---

## Prerequisites

Before running Phoenix, ensure you have the following installed:

| Requirement       | Version   | Purpose                                |
|--------------------|-----------|----------------------------------------|
| **Python**         | 3.10+     | Core runtime                           |
| **Docker**         | 20.10+    | Sandboxed code execution & test runner |
| **pip**            | 21+       | Python package management              |
| **Azure OpenAI**   | —         | LLM backend for agent reasoning        |

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/pprakash02/phoenix.git
cd phoenix
```

### 2. Install Docker

Docker is required for sandboxed code execution and test verification.

**Ubuntu:**

```bash
# Update package index
sudo apt-get update

# Install prerequisite packages
sudo apt-get install -y docker.io

# Add your user to the docker group (avoids needing sudo)
sudo usermod -aG docker $USER

# Apply group changes (or log out and back in)
newgrp docker

# Verify Docker is running
docker ps #should show a blank table
```

> **Note:** The Docker daemon must be running before you start Phoenix. On the first run, Phoenix will automatically pull the `python:3.10-slim` image and build the `phoenix-test-runner` image.

### 3. Set Up the Python Environment

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate        # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

**Dependencies installed:**

| Package            | Purpose                                      |
|--------------------|----------------------------------------------|
| `docker`           | Python SDK for Docker Engine API             |
| `agent-framework`  | Multi-agent orchestration framework          |
| `python-dotenv`    | Load environment variables from `.env` file  |
| `pydantic`         | Data validation and schema definition        |

### 4. Configure Environment Variables

Create a `.env` file in the project root with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-10-21
```

> **Important:** Never commit your `.env` file to version control. Add it to `.gitignore`.

### 5. Add Legacy Code

Place the legacy Python files you want to modernize into the `legacy_workspace/` directory:

```bash
cp /path/to/your/legacy_script.py legacy_workspace/
```

Phoenix will automatically discover all `.py` files in `legacy_workspace/` (excluding `__init__.py` and `__pycache__`).

**Requirements for legacy files:**
- Must be valid Python 3 syntax
- Functions using `input()` are automatically skipped (not testable in automated pipelines)
- Data files (`.txt`, `.csv`, etc.) can be placed alongside the scripts

### 6. Run Phoenix

```bash
python3 main.py
```

Phoenix will:
1. Discover all `.py` files in `legacy_workspace/`
2. Analyze each file's AST to identify testable functions
3. Deploy the Observer → QA Engineer → Critic pipeline
4. Output the full agent conversation and results to the terminal

---

## How It Works

### Step-by-Step Workflow

1. **File Discovery** — `main.py` scans `legacy_workspace/` for all Python files and extracts function signatures via AST parsing.

2. **Mission Briefing** — A dynamic prompt is generated containing all source code, function lists, and testability annotations.

3. **Observer Phase** — For each file, the Observer:
   - Extracts testable functions (skips those using `input()`)
   - Calls an LLM to generate 5–10 diverse inputs per function
   - Runs each function in a Docker sandbox with instrumentation
   - Saves input/output/crash data to `observer_captures.json`

4. **QA Engineer Phase** — Reads the capture data and generates:
   - Success tests with exact assertions
   - Crash tests using `pytest.raises`
   - Non-deterministic tests with membership assertions
   - Float-aware comparisons using `pytest.approx`

5. **Critic Phase** — Runs every `test_*.py` file in isolated Docker containers:
   - If all pass → `PHOENIX_APPROVED` → pipeline ends
   - If any fail → feedback sent to QA Engineer for regeneration

6. **Iterative Fix Loop** — If tests fail, the QA Engineer and Critic iterate (QA regenerates → Critic re-verifies) for up to 12 total rounds.

---

## Output

After a successful run, you'll find:

| File                                      | Description                              |
|-------------------------------------------|------------------------------------------|
| `generated_tests/observer_captures.json`  | Raw runtime behavior data                |
| `generated_tests/test_<module>.py`        | Generated PyTest regression test suites  |

You can run the generated tests manually:

```bash
cd legacy_workspace
pytest ../generated_tests/ -v
```

---

## Configuration

| Parameter                    | Location         | Default | Description                                |
|------------------------------|------------------|---------|--------------------------------------------|
| Max orchestration rounds     | `main.py`        | 12      | Maximum agent conversation rounds          |
| LLM temperature (agents)    | `agents/*.py`    | 0       | Controls agent response randomness         |
| LLM temperature (fuzzing)   | `runtime_capture.py` | 0.2 | Controls test input generation diversity   |
| Container memory limit      | `docker_sandbox.py`  | 256 MB | Memory limit for sandboxed execution       |
| Container CPU quota          | `docker_sandbox.py`  | 50%    | CPU limit for sandboxed execution          |
| Container timeout            | `critic_tools.py`    | 60s    | Max time for test execution per file       |

---
