#!/usr/bin/env python3
"""
GitHub integration for Norns development.
This module provides functionality for working with GitHub repositories for Norns scripts.
"""

import asyncio
import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

# Add the parent directory to the path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Norns SSH utility
from norns_cli.norns_ssh import NornsSSH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("norns_github")


class NornsGitHub:
    """
    GitHub integration for Norns development.
    Handles cloning repositories, syncing to Norns, and pushing changes back to GitHub.
    """
    
    def __init__(
        self,
        norns_ssh: Optional[NornsSSH] = None,
        host: str = None,
        port: int = 22,
        username: str = "we",
        password: str = "sleep"
    ):
        """
        Initialize the GitHub integration.
        
        Args:
            norns_ssh: Existing NornsSSH instance (optional)
            host: Hostname or IP address of the Norns device
            port: SSH port on the Norns device
            username: Username for the Norns device
            password: Password for the Norns device
        """
        self.ssh = norns_ssh or NornsSSH(host, port, username, password)
        self._connected = False
    
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
    
    def clone_repo(self, repo_url: str, target_dir: str = None) -> bool:
        """
        Clone a GitHub repository.
        
        Args:
            repo_url: URL of the repository to clone
            target_dir: Directory to clone into (defaults to repo name)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # If no target directory provided, use repo name
            if not target_dir:
                repo_name = repo_url.split('/')[-1].replace('.git', '')
                target_dir = os.path.join(os.getcwd(), repo_name)
            
            # Clone the repository
            cmd = ['git', 'clone', repo_url, target_dir]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to clone repository: {result.stderr}")
                return False
            
            logger.info(f"Cloned repository to {target_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return False
    
    async def sync_repo_to_norns(self, local_dir: str, remote_dir: str = None) -> Dict[str, bool]:
        """
        Sync a repository to the Norns device.
        
        Args:
            local_dir: Path to local repository
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
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                
                # Get local and remote paths
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, local_dir)
                remote_path = os.path.join(remote_dir, rel_path)
                
                # Sync file
                try:
                    success = await self.ssh.sync_script(local_path, remote_path)
                    results[rel_path] = success
                except Exception as e:
                    logger.error(f"Error syncing {rel_path}: {e}")
                    results[rel_path] = False
        
        return results
    
    def create_branch(self, repo_dir: str, branch_name: str) -> bool:
        """
        Create a new Git branch.
        
        Args:
            repo_dir: Path to local repository
            branch_name: Name of the branch to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if branch already exists
            cmd = ['git', '-C', repo_dir, 'branch', '--list', branch_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if branch_name in result.stdout:
                logger.info(f"Branch {branch_name} already exists, checking it out")
                checkout_cmd = ['git', '-C', repo_dir, 'checkout', branch_name]
                checkout_result = subprocess.run(checkout_cmd, capture_output=True, text=True)
                return checkout_result.returncode == 0
            
            # Create and checkout branch
            cmd = ['git', '-C', repo_dir, 'checkout', '-b', branch_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to create branch {branch_name}: {result.stderr}")
                return False
            
            logger.info(f"Created and checked out branch {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return False
    
    def stage_changes(self, repo_dir: str, files: List[str] = None) -> bool:
        """
        Stage changes for commit.
        
        Args:
            repo_dir: Path to local repository
            files: List of files to stage (None means all changes)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = ['git', '-C', repo_dir, 'add']
            
            if files:
                cmd.extend(files)
            else:
                cmd.append('.')
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to stage changes: {result.stderr}")
                return False
            
            logger.info(f"Staged changes in {repo_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error staging changes: {e}")
            return False
    
    def commit_changes(self, repo_dir: str, message: str) -> bool:
        """
        Commit staged changes.
        
        Args:
            repo_dir: Path to local repository
            message: Commit message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add a signature to the commit message
            full_message = f"{message}\n\nCommitted via Norns CLI"
            
            cmd = ['git', '-C', repo_dir, 'commit', '-m', full_message]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Check if there's nothing to commit
                if "nothing to commit" in result.stderr or "nothing to commit" in result.stdout:
                    logger.info("No changes to commit")
                    return True
                    
                logger.error(f"Failed to commit changes: {result.stderr}")
                return False
            
            logger.info(f"Committed changes with message: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    def push_changes(self, repo_dir: str, branch: str = None, remote: str = "origin") -> bool:
        """
        Push changes to remote repository.
        
        Args:
            repo_dir: Path to local repository
            branch: Branch to push (None means current branch)
            remote: Remote name (default is origin)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = ['git', '-C', repo_dir, 'push', remote]
            
            if branch:
                cmd.append(branch)
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to push changes: {result.stderr}")
                return False
            
            branch_info = branch or "current branch"
            logger.info(f"Pushed changes to {remote}/{branch_info}")
            return True
            
        except Exception as e:
            logger.error(f"Error pushing changes: {e}")
            return False
    
    def get_current_branch(self, repo_dir: str) -> Optional[str]:
        """
        Get the name of the current branch.
        
        Args:
            repo_dir: Path to local repository
            
        Returns:
            Name of current branch if successful, None otherwise
        """
        try:
            cmd = ['git', '-C', repo_dir, 'branch', '--show-current']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to get current branch: {result.stderr}")
                return None
            
            return result.stdout.strip()
            
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            return None
    
    def get_repo_status(self, repo_dir: str) -> Dict[str, Any]:
        """
        Get the status of the repository.
        
        Args:
            repo_dir: Path to local repository
            
        Returns:
            Dictionary containing repository status
        """
        status = {
            "branch": None,
            "has_changes": False,
            "staged_files": [],
            "unstaged_files": [],
            "untracked_files": []
        }
        
        try:
            # Get current branch
            status["branch"] = self.get_current_branch(repo_dir)
            
            # Check for changes
            cmd = ['git', '-C', repo_dir, 'status', '--porcelain']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to get repository status: {result.stderr}")
                return status
            
            # Parse status output
            if result.stdout.strip():
                status["has_changes"] = True
                
                for line in result.stdout.strip().split('\n'):
                    if not line.strip():
                        continue
                        
                    code = line[:2]
                    file_path = line[3:].strip()
                    
                    if code.startswith('?'):
                        status["untracked_files"].append(file_path)
                    elif code.startswith('M'):
                        status["unstaged_files"].append(file_path)
                    elif code.startswith(' M'):
                        status["unstaged_files"].append(file_path)
                    elif code.startswith('A') or code.startswith('M'):
                        status["staged_files"].append(file_path)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting repository status: {e}")
            return status
        
    def commit_and_push(self, repo_dir: str, message: str, branch: str = None, create_branch: bool = False) -> bool:
        """
        Stage all changes, commit, and push to remote repository.
        
        Args:
            repo_dir: Path to local repository
            message: Commit message
            branch: Branch to push to (None means current branch)
            create_branch: Whether to create the branch if it doesn't exist
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current branch for reference
            current_branch = self.get_current_branch(repo_dir)
            if not current_branch:
                logger.error("Failed to get current branch")
                return False
                
            # Create branch if needed
            if branch and create_branch and branch != current_branch:
                if not self.create_branch(repo_dir, branch):
                    logger.error(f"Failed to create and checkout branch {branch}")
                    return False
            
            # Stage changes
            if not self.stage_changes(repo_dir):
                logger.error("Failed to stage changes")
                return False
            
            # Commit changes
            if not self.commit_changes(repo_dir, message):
                logger.error("Failed to commit changes")
                return False
            
            # Push changes
            push_branch = branch or current_branch
            if not self.push_changes(repo_dir, push_branch):
                logger.error(f"Failed to push to {push_branch}")
                return False
            
            logger.info(f"Successfully committed and pushed changes to {push_branch}")
            return True
            
        except Exception as e:
            logger.error(f"Error in commit and push: {e}")
            return False
        
    async def clone_and_sync(self, repo_url: str, script_name: str = None) -> bool:
        """
        Clone a repository and sync it to the Norns device.
        
        Args:
            repo_url: URL of the repository to clone
            script_name: Name to use for the script on Norns (defaults to repo name)
            
        Returns:
            True if successful, False otherwise
        """
        # Extract repo name
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        # Use provided script name or repo name
        script_name = script_name or repo_name
        
        # Create temp directory
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clone repository
            if not self.clone_repo(repo_url, temp_dir):
                return False
            
            # Sync to Norns
            await self.connect()
            results = await self.sync_repo_to_norns(temp_dir, f"/home/we/dust/code/{script_name}")
            
            # Check if sync was successful
            success = all(results.values())
            
            if success:
                logger.info(f"Successfully cloned and synced {repo_url} to Norns as {script_name}")
            else:
                logger.error(f"Failed to sync some files from {repo_url} to Norns")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in clone and sync: {e}")
            return False
        finally:
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir)


async def main():
    """
    Main function for command line use.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Norns GitHub integration")
    parser.add_argument("--host", help="Hostname or IP address of the Norns device")
    parser.add_argument("--port", type=int, help="SSH port on the Norns device")
    parser.add_argument("--username", help="Username for the Norns device")
    parser.add_argument("--password", help="Password for the Norns device")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Clone repository
    clone_parser = subparsers.add_parser("clone", help="Clone a GitHub repository")
    clone_parser.add_argument("repo_url", help="URL of the repository to clone")
    clone_parser.add_argument("--target-dir", help="Directory to clone into")
    
    # Sync repository to Norns
    sync_parser = subparsers.add_parser("sync", help="Sync a repository to the Norns device")
    sync_parser.add_argument("local_dir", help="Path to local repository")
    sync_parser.add_argument("--remote-dir", help="Path on Norns")
    
    # Clone and sync
    clone_sync_parser = subparsers.add_parser("clone-sync", help="Clone a repository and sync it to the Norns device")
    clone_sync_parser.add_argument("repo_url", help="URL of the repository to clone")
    clone_sync_parser.add_argument("--script-name", help="Name to use for the script on Norns")
    
    args = parser.parse_args()
    
    # Create GitHub integration
    github = NornsGitHub(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password
    )
    
    try:
        # Run command
        if args.command == "clone":
            success = github.clone_repo(args.repo_url, args.target_dir)
            sys.exit(0 if success else 1)
        
        # Sync repository
        elif args.command == "sync":
            await github.connect()
            results = await github.sync_repo_to_norns(args.local_dir, args.remote_dir)
            success = all(results.values())
            sys.exit(0 if success else 1)
        
        # Clone and sync
        elif args.command == "clone-sync":
            success = await github.clone_and_sync(args.repo_url, args.script_name)
            sys.exit(0 if success else 1)
        
        # No command specified
        else:
            parser.print_help()
            sys.exit(1)
    
    finally:
        # Disconnect
        await github.disconnect()


if __name__ == "__main__":
    asyncio.run(main())