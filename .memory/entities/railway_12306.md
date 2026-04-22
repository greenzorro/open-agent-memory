---
id: "mem-20260422-railway"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "railway", "12306", "train", "travel", "数据源"]
---

# 12306 官方查询接口汇总

## 可用接口

### 接口一：车次搜索（search.12306.cn）

```
GET https://search.12306.cn/search/v1/train/search?keyword={车次号或前缀}&date={YYYYMMDD}
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `keyword` | 是 | 车次号（精确）或前缀（如 `G`），不可为空 |
| `date` | 否 | 日期，格式 `YYYYMMDD`，默认当天 |

**返回字段：** `station_train_code`（车次号）、`from_station`（起始站）、`to_station`（终到站）、`total_num`（停站数）、`train_no`（内部编号）、`date`（日期）

**使用要点：**
- 前缀查询（如 `keyword=G`）最多返回 200 条，需精确车次号查询可用 `keyword=G8322`
- 不支持按出发/到达站筛选，需本地处理
- 无时刻、无票价、无经停站信息
- 无需认证、无特殊请求头

### 接口二：经停站查询（kyfw.12306.cn）

```
GET https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={内部编号}&from_station_telecode={出发站码}&to_station_telecode={到达站码}&depart_date={YYYY-MM-DD}
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `train_no` | 是 | 内部编号（从接口一获取） |
| `from_station_telecode` | 是 | 出发站电报码（三个大写字母） |
| `to_station_telecode` | 是 | 到达站电报码 |
| `depart_date` | 是 | 日期，格式 `YYYY-MM-DD` |

**返回字段：** 每站包含 `station_name`（站名）、`station_no`（站序）、`arrive_time`（到达时间）、`start_time`（出发时间）、`stopover_time`（停站时长，如"2分钟"）、`start_station_name`（始发站）、`end_station_name`（终到站）

**使用要点：**
- 需要配合接口一使用：先用 search 获取 `train_no`，再用此接口查经停
- `from_station_telecode` 和 `to_station_telecode` 只需要填起终站码，中间站信息全部返回
- 需加 `User-Agent: Mozilla/5.0` 请求头，否则可能被拒
- 无需登录态，curl 直接可用
- 完整的到发时间 + 停站时长，可实现站间时刻查询

### 接口三：站名电报码表（kyfw.12306.cn）

```
GET https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
```

- 全国 3365 个站点的完整对照表
- 格式：`@拼音缩写|中文名|三字电报码|拼音全拼|拼音首字母|序号|所属路局|省份|||`
- 示例：`@hzx|杭州西|HVU|hangzhouxi|hzx|...`
- 常用站码：杭州西=HVU、杭州东=HGH、杭州=HZH、杭州南=XHH、苏州=SZH、苏州北=OHH、苏州南=SMU、苏州园区=KAH、苏州新区=ITH

## 组合查询方案

按站对查车次（如杭州西→苏州）的完整流程：

1. 从携程等第三方通过 Cloudflare Browser Rendering 获取车次列表（带时间、票价）
2. 用 12306 search API 精确查询获取 `train_no`
3. 用 12306 czxx 接口查询经停站信息（到发时间、中间经停）

直接用 12306 两接口的组合无法实现按站对搜索，因为 search API 只返回起终站信息，不知道中间经停哪些站。

## 不可用的接口

| 接口 | 状态 | 说明 |
|------|------|------|
| `kyfw.12306.cn/otn/leftTicket/queryZ` | 严格反爬 | 余票查询，curl 和 CF BR 均被拦截（返回"网络可能存在问题"错误页） |
| `search.12306.cn/search/v1/train/stop` | 403 | 停站接口未公开 |
| `search.12306.cn/search/v1/train/price` | 403 | 票价接口未公开 |
| `search.12306.cn/search/v1/train/info` | 403 | |
| `search.12306.cn/search/v1/train/schedule` | 403 | |
| `search.12306.cn/search/v1/station/*` | 403 | |
| `kyfw.12306.cn/otn/leftTicket/queryA` | 302（重定向） | 需登录 |
| `kyfw.12306.cn/otn/czxx/queryByStation` | 302（重定向） | 需登录 |

## 第三方查询方案

当 12306 官方接口不足时，可通过 Cloudflare Browser Rendering 访问携程火车票页面获取完整信息：

```
POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/browser-rendering/content
{
  "url": "https://trains.ctrip.com/webapp/train/list?ticketType=0&dStation=杭州西&aStation=苏州&dDate=2026-04-23"
}
```

- 返回 HTML 中嵌入了完整 JSON 数据（`trainInfoList` 字段）
- 包含车次、时刻、历时、票价、是否可订等全部信息
- 站名用 URL 编码中文传递
- 缺点：消耗 Cloudflare BR 配额（Free 计划每天 10 分钟浏览器时间）

---
*创建: 2026-04-22*
*更新: 2026-04-22 — 新增 czxx 经停站接口、station_name.js 站码表、携程 BR 方案*
