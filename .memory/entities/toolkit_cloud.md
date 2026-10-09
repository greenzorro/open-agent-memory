---
id: "mem-20260302-toolkit-cloud"
type: "entity"
env: "cloud"
confidence: "high"
tags: ["toolkit", "sanitized", "cloud"]
---

# _toolkit: 云端净化工具包

## 定位
`lab/_toolkit/` 是随本仓库分发的云端工具集，只保留安全、无需密钥的通用能力。

## 能力边界
**包含**：基础工具、图像处理、视频处理、Telegram API、Groq AI
**排除**：需要敏感 Key 的服务

## 用户指南
**完整文档：** `lab/_toolkit/user_guide.md`

## 依赖安装
```bash
cd lab/_toolkit
pip install -r requirements.txt
```
