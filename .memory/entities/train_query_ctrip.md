---
id: "mem-20260422-train-ctrip"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "railway", "train", "travel", "数据源", "携程", "SSR"]
---

# 火车票余票查询

## 方案一：携程PC端 SSR（推荐）

携程PC端火车票列表页使用 Next.js 服务端渲染，车次数据直接嵌入在 HTML 的 `__NEXT_DATA__` JSON 中，无需浏览器或反爬绕过，一个 HTTP 请求即可获取全部车次数据。

- **数据源**：携程PC端 trains.ctrip.com
- **技术**：普通 HTTP GET 请求，解析 HTML 中的 `<script id="__NEXT_DATA__">` JSON
- **能力**：车次信息 + 票价 + 余票数量 + 历时 + 是否可预订 + 始发终到标识 + 座位类型
- **无需**：浏览器渲染、Cookie、登录、反反爬
- **无 User-Agent 要求**：即使不设置 UA 也能正常返回数据
- **响应大小**：约 200-400KB（含 HTML + JSON 数据）

### 请求格式

```
GET https://trains.ctrip.com/webapp/train/list?ticketType=0&dStation={出发城市}&aStation={到达城市}&dDate={YYYY-MM-DD}&rDate=&trainsType=&hubCityName=&highSpeedOnly=0
```

### URL 参数

| 参数 | 说明 | 示例 |
|------|------|------|
| ticketType | 票种：0=单程, 1=往返, 2=中转 | 0 |
| dStation | 出发城市（中文URL编码） | 上海 |
| aStation | 到达城市（中文URL编码） | 北京 |
| dDate | 出发日期 | 2026-05-01 |
| rDate | 返程日期（往返时使用） | |
| trainsType | 车型筛选（空=全部） | G=高铁 |
| hubCityName | 中转城市 | |
| highSpeedOnly | 是否只看高铁动车：0=否, 1=是 | 0 |

### 数据提取方式

从返回的 HTML 中用正则提取：

```python
import re, json
match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
trains = data['props']['pageProps']['initialState']['trainSearchInfo']['trainInfoList']
```

### 每趟车的数据字段

| 字段 | 说明 |
|------|------|
| trainNumber | 车次号，如 G2 |
| departureStationName | 出发站名，如 上海虹桥 |
| arrivalStationName | 到达站名，如 北京南 |
| departureTime | 出发时间，如 06:43 |
| arrivalTime | 到达时间，如 11:32 |
| duration | 历时，如 4时49分 |
| runTime | 运行分钟数，如 289 |
| isStartStation | 是否始发站 |
| isEndStation | 是否终到站 |
| isBookable | 是否可预订 |
| isSaleStop | 是否停售 |
| isFuXingTrain | 是否复兴号 |
| startPrice | 最低票价（分） |
| preSaleDay | 预售天数 |
| preSaleTime | 预售时间点 |
| seatItemInfoList | 座位信息数组（见下方） |

### 座位信息字段（seatItemInfoList 中的每个元素）

| 字段 | 说明 |
|------|------|
| seatName | 座位类型名，如 二等座/一等座/商务座/无座/软卧 |
| seatPrice | 票价（元） |
| seatBookable | 是否可购买 |
| seatInventory | 余票数量（仅可购时有效） |
| discountRate | 折扣率，如 0.91 表示9.1折 |
| forecastSeatPriceList | 学生票/儿童票预估价 |

### Python 查询示例

```python
import urllib.request
import urllib.parse
import re
import json

def query_trains(departure, arrival, date):
    params = urllib.parse.urlencode({
        "ticketType": "0",
        "dStation": departure,
        "aStation": arrival,
        "dDate": date,
        "rDate": "",
        "trainsType": "",
        "hubCityName": "",
        "highSpeedOnly": "0",
    })
    url = f"https://trains.ctrip.com/webapp/train/list?{params}"

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8')

    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not match:
        return None

    data = json.loads(match.group(1))
    return data['props']['pageProps']['initialState']['trainSearchInfo']['trainInfoList']
```

### 已知限制

- 当日车次若超出预售期，返回空列表（非报错），需检查预售天数
- 站名使用中文城市名（如"上海"），非电报码

## 方案二：Cloudflare Browser Rendering + 携程移动端

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
