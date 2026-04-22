---
id: "mem-20260422-train-ctrip"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "railway", "train", "travel", "数据源", "携程", "Browser-Rendering"]
---

# 火车票余票查询方案

## 唯一方案：Cloudflare Browser Rendering + 携程移动端 ⭐

通过 Cloudflare Workers Browser Rendering 访问携程移动端火车票查询页面，获取余票和票价信息。

- **数据源**：携程移动端 m.ctrip.com
- **技术**：Cloudflare Browser Rendering（Puppeteer）
- **能力**：余票数量 + 明文票价 + 车次信息 + 历时
- **合规性**：纯查询，不涉及自动化购票，不受 2026-04 约谈政策影响
- **稳定性**：已验证可用（2026-04-22）

## 12306 静态资源（唯一保留）

### 站名电报码映射表

```
GET https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
```

- 无反爬保护，HTTP 200，可直接 curl 获取
- 全国 3365 个站点的完整站名↔电报码对照表
- 用于将中文站名转换为携程查询所需参数（携程页面直接支持中文输入，此表主要用于本地缓存和快速查找）
- 常用站点代码备查：杭州西=HVU、杭州东=HGH、杭州=HZH、杭州南=XHH、苏州=SZH、苏州北=OHH、苏州南=SMU

## 政策背景（2026-04）

- 4/10：中央网信办联合国家铁路局约谈 7 家 OTA 平台，禁止自动化大规模高频次抢票
- 政策收紧的是**购票渠道**，不是**查询渠道**
- 携程商旅关闭火车票预订入口，但消费端保留基础查询与跳转功能
- 12306 官方接口（kyfw/hzfw）技术层面已全面封锁非浏览器请求，不再作为可行方案

## 不再考虑的方案

- ~~12306 kyfw/hzfw API~~ — WAF 全面拦截，不可靠
- ~~search.12306.cn~~ — 功能有限，仅车次号搜索
- ~~其他 OTA 平台直连 API~~ — 均无公开接口


