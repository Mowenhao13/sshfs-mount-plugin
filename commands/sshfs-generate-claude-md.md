---
command: sshfs-generate-claude-md
description: 为已挂载的 SSHFS 远程目录生成 CLAUDE.md 文件
---

## 功能说明

为所有已挂载的 SSHFS 远程目录自动生成 `CLAUDE.md` 文件，该文件包含：
- 远程主机连接信息
- 命令执行注意事项（必须在远程主机上执行）
- 正确的 SSH 执行示例

## 执行方式

运行以下命令：

```bash
python3 lib/generate_claude_md.py generate-all
```

## 输出示例

```
Generating CLAUDE.md files for 2 remote(s)...

  Skipping remote-machine1 (not mounted)
  ✓ Generated for remote-machine2

Done.
```

## CLAUDE.md 内容示例

生成的 `CLAUDE.md` 文件包含以下内容：

```markdown
# CLAUDE.md

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
| `/Users/halllo/projects/remote-machine2` | `ssh ubuntu@172.18.166.57` | remote-machine2 |
```

## 注意事项

- 只为**已挂载**的远程目录生成 CLAUDE.md
- 如果目录中已存在 CLAUDE.md，会被覆盖

## 相关命令

- `/sshfs-status` - 检查挂载状态
- `/sshfs-mount-all` - 挂载所有远程目录
