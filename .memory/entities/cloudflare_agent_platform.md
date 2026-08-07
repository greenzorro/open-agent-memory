---
id: "mem-20260417-cfap"
type: "entity"
env: "global"
confidence: "high"
tags: ["cloudflare", "api", "cloud-platform", "browser-run", "browser-rendering", "kitesurf", "chromium", "workers", "r2", "object-storage", "ai-agent", "anti-crawl"]
---

# Cloudflare — AI Agent 云端平台

## 定位

Cloudflare 账号可为 AI Agent 提供云端浏览器和对象存储能力。当前已验证的能力：Browser Run（云端浏览器）和 R2 对象存储。

## 凭证

| 属性 | 说明 |
|------|------|
| **API Token** | `${CF_TOKEN}` |
| **Account ID** | `${CF_ACCOUNT_ID}` |
| **R2 Bucket** | `${CF_R2_BUCKET}` |
| **公开访问域名** | `${CF_PUBLIC_ARTIFACTS_BASE_URL}` |
| **计划** | Workers Free |

> **部署说明**：使用前请将 Token、Account ID、bucket 名 和 公开域名配置为环境变量 `CF_TOKEN`、`CF_ACCOUNT_ID`、`CF_R2_BUCKET` 和 `CF_PUBLIC_ARTIFACTS_BASE_URL`，或在调用时直接替换。

## 通用调用方式

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"
CF_TOKEN="${CF_TOKEN}"

curl -s -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/<service>/<endpoint>"
```

## 能力一：Browser Run（云端无头浏览器）

在 Cloudflare 全球边缘运行无头浏览器。核心价值：**边缘 IP 不易被常见反爬封禁**，可作为沙盒本地浏览器被拦截时的备用通道。

### 引擎

| 引擎 | 选用方式 | 定位 |
|------|----------|------|
| **Chromium** | 默认；不传 `browser` 参数 | 全功能无头 Chrome，兼容性最好 |
| **Kitesurf** | CDP / Quick Actions 加 `browser=kitesurf` | Agent 优先；跑在 Workers V8 isolate；CPU/内存约省 3–7×，墙钟略慢 |

选用规则：

- 需要视频、WebGL、真实 TLS 指纹过 bot、或长登录态时，用 Chromium。
- 短任务抽 HTML / 截图 / PDF、可接受非像素级渲染、要压并发成本时，用 Kitesurf。
- 站点兼容性以实测为准：https://kitesurf.cloudflare.app/

别名与触发：`Browser Run`、`Browser Rendering`、`Kitesurf`、`browser=kitesurf`。

### Quick Actions（单次请求，无需管理会话）

API 前缀：`/browser-run/`。

| 端点 | 功能 |
|------|------|
| `/browser-run/content` | 获取页面 HTML |
| `/browser-run/screenshot` | 页面截图 (PNG) |
| `/browser-run/pdf` | 页面转 PDF |
| `/browser-run/markdown` | 页面转 Markdown |
| `/browser-run/json` | AI 结构化数据提取 |
| `/browser-run/links` | 提取页面链接 |
| `/browser-run/snapshot` | 页面快照 |
| `/browser-run/scrape` | CSS 选择器元素提取 |
| `/browser-run/crawl` | 整站爬取 |

多步交互（点击、等待、跳转）使用 Browser Sessions（Puppeteer / Playwright / CDP）。Chromium 与 Kitesurf 均兼容 CDP。

### 已知局限

- Quick Actions 为单次请求，不自动跟随多次跳转
- Kitesurf 不适用于：视频、WebGL、TLS 指纹 bot 挑战、需持久态的长认证会话

### Free 计划限制

| 限制项 | 值 |
|--------|-----|
| 浏览器时间 | 10 分钟/天 |
| 并发浏览器 | 3 个 |
| 请求间隔 | 每 10 秒 1 次 (Quick Actions) |
| /crawl | 5 次/天，每次最多 100 页 |

## 能力二：R2 对象存储

通过 REST API 对 `${CF_R2_BUCKET}` bucket 进行对象的读写和删除。可用于文件中转、产物暂存等场景。

### 调用方式

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"
CF_TOKEN="${CF_TOKEN}"
BUCKET="${CF_R2_BUCKET}"

# 上传
PUT /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}

# 读取
GET /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}

# 列出（支持 prefix/delimiter/limit 查询参数）
GET /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects

# 删除
DELETE /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}
```

上传非 JSON 文件时，必须通过 `Content-Type` 请求头指定正确的 MIME 类型，否则 R2 会默认使用错误类型，导致浏览器下载而非渲染。常见类型：

- HTML：`text/html; charset=utf-8`
- PDF：`application/pdf`
- PNG：`image/png`
- JPG：`image/jpeg`
- SVG：`image/svg+xml`

示例：

```bash
curl -s -X PUT \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: text/html; charset=utf-8" \
  --data-binary "@local_file.html" \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}"
```

### 公开访问域名

优先使用自定义公开域名生成链接，不要使用 workers.dev 子域名：

```bash
PUBLIC_BASE_URL="${CF_PUBLIC_ARTIFACTS_BASE_URL}"
echo "${PUBLIC_BASE_URL}/{key}"
```

### 注意事项

- Token 权限应仅限配置的 artifacts bucket，不要授予同账户下其他 bucket 的操作权限
- R2 REST API 使用 Bearer Token 认证，不需要单独的 S3 API 密钥
- Free 计划限制：10GB 存储、每月 1000 万次 Class A 操作（写入）、每月 1000 万次 Class B 操作（读取/列出）
