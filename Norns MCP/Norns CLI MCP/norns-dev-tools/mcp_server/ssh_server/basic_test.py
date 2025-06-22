#!/usr/bin/env python3
"""
Basic test script for SSH connection to Norns.
"""

import asyncio
import asyncssh
import sys

async def main():
    print("Attempting basic SSH connection to Norns...")
    
    try:
        # Attempt to connect with basic parameters
        conn = await asyncssh.connect(
            host='192.168.50.151',
            port=22,
            username='we',
            password='sleep',  # Using the correct password
            known_hosts=None   # Skip host key checking for this test
        )
        
        print("Connection successful!")
        
        # Run a basic command
        result = await conn.run('uname -a')
        print(f"Command output: {result.stdout}")
        
        # Close the connection
        conn.close()
        await conn.wait_closed()
        
    except (OSError, asyncssh.Error) as exc:
        print(f"SSH connection failed: {exc}")
        return 1
        
if __name__ == '__main__':
    asyncio.run(main())