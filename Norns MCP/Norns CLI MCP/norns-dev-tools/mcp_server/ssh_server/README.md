# Norns SSH Server and Client

This module provides SSH functionality for connecting to a Norns device from Claude Code.

## Features

- SSH server for listening for connections
- SSH client for connecting to a Norns device
- Command-line interface for executing commands over SSH
- Support for executing Lua code on the Norns device
- Interactive shell mode

## Requirements

- Python 3.7+
- asyncssh

## Installation

```bash
# Install the required dependencies
pip install asyncssh
```

## Usage

### SSH Client

```python
import asyncio
from norns_dev_tools.mcp_server.ssh_server.client import NornsSSHClient

async def main():
    # Create a client
    client = NornsSSHClient(
        host="norns.local",  # or IP address
        port=22,
        username="we",
        # Either provide password or key_file
        password="your_password",  # Optional
        key_file="~/.ssh/id_rsa"   # Optional
    )
    
    try:
        # Connect to the Norns device
        await client.connect()
        
        # Execute a shell command
        stdout, stderr, return_code = await client.execute_command("ls -la")
        print(f"Command output: {stdout}")
        
        # Execute Lua code
        stdout, stderr, return_code = await client.execute_lua('print("Hello from Lua")')
        print(f"Lua output: {stdout}")
        
    finally:
        # Disconnect from the device
        await client.disconnect()

# Run the example
asyncio.run(main())
```

### Command Line Interface

The module includes a command-line interface for connecting to a Norns device:

```bash
# Execute a command on the Norns device
python -m norns_dev_tools.mcp_server.ssh_server.cli -c "ls -la"

# Execute Lua code on the Norns device
python -m norns_dev_tools.mcp_server.ssh_server.cli -l 'print("Hello from Lua")'

# Open an interactive shell
python -m norns_dev_tools.mcp_server.ssh_server.cli
```

### SSH Server

The module also includes an SSH server that can be used to listen for connections:

```python
import asyncio
from norns_dev_tools.mcp_server.ssh_server.server import NornsSSHServer

async def main():
    # Create a server
    server = NornsSSHServer(
        host="0.0.0.0",
        port=22023
    )
    
    # Start the server
    await server.start()
    
    try:
        # Keep the server running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Stop the server
        await server.stop()

# Run the server
asyncio.run(main())
```

## Configuration

SSH keys and known hosts are stored in the following locations:

- SSH keys: `~/.norns-cli/ssh_keys/`
- Known hosts: `~/.norns-cli/ssh_keys/known_hosts`

You can customize these locations by passing appropriate parameters to the `NornsSSHClient` or `NornsSSHServer` constructors.

## Using from Claude Code

To use this module from Claude Code, you can make SSH connections to your Norns device using the following Python code:

```python
import asyncio
from norns_dev_tools.mcp_server.ssh_server.client import NornsSSHClient

async def connect_to_norns():
    client = NornsSSHClient(
        host="norns.local",  # Use the appropriate hostname or IP
        username="we"        # Default Norns username
    )
    
    await client.connect()
    
    # Execute your commands here
    stdout, _, _ = await client.execute_command("ls -la")
    print(stdout)
    
    await client.disconnect()

# Run in Claude Code
asyncio.run(connect_to_norns())
```