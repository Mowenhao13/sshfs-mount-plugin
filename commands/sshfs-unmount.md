---
command: sshfs-unmount-all
description: 卸载所有 SSHFS 远程目录
---

## 功能说明

一次性卸载所有已挂载的 SSHFS 远程目录。

## 执行方式

运行以下命令：

```bash
python3 lib/sshfs_mount.py unmount -v
```

或直接使用：

```bash
./bin/sshfs-mount unmount -v
```

## 输出示例

```
Unmounting 2 remote(s)...
✓ Unmounted remote-machine1
✓ Unmounted remote-machine2

2/2 remotes unmounted.
```

## 注意事项

- 如果某个目录未挂载，会显示 "is not mounted" 提示
- 卸载失败时会尝试强制卸载 (`umount -f`)

## 相关命令

- `/sshfs-mount-all` - 挂载所有远程目录
- `/sshfs-status` - 检查挂载状态
