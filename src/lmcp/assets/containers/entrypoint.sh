#!/bin/sh

set -e # Exit on error

VENV_DIR="/app/.venv"
REQUIREMENTS_FILE="/app/requirements.txt"

echo ">>> Checking virtual environment..."

# Clean up empty .venv directory if it exists (from volume mount point)
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/python" ]; then
    echo ">>> Removing empty venv directory..."
    rmdir "$VENV_DIR" 2>/dev/null || true
fi

# Check if venv is properly initialized (has bin/python)
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo ">>> Virtual environment not found or incomplete. Creating..."
    uv venv "$VENV_DIR"
    echo ">>> Virtual environment created."
    VENV_CREATED=true
else
    echo ">>> Virtual environment already exists."
    VENV_CREATED=false
fi

# Install dependencies if:
# 1. requirements.txt exists AND
# 2. (venv was just created OR dependencies not yet installed)
if [ -f "$REQUIREMENTS_FILE" ]; then
    # Check if we need to install (either new venv or missing the main package)
    if [ "$VENV_CREATED" = true ] || ! "$VENV_DIR/bin/python" -c "import mcdreforged" 2>/dev/null; then
        echo ">>> Installing dependencies from requirements.txt..."
        uv pip install --python "$VENV_DIR/bin/python" -r "$REQUIREMENTS_FILE"
        echo ">>> Dependencies installed."
    else
        echo ">>> Dependencies already installed. Skipping."
    fi
else
    echo ">>> No requirements.txt found. Skipping dependency installation."
fi

echo ">>> Handing over control to MCDR with LMCP..."
exec "$VENV_DIR/bin/python" -m mcdreforged start 