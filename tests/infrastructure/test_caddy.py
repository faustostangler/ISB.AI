import pathlib
import shutil
import subprocess
import pytest


@pytest.mark.integration
def test_caddyfile_validation() -> None:
    """Validate the syntax of the infrastructure Caddyfile.

    First tries to use the local caddy binary if installed, falling back to running
    caddy validate inside a lightweight docker container if docker is running.
    If neither is available, the test skips gracefully.
    """
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    caddyfile_path = project_root / "infrastructure" / "caddy" / "Caddyfile"

    assert caddyfile_path.exists(), f"Caddyfile must exist at {caddyfile_path}"

    # 1. Attempt local validation
    caddy_bin = shutil.which("caddy")
    if caddy_bin:
        result = subprocess.run(
            [caddy_bin, "validate", "--config", str(caddyfile_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, f"Local Caddy validation failed:\n{result.stderr}\n{result.stdout}"
        return

    # 2. Attempt fallback validation via Docker container
    docker_bin = shutil.which("docker")
    if docker_bin:
        # Verify docker daemon accessibility
        daemon_status = subprocess.run(
            [docker_bin, "info"],
            capture_output=True,
            check=False,
        )
        if daemon_status.returncode == 0:
            result = subprocess.run(
                [
                    docker_bin,
                    "run",
                    "--rm",
                    "-v",
                    f"{caddyfile_path.resolve()}:/etc/caddy/Caddyfile",
                    "caddy:2-alpine",
                    "caddy",
                    "validate",
                    "--config",
                    "/etc/caddy/Caddyfile",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0, f"Docker Caddy validation failed:\n{result.stderr}\n{result.stdout}"
            return

    pytest.skip("Neither local Caddy nor running Docker daemon is available to validate Caddyfile syntax")
