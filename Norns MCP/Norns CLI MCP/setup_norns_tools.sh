#!/bin/bash
# Setup script for Norns Dev Tools

echo "=== Norns Dev Tools Setup ==="
echo "This script will set up the Norns Dev Tools for use with Claude Code."

# Create necessary directories
echo "Creating directories..."
mkdir -p ~/.claude/tools
mkdir -p ~/.norns-cli/ssh_keys

# Copy MCP tool specification
echo "Installing MCP tool specifications..."
cp norns-dev-tools/mcp_server/norns_mcp_tool.json ~/.claude/tools/norns.json

# Install Python package
echo "Installing Python package..."
pip install -e norns-dev-tools

echo "Setup complete!"
echo 
echo "To use the Norns tools with Claude Code:"
echo "1. Restart Claude Code: claude-code restart"
echo "2. Find your Norns IP address in SYSTEM > WIFI on your Norns"
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
echo "For more detailed instructions, see INSTALLATION.md"