---
id: "mem-20260412-amap-api"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "map", "geography", "travel", "数据源"]
---

# 高德地图 (Amap) Web服务API

## 基本信息
- **服务商**: 高德开放平台
- **覆盖范围**: 中国大陆全境（含港澳，不含台湾详细地址）
- **API 文档**: https://lbs.amap.com/api/webservice/guide/api/summary
- **控制台**: https://console.amap.com

## 认证
- **API Key**: `Your key here`（引导用户注册并获得key后更新到这里）
- **认证方式**: URL 参数 `key=xxx`

## 调用方式
```
GET https://restapi.amap.com/v3/{服务路径}?parameters&key={api_key}
```

## 能力概览

| 类别 | 能力 |
|------|------|
| 地理编码 | 地址↔经纬度互转 |
| 路径规划 | 驾车/公交/步行/骑行路线、距离测量 |
| POI搜索 | 关键字/周边/多边形区域搜索、ID查询 |
| 天气查询 | 实时天气、天气预报 |
| 行政区域 | 省市区边界查询 |
| 定位 | IP定位 |
| 其他 | 坐标转换、输入提示、交通态势、静态地图 |

## 配额
- 个人开发者：大部分能力 5,000次/天，POI搜索仅 100次/天
- 超限阶梯付费，每日0:00重置

## 注意事项
- 坐标系: GCJ-02（非WGS-84），经纬度格式 `经度,纬度`
- status=1 成功，status=0 失败

---
*创建: 2026-04-12*
