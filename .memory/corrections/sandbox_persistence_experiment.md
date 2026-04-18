---
id: "mem-20260404-sandbox-test"
type: "correction"
env: "cloud"
confidence: "high"
tags: ["sandbox", "persistence", "experiment", "container", "cross-platform", "lab"]
---

# 沙盒持久性实验

## 问题
不同云平台的沙盒生命周期不透明，需要通用方法判断容器是持久存活还是每次会话重建。

## 位置
`~/agent-workspace/lab/sandbox-persistence/`（云端沙盒固定路径）

## 使用方法
- 首次: `bash run_test.sh --baseline`
- 后续: `bash run_test.sh`

## 触发词
"持久化检测" / "跑 persistence_test" / "检测沙盒"

## 跨平台注意
切换平台后必须重新 --baseline。脚本通过 platform fingerprint 自动匹配基线，不会误判。
