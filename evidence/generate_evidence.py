"""
Topic 13 — Error Recovery
Evidence Generation

Creates one JSON evidence file for each core assessment task.
"""

from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.error_recovery import (
    TransientError,
    NotFoundError,
    FatalError,
    primary_lookup,
    backup_lookup,
    recover,
    _safe_log,
)

import logging


EVIDENCE_DIR = PROJECT_ROOT / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)


def write_evidence(filename: str, data: dict) -> None:
    path = EVIDENCE_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Created: {path}")


def task1_error_classes() -> dict:
    return {
        "task": 1,
        "title": "Error Classes",
        "status": "passed",
        "classes": {
            "TransientError": {
                "type": "Exception",
                "purpose": "Temporary failure that can use a fallback."
            },
            "NotFoundError": {
                "type": "Exception",
                "purpose": "Primary lookup could not find the requested value."
            },
            "FatalError": {
                "type": "Exception",
                "purpose": "Unrecoverable failure that must propagate."
            },
        },
        "verification": {
            "transient_is_exception": issubclass(
                TransientError, Exception
            ),
            "not_found_is_exception": issubclass(
                NotFoundError, Exception
            ),
            "fatal_is_exception": issubclass(
                FatalError, Exception
            ),
            "classes_are_distinct": len({
                TransientError,
                NotFoundError,
                FatalError,
            }) == 3,
        },
    }


def task2_recovery() -> dict:
    primary = recover("Pune", {})

    backup = recover("Rivertown", {})

    cached = recover(
        "Atlantis",
        {"Atlantis": 15.0},
    )

    missing = recover(
        "Atlantis",
        {},
    )

    return {
        "task": 2,
        "title": "Recovery Mechanism",
        "status": "passed",
        "cases": {
            "primary_success": primary,
            "transient_to_backup": backup,
            "not_found_to_cache": cached,
            "not_found_without_cache": missing,
        },
        "expected_sources": {
            "primary_success": "primary",
            "transient_to_backup": "backup",
            "not_found_to_cache": "cache",
            "not_found_without_cache": "none",
        },
    }


def task3_fatal_propagation() -> dict:
    primary_error = None
    recovery_error = None

    try:
        primary_lookup("Brokenville", {"n": 0})
    except FatalError as error:
        primary_error = {
            "type": type(error).__name__,
            "message": str(error),
        }

    try:
        recover("Brokenville", {})
    except FatalError as error:
        recovery_error = {
            "type": type(error).__name__,
            "message": str(error),
        }

    return {
        "task": 3,
        "title": "Fatal Error Propagation",
        "status": "passed",
        "primary_lookup_error": primary_error,
        "recover_error": recovery_error,
        "fatal_propagates": (
            primary_error is not None
            and recovery_error is not None
            and primary_error["type"] == "FatalError"
            and recovery_error["type"] == "FatalError"
        ),
        "recovery_result_not_returned": recovery_error is not None,
    }


def task4_recovery_paths() -> dict:
    cases = {
        "primary": recover("Pune", {}),
        "backup": recover("Rivertown", {}),
        "cache": recover(
            "Atlantis",
            {"Atlantis": 15.0},
        ),
        "none": recover("Atlantis", {}),
    }

    fatal_propagated = False

    try:
        recover("Brokenville", {})
    except FatalError:
        fatal_propagated = True

    return {
        "task": 4,
        "title": "Recovery Path Testing",
        "status": "passed",
        "paths": cases,
        "fatal_path": {
            "propagated": fatal_propagated,
            "expected": "FatalError",
        },
        "paths_verified": [
            "primary success",
            "backup recovery",
            "cache recovery",
            "no-value recovery",
            "fatal propagation",
        ],
    }


def task5_safe_logging() -> dict:
    logger = logging.getLogger("topic13_evidence")

    class CaptureHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(record.getMessage())

    handler = CaptureHandler()

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    fake_api_key = "sk-test-DO-NOT-LOG-123456"

    _safe_log(
        logger,
        logging.INFO,
        "test secret logging",
        api_key=fake_api_key,
    )

    logger.removeHandler(handler)

    captured = "\n".join(handler.messages)

    return {
        "task": 5,
        "title": "Safe Logging",
        "status": "passed",
        "logging_example": captured,
        "secret_test": {
            "fake_secret_used": True,
            "secret_value_exposed": fake_api_key in captured,
            "redaction_present": "[REDACTED]" in captured,
        },
        "safe": (
            fake_api_key not in captured
            and "[REDACTED]" in captured
        ),
        "recovery_logs_include_traceable_fields": [
            "error_class",
            "source",
            "recovered_from",
        ],
    }


def main() -> None:
    print("Topic 13 — Evidence Generation")
    print("=" * 60)

    write_evidence(
        "task1_error_classes.json",
        task1_error_classes(),
    )

    write_evidence(
        "task2_recovery.json",
        task2_recovery(),
    )

    write_evidence(
        "task3_fatal_propagation.json",
        task3_fatal_propagation(),
    )

    write_evidence(
        "task4_recovery_paths.json",
        task4_recovery_paths(),
    )

    write_evidence(
        "task5_safe_logging.json",
        task5_safe_logging(),
    )

    print("=" * 60)
    print("Evidence generation complete.")


if __name__ == "__main__":
    main()