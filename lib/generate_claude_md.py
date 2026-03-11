#!/usr/bin/env python3
"""
SSHFS Mount Manager - CLAUDE.md Auto-generator
This script generates CLAUDE.md files for remote-mounted directories
"""

import os
import sys
import subprocess
from pathlib import Path

# Import from main module
sys.path.insert(0, str(Path(__file__).parent))
from sshfs_mount import load_config, expand_path, check_mount_status


def generate_claude_md(mount_point: Path, ssh_host: str, remote_name: str) -> None:
    """Generate CLAUDE.md file for a remote mount."""
    claude_md = mount_point / "CLAUDE.md"

    content = f'''# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 重要：远程仓库命令执行规则

**本目录是通过 SSHFS 挂载的远程主机目录，所有命令必须在远程主机上执行！**

当 Claude Code 需要运行命令时：
1. **不要直接在本地终端运行命令**
2. **必须先 SSH 登录到远程主机**，然后在远程主机上执行
3. 或者使用 `ssh user@host "command"` 的方式远程执行

### 远程主机连接信息

| 挂载点 | SSH 主机 | 说明 |
|--------|----------|------|
| `{mount_point}` | `ssh {ssh_host}` | {remote_name} |

### 命令执行示例

**错误做法**（在本地直接运行）：
```bash
python train.py  # 会在本地 macOS 运行，错误！
```

**正确做法**（SSH 到远程后运行）：
```bash
# 方式 1：先登录远程主机
ssh {ssh_host}
cd ~/projects/my-repo
python train.py

# 方式 2：直接远程执行
ssh {ssh_host} "cd ~/projects/my-repo && python train.py"
```

---
'''

    with open(claude_md, 'w') as f:
        f.write(content)

    print(f"Generated {claude_md}")


def generate_all() -> None:
    """Generate CLAUDE.md for all mounted remotes."""
    config = load_config()
    local_root = expand_path(config.get("local_root", "~/projects"))
    remotes = config.get("remotes", [])

    if not remotes:
        print("No remotes configured.")
        return

    print(f"Generating CLAUDE.md files for {len(remotes)} remote(s)...\n")

    for remote in remotes:
        name = remote.get("name", "unknown")
        local_path = remote.get("local_path", name)
        mount_point = local_root / local_path
        host = remote.get("host", "")

        # Check if mounted
        if not check_mount_status(mount_point):
            print(f"  Skipping {name} (not mounted)")
            continue

        # Generate CLAUDE.md
        generate_claude_md(mount_point, host, name)
        print(f"  ✓ Generated for {name}")

    print("\nDone.")


def check_current_directory() -> None:
    """Check if current directory is an SSHFS mount."""
    cwd = Path.cwd()

    try:
        result = subprocess.run(
            ["mount"],
            capture_output=True,
            text=True
        )

        is_sshfs = False
        for line in result.stdout.split('\n'):
            if str(cwd) in line and 'sshfs' in line:
                is_sshfs = True
                break

        if is_sshfs:
            print(f"Current directory ({cwd}) is an SSHFS mount.")

            claude_md = cwd / "CLAUDE.md"
            if not claude_md.exists():
                print("CLAUDE.md not found.")
                print("\nRun this to generate:")
                print("  sshfs-mount generate-claude-md")
            else:
                print("CLAUDE.md already exists.")
        else:
            print("Current directory is not an SSHFS mount.")

    except Exception as e:
        print(f"Error checking mount status: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: generate-claude-md {check|generate|generate-all}")
        print()
        print("Commands:")
        print("  check         Check if current directory is SSHFS mount")
        print("  generate      Generate CLAUDE.md for specific mount")
        print("  generate-all  Generate CLAUDE.md for all mounted remotes")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        check_current_directory()

    elif command == "generate":
        if len(sys.argv) < 5:
            print("Usage: generate-claude-md generate <mount_point> <ssh_host> <remote_name>")
            sys.exit(1)

        mount_point = expand_path(sys.argv[2])
        ssh_host = sys.argv[3]
        remote_name = sys.argv[4]

        generate_claude_md(mount_point, ssh_host, remote_name)

    elif command == "generate-all":
        generate_all()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
