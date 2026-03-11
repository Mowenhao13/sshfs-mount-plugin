#!/usr/bin/env python3
"""
SSHFS Mount Manager - Daemon for automatic reconnection
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "sshfs-mounts"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
PROFILES_DIR = CONFIG_DIR / "profiles"
ACTIVE_PROFILE_FILE = CONFIG_DIR / "active-profile"
DAEMON_PID = CONFIG_DIR / "daemon.pid"
DAEMON_LOG = CONFIG_DIR / "daemon.log"

import yaml

def expand_path(path: str) -> Path:
    """Expand ~ and environment variables in path."""
    return Path(os.path.expanduser(os.path.expandvars(path)))


def load_config() -> dict:
    """Load configuration from YAML file."""
    # Check for active profile
    if ACTIVE_PROFILE_FILE.exists():
        active_profile = ACTIVE_PROFILE_FILE.read_text().strip()
        profile_config = PROFILES_DIR / f"{active_profile}.yaml"
        if profile_config.exists():
            with open(profile_config, 'r') as f:
                return yaml.safe_load(f) or {}

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f) or {}

    return {}


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
    user_host = host
    port = ssh_port

    if ':' in host and not host.count('@') > 1:
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

    # Build SSH options for sshfs
    # Note: sshfs uses -o IdentityFile=xxx, not -i xxx
    ssh_identity = f"-o IdentityFile={ssh_key_expanded}"
    ssh_port_opt = f"-p {port}"

    # Build sshfs -o options
    sshfs_opts = [
        "ServerAliveInterval=30",
        "ServerAliveCountMax=3",
    ]

    if options.get("reconnect", False):
        sshfs_opts.append("reconnect")

    # Build remote path
    remote_full = f"{user}@{hostname}:{remote_path}"

    # Build command: sshfs user@host:path mount_point -o IdentityFile=xxx -p port -o opts
    sshfs_opts_str = " -o ".join(sshfs_opts)
    cmd = f"sshfs {remote_full} {mount_point} {ssh_identity} {ssh_port_opt} -o {sshfs_opts_str}"

    return cmd, mount_point


def log(message: str) -> None:
    """Write to daemon log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"

    with open(DAEMON_LOG, 'a') as f:
        f.write(log_line)

    print(log_line.strip())


def mount_remote(remote: dict, config: dict) -> bool:
    """Mount a single remote directory."""
    cmd, mount_point = build_sshfs_command(remote, expand_path(config["local_root"]))

    # Create mount point
    mount_point.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True
        else:
            log(f"Mount failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        log("Mount timed out")
        return False
    except Exception as e:
        log(f"Mount error: {e}")
        return False


def unmount_remote(remote: dict, config: dict) -> bool:
    """Unmount a single remote directory."""
    name = remote.get("name", "unknown")
    local_path = remote.get("local_path", name)
    local_root = expand_path(config["local_root"])
    mount_point = local_root / local_path

    try:
        subprocess.run(
            ["umount", "-f", str(mount_point)],
            capture_output=True,
            text=True,
            timeout=10
        )
        return True
    except Exception as e:
        log(f"Unmount error: {e}")
        return False


def check_all_mounts(config: dict) -> list:
    """Check status of all mounts, return list of unmounted remotes."""
    unmounted = []
    local_root = expand_path(config.get("local_root", "~/projects"))

    for remote in config.get("remotes", []):
        name = remote.get("name", "unknown")
        local_path = remote.get("local_path", name)
        mount_point = local_root / local_path

        if not check_mount_status(mount_point):
            unmounted.append(remote)

    return unmounted


def daemon_loop(check_interval: int = 30) -> None:
    """Main daemon loop."""
    log("Daemon started")
    log(f"Check interval: {check_interval} seconds")

    config = load_config()
    remotes = config.get("remotes", [])

    if not remotes:
        log("No remotes configured, exiting")
        return

    log(f"Monitoring {len(remotes)} remote(s)")

    while True:
        try:
            unmounted = check_all_mounts(config)

            if unmounted:
                for remote in unmounted:
                    name = remote.get("name", "unknown")
                    log(f"Detected unmounted: {name}, attempting reconnect...")

                    if mount_remote(remote, config):
                        log(f"✓ Reconnected: {name}")
                    else:
                        log(f"✗ Reconnect failed: {name}")
            else:
                log("All mounts healthy")

        except Exception as e:
            log(f"Error in check loop: {e}")

        time.sleep(check_interval)


def start_daemon(interval: int = 30) -> None:
    """Start the daemon."""
    if DAEMON_PID.exists():
        pid = DAEMON_PID.read_text().strip()
        try:
            os.kill(int(pid), 0)
            print(f"Daemon already running (PID: {pid})")
            return
        except ProcessLookupError:
            DAEMON_PID.unlink()

    # Ensure config exists
    if not CONFIG_FILE.exists() and not any(PROFILES_DIR.glob("*.yaml")):
        print("No configuration found. Run 'sshfs-mount init' first.")
        sys.exit(1)

    log(f"Starting daemon (interval: {interval}s)")
    DAEMON_PID.write_text(str(os.getpid()))

    # Setup signal handlers
    def signal_handler(signum, frame):
        log("Received signal, stopping daemon")
        if DAEMON_PID.exists():
            DAEMON_PID.unlink()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    daemon_loop(interval)


def stop_daemon() -> None:
    """Stop the daemon."""
    if not DAEMON_PID.exists():
        print("Daemon not running (no PID file)")
        return

    pid = int(DAEMON_PID.read_text().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"✓ Stopped daemon (PID: {pid})")
        DAEMON_PID.unlink()
    except ProcessLookupError:
        print("Daemon process not found (already stopped?)")
        DAEMON_PID.unlink()
    except Exception as e:
        print(f"Error stopping daemon: {e}")


def daemon_status() -> None:
    """Show daemon status."""
    if DAEMON_PID.exists():
        pid = DAEMON_PID.read_text().strip()
        try:
            os.kill(int(pid), 0)
            print(f"Daemon is running (PID: {pid})")

            if DAEMON_LOG.exists():
                print(f"\nRecent log ({DAEMON_LOG}):")
                with open(DAEMON_LOG, 'r') as f:
                    lines = f.readlines()[-10:]
                    for line in lines:
                        print(f"  {line.strip()}")

            return
        except ProcessLookupError:
            DAEMON_PID.unlink()

    print("Daemon is not running")


def main():
    if len(sys.argv) < 2:
        print("Usage: sshfs-daemon {start|stop|status}")
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        start_daemon(interval)

    elif command == "stop":
        stop_daemon()

    elif command == "status":
        daemon_status()

    else:
        print("Usage: sshfs-daemon {start|stop|status}")
        sys.exit(1)


if __name__ == "__main__":
    main()
