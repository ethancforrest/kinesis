# Norns Dev Tools

A comprehensive development toolkit for Monome Norns, with Claude Code integration.

## Features

- **SSH Connectivity**: Connect to your Norns device directly from Claude Code
- **Documentation Access**: Search and browse Norns documentation, API functions, and engines
- **Script Management**: Create, sync, and test scripts on your Norns device
- **Git Integration**: Commit and push your changes to GitHub
- **MCP Tool**: Use as a Claude Code MCP tool for seamless integration

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/norns-dev-tools.git
   cd norns-dev-tools
   ```

2. Install dependencies:
   ```
   pip install -e .
   ```

3. To install as an MCP tool for Claude Code:
   ```
   cd norns-dev-tools
   ./install.sh
   ```

## Usage

### Basic Usage with Claude Code

```python
# Import the Norns client
from norns_cli.claude_norns import connect_to_norns

# Connect to your Norns device (find your Norns IP in SYSTEM > WIFI)
norns = connect_to_norns(host="192.168.1.100", password="sleep")
await norns.connect()

# Run Lua code on Norns
result = await norns.run_lua('print("Hello from Claude Code!")')
print(result)

# Sync a script to Norns
await norns.sync_file("local_script.lua", "/home/we/dust/code/my_script/my_script.lua")

# Search Norns documentation
metro_docs = norns.search_api("metro")
print(metro_docs)

# Disconnect when done
await norns.disconnect()
```

### Working with Git

```python
from norns_cli.github_integration import NornsGitHub

# Create GitHub integration
github = NornsGitHub(host="192.168.1.100", password="sleep")

# Clone a repository
github.clone_repo("https://github.com/monome/dust.git", "dust")

# Sync to Norns
await github.connect()
await github.sync_repo_to_norns("dust/scripts/my_script")

# Make changes, commit, and push
github.create_branch("dust", "feature/my-changes")
github.stage_changes("dust")
github.commit_changes("dust", "Add awesome features")
github.push_changes("dust", "feature/my-changes")
```

### Complete Workflow Example

See `claude_complete_workflow_demo.py` for a complete demonstration of the development workflow, including:

1. Connecting to Norns
2. Using documentation to create a script
3. Syncing to Norns for testing
4. Committing and pushing changes to GitHub

To run the demo:
```
python claude_complete_workflow_demo.py
```

## CLI Usage

The toolkit also includes a command-line interface:

```
# Connect to Norns and run a command
norns-cli ssh --host 192.168.1.100 --command "ls /home/we/dust/code"

# Sync a script to Norns
norns-cli sync my_script.lua

# Search Norns documentation
norns-cli docs search metro

# Work with GitHub
norns-cli github clone https://github.com/monome/dust.git
norns-cli github sync dust/scripts/my_script
```

## Directory Structure

- `mcp_server/`: MCP server for Claude Code integration
  - `ssh_server/`: SSH server implementation
  - `norns_mcp_tool.json`: MCP tool specification
  - `norns_openapi.yaml`: OpenAPI specification

- `norns_cli/`: Core functionality
  - `claude_norns.py`: Claude Code integration
  - `norns_ssh.py`: SSH utility functions
  - `docs_manager.py`: Documentation management
  - `github_integration.py`: GitHub integration
  - `cli.py`: Command-line interface

## Requirements

- Python 3.8+
- asyncssh
- aiohttp
- beautifulsoup4
- typer
- rich
- sqlite3

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.