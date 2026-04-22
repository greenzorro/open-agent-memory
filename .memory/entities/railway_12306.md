---
id: "mem-20260422-railway"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "railway", "12306", "train", "travel", "数据源"]
---

# 12306 车次查询（search.12306.cn）

## 基本信息

- **来源**: 中国铁路 12306 官方搜索接口（`search.12306.cn`）
- **性质**: 公开 REST API，无需认证、无需 API Key、无需登录
- **覆盖范围**: 全国所有国铁车次（G/D/C/Z/T/K/Y 及普速）

## 调用方式

```
GET https://search.12306.cn/search/v1/train/search?keyword={车次前缀}&date={YYYYMMDD}
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `keyword` | 是 | 车次号前缀，如 `G`、`D1`、`K`。不可为空 |
| `date` | 否 | 日期，格式 `YYYYMMDD`，默认当天 |

示例：
```bash
# 查所有高铁（单次最多200条）
curl -s "https://search.12306.cn/search/v1/train/search?keyword=G&date=20260423"

# 查某车次
curl -s "https://search.12306.cn/search/v1/train/search?keyword=G1&date=20260423"
```

## 返回字段

| 字段 | 说明 |
|------|------|
| `station_train_code` | 车次号，如 `G1`、`D3120` |
| `from_station` | 起始站名（中文） |
| `to_station` | 终到站名（中文） |
| `total_num` | 途经站数 |
| `train_no` | 内部编号（可用于其他查询） |
| `date` | 运行日期，`YYYYMMDD` |

## 使用要点

- **覆盖全车次类型**：需按前缀分别查询（`G`/`D`/`C`/`Z`/`T`/`K`），每种最多返回 200 条
- **不支持站间过滤**：keyword 按车次号匹配，返回全国所有匹配车次；按出发/到达站过滤需在本地处理
- **无时刻和票价**：只有车次号+起终站+停站数，没有发车/到达时间和票价
- **响应格式**：`{"data":[...], "status":true}`
- **无需特殊请求头**：直接 curl 即可，不反爬

## 不可用的 12306 接口

| 接口 | 状态 | 说明 |
|------|------|------|
| `kyfw.12306.cn/otn/leftTicket/queryZ` | 严格反爬 | 余票查询，需登录态+cookie，curl 和 Cloudflare BR 均被拦截 |
| `search.12306.cn/search/v1/train/stop` | 403 | 停站时刻（未公开） |
| `search.12306.cn/search/v1/train/price` | 403 | 票价（未公开） |

---
*创建: 2026-04-22*
