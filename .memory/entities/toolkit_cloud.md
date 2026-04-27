---
id: "mem-20260302-toolkit-cloud"
type: "entity"
env: "cloud"
confidence: "high"
tags: ["toolkit", "sanitized", "routine"]
---

# _toolkit: 云端净化工具包

## 背景
**routine** 是本地的全能工具集（文件处理、数据转换、自动化、音视频处理），但包含敏感 API Key。

**_toolkit** 是 `routine` 的净化副本：
- 仅保留安全功能
- 移除所有敏感 API Key（Gemini、DeepSeek、Kimi、OpenRouter、Replicate、Feishu、RunComfy）
- 通过 GitHub 同步到云端

## 能力边界
**包含**：基础工具、图像处理、视频处理、Telegram API、Groq/Cerebras AI
**排除**：需要敏感 Key 的服务

## 用户指南
**完整文档：** `lab/_toolkit/user_guide.md`

## 依赖安装
```bash
cd ~/agent-workspace/lab/_toolkit
pip install -r requirements.txt
```
