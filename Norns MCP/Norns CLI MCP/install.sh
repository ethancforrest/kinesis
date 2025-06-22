#!/bin/bash
# Norns Development Tools - Quick Install Script

set -e

echo "🎛️  Installing Norns Development Tools"
echo "======================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="$SCRIPT_DIR/norns-dev-tools"

# Check Python version
echo "📋 Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.8+"; exit 1; }

# Check if virtual environment exists
if [ ! -d "$TOOLS_DIR/venv" ]; then
    echo "🔧 Creating virtual environment..."
    cd "$TOOLS_DIR"
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install
echo "📦 Installing dependencies..."
cd "$TOOLS_DIR"
source venv/bin/activate
pip install --upgrade pip
pip install -e .

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Quick Start:"
echo "   1. Update your Norns IP in quick_sync.py"
echo "   2. Test connection: python3 quick_sync.py --help"
echo "   3. Sync a file: python3 quick_sync.py your_script.lua --restart"
echo ""
echo "📖 See NORNS_DEVELOPMENT_SETUP.md for full documentation"