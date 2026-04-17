---
id: "mem-20260417-sgwx"
type: "entity"
env: "global"
confidence: "high"
tags: ["sogou", "wechat", "微信公众号", "search", "article", "搜狗", "反爬", "cloudflare"]
---

# 搜狗微信搜索：获取微信公众号文章

## 搜索方法

搜狗微信搜索是唯一可公开访问的微信公众号文章搜索引擎，无需登录、无需 API Key。

**搜索 URL 模板：**

```
https://wx.sogou.com/weixin?type=2&query={keyword}
```

- `type=2`：搜索微信公众号文章
- `keyword`：URL 编码的搜索关键词
- 搜索结果为 HTML 页面，包含文章标题、公众号名、摘要、链接

## 执行策略

### 主路径：当前环境的本地浏览器

优先使用当前运行环境自带的浏览器工具（如 agent-browser、Playwright 等）直接访问搜狗微信搜索页面并提取结果。

### 备用路径：Cloudflare 云端浏览器（反爬拦截时启用）

当本地浏览器被搜狗反爬机制拦截（headless browser detection、403、验证码等），**切换到 Cloudflare Browser Run**，因为 Cloudflare 的边缘 IP 不会被搜狗封禁。凭证与调用方式见 → `cloudflare_agent_platform.md`。

## 决策逻辑

```
搜索微信公众号文章
    ├── 本地浏览器可用？
    │   ├── 是 → 使用本地浏览器（零成本，无速率限制）
    │   └── 否（被反爬拦截）→ 切换到 Cloudflare Browser Run
        ├── 调用 /markdown 端点获取搜索结果
        └── 注意 Free 计划每 10 秒 1 次请求
```

## 局限性

- 搜狗收录范围非全量（用户的文章可能搜不到，即使标题完全匹配）
- 搜狗排序算法不透明，同名文章不一定排在第一位
- 搜狗无主动提交入口，收录是黑盒
- 搜索结果中的文章链接经搜狗多次跳转后最终到达微信公众号原文页（GUI 浏览器中已验证）；但 Cloudflare Browser Run 的 Quick Actions 是单次请求模式，无法自动跟随多次跳转，因此尚未通过云端路径成功到达原文页

## 更新历史

- 2026-04-17: 初始创建，建立本地+云端双路径策略
