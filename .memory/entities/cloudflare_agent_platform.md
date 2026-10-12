---
id: "mem-20260417-cfap"
type: "entity"
env: "global"
confidence: "high"
tags: ["cloudflare", "api", "cloud-platform", "browser-run", "browser-rendering", "kitesurf", "chromium", "workers", "r2", "object-storage", "handoff", "ai-agent", "anti-crawl"]
---

# Cloudflare — AI Agent 云端平台

## 定位

用户为 AI Agent 专门开通的 Cloudflare 账号（Workers Free 计划），经 REST API + Bearer Token 使用。两项能力：

- **Browser Run**：云端无头浏览器，边缘 IP 不易被常见反爬封禁，可作为沙盒本地浏览器被拦截时的备用通道
- **R2 对象存储**：对象级读写，含公开交付桶 `${CF_R2_PUBLIC_BUCKET}` 与私有实验桶 `${CF_R2_PRIVATE_BUCKET}`

## 凭据与调用

| 属性 | 值 |
|------|-----|
| **API Token** | `${CF_TOKEN}` |
| **Account ID** | `${CF_ACCOUNT_ID}` |
| **账户名** | 用户 |
| **计划** | Workers Free |

```bash
ACCOUNT_ID="${CF_ACCOUNT_ID}"
CF_TOKEN="${CF_TOKEN}"

curl -s -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/<service>/<endpoint>"
```

## 能力一：Browser Run（云端无头浏览器）

别名与触发：`Browser Run`、`Browser Rendering`、`Kitesurf`、`browser=kitesurf`。

### 引擎

| 引擎 | 选用方式 | 定位 |
|------|----------|------|
| **Chromium** | 默认；不传 `browser` 参数 | 全功能无头 Chrome，兼容性最好 |
| **Kitesurf** | CDP / Quick Actions 加 `browser=kitesurf` | Agent 优先；跑在 Workers V8 isolate；CPU/内存约省 3–7×，墙钟略慢 |

选用规则：

- 需要视频、WebGL、真实 TLS 指纹过 bot、或长登录态时，用 Chromium。
- 短任务抽 HTML / 截图 / PDF、可接受非像素级渲染、要压并发成本时，用 Kitesurf。
- 站点兼容性以实测为准：https://kitesurf.cloudflare.app/

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

多步交互（点击、等待、跳转）使用 Browser Sessions（Puppeteer / Playwright / CDP），Chromium 与 Kitesurf 均兼容 CDP。

### 已知局限

- Quick Actions 为单次请求，不自动跟随多次跳转
- Kitesurf 不适用于：视频、WebGL、TLS 指纹 bot 挑战、需持久态的长认证会话
- Free 计划限制：浏览器时间 10 分钟/天；并发浏览器 3 个；Quick Actions 每 10 秒 1 次；`/crawl` 5 次/天、每次最多 100 页

## 能力二：R2 对象存储

### 桶与分工

| Bucket | 可见性 | 用途 |
|--------|--------|------|
| **`${CF_R2_PUBLIC_BUCKET}`** | 公开（自定义域名） | 交付物、给人直接打开的成品（地图 HTML、导出文件等） |
| **`${CF_R2_PRIVATE_BUCKET}`** | 私有（仅 Token 读写） | 实验/过程产物、未公开中间件；无公开域名，不存在可分享的 HTTP URL。其中 **`handoff/<主题>/`** 是全体 Agent 化身（本地 + 云端）共用的任务交接通道；规则见 `.memory/principles/handoff.md`，主题名为纯主题、不带 `handoff-` 前缀 |

### 调用方式

```bash
# 上传（非 JSON 文件必须用 Content-Type 指定 MIME，否则默认类型错误，浏览器会下载而非渲染）
PUT /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}

# 读取
GET /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}

# 列出（支持 prefix/delimiter/limit）
GET /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects

# 删除
DELETE /accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}
```

常见 MIME：HTML `text/html; charset=utf-8`、PDF `application/pdf`、PNG `image/png`、JPG `image/jpeg`、SVG `image/svg+xml`。

上传示例：

```bash
curl -s -X PUT \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: text/html; charset=utf-8" \
  --data-binary "@local_file.html" \
  "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/r2/buckets/${BUCKET}/objects/{key}"
```

### 公开访问与域名

- `${CF_R2_PUBLIC_BUCKET}` 的自定义域名：`${CF_PUBLIC_ARTIFACTS_BASE_URL}/{key}`——生成给人看的链接一律用此域名，不用 workers.dev / r2.dev 子域名
- 各桶与自定义域名的绑定关系随时可调，以查询为准：`GET /accounts/${ACCOUNT_ID}/r2/buckets/{bucket}/custom_domains`（`/domains` 等路径不存在）

### 选用规则

- 需要链接给人点开、嵌入攻略/笔记 → **`${CF_R2_PUBLIC_BUCKET}`**
- 仅 Agent/自己后续再用、不宜外泄 → **`${CF_R2_PRIVATE_BUCKET}`**
- 旅行地图等已约定产物：`${CF_R2_PUBLIC_BUCKET}`，key 建议 `travel/{project_name}/...`

### 计划限制与认证

- R2 REST API 使用 Bearer Token 认证，不需要单独的 S3 API 密钥
- Free 计划限制：10GB 存储；每月 1000 万次 Class A 操作（写入）；每月 1000 万次 Class B 操作（读取/列出）
