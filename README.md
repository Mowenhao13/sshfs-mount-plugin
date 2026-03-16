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
│       │   ├── sshfs-mount-project.md    # /sshfs-mount-project mount specific remote
│       │   ├── sshfs-unmount-project.md  # /sshfs-unmount-project unmount specific remote
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
/plugin marketplace add Mowenhao13/sshfs-mount-plugin
/plugin install sshfs-mount@sshfs-mount-plugin
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

# Mount a specific remote directory
sshfs-mount mount <remote-name>

# Unmount all remote directories
sshfs-mount unmount

# Unmount a specific remote directory
sshfs-mount unmount <remote-name>

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
| `/sshfs-mount-project <name>` | Mount a specific remote directory by name |
| `/sshfs-unmount-project <name>` | Unmount a specific remote directory by name |
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
    ssh_key: ~/.ssh/id_rsa
    ssh_port: 22
    options:
      reconnect: true
      server_alive_interval: 30
```

### Complete Configuration Parameters

#### Top-Level Fields

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| `local_root` | Yes | string | Local base directory for mounting mounts | `~/projects` |
| `remotes` | Yes | array | List of remote host configurations | See below |

#### Remote Host Fields

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| `name` | Yes | string | Unique identifier for this remote |  |
| `host` | Yes | string | SSH host in format `user@hostname` or `user@ip` | `halllo-max@172.18.198.243` |
| `remote_path` | Yes | string | Absolute path on remote server | `/home/halllo-max/projects` |
| `local_path` | Yes | string | Relative path under `local_root` for mount point | |
| `ssh_key` | No | string | Path to SSH private key (default: `~/.ssh/id_rsa`) | `~/.ssh/id_rsa` |
| `ssh_port` | No | integer | SSH port (default: 22) | `55900` |
| `options` | No | object | SSHFS mount options | See below |

#### SSHFS Options Fields

| Option | Type | Default | Description | Recommended Value |
|--------|------|---------|-------------|-------------------|
| `reconnect` | boolean | `false` | Auto-reconnect on connection drop | `true` |
| `server_alive_interval` | integer | `0` | Seconds between keepalive packets. Set to 15-30 for unstable connections | `15` |
| `server_alive_count_max` | integer | `3` | Max missed keepalives before disconnect | `3` |
| `connect_timeout` | integer | `15` | Connection timeout in seconds | `10` |
| `ssh_command` | string | `ssh` | Custom SSH command with options | `ssh -o TCPKeepAlive=yes -o ServerAliveInterval=15` |
| `fsname` | string | - | Filesystem name shown in mount output | |
| `follow_symlinks` | boolean | `false` | Follow symlinks on remote server | `true` |
| `nonempty` | boolean | `false` | Allow mounting over non-empty directories | `true` |
| `large_read` | boolean | `false` | Enable large read operations for better throughput | `true` |
| `max_readahead` | integer | `65536` | Max bytes to read ahead | `65536` |
| `cache_timeout` | integer | `20` | Attribute cache timeout in seconds | `30` |
| `sshfs_debug` | boolean | `false` | Enable SSHFS debug output | `false` |
| `slave` | boolean | `false` | Enable slave mode for SSH communication | `false` |
| `disable_hardlink` | boolean | `false` | Disable hardlink creation | `false` |
| `umask` | string | - | File permission mask | `0022` |
| `uid` | integer | - | Force UID for all files | - |
| `gid` | integer | - | Force GID for all files | - |
| `entry_timeout` | integer | `20` | Timeout for cached directory entries | `30` |
| `attr_timeout` | integer | `20` | Timeout for cached file attributes | `30` |

#### Performance Tuning Recommendations

For **slow/unstable connections**:
```yaml
options:
  reconnect: true
  server_alive_interval: 15
  server_alive_count_max: 3
  connect_timeout: 10
  cache_timeout: 60
  entry_timeout: 60
  attr_timeout: 60
```

For **high-throughput needs**:
```yaml
options:
  large_read: true
  max_readahead: 131072
  ssh_command: ssh -c arcfour -o Compression=no
```

For **frequently changing files**:
```yaml
options:
  cache_timeout: 5
  entry_timeout: 5
  attr_timeout: 5
```

#### Complete Example Configuration

```yaml
local_root: ~/projects

remotes:
  - name: remote-matrix
    host: halllo-max@172.18.198.243
    remote_path: /home/halllo-max/projects
    local_path: remote-matrix
    ssh_key: ~/.ssh/id_rsa
    ssh_port: 22
    options:
      reconnect: true
      server_alive_interval: 15
      server_alive_count_max: 3
      connect_timeout: 10
      ssh_command: ssh -o TCPKeepAlive=yes -o ServerAliveInterval=15 -o ServerAliveCountMax=3
      fsname: remote-matrix
      follow_symlinks: true
      nonempty: true
      large_read: true
      max_readahead: 65536
      cache_timeout: 30

  # With custom SSH port
  - name: remote-lab
    host: ubuntu@172.18.166.57
    remote_path: /home/ubuntu/projects
    local_path: remote-lab
    ssh_key: ~/.ssh/id_rsa
    ssh_port: 55900
    options:
      reconnect: true
      server_alive_interval: 30
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