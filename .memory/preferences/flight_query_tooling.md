---
id: "mem-20260227-flight-query-tooling"
type: "preference"
env: "global"
confidence: "high"
tags: ["travel", "API", "automation", "航班", "机票", "飞常准", "航班查询", "机票价格", "航线", "机场", "中转", "火车票", "variflight", "flight", "aviation", "数据源"]
---

# 航班查询工具选型

**首选：飞常准 API (Variflight)**

## 选型理由
1. API直接调用，响应快、稳定
2. 数据结构化JSON，无需解析DOM
3. 覆盖范围：国内100%，全球94-97%
4. 功能完整：航班查询、中转方案、价格、天气、火车票
5. 无登录门槛，仅需API Key

## 技术详情
参见 `entities/variflight_api.md`
