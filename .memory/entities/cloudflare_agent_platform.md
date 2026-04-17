---
id: "mem-20260417-cfap"
type: "entity"
env: "global"
confidence: "high"
tags: ["cloudflare", "api", "cloud-platform", "browser-run", "workers", "ai-agent", "anti-crawl"]
---

# Cloudflare — AI Agent 云端平台

## 定位

Victor42 为 AI Agent 专门开通的 Cloudflare 账号，API Token 授予了多个服务权限。当前已验证的能力集中在 Browser Run（云端浏览器），未来可能扩展更多 Cloudflare 服务。

## 凭证

| 属性 | 说明 |
|------|------|
| **API Token** | Cloudflare API Token（需自行申请，赋予所需服务权限） |
| **Account ID** | Cloudflare Account ID（在 Dashboard 中查看） |
| **计划** | Workers Free 即可使用 |

> **部署说明**：使用前请将 Token 和 Account ID 配置为环境变量 `CF_TOKEN` 和 `CF_ACCOUNT_ID`，或在调用时直接替换。

## 通用调用方式

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"    # 替换为你的 Cloudflare Account ID
CF_TOKEN="${CF_TOKEN}"            # 替换为你的 Cloudflare API Token

curl -s -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/<service>/<endpoint>"
```

## 已验证能力：Browser Run（云端无头浏览器）

Browser Run 在 Cloudflare 全球边缘网络运行无头 Chrome。核心价值：**Cloudflare 边缘 IP 不会被常见反爬机制封禁**，可作为沙盒本地浏览器被拦截时的备用通道。

### Quick Actions（单次请求，无需管理会话）

| 端点 | 功能 |
|------|------|
| `/browser-rendering/content` | 获取页面 HTML |
| `/browser-rendering/screenshot` | 页面截图 (PNG) |
| `/browser-rendering/pdf` | 页面转 PDF |
| `/browser-rendering/markdown` | 页面转 Markdown |
| `/browser-rendering/json` | AI 结构化数据提取 |
| `/browser-rendering/links` | 提取页面链接 |
| `/browser-rendering/snapshot` | 页面快照 |
| `/browser-rendering/scrape` | CSS 选择器元素提取 |
| `/browser-rendering/crawl` | 整站爬取 |

### 已知局限

- Quick Actions 是单次请求模式，不会自动跟随多次跳转
- 要实现多步交互（点击、等待、跳转），需要通过 Puppeteer/Playwright 接入 Browser Session（尚未验证）

### Free 计划限制

| 限制项 | 值 |
|--------|-----|
| 浏览器时间 | 10 分钟/天 |
| 并发浏览器 | 3 个 |
| 请求间隔 | 每 10 秒 1 次 (Quick Actions) |
| /crawl | 5 次/天，每次最多 100 页 |

