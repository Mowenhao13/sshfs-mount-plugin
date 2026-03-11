# SSHFS Mount Manager

一个通用的 SSHFS 远程挂载管理工具，专为 Claude Code Plugin 设计。

## 功能特性

- 🔧 **通用配置** - 支持任意数量的远程主机，每个主机独立配置
- 📋 **Profile 管理** - 支持多套配置（工作/个人等场景）
- 🔄 **守护进程** - 自动检测断开并重连
- 🤖 **Claude Code 集成** - 通过 Plugin/Skills 提供便捷的挂载管理
- 📝 **CLAUDE.md 自动生成** - 为远程目录自动生成使用说明

## 项目结构 (v2.0 - Plugin 架构)

```
sshfs-mount/
├── .claude-plugin/
│   └── plugin.json              # Plugin 清单文件
├── skills/
│   └── sshfs-mount.skill.md     # Skill 定义
├── commands/
│   ├── sshfs-status.md          # /sshfs-status 状态检查
│   ├── sshfs-mount-all.md       # /sshfs-mount-all 挂载所有
│   ├── sshfs-unmount-all.md     # /sshfs-unmount-all 卸载所有
│   ├── sshfs-daemon.md          # /sshfs-daemon 守护进程管理
│   └── sshfs-generate-claude-md.md  # /sshfs-generate-claude-md 生成 CLAUDE.md
├── lib/
│   ├── sshfs_mount.py           # 核心逻辑 (配置管理、挂载/卸载)
│   ├── sshfs_daemon.py          # 守护进程 (自动重连)
│   └── generate_claude_md.py    # CLAUDE.md 生成器
├── bin/
│   ├── sshfs-mount              # 命令行入口
│   ├── sshfs-daemon             # 守护进程入口
│   └── sshfs                    # 快速挂载脚本
├── scripts/
│   ├── install.sh               # 安装脚本
│   └── create-package.sh        # 打包脚本
└── README.md                    # 本文档
```

## 快速开始

### 安装

```bash
# 克隆或下载项目
cd sshfs-mount

# 运行安装脚本
./scripts/install.sh
```

### 首次使用

```bash
# 运行初始化向导
./bin/sshfs-mount init

# 或从 Claude Code 中
/sshfs-mount init
```

### 基本命令

```bash
# 查看挂载状态
./bin/sshfs-mount status

# 挂载所有远程目录
./bin/sshfs-mount mount

# 卸载所有远程目录
./bin/sshfs-mount unmount

# 启动守护进程（自动重连）
./bin/sshfs-daemon start

# 查看守护进程状态
./bin/sshfs-daemon status
```

## Claude Code Plugin 集成

安装后，在 Claude Code 中可以使用以下命令：

### Skills

- `/sshfs-mount` - 主 Skill，显示可用功能

### Commands

| Command | 功能 |
|---------|------|
| `/sshfs-status` | 检查所有远程目录的挂载状态 |
| `/sshfs-mount-all` | 挂载所有远程目录 |
| `/sshfs-unmount-all` | 卸载所有远程目录 |
| `/sshfs-daemon start` | 启动守护进程 |
| `/sshfs-daemon stop` | 停止守护进程 |
| `/sshfs-daemon status` | 查看守护进程状态 |
| `/sshfs-generate-claude-md` | 为已挂载目录生成 CLAUDE.md |

## 配置文件

### 配置文件位置

- **主配置**: `~/.config/sshfs-mounts/config.yaml`
- **Profiles**: `~/.config/sshfs-mounts/profiles/`
- **守护进程日志**: `~/.config/sshfs-mounts/daemon.log`

### 配置文件格式

```yaml
local_root: ~/projects

remotes:
  - name: remote-machine1
    host: ubuntu@172.18.198.243
    remote_path: ~/projects
    local_path: remote-machine1
    ssh_key: ~/.ssh/id_rsa
    ssh_port: 22
    options:
      reconnect: true
      server_alive_interval: 30

  - name: remote-machine2
    host: ubuntu@172.18.166.57:55900
    remote_path: ~/projects
    local_path: remote-machine2
    ssh_key: ~/.ssh/id_rsa
    ssh_port: 55900
```

### Profile 配置示例

```yaml
# ~/.config/sshfs-mounts/profiles/work.yaml
name: work
description: 工作开发环境

local_root: ~/work-projects

remotes:
  - name: remote-prod
    host: user@prod-server.example.com
    remote_path: ~/projects
    local_path: remote-prod
```

## Profile 管理

```bash
# 列出所有 profile
./bin/sshfs-mount profile list

# 切换到 work profile
./bin/sshfs-mount profile switch work
```

## 守护进程

守护进程每 30 秒（可配置）检查一次挂载状态，自动重新连接断开的远程目录。

```bash
# 启动守护进程
./bin/sshfs-daemon start

# 指定检查间隔（秒）
./bin/sshfs-daemon start 60

# 停止守护进程
./bin/sshfs-daemon stop

# 查看状态
./bin/sshfs-daemon status
```

## 依赖

- Python 3.6+
- sshfs
- PyYAML

### 安装依赖

```bash
# macOS
brew install sshfs
pip3 install pyyaml

# Ubuntu/Debian
sudo apt-get install sshfs python3-yaml

# Arch Linux
sudo pacman -S sshfs python-yaml
```

## 故障排除

### 挂载失败

检查 SSH key 是否存在并有正确的权限：
```bash
ls -la ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
```

### 连接断开

检查网络连接和 SSH 服务：
```bash
ssh user@host  # 测试 SSH 连接
```

### 查看日志

```bash
# 查看守护进程日志
tail -f ~/.config/sshfs-mounts/daemon.log
```

## 版本历史

- **v2.0** - 重构为 Claude Code Plugin 架构，新增 commands/ 和 skills/ 目录
- **v1.0** - 初始版本，基础 SSHFS 挂载管理功能

## 支持系统

- macOS
- Linux

> **注意**: Windows 版本尚未开发，欢迎贡献！
