---
id: "mem-20261022-nk5d"
type: "correction"
env: "global"
confidence: "high"
tags: ["memory-schema", "structure", "type-classification", "runtime-concept", "directory"]
---

# 记忆库没有 skills 类型

## 规则

`.memory/` 只有四类：`preference` / `principle` / `entity` / `correction`，映射见 `00_kernel/memory_schema.md` §3。不存在 `skills/` 目录，也不为任何运行时概念新增第五类目录。

## 判据

- skill 是运行时的加载概念——由某个 runtime 按需注入上下文。
- 记忆库不依赖任何 runtime，它的等价物是 `principle`：流程性、可执行的知识写成 principle（例如旅行攻略的编排流程即由 principle 承载）。
- 另立 `skills/` 等于把某个 runtime 的实现细节固化成架构：换 runtime 即失效，且内容必然与已有 principle / entity 重复。

## 落笔前判定

1. 这条属于四类中的哪一类？
2. 已有条目能否覆盖，或扩写已有条目？
3. 类型答不上来、又确实无处可放——不写。不新建目录。

## 常见借口与驳回

- "这是 skill，所以放 skills/" → 记忆库没有 skill 这个类型；它是流程知识，归 principle。
- "先建个目录，以后再归位" → 目录一旦存在就被当成结构，并被后续写入当作先例。归位成本只在写入时付一次，越晚越贵。
- "别的 runtime / 别的 agent 也这么分" → 那是那边的实现。本库结构以 `memory_schema.md` 为准。
