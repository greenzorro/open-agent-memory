---
id: "mem-20260412-amap-api"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "map", "geography", "travel", "数据源", "POI", "地理编码"]
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

## POI 搜索行为特征

- **types 参数不仅过滤类型，还会改变排序**：设置 types 后，结果排序逻辑会发生变化
- **结果排序按热度而非相关性**：同名 POI 中，日常搜索量高的可能排在目标 POI 前面
- **city 参数接受县级**：直接使用县/区级行政区名即可
- **citylimit 与 keyword 是独立维度**：往 keyword 里塞地理词会破坏模糊匹配
- **POI 注册名可能与常用名不同**：用户使用的名称与 POI 库中的注册名可能不一致

## 地图瓦片

```
https://wprd0{s}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=8
```

- subdomains: "1234"，style=8 为标准地图样式
- HTTPS + CORS，支持跨域嵌入

## 注意事项
- 坐标系: GCJ-02（非WGS-84），经纬度格式 `经度,纬度`
- status=1 成功，status=0 失败
