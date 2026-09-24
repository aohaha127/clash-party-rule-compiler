# 规则重复与覆盖报告

- 上游版本：`17582922869fc3ebb35b9081631b11e02303f3f5`
- 原始规则条数：247,565
- 去重后规则条数：240,754
- 同一策略组内重复：11
- 跨组相同规则：6,800
- 不同策略组的域名后缀覆盖：7,884

规则按 `dist/clash-party.yaml` 中的先后顺序匹配。完全相同的规则仅保留先出现的一条。
域名后缀覆盖保留在报告中，专用规则优先于通用合集。

## 跨组重复最多的策略组

| 先匹配 | 后匹配 | 相同规则数 |
|---|---|---:|
| 苹果服务 | 国外网站 | 1,421 |
| 谷歌服务 | 国外网站 | 637 |
| 国外媒体 | 国外网站 | 594 |
| Facebook | 国外网站 | 552 |
| 微软服务 | 国外网站 | 408 |
| 游戏平台 | 国外网站 | 245 |
| PayPal | 国外网站 | 233 |
| 油管视频 | 国外媒体 | 183 |
| 油管视频 | 国外网站 | 172 |
| 迪士尼视频 | 国外网站 | 157 |
| 迪士尼视频 | 国外媒体 | 153 |
| 国内媒体 | 国内网站 | 150 |
| Amazon | 国外网站 | 136 |
| Nintendo | 游戏平台 | 126 |
| 哔哩哔哩 | 国内媒体 | 124 |
| Nintendo | 国外网站 | 110 |
| 奈飞视频 | 国外媒体 | 94 |
| 苹果云端 | 苹果服务 | 57 |
| Hulu | 国外媒体 | 55 |
| Steam | 游戏平台 | 51 |
| 哔哩哔哩 | 国内网站 | 51 |
| Hulu | 国外网站 | 48 |
| 苹果云端 | 国外网站 | 46 |
| 全球直连 | 国内网站 | 43 |
| 广告拦截 | 应用净化 | 38 |
| 微软服务 | 游戏平台 | 37 |
| 微软服务 | Xbox | 36 |
| HBO | 国外媒体 | 34 |
| 奈飞视频 | 国外网站 | 34 |
| Cloudflare | 国外网站 | 28 |
| Discord | 国外网站 | 26 |
| Telegram | 国外网站 | 26 |
| HBO | 国外网站 | 25 |
| X / Twitter | 国外网站 | 25 |
| GitHub | 国外网站 | 24 |
| Vercel | 国外网站 | 24 |
| LINE | 国外网站 | 22 |
| 隐私拦截 | 国外网站 | 21 |
| 全球直连 | 国外网站 | 21 |
| Prime Video | Amazon | 19 |
| Shopee | 国外网站 | 19 |
| Spotify | 国外媒体 | 18 |
| Prime Video | 国外媒体 | 17 |
| TikTok | 国外网站 | 17 |
| 国内媒体 | 国外媒体 | 16 |
| Spotify | 国外网站 | 16 |
| Epic | 游戏平台 | 14 |
| Prime Video | 国外网站 | 14 |
| Epic | 国外网站 | 14 |
| WhatsApp | 国外网站 | 14 |
| TikTok | 国外媒体 | 13 |
| JetBrains | 国外网站 | 13 |
| 微软云盘 | 微软服务 | 12 |
| 广告拦截 | 国内媒体 | 12 |
| Cloudflare | 国内网站 | 12 |
| 网易音乐 | 国内媒体 | 11 |
| 全球直连 | 下载服务 | 11 |
| OpenAI | 国外网站 | 11 |
| 广告拦截 | 谷歌服务 | 10 |
| 全球直连 | 谷歌FCM | 9 |

## 域名后缀覆盖示例

| 专用规则 | 策略组 | 通用后缀 | 策略组 |
|---|---|---|---|
| `DOMAIN,local.adguard.org` | 局域网 | `DOMAIN-SUFFIX,adguard.org` | 国外网站 |
| `DOMAIN,oasisauth.h3c.com` | 局域网 | `DOMAIN-SUFFIX,h3c.com` | 国内网站 |
| `DOMAIN,router.asus.com` | 局域网 | `DOMAIN-SUFFIX,asus.com` | 国外网站 |
| `DOMAIN-SUFFIX,kis.v2.scr.kaspersky-labs.com` | 局域网 | `DOMAIN-SUFFIX,kaspersky-labs.com` | 国内网站 |
| `DOMAIN-SUFFIX,localhost.ptlogin2.qq.com` | 局域网 | `DOMAIN-SUFFIX,qq.com` | 国内网站 |
| `DOMAIN-SUFFIX,localhost.sec.qq.com` | 局域网 | `DOMAIN-SUFFIX,qq.com` | 国内网站 |
| `DOMAIN,ad.10010.com` | 全球直连 | `DOMAIN-SUFFIX,10010.com` | 国内网站 |
| `DOMAIN,ad.12306.cn` | 全球直连 | `DOMAIN-SUFFIX,ad.12306.cn` | 广告拦截 |
| `DOMAIN,ain.bgm.tv` | 全球直连 | `DOMAIN-SUFFIX,bgm.tv` | 国外网站 |
| `DOMAIN,alt1-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,alt2-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,alt3-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,alt4-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,alt5-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,alt6-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,alt7-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,alt8-mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,analytics.95516.com` | 全球直连 | `DOMAIN-SUFFIX,95516.com` | 国内网站 |
| `DOMAIN,app.adjust.com` | 全球直连 | `DOMAIN-SUFFIX,adjust.com` | 隐私拦截 |
| `DOMAIN,bdtj.tagtic.cn` | 全球直连 | `DOMAIN-SUFFIX,tagtic.cn` | 广告拦截 |
| `DOMAIN,cdn.jsdelivr.net` | 全球直连 | `DOMAIN-SUFFIX,jsdelivr.net` | 国外网站 |
| `DOMAIN,clientservices.googleapis.com` | 全球直连 | `DOMAIN-SUFFIX,googleapis.com` | 谷歌服务 |
| `DOMAIN,deo.shopeemobile.com` | 全球直连 | `DOMAIN-SUFFIX,shopeemobile.com` | Shopee |
| `DOMAIN,dl.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,dl.l.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,eco-push-api-client.meiqia.com` | 全球直连 | `DOMAIN-SUFFIX,meiqia.com` | 广告拦截 |
| `DOMAIN,errlog.umeng.com` | 全球直连 | `DOMAIN-SUFFIX,umeng.com` | 国内网站 |
| `DOMAIN,fairplay.l.qq.com` | 全球直连 | `DOMAIN-SUFFIX,l.qq.com` | 广告拦截 |
| `DOMAIN,init.ess.apple.com` | 全球直连 | `DOMAIN-SUFFIX,apple.com` | 苹果服务 |
| `DOMAIN,itunes.apple.com` | 全球直连 | `DOMAIN-SUFFIX,apple.com` | 苹果服务 |
| `DOMAIN,lain.bgm.tv` | 全球直连 | `DOMAIN-SUFFIX,bgm.tv` | 国外网站 |
| `DOMAIN,livew.l.qq.com` | 全球直连 | `DOMAIN-SUFFIX,l.qq.com` | 广告拦截 |
| `DOMAIN,log.mmstat.com` | 全球直连 | `DOMAIN-SUFFIX,mmstat.com` | 广告拦截 |
| `DOMAIN,msg.umeng.com` | 全球直连 | `DOMAIN-SUFFIX,umeng.com` | 国内网站 |
| `DOMAIN,msg.umengcloud.com` | 全球直连 | `DOMAIN-SUFFIX,umengcloud.com` | 国内网站 |
| `DOMAIN,mtalk.google.com` | 全球直连 | `DOMAIN-SUFFIX,google.com` | 谷歌服务 |
| `DOMAIN,new-api.meiqia.com` | 全球直连 | `DOMAIN-SUFFIX,meiqia.com` | 广告拦截 |
| `DOMAIN,origin-a.akamaihd.net` | 全球直连 | `DOMAIN-SUFFIX,origin-a.akamaihd.net` | 游戏平台 |
| `DOMAIN,smp-device-content.apple.com` | 全球直连 | `DOMAIN-SUFFIX,apple.com` | 苹果服务 |
| `DOMAIN,sycm.mmstat.com` | 全球直连 | `DOMAIN-SUFFIX,mmstat.com` | 广告拦截 |
