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
    item("lan", "局域网", "Lan", mode="direct", icon="Direct"),
    item("direct", "全球直连", "Direct", mode="direct", icon="Direct"),
    item("steam_cn", "国服游戏", "SteamCN", mode="direct", icon="Game"),
    item("advertising", "广告拦截", "AdvertisingLite", mode="block", icon="AdBlack"),
    item("hijacking", "应用净化", "Hijacking", mode="block", icon="Hijacking"),
    item("privacy", "隐私拦截", "Privacy", mode="block", icon="Filter"),
    item("zhihu_ads", "知乎广告", "ZhihuAds", mode="block", icon="AdBlack"),

    item("openai", "OpenAI", "OpenAI", mode="ai", icon="Bot"),
    item("claude", "Claude", "Claude", "Anthropic", mode="ai", icon="AI"),
    item("gemini", "Gemini", "Gemini", "BardAI", mode="ai", icon="AI"),
    item("civitai", "Civitai", "Civitai", mode="ai", icon="AI"),

    item("telegram", "Telegram", "Telegram", icon="Telegram"),
    item("whatsapp", "WhatsApp", "Whatsapp", icon="Global"),
    item("discord", "Discord", "Discord", icon="Discord"),
    item("line", "LINE", "Line", icon="Line"),

    item("npm", "NPM", "Npmjs", icon="GitHub"),
    item("github", "GitHub", "GitHub", icon="GitHub"),
    item("gitlab", "GitLab", "GitLab", icon="GitHub"),
    item("docker", "Docker", "Docker", icon="GitHub"),
    item("jetbrains", "JetBrains", "Jetbrains", icon="GitHub"),
    item("notion", "Notion", "Notion", icon="Notion"),
    item("figma", "Figma", "Figma", icon="GitHub"),
    item("cloudflare", "Cloudflare", "Cloudflare", icon="Cloudflare"),
    item("vercel", "Vercel", "Vercel", icon="Cloudflare"),
    item("digitalocean", "DigitalOcean", "DigitalOcean", icon="Cloudflare"),

    item("google_fcm", "谷歌FCM", "GoogleFCM", mode="direct", icon="Google_Search"),
    item("google_search", "谷歌搜索", "GoogleSearch", icon="Google_Search"),
    item("google_drive", "谷歌云盘", "GoogleDrive", icon="Google_Drive"),
    item("google_voice", "Google Voice", "GoogleVoice", icon="Google"),
    item("youtube_music", "YouTube Music", "YouTubeMusic", icon="YouTube_Music"),
    item("youtube", "油管视频", "YouTube", icon="YouTube"),
    item("google", "谷歌服务", "Google", icon="Google_Search"),

    item("bing", "微软Bing", "Bing", mode="direct", icon="Microsoft"),
    item("onedrive", "微软云盘", "OneDrive", mode="direct", icon="OneDrive"),
    item("microsoft_edge", "微软浏览器", "MicrosoftEdge", mode="direct", icon="Microsoft"),
    item("microsoft", "微软服务", "Microsoft", mode="direct", icon="Microsoft"),

    item("app_store", "苹果商店", "AppStore", mode="direct", icon="App_Store"),
    item("icloud", "苹果云端", "iCloud", mode="direct", icon="iCloud"),
    item("testflight", "TestFlight", "TestFlight", mode="direct", icon="Apple"),
    item("apple_music", "苹果音乐", "AppleMusic", icon="Apple_Music"),
    item("apple_tv", "苹果视频", "AppleTV", icon="Apple_TV"),
    item("apple_news", "苹果新闻", "AppleNews", icon="Apple"),
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

    item("steam", "Steam", "Steam", icon="Steam"),
    item("epic", "Epic", "Epic", icon="Game"),
    item("playstation", "PlayStation", "PlayStation", icon="Game"),
    item("nintendo", "Nintendo", "Nintendo", icon="Game"),
    item("xbox", "Xbox", "Xbox", icon="Game"),
    item("game", "游戏平台", "Game", mode="direct", icon="Game"),

    item("twitter", "X / Twitter", "Twitter", icon="Twitter"),
    item("facebook", "Facebook", "Facebook", icon="Facebook"),
    item("instagram", "Instagram", "Instagram", icon="Instagram"),
    item("reddit", "Reddit", "Reddit", icon="Global"),
    item("threads", "Threads", "Threads", icon="Instagram"),
    item("snap", "Snapchat", "Snap", icon="Global"),

    item("paypal", "PayPal", "PayPal", icon="PayPal"),
    item("amazon", "Amazon", "Amazon", icon="Amazon"),
    item("shopify", "Shopify", "Shopify", icon="Amazon"),
    item("shopee", "Shopee", "Shopee", icon="Amazon"),

    item("download", "下载服务", "Download", mode="direct", icon="Download"),
    item("speedtest", "测速服务", "Speedtest", mode="direct", icon="Speedtest"),
    item("china", "国内网站", "ChinaMax", mode="direct", icon="China"),
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
