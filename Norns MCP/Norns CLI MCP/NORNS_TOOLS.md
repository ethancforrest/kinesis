# Norns Tools for Claude

This document describes the enhanced tools for working with Norns devices from Claude Code.

## Quick Start

Use the `norns.sh` helper script for common tasks:

```bash
# Sync a file to Norns
./norns.sh sync /path/to/your/script.lua

# Sync a file and restart the script
./norns.sh push /path/to/your/script.lua

# Restart current script
./norns.sh restart

# Reboot Norns system
./norns.sh reboot

# Reset Norns system
./norns.sh reset
```

## Enhanced Sync Script

The `sync_to_norns.py` script has been improved to handle:

1. Syncing individual files with proper path handling
2. Syncing entire directories
3. Sending REPL commands directly to Norns
4. Loading specific scripts
5. Restarting the current script
6. Rebooting the Norns system

### Usage

```bash
# Basic syncing
python3 sync_to_norns.py /path/to/your/script.lua

# Sync and restart
python3 sync_to_norns.py /path/to/your/script.lua --restart

# Send a restart command
python3 sync_to_norns.py restart

# Reboot the system
python3 sync_to_norns.py reboot

# Specify a different Norns IP address
python3 sync_to_norns.py /path/to/your/script.lua --host 192.168.1.100
```

## Improvements

The tools now include:

1. **Better path handling**: Correctly syncs files to appropriate locations on Norns
2. **Multiple restart methods**: Tries several approaches to restart scripts
3. **REPL integration**: Sends commands directly to the Norns REPL when needed
4. **Improved error handling**: More robust error recovery
5. **Better logging**: Clearer status messages
6. **Helper script**: Simple shell script for common tasks

## Troubleshooting

If you encounter issues:

1. **Connection problems**: Verify your Norns IP address
2. **Script not restarting**: Try rebooting the Norns
3. **Sync failures**: Use the `--verbose` flag for more detailed logs

```bash
python3 sync_to_norns.py /path/to/your/script.lua --verbose
```

## Development Workflow

1. Make changes to your script in Claude Code
2. Sync the file to Norns: `./norns.sh push /path/to/your/script.lua`
3. Test on Norns
4. Repeat

For larger projects, sync entire directories:

```bash
./norns.sh push /path/to/your/script/directory
```

## New Features Coming Soon

- Direct file editing on Norns
- Real-time script monitoring
- Parameter editing from Claude
- Audio recording and playback