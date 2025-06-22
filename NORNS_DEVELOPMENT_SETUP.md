# Norns Development Setup Guide

Complete setup for efficient Norns script development with instant sync, VS Code integration, and GitHub workflow.

## 🚀 Quick Start

### Prerequisites
- macOS with Homebrew
- Python 3.8+
- VS Code (recommended)
- Norns device on your network

### One-Time Setup

1. **Clone this repository:**
   ```bash
   git clone https://github.com/ethancforrest/kinesis.git
   cd kinesis
   ```

2. **Install Norns development tools:**
   ```bash
   cd "Norns MCP/Norns CLI MCP/norns-dev-tools"
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

3. **Update your Norns IP address:**
   Edit `Norns MCP/Norns CLI MCP/quick_sync.py` and change:
   ```python
   DEFAULT_HOST = "192.168.50.151"  # Your Norns IP here
   ```

4. **Open VS Code in the project directory:**
   ```bash
   cd "/Users/yourusername/path/to/kinesis"
   code .
   ```

## 🎯 Development Workflow

### Option 1: VS Code (Recommended)
- **⌘+Shift+S** - Sync current file to Norns
- **⌘+Shift+R** - Sync current file + restart script
- **⌘+Shift+D** - Sync entire directory + restart

### Option 2: Command Line
```bash
# Quick sync single file
python3 "Norns MCP/Norns CLI MCP/quick_sync.py" my_script.lua

# Sync with restart
python3 "Norns MCP/Norns CLI MCP/quick_sync.py" my_script.lua --restart

# Sync entire project
python3 "Norns MCP/Norns CLI MCP/quick_sync.py" ./my_project/ --restart
```

### Option 3: Advanced Features
```bash
cd "Norns MCP/Norns CLI MCP/norns-dev-tools"
source venv/bin/activate

# Use full-featured sync tool
python ../sync_to_norns.py my_script.lua --restart

# Send REPL commands
python ../sync_to_norns.py "restart"
python ../sync_to_norns.py "reboot"
```

## 📁 Project Structure

```
kinesis/
├── .vscode/                    # VS Code configuration
│   ├── tasks.json             # Build tasks for sync
│   └── keybindings.json       # Keyboard shortcuts
├── Norns MCP/                 # Development tools
│   └── Norns CLI MCP/
│       ├── quick_sync.py      # Streamlined sync script
│       ├── sync_to_norns.py   # Full-featured sync
│       └── norns-dev-tools/   # Core package
├── kinesis/                   # Your Norns scripts
├── meadowphysics/
├── panharmonium/
└── [other script projects]
```

## 🔧 Configuration

### Norns Network Setup
1. On your Norns: **SYSTEM > WIFI**
2. Note the IP address (e.g., 192.168.1.100)
3. Update `DEFAULT_HOST` in `quick_sync.py`

### VS Code Extensions (Recommended)
- Lua Language Server
- GitLens
- Remote - SSH (for direct Norns editing)

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test connection
ping 192.168.50.151  # Your Norns IP

# Test SSH
ssh we@192.168.50.151  # Password: sleep
```

### Package Issues
```bash
# Reinstall tools
cd "Norns MCP/Norns CLI MCP/norns-dev-tools"
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Sync Failures
- Check Norns is powered on and connected
- Verify IP address is correct
- Ensure you're on the same network
- Try restarting Norns: **SYSTEM > RESTART**

## 🎵 Features

### ✅ Instant Sync
- Sub-3-second file transfers
- Automatic directory structure
- Smart path detection

### ✅ VS Code Integration  
- One-click sync and restart
- Keyboard shortcuts
- Integrated terminal output

### ✅ Git Workflow
- Version control ready
- Automatic .gitignore
- GitHub integration

### ✅ Documentation Access
- Built-in API search
- Engine documentation
- Code examples

### ✅ Remote Control
- Script restart commands
- System reboot capability
- REPL integration

## 📚 Additional Resources

- [Norns Documentation](https://monome.org/docs/norns/)
- [Scripting Guide](https://monome.org/docs/norns/scripting/)
- [Community Scripts](https://norns.community/)

## 🤝 Contributing

This setup is designed to be shared and improved. Feel free to:
- Submit issues for bugs
- Propose workflow improvements
- Share your script projects

---

**Happy Norns scripting!** 🎛️