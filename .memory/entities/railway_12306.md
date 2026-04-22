---
id: "mem-20260422-railway"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "railway", "12306", "train", "travel", "数据源", "反爬"]
---

# 12306 官方接口全面研究

## 概览

12306 的接口分为两个域名体系：`kyfw.12306.cn`（主站）和 `search.12306.cn`（搜索子站）。
主站 `kyfw.12306.cn` 自 2026 年 4 月起大幅收紧了反爬策略，CDN/WAF 层（网宿 CDN）
直接拦截非浏览器请求返回 302 跳转至 error.html。绝大多数动态 API 已不可用。

> **2026-04 背景**：中央网信办联合国家铁路局约谈携程、同程、去哪儿、飞猪、美团、
> 智行、高铁管家等 7 家 OTA 平台，要求下架付费加速包、自动刷票功能。
> 国铁 4/16-4/18 三天拒绝出票 105.6 万张。OTA 平台的火车票查询功能面临全面调整。

## kyfw.12306.cn 接口测试结果（2026-04-22）

### 可用接口

#### 站名电报码表（静态资源）

```
GET https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
```

- **状态**：可用（HTTP 200，167KB）
- 全国 3365 个站点的完整对照表
- 格式：`@拼音缩写|中文名|三字电报码|...`
- 常用：杭州西=HVU、杭州东=HGH、杭州=HZH、杭州南=XHH、苏州=SZH、苏州北=OHH、苏州南=SMU、苏州园区=KAH、苏州新区=ITH
- 这是唯一无反爬保护的 CDN 静态资源

### 被阻断的接口（302 → error.html）

以下所有接口在沙盒 curl 环境中均被 CDN 层拦截（302 → error.html）：

| 接口路径 | 用途 | 说明 |
|----------|------|------|
| `/otn/leftTicket/queryA` | 余票查询 | 核心接口，已不可直连 |
| `/otn/leftTicket/queryG` | 余票查询（另一版本） | 同上，query 后缀字母定期变化 |
| `/otn/queryTrainInfo/query` | 车次查询 | 被拦截 |
| `/otn/leftTicketPrice/queryAllPublicPrice` | 票价查询 | 被拦截 |
| `/otn/czxx/queryByTrain` | 经停站查询 | 被拦截 |
| `/otn/trainInfo/getDelayInfo` | 正晚点查询 | 被拦截 |
| `/otn/HttpZF/GetJS` | JS 挑战 token 初始化 | 被拦截（反爬链的第一环） |
| `/otn/queryTrainInfo/getTrainSchedule` | 列车时刻表 | 被拦截 |
| `/otn/link/query` | 中转查询 | 被拦截 |

**阻断机制**：网宿 CDN `Cdn Cache Server V2.0` 在请求到达应用后端前就拦截，
返回 302 跳转到 `https://www.12306.cn/mormhweb/logFiles/error.html`。
仅添加 User-Agent / Referer / X-Requested-With 等请求头无法绕过。

#### 票价查询（软阻断）

```
GET /otn/leftTicketPrice/queryTicketPrice
```

- HTTP 200 但返回错误 JSON：`{"status":false,"messages":["系统忙，请稍后重试"]}`
- 请求到达了应用服务器但缺少会话 token 被拒绝

## search.12306.cn 接口测试结果

### 车次搜索

```
GET https://search.12306.cn/search/v1/train/search?keyword={车次号前缀}&date={YYYYMMDD}&pageIndex=1&pageSize=10
```

- **状态**：可访问（HTTP 200，返回有效 JSON）
- **能力**：按车次号前缀搜索，返回车次基本信息（起终站、车次类型等）
- **局限**：不支持站对查询；仅返回起终站信息，不含中间经停站
- 这是独立于主站的搜索子系统，反爬较轻

### 停站 / 票价

```
GET https://search.12306.cn/search/v1/train/stop  → 403
GET https://search.12306.cn/search/v1/train/price  → 403
```
均不可用。

## 突破方案

### 方案一：Cloudflare Browser Rendering + 携程（推荐）

当 12306 官方接口不可用时，通过 Cloudflare Workers Browser Rendering 访问携程移动端火车票页面：

```
# 加载页面（返回渲染后的 HTML，内嵌 JSON 数据）
GET https://m.ctrip.com/html5/flight/swift/domestic/defer_train_list?
   .ticketType=0&destType=0&fromStation=杭州西&toStation=苏州&depDate=2026-04-23

# 从 HTML 中正则提取 JSON 数据，包含：
# - trainCode (车次号)
# - departureTime / arriveTime (起止时间)
# - duration (历时)
# - 各座位价格（明文）
```

- **优势**：数据完整，含明文票价；绕过 12306 反爬
- **风险**：依赖第三方（携程）；OTA 接口可能因政策收紧而关闭
- **已验证可用**：2026-04-22 成功查询杭州西→苏州

### 方案二：12306 官网 + 浏览器自动化

理论上可通过 Playwright/Puppeteer + stealth 插件模拟真实浏览器访问 kyfw.12306.cn，
完成 JS 挑战后获取 cookie 再调 API。但：
- 实现复杂度高（需要完整浏览器环境）
- Cloudflare Browser Rendering 已能满足需求，暂无必要投入

### 方案三：12306 init → cookie → queryG 链（待重新验证）

之前的记忆中记录此链可用（init 获取 cookie → 带 cookie 请求 queryG），
但 2026-04-22 实测已被 302 拦截。可能原因：
- CDN 策略已更新
- 沙盒 IP 被标记
- 需要 JS 挑战才能获取有效 cookie
**结论：此方案当前不可靠，降级为备用。**

## API 数据格式参考（queryA/queryG 返回值）

虽然当前不可直连，但接口格式仍有参考价值（用于理解数据结构）：

```json
{
  "data": [{
    "queryLeftNewDTO": {
      "train_no": "5l000G737160",
      "station_train_code": "G7371",
      "from_station_name": "杭州西",
      "to_station_name": "苏州",
      "start_time": "09:32",
      "arrive_time": "11:35",
      "lishi": "02:03",
      "canWebBuy": "Y",
      "swz_num": "无",   // 商务座
      "zy_num": "10",    // 一等座
      "ze_num": "有",    // 二等座
      "wz_num": "--"     // 无座
    }
  }]
}
```

## 结论与策略

1. **首选**：Cloudflare Browser Rendering + 携程移动端（稳定、数据全、已验证）
2. **备选**：search.12306.cn 搜索接口（仅车次号搜索，信息有限）
3. **补充**：station_name.js 静态资源（站名→电报码映射）
4. **不稳定**：kyfw.12306.cn 动态接口（反爬严重，暂不可用）
5. **关注**：OTA 政策变化可能影响方案一；12306 可能进一步收紧或开放

---
*创建: 2026-04-22*
*更新: 2026-04-22 — 全面接口测试，10 个端点逐一验证；确认 kyfw 主站仅 station_name.js 可用；更新推荐方案为携程 Browser Rendering*
