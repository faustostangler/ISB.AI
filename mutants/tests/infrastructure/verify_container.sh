#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo "Starting SPEC-006 Container Security Smoke Checks"
echo "=================================================="

# 1. Build the docker image locally
echo "--> Building Docker image 'isb:latest'..."
docker build -t isb:latest .

# 2. Assert identity constraints (user ID must be 10001)
echo "--> Asserting running user ID equals 10001..."
RUNNING_UID=$(docker run --rm isb:latest id -u)
if [ "$RUNNING_UID" != "10001" ]; then
    echo "ERROR: Expected UID 10001, got $RUNNING_UID" >&2
    exit 1
fi
echo "  [PASS] Running UID is $RUNNING_UID"

# 3. Assert identity constraints (group ID must be 10001)
echo "--> Asserting running group ID equals 10001..."
RUNNING_GID=$(docker run --rm isb:latest id -g)
if [ "$RUNNING_GID" != "10001" ]; then
    echo "ERROR: Expected GID 10001, got $RUNNING_GID" >&2
    exit 1
fi
echo "  [PASS] Running GID is $RUNNING_GID"

# 4. Assert system library validation (ffmpeg exits 0)
echo "--> Asserting ffmpeg is installed and executable..."
docker run --rm isb:latest ffmpeg -version >/dev/null
echo "  [PASS] ffmpeg executes successfully"

# 5. Assert writable app directory (dummy file write/cleanup)
echo "--> Asserting /app workspace is writable by user isb..."
docker run --rm isb:latest bash -c "touch /app/src/test_write.tmp && rm /app/src/test_write.tmp"
echo "  [PASS] File creation and cleanup succeeded"

echo "=================================================="
echo "All SPEC-006 Container Security Smoke Checks PASSED"
echo "=================================================="
