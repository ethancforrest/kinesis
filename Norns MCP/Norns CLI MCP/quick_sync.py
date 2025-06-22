#!/usr/bin/env python3
"""
Quick Sync - Streamlined Norns development workflow
Usage: python quick_sync.py <file_or_directory> [--restart]
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add norns-dev-tools to path
sys.path.insert(0, "/Users/eforrest/Norns scripts/Norns MCP/Norns CLI MCP/norns-dev-tools")

from norns_cli.claude_norns import connect_to_norns

# Default Norns configuration
DEFAULT_HOST = "192.168.50.151"  # Update with your Norns IP
DEFAULT_PASSWORD = "sleep"

async def quick_sync(file_path, restart=False, host=DEFAULT_HOST):
    """Quick sync with minimal setup"""
    print(f"🔄 Syncing {file_path} to Norns at {host}")
    
    # Connect to Norns
    norns = connect_to_norns(host=host, password=DEFAULT_PASSWORD)
    
    try:
        await norns.connect()
        print("✅ Connected to Norns")
        
        if os.path.isfile(file_path):
            # Sync single file
            success = await norns.sync_file(file_path, None)  # Auto-detect target path
            if success:
                print(f"✅ Synced {os.path.basename(file_path)}")
            else:
                print(f"❌ Failed to sync {file_path}")
                return False
                
        elif os.path.isdir(file_path):
            # Sync directory
            results = await norns.sync_directory(file_path, None)  # Auto-detect target
            success_count = sum(1 for s in results.values() if s)
            print(f"✅ Synced {success_count}/{len(results)} files")
            
            if not all(results.values()):
                print("⚠️  Some files failed to sync")
        
        # Restart script if requested
        if restart:
            print("🔄 Restarting script...")
            await norns.run_lua("norns.script.load(norns.state.script)")
            print("✅ Script restarted")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await norns.disconnect()
        
    return True

def main():
    parser = argparse.ArgumentParser(description="Quick sync to Norns")
    parser.add_argument("path", help="File or directory to sync")
    parser.add_argument("--restart", "-r", action="store_true", help="Restart script after sync")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Norns IP address")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"❌ Path not found: {args.path}")
        sys.exit(1)
    
    try:
        success = asyncio.run(quick_sync(args.path, args.restart, args.host))
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Sync cancelled")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()