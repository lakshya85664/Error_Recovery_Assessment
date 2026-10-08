"""
Topic 13: Error Recovery

Tasks 1-5:
- Define error classes.
- Implement primary lookup and recovery.
- Propagate fatal errors.
- Test every recovery path.
- Log failures and recoveries safely.
"""

import logging
import re


logger = logging.getLogger(__name__)


class TransientError(Exception):
    """Raised when an operation fails temporarily."""
    pass


class NotFoundError(Exception):
    """Raised when the requested value cannot be found."""
    pass


class FatalError(Exception):
    """Raised when the operation must stop immediately."""
    pass


def _safe_log(logger_instance: logging.Logger, level: int, message: str, **fields) -> None:
    """
    Write a structured log message while redacting common secrets.

    This helper prevents API keys, bearer tokens, passwords, and similar
    values from being written to logs.
    """
    secret_pattern = re.compile(
        r"(?i)"
        r"(api[_-]?key|authorization|bearer|token|password|secret)"
        r"\s*[:=]\s*[^\s,;]+"
    )

    parts = [message]

    for key, value in fields.items():
        field_text = f"{key}={value}"
        field_text = secret_pattern.sub(
            lambda match: f"{match.group(1)}=[REDACTED]",
            field_text,
        )
        parts.append(field_text)

    final_message = " | ".join(parts)

    logger_instance.log(level, final_message)


def primary_lookup(city: str, calls: dict[str, int]) -> float:
    """
    Simulate the primary lookup tool.

    The calls dictionary tracks how many times the primary tool
    has been called.
    """
    if not isinstance(city, str):
        raise TypeError("city must be a string")

    if not isinstance(calls, dict):
        raise TypeError("calls must be a dictionary")

    calls["n"] = calls.get("n", 0) + 1

    if city == "Atlantis":
        raise NotFoundError(city)

    if city == "Rivertown":
        raise TransientError("timeout")

    if city == "Brokenville":
        raise FatalError("auth key revoked")

    if city not in {"Pune"}:
        raise NotFoundError(city)

    return 29.0


def backup_lookup(city: str) -> float:
    """
    Simulate a backup lookup tool.

    The backup tool can recover from transient primary failures.
    """
    if not isinstance(city, str):
        raise TypeError("city must be a string")

    return {
        "Rivertown": 21.5,
    }[city]


def recover(city: str, cache: dict[str, float]) -> dict[str, object]:
    """
    Recover a lookup using the appropriate strategy.

    Recovery strategy:
    - Primary success -> primary result.
    - TransientError -> backup lookup.
    - NotFoundError -> cache, otherwise None.
    - FatalError -> log and propagate unchanged.
    """
    if not isinstance(city, str):
        raise TypeError("city must be a string")

    if not isinstance(cache, dict):
        raise TypeError("cache must be a dictionary")

    calls = {"n": 0}

    try:
        value = primary_lookup(city, calls)

        _safe_log(
            logger,
            logging.INFO,
            "recovery success",
            city=city,
            source="primary",
            recovered_from=None,
        )

        return {
            "value": value,
            "source": "primary",
            "recovered_from": None,
        }

    except TransientError as error:
        _safe_log(
            logger,
            logging.ERROR,
            "recovery failure",
            city=city,
            error_class=type(error).__name__,
        )

        try:
            value = backup_lookup(city)

            _safe_log(
                logger,
                logging.INFO,
                "recovery success",
                city=city,
                source="backup",
                recovered_from=str(error),
            )

            return {
                "value": value,
                "source": "backup",
                "recovered_from": str(error),
            }

        except KeyError:
            _safe_log(
                logger,
                logging.WARNING,
                "recovery exhausted",
                city=city,
                source="none",
                recovered_from=str(error),
            )

            return {
                "value": None,
                "source": "none",
                "recovered_from": str(error),
            }

    except NotFoundError as error:
        _safe_log(
            logger,
            logging.ERROR,
            "recovery failure",
            city=city,
            error_class=type(error).__name__,
        )

        if city in cache:
            _safe_log(
                logger,
                logging.INFO,
                "recovery success",
                city=city,
                source="cache",
                recovered_from="not_found",
            )

            return {
                "value": cache[city],
                "source": "cache",
                "recovered_from": "not_found",
            }

        _safe_log(
            logger,
            logging.WARNING,
            "recovery exhausted",
            city=city,
            source="none",
            recovered_from="not_found",
        )

        return {
            "value": None,
            "source": "none",
            "recovered_from": "not_found",
        }

    except FatalError as error:
        _safe_log(
            logger,
            logging.ERROR,
            "fatal recovery failure",
            city=city,
            error_class=type(error).__name__,
        )

        # FatalError must never be replaced by a default,
        # cache value, or backup result.
        raise