---
command: sshfs-mount-all
description: 挂载所有 SSHFS 远程目录
---

## 功能说明

一次性挂载所有配置的 SSHFS 远程目录。

## 执行方式

运行以下命令：

```bash
python3 lib/sshfs_mount.py mount -v
```

或直接使用：

```bash
./bin/sshfs-mount mount -v
```

## 输出示例

```
Mounting 2 remote(s)...
✓ Mounted remote-machine1 at /Users/halllo/projects/remote-machine1
✓ Mounted remote-machine2 at /Users/halllo/projects/remote-machine2

2/2 remotes mounted successfully.
```

## 前置条件

1. 确保已运行初始化向导 (`sshfs-mount init`)
2. 确保 SSH key 存在并有正确的权限
3. 确保远程主机 SSH 服务可访问

## 相关命令

- `/sshfs-status` - 检查挂载状态
- `/sshfs-unmount-all` - 卸载所有远程目录
- `/sshfs-daemon start` - 启动守护进程（自动重连）
