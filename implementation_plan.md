# Per-File Sequential Processing with LLM-Based Test Generation

## Problem

The current pipeline processes **all files in a single GroupChat** with `max_rounds=15`. Each file requires at minimum 3 rounds (Observer → QA → Critic), plus fix iterations. With repos containing many files (e.g., 15+ Python files in the `testing` repo), the pipeline exhausts rounds before all files get tests generated — resulting in incomplete output.

Additionally, the current test generation in [qa_tools.py](file:///home/pprakash/phoenix/tools/qa_tools.py) is **template-based** (string formatting from capture records), not LLM-powered. This produces rigid, mechanical tests that miss edge cases a smarter approach would catch.

## Proposed Changes

### Strategy: Outer Loop + Per-File GroupChat

Instead of one big GroupChat for all files, the engine will:
1. **Loop over files sequentially** in [phoenix_engine.py](file:///home/pprakash/phoenix/services/phoenix_engine.py)
2. For each file, run a **dedicated per-file GroupChat** (Observer → QA → Critic) with its own round budget
3. After all files pass, run a **single Doc_Writer pass** (either as a separate GroupChat or direct tool call)

This keeps the GroupChat orchestration pattern intact while guaranteeing every file gets fully processed.

---

### Services

#### [MODIFY] [phoenix_engine.py](file:///home/pprakash/phoenix/services/phoenix_engine.py)

Major refactor of [run_pipeline()](file:///home/pprakash/phoenix/services/phoenix_engine.py#169-421):

- **Outer loop over files**: Iterate through `legacy_files` one at a time
- **Per-file GroupChat**: For each file, create a focused GroupChat with Observer, QA_Engineer, and Critic
  - Mission briefing scoped to a **single file** (source code + functions + context)
  - `max_rounds=10` per file (enough for observe + generate + verify + 2-3 fix cycles)
  - Selection function: Observer → QA_Engineer → Critic → (QA_Engineer ↔ Critic if fixes needed)
  - Termination: `PHOENIX_APPROVED` in Critic's message
- **Progress emission**: Update WebSocket progress per-file (e.g., "Processing file 3/8: Problem 3.py")
- **Doc generation**: After all files pass, run doc generation for each file (direct tool call, already has a fallback for this)
- **Dynamic max_rounds**: Each file gets adequate rounds — no global cap that starves later files
- Build a `build_single_file_briefing()` helper (similar to existing [build_mission_briefing](file:///home/pprakash/phoenix/services/phoenix_engine.py#95-167) but for one file)

---

### Tools

#### [MODIFY] [qa_tools.py](file:///home/pprakash/phoenix/tools/qa_tools.py)

Replace template-based [_generate_test_code()](file:///home/pprakash/phoenix/tools/qa_tools.py#46-169) with **LLM-powered test generation**:

- New function `_generate_test_code_via_llm()` that:
  1. Takes the source code, function signatures, and capture records
  2. Builds a detailed prompt asking the LLM to generate a pytest suite
  3. Includes the actual observed I/O as examples for the LLM to learn from
  4. Asks the LLM to add **edge cases, boundary conditions, and type-checking** tests beyond just the captured data
  5. Uses the same `client` from [agents/client.py](file:///home/pprakash/phoenix/agents/client.py) for the LLM call
- Keep the template-based generation as a **fallback** if LLM fails
- The [generate_tests](file:///home/pprakash/phoenix/tools/qa_tools.py#171-201) tool function stays the same (same signature, same tool decorator) — only the internal implementation changes

---

### Agents

#### [MODIFY] [qa_engineer.py](file:///home/pprakash/phoenix/agents/qa_engineer.py)

- Update instructions to reflect single-file processing (the agent now only needs to call [generate_tests](file:///home/pprakash/phoenix/tools/qa_tools.py#171-201) once per turn)

#### [MODIFY] [observer.py](file:///home/pprakash/phoenix/agents/observer.py)

- Update instructions to reflect single-file processing

#### [MODIFY] [critic.py](file:///home/pprakash/phoenix/agents/critic.py)

- Update instructions slightly — it still calls [verify_all_tests](file:///home/pprakash/phoenix/tools/critic_tools.py#79-129) but now in a single-file context

---

## User Review Required

> [!IMPORTANT]
> This changes the pipeline from a "process everything at once" model to a "process one file at a time" model.
> - Each file gets its own GroupChat lifecycle, ensuring completion before moving to the next.
> - The GroupChat orchestration pattern (Observer → QA → Critic) is preserved — just scoped per-file.
> - Total processing time may increase slightly due to sequential processing, but reliability is much higher.

> [!WARNING]
> The LLM-based test generation will make additional API calls (one per [generate_tests](file:///home/pprakash/phoenix/tools/qa_tools.py#171-201) invocation). This adds latency (~2-5s per file) but produces significantly better tests.

## Verification Plan

### Manual Verification
1. Run `python app.py` and start a project with the `pprakash02/testing` repo
2. Verify all Python files get test files generated (check `generated_tests/` directory)
3. Check that the generated tests use intelligent assertions (not just template patterns)
4. Verify WebSocket progress updates show per-file progress (e.g. "Processing file 3/8")
5. Confirm the download ZIP contains all test and doc files
