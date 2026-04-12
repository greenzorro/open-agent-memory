---
id: "mem-20260227-url-injection-rule"
type: "principle"
env: "global"
confidence: "high"
tags: ["automation", "protocol", "scraping"]
---

# Web 自动化 URL 注入优先级准则

* **执行协议**：在处理带有复杂 DOM 结构、动态验证码或自定义 UI 组件（如 OTA 平台的筛选器）时，**构造 URL 参数注入查询条件**的优先级高于**模拟鼠标/键盘 UI 点击**。
* **逻辑优势**：URL 注入直接与服务端交互，规避了前端渲染延迟、元素不可见、UID 变更或反爬机制对模拟操作的干扰。
* **最佳实践**：优先分析目标站点的 URL Query String 结构（如 `child=1`, `directonly=true`），将其作为自动化的第一控制点。
