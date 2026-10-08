# Topic 13 — Error Recovery Assessment

## Project Overview
This project implements and tests a deterministic error-recovery system for an AI-agent-style workflow. Failures are classified into transient, not-found, and fatal errors and handled with appropriate recovery strategies.

## Assessment Tasks

### Task 1 — Error Classes
Implemented `TransientError`, `NotFoundError`, and `FatalError` as dedicated exception classes.

### Task 2 — Recovery Mechanism
`recover()` tries the primary lookup, uses the backup for `TransientError`, checks the cache for `NotFoundError`, returns `None` when no cached value exists, and does not swallow `FatalError`.

Results contain `value`, `source`, and `recovered_from`.

### Task 3 — Fatal Error Propagation
Fatal errors are logged and re-raised. They are never converted into `None`, cache values, or backup results.

### Task 4 — Recovery Path Testing
Pytest coverage verifies primary success, backup recovery, cache recovery, no-value behavior, fatal propagation, traceability, and input validation.

### Task 5 — Safe Logging
Python's standard `logging` module records recovery details. A safe logging helper redacts common secret formats such as API keys, authorization values, tokens, passwords, and secrets. Tests verify that a fake API key is not exposed.

## Recovery Flow

```text
Primary success -> primary result
TransientError -> backup result
NotFoundError -> cache result or None
FatalError -> propagate
```

## Project Structure

```text
Error_Recovery_Assessment/
+-- src/error_recovery.py
+-- tests/test_error_recovery.py
+-- evidence/generate_evidence.py
+-- evidence/task1_error_classes.json
+-- evidence/task2_recovery.json
+-- evidence/task3_fatal_propagation.json
+-- evidence/task4_recovery_paths.json
+-- evidence/task5_safe_logging.json
+-- demo.py
+-- requirements.txt
+-- .gitignore
+-- README.md
```

## Running the Project

```cmd
E:
cd E:\Tayana_Projects\Agent_Planning_and_Reasoning\Error_Recovery_Assessment
.venv\Scripts\activate
python -m pip install -r requirements.txt
python demo.py
python -m pytest -q
python evidence\generate_evidence.py
```

## Verification Results

Final automated regression:

```text
36 passed in 0.16s
```

The live demonstration verified:
1. Primary success.
2. Transient failure to backup.
3. Not-found failure to cache.
4. Not-found failure with no available value.
5. Fatal error propagation.

All five evidence JSON files were generated successfully.

## Evidence

- `task1_error_classes.json`
- `task2_recovery.json`
- `task3_fatal_propagation.json`
- `task4_recovery_paths.json`
- `task5_safe_logging.json`

## GitHub Safety

No real API keys or external credentials are required. `.gitignore` excludes virtual environments, Python cache files, pytest cache, and `.env` files.

## Reflection

This activity helped me understand that error recovery in an agent workflow is not simply about catching exceptions and returning a default value. Different failures require different decisions. A transient failure may be recoverable through a backup tool, while a not-found condition may be handled using cached information. A fatal failure must instead stop the workflow and remain visible to the caller.

Implementing the `recover()` function made this distinction practical. I had to think about the order of recovery decisions, the structure of returned results, and how to ensure that a fatal error could never accidentally fall through into a fallback path. Testing each recovery route also showed why explicit behavior is important in agent systems: successful execution alone does not prove that failure handling is correct.

The logging task added another important lesson. Recovery behavior needs to be observable so that developers can understand which path was taken, but logs must not become a source of secret leakage. The redaction helper and tests for fake API keys demonstrated how traceability and security can be designed together.

Overall, this project improved my understanding of robust agent workflows, exception classification, fallback strategies, testing, and safe operational logging. The final implementation is deterministic, fully tested, and structured so that each recovery decision can be verified independently.
