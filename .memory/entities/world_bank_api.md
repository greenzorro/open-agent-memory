---
id: "mem-20260411-wbapi"
type: "entity"
env: "global"
confidence: "high"
tags: ["world-bank", "API", "macro-data", "automation", "crawler", "数据收集", "宏观数据", "国际数据", "统计数据", "数据源", "经济指标", "人口数据", "跨国对比", "公开API", "GDP", "CPI"]
---

# 世界银行开放数据 API

## 接口规范
- **文档**：https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- **基址**：`https://api.worldbank.org/v2/country/{country}/indicator/{indicator}`
- **格式参数**：`?format=json`（默认 XML）
- **日期范围**：`&date=2019:2026`
- **分页**：`&per_page=50`（默认 50，最大 2000）
- **鉴权**：无需，完全匿名

## 常用指标代码
- `NY.GDP.MKTP.CD` — GDP (current US$)
- `SP.POP.TOTL` — 总人口
- `FP.CPI.TOTL` — CPI
- 完整指标列表：https://data.worldbank.org/indicator

## 国家代码
- `WLD` — 全球
- `CHN` — 中国
- `all` — 所有国家

## 限制
- 建议 QPS ≤ 1
- 单次请求最大 2000 条

## 稳定性评估
- 官方 SLA 承诺，有版本管理（v2）
- 与国家统计局 `data.stats.gov.cn` 逆向接口形成对比（后者无文档、有 WAF、随时可能改版）
- 宏观经济数据首选此 API

## 复用参考
- 模板模式：fetch → process → save_to_csv，换 indicator code 即可复用
