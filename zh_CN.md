# SSHFS Mount Manager

**一个通用的 SSHFS 远程挂载管理工具，专为 Claude Code Plugin 设计。**

[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-purple)](https://code.claude.com)
[![SSHFS](https://img.shields.io/badge/SSHFS-Mount_Generator-blue)](https://github.com/Mowenhao13/sshfs-mount-plugin)

## 功能特性

- 🔧 **通用配置** - 支持任意数量的远程主机，每个主机独立配置
- 📋 **Profile 管理** - 支持多套配置（工作/个人等场景）
- 🔄 **守护进程** - 自动检测断开并重连
- 🤖 **Claude Code 集成** - 通过 Plugin/Skills 提供便捷的挂载管理
- 📝 **CLAUDE.md 自动生成** - 为远程目录自动生成使用说明

## 项目结构 (v2.0 - Plugin 架构)

```
sshfs-mount/
├── plugins/
│   └── sshfs-mount/               # 插件主目录
│       ├── .claude-plugin/
│       │   └── plugin.json        # Plugin 清单文件
│       ├── skills/
│       │   └── sshfs-mount.skill.md  # Skill 定义
│       ├── commands/
│       │   ├── sshfs-status.md       # /sshfs-status 状态检查
│       │   ├── sshfs-mount-all.md    # /sshfs-mount-all 挂载所有
│       │   ├── sshfs-unmount-all.md  # /sshfs-unmount-all 卸载所有
│       │   ├── sshfs-daemon.md       # /sshfs-daemon 守护进程管理
│       │   └── sshfs-generate-claude-md.md  # /sshfs-generate-claude-md 生成 CLAUDE.md
│       ├── lib/
│       │   ├── sshfs_mount.py        # 核心逻辑 (配置管理、挂载/卸载)
│       │   ├── sshfs_daemon.py       # 守护进程 (自动重连)
│       │   └── generate_claude_md.py # CLAUDE.md 生成器
│       ├── bin/
│       │   ├── sshfs-mount           # 命令行入口
│       │   ├── sshfs-daemon          # 守护进程入口
│       │   └── sshfs                 # 快速挂载脚本
│       └── scripts/
│           ├── install.sh            # 安装脚本
│           └── create-package.sh     # 打包脚本
├── .claude/
│   └── settings.local.json          # Claude Code 本地设置
├── CHANGELOG.md                     # 变更日志
└── README.md                        # 英文文档
```

## 快速开始

### 安装方式

#### 方式 1：通过 Claude Code 安装（推荐）

```bash
# 在 Claude Code 中执行
/plugins install /Users/halllo/.claude/plugins/cache/local-plugins/sshfs-mount
```

#### 方式 2：运行安装脚本（独立 CLI 安装）

```bash
# 克隆或下载项目
cd sshfs-mount/plugins/sshfs-mount

# 运行安装脚本
./scripts/install.sh
```

安装后会创建全局命令：
- `sshfs-mount` - 主命令行工具
- `sshfs-daemon` - 守护进程管理

### 首次使用

```bash
# 运行初始化向导
sshfs-mount init
```

初始化会：
1. 创建配置文件目录 `~/.config/sshfs-mount-plugin/`
2. 运行交互式向导配置远程主机
3. 解析现有 SSH 配置自动填充

### 基本命令

```bash
# 查看挂载状态
sshfs-mount status

# 挂载所有远程目录
sshfs-mount mount

# 卸载所有远程目录
sshfs-mount unmount

# 启动守护进程（自动重连）
sshfs-daemon start

# 查看守护进程状态
sshfs-daemon status
```

## Claude Code Plugin 集成

安装插件后，重启 Claude Code 即可使用以下功能：

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

### Skill

使用 `/sshfs-mount` 技能可以进行交互式操作，包括：
- 挂载/卸载远程目录
- 守护进程管理
- Profile 切换
- 配置管理

## 配置文件

### 配置文件位置

- **主配置**: `~/.config/sshfs-mount-plugin/config.yaml`
- **Profiles**: `~/.config/sshfs-mount-plugin/profiles/`
- **守护进程日志**: `~/.config/sshfs-mount-plugin/daemon.log`

### 配置文件格式

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

### Profile 配置示例

```yaml
# ~/.config/sshfs-mount-plugin/profiles/work.yaml
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
sshfs-mount profile list

# 切换到 work profile
sshfs-mount profile switch work
```

## 守护进程

守护进程每 30 秒（可配置）检查一次挂载状态，自动重新连接断开的远程目录。

```bash
# 启动守护进程
sshfs-daemon start

# 指定检查间隔（秒）
sshfs-daemon start 60

# 停止守护进程
sshfs-daemon stop

# 查看状态和日志
sshfs-daemon status
tail -f ~/.config/sshfs-mount-plugin/daemon.log
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
tail -f ~/.config/sshfs-mount-plugin/daemon.log
```

## 支持系统

- macOS
- Linux

> **注意**: Windows 版本尚未开发，欢迎贡献！

## License

MIT
