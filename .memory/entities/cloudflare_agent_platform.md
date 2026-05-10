---
id: "mem-20260417-cfap"
type: "entity"
env: "global"
confidence: "high"
tags: ["cloudflare", "api", "cloud-platform", "browser-run", "workers", "r2", "object-storage", "ai-agent", "anti-crawl"]
---

# Cloudflare — AI Agent 云端平台

## 定位

Cloudflare 账号可为 AI Agent 提供云端浏览器和对象存储能力。当前已验证的能力：Browser Run（云端浏览器）和 R2 对象存储。

## 凭证

| 属性 | 说明 |
|------|------|
| **API Token** | Cloudflare API Token（需自行申请，赋予所需服务权限） |
| **Account ID** | Cloudflare Account ID（在 Dashboard 中查看） |
| **R2 Bucket** | 用于 artifacts 或文件中转的 R2 bucket 名称 |
| **公开访问域名** | 可选，自定义绑定到 R2 bucket 的公开域名 |
| **计划** | Workers Free 即可使用 |

> **部署说明**：使用前请将 Token、Account ID、bucket 名和公开域名配置为环境变量 `CF_TOKEN`、`CF_ACCOUNT_ID`、`CF_R2_BUCKET` 和 `CF_PUBLIC_ARTIFACTS_BASE_URL`，或在调用时直接替换。

## 通用调用方式

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"    # 替换为你的 Cloudflare Account ID
CF_TOKEN="${CF_TOKEN}"            # 替换为你的 Cloudflare API Token

curl -s -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/<service>/<endpoint>"
```

## 能力一：Browser Run（云端无头浏览器）

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

## 能力二：R2 对象存储

通过 REST API 对 R2 bucket 进行对象的读写和删除。可用于文件中转、产物暂存等场景。

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

上传非 JSON 文件时，必须通过 `Content-Type` 请求头指定正确的 MIME 类型，否则 R2 可能默认使用错误类型，导致浏览器下载而非渲染。常见类型：

- HTML：`text/html; charset=utf-8`
- PDF：`application/pdf`
- PNG：`image/png`
- JPG：`image/jpeg`
- SVG：`image/svg+xml`

示例：

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"
CF_TOKEN="${CF_TOKEN}"
BUCKET="${CF_R2_BUCKET}"

curl -s -X PUT \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: text/html; charset=utf-8" \
  --data-binary "@local_file.html" \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}"
```

### 公开访问域名

如果 bucket 已绑定自定义公开域名，优先使用该域名生成公开链接：

```bash
PUBLIC_BASE_URL="${CF_PUBLIC_ARTIFACTS_BASE_URL}"
echo "${PUBLIC_BASE_URL}/{key}"
```

不要在开源记忆中写入私有账号、专属 bucket 名、私有域名或真实 Token。

### 注意事项

- R2 REST API 使用 Bearer Token 认证，不需要单独的 S3 API 密钥
- Token 需要授予对应 bucket 的读写权限
- Free 计划限制：10GB 存储、每月 1000 万次 Class A 操作（写入）、每月 1000 万次 Class B 操作（读取/列出）
