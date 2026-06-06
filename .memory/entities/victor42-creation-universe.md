---
id: "mem-20260606-cv42"
type: "entity"
env: "global"
confidence: "high"
tags: ["victor42", "victor42-work", "gadgets", "open-source", "github", "portfolio"]
---

# Victor42 小玩意与公开开源项目矩阵

## 定义

本记忆定义 Victor42 的公开小工具与开源代码资产矩阵。范围只包括 `victor42.work` 公开展示的小玩意，以及 GitHub 上 `greenzorro`、`agent-vik` 账号中可公开验证的相关仓库。

它不是 Victor42 全部创造物宇宙，不覆盖博客内容、notebook、世界观、内容战略、旅行方法论或私有项目。

## 双层模型

### 1. 展示层：`victor42.work`

- 定位：Victor42 的小玩意公开展示入口。
- 本地真相源：`victor42-work/data.json`。
- 云端真相源：公开站点 `https://victor42.work/` 及其可公开抓取的数据资源。
- 内容特征：工作与生活中遇到真实问题后，自制工具、模板、脚本、工作流或小网站来解决。
- 作用：面向外部用户解释“这些工具是什么、解决什么问题、去哪里使用”。

### 2. 代码资产层：GitHub 公开仓库

- 账号范围：`greenzorro` 与 `agent-vik` 的公开仓库。
- 作用：承载工具源码、发布包、网站源码、自动化脚本、Agent 记忆系统和实验项目。
- GitHub 公开仓库是判断“是否可写入全局记忆”的硬边界之一。

## 去重规则

- 同一个工具如果同时出现在 `victor42.work` 和 GitHub，只记为一个创造物。
- `victor42.work` 是产品展示入口，GitHub 是源码或实现入口；两者是同一对象的不同层级，不应重复计数。
- 如果 `victor42.work` 展示的是公开工具，但源码仓库不公开，只按公开展示信息描述，不推断、不补充本地实现细节。
- 本地存在但未在 `greenzorro` 或 `agent-vik` 公开 GitHub 仓库中出现的项目，一律视为私有项目，不写入本记忆。
- 不通过扫描本地项目目录来枚举创造物；本地项目目录只能辅助读取已知公开项目的真相源。

## 主要类别

### 1. 浏览器脚本与插件

- 代表项目：Google AI Studio 助手、NotebookLM 助手、酒店对比助手、瓴羊刷题助手。
- 共同模式：从具体网页产品的低效操作中抽出自动化脚本，并通过油猴脚本或浏览器扩展分发。
- 相关公开仓库示例：`ai-studio-easy-use`、`notebooklm-easy-use`、`hotel-comparer`、`ly-certification`、`browser-script-to-extension`。

### 2. 自动化与工作流工具

- 代表项目：Google Apps Script 工具集、自用软件一键安装系统、Excel+PS 批量自动出图。
- 共同模式：将高频维护、批量生产或跨软件流程压缩为低边际成本系统。
- 相关公开仓库示例：`google-apps-scripts`、`my-handy-tools`、`excel-ps-batch-export`。

### 3. AI 与图像生产工具

- 代表项目：ComfyUI 万能工作流、ComfyUI upscale 工作流、自动化 AI 插画生成系统。
- 共同模式：围绕图像生成、放大、风格探索和批量生产搭建可复用工作流。
- 相关公开仓库示例：`comfyui-workflow-versatile`、`comfyui-workflow-upscaler`、`ai-illustration-factory`。

### 4. 小网站与交互实验

- 代表项目：小熊歌单搬家、全球电源插座指南、违禁词替换工具、UI 画布尺寸计算器、蒲丰投针实验、混沌系统实验、前端练习本。
- 共同模式：把一个清晰问题做成可直接访问的轻量 Web 工具或交互实验。
- 相关公开仓库示例：`victor42-playlist`、`power-plug-guide`、`forbidden-phrases-replacer`、`ui-canvas-size-calculator`、`find-out-pi`、`chaos`、`demo`。

### 5. Agent 与记忆系统

- 代表项目：Agent 记忆系统。
- 共同模式：把 Agent 身份、长期记忆和跨平台加载能力产品化。
- 相关公开仓库示例：`agent-vik/about-me`、`greenzorro/open-agent-memory`。

## 不纳入本记忆的内容

- 私有项目：本地有但 GitHub 公开账号不可见的项目不写入。
- 博客内容与内容策略：归 `victor42-digital-entity.md`、`content-strategy.md` 等记忆处理。
- notebook、TIL、研究笔记、写作模板：归 `victor42_notebook.md` 处理。
- 具体项目实现细节、bug、部署步骤：放在对应项目 README、notes 或仓库文档中。
- 已归档的历史主题或模板资产，除非用户明确要求梳理历史开源资产。

## Agent 使用方式

- 当用户提到“小玩意”“victor42.work”“我的工具集合”“我的开源项目”“产品矩阵”“工具矩阵”时，优先加载本记忆。
- Local mode 需要最新公开展示清单时，读取 `victor42-work/data.json`。
- Cloud mode 需要最新公开展示清单时，抓取 `https://victor42.work/` 及其公开数据资源。
- 需要最新开源仓库清单时，查询 GitHub `greenzorro` 与 `agent-vik` 的公开 repositories。
- 写总结时按“展示层产品”去重，不按 URL 或仓库数量机械计数。
- 若要把某个项目写入全局记忆，先确认它已经公开展示或存在于公开 GitHub 仓库中。

## 与现有记忆的边界

- 本记忆只记录公开小工具与公开开源项目矩阵，不记录 Victor42 的完整公开身份、内容资产或世界观。
- 自动化审美、内容策略、GA 配置、具体项目使用方法仍由对应专项记忆或项目文档负责。
- 具体项目实现、部署、bug、使用细节属于项目 README/notes，不写入本记忆。
