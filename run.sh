#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000