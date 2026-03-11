---
name: sshfs-mount
description: SSHFS 远程挂载管理工具 - 挂载/卸载远程目录、守护进程自动重连、生成 CLAUDE.md
version: 1.0.0
---

## 触发条件

当用户提到以下关键词时触发：
- SSHFS 挂载、远程挂载、mount、unmount
- 守护进程、daemon、自动重连
- 远程主机、SSH 远程目录
- 使用 `/sshfs-mount` 命令

## Skill 功能

### 核心功能
1. **挂载/卸载 SSHFS 远程目录** - 管理多个远程主机的 SSHFS 挂载
2. **守护进程管理** - 自动检测断开并重连的后台服务
3. **生成 CLAUDE.md 文件** - 为远程挂载目录自动生成使用说明
4. **多 Profile 配置管理** - 支持多套配置（工作/个人等场景）

### 可用命令
- `/sshfs-mount status` - 检查所有远程目录的挂载状态
- `/sshfs-mount mount` - 挂载所有远程目录
- `/sshfs-mount unmount` - 卸载所有远程目录
- `/sshfs-mount init` - 运行初始化向导
- `/sshfs-mount profile` - Profile 管理（list/switch）
- `/sshfs-mount daemon` - 守护进程管理（start/stop/status）
- `/sshfs-mount generate-claude-md` - 为已挂载的远程目录生成 CLAUDE.md
- `/sshfs-mount config-path` - 显示配置文件路径

## 配置文件位置

- **主配置**: `~/.config/sshfs-mounts/config.yaml`
- **Profiles**: `~/.config/sshfs-mounts/profiles/`
- **守护进程日志**: `~/.config/sshfs-mounts/daemon.log`

## 相关 Commands

- `/sshfs-status` - 快速检查挂载状态
- `/sshfs-mount-all` - 快速挂载所有远程目录
- `/sshfs-unmount-all` - 快速卸载所有远程目录
- `/sshfs-daemon` - 守护进程管理
- `/sshfs-generate-claude-md` - 生成 CLAUDE.md

## 注意事项

1. 本工具通过 SSHFS 挂载远程目录，需要先安装 `sshfs` 和 `PyYAML`
2. 首次使用需要运行 `/sshfs-mount init` 进行初始化配置
3. 建议开启守护进程以实现自动重连功能
