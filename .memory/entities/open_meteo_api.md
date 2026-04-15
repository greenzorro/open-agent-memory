---
id: "mem-20260414-omet"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "weather", "forecast", "geocoding", "数据源", "天气", "天气预报", "open-meteo"]
---

# Open-Meteo 免费天气 API

## 基本信息
- **服务商**: Open-Meteo (开源)
- **认证**: 无需，完全匿名，无需 API Key
- **文档**: https://open-meteo.com/en/docs

## 能力概览

| API | 用途 | 文档链接 |
|-----|------|---------|
| 天气预报 API | 未来 ~16 天逐日/逐时天气 | https://open-meteo.com/en/docs |
| 地理编码 API | 城市名 → 经纬度坐标 | https://open-meteo.com/en/docs/geocoding-api |
| 历史天气 API | 1940 年至今的历史天气 | https://open-meteo.com/en/docs/historical-weather-api |
| 空气质量 API | PM2.5、臭氧等空气质量指标 | https://open-meteo.com/en/docs/air-quality-api |

## 地理编码

**用途**: 将城市名转换为经纬度，供天气 API 使用。

```bash
GET https://geocoding-api.open-meteo.com/v1/search?name={CITY}&count=1&language=zh&format=json
```

**参数**:
- `name`: 城市名（**优先使用英文或拼音**，如 `Jinghong` 而非 `景洪`，中文名可能无结果）
- `count`: 返回结果数量
- `language`: 响应语言（`zh`/`en`）

**返回字段**: `latitude`, `longitude`, `name`, `country`

## 天气预报

```bash
GET https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily={VARS}&timezone=Asia/Shanghai&start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}
```

**常用 daily 变量**:
- `temperature_2m_max` / `temperature_2m_min` — 最高/最低气温
- `precipitation_probability_max` — 降水概率
- `precipitation_sum` — 降水量
- `windspeed_10m_max` — 最大风速

**限制**:
- 预报范围仅覆盖未来约 **16 天**
- 超出范围会返回错误：`Parameter 'start_date' is out of allowed range`

## 关键避坑

- **城市名用英文/拼音**: 中文名常无匹配结果，如用 `Hangzhou` 而非 `杭州`
- **先查坐标再查天气**: 不要依赖 AI 内置坐标，调用地理编码 API 获取精确坐标，避免幻觉和同名城市歧义
- **日期范围检查**: 查询前确认日期在 16 天预报窗口内，超出则标注"暂无预报"
- **无需鉴权**: 没有 API Key，没有调用频率限制（但建议 QPS ≤ 10 保持稳定）
