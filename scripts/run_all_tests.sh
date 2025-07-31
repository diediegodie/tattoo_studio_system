#!/bin/bash
# Always use the venv Python for tests

VENV_PYTHON="./.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Virtual environment not found! Please create it and install dependencies."
  exit 1
fi

echo "Running backend tests..."
PYTHONPATH="$(pwd)" pytest -v tests/backend/

echo "Running frontend tests..."
PYTHONPATH="$(pwd)" pytest -v tests/frontend/

echo "Running integration tests..."
PYTHONPATH="$(pwd)" pytest -v tests/integration/