# Phoenix — Multi-Agent Legacy Code Modernization System

Phoenix is a multi-agent AI platform that **automatically modernizes undocumented legacy code**. Point it at any GitHub repository containing Python, COBOL, or C source files — Phoenix will analyze the code, capture runtime behavior, generate regression test suites, validate them in Docker sandboxes, and produce comprehensive documentation. All orchestrated by a team of AI agents, with a real-time web dashboard and human-in-the-loop feedback.

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture](#architecture)
- [Agent Pipeline](#agent-pipeline)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Docker](#2-install-docker)
  - [3. Set Up the Python Environment](#3-set-up-the-python-environment)
  - [4. Install the Web Frontend](#4-install-the-web-frontend)
  - [5. Configure Environment Variables](#5-configure-environment-variables)
  - [6. Run Phoenix](#6-run-phoenix)
- [Usage Modes](#usage-modes)
  - [Web Application (Recommended)](#web-application-recommended)
  - [CLI Mode](#cli-mode)
- [How It Works](#how-it-works)
- [API Reference](#api-reference)
- [Output](#output)
- [Configuration](#configuration)
- [Tech Stack](#tech-stack)

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Language Support** | Analyzes and generates tests for **Python**, **COBOL** (.cob, .cbl, .cpy), and **C** (.c, .h) |
| **4 AI Agents** | Observer, QA Engineer, Critic, and Doc Writer collaborate via group-chat orchestration |
| **Runtime Behavior Capture** | Executes Python functions in Docker sandboxes with LLM-generated inputs |
| **Automated Test Generation** | Produces PyTest suites (Python), test specs (COBOL), and assert.h test files (C) |
| **Docker Sandbox Validation** | All tests are verified in isolated containers before approval |
| **Auto-Generated Documentation** | Comprehensive Markdown docs for every processed source file |
| **Web Dashboard** | Real-time React UI with live progress tracking via WebSocket |
| **GitHub PR Integration** | One-click creation of pull requests with generated tests and docs |
| **Human-in-the-Loop** | Provide per-file context, approve/reject results, and trigger re-generation |
| **Azure Cloud Services** | Cosmos DB for sessions, Blob Storage for artifacts, Azure OpenAI for LLM |
| **Session & History** | Track all runs, revisit results, and download artifact bundles |

---

## Architecture

```
                          ┌──────────────────────────────┐
                          │     React + Vite Frontend    │
                          │   (Real-time WebSocket UI)   │
                          └──────────────┬───────────────┘
                                         │ HTTP / WebSocket
                          ┌──────────────▼───────────────┐
                          │   Flask + SocketIO Backend   │
                          │        (app.py)              │
                          └──────────────┬───────────────┘
                                         │
                     ┌───────────────────▼───────────────────────┐
                     │        Phoenix Engine (Orchestrator)       │
                     │    Per-file GroupChat: Observer → QA →     │
                     │    Critic (→ fix loop) → Doc_Writer       │
                     └───────┬───────┬───────┬───────┬──────────┘
                             │       │       │       │
                  ┌──────────▼┐  ┌───▼─────┐ ┌▼──────┐ ┌▼─────────┐
                  │  Observer  │  │   QA    │ │Critic │ │Doc Writer│
                  │  Agent     │  │Engineer │ │ Agent │ │  Agent   │
                  └─────┬──────┘  └──┬──────┘ └──┬────┘ └──┬───────┘
                        │            │            │         │
                  ┌─────▼──────┐ ┌───▼──────┐ ┌──▼─────┐ ┌─▼──────┐
                  │  Runtime   │ │  Test    │ │Docker  │ │  Doc   │
                  │  Capture   │ │  Gen    │ │Sandbox │ │  Gen   │
                  │  (Docker)  │ │  Engine  │ │Runner  │ │ Engine │
                  └────────────┘ └──────────┘ └────────┘ └────────┘
                        │            │            │         │
                        ▼            ▼            ▼         ▼
                  ┌──────────────────────────────────────────────┐
                  │           Azure Cloud Services               │
                  │  Cosmos DB │ Blob Storage │ Azure OpenAI     │
                  └──────────────────────────────────────────────┘
```

---

## Agent Pipeline

### 1. Observer Agent
- Scans each legacy file's structure to discover testable functions
- **Python:** Uses an LLM to generate diverse, realistic test inputs (including edge cases), then executes functions inside a Docker sandbox with instrumentation wrappers. Captures input/output pairs, exceptions, and crash data.
- **COBOL / C:** Performs static code analysis (no runtime capture) — summarizes purpose, logic flow, data structures, and dependencies.
- Persists all captures to `observer_captures.json`

### 2. QA Engineer Agent
- Reads the Observer's captured runtime data (Python) or source analysis (COBOL/C)
- Generates language-appropriate test suites:
  - **Python:** PyTest suites with deterministic assertions, non-deterministic membership checks, crash/exception testing, `pytest.approx` for floats
  - **COBOL:** Comprehensive test specification documents from source analysis
  - **C:** Test files using `assert.h` with a `main()` entry point
- Saves test files to `generated_tests/`

### 3. Critic Agent
- **Python:** Runs all generated test suites inside isolated Docker containers and returns a pass/fail report with detailed logs
- **COBOL / C:** Reviews the generated test specification/test file for completeness
- If all tests pass → emits `PHOENIX_APPROVED` to advance the pipeline
- If tests fail → provides feedback; the QA Engineer regenerates and the Critic re-verifies (iterative fix loop)

### 4. Doc Writer Agent
- Activated only after the Critic approves the test suite
- Generates comprehensive Markdown documentation for each processed source file
- Reads both the source code and observed runtime behavior to produce rich docs
- Supports Python, COBOL, and C files
- Signals `PHOENIX_DOCS_COMPLETE` to end the pipeline for that file

---

## Project Structure

```
phoenix/
├── app.py                         # Web backend: Flask + SocketIO server
├── main.py                        # CLI orchestrator (standalone mode)
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Multi-stage production build (frontend + backend)
├── Dockerfile.test-runner         # Docker image for running pytest in sandbox
├── .env                           # Environment variables (not committed)
│
├── agents/                        # AI Agent definitions
│   ├── client.py                  # Shared Azure OpenAI client configuration
│   ├── observer.py                # Observer agent (runtime capture / static analysis)
│   ├── qa_engineer.py             # QA Engineer agent (test generation)
│   ├── critic.py                  # Critic agent (test validation)
│   └── doc_writer.py              # Doc Writer agent (documentation generation)
│
├── tools/                         # Agent tooling
│   ├── runtime_capture.py         # Runtime instrumentation & LLM input generation
│   ├── qa_tools.py                # Test generation for Python, COBOL, and C
│   ├── critic_tools.py            # Docker-based test verification
│   ├── doc_tools.py               # Documentation generation engine
│   └── docker_sandbox.py          # Generic Docker sandbox executor
│
├── services/                      # Backend services
│   ├── phoenix_engine.py          # Core orchestration engine (per-file GroupChat)
│   ├── llm_service.py             # Dynamic LLM client factory (multi-model support)
│   ├── github_service.py          # GitHub cloning, file analysis, PR creation
│   ├── azure_db_service.py        # Azure Cosmos DB session/history management
│   ├── azure_blob_service.py      # Azure Blob Storage for artifacts
│   └── blob_service.py            # Blob storage abstraction layer
│
├── schemas/                       # Pydantic data models
│   ├── test_spec.py               # Test specification & analyst output schemas
│   ├── validation_report.py       # Critic report & validation issue schemas
│   └── doc_spec.py                # Documentation specification schemas
│
├── orchestration/                 # Orchestration utilities
│   └── __init__.py
│
├── web/                           # React frontend (Vite)
│   ├── package.json               # Frontend dependencies (React 19, Vite 6)
│   ├── vite.config.js             # Vite configuration
│   ├── index.html                 # HTML entry point
│   ├── src/                       # React source code
│   │   ├── App.jsx                # Main app with routing
│   │   ├── components/            # Reusable UI components
│   │   ├── pages/                 # Page-level components
│   │   ├── contexts/              # React context providers
│   │   ├── hooks/                 # Custom React hooks
│   │   └── services/              # API client services
│   └── dist/                      # Built frontend (served by Flask)
│
├── assets/                        # Static assets (design mockups, etc.)
│
├── legacy_workspace/              # ⬅ Place legacy files here (CLI mode only)
│
└── generated_tests/               # Auto-generated output
    ├── observer_captures.json     # Runtime behavior captures
    ├── test_<module>.py           # Generated Python test suites
    ├── test_<module>.c            # Generated C test files
    └── docs_<module>.md           # Generated documentation
```

---

## Prerequisites

| Requirement           | Version   | Purpose                                       |
|-----------------------|-----------|-----------------------------------------------|
| **Python**            | 3.10+     | Core backend runtime                          |
| **Node.js**           | 18+       | Frontend build (React + Vite)                 |
| **Docker**            | 20.10+    | Sandboxed code execution & test runner        |
| **pip**               | 21+       | Python package management                     |
| **Azure OpenAI**      | —         | LLM backend for agent reasoning               |
| **Azure Cosmos DB**   | —         | Session and history persistence (web mode)     |
| **Azure Blob Storage**| —         | Artifact storage (web mode)                   |
| **GitHub Token**      | —         | For PR creation (optional)                     |

> **Note:** Azure Cosmos DB and Blob Storage are required only for the web application mode. CLI mode works with just Azure OpenAI and Docker.

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

# Install Docker
sudo apt-get install -y docker.io

# Add your user to the docker group (avoids needing sudo)
sudo usermod -aG docker $USER

# Apply group changes (or log out and back in)
newgrp docker

# Verify Docker is running
docker ps  # should show a blank table
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

**Key dependencies installed:**

| Package               | Purpose                                      |
|-----------------------|----------------------------------------------|
| `agent-framework`     | Multi-agent orchestration framework          |
| `docker`              | Python SDK for Docker Engine API             |
| `flask`               | Web backend server                           |
| `flask-socketio`      | Real-time WebSocket communication            |
| `flask-cors`          | Cross-origin resource sharing                |
| `eventlet`            | Async networking for SocketIO                |
| `pygithub`            | GitHub API integration for PR creation       |
| `azure-cosmos`        | Azure Cosmos DB SDK                          |
| `azure-storage-blob`  | Azure Blob Storage SDK                       |
| `gitpython`           | Git operations (repo cloning)                |
| `pydantic`            | Data validation and schema definition        |
| `python-dotenv`       | Load environment variables from `.env`       |
| `gunicorn`            | Production WSGI server                       |
| `weasyprint`          | PDF generation for documentation             |
| `pymupdf`             | PDF processing                               |
| `markdown`            | Markdown rendering                           |

### 4. Install the Web Frontend

```bash
cd web
npm install
npm run build
cd ..
```

This builds the React frontend into `web/dist/`, which Flask serves automatically.

**For frontend development with hot-reload:**

```bash
cd web
npm run dev       # Starts Vite dev server on port 5173
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# ─── Azure OpenAI (Required) ───────────────────────────────────
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-10-21

# ─── Azure Cosmos DB (Required for web mode) ───────────────────
AZURE_COSMOS_ENDPOINT=https://<your-cosmos>.documents.azure.com
AZURE_COSMOS_KEY=<your-cosmos-key>
AZURE_COSMOS_DB_NAME=<your-db-name>

# ─── Azure Blob Storage (Required for web mode) ────────────────
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>

# ─── Azure App Service (Optional — for deployed CORS) ──────────
AZURE_APP_URL=https://<your-app>.azurewebsites.net
```

> **Important:** Never commit your `.env` file to version control.

### 6. Run Phoenix

**Web application (recommended):**

```bash
python3 app.py
```

The server starts at `http://localhost:5000`. Open this URL in your browser to access the Phoenix dashboard.

**CLI mode (standalone, no web UI):**

```bash
python3 main.py
```

Place legacy files in `legacy_workspace/` before running CLI mode.

---

## Usage Modes

### Web Application (Recommended)

1. **Start the server** — Run `python3 app.py` and open `http://localhost:5000`
2. **Enter a GitHub repo URL** — Phoenix clones the repo and analyzes all source files
3. **Select an LLM model** — Choose from configured Azure OpenAI deployments
4. **Provide context** — Add optional per-file instructions (e.g., "Focus on edge cases for negative numbers")
5. **Monitor progress** — Watch the real-time agent pipeline via WebSocket updates
6. **Review results** — View generated tests and documentation in the dashboard
7. **Approve or reject** — Approve results or provide feedback to trigger re-generation
8. **Export** — Download artifacts as a ZIP or create a GitHub PR directly

### CLI Mode

1. Place legacy Python files in `legacy_workspace/`
2. Run `python3 main.py`
3. Provide optional per-file instructions when prompted (human-in-the-loop)
4. Phoenix processes each file sequentially through the full agent pipeline
5. Results are saved to `generated_tests/`

---

## How It Works

### End-to-End Workflow

1. **Repository Ingestion** — The web app clones a GitHub repository (or CLI mode reads from `legacy_workspace/`). Source files are uploaded to Azure Blob Storage for persistence.

2. **File Discovery & Analysis** — Discovers all Python, COBOL, and C files. Extracts function signatures (Python via AST, COBOL via regex paragraph detection, C via regex function matching). Filters out untestable functions (e.g., those using `input()` in Python, `main()` in C).

3. **Per-File Agent Pipeline** — Each source file gets its own GroupChat session with all four agents:

   - **Observer Phase** — For Python: generates 5–10 diverse inputs per function via LLM, executes in Docker sandbox, captures I/O pairs, exceptions, and crash data. For COBOL/C: performs static source analysis.

   - **QA Engineer Phase** — Generates language-appropriate test suites from captured data. Handles deterministic assertions, non-deterministic outputs, crash testing, float comparisons, and large output truncation.

   - **Critic Phase** — Runs tests in isolated Docker containers (Python) or reviews test completeness (COBOL/C). If tests fail, feeds back to QA Engineer for regeneration.

   - **Iterative Fix Loop** — QA Engineer and Critic iterate until all tests pass or max rounds (10 for Python/COBOL, 5 for C) are reached.

   - **Doc Writer Phase** — After Critic approval, generates comprehensive Markdown documentation from both source code and runtime observations.

4. **Artifact Storage** — All generated tests, docs, and conversation logs are uploaded to Azure Blob Storage. Session metadata is stored in Cosmos DB.

5. **Results Delivery** — Results are emitted via WebSocket to the frontend in real-time. Users can download ZIP bundles or create GitHub PRs.

### Rate Limit Handling

Phoenix includes automatic retry logic for Azure OpenAI rate limits — backs off for 65–130 seconds before retrying, up to 2 attempts per file.

---

## API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check — returns server status and version |
| `GET` | `/api/models` | List available LLM models with configuration status |
| `POST` | `/api/start-project` | Start a new project (clone repo, analyze files) |
| `POST` | `/api/submit-context` | Submit per-file context and start the agent pipeline |
| `GET` | `/api/session/<id>` | Get session status and data |
| `GET` | `/api/results/<id>` | Get pipeline results (tests, docs, conversation) |
| `POST` | `/api/approve` | Approve generated tests |
| `POST` | `/api/reject` | Reject with feedback — triggers re-generation |
| `GET` | `/api/download/<id>` | Download generated artifacts as ZIP |
| `POST` | `/api/create-pr` | Create a GitHub PR with generated tests and docs |
| `GET` | `/api/history` | Get run history for the current user |
| `GET` | `/api/history/<id>` | Get details of a specific history entry |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client → Server | Client connects to WebSocket |
| `join_session` | Client → Server | Client subscribes to a session's updates |
| `connected` | Server → Client | Connection acknowledgment |
| `agent_progress` | Server → Client | Real-time pipeline progress (stage, agent, message, %) |
| `pipeline_complete` | Server → Client | Pipeline finished — includes all results |
| `pipeline_error` | Server → Client | Pipeline error notification |

---

## Output

After a successful run, Phoenix generates:

| File Pattern | Description |
|--------------|-------------|
| `test_<module>.py` | PyTest regression test suites (Python files) |
| `test_<module>.c` | C test files using assert.h (C files) |
| `docs_<module>.md` | Comprehensive Markdown documentation |
| `observer_captures.json` | Raw runtime behavior data (Python files) |
| `conversation_log.json` | Full agent conversation transcript |

**Run generated Python tests manually:**

```bash
cd legacy_workspace
pytest ../generated_tests/ -v
```

---

## Configuration

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| Max orchestration rounds (Python/COBOL) | `phoenix_engine.py` | 10 | Maximum agent conversation rounds per file |
| Max orchestration rounds (C) | `phoenix_engine.py` | 5 | Streamlined rounds for C files |
| Max orchestration rounds (CLI) | `main.py` | 10 | Maximum rounds in CLI mode |
| LLM temperature (agents) | `agents/*.py` | 0 | Controls agent response randomness |
| LLM temperature (fuzzing) | `runtime_capture.py` | 0.2 | Controls test input generation diversity |
| Container memory limit | `docker_sandbox.py` | 256 MB | Memory limit for sandboxed execution |
| Container CPU quota | `docker_sandbox.py` | 50% | CPU limit for sandboxed execution |
| Container timeout | `critic_tools.py` | 60s | Max time for test execution per file |
| Rate limit retry delay | `phoenix_engine.py` | 65s × attempt | Backoff delay for Azure OpenAI rate limits |
| Max rate limit retries | `phoenix_engine.py` | 2 | Maximum retry attempts per file |
| Web server port | `app.py` | 5000 | Flask development server port |
| Production port | `Dockerfile` | 80 | Gunicorn production server port |

---

## Tech Stack

### Backend
- **Python 3.10+** — Core runtime
- **Flask + Flask-SocketIO** — Web server with real-time WebSocket support
- **Gunicorn + Eventlet** — Production async workers
- **Agent Framework** — Multi-agent orchestration (GroupChat pattern)
- **Docker SDK** — Sandboxed code execution
- **Pydantic** — Data validation and schema enforcement

### Frontend
- **React 19** — UI framework
- **Vite 6** — Build tool and dev server
- **React Router DOM** — Client-side routing
- **Socket.IO Client** — Real-time server communication
- **React Markdown** — Rendered documentation display
- **React Syntax Highlighter** — Code block highlighting

### Cloud Services
- **Azure OpenAI** — LLM backend (GPT-4o and configurable models)
- **Azure Cosmos DB** — Session metadata and run history persistence
- **Azure Blob Storage** — Artifact storage (tests, docs, conversation logs)
- **GitHub API (PyGitHub)** — Repository cloning and PR creation

### DevOps
- **Docker** — Multi-stage production build (Node.js frontend → Python backend)
- **Docker-in-Docker** — Sandboxed test execution via `phoenix-test-runner` image

---

## Docker Deployment

Build and run the production Docker image:

```bash
# Build the multi-stage image
docker build -t phoenix:latest .

# Run the container
docker run -p 80:80 \
  -e AZURE_OPENAI_ENDPOINT=<endpoint> \
  -e AZURE_OPENAI_API_KEY=<key> \
  -e AZURE_OPENAI_DEPLOYMENT_NAME=<deployment> \
  -e AZURE_OPENAI_API_VERSION=2024-10-21 \
  -e AZURE_COSMOS_ENDPOINT=<cosmos-endpoint> \
  -e AZURE_COSMOS_KEY=<cosmos-key> \
  -e AZURE_COSMOS_DB_NAME=<db-name> \
  -e AZURE_STORAGE_CONNECTION_STRING=<blob-conn-string> \
  -v /var/run/docker.sock:/var/run/docker.sock \
  phoenix:latest
```

> **Note:** The Docker socket mount (`-v /var/run/docker.sock:...`) is required for Phoenix to spin up sandboxed test-runner containers.

---