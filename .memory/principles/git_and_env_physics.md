---
id: "mem-20260211-git1"
type: "principle"
env: "cloud"
confidence: "high"
tags: ["git", "sandbox", "physics"]
---

# Git 与环境物理规则

## 核心原则

- **路径规则**：优先使用相对路径以增强可移植性，但绝对路径同样有效。操作前通过 `pwd` 和 `ls` 验证当前目录。注意在云端环境中，默认工作目录与 agent-workspace 挂载点可能分离。
- **分支规则**：主分支始终是 `main`，永远不要推送到 `master`。
- **工作流规则**：在任何本地提交或推送之前，必须先执行 `git pull origin main` 以同步远程状态。
- **安全配置**：遇到 `dubious ownership` 错误时，运行 `git config --global --add safe.directory <path>` 修复。

## 执行流程

1. 任何 Git 操作前：先 `git pull origin main`
2. 提交前确认当前分支是 `main`
3. 文件操作时注意当前工作目录与目标路径的关系

## 更新历史

- 2026-02-11: 修正路径规则，移除"绝对路径无效"的过时陈述；增加工作目录与挂载点分离的提醒
