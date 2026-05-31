import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from isb.presentation.api import HealthCheckResponse, health_check, main


def test_health_check_endpoint() -> None:
    """Verifies that the health check endpoint returns a healthy status."""
    response = health_check()
    assert isinstance(response, HealthCheckResponse)
    assert response.status == "healthy"


def test_cli_exporter_success_in_process(tmp_path: Path) -> None:
    """Scenario 1: CLI schema exporter executes successfully and writes a valid OpenAPI spec."""
    output_file = tmp_path / "openapi.json"
    test_args = ["api.py", "export-schema", "--output", str(output_file)]

    with patch.object(sys, "argv", test_args):
        main()

    # Verify output file existence
    assert output_file.exists(), f"Output file was not created at {output_file}"

    # Verify valid JSON and expected OpenAPI root keys
    with output_file.open(encoding="utf-8") as f:
        schema = json.load(f)

    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    assert "components" in schema
    assert "/health" in schema["paths"]


def test_cli_exporter_short_flag_success(tmp_path: Path) -> None:
    """Scenario 2: CLI schema exporter executes successfully using the short flag '-o'."""
    output_file = tmp_path / "openapi_short.json"
    test_args = ["api.py", "export-schema", "-o", str(output_file)]

    with patch.object(sys, "argv", test_args):
        main()

    assert output_file.exists()


def test_cli_exporter_invalid_path_in_process() -> None:
    """Boundary Condition: Invalid output path must fail and exit with non-zero code."""
    test_args = ["api.py", "export-schema", "--output", "/nonexistent_dir_xyz/openapi.json"]

    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code == 1


def test_cli_exporter_missing_args_in_process() -> None:
    """Boundary Condition: Running without required command arguments must exit with SystemExit."""
    test_args = ["api.py"]

    with patch.object(sys, "argv", test_args):
        # argparse defaults to printing to stderr and exiting with 2 on missing args
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code != 0


def test_cli_exporter_missing_output_argument() -> None:
    """Boundary Condition: Running export-schema command without --output must exit with SystemExit."""
    test_args = ["api.py", "export-schema"]

    with patch.object(sys, "argv", test_args):
        # argparse should exit with non-zero code (typically 2) on missing required argument
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code == 2


def test_cli_exporter_help_contains_expected_text() -> None:
    """Verifies that the CLI help outputs contain expected help text, killing documentation mutants."""
    # 1. Check parent parser help
    parent_args = ["api.py", "--help"]
    with patch.object(sys, "argv", parent_args), patch.object(sys, "stdout", new_callable=StringIO) as mock_stdout:
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 0
    assert "Export the OpenAPI schema to a file" in mock_stdout.getvalue()

    # 2. Check subcommand parser help
    sub_args = ["api.py", "export-schema", "--help"]
    with patch.object(sys, "argv", sub_args), patch.object(sys, "stdout", new_callable=StringIO) as mock_stdout:
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code == 0
    assert "Path where the openapi.json file will be written" in mock_stdout.getvalue()
