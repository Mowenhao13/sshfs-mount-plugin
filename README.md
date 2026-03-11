# SSHFS Mount Manager

**A universal SSHFS remote mount management tool, designed for Claude Code Plugin.**

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-purple)](https://code.claude.com)
[![SSHFS](https://img.shields.io/badge/SSHFS-Mount_Generator-blue)](https://github.com/Mowenhao13/sshfs-mount-plugin)

## Features

- 🔧 **Universal Configuration** - Support for any number of remote hosts with independent configurations
- 📋 **Profile Management** - Multiple configuration sets for different scenarios (work/personal)
- 🔄 **Daemon Process** - Automatic detection and reconnection for dropped mounts
- 🤖 **Claude Code Integration** - Convenient mount management via Plugin/Skills
- 📝 **Auto CLAUDE.md Generation** - Automatically generate usage documentation for remote directories

## Project Structure (v2.0 - Plugin Architecture)

```
sshfs-mount/
├── plugins/
│   └── sshfs-mount/               # Plugin main directory
│       ├── .claude-plugin/
│       │   └── plugin.json        # Plugin manifest file
│       ├── skills/
│       │   └── sshfs-mount.skill.md  # Skill definition
│       ├── commands/
│       │   ├── sshfs-status.md       # /sshfs-status status check
│       │   ├── sshfs-mount-all.md    # /sshfs-mount-all mount all
│       │   ├── sshfs-unmount-all.md  # /sshfs-unmount-all unmount all
│       │   ├── sshfs-daemon.md       # /sshfs-daemon daemon management
│       │   └── sshfs-generate-claude-md.md  # /sshfs-generate-claude-md generate CLAUDE.md
│       ├── lib/
│       │   ├── sshfs_mount.py        # Core logic (config management, mount/unmount)
│       │   ├── sshfs_daemon.py       # Daemon process (auto-reconnect)
│       │   └── generate_claude_md.py # CLAUDE.md generator
│       ├── bin/
│       │   ├── sshfs-mount           # CLI entry point
│       │   ├── sshfs-daemon          # Daemon entry point
│       │   └── sshfs                 # Quick mount script
│       └── scripts/
│           ├── install.sh            # Installation script
│           └── create-package.sh     # Packaging script
├── .claude/
│   └── settings.local.json          # Claude Code local settings
├── CHANGELOG.md                     # Changelog
└── README.md                        # This file (English)
```

## Quick Start

### Installation

#### Option 1: Install via Claude Code (Recommended)

```bash
# Run in Claude Code
/plugins install /Users/halllo/.claude/plugins/cache/local-plugins/sshfs-mount
```

#### Option 2: Run Installation Script (Standalone CLI)

```bash
# Clone or download the project
cd sshfs-mount/plugins/sshfs-mount

# Run installation script
./scripts/install.sh
```

After installation, global commands are created:
- `sshfs-mount` - Main CLI tool
- `sshfs-daemon` - Daemon management

### First Time Usage

```bash
# Run initialization wizard
sshfs-mount init
```

The initialization will:
1. Create config directory `~/.config/sshfs-mount-plugin/`
2. Run interactive wizard to configure remote hosts
3. Parse existing SSH config for auto-fill

### Basic Commands

```bash
# Check mount status
sshfs-mount status

# Mount all remote directories
sshfs-mount mount

# Unmount all remote directories
sshfs-mount unmount

# Start daemon (auto-reconnect)
sshfs-daemon start

# Check daemon status
sshfs-daemon status
```

## Claude Code Plugin Integration

After installing the plugin, restart Claude Code to use the following features:

### Commands

| Command | Function |
|---------|----------|
| `/sshfs-status` | Check mount status of all remote directories |
| `/sshfs-mount-all` | Mount all remote directories |
| `/sshfs-unmount-all` | Unmount all remote directories |
| `/sshfs-daemon start` | Start daemon process |
| `/sshfs-daemon stop` | Stop daemon process |
| `/sshfs-daemon status` | Check daemon status |
| `/sshfs-generate-claude-md` | Generate CLAUDE.md for mounted directories |

### Skill

Use `/sshfs-mount` skill for interactive operations including:
- Mount/unmount remote directories
- Daemon management
- Profile switching
- Configuration management

## Configuration Files

### File Locations

- **Main Config**: `~/.config/sshfs-mount-plugin/config.yaml`
- **Profiles**: `~/.config/sshfs-mount-plugin/profiles/`
- **Daemon Log**: `~/.config/sshfs-mount-plugin/daemon.log`

### Configuration Format

```yaml
local_root: ~/projects

remotes:
  - name: remote-machine1
    host: halllo-max@172.18.198.243
    remote_path: /home/halllo-max/projects
    local_path: remote-machine1
    ssh_key: ~/.ssh/id_rsa_mac
    ssh_port: 22
    options:
      reconnect: true
      server_alive_interval: 30

  - name: remote-machine2
    host: ubuntu@172.18.166.57:55900
    remote_path: /home/ubuntu/projects
    local_path: remote-machine2
    ssh_key: ~/.ssh/id_rsa_mac
    ssh_port: 55900
```

### Profile Example

```yaml
# ~/.config/sshfs-mount-plugin/profiles/work.yaml
name: work
description: Work development environment

local_root: ~/work-projects

remotes:
  - name: remote-prod
    host: user@prod-server.example.com
    remote_path: ~/projects
    local_path: remote-prod
```

## Profile Management

```bash
# List all profiles
sshfs-mount profile list

# Switch to work profile
sshfs-mount profile switch work
```

## Daemon Process

The daemon checks mount status every 30 seconds (configurable) and automatically reconnects dropped remote directories.

```bash
# Start daemon
sshfs-daemon start

# Specify check interval (seconds)
sshfs-daemon start 60

# Stop daemon
sshfs-daemon stop

# Check status and logs
sshfs-daemon status
tail -f ~/.config/sshfs-mount-plugin/daemon.log
```

## Dependencies

- Python 3.6+
- sshfs
- PyYAML

### Install Dependencies

```bash
# macOS
brew install sshfs
pip3 install pyyaml

# Ubuntu/Debian
sudo apt-get install sshfs python3-yaml

# Arch Linux
sudo pacman -S sshfs python-yaml
```

## Troubleshooting

### Mount Failures

Check if SSH key exists and has correct permissions:
```bash
ls -la ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
```

### Connection Dropped

Check network connection and SSH service:
```bash
ssh user@host  # Test SSH connection
```

### View Logs

```bash
# View daemon logs
tail -f ~/.config/sshfs-mount-plugin/daemon.log
```

## Supported Systems

- macOS
- Linux

> **Note**: Windows version is not yet available. Contributions welcome!

## License

MIT
