---
id: "mem-20260813-tyca"
type: "entity"
env: "global"
confidence: "high"
tags: ["API", "tianyancha", "天眼查", "天眼AI", "企业", "工商", "尽调", "KYB", "公司查询", "数据源"]
---

# 天眼 AI（天眼查企业数据）

查中国大陆企业工商、风险、知产、经营公示、历史沿革、董监高时使用。

## 基本信息
- **服务商**: 北京金堤科技（天眼查）
- **产品**: 天眼 AI
- **站点**: https://www.tianyancha.com/ai
- **Key 与用量**: https://www.tianyancha.com/ai/profile
- **开发者文档**: https://www.tianyancha.com/ai/developer-docs
- **工具名清单**: https://raw.githubusercontent.com/tyc-tech/tyc-cli/main/src/catalog.json（162 个 `tool_name`）

## 认证
- **API Key**: `{your_api_key}`（引导用户注册并获得 key 后更新到私有记忆或环境变量）
- **认证方式**: HTTP Header `Authorization: {api_key}`（也可 `Authorization: Bearer {api_key}`）
- **连通性（不扣额度）**: `GET https://mcp.tianyancha.com/v1/core/auth/ready`，成功返回 `ok`
- 完整 Key 只写在私有记忆；对话、日志、skill、公开仓库里只允许掩码（如 `mcpk2_62f…8b`）

## 调用方式
本地与云端化身走同一条 HTTPS Shared Core。凭证在私有记忆实体文件中，不按环境单独配客户端。

```
POST https://mcp.tianyancha.com/v1/core/tools/call
Content-Type: application/json
Accept: application/json
Authorization: {api_key}

Body: {"tool_name": "<工具名>", "arguments": {...}, "format": "json"}
```

`format` 也可为 `markdown`。成功时 HTTP 200，body 为 `{"tool_name","format","content"}`；`content` 是业务 JSON。列表类参数常用 `pageNum`（默认 1）、`pageSize`（默认 10，常见上限 100）。

## 查询顺序
1. 用户给的不是完整企业名或 18 位统一社会信用代码时，先 L0 锚定，不要直接下钻。
2. 先打 1–2 个 L1 总览，再按问题下钻 L2；L3 只在需要详情页或专项检索时用。
3. 多个候选都可能匹配时，先让用户确认，不要猜。
4. 不能编造中国企业数据；空结果只表示本次未返回数据，不要写成「绝对没有风险」。
5. `quota_exceeded` 不要重试；把剩余额度、重置时间转述给用户。

## 分层与常用工具

| 层 | 作用 | tool_name | arguments |
|---|---|---|---|
| L0 | 简称/模糊名 → 候选企业 | `search_companies` | `searchKey`；可选 `pageNum`,`pageSize` |
| L1 工商 | 登记信息与企业属性 | `get_company_registration_info` | `searchKey` |
| L1 风险 | 风险总览 | `get_risk_overview` | `searchKey` |
| L1 知产 | 知产评分 | `get_ipr_score` | `searchKey` |
| L1 经营 | 信用评价 | `get_credit_evaluation` | `searchKey`；可选分页 |
| L1 历史 | 历史总览 | `get_historical_overview` | `searchKey` |
| L1 人员 | 人员画像 | `get_person_profile` | `searchKey`,`humanName` |

`searchKey` 为企业名称、统一社会信用代码或天眼查企业 ID。已知 USCC 时优先用 USCC。董监高类工具必须同时传企业 `searchKey` 与 `humanName`，避免同名误查。

不确定某模块先下钻哪个明细时：

| 模块 | 优先 L2 |
|---|---|
| 企业基础信息 | `get_shareholder_info` |
| 风险合规 | `get_judicial_case` |
| 知识产权 | `get_trademark_info` |
| 经营与公示 | `get_bidding_info` |
| 历史信息 | `get_historical_registration` |
| 董监高 | `get_person_risk_overview` |

另常用：`get_company_profile`、`get_actual_controller`、`get_beneficial_owners`、`get_contact_info`、`get_patent_info`、`get_qualifications`、`get_news_sentiment`。其余工具名以 catalog 为准；共 6 组：company / risk / intellectual_property / operation / history / executive。

## 返回要点
工商登记常见字段在 `content.sources.base`：`name`、`creditCode`、`regStatus`、`legalPersonName`、`regCapital`、`estiblishTime`、`businessScope`。服务端可能注入 `_summary`、`_empty`、`_warnings`。

## 额度
- 账号档位 VIP：日 1,000、月 10,000。
- 月额度 = 日额度 × 10，是月度总上限，不是日额度累加。
- 仅成功返回数据的有效调用扣减；报错、限流、空结果与无数据不扣减。
- 用量页：https://www.tianyancha.com/ai/profile?tab=usage

## 示例
```python
import requests

headers = {
    "Authorization": "{your_api_key}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
body = {
    "tool_name": "get_company_registration_info",
    "arguments": {"searchKey": "北京金堤科技有限公司"},
    "format": "json",
}
response = requests.post(
    "https://mcp.tianyancha.com/v1/core/tools/call",
    headers=headers, json=body,
)
```
