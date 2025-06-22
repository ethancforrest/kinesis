# Norns Dev Tools Installation Guide

This guide will help you install and configure the Norns Dev Tools for use with Claude Code.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- Claude Code installed on your system
- A Monome Norns device on your local network

## Installation Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/norns-dev-tools.git
   cd norns-dev-tools
   ```

2. **Install the Python package:**

   ```bash
   pip install -e .
   ```

   This will install the package in development mode, allowing you to make changes to the code.

3. **Set up MCP integration:**

   Create the necessary directories:

   ```bash
   mkdir -p ~/.claude/tools
   mkdir -p ~/.norns-cli/ssh_keys
   ```

   Copy the MCP tool specification:

   ```bash
   cp mcp_server/norns_mcp_tool.json ~/.claude/tools/norns.json
   ```

4. **Restart Claude Code:**

   ```bash
   claude-code restart
   ```

## Configuration

Before using the tools, you need to know the IP address of your Norns device:

1. On your Norns, navigate to **SYSTEM > WIFI**
2. Note the IP address displayed on the screen (e.g., 192.168.1.100)

## Testing the Installation

1. **Test SSH connectivity:**

   ```bash
   python -m norns_cli.norns_ssh test --host 192.168.1.100 --password sleep
   ```

   You should see a success message if the connection works.

2. **Test documentation access:**

   ```bash
   python -m norns_cli.docs_manager test
   ```

   This will test the documentation fetching and parsing.

3. **Test the complete workflow:**

   ```bash
   python claude_complete_workflow_demo.py
   ```

   This will demonstrate the entire development workflow.

## Using with Claude Code

In Claude Code, you can now use the Norns tools as follows:

```python
from norns_cli.claude_norns import connect_to_norns

# Connect to your Norns device
norns = connect_to_norns(host="192.168.1.100", password="sleep")
await norns.connect()

# Run Lua code on Norns
result = await norns.run_lua('print("Hello from Claude Code!")')
print(result)

# Sync a script to Norns
await norns.sync_file("local_script.lua", "/home/we/dust/code/my_script/my_script.lua")

# Disconnect when done
await norns.disconnect()
```

## Troubleshooting

- **SSH Connection Issues**: Verify your Norns IP address is correct and that you're on the same network.
- **Permission Errors**: Make sure you have appropriate permissions for all directories.
- **Import Errors**: Check that the package was installed correctly with `pip list | grep norns-dev-tools`.

## Additional Resources

- Norns Documentation: https://monome.org/docs/norns/
- Norns Scripting Guide: https://monome.org/docs/norns/scripting/
- Norns Studies: https://monome.org/docs/norns/scripting/#study-1-hello-world

For any issues or questions, please open an issue on the GitHub repository.