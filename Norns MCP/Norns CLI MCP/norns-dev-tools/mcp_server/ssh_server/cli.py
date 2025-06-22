"""
Command-line interface for the Norns SSH client.
"""

import argparse
import asyncio
import getpass
import os
import sys
import logging
from typing import List, Optional

from .client import NornsSSHClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("norns_ssh_cli")


async def handle_command(args):
    """Handle the command line arguments."""
    # Create the client
    client = NornsSSHClient(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        key_file=args.key_file,
    )
    
    try:
        # Connect to the server
        await client.connect()
        
        # Execute command if provided
        if args.command:
            stdout, stderr, return_code = await client.execute_command(args.command)
            print(stdout, end="")
            if stderr:
                print(stderr, file=sys.stderr, end="")
            if args.verbose:
                print(f"Command exited with status {return_code}")
            
            # Set exit code to match command exit code
            sys.exit(return_code)
            
        # Execute Lua code if provided
        elif args.lua:
            stdout, stderr, return_code = await client.execute_lua(args.lua)
            print(stdout, end="")
            if stderr:
                print(stderr, file=sys.stderr, end="")
            if args.verbose:
                print(f"Lua code exited with status {return_code}")
                
            # Set exit code to match command exit code
            sys.exit(return_code)
            
        # Interactive shell mode
        else:
            print(f"Connected to {args.host}. Press Ctrl+D to exit.")
            await interactive_shell(client)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        # Disconnect from the server
        await client.disconnect()


async def interactive_shell(client: NornsSSHClient):
    """Run an interactive shell session."""
    # This is a simplified version - a real implementation would need
    # proper terminal handling with asyncio
    try:
        # Start a shell on the server
        async with client._connection.start_shell() as shell:
            # Set up stdin reader
            stdin_reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(stdin_reader)
            await asyncio.get_event_loop().connect_read_pipe(
                lambda: protocol, sys.stdin)
            
            # Task to read from stdin and send to shell
            async def stdin_to_shell():
                while True:
                    data = await stdin_reader.readline()
                    if not data:  # EOF (Ctrl+D)
                        break
                    shell.write(data)
            
            # Task to read from shell and write to stdout
            async def shell_to_stdout():
                while True:
                    data = await shell.read(1024)
                    if not data:
                        break
                    sys.stdout.write(data)
                    sys.stdout.flush()
            
            # Run the tasks
            await asyncio.gather(
                stdin_to_shell(),
                shell_to_stdout()
            )
    except Exception as e:
        logger.error(f"Interactive shell error: {e}")


def main():
    """Run the CLI."""
    parser = argparse.ArgumentParser(description="Connect to a Norns device via SSH")
    
    # Connection options
    parser.add_argument("-H", "--host", default="norns.local",
                        help="Hostname or IP address of the Norns device")
    parser.add_argument("-p", "--port", type=int, default=22,
                        help="SSH port on the Norns device")
    parser.add_argument("-u", "--username", default="we",
                        help="Username for the Norns device")
    parser.add_argument("-P", "--password", default=None,
                        help="Password for the Norns device (if not using key)")
    parser.add_argument("-i", "--key-file", default=None,
                        help="Path to the SSH key file")
    
    # Command options
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--command", default=None,
                        help="Execute a command on the Norns device")
    group.add_argument("-l", "--lua", default=None,
                        help="Execute Lua code on the Norns device")
    
    # Other options
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Prompt for password if not provided
    if args.password is None and not os.path.exists(args.key_file or ""):
        args.password = getpass.getpass(f"Password for {args.username}@{args.host}: ")
    
    # Run the command
    asyncio.run(handle_command(args))


if __name__ == "__main__":
    main()