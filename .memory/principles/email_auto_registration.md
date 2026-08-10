---
id: "mem-20260727-email-register"
type: "principle"
env: "global"
confidence: "high"
tags: ["email", "registration", "automation", "cloudflare", "signup", "API", "account"]
---

# 临时邮箱自助注册流程

## 背景

Agent 专用域名通过 Cloudflare 邮件转发，任意前缀都会转发到用户的邮箱。Agent 可以利用这个机制自助注册新服务，无需用户编造邮箱地址。

## 适用场景

仅用于注册临时性的、会定期失效或需要轮换的账号（如 API 服务的体验额度账号）。不用于注册长期使用的账号。长期账号应由用户亲自注册和维护。

## 邮箱格式

`vik-{service}-{word1}-{word2}@${AGENT_EMAIL_DOMAIN}`

- `vik` — 标识 Agent 注册的账号
- `{service}` — 服务名（如 variflight、amap）
- `{word1}-{word2}` — 两个随机英文词，不关联服务，不维护已用列表，不记录序号

两个随机英文词的组合空间足够大，重复概率可忽略，因此无需记录哪些邮箱已用过。

## 流程

1. Agent 选择邮箱（按格式） ✅ 自动
2. Agent 填写注册表单 ✅ 自动
3. 激活邮件转发到用户的邮箱 → 用户把链接发给 Agent ⬅️ 唯一需用户介入
4. Agent 访问激活链接完成激活 ✅ 自动
5. Agent 拿到 API key / credentials ✅ 自动
6. Agent 存入记忆系统 ✅ 自动

## 注意

- 如果服务要求验证码而非链接，用户收到后把验证码发给 Agent 即可
- 如果服务限制同域名多注册，考虑使用其他可转发域名或联系用户处理
- 注册完成后，有用的凭证等信息应记录下来。Agent 应提醒用户确认记录方式（存入哪个记忆目录、记录哪些字段），不默认自动写入 `entities/`
