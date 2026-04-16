---
id: "mem-20260416-arx1"
type: "entity"
env: "cloud"
confidence: "high"
tags: ["arxiv", "academic", "paper", "pdf", "search", "full-text"]
---

# ArXiv 论文搜索与全文获取

## 能力定义

通过 ArXiv 官方 API 实现论文搜索 + PDF 下载 + 正文提取的完整链路。零成本、零注册、零 API Key。

## 接口信息

| 属性 | 值 |
|------|-----|
| **搜索 API** | `https://export.arxiv.org/api/query?search_query={query}&start=0&max_results={n}` |
| **协议** | Atom XML（需用 `-sL` 跟随重定向） |
| **速率限制** | 每 3 秒最多 1 个请求 |
| **PDF 下载** | 搜索结果中 `rel="related" type="application/pdf"` 的 `href` |
| **正文提取** | PyMuPDF (`pymupdf`) 已安装于沙盒，`fitz.open()` 解析 PDF |

## 搜索语法

| 查询方式 | 示例 |
|---------|------|
| 全字段搜索 | `all:transformer` |
| 标题搜索 | `ti:attention+is+all+you+need` |
| 作者搜索 | `au:Vaswani` |
| 分类限定 | `cat:cs.CV+AND+all:segmentation` |
| 组合查询 | `all:transformer+AND+all:attention` |

## 学科覆盖范围

物理、数学、计算机科学（CS/AI）、量化生物、量化金融、统计学、电气工程、系统科学。

## 局限性

- 仅覆盖 ArXiv 收录的预印本/论文，非全学科（无医学、化学、人文社科）
- PDF 为预印本版本，可能与最终出版版本有差异
- 搜索接口返回 XML 格式，需解析
