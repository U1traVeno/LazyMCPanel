#!/bin/sh

set -e # Exit on error
echo ">>> handling over contorl to MCDR with LMCP..."
exec /app/.venv/bin/python -m mcdreforged start 