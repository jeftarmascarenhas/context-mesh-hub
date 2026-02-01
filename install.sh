#!/bin/bash
# Context Mesh Hub - Installation Script
# 
# This script installs Context Mesh Hub for development/testing
#
# Usage:
#   ./install.sh          # Auto-detect best installer (uv > pipx > venv)
#   ./install.sh --uv     # Force uv
#   ./install.sh --venv   # Force venv creation

set -e

echo "╭──────────────────────────────────────────────────────────────╮"
echo "│                                                              │"
echo "│     ██████╗ ██████╗ ███╗   ██╗████████╗███████╗██╗  ██╗████████╗"
echo "│    ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝"
echo "│    ██║     ██║   ██║██╔██╗ ██║   ██║   █████╗   ╚███╔╝    ██║  "
echo "│    ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══╝   ██╔██╗    ██║  "
echo "│    ╚██████╗╚██████╔╝██║ ╚████║   ██║   ███████╗██╔╝ ██╗   ██║  "
echo "│     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝  "
echo "│                          MESH HUB                              │"
echo "│                                                              │"
echo "│     Installing Context Mesh Hub...                           │"
echo "│                                                              │"
echo "╰──────────────────────────────────────────────────────────────╯"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    echo "❌ Python 3.12+ is required (found: Python $PYTHON_VERSION)"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION"

# Determine installer method
USE_UV=false
USE_VENV=false

if [ "$1" == "--uv" ]; then
    USE_UV=true
elif [ "$1" == "--venv" ]; then
    USE_VENV=true
else
    # Auto-detect: prefer uv if available
    if command -v uv &> /dev/null; then
        USE_UV=true
    else
        USE_VENV=true
    fi
fi

if [ "$USE_UV" = true ]; then
    if ! command -v uv &> /dev/null; then
        echo "❌ uv not found. Install it with:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo ""
        echo "Or run: ./install.sh --venv"
        exit 1
    fi
    echo "✓ Using uv"
    
    # Install hub-core
    echo ""
    echo "📦 Installing hub-core (MCP server)..."
    cd "$SCRIPT_DIR/hub-core"
    uv pip install -e . --system 2>/dev/null || uv pip install -e .
    
    # Install hub-cli
    echo ""
    echo "📦 Installing hub-cli..."
    cd "$SCRIPT_DIR/hub-cli"
    uv pip install -e . --system 2>/dev/null || uv pip install -e .
    
else
    echo "✓ Using venv"
    
    # Create virtual environment
    VENV_DIR="$SCRIPT_DIR/.venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo ""
        echo "📦 Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate venv
    source "$VENV_DIR/bin/activate"
    
    # Install hub-core
    echo ""
    echo "📦 Installing hub-core (MCP server)..."
    cd "$SCRIPT_DIR/hub-core"
    pip install -e .
    
    # Install hub-cli
    echo ""
    echo "📦 Installing hub-cli..."
    cd "$SCRIPT_DIR/hub-cli"
    pip install -e .
    
    echo ""
    echo "⚠️  Virtual environment created at: $VENV_DIR"
    echo "   Activate it with: source $VENV_DIR/bin/activate"
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."

# Check if cm is available
if [ "$USE_VENV" = true ]; then
    CM_PATH="$VENV_DIR/bin/cm"
else
    CM_PATH=$(command -v cm 2>/dev/null || echo "")
fi

if [ -n "$CM_PATH" ] && [ -x "$CM_PATH" ]; then
    CM_VERSION=$("$CM_PATH" --version 2>&1)
    echo "✓ $CM_VERSION"
else
    echo "⚠ 'cm' command not found in PATH"
    if [ "$USE_VENV" = true ]; then
        echo "  Run: source $VENV_DIR/bin/activate"
    else
        echo "  You may need to restart your shell"
    fi
fi

echo ""
echo "╭──────────────────────────────────────────────────────────────╮"
echo "│  ✅ Installation complete!                                   │"
echo "│                                                              │"
if [ "$USE_VENV" = true ]; then
echo "│  Activate environment:                                       │"
echo "│    source $SCRIPT_DIR/.venv/bin/activate"
echo "│                                                              │"
fi
echo "│  Next steps:                                                 │"
echo "│    1. cm init --ai cursor    # Choose your AI agent         │"
echo "│    2. cm config              # Get MCP configuration        │"
echo "│    3. cm doctor              # Verify setup                 │"
echo "│                                                              │"
echo "│  For help: cm --help                                        │"
echo "╰──────────────────────────────────────────────────────────────╯"
