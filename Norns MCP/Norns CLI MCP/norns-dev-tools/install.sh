#!/bin/bash
# Install script for Norns Dev Tools MCP integration

echo "Installing Norns Dev Tools for Claude Code..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Install Python package in development mode
echo "Installing Python package..."
pip install -e "$SCRIPT_DIR"

# Create Claude MCP tool directory if it doesn't exist
MCP_DIR="$HOME/.claude/tools"
mkdir -p "$MCP_DIR"

# Copy MCP tool specification
echo "Installing MCP tool specification..."
cp "$SCRIPT_DIR/mcp_server/norns_mcp_tool.json" "$MCP_DIR/norns.json"

# Create SSH keys directory if it doesn't exist
SSH_DIR="$HOME/.norns-cli/ssh_keys"
mkdir -p "$SSH_DIR"

echo "Installation complete!"
echo 
echo "To use the Norns MCP tool with Claude Code:"
echo "1. Restart Claude Code: claude-code restart"
echo "2. The 'norns' tool should now be available in the tool list"
echo "3. Use the following code to connect to your Norns device:"
echo 
echo "from norns_cli.claude_norns import connect_to_norns"
echo 
echo "# Connect to your Norns device (replace with your Norns IP address)"
echo "norns = connect_to_norns(host=\"192.168.1.100\", password=\"sleep\")"
echo "await norns.connect()"
echo 
echo "# Now you can use norns.run_lua(), norns.sync_file(), etc."
echo
echo "For CLI usage:"
echo "norns-cli --help"