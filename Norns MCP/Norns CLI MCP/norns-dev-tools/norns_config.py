#!/usr/bin/env python3
"""
Norns Development Configuration Manager
Simplified configuration for norns development workflow
"""

import os
import yaml
from pathlib import Path
import subprocess
import socket

class NornsConfig:
    def __init__(self):
        self.config_dir = Path.home() / ".norns-cli"
        self.config_file = self.config_dir / "config.yml"
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        default_config = {
            'devices': {
                'default': {
                    'name': 'My Norns',
                    'ip': '192.168.50.151',
                    'user': 'we',
                    'password': 'sleep',
                    'code_path': '/home/we/dust/code'
                }
            },
            'local': {
                'scripts_path': str(Path.home() / "Documents" / "norns-scripts"),
                'editor': 'code',
                'auto_restart': True,
                'auto_discover': True
            },
            'sync': {
                'exclude_patterns': ['.git', '.DS_Store', '__pycache__', '*.pyc'],
                'backup_before_sync': False
            }
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def get_device(self, name='default'):
        """Get device configuration"""
        return self.config['devices'].get(name, self.config['devices']['default'])
    
    def add_device(self, name, ip, user='we', password='sleep'):
        """Add a new norns device"""
        self.config['devices'][name] = {
            'name': name,
            'ip': ip,
            'user': user,
            'password': password,
            'code_path': '/home/we/dust/code'
        }
        self.save_config()
    
    def discover_devices(self):
        """Auto-discover norns devices on network"""
        print("🔍 Scanning for norns devices...")
        
        # Get local network range
        try:
            import netifaces
            gateways = netifaces.gateways()
            default_gateway = gateways['default'][netifaces.AF_INET][0]
            network_base = '.'.join(default_gateway.split('.')[:-1])
        except:
            # Fallback to common network ranges
            network_base = "192.168.1"
        
        discovered = []
        
        # Check common norns ports and IPs
        common_ips = [
            f"{network_base}.{i}" for i in range(100, 200)
        ]
        
        for ip in common_ips:
            if self.is_norns_device(ip):
                discovered.append(ip)
                print(f"✅ Found norns at {ip}")
        
        return discovered
    
    def is_norns_device(self, ip, timeout=1):
        """Check if IP is a norns device"""
        try:
            # Check if SSH port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 22))
            sock.close()
            
            if result == 0:
                # Try to connect and check for norns-specific files
                try:
                    cmd = f"ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no we@{ip} 'test -d /home/we/dust && echo norns'"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                    return 'norns' in result.stdout
                except:
                    return False
        except:
            pass
        
        return False
    
    def test_connection(self, device_name='default'):
        """Test connection to norns device"""
        device = self.get_device(device_name)
        ip = device['ip']
        user = device['user']
        
        print(f"🔌 Testing connection to {device['name']} ({ip})...")
        
        try:
            cmd = f"ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{ip} 'echo Connection successful'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Successfully connected to {device['name']}")
                return True
            else:
                print(f"❌ Failed to connect: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Connection timeout to {ip}")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

def main():
    """CLI for norns configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Norns Development Configuration")
    parser.add_argument('--discover', action='store_true', help='Discover norns devices on network')
    parser.add_argument('--test', help='Test connection to device (default: default)')
    parser.add_argument('--add-device', nargs=3, metavar=('NAME', 'IP', 'USER'), 
                       help='Add new device: name ip user')
    parser.add_argument('--list', action='store_true', help='List configured devices')
    
    args = parser.parse_args()
    config = NornsConfig()
    
    if args.discover:
        devices = config.discover_devices()
        if devices:
            print(f"\n📱 Found {len(devices)} norns device(s)")
            for ip in devices:
                config.add_device(f"norns-{ip.split('.')[-1]}", ip)
        else:
            print("🔍 No norns devices found")
    
    elif args.test:
        config.test_connection(args.test)
    
    elif args.add_device:
        name, ip, user = args.add_device
        config.add_device(name, ip, user)
        print(f"✅ Added device '{name}' at {ip}")
    
    elif args.list:
        print("📱 Configured norns devices:")
        for name, device in config.config['devices'].items():
            print(f"  {name}: {device['name']} ({device['ip']})")
    
    else:
        print("Norns configuration file:", config.config_file)
        print("Use --help for available commands")

if __name__ == "__main__":
    main()