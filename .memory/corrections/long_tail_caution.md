---
id: "mem-20260212-lt-caution"
type: "correction"
env: "global"
confidence: "high"
tags: ["hallucination", "verification", "search"]
---

# 长尾知识验证协议

## 1. 幻觉警戒
- **长尾不推测**: 对于涉及具体的物理常识、地缘政治冷知识、冷门软件参数或特定生物学细节，严禁仅依赖模型内部权重进行推理。
- **搜索先行**: 遇到此类“长尾知识”，必须强制调用 `google_web_search` 或 `tavily_search`。

## 2. 验证路径
- **网络总结优于模型权重**: 优先总结实时抓取的网页内容（特别是维基百科、Kaggle、或 Architect 认可的专业博客）。
- **标注未验证项**: 如果搜索无法覆盖，必须明确标注“未找到经过验证的事实”，严禁编造看似合理的解释。
