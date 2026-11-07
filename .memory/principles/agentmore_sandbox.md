---
id: "mem-20261003-agentmore-sandbox"
type: "principle"
env: "cloud"
confidence: "high"
tags: ["agentmore", "agent-more", "清言", "sandbox", "沙盒", "平台特征", "限制", "cron", "会话隔离", "阿里云", "出网", "墙外", "k8s", "pod"]
---

# Agent More 沙盒环境特征与限制

> 本节点身份：Agent 运行于 Agent More（智谱清言 Agent 功能）。本条目基于 2026-10-03 实测勘察（金丝雀会话隔离实验 + 实例指纹差分实验 + 出网连通性测试），实测项标 `confidence: high`，推断项单独标注。

## 底层基础设施（实测）

- 宿主：阿里云北京 Serverless K8s（ECI 弹性容器实例）
  - hostname：`${SANDBOX_HOSTNAME}`（每 Pod 不同）
  - Pod 形如 `cp-2zexxxxxxxx-f7r86`（每次拉取不同）
  - 内核 `5.10.134-18.0.12.lifsea8`（Alibaba Cloud Linux）
  - 出口 IP：`101.201.238.123`（中国 北京 阿里云）
- 资源：2 vCPU / 4 GiB RAM / 30 GB overlay 磁盘；用户 `z`（uid 1001），**无 sudo/elevated 权限**
- 运行时：Python 3.12.13（uv + `.venv` 管理）、Node v24.18.0、Bun 1.3.14
- 平台对长 token/secret 做视觉脱敏（输出显示 `[REDACTED:github_token]`）——与 autoclaw 相同，不能凭显示判断 token 完整性

## Pod 生命周期与会话模型（核心发现，实测）

- **Pod 是短命的**：观测到 Pod 在主会话进行中（约 3 小时处）被整体替换，会话无缝存活
- 会话状态存于平台控制平面，新 Pod 拉起后重水化——**容器可弃，会话逻辑上是永续的**（"RAM 清零是换班不是死亡"的直接观测）
- **三层模型**：
  1. 控制平面：会话 = 逻辑记录（主会话、cron 会话各自独立记账）
  2. 计算层：同 Pod 内多个进程树（主会话与 cron 实例 PPID 不同）
  3. 存储层：所有实例共享 `/home/z/my-project` 文件系统

## Cron 定时任务行为（金丝雀实验实测）

- cron 实例与主会话**同 Pod、同文件系统、同工具权限**，但**完全无法访问主会话对话上下文**（金丝雀词仅存在于主会话对话中，cron 实例确认"没见过"且"无历史上下文"）
- cron 的一次性执行**不会在用户会话列表中生成可见会话**——它是"路过式执行"，结果以系统消息形式投递回主对话
- **铁律：cron 的 prompt 必须完全自包含**；要传递上下文只能写文件（HEARTBEAT.md、daily notes、lab/ 下的交接文件），让任务实例自己读
- 验明实例身份的方法（可复用）：①金丝雀词（只放对话不落盘）②运行时指纹差分（hostname/Pod名/uptime/PPID/env）③证据文件落盘回读

## 目录结构与持久化

```
/home/z/
├── Drive/                        ← 平台云盘挂载（notebook/screenshots/workspace）
├── .venv/ .bun/ .npm* node_modules/  ← 运行时环境（uid z 可写）
└── my-project/                   ← 唯一工作区（无 .git，见下）
    ├── AGENTS/SOUL/USER/IDENTITY/TOOLS.md  ← 平台注入的角色文件（用户可编辑）
    ├── agent-workspace/          ← 记忆仓库（独立 .git，远程 GitHub）
    ├── projects/ skills/ lab/ download/ upload/
    ├── .env                      ← 仅 DATABASE_URL（sqlite，内建数据库）
    └── db/custom.db              ← 平台内建数据库
```

- **与 z.ai 沙盒的关键差异**：`my-project` 下**没有 `.git`**，不适用 zai 条目的 repo.tar 打包机制；实测文件在 Pod 整体替换后无丢失 → 持久化应为**卷挂载**而非会话结束打包（此推断 confidence: medium，机制未拆解验证，但"Pod 换新文件仍在"为实测）
- `skills/` 内置约 73 个平台技能（含 z-ai CLI `/usr/local/bin/z-ai`），平台侧管理
- Bash 工具单次执行超时上限 10 分钟

## 网络环境（实测，2026-10-03）

出口为阿里云北京（与 autoclaw 同款 AS37963 大陆出口），**自身无翻墙能力**：

| 目标 | 结果 |
|------|------|
| github.com / api.github.com | ✅ 200（github.com 走内网代理 `${INTERNAL_PROXY_IP}`，api 直连 `20.205.243.168`） |
| pypi.org / registry.npmjs.org / baidu.com | ✅ 200 |
| google.com / youtube.com / api.telegram.org / api.openai.com / huggingface.co / medium.com | ❌ `000`（直连不通，无 DNS 可用结果） |
| api.anthropic.com | ⚠️ 403（能建连，被 Cloudflare 按地区拒绝） |

- **可用借道通道**：`z-ai` CLI 的 `web_search`（远端执行，出口独立于沙盒，实测可用）；`web-reader` 技能同理
- **能力边界与 autoclaw 条目口径一致**：信息获取类任务不受墙限制；登录/交互墙外账号不可行；Telegram 发消息为结构性缺口
- **分工定案（2026-10-03）**：墙外任务归 Autoclaw 节点；本节点承接无墙外需求的日常任务。勿再向用户建议租用 VPS/服务器

## Git 操作规则

- 记忆仓库：`${MEMORY_REPO}`，远程仓库凭据由运行环境注入；git 身份 `agent-vik@victor42.work`
- 写入策略：本仓库只存长期记忆，**需用户明确授权才写入**；写入后必须完整 `pull --rebase → add → commit → push`
- 多节点同时维护此仓库，push 前先 pull --rebase 防冲突
- 工作区 `my-project/` 无 git，跨会话留存靠卷持久化（未 commit 的文件不会丢——与 zai 条目相反，但**重要数据仍建议进记忆仓库或 Drive**）

## 执行红线

1. cron prompt 必须自包含，状态传递只走文件
2. 修改记忆仓库前先 pull --rebase，操作前 `git remote -v` 确认所在仓库
3. 不凭工具输出显示判断 token 完整性（平台会脱敏）
4. 需要墙外资源的任务直接移交 Autoclaw 节点，不在本节点死磕
5. 长进程单次 Bash 不超过 10 分钟，超长任务分段执行或走 cron

## Python 环境与网关风暴应对（2026-10-08 实测补充）

- **系统默认 python = `/home/z/.venv`（持久 venv，PATH 默认首位）**——装第三方包一律 `uv pip install -p /home/z/.venv/bin/python`；沙盒 python 受 PEP 668 保护（externally-managed），pip 直装被拒
- **`/tmp` 是易失区**：venv、缓存、后台产物建在 /tmp 会在风暴/会话重建中丢失；重活一律用 `/home/z` 持久区（如 `UV_CACHE_DIR=/home/z/.uvcache`，断点续传不丢）
- **网关风暴（504 broken session）行为模式**：
  - 长命令（>30-45s）高概率 504 被杀，且**整个进程组连 setsid/nohup 后台一起清**——"后台安装"在此平台不可靠
  - 短命令（echo 级）必活；**应对=拆小批（每批 <45s）+ 批间 import 验证 + 循环重试**，uv 有缓存续传，风暴中反复重跑同一批命令最终会收敛
  - 装依赖用 uv（Rust 快速下载），不 pip；`pip --break-system-packages` 与 `uv --system` 在本沙盒均不可行
  - **504 响应可能掩盖已成功执行**（2026-11-01 实锤：返回 broken session 但 git commit 实际完成，working tree clean）——重试前先查状态（log/status/diff），勿盲目重跑有副作用命令（append/commit 类重跑会重复执行）
- **持久 shell 的 cwd 不保跨调用**（2026-11-01 实测）：同会话内 `cd` 只对当条命令生效，下一条又回到默认目录——git 用 `-C`、脚本用绝对路径、python 脚本内自行 `os.chdir` 或全程绝对路径，勿依赖会话 cwd
