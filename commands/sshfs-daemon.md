---
command: sshfs-daemon
description: SSHFS 守护进程管理 - 自动检测断开并重连
---

## 功能说明

守护进程每 30 秒（可配置）检查一次挂载状态，自动重新连接断开的 SSHFS 远程目录。

## 子命令

### 启动守护进程

```bash
python3 lib/sshfs_daemon.py start
# 或指定检查间隔（秒）
python3 lib/sshfs_daemon.py start 60
```

### 停止守护进程

```bash
python3 lib/sshfs_daemon.py stop
```

### 查看守护进程状态

```bash
python3 lib/sshfs_daemon.py status
```

## 输出示例

**启动:**
```
[2026-03-11 10:00:00] Starting daemon (interval: 30s)
[2026-03-11 10:00:00] Daemon started
[2026-03-11 10:00:00] Monitoring 2 remote(s)
```

**状态:**
```
Daemon is running (PID: 12345)

Recent log (~/.config/sshfs-mounts/daemon.log):
  [2026-03-11 10:05:00] All mounts healthy
  [2026-03-11 10:05:30] All mounts healthy
```

**停止:**
```
✓ Stopped daemon (PID: 12345)
```

## 日志位置

守护进程日志文件：`~/.config/sshfs-mounts/daemon.log`

## 查看日志

```bash
tail -f ~/.config/sshfs-mounts/daemon.log
```

## 相关命令

- `/sshfs-status` - 检查挂载状态
- `/sshfs-mount-all` - 挂载所有远程目录
