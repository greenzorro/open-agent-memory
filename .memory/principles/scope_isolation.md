---
id: "mem-20260212-scope-iso"
type: "principle"
env: "global"
confidence: "high"
tags: ["memory", "boundary", "isolation"]
---

# 知识范围隔离法 (Scope Isolation Law)

## 1. 记忆防火墙设定
- **Local Knowledge (项目级)**: 凡是仅作用于特定项目（如：特定的 PSD 路径、具体的 UI 业务逻辑）的知识，**严禁**进入 `.memory/` 系统。
  - *存放地*: 对应项目目录下的 `notes.md` 或 `README.md`。
- **Global Knowledge (系统级)**: 仅允许存储具备“跨项目通用性”的底层逻辑（如：自动化审美、验证协议、环境物理法则）。

## 2. 写入审计协议 (/learn Audit)
在执行 `/learn` 或写入任何新记忆前，必须进行以下 MECE 审计：
1. **通用性验证**: “这套逻辑如果换一个完全不同的领域（如：从写代码换到写剧本），是否依然有效？”
2. **脱敏验证**: 是否包含特定的项目变量名、API Key 或具体的商业逻辑？
3. **真相源核对**: 该知识是否已经存在于某个项目的 `notes.md` 中？若是，则保持局部性，不升级为全局。

## 3. 意图
防止记忆系统产生“认知冗余”和“逻辑漂移”，保持 Agent Vik 的决策核心极其轻量且锋利。
