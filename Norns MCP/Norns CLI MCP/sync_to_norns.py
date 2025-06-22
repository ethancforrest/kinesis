#!/usr/bin/env python3
"""
Enhanced Sync script for Norns development.
This script syncs files from the local desktop to Norns and provides various control options.
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("norns_sync")

# Add the Norns tools to Python path
norns_tools_path = "/Users/eforrest/Norns CLI MCP/norns-dev-tools"
if norns_tools_path not in sys.path:
    sys.path.insert(0, norns_tools_path)

# Import Norns tools
from norns_cli.claude_norns import connect_to_norns

async def send_repl_command(norns, command):
    """Send a command to the Norns REPL using direct SSH"""
    if not command.startswith(';'):
        command = ';' + command
    
    result = await norns.run_command(f"echo '{command}' | nc localhost 10111")
    return result

async def sync_file_to_norns(norns, source_path, target_path=None):
    """
    Sync a single file to Norns.
    
    Args:
        norns: Norns connection object
        source_path: Path to source file
        target_path: Path on Norns (if None, will use same name in dust/code)
    """
    source_path = os.path.abspath(source_path)
    
    if not os.path.exists(source_path):
        logger.error(f"Source file not found: {source_path}")
        return False
    
    # If it's a special command
    if os.path.basename(source_path).startswith(';'):
        command = os.path.basename(source_path)
        logger.info(f"Detected REPL command: {command}")
        result = await send_repl_command(norns, command)
        return True
    
    # Determine target path if not specified
    if target_path is None:
        # If it's in a script directory, maintain structure
        if '/lib/' in source_path:
            # Get script name from path (dir before lib)
            path_parts = source_path.split('/')
            lib_index = path_parts.index('lib')
            script_name = path_parts[lib_index-1]
            file_name = path_parts[-1]
            target_path = f"/home/we/dust/code/{script_name}/lib/{file_name}"
        else:
            # Just sync to root of script dir
            script_name = os.path.splitext(os.path.basename(source_path))[0]
            target_path = f"/home/we/dust/code/{script_name}/{os.path.basename(source_path)}"
    
    # Create parent directories
    parent_dir = os.path.dirname(target_path)
    await norns.run_command(f"mkdir -p {parent_dir}")
    
    # Copy the file
    success = await norns.sync_file(source_path, target_path)
    
    if success:
        logger.info(f"✅ Successfully synced {os.path.basename(source_path)} to {target_path}")
    else:
        logger.error(f"❌ Failed to sync {os.path.basename(source_path)}")
    
    return success

async def sync_directory_to_norns(norns, source_dir, target_dir=None):
    """
    Sync a directory to Norns.
    
    Args:
        norns: Norns connection object
        source_dir: Path to source directory
        target_dir: Path on Norns (if None, will use /home/we/dust/code/<dirname>)
    """
    source_dir = os.path.abspath(source_dir)
    
    if not os.path.isdir(source_dir):
        logger.error(f"Source directory not found: {source_dir}")
        return False
    
    # Determine target directory if not specified
    if target_dir is None:
        script_name = os.path.basename(source_dir)
        target_dir = f"/home/we/dust/code/{script_name}"
    
    # Create target directory
    await norns.run_command(f"mkdir -p {target_dir}")
    
    # Sync all files
    results = await norns.sync_directory(source_dir, target_dir)
    
    success_count = sum(1 for success in results.values() if success)
    logger.info(f"✅ Synced {success_count}/{len(results)} files to {target_dir}")
    
    if not all(results.values()):
        # List failures
        failures = [file for file, success in results.items() if not success]
        logger.warning(f"Failed to sync: {', '.join(failures)}")
    
    return all(results.values())

async def norns_system_restart(norns):
    """Restart the entire Norns system"""
    logger.info("Restarting Norns system...")
    
    try:
        # Send reboot command - this will disconnect immediately
        await norns.run_command("sudo reboot")
        logger.info("✅ Restart command sent to Norns")
        return True
    except Exception as e:
        # This will likely fail due to disconnect, which is expected
        logger.info("✅ Norns is rebooting")
        return True

async def norns_script_restart(norns, script_path=None):
    """
    Restart the current script or load a specific script.
    
    Args:
        norns: Norns connection object
        script_path: Path to script to load (if None, will restart current script)
    """
    if script_path:
        # Format the path correctly for Norns
        if script_path.startswith("/home/we/dust/"):
            script_path = script_path[len("/home/we/dust/"):]
        
        # Load the specified script
        logger.info(f"Loading script: {script_path}")
        
        # Try both methods
        try:
            # First try via REPL
            await send_repl_command(norns, f"script.load('{script_path}')")
            logger.info(f"✅ Loaded script via REPL: {script_path}")
            return True
        except Exception as e:
            logger.warning(f"REPL command failed, trying Lua: {e}")
            
            # Then try via Lua
            try:
                result = await norns.run_lua(f"norns.script.load('{script_path}')")
                logger.info(f"✅ Loaded script via Lua: {script_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to load script: {e}")
                return False
    else:
        # Restart current script
        logger.info("Restarting current script")
        
        # Try REPL first
        try:
            await send_repl_command(norns, "restart")
            logger.info("✅ Restarted script via REPL")
            return True
        except Exception as e:
            logger.warning(f"REPL restart failed, trying Lua: {e}")
            
            # Then try via Lua
            try:
                current_script = await norns.get_current_script()
                result = await norns.run_lua("norns.script.load(norns.state.script)")
                logger.info(f"✅ Restarted current script: {current_script}")
                return True
            except Exception as e:
                logger.error(f"Failed to restart script: {e}")
                
                # Try system reset as last resort
                try:
                    await send_repl_command(norns, "reset")
                    logger.info("✅ Reset system via REPL")
                    return True
                except Exception as e:
                    logger.error(f"Failed to reset system: {e}")
                    return False

async def main(args):
    """Main function"""
    # Connect to Norns
    norns = connect_to_norns(host=args.host, password="sleep")
    await norns.connect()
    logger.info(f"Connected to Norns at {args.host}")
    
    success = False
    
    try:
        # Special case: if script_path is "restart", "reboot" or other command
        if args.script_path in ["restart", "reboot", "reset", ";restart", ";reset", ";reboot"]:
            command = args.script_path.lstrip(';')
            
            if command == "restart":
                success = await norns_script_restart(norns)
            elif command == "reboot":
                success = await norns_system_restart(norns)
            elif command == "reset":
                success = await send_repl_command(norns, "reset")
                logger.info("✅ Reset Norns system")
                success = True
            
        # Otherwise, sync files
        elif os.path.isdir(args.script_path):
            # Sync directory
            success = await sync_directory_to_norns(norns, args.script_path)
            
            # Restart if requested
            if args.restart:
                script_name = os.path.basename(args.script_path)
                script_file = f"{script_name}.lua"
                script_path = f"code/{script_name}/{script_file}"
                await norns_script_restart(norns, script_path)
                
        elif os.path.isfile(args.script_path):
            # Sync single file
            success = await sync_file_to_norns(norns, args.script_path)
            
            # Restart if requested
            if args.restart:
                await norns_script_restart(norns)
        else:
            logger.error(f"Path not found: {args.script_path}")
    
    finally:
        # Disconnect from Norns
        await norns.disconnect()
        logger.info("Disconnected from Norns")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Norns sync and control tool")
    parser.add_argument("script_path", help="Path to script/file to sync, or command (restart/reboot/reset)")
    parser.add_argument("--restart", "-r", action="store_true", help="Restart script after syncing")
    parser.add_argument("--host", default="192.168.50.151", help="Norns IP address or hostname")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nSync cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)