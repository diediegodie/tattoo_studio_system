#!/bin/bash
# Always use the venv Python for tests

VENV_PYTHON="./.venv/bin/python"
VENV_PYTEST="./.venv/bin/pytest"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Virtual environment not found! Please create it and install dependencies."
  exit 1
fi

echo "Running backend tests..."
PYTHONPATH="$(pwd)" "$VENV_PYTEST" -v tests/backend/

echo "Running frontend tests..."
PYTHONPATH="$(pwd)" "$VENV_PYTEST" -v tests/frontend/