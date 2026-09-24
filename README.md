# Clash Party 分流覆写

> 本项目由 ChatGPT（Codex）协助构建，规则文件由自动化流程生成，仅供个人学习使用。规则内容来自上游项目，并非 blackmatrix7 或 Clash Party 的官方发布。

基于 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Clash) 自动生成的 Clash Party YAML 覆写。当前版本将 79 个上游规则目录编译为 **77 个规则集、55 个策略组**。相关服务共用策略组，但保留独立规则集，便于追踪上游更新与规则冲突。上游 `ChinaMax`、`Global`、`GlobalMedia` 和 `Game` 等合集覆盖大量子规则，因此没有逐一启用上游全部目录。

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

规则内容来自 blackmatrix7/ios_rule_script，按其 [GPL-2.0 许可](LICENSE)发布。每个生成的 provider 文件标注上游提交与源文件；本仓库保留生成脚本，便于检查与重新构建。图标链接引用 [Koolson/Qure](https://github.com/Koolson/Qure) 的图标资源。
