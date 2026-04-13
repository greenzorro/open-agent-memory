---
id: "mem-20260413-apkdl"
type: "entity"
env: "global"
confidence: "low"
tags: ["apk", "download", "android", "apkpure", "apkcombo"]
---

# APK 下载能力

通过第三方站点组合实现的服务器端 APK 下载，非公开接口，可能随时失效。

## 工作流（两步）

### 第1步：App 名称 → 包名

使用 apkcombo 搜索页，从第一条搜索结果的 URL 中提取包名。

```bash
# 中英文 App 名称均可，中文需 URL 编码
PKG=$(curl -sL "https://apkcombo.com/zh/search/{APP_NAME}/" \
  -H "User-Agent: Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36" \
  | rg -oP 'href="/zh/[^/]+/(\Kcom\.|org\.)[a-z0-9_.]+' | head -1)
```

- 第一条结果通常是最匹配的官方版本
- **中文搜索不一定准**，同名或近似名的第三方应用可能排在前面；优先用英文原名搜索，中文作为备选
- 搜索结果取包名时按出现顺序取第一个，但应人工确认包名是否对应目标应用

### 第2步：包名 → 下载 APK

使用 APKPure CDN 直链获取最新版 APK。

```bash
# 查询版本信息（不下载）
curl -sI -L --max-redirs 10 \
  -A "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36" \
  -r 0-0 "https://d.apkpure.com/b/APK/{PACKAGE_NAME}?version=latest"
# 从 Content-Disposition 头获取文件名和版本号

# 下载 APK
curl -L --max-redirs 10 \
  -A "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36" \
  "https://d.apkpure.com/b/APK/{PACKAGE_NAME}?version=latest" \
  -o {output_filename}.apk
```

## 关键要求

- **User-Agent 必须伪装为 Android 手机浏览器**，否则被 Cloudflare 拦截返回 403
- **跳转后的 CDN URL 带签名参数，有时效性**，不能缓存复用，每次必须从 `d.apkpure.com` 入口重新走
- CDN 域名为 `winudf.com`（APKPure 自建/托管）

## 已知限制

- 仅能下载最新版本，指定版本号不可用
- 仅返回标准 APK，不支持 XAPK、OBB 等分包格式
- 高频请求可能触发限流或人机验证
- 非公开接口，APKPure 随时可能更改路由规则导致失效

## 已验证可下载的应用

com.tencent.mm（微信）、org.telegram.messenger（Telegram）、com.android.chrome（Chrome）、com.whatsapp、com.instagram.android、com.zhiliaoapp.musically（TikTok）、com.huawei.health（华为运动健康）
