---
id: "mem-20260417-cfbr"
type: "entity"
env: "cloud"
confidence: "high"
tags: ["cloudflare", "browser-run", "headless-browser", "anti-crawl", "web-scraping", "screenshot", "CDP", "反爬"]
---

# Cloudflare Browser Run — 云端无头浏览器

## 能力定义

通过 Cloudflare Browser Run（原名 Browser Rendering）在云端边缘网络运行无头 Chrome 实例。核心价值：**Cloudflare 的边缘 IP 不会被常见反爬机制（如搜狗、WAF）封禁**，可作为沙盒本地浏览器被拦截时的备用通道。

## 凭证

| 属性 | 说明 |
|------|------|
| **API Token** | Cloudflare API Token（需自行申请，赋予 Browser Run 权限） |
| **Account ID** | Cloudflare Account ID（在 Dashboard → Workers & Pages 中查看） |
| **计划** | Workers Free 即可使用 |

> **部署说明**：使用前请将 Token 和 Account ID 配置为环境变量 `CF_TOKEN` 和 `CF_ACCOUNT_ID`，或在调用时直接替换下方的占位符。

## 已验证可用的 Quick Actions

| 端点 | 功能 | 用途 |
|------|------|------|
| `/content` | 获取页面 HTML | 提取网页源码 |
| `/screenshot` | 页面截图 (PNG) | 保存页面截图 |
| `/pdf` | 页面转 PDF | 生成 PDF 文件 |
| `/markdown` | 页面转 Markdown | 提取文本内容（推荐用于搜索结果解析） |
| `/json` | AI 结构化提取 | 用 prompt 提取结构化数据 |
| `/links` | 提取页面链接 | 获取页面上所有链接 |
| `/snapshot` | 页面快照 | 类似 accessibility tree |
| `/scrape` | CSS 选择器提取 | 从 HTML 中提取指定元素 |
| `/crawl` | 整站爬取 | 从起始 URL 自动发现并抓取页面 |

## 调用方式

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"    # 替换为你的 Cloudflare Account ID
CF_TOKEN="${CF_TOKEN}"            # 替换为你的 Cloudflare API Token

# 截图
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/browser-rendering/screenshot" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "viewport": {"width": 1280, "height": 720}}' \
  -o output.png

# 提取 Markdown
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/browser-rendering/markdown" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Free 计划限制

| 限制项 | 值 |
|--------|-----|
| 浏览器时间 | 10 分钟/天 |
| 并发浏览器 | 3 个 |
| 请求间隔 | 每 10 秒 1 次 (Quick Actions) |
| /crawl | 5 次/天，每次最多 100 页 |
| 浏览器超时 | 60 秒（可通过 keep_alive 延长至 10 分钟） |

## 未验证能力

- **CDP Session（Puppeteer/Playwright）**：HTTP 端点返回 404，可能需通过 Worker 或 SDK 接入
- **Live View / Human in the Loop**：需要前端 UI，沙盒内无法直接使用
- **WebMCP**：需要 Chromium 146+，属于实验性功能

## 已验证实战案例

- 搜狗微信搜索（`wx.sogou.com`）在沙盒被反爬拦截，通过 Browser Run `/markdown` 端点成功获取完整搜索结果
- 搜索关键词"中东乱局80年"和"手把手教你制作旅行攻略"均返回完整的微信公众号文章列表

## 更新历史

- 2026-04-17: 初始创建，验证全部 Quick Actions 端点
