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
echo "Running APIClient authentication tests..."
PYTHONPATH="$(pwd)" pytest -v tests/frontend/test_api_client_auth.py

echo "Running integration tests..."
echo "Ensuring backend server is stopped before starting tests..."
# Kill any process using port 5000 (Flask default)
fuser -k 5000/tcp || true

echo "Initializing test database for frontend/integration tests..."
export DB_URL=sqlite:///test_integration.db

# Clean up old test database
if [ -f "test_integration.db" ]; then
  rm test_integration.db
fi

# Initialize the database using the database initializer service directly
python3 -c "
import os
os.environ['DB_URL'] = 'sqlite:///test_integration.db'
from services.database_initializer import initialize_database
from sqlalchemy import create_engine
engine = create_engine('sqlite:///test_integration.db')
result = initialize_database(engine=engine)
print('Database initialization result:', result)
"

if [ $? -ne 0 ]; then
  echo "Test database initialization failed!"
  exit 1
fi
echo "Test database initialized."

echo "Starting backend server for frontend/integration tests..."
export DB_URL=sqlite:///test_integration.db
python3 -m backend.app &
SERVER_PID=$!

# Wait for server to be ready (poll /health endpoint)
for i in {1..20}; do
  sleep 1
  if curl -s http://127.0.0.1:5000/health | grep 'success'; then
    echo "Backend server is up."
    break
  fi
done

echo "Running frontend tests that need live backend..."
export DB_URL=sqlite:///test_integration.db
PYTHONPATH="$(pwd)" DB_URL=sqlite:///test_integration.db pytest -v tests/frontend/

echo "Running integration tests..."
export DB_URL=sqlite:///test_integration.db
PYTHONPATH="$(pwd)" DB_URL=sqlite:///test_integration.db pytest -v tests/integration/

echo "Stopping backend server..."
kill $SERVER_PID