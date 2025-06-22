# Streamlined Norns Development Environment

A clean, focused development toolkit for Monome Norns with VS Code integration.

## 🚀 Quick Start

**One-command installation:**
```bash
cd norns-dev-tools
./install_norns_dev.sh
```

This will:
- Install all dependencies
- Set up norns device configuration  
- Install VS Code extensions
- Create shell shortcuts
- Open the norns workspace in VS Code

## 🎯 What This Provides

### **Core Development Tools**
- **Unified Configuration**: Single config file for all norns devices
- **Auto-Discovery**: Automatically find norns devices on your network
- **Smart Sync**: Sync files/directories to norns with restart
- **VS Code Integration**: Tasks, shortcuts, and workspace setup
- **SSH Shortcuts**: Easy terminal access to norns

### **VS Code Integration**
- **Workspace**: Pre-configured workspace with your scripts and dev tools
- **Tasks**: Keyboard shortcuts for sync, restart, SSH, maiden
- **Extensions**: Lua support, SSH, Python, Git integration
- **Settings**: Optimized for norns development

### **Shell Shortcuts**
```bash
norns-ssh                    # SSH into norns
norns-sync <file>           # Sync file to norns  
norns-quick-sync <file>     # Sync and restart script
norns-config --list        # List configured devices
norns-maiden               # Open maiden web interface
```

## 📁 Clean Directory Structure

```
norns-dev-tools/
├── vscode/                    # VS Code workspace and settings
│   └── norns-workspace.code-workspace
├── mcp_server/               # MCP integration for Claude Code
├── norns_cli/                # Core CLI tools
├── norns_config.py           # Device configuration manager
├── install_norns_dev.sh      # One-command installer
└── README_STREAMLINED.md     # This file
```

## 🔧 Configuration

Configuration is stored in `~/.norns-cli/config.yml`:

```yaml
devices:
  default:
    name: My Norns
    ip: 192.168.50.151
    user: we
    password: sleep
    code_path: /home/we/dust/code

local:
  scripts_path: ~/Documents/norns-scripts
  auto_restart: true
  auto_discover: true

sync:
  exclude_patterns: ['.git', '.DS_Store', '__pycache__']
  backup_before_sync: false
```

## 🎵 Development Workflow

### **VS Code Workflow**
1. Open norns workspace: `code vscode/norns-workspace.code-workspace`
2. Create/edit scripts in the scripts folder
3. Use `Cmd+Shift+P` → "Tasks: Run Task" → "Sync Script to Norns"
4. Script automatically restarts on norns

### **Command Line Workflow**  
```bash
# Quick sync and restart
norns-quick-sync my_script.lua

# Just sync without restart
norns-sync my_script_directory/

# SSH to debug
norns-ssh

# Open maiden for testing
norns-maiden
```

### **Available VS Code Tasks**
- **Sync Script to Norns**: Sync current file and restart
- **Sync Current Directory to Norns**: Sync entire directory and restart  
- **Restart Norns Script**: Restart without syncing
- **SSH to Norns**: Open SSH terminal
- **Open Maiden**: Open web interface

## 🔍 Device Management

```bash
# Discover norns devices on network
norns-config --discover

# Add a new device
norns-config --add-device studio-norns 192.168.1.100 we

# Test connection
norns-config --test default

# List all devices
norns-config --list
```

## 🔗 Integration with Claude Code

The MCP server provides Claude Code integration:
- Direct SSH access to norns
- File synchronization
- Documentation search
- Git integration

## 🚫 What Was Removed

This streamlined version removes:
- ❌ Multiple demo files (claude_*_demo.py)
- ❌ Duplicate fetch scripts 
- ❌ Multiple project copies (spectrum_splice variants)
- ❌ Test/experimental directories
- ❌ Redundant shell scripts

**Result**: ~80% reduction in files while maintaining all essential functionality.

## 🛠️ Manual Setup (if installer fails)

1. **Install dependencies:**
   ```bash
   pip3 install asyncssh typer rich aiohttp beautifulsoup4 markdown pyyaml netifaces
   ```

2. **Install dev tools:**
   ```bash
   pip3 install -e .
   ```

3. **Set up configuration:**
   ```bash
   python3 norns_config.py --discover
   ```

4. **Open VS Code workspace:**
   ```bash
   code vscode/norns-workspace.code-workspace
   ```

## 📚 Documentation

- **Norns Documentation**: [monome.org/docs/norns](https://monome.org/docs/norns/)
- **Lines Community**: [llllllll.co](https://llllllll.co/)
- **Norns Studies**: [monome.org/docs/norns/studies](https://monome.org/docs/norns/studies/)

## 🤝 Contributing

This toolkit focuses on core development workflow. For feature requests or issues, please ensure they improve the essential development experience rather than adding complexity.

---

**Happy norns coding! 🎵**