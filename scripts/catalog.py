"""Ordered routing catalog. Earlier entries win when upstream sets overlap."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuleSet:
    slug: str
    group: str
    sources: tuple[str, ...]
    mode: str = "proxy"
    icon: str = "Proxy"


def item(slug: str, group: str, *sources: str, mode: str = "proxy", icon: str = "Proxy") -> RuleSet:
    return RuleSet(slug, group, sources, mode, icon)


# Specific services precede broad upstream collections. Do not add a parent
# collection ahead of its children. The compiler reports exact and suffix
# overlaps; the YAML order is the intended tie breaker.
CATALOG = [
    item("lan", "DIRECT", "Lan", mode="direct", icon="Direct"),
    item("direct", "国内直连", "Direct", mode="direct", icon="Direct"),
    item("steam_cn", "游戏直连", "SteamCN", mode="direct", icon="Game"),
    item("advertising", "广告拦截", "AdvertisingLite", mode="block", icon="AdBlack"),
    item("hijacking", "应用净化", "Hijacking", mode="block", icon="Hijacking"),
    item("privacy", "隐私拦截", "Privacy", mode="block", icon="Filter"),
    item("zhihu_ads", "广告拦截", "ZhihuAds", mode="block", icon="AdBlack"),

    item("openai", "AI 服务", "OpenAI", mode="ai", icon="Bot"),
    item("claude", "AI 服务", "Claude", "Anthropic", mode="ai", icon="AI"),
    item("gemini", "AI 服务", "Gemini", "BardAI", mode="ai", icon="AI"),
    item("civitai", "AI 服务", "Civitai", mode="ai", icon="AI"),

    item("telegram", "Telegram", "Telegram", icon="Telegram"),
    item("whatsapp", "即时通讯", "Whatsapp", icon="Global"),
    item("discord", "即时通讯", "Discord", icon="Discord"),
    item("line", "即时通讯", "Line", icon="Line"),

    item("npm", "开发工具", "Npmjs", icon="GitHub"),
    item("github", "GitHub", "GitHub", icon="GitHub"),
    item("gitlab", "开发工具", "GitLab", icon="GitHub"),
    item("docker", "开发工具", "Docker", icon="GitHub"),
    item("jetbrains", "开发工具", "Jetbrains", icon="GitHub"),
    item("notion", "Notion", "Notion", icon="Notion"),
    item("figma", "开发工具", "Figma", icon="GitHub"),
    item("cloudflare", "Cloudflare", "Cloudflare", icon="Cloudflare"),
    item("vercel", "云平台", "Vercel", icon="Cloudflare"),
    item("digitalocean", "云平台", "DigitalOcean", icon="Cloudflare"),

    item("google_fcm", "谷歌FCM", "GoogleFCM", mode="direct", icon="Google_Search"),
    item("google_search", "谷歌服务", "GoogleSearch", icon="Google_Search"),
    item("google_drive", "谷歌服务", "GoogleDrive", icon="Google_Drive"),
    item("google_voice", "谷歌服务", "GoogleVoice", icon="Google"),
    item("youtube_music", "YouTube", "YouTubeMusic", icon="YouTube_Music"),
    item("youtube", "YouTube", "YouTube", icon="YouTube"),
    item("google", "谷歌服务", "Google", icon="Google_Search"),

    item("bing", "微软服务", "Bing", mode="direct", icon="Microsoft"),
    item("onedrive", "微软云盘", "OneDrive", mode="direct", icon="OneDrive"),
    item("microsoft_edge", "微软服务", "MicrosoftEdge", mode="direct", icon="Microsoft"),
    item("microsoft", "微软服务", "Microsoft", mode="direct", icon="Microsoft"),

    item("app_store", "苹果服务", "AppStore", mode="direct", icon="App_Store"),
    item("icloud", "苹果服务", "iCloud", mode="direct", icon="iCloud"),
    item("testflight", "苹果服务", "TestFlight", mode="direct", icon="Apple"),
    item("apple_music", "苹果媒体", "AppleMusic", icon="Apple_Music"),
    item("apple_tv", "苹果媒体", "AppleTV", icon="Apple_TV"),
    item("apple_news", "苹果媒体", "AppleNews", icon="Apple"),
    item("apple", "苹果服务", "Apple", mode="direct", icon="Apple"),

    item("netflix", "奈飞视频", "Netflix", mode="netflix", icon="Netflix"),
    item("disney", "迪士尼视频", "Disney", icon="Disney"),
    item("prime_video", "Prime Video", "AmazonPrimeVideo", icon="Amazon"),
    item("hbo", "HBO", "HBO", icon="HBO"),
    item("hulu", "Hulu", "Hulu", icon="Hulu"),
    item("spotify", "Spotify", "Spotify", icon="Spotify"),
    item("bahamut", "巴哈姆特", "Bahamut", mode="taiwan", icon="Bahamut"),
    item("bilibili_intl", "哔哩哔哩国际", "BiliBiliIntl", icon="bilibili"),
    item("bilibili", "哔哩哔哩", "BiliBili", mode="domestic_media", icon="bilibili"),
    item("tiktok", "TikTok", "TikTok", icon="TikTok"),
    item("twitch", "Twitch", "Twitch", icon="Twitch"),
    item("netease_music", "网易音乐", "NetEaseMusic", mode="domestic_media", icon="Netease_Music"),
    item("china_media", "国内媒体", "ChinaMedia", mode="domestic_media", icon="DomesticMedia"),
    item("global_media", "国外媒体", "GlobalMedia", icon="ForeignMedia"),

    item("steam", "游戏代理", "Steam", icon="Steam"),
    item("epic", "游戏代理", "Epic", icon="Game"),
    item("playstation", "游戏代理", "PlayStation", icon="Game"),
    item("nintendo", "游戏代理", "Nintendo", icon="Game"),
    item("xbox", "游戏代理", "Xbox", icon="Game"),
    item("game", "游戏直连", "Game", mode="direct", icon="Game"),

    item("twitter", "X / Twitter", "Twitter", icon="Twitter"),
    item("facebook", "Meta 社交", "Facebook", icon="Facebook"),
    item("instagram", "Meta 社交", "Instagram", icon="Instagram"),
    item("reddit", "Reddit", "Reddit", icon="Global"),
    item("threads", "Meta 社交", "Threads", icon="Instagram"),
    item("snap", "Snapchat", "Snap", icon="Global"),

    item("paypal", "PayPal", "PayPal", icon="PayPal"),
    item("amazon", "海外购物", "Amazon", icon="Amazon"),
    item("shopify", "海外购物", "Shopify", icon="Amazon"),
    item("shopee", "海外购物", "Shopee", icon="Amazon"),

    item("download", "国内直连", "Download", mode="direct", icon="Download"),
    item("speedtest", "测速服务", "Speedtest", mode="direct", icon="Speedtest"),
    item("china", "国内直连", "ChinaMax", mode="direct", icon="China"),
    item("global", "国外网站", "Global", icon="Global"),
]


REGIONS = [
    ("香港节点", r"(?i)港|HK|Hong[ _-]?Kong", "Hong_Kong"),
    ("台湾节点", r"(?i)台|TW|Taiwan", "Taiwan"),
    ("狮城节点", r"(?i)新加坡|坡|狮城|SG|Singapore", "Singapore"),
    ("日本节点", r"(?i)日本|东京|大阪|JP|Japan", "Japan"),
    ("美国节点", r"(?i)美|US|United[ _-]?States", "United_States"),
    ("韩国节点", r"(?i)韩|韓|首尔|KR|Korea", "Korea"),
]
