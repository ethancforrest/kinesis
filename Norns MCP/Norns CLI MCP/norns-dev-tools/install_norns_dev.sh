#!/bin/bash

# Streamlined Norns Development Environment Installer
# This sets up everything needed for norns development with VS Code integration

set -e

echo "🚀 Installing Norns Development Environment..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
NORNS_DEV_ROOT="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed"
    exit 1
fi

print_success "Prerequisites check passed"

# Install Python dependencies
print_status "Installing Python dependencies..."
cd "$NORNS_DEV_ROOT"

# Create requirements.txt if it doesn't exist
cat > requirements.txt << EOF
asyncssh>=2.13.0
typer>=0.9.0
rich>=13.3.5
aiohttp>=3.8.0
beautifulsoup4>=4.9.0
markdown>=3.3.0
pyyaml>=6.0
netifaces>=0.11.0
EOF

pip3 install -r requirements.txt
print_success "Python dependencies installed"

# Install the norns development tools
print_status "Installing norns development tools..."
pip3 install -e .
print_success "Norns development tools installed"

# Set up configuration
print_status "Setting up norns configuration..."
python3 norns_config.py --discover
print_success "Configuration initialized"

# Make scripts executable
print_status "Setting up permissions..."
chmod +x norns_config.py
chmod +x ../sync_to_norns.py
print_success "Permissions set"

# Create VS Code configuration
print_status "Setting up VS Code integration..."

# Check if VS Code is installed
if command -v code &> /dev/null; then
    # Install recommended extensions
    print_status "Installing VS Code extensions..."
    code --install-extension sumneko.lua
    code --install-extension ms-vscode-remote.remote-ssh
    code --install-extension ms-python.python
    code --install-extension formulahendry.code-runner
    code --install-extension eamodio.gitlens
    
    print_success "VS Code extensions installed"
    
    # Open the workspace
    if [ -f "vscode/norns-workspace.code-workspace" ]; then
        print_status "Opening norns workspace in VS Code..."
        code "vscode/norns-workspace.code-workspace"
    fi
else
    print_warning "VS Code not found. Install VS Code for full integration."
fi

# Create shell aliases and functions
print_status "Creating shell shortcuts..."

SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_CONFIG="$HOME/.bash_profile"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if [ -n "$SHELL_CONFIG" ]; then
    # Add norns development aliases
    cat >> "$SHELL_CONFIG" << EOF

# Norns Development Shortcuts
alias norns-ssh='ssh we@192.168.50.151'
alias norns-sync='python3 "$NORNS_DEV_ROOT/../sync_to_norns.py"'
alias norns-config='python3 "$NORNS_DEV_ROOT/norns_config.py"'
alias norns-maiden='open http://192.168.50.151/maiden'

# Norns quick sync function
norns-quick-sync() {
    if [ -z "\$1" ]; then
        echo "Usage: norns-quick-sync <script-or-directory>"
        return 1
    fi
    python3 "$NORNS_DEV_ROOT/../sync_to_norns.py" "\$1" --restart
}
EOF

    print_success "Shell shortcuts added to $SHELL_CONFIG"
    print_warning "Run 'source $SHELL_CONFIG' or restart your terminal to use shortcuts"
else
    print_warning "Could not find shell configuration file to add shortcuts"
fi

# Test connection
print_status "Testing norns connection..."
if python3 norns_config.py --test default; then
    print_success "Norns connection test passed"
else
    print_warning "Could not connect to norns. Check your network connection and norns IP address."
fi

echo ""
print_success "🎉 Norns Development Environment installation complete!"
echo ""
echo -e "${BLUE}Available commands:${NC}"
echo "  norns-config --list          List configured devices"
echo "  norns-config --discover      Discover norns devices on network"
echo "  norns-sync <file>            Sync file/directory to norns"
echo "  norns-quick-sync <file>      Sync and restart script on norns"
echo "  norns-ssh                    SSH into norns"
echo "  norns-maiden                 Open maiden web interface"
echo ""
echo -e "${BLUE}VS Code Integration:${NC}"
echo "  Use Cmd+Shift+P and search for 'Tasks: Run Task'"
echo "  Available tasks:"
echo "    - Sync Script to Norns"
echo "    - Sync Current Directory to Norns" 
echo "    - Restart Norns Script"
echo "    - SSH to Norns"
echo "    - Open Maiden"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Open the norns workspace in VS Code: code '$NORNS_DEV_ROOT/vscode/norns-workspace.code-workspace'"
echo "2. Start developing norns scripts in '/Users/eforrest/Norns scripts'"
echo "3. Use the sync tasks to deploy your scripts to norns"
echo ""
echo "Happy norns coding! 🎵"