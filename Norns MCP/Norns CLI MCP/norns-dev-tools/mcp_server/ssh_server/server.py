"""
SSH Server for Norns MCP.
This server allows SSH access to the Norns device from Claude Code.
"""

import asyncio
import os
import socket
import sys
import threading
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Any

import asyncssh

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("norns_ssh_server")


class NornsSSHServer:
    """SSH Server that provides access to a Norns device."""
    
    def __init__(
        self, 
        host: str = "0.0.0.0", 
        port: int = 22023,
        server_keys_dir: str = None,
        known_hosts_path: str = None
    ):
        """
        Initialize the SSH server.
        
        Args:
            host: The address to bind the server to
            port: The port to listen on
            server_keys_dir: Directory where server keys are stored
            known_hosts_path: Path to known_hosts file
        """
        self.host = host
        self.port = port
        self._running = False
        self._server = None
        
        # Set up server keys directory
        if server_keys_dir is None:
            home_dir = os.path.expanduser("~")
            self.server_keys_dir = os.path.join(home_dir, ".norns-cli", "ssh_keys")
        else:
            self.server_keys_dir = server_keys_dir
            
        # Ensure server keys directory exists
        os.makedirs(self.server_keys_dir, exist_ok=True)
        
        # Server key paths
        self.server_key_paths = {
            "rsa": os.path.join(self.server_keys_dir, "ssh_host_rsa_key"),
            "ed25519": os.path.join(self.server_keys_dir, "ssh_host_ed25519_key")
        }
        
        # Set up known_hosts path
        if known_hosts_path is None:
            self.known_hosts_path = os.path.join(self.server_keys_dir, "known_hosts")
        else:
            self.known_hosts_path = known_hosts_path
            
    async def _start_server(self):
        """Start the SSH server."""
        try:
            # Generate server keys if they don't exist
            server_keys = await self._ensure_server_keys()
            
            # Start the server
            logger.info(f"Starting SSH server on {self.host}:{self.port}")
            self._server = await asyncssh.create_server(
                self._handle_client,
                self.host,
                self.port,
                server_host_keys=server_keys,
                process_factory=self._process_factory,
                encoding="utf-8"
            )
            self._running = True
            logger.info(f"SSH server running on {self.host}:{self.port}")
        except (OSError, asyncssh.Error) as exc:
            logger.error(f"Error starting SSH server: {exc}")
            raise

    async def _ensure_server_keys(self) -> List[asyncssh.SSHKey]:
        """
        Ensure server keys exist and load them.
        
        Returns:
            List of server host keys
        """
        server_keys = []
        
        # Check for RSA key
        if not os.path.exists(self.server_key_paths["rsa"]):
            logger.info("Generating RSA host key")
            rsa_private_key = asyncssh.generate_private_key("ssh-rsa")
            rsa_private_key.write_private_key(self.server_key_paths["rsa"])
            rsa_private_key.write_public_key(f"{self.server_key_paths['rsa']}.pub")
        server_keys.append(self.server_key_paths["rsa"])
        
        # Check for ED25519 key
        if not os.path.exists(self.server_key_paths["ed25519"]):
            logger.info("Generating ED25519 host key")
            ed25519_private_key = asyncssh.generate_private_key("ssh-ed25519")
            ed25519_private_key.write_private_key(self.server_key_paths["ed25519"])
            ed25519_private_key.write_public_key(f"{self.server_key_paths['ed25519']}.pub")
        server_keys.append(self.server_key_paths["ed25519"])
        
        return server_keys

    def _handle_client(self):
        """Handle a new client connection."""
        class NornsSSHServerSession(asyncssh.SSHServerSession):
            def connection_made(self, chan):
                self._chan = chan
                
            def connection_lost(self, exc):
                if exc:
                    logger.warning(f'SSH connection error: {exc}')
                else:
                    logger.info('SSH connection closed')
        
        return NornsSSHServerSession()
    
    def _process_factory(self, process):
        """Create a new shell process."""
        return process
    
    async def start(self):
        """Start the SSH server."""
        await self._start_server()
    
    async def stop(self):
        """Stop the SSH server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._running = False
            logger.info("SSH server stopped")
    
    @property
    def is_running(self):
        """Check if the server is running."""
        return self._running


async def main():
    """Run the SSH server."""
    server = NornsSSHServer()
    await server.start()
    
    # Keep the server running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())