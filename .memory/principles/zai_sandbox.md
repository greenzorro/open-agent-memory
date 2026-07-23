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
└── my-project/                       ← 工作目录（git repo → repo.tar 持久化）
    ├── .git/                         ← 工作目录的 git（纯本地，无远程）
    ├── backup/                       ← 自定义 skill 备份（git-tracked → 进 tar）
    ├── projects/                     ← 长期项目目录（git-tracked → 进 tar，内容可变）
    ├── download/                     ← 产出物 + 港口（清理港口归集 + 7天过期）
    ├── upload/ / scripts/ / tool-results/  ← 临时工作目录
    ├── skills/                       ← 平台技能（.gitignore 排除，每次重置为默认）
    ├── worklog.md / .env / .gitignore
    └── agent-workspace/              ← 记忆系统仓库（嵌套 git）
        ├── .git/                     ← 记忆系统的 git（远程 → greenzorro/agent-workspace）
        ├── .memory/                  ← 全局记忆（本仓库的核心内容）
        ├── README.md
        └── lab/                      ← 工具包 + 项目实验数据（含 _toolkit/ 等）
```

## 持久化原理

`/home/z/my-project/` 是**唯一可靠的持久存储区域**，沙盒重置时该目录不会丢失。但其持久化机制有严格前提：

### 核心机制：repo.tar

- 会话结束时，平台将 `my-project` 的 **git 仓库**打包为 `repo.tar`
- 新会话开始时，从 `repo.tar` 解压恢复
- **只有 git 已 commit 的文件才会进入 tar**，未 commit 的新文件和修改会丢失
- `.gitignore` 排除的目录（如 `skills/`）每次重置为平台默认值，tar 中不包含

### 持久化策略

| 需要持久化的内容 | 方法 |
|-----------------|------|
| 自定义 skills | 存入 `backup/`，commit 进 git → 进 tar；每次 session 由 cron `cp -r backup/* skills/` 恢复 |
| 长期项目 | 存入 `projects/`，commit 进 git → 进 tar |
| 记忆系统 | `agent-workspace/` 是独立 git repo，通过 `git pull` 从 GitHub 同步 |
| 产出物 | `download/` 会被清理港口归集和过期清理，不保证长期存在 |

### 常见陷阱

- 创建了新目录/文件但**忘记 commit** → session 结束后丢失
- 把需要保留的文件放在 `.gitignore` 排除的目录（如 `skills/`）中 → 不会进 tar
- 清理港口 cron 误把重要目录（`backup/`、`projects/`）当散落文件归集走 → 需在 exclude-dirs 中排除

`/home/z/` 下其他目录（`.venv/`、`.cache/`、`.bun/`、`.npm/` 等）在沙盒重置时**可能丢失**，不应存放任何有价值的产出物。

## 双仓库强制分离

沙盒中物理上存在两个独立的 Git 仓库，**绝不可混淆**：

| 仓库 | 路径 | 远程 | 允许提交的内容 |
|------|------|------|----------------|
| 工作目录 | `/home/z/my-project/` | 无（纯本地） | `backup/`、`projects/`、临时数据、实验产出；projects/ 下可有独立 git 仓库 |
| 记忆系统 | `/home/z/my-project/agent-workspace/` | `greenzorro/agent-workspace` | 整个仓库（`.memory/`、`lab/`、`README.md` 等） |

## 执行红线

- 项目级操作（分组调整、数据生成、脚本适配、地图产出等）**只在工作目录的 git 中操作**，不可 commit 到记忆系统仓库
- 记忆系统仓库包含 `.memory/`、`lab/`、`README.md` 等，这些内容的变更可提交到该仓库
- 在执行 `git add`/`git commit`/`git push` 前，**必须通过 `git remote -v` 确认当前所在仓库**
- 操作记忆系统仓库时，**必须先 `cd /home/z/my-project/agent-workspace`**，绝不能在工作目录下误操作
