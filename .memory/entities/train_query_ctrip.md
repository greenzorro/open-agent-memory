---
id: "mem-20260422-train-ctrip"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "railway", "train", "travel", "数据源", "携程", "Browser-Rendering"]
---

# 火车票余票查询

## 方案：Cloudflare Browser Rendering + 携程移动端

通过 Cloudflare Workers Browser Rendering 访问携程移动端火车票查询页面，获取余票和票价信息。

- **数据源**：携程移动端 m.ctrip.com
- **技术**：Cloudflare Browser Rendering（Puppeteer）
- **能力**：余票数量 + 明文票价 + 车次信息 + 历时

## 12306 静态资源：站名电报码映射表

```
GET https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
```

- 无反爬保护，可直接 curl 获取
- 全国 3365 个站点的完整站名↔电报码对照表

