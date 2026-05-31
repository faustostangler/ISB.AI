import logging
import os

import pytest

from isb.main import main


def test_main_startup_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Verify that isb.main logs the current user ID and role on startup."""
    with caplog.at_level(logging.INFO, logger="isb.main"):
        main()

        # Check that we logged the startup message at INFO level
        assert len(caplog.records) >= 1
        startup_record = None
        for record in caplog.records:
            if "Starting ISB.AI system component" in record.message:
                startup_record = record
                break

        assert startup_record is not None, "Expected startup identity log was not found"
        assert startup_record.levelname == "INFO"

        # Verify the exact format: "Starting ISB.AI system component [role=worker] under UID <uid>"
        expected_uid = os.getuid()
        expected_msg = f"Starting ISB.AI system component [role=worker] under UID {expected_uid}"
        assert startup_record.message == expected_msg
