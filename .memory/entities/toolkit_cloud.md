---
id: "mem-20260302-toolkit-cloud"
type: "entity"
env: "cloud"
confidence: "high"
tags: ["toolkit", "sanitized", "cloud"]
---

# _toolkit: 云端净化工具包

## 定位
`lab/_toolkit/` 是随本仓库分发的云端工具集：基础的文件/图像/视频处理，以及依赖 API Key 的服务（AI、Telegram、邮件等）。

## 凭据
所有敏感 API Key 均已替换为占位符，仓库内不含任何真实凭据；使用这些能力时需自行提供 Key。

## 用户指南
**完整文档：** `lab/_toolkit/user_guide.md`

## 依赖安装
```bash
cd lab/_toolkit
pip install -r requirements.txt
```
