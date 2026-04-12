---
id: "mem-20260411-nbsapi"
type: "preference"
env: "global"
confidence: "medium"
tags: ["NBS", "national-bureau-of-statistics", "cn-stats", "API", "reverse-engineered", "crawler", "数据收集", "宏观数据", "统计数据", "数据源", "国家统计局", "经济指标", "人口数据", "分省数据", "城市数据", "价格指数", "CPI", "逆向接口", "事实标准"]
---

# 国家统计局数据获取 (cn-stats)

## 概述
国家统计局 (`data.stats.gov.cn`) 没有公开的官方 API。社区广泛使用逆向工程接口 `easyquery.htm`，形成事实标准。推荐通过 PyPI 包 `cn-stats` (导入名 `cnstats`) 调用，而非手写 HTTP 请求。

## 安装
```bash
pip install cn-stats
```
注意：pip 包名 `cn-stats`（连字符），Python 导入名 `cnstats`（无连字符）。
最新版本：0.1.3 (2026-03)，依赖 `requests`, `pandas`, `urllib3<2`。

## 核心 API

### 数据查询 — `cnstats.stats.stats()`
```python
from cnstats.stats import stats

result = stats(
    zbcode='A090201',        # 指标代码（必填）
    datestr='2024',          # 日期：YYYY（年度）或 YYYYMM（月度），支持逗号分隔多日期
    regcode=None,            # 地区代码，如 '110000'（北京），可选
    dbcode='hgyd',           # 数据库代码（默认 hgyd）
    as_df=False,             # True 返回 pandas DataFrame
)
```

**返回格式** (`as_df=False`)：
- 无 regcode：`[[指标名称, 指标代码, 查询日期, 数值], ...]`
- 有 regcode：`[[指标名称, 指标代码, 地区名称, 地区代码, 查询日期, 数值], ...]`

### 浏览指标树 — `cnstats.zbcode.get_tree()`
```python
from cnstats.zbcode import get_tree
get_tree('A09', dbcode='hgnd')  # 查看某分类下的所有指标
```

### 地区代码 — `cnstats.regcode.get_reg()`
```python
from cnstats.regcode import get_reg
provinces = get_reg('fsyd')   # 省级
cities = get_reg('csnd')      # 城市
```

## 数据库代码 (dbcode)

| dbcode | 说明 | 粒度 | 频率 |
|--------|------|------|------|
| `hgyd` | 宏观月度 | 全国 | 月度（**默认**）|
| `hgjd` | 宏观季度 | 全国 | 季度 |
| `hgnd` | 宏观年度 | 全国 | 年度 |
| `fsyd` | 分省月度 | 省级 | 月度 |
| `fsjd` | 分省季度 | 省级 | 季度 |
| `fsnd` | 分省年度 | 省级 | 年度 |
| `csyd` | 城市月度 | 城市 | 月度 |
| `csjd` | 城市季度 | 城市 | 季度 |
| `csnd` | 城市年度 | 城市 | 年度 |

规律：前2字符=级别(hg宏观/fs分省/cs城市)，后2字符=频率(yd月/jd季/nd年)。

## 已验证的指标示例

| 指标 | 代码 | 数据库 |
|------|------|--------|
| 居民消费价格指数(1978=100) | A090201 | hgnd |
| CPI上年同月=100 (2016+) | A010101 | hgyd |
| 省级CPI (2021+) | A01010B01 | fsyd |

不同数据库中的指标代码可能不同，用 `get_tree()` 确认。

## 风险与限制
- **非官方接口**：`easyquery.htm` 是逆向工程所得，无官方文档、无 SLA
- **WAF 封锁**：云服务器 IP 常被拦截（403 UrlACL），在 GitHub Actions runner 上可正常访问
- **无版本管理**：接口参数可能随时变更
- **置信度**：medium（事实标准但非官方）

## 复用参考
- 模板模式：`stats()` → 数据处理 → CSV，换 zbcode/dbcode 即可复用

## 社区生态
- `cn-stats` (PyPI)：https://pypi.org/project/cn-stats/
- `cnstats` (GitHub)：https://github.com/songjian/cnstats
- `nbsc` (GitHub)：另一个可选的 NBS 数据获取库
- 所有社区方案底层均调用同一 `easyquery.htm` 接口
