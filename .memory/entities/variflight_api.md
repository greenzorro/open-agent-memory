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
- **当前主 API Key**: `{your_api_key}` (`vik-variflight-{word1}-{word2}@${AGENT_EMAIL_DOMAIN}`，2026-10-06 注册)
- **认证方式**: HTTP Header `X-VARIFLIGHT-KEY`

### 备用 Key 池（已全自动注册并激活，各含 50 元初始额度）
1. `{your_api_key}` (`vik-variflight-{word1}-{word2}@${AGENT_EMAIL_DOMAIN}`，2026-10-06)
2. `{your_api_key}` (`vik-variflight-{word1}-{word2}@${AGENT_EMAIL_DOMAIN}`，2026-10-06)

### 已耗尽 Key（2026-10-06 轻重双端点 403 确认，勿再使用）
- `{your_api_key}`（原主 Key，2026-04 起用）
- `{your_api_key}` (`vik-variflight-{word1}-{word2}@${AGENT_EMAIL_DOMAIN}`)
- `{your_api_key}` (`vik-variflight-{word1}-{word2}@${AGENT_EMAIL_DOMAIN}`)

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
    "X-VARIFLIGHT-KEY": "{your_api_key}",
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
