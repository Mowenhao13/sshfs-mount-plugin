#!/usr/bin/env python3
"""
SSHFS Mount Manager - Universal remote directory mounting tool
"""

import os
import sys
import subprocess
import yaml
import argparse
import shutil
from pathlib import Path
from typing import Optional

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "sshfs-mounts"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
PROFILES_DIR = CONFIG_DIR / "profiles"
ACTIVE_PROFILE_FILE = CONFIG_DIR / "active-profile"
DAEMON_LOG = CONFIG_DIR / "daemon.log"

# Default configuration
DEFAULT_CONFIG = {
    "local_root": "~/projects",
    "remotes": []
}


def expand_path(path: str) -> Path:
    """Expand ~ and environment variables in path."""
    return Path(os.path.expanduser(os.path.expandvars(path)))


def load_config(profile: Optional[str] = None) -> dict:
    """Load configuration from YAML file."""
    if profile:
        config_file = PROFILES_DIR / f"{profile}.yaml"
        if not config_file.exists():
            print(f"Error: Profile '{profile}' not found at {config_file}")
            sys.exit(1)
        config_path = config_file
    else:
        # Check for active profile
        if ACTIVE_PROFILE_FILE.exists():
            active_profile = ACTIVE_PROFILE_FILE.read_text().strip()
            profile_config = PROFILES_DIR / f"{active_profile}.yaml"
            if profile_config.exists():
                config_path = profile_config
            else:
                config_path = CONFIG_FILE
        else:
            config_path = CONFIG_FILE

    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or DEFAULT_CONFIG.copy()

    # Set defaults if missing
    if "local_root" not in config:
        config["local_root"] = "~/projects"

    return config


def save_config(config: dict, profile: Optional[str] = None) -> None:
    """Save configuration to YAML file."""
    if profile:
        config_file = PROFILES_DIR / f"{profile}.yaml"
    else:
        config_file = CONFIG_FILE

    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def parse_ssh_host(host: str) -> tuple:
    """Parse SSH host string (user@host or user@host:port)."""
    port = 22 # default port for ssh
    user_host = host

    if ':' in host:
        parts = host.rsplit(':', 1)
        user_host = parts[0]
        try:
            port = int(parts[1])
        except ValueError:
            pass

    if '@' in user_host:
        user, hostname = user_host.split('@', 1)
    else:
        user = os.getenv("USER", "root")
        hostname = user_host

    return user, hostname, port


def build_sshfs_command(remote: dict, local_root: Path) -> tuple:
    """Build sshfs mount command for a remote configuration."""
    name = remote.get("name", "unknown")
    host = remote.get("host", "")
    remote_path = remote.get("remote_path", "~")
    local_path = remote.get("local_path", name)
    ssh_key = remote.get("ssh_key", "~/.ssh/id_rsa")
    ssh_port = remote.get("ssh_port", 22)
    options = remote.get("options", {})

    # Build paths
    local_root_expanded = expand_path(local_root)
    mount_point = local_root_expanded / local_path
    ssh_key_expanded = expand_path(ssh_key)

    # Parse host
    user, hostname, port = parse_ssh_host(host)
    if ssh_port != 22:
        port = ssh_port

    # Build SSH options for sshfs
    # Note: sshfs uses -o IdentityFile=xxx, not -i xxx
    ssh_identity = f"-o IdentityFile={ssh_key_expanded}"
    ssh_port_opt = f"-p {port}"

    # Build sshfs -o options
    sshfs_opts = [
        "ServerAliveInterval=30",
        "ServerAliveCountMax=3",
    ]

    # Add custom options
    if options.get("reconnect", False):
        sshfs_opts.append("reconnect")
    if "server_alive_interval" in options:
        sshfs_opts.append(f"ServerAliveInterval={options['server_alive_interval']}")

    # Build remote path
    remote_full = f"{user}@{hostname}:{remote_path}"

    # Build command: sshfs user@host:path mount_point -o IdentityFile=xxx -p port -o opts
    sshfs_opts_str = " -o ".join(sshfs_opts)
    cmd = f"sshfs {remote_full} {mount_point} {ssh_identity} {ssh_port_opt} -o {sshfs_opts_str}"

    return cmd, mount_point


def check_mount_status(mount_point: Path) -> bool:
    """Check if a path is mounted."""
    try:
        result = subprocess.run(
            ["mount"],
            capture_output=True,
            text=True
        )
        return str(mount_point) in result.stdout
    except Exception:
        return False


def mount_remote(remote: dict, config: dict, verbose: bool = False) -> bool:
    """Mount a single remote directory."""
    cmd, mount_point = build_sshfs_command(remote, expand_path(config["local_root"]))

    # Check if already mounted
    if check_mount_status(mount_point):
        print(f"✓ {remote['name']} already mounted at {mount_point}")
        return True

    # Create mount point
    mount_point.mkdir(parents=True, exist_ok=True)

    # Execute mount
    if verbose:
        print(f"Mounting {remote['name']}...")
        print(f"  Command: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✓ Mounted {remote['name']} at {mount_point}")
            return True
        else:
            print(f"✗ Failed to mount {remote['name']}: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error mounting {remote['name']}: {e}")
        return False


def unmount_remote(name: str, config: dict, verbose: bool = False) -> bool:
    """Unmount a single remote directory by name."""
    local_root = expand_path(config["local_root"])

    # Find the remote by name
    mount_point = None
    for remote in config.get("remotes", []):
        if remote.get("name") == name or remote.get("local_path") == name:
            local_path = remote.get("local_path", name)
            mount_point = local_root / local_path
            break

    if not mount_point:
        # Try direct path
        mount_point = local_root / name

    if not check_mount_status(mount_point):
        print(f"  {name} is not mounted")
        return True

    try:
        if verbose:
            print(f"Unmounting {name}...")

        result = subprocess.run(
            ["umount", str(mount_point)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✓ Unmounted {name}")
            return True
        else:
            # Try lazy unmount if normal fails
            result = subprocess.run(
                ["umount", "-f", str(mount_point)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ Unmounted {name} (forced)")
                return True
            print(f"✗ Failed to unmount {name}: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error unmounting {name}: {e}")
        return False


def mount_all(config: dict, verbose: bool = False) -> None:
    """Mount all configured remote directories."""
    remotes = config.get("remotes", [])

    if not remotes:
        print("No remote configurations found.")
        return

    print(f"Mounting {len(remotes)} remote(s)...")

    success = 0
    for remote in remotes:
        if mount_remote(remote, config, verbose):
            success += 1

    print(f"\n{success}/{len(remotes)} remotes mounted successfully.")


def unmount_all(config: dict, verbose: bool = False) -> None:
    """Unmount all configured remote directories."""
    remotes = config.get("remotes", [])

    if not remotes:
        print("No remote configurations found.")
        return

    print(f"Unmounting {len(remotes)} remote(s)...")

    success = 0
    for remote in remotes:
        if unmount_remote(remote.get("name", "unknown"), config, verbose):
            success += 1

    print(f"\n{success}/{len(remotes)} remotes unmounted.")


def status(config: dict) -> None:
    """Show mount status for all remotes."""
    remotes = config.get("remotes", [])
    local_root = expand_path(config.get("local_root", "~/projects"))

    if not remotes:
        print("No remote configurations found.")
        return

    print(f"SSHFS Mount Status (local_root: {local_root})\n")
    print(f"{'Name':<20} {'Status':<12} {'Mount Point'}")
    print("-" * 60)

    for remote in remotes:
        name = remote.get("name", "unknown")
        local_path = remote.get("local_path", name)
        mount_point = local_root / local_path

        is_mounted = check_mount_status(mount_point)
        status_str = "✓ Mounted" if is_mounted else "✗ Unmounted"

        print(f"{name:<20} {status_str:<12} {mount_point}")


def parse_ssh_config() -> dict:
    """
    Parse SSH config file and extract host configurations.
    Returns a dict mapping Host aliases to their configurations.
    """
    ssh_config_path = Path.home() / ".ssh" / "config"
    hosts = {}

    if not ssh_config_path.exists():
        return hosts

    current_host = None

    try:
        with open(ssh_config_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse Host line
                if line.startswith('Host '):
                    parts = line.split()
                    if len(parts) >= 2:
                        alias = parts[1]
                        # Skip wildcard hosts
                        if '*' not in alias:
                            current_host = alias
                            hosts[current_host] = {
                                'host': alias,
                                'user': None,
                                'hostname': None,
                                'port': 22,
                                'identity_file': None
                            }
                        else:
                            current_host = None
                    continue

                # Parse host-specific options
                if current_host:
                    if line.startswith('HostName '):
                        hosts[current_host]['hostname'] = line.split(None, 1)[1]
                    elif line.startswith('User '):
                        hosts[current_host]['user'] = line.split(None, 1)[1]
                    elif line.startswith('Port '):
                        try:
                            hosts[current_host]['port'] = int(line.split(None, 1)[1])
                        except ValueError:
                            pass
                    elif line.startswith('IdentityFile '):
                        hosts[current_host]['identity_file'] = line.split(None, 1)[1].strip('"')
    except Exception as e:
        print(f"Warning: Could not parse SSH config: {e}")

    return hosts


def init_wizard() -> dict:
    """Interactive initialization wizard."""
    print("=" * 60)
    print("SSHFS Mount Manager - Initialization Wizard")
    print("=" * 60)
    print()

    config = {
        "local_root": "~/projects",
        "remotes": []
    }

    # Ask for local root
    default_root = input(f"Local root directory [{config['local_root']}]: ").strip()
    if default_root:
        config["local_root"] = default_root

    print()

    # Parse existing SSH config
    ssh_hosts = parse_ssh_config()
    ssh_config_path = Path.home() / ".ssh" / "config"

    if ssh_hosts:
        print(f"Found {len(ssh_hosts)} SSH host(s) in {ssh_config_path}:")
        for alias, details in ssh_hosts.items():
            user_host = details['hostname'] or alias
            if details['user']:
                user_host = f"{details['user']}@{user_host}"
            port_info = f":{details['port']}" if details['port'] != 22 else ""
            print(f"  - {alias}: {user_host}{port_info}")
        print()

    print("Now let's configure your remote hosts.")
    print("You can use existing SSH config aliases or enter full connection strings.")
    print("Hint: Press Enter to use an SSH alias directly from the list above.")
    print()

    remote_num = 1
    while True:
        print(f"--- Remote #{remote_num} ---")

        # Suggest SSH aliases
        name = input(f"Remote name (e.g., remote-server-{remote_num}): ").strip()
        if not name:
            name = f"remote-server-{remote_num}"

        host_prompt = f"SSH host (SSH alias or user@host)"
        if ssh_hosts:
            aliases = list(ssh_hosts.keys())[:5]
            host_prompt += f" [{'/'.join(aliases)}]"
        host = input(f"{host_prompt}: ").strip()

        # Auto-fill from SSH config if using an alias
        ssh_key_default = "~/.ssh/id_rsa"
        ssh_port_default = "22"
        remote_path_default = "~/projects"

        if host in ssh_hosts:
            ssh_config = ssh_hosts[host]
            print(f"  Using SSH config for '{host}'")

            # Build user@host string
            if ssh_config['user'] and ssh_config['hostname']:
                host_display = f"{ssh_config['user']}@{ssh_config['hostname']}"
            elif ssh_config['hostname']:
                host_display = ssh_config['hostname']
            else:
                host_display = host

            if ssh_config['identity_file']:
                ssh_key_default = ssh_config['identity_file']
            if ssh_config['port'] != 22:
                ssh_port_default = str(ssh_config['port'])

            # Set host to full user@host for sshfs command
            if ssh_config['user'] and ssh_config['hostname']:
                host = f"{ssh_config['user']}@{ssh_config['hostname']}"
                if ssh_config['port'] != 22:
                    host += f":{ssh_config['port']}"
            elif ssh_config['hostname']:
                host = ssh_config['hostname']

            print(f"  Host resolved to: {host}")
            if ssh_config['port'] != 22:
                ssh_port_default = str(ssh_config['port'])

        remote_path = input(f"Remote path [{remote_path_default}]: ").strip() or remote_path_default
        local_path = input(f"Local subdirectory name [{name}]: ").strip() or name
        ssh_port = input(f"SSH port [{ssh_port_default}]: ").strip() or ssh_port_default
        ssh_key = input(f"SSH key path [{ssh_key_default}]: ").strip() or ssh_key_default

        remote = {
            "name": name,
            "host": host,
            "remote_path": remote_path,
            "local_path": local_path,
            "ssh_port": int(ssh_port) if ssh_port.isdigit() else 22,
            "ssh_key": ssh_key
        }

        # Check if using SSH alias
        original_alias = None
        for alias in ssh_hosts.keys():
            if host == alias or (ssh_hosts[alias].get('hostname') and
                                  host == f"{ssh_hosts[alias]['user']}@{ssh_hosts[alias]['hostname']}"):
                original_alias = alias
                break

        if original_alias:
            remote["ssh_alias"] = original_alias
            print(f"  (Linked to SSH alias: {original_alias})")

        config["remotes"].append(remote)
        print(f"✓ Added {name}")
        print()

        more = input("Add another remote? [y/N]: ").strip().lower()
        if more != 'y':
            break

        remote_num += 1

    print()
    print("=" * 60)
    print("Configuration Summary:")
    print("=" * 60)
    print(f"Local root: {config['local_root']}")
    print(f"Remotes: {len(config['remotes'])}")
    for r in config["remotes"]:
        alias_info = f" (SSH: {r['ssh_alias']})" if r.get('ssh_alias') else ""
        print(f"  - {r['name']}{alias_info}: {r['host']}:{r['remote_path']} -> {r['local_path']}")
    print()

    return config


def ensure_config_exists() -> None:
    """Ensure configuration directory and file exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        print("No configuration found. Starting initialization wizard...")
        print()
        config = init_wizard()
        save_config(config)
        print(f"✓ Configuration saved to {CONFIG_FILE}")
        print()
        print("You can now run 'sshfs-mount mount' to mount all remotes.")


def switch_profile(profile: str) -> None:
    """Switch to a different profile."""
    profile_file = PROFILES_DIR / f"{profile}.yaml"

    if not profile_file.exists():
        print(f"Error: Profile '{profile}' not found.")
        print("Available profiles:")
        for p in PROFILES_DIR.glob("*.yaml"):
            print(f"  - {p.stem}")
        sys.exit(1)

    ACTIVE_PROFILE_FILE.write_text(profile)
    print(f"✓ Switched to profile '{profile}'")


def list_profiles() -> None:
    """List all available profiles."""
    print("Available profiles:")

    # Check active profile
    active = None
    if ACTIVE_PROFILE_FILE.exists():
        active = ACTIVE_PROFILE_FILE.read_text().strip()

    for profile_file in PROFILES_DIR.glob("*.yaml"):
        profile_name = profile_file.stem
        marker = " (active)" if profile_name == active else ""
        print(f"  - {profile_name}{marker}")


def main():
    parser = argparse.ArgumentParser(
        description="SSHFS Mount Manager - Universal remote directory mounting tool"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Mount command
    mount_parser = subparsers.add_parser("mount", help="Mount remote directories")
    mount_parser.add_argument("name", nargs="?", help="Specific remote to mount")
    mount_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Unmount command
    unmount_parser = subparsers.add_parser("unmount", help="Unmount remote directories")
    unmount_parser.add_argument("name", nargs="?", help="Specific remote to unmount")
    unmount_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Status command
    subparsers.add_parser("status", help="Show mount status")

    # Init command
    subparsers.add_parser("init", help="Run initialization wizard")

    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Profile management")
    profile_subparsers = profile_parser.add_subparsers(dest="profile_command")
    profile_subparsers.add_parser("list", help="List profiles")
    profile_subparsers.add_parser("switch", help="Switch profile").add_argument("name", help="Profile name")

    # Config path command
    subparsers.add_parser("config-path", help="Show configuration file path")

    args = parser.parse_args()

    if args.command == "config-path":
        print(f"Configuration file: {CONFIG_FILE}")
        print(f"Profiles directory: {PROFILES_DIR}")
        return

    if args.command == "init":
        config = init_wizard()
        save_config(config)
        print(f"✓ Configuration saved to {CONFIG_FILE}")
        return

    if args.command == "profile":
        if args.profile_command == "list":
            list_profiles()
            return
        elif args.profile_command == "switch":
            switch_profile(args.name)
            return

    # Ensure config exists for other commands
    ensure_config_exists()

    config = load_config()

    if args.command == "mount":
        if args.name:
            # Mount specific remote
            remote = None
            for r in config.get("remotes", []):
                if r.get("name") == args.name or r.get("local_path") == args.name:
                    remote = r
                    break
            if not remote:
                print(f"Error: Remote '{args.name}' not found.")
                sys.exit(1)
            mount_remote(remote, config, args.verbose)
        else:
            mount_all(config, args.verbose)

    elif args.command == "unmount":
        if args.name:
            unmount_remote(args.name, config, args.verbose)
        else:
            unmount_all(config, args.verbose)

    elif args.command == "status":
        status(config)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
