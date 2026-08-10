---
id: "mem-20260810-kzfv"
type: "principle"
env: "global"
confidence: "high"
tags: ["handoff", "交接", "换 Agent", "多工具", "任务延续", "r2"]
---

# 任务交接（Handoff）

## 用途

多轮任务需要换工具、换设备或换 Agent 化身时，用一份极简临时交接包传递「下一步接着干什么」。

交接包只回答一个问题：**下一个 Agent 要继续，还缺什么？** 其余都是噪音。

## 使用时机

- 用户明确要求交接 / handoff / 换 Agent
- 用户即将换到另一工具（Cursor、Claude、GPT、Codex、云端 Agent 等）继续当前任务
- 多轮任务进行中，需要跨工具或跨化身存活

**不要用交接包时：**

- 用户只是想给自己留笔记（应走笔记本）
- 并未发生工具或化身切换

用户明确要求交接时一律执行。即便任务已完成，也可做终态摘要；在 Goal 中标明任务已完成。接手 Agent 吸收后仍须删除交接包。

## 通道与命名

- **桶**：Cloudflare R2 私有桶 `${CF_R2_PRIVATE_BUCKET}`（凭证与 API：`.memory/entities/cloudflare_agent_platform.md`）
- **前缀**：`handoff/<主题>/`
- **入口文件**：`notes.md`（必有）
- **主题**：用户选定；无日期、无 slug、无额外前缀（含不得以 `handoff-` 开头）
- 未给出主题时：先问「交接主题叫什么？」；可给 2–3 个候选；禁止擅自命名后上传
- 禁止写入 `${CF_R2_PUBLIC_BUCKET}`（公开交付桶）

正确示例：`handoff/blog-seo/notes.md`  
错误示例：`handoff/handoff-blog-seo/notes.md`、`handoff/blog-seo-20260707/`

## 包内容

默认只有 `notes.md`。仅当内容**本质上非叙事**时另加文件，且必须在 `notes.md` 中说明用途：

- 接手方应直接跑的脚本（`verify.sh`、`repro.py`）
- 接手方会**程序化解析**的结构化数据（CSV / JSON / 测试矩阵）；短名单仍写在 `notes.md`
- 会打断 `notes.md` 阅读流的长日志 / 堆栈（> 30 行）

**上传副本还是只引用路径：**

- 源在临时位置（`PATH_DOWNLOADS/temp/`、`/tmp/` 等）→ 上传副本进交接前缀
- 源在接手方能到达的项目仓库或持久存储 → 引用绝对路径或持久 URL，不复制

**禁止**作为叙事冗余另建：`README.md`、`todo.md`、`summary.md`、`changelog.md`、`paths.txt`、`index.json`、`diff.patch` / `changes.diff`（用 git；在 notes 里写 commit/branch）

## notes.md 结构

固定结构，不增删、不改名章节：

```markdown
# <主题> Handoff

Created: YYYY-MM-DD
Triggered by: 用户主动触发
Receiving agent: <未指定 / 用户指定的工具>

## Goal
<一句话目标。如果存在不可自动化的红线，紧跟一句说明。>

## Context
<下一个 Agent 会踩的坑、会误解的前提。只写不读源文件就无从得知的隐性知识。不写显而易见的背景。>

## Current State
<分三类，每类用列表：>
- 已完成：<具体的事实，带文件路径>
- 已验证：<带可复现命令>
- 待办：<明确的下一步>

## Handoff Notes
<写给接手 Agent 的关键注意事项。语气直接，像给同事留便签。>

## Cleanup
交接包内全部任务完成后，接手 Agent 删除 R2 `${CF_R2_PRIVATE_BUCKET}` 桶中本前缀 `handoff/<主题>/` 下的全部对象。
```

写作原则：

- 少写：下一任能读源文件；不要把文件内容贴进 notes
- 引用不复制：可到达的路径写绝对路径或持久 URL；例外：< 5 行内联片段说明非显然点
- 写隐性知识：决策理由、陷阱、约定、「别动 X 因为 Y」
- 无内容的节写 `<无>`；Cleanup 永不空

## 创建流程

1. 确认主题名
2. 从 `cloudflare_agent_platform` 解析 R2 凭证
3. 写 `notes.md`（可暂存于 `PATH_DOWNLOADS/temp/<主题>/`）
4. 确有需要时加非叙事附件并在 notes 中引用
5. 上传到 `${CF_R2_PRIVATE_BUCKET}`，key 为 `handoff/<主题>/...`（`notes.md` 的 Content-Type：`text/markdown; charset=utf-8`）
6. 告知用户：桶 `${CF_R2_PRIVATE_BUCKET}`，前缀 `handoff/<主题>/`，然后停止

## 接手与收尾

1. List / GET `${CF_R2_PRIVATE_BUCKET}` 下 `handoff/<主题>/`
2. 先读 `notes.md`，再按需取同前缀附件
3. 完成 Goal / 待办中的工作
4. **包内全部任务完成后**，删除该前缀下全部对象，并简短告知用户已删除

**完成判定：** Goal 已满足，且每条待办已关闭（或经用户同意明确放弃）。进行中途不得删包。

## 生命周期

1. 创建方写入 `${CF_R2_PRIVATE_BUCKET}` / `handoff/<主题>/`
2. 接手方消费并完成具名工作
3. 接手方删除该前缀全部对象
4. 无索引、无登记、无归档；每次交接独立

再次交接由用户重新触发，写入新的前缀，不引用旧包。

## 禁止事项

1. 叙事冗余文件（见上）
2. 复制接手方已能到达的源文件快照
3. 把 notes 写成操作教程（Cleanup 仅记录本记忆已规定的删除职责）
4. 主题名带日期
5. 主题未定时擅自命名上传
6. 把交接包写成会话记忆或身份持久化（「你是谁」、一般偏好属于 agent-workspace，不属于交接包）
7. 写入 `${CF_R2_PUBLIC_BUCKET}`（公开交付桶）
8. 主题名以 `handoff-` 开头
9. 任务已完成后仍把前缀留在 R2
