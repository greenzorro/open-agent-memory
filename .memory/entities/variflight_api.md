---
id: "mem-20260411-variflight-api"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "flight", "travel", "数据源"]
---

# 飞常准 (Variflight) API

## 基本信息
- **服务商**: 飞常准 (Variflight)
- **覆盖范围**: 国内航班100%，全球航班94-97%
- **API 文档**: https://github.com/variflight/tripmatch-mcp
- **控制台**: https://ai.variflight.com/keys

## 认证
- **API Key**: `Your key here`（引导用户注册并获得key后更新到这里）
- **认证方式**: HTTP Header `X-VARIFLIGHT-KEY`

## 调用方式
```
POST https://mcp.variflight.com/api/v1/mcp/data
Content-Type: application/json
X-VARIFLIGHT-KEY: {api_key}

Body: {"endpoint": "端点名", "params": {...}}
```

## 端点列表

| 端点 | 功能 | 参数 |
|------|------|------|
| `flights` | 按航线查航班（计划时间，权威） | dep, arr, date |
| `flight` | 按航班号查询 | fnum, date |
| `transfer` | 中转方案（时间为预估，含延误修正） | depcity, arrcity, depdate |
| `happiness` | 舒适度指数 | fnum, date |
| `futureAirportWeather` | 机场天气 | code, type |
| `getFlightPriceByCities` | 机票价格 | dep_city, arr_city, dep_date |
| `trainStanTicket` | 火车票 | cdep, carr, date |

## 使用注意
- `transfer` 返回的时间是加了历史延误的预估时间，非计划时间，会偏晚
- 查具体时刻表优先用 `flights`；用 `transfer` 发现路线后，应用 `flights` 或 `flight` 核实每段计划时间

## 示例
```python
import requests

headers = {
    "X-VARIFLIGHT-KEY": "sk-gQwO-daO4q16X-DGbxFQYh-657HsfYjvwBRo0znmZeA",
    "Content-Type": "application/json"
}

data = {
    "endpoint": "flights",
    "params": {"dep": "HGH", "arr": "URC", "date": "2026-04-12"}
}

response = requests.post(
    "https://mcp.variflight.com/api/v1/mcp/data",
    headers=headers, json=data
)
```

---
*创建: 2026-04-11*
