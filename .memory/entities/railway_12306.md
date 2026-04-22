---
id: "mem-20260422-railway"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "railway", "12306", "train", "travel", "数据源"]
---

# 12306 官方查询接口汇总

## 可用接口

### 接口一：余票查询（kyfw.12306.cn）— 最核心

**两步流程：先获取 cookie，再查询余票。**

**Step 1 — 获取 cookie：**
```
GET https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={站名},{站码}&ts={站名},{站码}&date={YYYY-MM-DD}&flag=N,N,Y
```

响应头包含三个 Set-Cookie：
- `route=...; Path=/`
- `JSESSIONID=...; Path=/otn`
- `BIGipServerotn=...; path=/`

**Step 2 — 查询余票：**
```
GET https://kyfw.12306.cn/otn/leftTicket/queryG?leftTicketDTO.train_date={YYYY-MM-DD}&leftTicketDTO.from_station={出发站码}&leftTicketDTO.to_station={到达站码}&purpose_codes=ADULT
```

必须携带 Step 1 获取的 cookie，以及以下请求头：
- `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36`
- `Referer: https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc`
- `X-Requested-With: XMLHttpRequest`

**返回数据格式：** `data.result` 是数组，每条记录用 `|` 分隔，关键字段位置：

| 位置 | 字段 | 说明 |
|------|------|------|
| 0 | secretStr | 加密字符串（用于预订） |
| 3 | station_train_code | 车次号，如 `G8322` |
| 6 | from_station_telecode | 出发站电报码 |
| 7 | to_station_telecode | 到达站电报码 |
| 8 | start_time | 出发时间，如 `09:32` |
| 9 | arrive_time | 到达时间，如 `11:35` |
| 10 | lishi | 历时，如 `02:03` |
| 11 | canWebBuy | `Y` 可订 / `N` 不可订 |
| 21 | yp_info | 余票信息（加密） |
| 23 | swz_num | 商务座余票 |
| 25 | wz_num | 无座余票 |
| 26 | yz_num | 二等座余票 |
| 27 | rz_num | 一等座余票 |
| 28 | gr_num | 高级软卧余票 |
| 30 | edz_num | 二等座票价（加密） |
| 31 | ydz_num | 一等座票价（加密） |

**使用要点：**
- 纯 curl 可用，不需要 Cloudflare Browser
- queryG 返回所有经过出发站→到达站的车次（含始发终到和中间经停的）
- 余票和票价字段是加密的（通过 JS 端 SM4 解密），但车次、时刻、可订状态是明文
- 当前（2026.04）使用的接口是 queryG，不是 queryZ
- cookie 有时效性，建议每次查询前重新获取

### 接口二：车次搜索（search.12306.cn）

```
GET https://search.12306.cn/search/v1/train/search?keyword={车次号或前缀}&date={YYYYMMDD}
```

- 用于按车次号获取 `train_no`（配合接口三使用）
- 无需认证、无特殊请求头
- 不支持按站对查询，只有起终站信息

### 接口三：经停站查询（kyfw.12306.cn）

```
GET https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no={内部编号}&from_station_telecode={站码}&to_station_telecode={站码}&depart_date={YYYY-MM-DD}
```

- 返回完整经停站列表，包含每站的到发时间和停站时长
- 需加 `User-Agent` 请求头

### 接口四：站名电报码表（kyfw.12306.cn）

```
GET https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
```

- 全国 3365 个站点的完整对照表
- 格式：`@拼音缩写|中文名|三字电报码|...`
- 常用：杭州西=HVU、杭州东=HGH、杭州=HZH、杭州南=XHH、苏州=SZH、苏州北=OHH、苏州南=SMU、苏州园区=KAH、苏州新区=ITH

## 站对查询最佳方案

按站对查车次（如杭州西→苏州），**推荐直接使用接口一（余票查询）**：

1. 站名 URL 编码拼入 init URL 参数 `fs` 和 `ts`
2. GET init 获取 cookie
3. 带上 cookie + Referer + XHR 头请求 queryG
4. 从返回数据中筛选出发站码和到达站码
5. 如需查看经停站详情，用接口二获取 train_no 后调接口三

## 不可用的接口

| 接口 | 状态 | 说明 |
|------|------|------|
| `search.12306.cn/search/v1/train/stop` | 403 | 停站接口未公开 |
| `search.12306.cn/search/v1/train/price` | 403 | 票价接口未公开 |
| `kyfw.12306.cn/otn/leftTicket/queryZ` | 需 cookie | 旧版接口，当前前端用 queryG |
| `kyfw.12306.cn/otn/czxx/queryByStation` | 302 | 需登录 |

## 备用方案

当 12306 官方接口不稳定时，可通过 Cloudflare Browser Rendering 访问携程火车票页面获取完整信息（含明文票价）。

---
*创建: 2026-04-22*
*更新: 2026-04-22 — 发现 queryG 余票接口可通过 init cookie 访问；从"不可用"升级为"核心方案"*
