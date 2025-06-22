#!/usr/bin/env python3
"""
Claude Code integration for Norns.
Makes it easy to connect to Norns from Claude Code in any directory.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

# Add the parent directory to the path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Norns utilities
from norns_cli.norns_ssh import NornsSSH
from norns_cli.docs_manager import NornsDocsManager, get_docs_manager


class ClaudeNorns:
    """
    Claude Code integration for Norns.
    This class provides a simple interface for interacting with Norns from Claude Code.
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
        Initialize the Claude Norns integration.
        
        Args:
            host: Hostname or IP address of the Norns device
            port: SSH port on the Norns device
            username: Username for the Norns device
            password: Password for the Norns device
            config_path: Path to configuration file
        """
        self.ssh = NornsSSH(host, port, username, password, config_path)
        self._connected = False
        
        # Initialize documentation manager
        self.docs = get_docs_manager()
    
    async def connect(self) -> bool:
        """
        Connect to the Norns device.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            self._connected = await self.ssh.connect()
        return self._connected
    
    async def disconnect(self) -> None:
        """
        Disconnect from the Norns device.
        """
        if self._connected:
            await self.ssh.disconnect()
            self._connected = False
    
    async def run_command(self, command: str) -> str:
        """
        Run a shell command on the Norns device.
        
        Args:
            command: Command to run
            
        Returns:
            Command output (stdout)
        """
        if not self._connected:
            await self.connect()
        
        stdout, stderr, _ = await self.ssh.run_command(command)
        return stdout
    
    async def run_lua(self, lua_code: str) -> str:
        """
        Run Lua code on the Norns device.
        
        Args:
            lua_code: Lua code to execute
            
        Returns:
            Lua output (stdout)
        """
        if not self._connected:
            await self.connect()
        
        stdout, stderr, _ = await self.ssh.run_lua(lua_code)
        return stdout
    
    async def list_scripts(self) -> List[str]:
        """
        List scripts on the Norns device.
        
        Returns:
            List of script names
        """
        if not self._connected:
            await self.connect()
        
        return await self.ssh.list_scripts()
    
    async def get_current_script(self) -> str:
        """
        Get the name of the currently running script.
        
        Returns:
            Name of current script
        """
        if not self._connected:
            await self.connect()
        
        return await self.ssh.get_current_script()
    
    async def restart_script(self) -> bool:
        """
        Restart the current script.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            await self.connect()
        
        return await self.ssh.restart_script()
    
    async def sync_file(self, local_path: str, remote_path: str = None) -> bool:
        """
        Sync a file to the Norns device.
        
        Args:
            local_path: Path to local file
            remote_path: Path on Norns (if None, will use same filename in dust/code)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            await self.connect()
        
        return await self.ssh.sync_script(local_path, remote_path)
    
    async def sync_directory(self, local_dir: str, remote_dir: str = None) -> Dict[str, bool]:
        """
        Sync a directory to the Norns device.
        
        Args:
            local_dir: Path to local directory
            remote_dir: Path on Norns (if None, will use directory name in dust/code)
            
        Returns:
            Dictionary of {filename: success}
        """
        if not self._connected:
            await self.connect()
        
        results = {}
        
        # Get base remote directory
        if not remote_dir:
            dir_name = os.path.basename(os.path.normpath(local_dir))
            remote_dir = f"/home/we/dust/code/{dir_name}"
        
        # Create remote directory
        await self.ssh.run_command(f"mkdir -p {remote_dir}")
        
        # Sync each file
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                
                # Get local and remote paths
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, local_dir)
                remote_path = os.path.join(remote_dir, rel_path)
                
                # Sync file
                success = await self.ssh.sync_script(local_path, remote_path)
                results[rel_path] = success
        
        return results
    
    # Documentation methods
    
    async def sync_docs(self, force: bool = False) -> bool:
        """
        Synchronize Norns documentation from monome.org.
        
        Args:
            force: Force refresh even if cache is recent
            
        Returns:
            True if successful, False otherwise
        """
        return await self.docs.sync_documentation(force)
    
    def search_docs(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Norns documentation.
        
        Args:
            query: Search query
            category: Optional category to search
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        return self.docs.search(query, category, limit)
    
    def search_api(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Norns API documentation.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching API functions
        """
        return self.docs.search_api(query, limit)
    
    def search_engines(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Norns engine documentation.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching engines
        """
        return self.docs.search_engines(query, limit)
    
    def get_doc(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document details if found, None otherwise
        """
        return self.docs.get_document(doc_id)
    
    def get_api_function(self, func_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an API function by ID.
        
        Args:
            func_id: Function ID
            
        Returns:
            Function details if found, None otherwise
        """
        return self.docs.get_api_function(func_id)
    
    def get_engine(self, engine_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an engine by ID.
        
        Args:
            engine_id: Engine ID
            
        Returns:
            Engine details if found, None otherwise
        """
        return self.docs.get_engine(engine_id)
    
    def get_docs_stats(self) -> Dict[str, Any]:
        """
        Get documentation statistics.
        
        Returns:
            Documentation statistics
        """
        return self.docs.get_stats()
    
    async def load_script(self, script_name: str) -> bool:
        """
        Load a script on the Norns device.
        
        Args:
            script_name: Name of script to load
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            await self.connect()
        
        # Check if script exists
        scripts = await self.ssh.list_scripts()
        if script_name not in scripts:
            print(f"Script '{script_name}' not found on Norns")
            return False
        
        # Load script
        lua_code = f'norns.script.load("code/{script_name}/filename.lua")'
        stdout, stderr, code = await self.ssh.run_lua(lua_code)
        
        return code == 0
    
    async def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information from the Norns device.
        
        Returns:
            Dictionary of system information
        """
        if not self._connected:
            await self.connect()
        
        info = {}
        
        # Get OS version
        stdout, _, _ = await self.ssh.run_command("cat /etc/os-release | grep PRETTY_NAME")
        if stdout:
            info['os_version'] = stdout.split('=')[1].strip().strip('"')
        
        # Get norns version
        stdout, _, _ = await self.ssh.run_lua('print(norns.version.norns)')
        if stdout:
            info['norns_version'] = stdout.strip()
        
        # Get current script
        info['current_script'] = await self.ssh.get_current_script()
        
        # Get free disk space
        stdout, _, _ = await self.ssh.run_command("df -h / | tail -1 | awk '{print $4}'")
        if stdout:
            info['free_disk'] = stdout.strip()
        
        # Get free memory
        stdout, _, _ = await self.ssh.run_command("free -m | grep Mem | awk '{print $4}'")
        if stdout:
            info['free_memory'] = f"{stdout.strip()} MB"
        
        return info


# Function to create a Norns client in Claude Code
def connect_to_norns(
    host: str = None,
    port: int = 22,
    username: str = "we",
    password: str = "sleep"
) -> ClaudeNorns:
    """
    Create a Norns client for use in Claude Code.
    
    Args:
        host: Hostname or IP address of the Norns device
        port: SSH port on the Norns device
        username: Username for the Norns device
        password: Password for the Norns device
        
    Returns:
        ClaudeNorns object
    """
    return ClaudeNorns(host, port, username, password)


# Example usage in Claude Code
async def example():
    # Connect to Norns (use the detected IP address)
    norns = connect_to_norns(host="192.168.50.151")
    
    # Get system info
    info = await norns.get_system_info()
    print("Norns System Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # List scripts
    scripts = await norns.list_scripts()
    print("\nScripts on Norns:")
    for script in scripts:
        print(f"  {script}")
    
    # Run a Lua command
    lua_output = await norns.run_lua('print(os.date())')
    print(f"\nCurrent Norns date: {lua_output}")
    
    # Disconnect
    await norns.disconnect()


if __name__ == "__main__":
    asyncio.run(example())