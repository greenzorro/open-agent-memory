---
id: "mem-20260417-sgwx"
type: "entity"
env: "cloud"
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

### 主路径：沙盒本地浏览器（agent-browser）

```bash
agent-browser open "https://wx.sogou.com/weixin?type=2&query={keyword}"
agent-browser snapshot -i
```

### 备用路径：Cloudflare 云端浏览器（反爬拦截时启用）

当沙盒本地浏览器被搜狗反爬机制拦截（headless browser detection、403、验证码等），**必须切换到 Cloudflare Browser Run**，因为 Cloudflare 的边缘 IP 不会被搜狗封禁。

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"    # 替换为你的 Cloudflare Account ID
CF_TOKEN="${CF_TOKEN}"            # 替换为你的 Cloudflare API Token

curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/browser-rendering/markdown" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://wx.sogou.com/weixin?type=2&query={keyword}"}'
```

> 凭证与详细调用方式见 → `cloudflare_browser_run.md`

## 决策逻辑

```
搜索微信公众号文章
    ├── 沙盒本地 agent-browser 可用？
    │   ├── 是 → 使用本地浏览器（零成本，无速率限制）
    │   └── 否（被反爬拦截）→ 使用 Cloudflare Browser Run
    │       ├── 调用 /markdown 端点获取搜索结果
    │       └── 注意 Free 计划每 10 秒 1 次请求
```

## 局限性

- 搜狗收录范围非全量（用户的文章可能搜不到，即使标题完全匹配）
- 搜狗排序算法不透明，同名文章不一定排在第一位
- 搜狗无主动提交入口，收录是黑盒
- 搜索结果中的文章链接指向搜狗的跳转页，非公众号原文直链

## 更新历史

- 2026-04-17: 初始创建，建立本地+云端双路径策略
