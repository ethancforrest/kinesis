#!/usr/bin/env python3
"""
Test script to verify connection to a Norns device.
"""

import asyncio
import os
import sys

# Add the root directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, parent_dir)

# Import the client directly since we're in the same directory
from client import NornsSSHClient

async def test_connection():
    print("Attempting to connect to Norns device...")
    
    # Create client with your Norns device IP address
    client = NornsSSHClient(
        host="192.168.50.151",  # Using the detected IP address instead of norns.local
        username="we",          # Default Norns username
        # Using the correct password
        password="sleep"        # The password for the Norns device
    )
    
    try:
        # Try to connect
        print(f"Connecting to {client.host}...")
        await client.connect()
        print(f"Successfully connected to {client.host}")
        
        # Run a simple command
        print("Running 'uname -a' command...")
        stdout, stderr, return_code = await client.execute_command("uname -a")
        
        print("\nCommand output:")
        print(f"STDOUT: {stdout}")
        if stderr:
            print(f"STDERR: {stderr}")
        print(f"Return code: {return_code}")
        
        # Try a Lua command
        print("\nRunning Lua test...")
        lua_stdout, lua_stderr, lua_rc = await client.execute_lua('print("Hello from Norns!")')
        
        print("Lua output:")
        print(f"STDOUT: {lua_stdout}")
        if lua_stderr:
            print(f"STDERR: {lua_stderr}")
        print(f"Return code: {lua_rc}")
        
    except Exception as e:
        print(f"Error connecting to Norns: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Disconnect if connected
        if client._connection:
            print("Disconnecting...")
            await client.disconnect()
            print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(test_connection())