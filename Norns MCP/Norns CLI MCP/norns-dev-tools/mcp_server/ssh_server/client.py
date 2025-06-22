"""
SSH Client for connecting to a Norns device.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Optional, List, Tuple, Any

import asyncssh

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("norns_ssh_client")


class NornsSSHClient:
    """SSH Client for connecting to a Norns device."""
    
    def __init__(
        self,
        host: str = "norns.local",
        port: int = 22,
        username: str = "we",
        password: str = None,
        key_file: str = None,
        known_hosts_path: str = None
    ):
        """
        Initialize the SSH client.
        
        Args:
            host: The Norns hostname or IP address
            port: The SSH port on the Norns device
            username: The username for the Norns device
            password: The password for the Norns device
            key_file: Path to the SSH key file to use
            known_hosts_path: Path to known_hosts file
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        
        # Set up key file path if not provided
        if self.key_file is None:
            home_dir = os.path.expanduser("~")
            self.key_file = os.path.join(home_dir, ".ssh", "id_rsa")
        
        # Set up known_hosts path
        if known_hosts_path is None:
            home_dir = os.path.expanduser("~")
            self.known_hosts_path = os.path.join(home_dir, ".norns-cli", "ssh_keys", "known_hosts")
        else:
            self.known_hosts_path = known_hosts_path
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.known_hosts_path), exist_ok=True)
        
        self._connection = None
    
    async def connect(self) -> asyncssh.SSHClientConnection:
        """
        Connect to the Norns device.
        
        Returns:
            SSHClientConnection: The SSH connection
        """
        try:
            # Connect to the SSH server
            logger.info(f"Connecting to {self.host}:{self.port} as {self.username}")
            
            connect_kwargs = {
                "host": self.host,
                "port": self.port,
                "username": self.username,
                "known_hosts": self.known_hosts_path if os.path.exists(self.known_hosts_path) else None,
            }
            
            # Add password if provided
            if self.password:
                connect_kwargs["password"] = self.password
            
            # Add key file if it exists
            if os.path.exists(self.key_file):
                connect_kwargs["client_keys"] = [self.key_file]
            
            # Connect to the server
            self._connection = await asyncssh.connect(**connect_kwargs)
            logger.info(f"Connected to {self.host}")
            
            return self._connection
        except (OSError, asyncssh.Error) as exc:
            logger.error(f"Error connecting to {self.host}: {exc}")
            raise
    
    async def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        Execute a command on the Norns device.
        
        Args:
            command: The command to execute
            
        Returns:
            Tuple containing stdout, stderr, and return code
        """
        if not self._connection:
            await self.connect()
        
        # Execute the command
        logger.info(f"Executing command: {command}")
        result = await self._connection.run(command)
        
        return result.stdout, result.stderr, result.exit_status
    
    async def execute_lua(self, lua_code: str) -> Tuple[str, str, int]:
        """
        Execute Lua code on the Norns device.
        
        Args:
            lua_code: The Lua code to execute
            
        Returns:
            Tuple containing stdout, stderr, and return code
        """
        # Quote the Lua code for the command line
        quoted_code = lua_code.replace("'", "\\'")
        command = f"lua -e '{quoted_code}'"
        
        return await self.execute_command(command)
    
    async def disconnect(self):
        """Disconnect from the Norns device."""
        if self._connection:
            self._connection.close()
            await self._connection.wait_closed()
            logger.info(f"Disconnected from {self.host}")
            self._connection = None


async def main():
    """Run the SSH client."""
    # Example usage
    client = NornsSSHClient()
    
    try:
        await client.connect()
        stdout, stderr, return_code = await client.execute_command("ls -la")
        print(f"STDOUT: {stdout}")
        if stderr:
            print(f"STDERR: {stderr}")
        print(f"Return code: {return_code}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())