import pytest

from src.error_recovery import (
    TransientError,
    NotFoundError,
    FatalError,
    primary_lookup,
    backup_lookup,
    recover,
)


# ============================================================
# Task 1 — Error classes
# ============================================================

def test_transient_error_is_exception():
    error = TransientError("temporary timeout")

    assert isinstance(error, Exception)
    assert str(error) == "temporary timeout"


def test_not_found_error_is_exception():
    error = NotFoundError("city not found")

    assert isinstance(error, Exception)
    assert str(error) == "city not found"


def test_fatal_error_is_exception():
    error = FatalError("authentication key revoked")

    assert isinstance(error, Exception)
    assert str(error) == "authentication key revoked"


def test_error_classes_are_distinct():
    assert TransientError is not NotFoundError
    assert NotFoundError is not FatalError
    assert TransientError is not FatalError


def test_transient_error_can_be_raised():
    with pytest.raises(TransientError):
        raise TransientError("timeout")


def test_not_found_error_can_be_raised():
    with pytest.raises(NotFoundError):
        raise NotFoundError("missing city")


def test_fatal_error_can_be_raised():
    with pytest.raises(FatalError):
        raise FatalError("key revoked")


# ============================================================
# Task 2 — Recovery
# ============================================================

def test_primary_lookup_success():
    calls = {"n": 0}

    result = primary_lookup("Pune", calls)

    assert result == 29.0
    assert calls["n"] == 1


def test_backup_lookup_returns_value():
    result = backup_lookup("Rivertown")

    assert result == 21.5


def test_recover_primary_success():
    result = recover("Pune", {})

    assert result == {
        "value": 29.0,
        "source": "primary",
        "recovered_from": None,
    }


def test_recover_transient_uses_backup():
    result = recover("Rivertown", {})

    assert result == {
        "value": 21.5,
        "source": "backup",
        "recovered_from": "timeout",
    }


def test_recover_not_found_uses_cache():
    result = recover(
        "Atlantis",
        {"Atlantis": 15.0},
    )

    assert result == {
        "value": 15.0,
        "source": "cache",
        "recovered_from": "not_found",
    }


def test_recover_not_found_without_cache_returns_none():
    result = recover("Atlantis", {})

    assert result == {
        "value": None,
        "source": "none",
        "recovered_from": "not_found",
    }


def test_recover_fatal_error_propagates():
    with pytest.raises(FatalError, match="auth key revoked"):
        recover("Brokenville", {})


def test_recover_rejects_non_string_city():
    with pytest.raises(TypeError, match="city must be a string"):
        recover(123, {})


def test_recover_rejects_non_dictionary_cache():
    with pytest.raises(TypeError, match="cache must be a dictionary"):
        recover("Pune", [])


def test_backup_lookup_rejects_non_string_city():
    with pytest.raises(TypeError, match="city must be a string"):
        backup_lookup(123)

# ============================================================
# Task 3 — Fatal errors must propagate
# ============================================================

def test_primary_lookup_raises_fatal_error():
    calls = {"n": 0}

    with pytest.raises(FatalError, match="auth key revoked"):
        primary_lookup("Brokenville", calls)

    assert calls["n"] == 1


def test_recover_propagates_fatal_error():
    cache = {
        "Brokenville": 999.0,
    }

    with pytest.raises(FatalError, match="auth key revoked"):
        recover("Brokenville", cache)


def test_fatal_error_is_not_replaced_with_none():
    with pytest.raises(FatalError):
        result = recover("Brokenville", {})

        # This line must never be reached.
        assert result["value"] is None


def test_fatal_error_is_not_recovered_from_cache():
    cache = {
        "Brokenville": 999.0,
    }

    with pytest.raises(FatalError):
        result = recover("Brokenville", cache)

        # Fatal errors must never reach the cache result.
        assert result["source"] == "cache"


def test_fatal_error_is_not_recovered_by_backup():
    with pytest.raises(FatalError):
        result = recover("Brokenville", {})

        # Fatal errors must never reach the backup result.
        assert result["source"] == "backup"

# ============================================================
# Task 4 — Test every recovery path
# ============================================================

def test_task4_primary_success_path():
    result = recover("Pune", {})

    assert result["value"] == 29.0
    assert result["source"] == "primary"
    assert result["recovered_from"] is None


def test_task4_backup_success_path():
    result = recover("Rivertown", {})

    assert result["value"] == 21.5
    assert result["source"] == "backup"
    assert result["recovered_from"] == "timeout"


def test_task4_cache_recovery_path():
    cache = {
        "Atlantis": 15.0,
    }

    result = recover("Atlantis", cache)

    assert result["value"] == 15.0
    assert result["source"] == "cache"
    assert result["recovered_from"] == "not_found"


def test_task4_no_value_path():
    result = recover("Atlantis", {})

    assert result["value"] is None
    assert result["source"] == "none"
    assert result["recovered_from"] == "not_found"


def test_task4_fatal_path():
    with pytest.raises(FatalError, match="auth key revoked"):
        recover("Brokenville", {})


def test_task4_recovery_sources_are_traceable():
    primary = recover("Pune", {})
    backup = recover("Rivertown", {})
    cached = recover("Atlantis", {"Atlantis": 15.0})
    missing = recover("Atlantis", {})

    assert primary["source"] == "primary"
    assert backup["source"] == "backup"
    assert cached["source"] == "cache"
    assert missing["source"] == "none"


def test_task4_fatal_never_returns_recovery_result():
    try:
        recover("Brokenville", {})
    except FatalError as error:
        assert str(error) == "auth key revoked"
    else:
        pytest.fail("FatalError was unexpectedly recovered")

# ============================================================
# Task 5 — Safe logging
# ============================================================

def test_task5_logs_primary_success(caplog):
    with caplog.at_level("INFO"):
        result = recover("Pune", {})

    assert result["source"] == "primary"
    assert "recovery success" in caplog.text
    assert "source=primary" in caplog.text


def test_task5_logs_transient_failure_and_backup(caplog):
    with caplog.at_level("INFO"):
        result = recover("Rivertown", {})

    assert result["source"] == "backup"
    assert "recovery failure" in caplog.text
    assert "error_class=TransientError" in caplog.text
    assert "source=backup" in caplog.text


def test_task5_logs_not_found_and_cache_recovery(caplog):
    with caplog.at_level("INFO"):
        result = recover("Atlantis", {"Atlantis": 15.0})

    assert result["source"] == "cache"
    assert "error_class=NotFoundError" in caplog.text
    assert "source=cache" in caplog.text


def test_task5_logs_not_found_without_recovery(caplog):
    with caplog.at_level("INFO"):
        result = recover("Atlantis", {})

    assert result["source"] == "none"
    assert "error_class=NotFoundError" in caplog.text
    assert "source=none" in caplog.text


def test_task5_logs_fatal_error_before_propagating(caplog):
    with caplog.at_level("INFO"):
        with pytest.raises(FatalError):
            recover("Brokenville", {})

    assert "fatal recovery failure" in caplog.text
    assert "error_class=FatalError" in caplog.text


def test_task5_logging_does_not_expose_fake_api_key(caplog):
    """
    Verify that the logging helper redacts a fake secret.
    """
    from src.error_recovery import _safe_log, logger

    fake_api_key = "sk-test-DO-NOT-LOG-123456"

    with caplog.at_level("INFO", logger=logger.name):
        _safe_log(
            logger,
            20,
            "test secret logging",
            api_key=fake_api_key,
        )

    assert fake_api_key not in caplog.text
    assert "[REDACTED]" in caplog.text


def test_task5_logging_contains_no_authorization_token(caplog):
    """
    Verify that authorization-style secrets are redacted.
    """
    from src.error_recovery import _safe_log, logger

    fake_token = "Bearer SECRET-TOKEN-123"

    with caplog.at_level("INFO", logger=logger.name):
        _safe_log(
            logger,
            20,
            "test authorization logging",
            authorization=fake_token,
        )

    assert fake_token not in caplog.text
    assert "[REDACTED]" in caplog.text