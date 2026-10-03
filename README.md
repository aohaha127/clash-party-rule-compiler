# Clash Party 分流覆写

> 本项目由 ChatGPT（Codex）协助构建，规则文件由自动化流程生成，仅供个人学习使用。规则内容来自上游项目，并非 blackmatrix7 或 Clash Party 的官方发布。

基于 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Clash)，并精选补充 [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR/tree/master/Clash) 的 Clash Party YAML 覆写。blackmatrix7 的 79 个目录形成 77 个基础规则集，ACL4SSR 按类别补充，仍保持 **55 个策略组**。相关服务共用策略组，规则集按来源分别生成，便于追踪更新与冲突。上游 `ChinaMax`、`Global`、`GlobalMedia` 和 `Game` 等合集覆盖大量子规则，因此没有逐一启用上游全部目录。

## 导入

1. 在 Clash Party 的「覆写」页面，通过下面的链接导入 YAML：

   `https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/clash-party.yaml`

2. 在「订阅管理」中编辑你的订阅，将该覆写绑定到订阅。
3. 更新订阅，并检查「节点选择」、地区节点组及各服务策略组。地区节点组根据节点名称筛选；名称不符合筛选式时，该组会为空并回退为 `REJECT`。

该覆写以 `rules` 和 `proxy-groups` 替换订阅中的对应数组，保留订阅提供的 `proxies` 与 `proxy-providers`。策略组默认选择见生成文件；「AI 服务」默认进入排除香港节点的「非港节点」，也可以手动选择其他列出的策略。

### Clash Party Smart 内核

「非港节点」使用 `url-test` 类型，并继续通过 `exclude-filter` 排除名称中带有香港标识的节点。在 Clash Party 的「内核设置 → 使用自动 Smart 规则覆写」开启后，应用会把 `url-test` 组转换为 Smart 组，显示为「非港节点(Smart Group)」，并更新「AI 服务」对它的引用。关闭自动 Smart 覆写时，该组仍会按延迟自动选择非港节点。由于自动覆写也会转换其他 `url-test` 地区组，启用后请在 Clash Party 中检查「AI 服务」选择的是「非港节点(Smart Group)」。

## 合并后的策略组

| 策略组 | 对应的独立规则集 |
|---|---|
| 国内直连 | 全球直连、下载服务、国内网站；局域网规则单独固定走 `DIRECT` |
| 广告拦截 | 广告拦截、知乎广告 |
| AI 服务 | OpenAI、Claude、Gemini、Civitai |
| 即时通讯 | WhatsApp、Discord、LINE；Telegram 保持独立 |
| 开发工具 | NPM、GitLab、Docker、JetBrains、Figma；GitHub 保持独立 |
| 云平台 | Vercel、DigitalOcean；Cloudflare 保持独立 |
| 谷歌服务 | 谷歌搜索、谷歌云盘、Google Voice、谷歌服务；谷歌FCM 保持独立 |
| YouTube | YouTube Music、油管视频 |
| 微软服务 | 微软Bing、微软浏览器、微软服务；微软云盘保持独立 |
| 苹果服务 | 苹果商店、苹果云端、TestFlight、苹果服务 |
| 苹果媒体 | 苹果音乐、苹果视频、苹果新闻 |
| 游戏代理 | Steam、Epic、PlayStation、Nintendo、Xbox |
| 游戏直连 | 国服游戏、游戏平台 |
| Meta 社交 | Facebook、Instagram、Threads |
| 海外购物 | Amazon、Shopify、Shopee |

完整策略组及其选项见 [`dist/clash-party.yaml`](dist/clash-party.yaml)。

## 规则优先顺序

局域网固定 `DIRECT` → 明确直连 → 广告及隐私拦截 → 具体服务 → 媒体和游戏合集 → 国内网站 → 国外网站 → 漏网之鱼。完全相同的规则只保留第一条。更具体的域名与通用后缀可能分别属于不同策略，按 YAML 中的先后顺序匹配。

查看 [重复与覆盖报告](reports/conflicts.md) 和 [机器可读报告](reports/conflicts.json)。报告列出完全重复规则、保留的策略、被去掉的后续重复项，以及不同策略之间的域名后缀覆盖示例。

## 自动更新

GitHub Actions 每天香港时间 **08:00** 拉取上游固定提交，重新编译、检查 YAML、检查引用与策略组循环，并使用官方稳定版 Mihomo 核心做配置测试。只有全部检查通过后才提交结果；失败时仓库保留上一版。`dist/build-info.json` 记录拉取时间与上游提交。GitHub 定时工作流可能延迟或漏跑，不能保证在整点完成。

本地运行：

```bash
python -m pip install -r requirements.txt
python scripts/build.py --repo aohaha127/clash-party-rule-compiler
python scripts/validate.py
```

## 来源与许可

blackmatrix7 规则文件遵循其 [GPL-2.0 许可](LICENSE)；ACL4SSR 补充规则文件遵循其 [CC-BY-SA-4.0 许可](licenses/ACL4SSR-CC-BY-SA-4.0.txt)。两种来源分开生成 provider，并分别标注来源、提交、许可与筛选修改。图标链接引用 [Koolson/Qure](https://github.com/Koolson/Qure)。

## Stash 和 Loon

每日香港时间 08:00 的同一构建同步生成两个客户端的四个版本，保持 55 个策略组。使用对应客户端的文件；Clash Party 的 YAML 继续独立发布。

| 版本 | Stash 覆写 | Loon 配置模板 |
|---|---|---|
| 默认 | [default.stoverride](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/stash/default.stoverride) | [default.conf](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/loon/default.conf) |
| 广告增强 | [adblock.stoverride](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/stash/adblock.stoverride) | [adblock.conf](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/loon/adblock.conf) |
| 本地服务 | [local.stoverride](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/stash/local.stoverride) | [local.conf](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/loon/local.conf) |
| 全部增强 | [full.stoverride](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/stash/full.stoverride) | [full.conf](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/loon/full.conf) |

Stash：先添加自己的节点订阅，再导入并启用一个 `.stoverride`。采用官方 `#!replace` 语法替换策略组、规则集和分流规则，订阅节点及节点提供者保留；其他分流覆写可能再次覆盖这些字段。为「节点选择」选一个可用代理。「非港节点」使用台湾、狮城、日本、美国、韩国地区组；其他地区的非港节点需自行加入这个组。Stash 不使用 Clash Party Smart 自动覆写。

Loon：下载一个 `.conf`，将 `[Remote Proxy]` 中 `https://example.invalid/replace-with-your-loon-subscription` 替换为自己的 **Loon 格式订阅 URL**，再导入配置；这是需要填写节点来源的模板。也可将 `[Remote Filter]`、`[Proxy Group]`、`[Rule]`、`[Remote Rule]` 合并到现有配置，并将筛选规则中的「机场订阅」改为自己的订阅别名，移除原有同名组和重复 FINAL。节点按名称筛选，非港筛选排除香港；无可用节点时请检查分组并手动选择可用策略。规则集按 Loon 资源更新设置拉取，仓库的每日编译不等于 App 每日自动重载本地模板。

两种导出以 iOS 为兼容目标，省略 `PROCESS-NAME`，因此下载软件/远程桌面进程直连不会在这些导出中生效（Stash macOS 的进程功能也未包含）。域名、IPv4/IPv6、ASN 规则保留；进程规则删除后为空的规则集不再引用。Loon 按其原生机制优先匹配域名、且本地规则优先于远程规则，无法保证与 Clash 的所有 IP/域名交叉覆盖行为完全相同。npm registry 的本地精确规则保留。

已验证 YAML/配置结构、规则类型、文件与策略引用、筛选表达式和策略循环；当前 Windows 环境无法运行 Loon/Stash 原生核心，**尚未在原生 App 做运行验证**。转换数量与排除统计见 [clients.json](reports/clients.json)。原生兼容依据：[Stash 覆写](https://stash.wiki/en/configuration/override)、[Stash 策略组](https://stash.wiki/en/proxy-protocols/proxy-groups)、[Stash 规则](https://stash.wiki/en/rules/rule-types)、[Loon 官方说明](https://github.com/Loon0x00/LoonManual)、[Loon 示例](https://github.com/Loon0x00/LoonExampleConfig/blob/master/example.conf)。

## ACL4SSR 精选补充

每天同一工作流同时拉取 [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR/tree/master/Clash) 和 blackmatrix7 的固定提交。下载文件和缓存均校验 Git blob SHA-1 与字节数，下载截断时从 GitHub blob API 恢复；完整性或配置验证失败会停止发布。

默认版本补充 AI、开发工具、明确下载进程和游戏 CDN，沿用现有 55 个策略组。AI 补充先于谷歌、微软及通用媒体合集；开发工具补充先于通用合集。共享登录/统计域名、宽泛下载/PT 关键词、URL-REGEX、USER-AGENT、NAS 海外云 IP 被排除；Reddit 保留原策略。局域网与已有拦截规则优先。

| 版本 | 使用链接 | 内容 |
|---|---|---|
| 默认 | [clash-party.yaml](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/clash-party.yaml) | 精选服务补充 |
| 广告增强 | [clash-party-adblock.yaml](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/clash-party-adblock.yaml) | 默认 + EasyList / EasyListChina |
| 本地服务 | [clash-party-local-services.yaml](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/clash-party-local-services.yaml) | 默认 + 明确 PT 域名、精选 NAS/DDNS、远程桌面进程直连 |
| 全部增强 | [clash-party-full.yaml](https://raw.githubusercontent.com/aohaha127/clash-party-rule-compiler/main/dist/clash-party-full.yaml) | 默认 + 上述两类可选补充 |

四个版本均为完整覆写，选一个绑定订阅即可。PT 版本会让列出的海外 PT 域名也走国内直连策略；远程桌面版本影响对应进程的全部连接，请按自己的访问条件选择。广告增强可能影响登录、统计和页面功能，上游广告合集的更新频率独立于本项目每日编译。

规则集通过「节点选择」下载，请为该组选择可用的代理。已有 `bm7_*` 规则集继续使用旧 `rule_provider/bm7/` 缓存，新补充及修改后的规则集使用 `rule_provider/compiled/`。如果日志显示 `[Provider] … pull error … EOF`，且对应规则集没有缓存，服务流量可能落到「漏网之鱼」。更新覆写并重新应用订阅，然后检查规则集是否下载成功；全局模式不会按这些规则分流。

`registry.npmjs.org` 额外使用内嵌精确规则 `DOMAIN,registry.npmjs.org,开发工具`，排在局域网规则后，不依赖 NPM 规则集下载。现有 `npmjs.org` 后缀覆盖仍保留，两者目标一致。此规则仅对进入 Clash 的连接生效；npm 没有经过 TUN 或显式代理时，仍需指定 npm 代理。

完全相同规则按顺序去重；ACL 补充被此前同策略后缀覆盖时省略。跨策略后缀覆盖保留并报告，避免删除有意设置的服务例外。最新规则数、补充保留数与各版本统计见 [build-info.json](dist/build-info.json)，排除原因与归类变化见 [ACL4SSR 报告](reports/acl4ssr.md) / [完整 JSON](reports/acl4ssr.json)。原 conflicts.md 专门记录 blackmatrix7 编译阶段。
