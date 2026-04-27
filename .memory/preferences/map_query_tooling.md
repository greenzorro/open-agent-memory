---
id: "mem-20260412-map-query-tooling"
type: "preference"
env: "global"
confidence: "high"
tags: ["travel", "API", "automation", "geography", "地图", "高德", "POI", "路线规划", "地理编码", "天气", "导航", "定位", "数据源", "amap", "高德地图"]
---

# 地图查询工具选型

**首选：高德地图 Web服务 API (Amap)**

## 选型理由
1. REST API直接调用，结构化JSON返回，无需解析DOM
2. 中国大陆数据质量最高（POI、路网、公交数据均为行业标杆）
3. 功能完整：地理编码/逆地理编码、4种路径规划、POI搜索、天气、行政区域、交通态势、静态地图
4. 个人开发者免费额度充裕（大部分能力5000次/天）
5. 注册门槛低，仅需手机号+Key，无需企业认证
6. 国内服务无延迟，无需翻墙

## 未选方案
- **OpenStreetMap/Overpass API**: 全球覆盖好，但国内POI和路网数据质量远不如高德；Overpass查询语法复杂，学习成本高
- **Google Maps API**: 需翻墙、需绑信用卡、国内数据被合规限制，免费额度低
- **腾讯地图 API**: 与高德功能近似，但POI数据丰富度略逊；选高德因为先注册了Key，无实质差异
- **百度地图 API**: 功能与高德 comparable，但API风格较老；同样可行，无显著优劣

## 技术详情
参见 `entities/amap_api.md`
