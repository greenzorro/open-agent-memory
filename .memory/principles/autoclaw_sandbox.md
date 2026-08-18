---
id: "mem-20260801-autoclaw-sandbox"
type: "principle"
env: "cloud"
confidence: "high"
tags: ["autoclaw", "sandbox", "沙盒", "git", "workspace", "限制", "平台特征"]
---

# Autoclaw 沙盒环境特征与限制

## 目录结构

- 当前会话工作区：`/root/.openclaw-autoclaw/workspace/`
- 港口目录：`/root/.openclaw-autoclaw/workspace/artifacts/`、`DELIVERY/`
- 项目目录：`/root/.openclaw-autoclaw/workspace/projects/`
- 内置记忆：`/root/.openclaw-autoclaw/workspace/*.md`、`memory/`
- 外挂记忆仓库：`/root/.openclaw-autoclaw/workspace/agent-workspace/`（独立 `.git`）

## 持久化规则

- 工作区内文件在同一会话内可用
- 跨会话是否保留不确定，关键数据必须提交到 git 或明确保存
- 不要把最终交付物放到 `/tmp`、home、Desktop、Downloads 等 workspace 外路径
- 大体积文件优先放 `artifacts/` 或 `DELIVERY/`

## 网络与进程限制

- 长进程约 5 分钟后被 SIGTERM 终止
- 沙盒到 GitHub HTTPS 连接不稳定，git push/fetch 容易超时
- PyPI 官方源下载大包易超时，Python 包安装必须使用清华镜像源
- 无 elevated 权限，不能 apt-get install
- 无 pip/ensurepip，必须用 `uv` 或 `python3 -m venv` 管理 Python 环境
- **出站 CDN 封锁**：沙盒出口 IP 被部分 CDN（Akamai、Fastly）的 Bot Management 默认拒绝，curl 裸连返回 403 或超时。使用自建 nginx 或 AWS ELB 的站点通常不受影响

## Git 操作规则

- 修改前先 `git pull origin main --rebase`
- **网络稳定配置**：沙盒 git 默认用 HTTP/2，长连接/大传输易触发 `GnuTLS recv error (-110): TLS connection was non-properly terminated`。设置 `git config --local http.version HTTP/1.1` 和 `git config --local http.postBuffer 52428800` 可稳定解决
- `git push` 超时可用 GitHub REST API 兜底
- API 直接写远程后必须执行 `git fetch origin main` 同步本地 ref
- 多仓库环境下每次 git 操作前确认 `pwd` 和 `git remote -v`
- 不要在 workspace 根目录执行 `git init`
- 沙盒中 git 仓库损坏时，优先用 tarball 重建整个目录
- 网络压测/验证时用 `--dry-run` 或临时分支，避免污染 main
- **credential store 目录**：仓库 local 配置的 credential.helper 指向 `/root/.openclaw-autoclaw/workspace/.git-credentials.d/git-credentials`。若该目录被清理（sandbox-port 等），git 会报 `unable to get credential storage lock`。需重建：`mkdir -p /root/.openclaw-autoclaw/workspace/.git-credentials.d`。token 内嵌在 remote URL 里，认证实际走 URL，credential store 仅为缓存

## 凭据与显示规则

- 平台工具对长串 token/secret 做视觉压缩
- 不能仅凭 `read`/`cat`/`grep` 输出判断 token 是否完整
- 验证 token 完整性应使用 Python `repr()` 或调用 API 实测
- 不要从对话上下文引用 token，上下文压缩会截断长字符串

## 工具与 API 可用性

- AutoGLM 系列 token 从本地服务自动获取（`http://127.0.0.1:18432/get_token`）
- AutoGLM 脚本位于 `~/.openclaw-autoclaw/skills/autoglm-*/`，调用远端 API，出口 IP 独立于沙盒，可穿透上述 CDN 封锁
- Cloudflare Browser Run 可用，边缘 IP 独立于沙盒
- Variflight API key 存储在外挂记忆系统
- 高德 API key 存储在外挂记忆系统
- Cloudflare R2 必须使用 REST API，不能用 S3 兼容协议
- 沙盒中无完整浏览器，无法与复杂 SPA 表单交互

## 子 Agent 使用规则

- OpenClaw 内置 cron 系统，支持 `isolated` agentTurn 定时任务
- 子 Agent 并发易触发模型/token 额度限制
- 关键路径任务应由主线程直接执行
- 子 Agent 失败后要有主线程兜底方案

## 执行红线

1. 重要修改先 `git add` + `git commit`
2. 产出物优先放 `artifacts/` 或 `DELIVERY/`
3. 对网络敏感操作预留 API 兜底方案
4. 多仓库环境下确认当前目录和远程后再操作
5. 不凭渲染层显示判断敏感凭据完整性
6. 大文件不直接提交到 git 仓库
