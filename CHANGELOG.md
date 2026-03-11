# Changelog

All notable changes to the SSHFS Mount Manager project will be documented in this file.

## [2.0.0] - 2026-03-11

### Changed
- **重构为 Claude Code Plugin 架构** - 按照 Claude Code plugin 规范重新组织目录结构
- 迁移 `skill/` 到 `skills/` 和 `commands/` 目录
- 移动 Python 核心模块到 `lib/` 目录
- 移动命令行脚本到 `bin/` 目录
- 移动安装脚本到 `scripts/` 目录

### Added
- 新增 5 个 Commands:
  - `/sshfs-status` - 状态检查
  - `/sshfs-mount-all` - 挂载所有
  - `/sshfs-unmount-all` - 卸载所有
  - `/sshfs-daemon` - 守护进程管理
  - `/sshfs-generate-claude-md` - 生成 CLAUDE.md
- 新增 `skills/sshfs-mount.skill.md` - 主 Skill 定义
- 新增 `.claude-plugin/plugin.json` - Plugin 清单文件
- 新增 `CHANGELOG.md` - 版本历史记录

### Updated
- 更新 `README.md` 反映新的目录结构和使用方式
- 更新 `scripts/install.sh` 支持新的文件布局
- 更新 `scripts/create-package.sh` 打包脚本

## [1.0.0] - 2026-03-10

### Added
- 初始版本发布
- 基础 SSHFS 挂载管理功能
- 守护进程自动重连
- CLAUDE.md 自动生成器
- Profile 管理支持
- 初始化向导
