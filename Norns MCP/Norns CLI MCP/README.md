# Norns CLI and MCP Integration

A comprehensive toolkit for Monome Norns development using Claude Code, providing SSH connectivity, documentation access, and GitHub integration.

## Overview

This project creates a seamless development environment for Norns scripts directly within Claude Code. Key features include:

- **SSH Connectivity**: Connect to your Norns device from Claude Code
- **Documentation Access**: Search and browse Norns documentation, API functions, and engines
- **Script Development**: Create, sync, and test scripts on your Norns device
- **Git Integration**: Commit and push your changes to GitHub
- **MCP Integration**: Use as a Claude Code MCP tool

## Components

The project consists of several integrated components:

1. **SSH Client/Server**: Connects to your Norns device using asyncssh
2. **Documentation Manager**: Fetches and caches Norns documentation
3. **GitHub Integration**: Handles Git operations for version control
4. **Claude Code Integration**: Provides a simple API for use in Claude Code
5. **MCP Tool**: Integrates with Claude Code's MCP system

## Getting Started

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/norns-dev-tools.git
   ```

2. Install dependencies:
   ```
   cd norns-dev-tools
   pip install -e .
   ```

3. Set up MCP integration:
   ```
   mkdir -p ~/.claude/tools
   cp norns-dev-tools/mcp_server/norns_mcp_tool.json ~/.claude/tools/norns.json
   cp norns-dev-tools/mcp_server/norns_openapi.yaml ~/.claude/tools/norns_openapi.yaml
   ```

4. Restart Claude Code:
   ```
   claude-code restart
   ```

See `INSTALLATION.md` for detailed installation instructions.

### Basic Usage

```python
from norns_cli.claude_norns import connect_to_norns

# Connect to your Norns device
norns = connect_to_norns(host="192.168.1.100", password="sleep")
await norns.connect()

# Run Lua code
result = await norns.run_lua('print("Hello from Claude Code!")')
print(result)

# Sync a script
await norns.sync_file("my_script.lua", "/home/we/dust/code/my_script/my_script.lua")

# Search documentation
docs = norns.search_api("metro")
for doc in docs:
    print(f"{doc['name']}: {doc.get('description', 'No description')}")

# Disconnect
await norns.disconnect()
```

### Complete Workflow

The `claude_complete_workflow_demo.py` script demonstrates a complete workflow:

1. Connect to Norns
2. Use documentation to create a script
3. Sync to Norns for testing
4. Commit and push changes to GitHub

## Demo Scripts

- **claude_norns_test.py**: Basic SSH connectivity test
- **claude_norns_docs_demo.py**: Documentation access demonstration
- **claude_complete_workflow_demo.py**: Complete development workflow

## Project Structure

```
norns-dev-tools/
├── mcp_server/               # MCP server components
│   ├── ssh_server/           # SSH client/server implementation
│   ├── norns_mcp_tool.json   # MCP tool specification
│   └── norns_openapi.yaml    # OpenAPI specification
├── norns_cli/                # Core functionality
│   ├── claude_norns.py       # Claude Code integration API
│   ├── norns_ssh.py          # SSH utility functions
│   ├── docs_manager.py       # Documentation management
│   ├── github_integration.py # GitHub integration
│   └── cli.py                # Command-line interface
└── setup.py                  # Package installation
```

## Requirements

- Python 3.8+
- asyncssh
- aiohttp
- beautifulsoup4
- typer
- rich
- Git

## Credits

- [Monome Norns](https://monome.org/docs/norns/)
- [asyncssh](https://asyncssh.readthedocs.io/)
- [Claude Code](https://www.anthropic.com/claude)

## License

MIT

---

**Note**: This project requires a Monome Norns device on your local network. You'll need to know your Norns IP address, which can be found in SYSTEM > WIFI on your Norns device.