#!/usr/bin/env python3
"""
Norns SSH utility for Claude Code.
Provides SSH functionality for connecting to a Norns device.
"""

import asyncio
import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Add parent directory to path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import SSH client
from mcp_server.ssh_server.client import NornsSSHClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("norns_ssh")


class NornsSSH:
    """
    Norns SSH utility class for Claude Code integration.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = 22,
        username: str = "we",
        password: str = "sleep",
        config_path: str = None
    ):
        """
        Initialize the Norns SSH utility.
        
        Args:
            host: Hostname or IP address of the Norns device
            port: SSH port on the Norns device
            username: Username for the Norns device
            password: Password for the Norns device
            config_path: Path to configuration file
        """
        # Use config file or environment variables if values not provided
        self.config = self._load_config(config_path)
        
        # Set connection parameters, prioritizing constructor args
        self.host = host or self.config.get("host") or "norns.local"
        self.port = port or self.config.get("port") or 22
        self.username = username or self.config.get("username") or "we"
        self.password = password or self.config.get("password") or "sleep"
        
        # Initialize client
        self.client = None
    
    def _load_config(self, config_path: str = None) -> Dict:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dict containing configuration
        """
        config = {}
        
        # If config_path not provided, use default locations
        if not config_path:
            # Check in user's home directory
            home_dir = os.path.expanduser("~")
            default_paths = [
                os.path.join(home_dir, ".norns-cli", "config.json"),
                os.path.join(home_dir, ".config", "norns-cli", "config.json")
            ]
            
            for path in default_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        # Load config if file exists
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded config from {config_path}")
            except Exception as e:
                logger.warning(f"Error loading config from {config_path}: {e}")
        
        return config
    
    async def connect(self) -> bool:
        """
        Connect to the Norns device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create client if needed
            if not self.client:
                self.client = NornsSSHClient(
                    host=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            
            # Connect to device
            await self.client.connect()
            logger.info(f"Connected to Norns at {self.host}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Norns at {self.host}: {e}")
            return False
    
    async def disconnect(self) -> None:
        """
        Disconnect from the Norns device.
        """
        if self.client:
            await self.client.disconnect()
            logger.info(f"Disconnected from Norns at {self.host}")
            self.client = None
    
    async def run_command(self, command: str) -> Tuple[str, str, int]:
        """
        Run a shell command on the Norns device.
        
        Args:
            command: The command to run
            
        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        if not self.client:
            await self.connect()
        
        return await self.client.execute_command(command)
    
    async def run_lua(self, lua_code: str) -> Tuple[str, str, int]:
        """
        Run Lua code on the Norns device.
        
        Args:
            lua_code: The Lua code to execute
            
        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        if not self.client:
            await self.connect()
        
        return await self.client.execute_lua(lua_code)
    
    async def sync_script(self, local_path: str, remote_path: str = None) -> bool:
        """
        Sync a script to the Norns device.
        
        Args:
            local_path: Path to local script
            remote_path: Path on Norns (if None, will use same filename in dust/code)
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(local_path):
            logger.error(f"Local file {local_path} does not exist")
            return False
        
        if not self.client:
            await self.connect()
        
        # If no remote path provided, use filename in dust/code
        if not remote_path:
            filename = os.path.basename(local_path)
            remote_path = f"/home/we/dust/code/{filename}"
        
        try:
            # Read local file
            with open(local_path, 'r') as f:
                content = f.read()
            
            # Create remote directory if needed
            remote_dir = os.path.dirname(remote_path)
            await self.client.execute_command(f"mkdir -p {remote_dir}")
            
            # Write content to remote file
            # Escape quotes in content
            content_escaped = content.replace('"', '\\"')
            cmd = f'cat > "{remote_path}" << \'NORNS_EOF\'\n{content}\nNORNS_EOF'
            stdout, stderr, code = await self.client.execute_command(cmd)
            
            if code != 0:
                logger.error(f"Failed to sync script to {remote_path}: {stderr}")
                return False
            
            logger.info(f"Synced script to {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing script to {remote_path}: {e}")
            return False
    
    async def list_scripts(self) -> List[str]:
        """
        List scripts on the Norns device.
        
        Returns:
            List of script names
        """
        if not self.client:
            await self.connect()
        
        stdout, stderr, code = await self.client.execute_command("ls -1 /home/we/dust/code")
        
        if code != 0:
            logger.error(f"Failed to list scripts: {stderr}")
            return []
        
        return [s.strip() for s in stdout.strip().split('\n') if s.strip()]
    
    async def restart_script(self) -> bool:
        """
        Restart the current script on Norns.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            await self.connect()
        
        # Send key command to restart script
        lua_code = 'norns.script.load(norns.state.script)'
        stdout, stderr, code = await self.client.execute_lua(lua_code)
        
        if code != 0:
            logger.error(f"Failed to restart script: {stderr}")
            return False
        
        logger.info("Restarted current script")
        return True
    
    async def get_current_script(self) -> str:
        """
        Get the name of the currently running script.
        
        Returns:
            Name of current script
        """
        if not self.client:
            await self.connect()
        
        lua_code = 'print(norns.state.script)'
        stdout, stderr, code = await self.client.execute_lua(lua_code)
        
        if code != 0:
            logger.error(f"Failed to get current script: {stderr}")
            return ""
        
        return stdout.strip()


async def main():
    """
    Main function for command line use.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Norns SSH utility")
    parser.add_argument("--host", help="Hostname or IP address of the Norns device")
    parser.add_argument("--port", type=int, help="SSH port on the Norns device")
    parser.add_argument("--username", help="Username for the Norns device")
    parser.add_argument("--password", help="Password for the Norns device")
    parser.add_argument("--config", help="Path to configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    cmd_parser = subparsers.add_parser("run", help="Run a command on the Norns device")
    cmd_parser.add_argument("cmd", help="Command to run")
    
    # Run Lua code
    lua_parser = subparsers.add_parser("lua", help="Run Lua code on the Norns device")
    lua_parser.add_argument("code", help="Lua code to run")
    
    # Sync script
    sync_parser = subparsers.add_parser("sync", help="Sync a script to the Norns device")
    sync_parser.add_argument("local_path", help="Path to local script")
    sync_parser.add_argument("--remote-path", help="Path on Norns")
    
    # List scripts
    subparsers.add_parser("list", help="List scripts on the Norns device")
    
    # Restart current script
    subparsers.add_parser("restart", help="Restart the current script")
    
    # Get current script
    subparsers.add_parser("current", help="Get the name of the currently running script")
    
    args = parser.parse_args()
    
    # Create SSH utility
    ssh = NornsSSH(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        config_path=args.config
    )
    
    try:
        # Connect to device
        if not await ssh.connect():
            sys.exit(1)
        
        # Run command
        if args.command == "run":
            stdout, stderr, code = await ssh.run_command(args.cmd)
            print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            sys.exit(code)
        
        # Run Lua code
        elif args.command == "lua":
            stdout, stderr, code = await ssh.run_lua(args.code)
            print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)
            sys.exit(code)
        
        # Sync script
        elif args.command == "sync":
            success = await ssh.sync_script(args.local_path, args.remote_path)
            sys.exit(0 if success else 1)
        
        # List scripts
        elif args.command == "list":
            scripts = await ssh.list_scripts()
            for script in scripts:
                print(script)
            sys.exit(0)
        
        # Restart current script
        elif args.command == "restart":
            success = await ssh.restart_script()
            sys.exit(0 if success else 1)
        
        # Get current script
        elif args.command == "current":
            script = await ssh.get_current_script()
            print(script)
            sys.exit(0)
        
        # No command specified
        else:
            parser.print_help()
            sys.exit(1)
    
    finally:
        # Disconnect
        await ssh.disconnect()


if __name__ == "__main__":
    asyncio.run(main())