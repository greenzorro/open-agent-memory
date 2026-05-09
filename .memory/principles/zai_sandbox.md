---
id: "mem-20260509-zai-sandbox"
type: "principle"
env: "cloud"
confidence: "high"
tags: ["git", "repo", "sandbox", "zai", "分离", "workspace", "持久化", "架构"]
---

# z.ai 沙盒环境架构

## 目录结构总览

```
/home/z/                              ← 用户主目录
├── .agent-browser/                   ← 浏览器自动化工具
├── .bun/                             ← Bun 运行时
├── .cache/                           ← 缓存
├── .local/                           ← 本地工具链
├── .npm/ / .npm-global/ / node_modules/  ← Node.js 生态
├── .venv/                            ← Python 虚拟环境
├── pyproject.toml / uv.lock          ← Python 依赖管理
└── my-project/                       ← 工作目录（持久化）
    ├── .git/                         ← 工作目录的 git（纯本地，无远程）
    ├── download/                     ← 产出物下载目录
    ├── skills/                       ← 平台技能（系统挂载）
    └── agent-workspace/              ← 记忆系统仓库（嵌套 git）
        ├── .git/                     ← 记忆系统的 git（远程 → greenzorro/agent-workspace）
        ├── .memory/                  ← 全局记忆（本仓库的核心内容）
        ├── README.md
        └── lab/                      ← 工具包 + 项目实验数据（含 _toolkit/、xian/、guilin/ 等）
```

## 持久化

`/home/z/my-project/` 具有**持久化能力**——沙盒周期性重置时，该目录下的文件不会丢失。这是唯一可靠的持久存储区域。所有需要跨会话保留的文件必须存放在此目录下。

`/home/z/` 下其他目录（`.venv/`、`.cache/`、`.bun/`、`.npm/` 等）在沙盒重置时**可能丢失**，不应存放任何有价值的产出物。

## 双仓库强制分离

沙盒中物理上存在两个独立的 Git 仓库，**绝不可混淆**：

| 仓库 | 路径 | 远程 | 允许提交的内容 |
|------|------|------|----------------|
| 工作目录 | `/home/z/my-project/` | 无（纯本地） | 项目文件、临时数据、实验产出 |
| 记忆系统 | `/home/z/my-project/agent-workspace/` | `greenzorro/agent-workspace` | 整个仓库（`.memory/`、`lab/`、`README.md` 等） |

## 执行红线

- 项目级操作（分组调整、数据生成、脚本适配、地图产出等）**只在工作目录的 git 中操作**，不可 commit 到记忆系统仓库
- 记忆系统仓库包含 `.memory/`、`lab/`、`README.md` 等，这些内容的变更可提交到该仓库
- 在执行 `git add`/`git commit`/`git push` 前，**必须通过 `git remote -v` 确认当前所在仓库**
- 操作记忆系统仓库时，**必须先 `cd /home/z/my-project/agent-workspace`**，绝不能在工作目录下误操作
