---
id: "mem-20260227-flight-query-tooling"
type: "preference"
env: "global"
confidence: "high"
tags: ["travel", "API", "automation", "航班", "机票", "特价机票", "飞常准", "同程", "航班查询", "机票价格", "航线", "机场", "中转", "火车票", "variflight", "flight", "aviation", "数据源"]
---

# 航班查询工具选型

**首选：飞常准 API (Variflight)**

## 选型理由
1. API直接调用，响应快、稳定
2. 数据结构化JSON，无需解析DOM
3. 覆盖范围：国内100%，全球94-97%
4. 功能完整：航班查询、中转方案、价格、天气、火车票
5. 无登录门槛，仅需API Key

## 场景分工与补充源
- **常规航线、权威计划时刻、中转核实与舒适度**：使用飞常准 API（`.memory/entities/variflight_api.md`）
- **开放式特价/低价目的地发现或节省飞常准付费额度**：使用同程程心 API `/flightResource`（支持仅传 `departure` + `lowPrice: true`，`.memory/entities/tongcheng_chengxin_api.md`）

## 技术详情
参见 `entities/variflight_api.md`、`entities/tongcheng_chengxin_api.md`
