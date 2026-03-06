#!/usr/bin/env bash
# Publish llm-model-deprecation to PyPI using a dedicated venv (no conflict with system packages).
# Set credentials: export TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-YourToken
# Then: bash scripts/publish.sh

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv-deploy"
cd "$REPO_ROOT"

# Create venv if missing
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating deploy venv at $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

# Activate and install build + twine (isolated from system urllib3/requests)
echo "Installing build and twine in venv..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip build twine

# Build
echo "Building..."
"$VENV_DIR/bin/python" -m build

# Upload (reads TWINE_USERNAME / TWINE_PASSWORD from environment)
echo "Uploading to PyPI..."
"$VENV_DIR/bin/twine" upload dist/*

echo "Done. Check https://pypi.org/project/llm-model-deprecation/"
