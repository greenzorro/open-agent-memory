---
id: "mem-20261114-tc01"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "travel", "数据源", "长途汽车", "大巴", "景区门票", "开放时间", "特价机票", "火车票", "酒店", "同程"]
---

# 同程程心 (Tongcheng Chengxin) API

## 基本信息
- **服务商**: 同程旅行（程心大模型资源网关）
- **定位**: 辅助/补充旅行数据源（机票、火车票、酒店均不作主力；唯一不可替代项是长途客运 `/busResource`）
- **调用形态**: 直连网关 HTTPS JSON POST，提取原始结构化数据（不依赖 Node 包装脚本，不附带引导话术与推广页脚）
- **生产网关**: `https://wx.17u.cn/skills/gateway/api/v1/gateway`
- **参考源码**: https://github.com/infometa/workbuddyskills/tree/main/connectors/tc-chengxin

## 认证与配额边界
- **个人激活码 (`CHENGXIN_API_KEY`)**: `{your_api_key}`（需按下方申领路径自行获取）
- **申领路径**: 同程旅行 App 或微信小程序（微信 → 我 → 服务 → 火车票机票/酒店民宿），顶部搜索「程心激活码」
- **必需请求头**:
  - `Authorization: Bearer {api_key}`
  - `Origin: https://www.ly.com`
  - `Referer: https://www.ly.com/`
  - `Content-Type: application/json`
- **必需请求体字段**: `"version": "1.0.0"`
- **配额与有效期特性**:
  - 静态激活码（`tc-` 前缀 46 字符非 JWT）由服务端托管配额与有效期，HTTP 响应头不返回 `X-RateLimit-*` / `X-Quota-*` 或到期时间，网关亦不提供余额/有效期查询接口
  - 省略 `Authorization` 头时网关回落到匿名试用额度；激活码失效、过期或额度耗尽时业务层返回 `code: 3` 或鉴权失败，需按申领路径重新获取激活码替换
  - 官方另有 OAuth CLI（`@tongcheng/tc-chengxin-cli`，经 `/api/v1/oauth/cli/*` 签发短期 `access_token`），直连 JSON API 不依赖该 CLI

## 端点与职责边界

仅接入结构化资源检索端点；`/travelResource`（一键生成完整行程）会越过旅行攻略流程本身的多阶段人工决策边界，**禁止调用**。

| 端点 | 功能 | 核心参数 |
|---|---|---|
| `/busResource` | 长途汽车/客运班次、时刻、时长、票价、余票 | `departure`, `destination`（或 `departureStation`, `arrivalStation`）, `extra` |
| `/sceneryResource` | 景区详情、门票价、开放时间、游玩时长、经纬度、票务明细 | `destination`, `extra` |
| `/flightResource` | 航班查询、中转、特价机票；支持仅传 `departure` + `lowPrice: true` 发现低价目的地 | `departure`, `destination`, `flightNumber`, `lowPrice` (bool), `extra`, `query` |
| `/hotelResource` | 酒店基础检索、参考起步价、设施、口碑标签与地标距离（不含分房型价格与房态） | `destination`, `query`（含地标/预算/日期的完整自然语言，推荐必传）, `extra` |
| `/trainResource` | 火车车次、历时、参考价、席别余票 | `departure`, `destination`（或 `departureStation`, `arrivalStation`, `trainNumber`）, `extra` |
| `/trafficResource` | 未指定交通方式时综合返回火车/机票/汽车/市内接驳方案 | `departure`, `destination`, `extra` |

## 与既有数据源分工
- **长途汽车（专用主力）**: 唯一结构化公路客运查询接口（`/busResource`）
- **景区与门票核验（辅助）**: 辅助旅行攻略景点深度调研（门票、开放时间、建议游玩时长）及每日行程阶段的门票/开放状态实时核验（`/sceneryResource`）
- **机票（仅作补充，不当主力）**: 权威全量计划时刻、机型/经停、中转与舒适度以飞常准为主力（`.memory/entities/variflight_api.md`）；同程 `/flightResource` 仅用于开放式低价目的地探索（`lowPrice: true`）或节省飞常准付费额度（单次最多返回 40 条综合推荐且无分页，缺失机型、经停、多舱位报价与退改/行李规则）
- **火车票（仅作补充，不当主力）**: 余票与预售期以携程 SSR 为主力（`.memory/entities/train_query_ctrip.md`），同程 `/trainResource` 仅作兜底
- **酒店（仅作初筛辅助，不当主力）**: 多酒店分房型价格、面积/含早/取消政策对比与导出通过 `hotel-comparer` 在携程详情页完成；同程 `/hotelResource` 仅提供酒店级起步价、设施、口碑标签与地标距离，不含分房型报价与房态

## 响应结构与关键字段
- **双层信封**: `{"code": 0, "message": "success", "data": {"code": "0", "data": { ... }}}`
- **状态码**: `code` 为 `0`/`"0"` 成功；`1`/`"1"` 无匹配结果；`3` 鉴权/配置/额度异常
- **核心字段**:
  - `busDataList[].busList[]`: `coachNo`, `depCityName`, `arrCityName`, `depStationName`, `arrStationName`, `depDateTime`, `depTime`, `arrTime`, `runTimeMinutes`, `coachType`, `price`, `leftTicketNum`
  - `sceneryDataList[].sceneryList[]`（及 `needExtend`）: `resourceId`, `name`, `cityName`, `star`, `score`, `commentNum`, `price`, `isFree`, `openTime`, `playTime`, `bestPlayTime`, `describe`, `rankTitle`, `address`, `lat`, `lon`, `facilityList`, `trafficList`, `ticketEntityList`
  - `flightDataList[].flightList[]`:
    - 常规航线（按「最便宜 3 条」「最短耗时 3 条」「综合推荐最多 40 条」分组，无分页）: `flightNo`, `airlineName`, `depAirportName`, `depAirportTerminal`, `arrAirportName`, `arrAirportTerminal`, `depDate`, `depTime`, `arrDate`, `arrTime`, `runTime`, `price`（单一最低起步参考价）, `tripType`, `directFlag`, `segmentList`（联程）；`aircraft`、`productList`（多舱位报价）、`discount`、`airportTax`、`adultSurcharge`、`isCodeShareFlight`、`flightRealtimeType` 字段恒为 `null`
    - 开放低价模式（`lowPrice: true` 且无 `destination`）: `flightNo` 为 `null`，含 `arrName`, `depDate`, `week`, `price`, `originPrice`, `discount`
  - `hotelDataList[].hotelList[]`（单次最多 20 家，无分页；无分房型价格/含早/取消规则/房态）: `resourceId`, `name`, `image`, `price`（当晚起步参考价）, `dailyPrices[]`, `star`, `starLevel`, `score`, `commentNum`, `distance`, `describe`, `recommendReasons`, `cityName`, `countyName`, `bdName`, `address`, `lat`, `lon`, `phoneNumber`, `openYear`, `decorYear`, `facilities`, `hotelExtra`（含 `roomFacility`/`facilitiesNew`/`hotelLabel`/`roomLabel`/`hotelBedType`/`drillLevel`）, `roomType`（仅房型名称 JSON 字符串）, `commentTag[]`（正负面标签计数）, `sceneCommentPhrase[]`
  - `trainDataList[].trainList[]`: `trainNo`, `trainType`, `depStationName`, `arrStationName`, `depDate`, `depTime`, `arrDate`, `arrTime`, `runTime`, `price`, `ticketList`, `limiter`

## 使用注意
- **酒店地标/位置筛选必传 `query`**: `/hotelResource` 仅传 `destination` + `extra`（如 `"外滩附近"`）时位置关键词会被忽略（`pageDataList[].keyword` 为空），直接返回机场周边默认推荐；需把完整自然语言条件写入 `query`（如 `"上海外滩附近的酒店，2026-11-20入住，2026-11-21离店"`）
- **`extra` 参数为自然语言约束**: 交通/景区可传入日期、时段或偏好，如 `"明天"`、`"最早 直飞"`、`"适合亲子 免费"`
- **城市参数直接传中文**: 如 `"上海"`、`"北京"`、`"苏州"`，无需机场三字码或 12306 电报码
- **地理坐标精度**: 高德是景区精准地理编码、空间聚类与驾车距离的基准数据源（`.memory/entities/amap_api.md`）

## 示例
```python
import json
import urllib.request

API_KEY = "{your_api_key}"
BASE_URL = "https://wx.17u.cn/skills/gateway/api/v1/gateway"

def query_tongcheng(endpoint: str, params: dict) -> dict:
    payload = {**params, "version": "1.0.0"}
    ep = endpoint.lstrip("/")
    req = urllib.request.Request(
        f"{BASE_URL}/{ep}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Origin": "https://www.ly.com",
            "Referer": "https://www.ly.com/",
            "User-Agent": "TC-Chengxin-NodeJS/1.0.0",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    inner = res.get("data") or {}
    if inner.get("code") in (0, "0"):
        return inner.get("data") or {}
    return inner
```
