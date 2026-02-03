#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Initializing data..."
python scripts/init_data.py || echo "Data already exists or init skipped"

echo "Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
