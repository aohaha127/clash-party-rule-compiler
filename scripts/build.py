#!/usr/bin/env python3
"""Compile selected blackmatrix7 Clash lists into a Clash Party YAML override."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from catalog import CATALOG, REGIONS, RuleSet


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_REPO = "blackmatrix7/ios_rule_script"
UPSTREAM_BRANCH = "master"
ICON_BASE = "https://testingcf.jsdelivr.net/gh/Koolson/Qure@master/IconSet/Color"
USER_AGENT = "clash-party-rule-compiler/1.0"
MAX_SOURCE_BYTES = 12_000_000


def get_bytes(url: str, *, token: str | None = None, attempts: int = 4) -> bytes:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urlopen(Request(url, headers=headers), timeout=45) as response:
                data = response.read(MAX_SOURCE_BYTES + 1)
            if len(data) > MAX_SOURCE_BYTES:
                raise ValueError(f"download too large: {url}")
            return data
        except Exception as exc:  # network failures are retried, then fail closed
            error = exc
            if attempt < attempts - 1:
                time.sleep(2**attempt)
    raise RuntimeError(f"failed to fetch {url}: {error}")


def github_api(path: str) -> dict:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return json.loads(get_bytes(f"https://api.github.com/{path}", token=token))
    # gh uses the user's existing credential without exposing it in process output.
    result = subprocess.run(
        ["gh", "api", path], check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return json.loads(result.stdout)


def upstream_snapshot() -> tuple[str, dict[str, dict]]:
    commit = github_api(f"repos/{UPSTREAM_REPO}/commits/{UPSTREAM_BRANCH}")
    sha = commit["sha"]
    tree_sha = commit["commit"]["tree"]["sha"]
    for part in ("rule", "Clash"):
        entries = github_api(f"repos/{UPSTREAM_REPO}/git/trees/{tree_sha}")["tree"]
        match = next((entry for entry in entries if entry["path"] == part), None)
        if not match or match["type"] != "tree":
            raise ValueError(f"upstream directory missing: {part}")
        tree_sha = match["sha"]
    listing = github_api(f"repos/{UPSTREAM_REPO}/git/trees/{tree_sha}?recursive=1")
    if listing.get("truncated"):
        raise ValueError("upstream Clash tree was truncated")
    files = {entry["path"]: entry for entry in listing["tree"] if entry["type"] == "blob"}
    return sha, files


def source_path(name: str, files: dict[str, dict]) -> str:
    for suffix in ("_Classical.yaml", ".yaml"):
        path = f"{name}/{name}{suffix}"
        if path in files:
            return path
    raise ValueError(f"no classical YAML source for {name}")


def fetch_source(sha: str, name: str, path: str) -> tuple[str, str, list[str]]:
    cache = ROOT / ".cache" / "raw" / sha / f"{name}.yaml"
    if cache.exists():
        body = cache.read_bytes()
    else:
        raw_url = (
            f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{sha}/rule/Clash/"
            f"{quote(path, safe='/')}"
        )
        body = get_bytes(raw_url)
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(body)
    parsed = yaml.safe_load(body)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("payload"), list):
        raise ValueError(f"invalid payload in {path}")
    payload = parsed["payload"]
    if not payload or any(not isinstance(rule, str) or not rule.strip() for rule in payload):
        raise ValueError(f"empty or non-string payload in {path}")
    return name, path, payload


def canonical(rule: str) -> str:
    parts = [part.strip() for part in rule.split(",")]
    if not parts:
        raise ValueError("empty rule")
    parts[0] = parts[0].upper()
    if len(parts) > 1 and parts[0] in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}:
        parts[1] = parts[1].lower().rstrip(".")
    return ",".join(parts)


def domain_part(rule: str) -> tuple[str, str] | None:
    parts = canonical(rule).split(",")
    if len(parts) < 2 or parts[0] not in {"DOMAIN", "DOMAIN-SUFFIX"}:
        return None
    domain = parts[1]
    if not domain or not re.fullmatch(r"[a-z0-9*_.-]+", domain):
        return None
    return parts[0], domain


def is_inside_root(path: Path) -> bool:
    return path.resolve().is_relative_to(ROOT.resolve())


def icon(name: str) -> str:
    return f"{ICON_BASE}/{name}.png"


def group(name: str, mode: str, icon_name: str) -> dict:
    regions = [label for label, _, _ in REGIONS]
    default_proxy = ["节点选择", "自动选择", *regions, "手动切换", "DIRECT"]
    direct = ["DIRECT", "节点选择", "自动选择", "手动切换"]
    options = {
        "proxy": default_proxy,
        "direct": direct,
        "block": ["REJECT", "DIRECT"],
        "ai": ["非港节点", "台湾节点", "狮城节点", "日本节点", "美国节点", "韩国节点", "DIRECT"],
        "taiwan": ["台湾节点", "节点选择", "手动切换", "DIRECT"],
        "netflix": ["奈飞节点", *default_proxy],
        "domestic_media": ["DIRECT", "香港节点", "台湾节点", "节点选择", "手动切换"],
    }
    if mode not in options:
        raise ValueError(f"unknown group mode: {mode}")
    return {"name": name, "type": "select", "icon": icon(icon_name), "proxies": options[mode]}


def base_groups() -> list[dict]:
    regions = [label for label, _, _ in REGIONS]
    groups = [
        {"name": "节点选择", "type": "select", "icon": icon("Proxy"),
         "proxies": ["自动选择", *regions, "手动切换", "DIRECT"]},
        {"name": "手动切换", "type": "select", "include-all": True,
         "icon": icon("Proxy"), "empty-fallback": "REJECT"},
        {"name": "自动选择", "type": "url-test", "include-all": True,
         "url": "https://www.gstatic.com/generate_204", "interval": 300,
         "tolerance": 50, "icon": icon("Auto"), "empty-fallback": "REJECT"},
        {"name": "非港节点", "type": "select", "include-all": True,
         "exclude-filter": r"(?i)港|HK|Hong[ _-]?Kong", "icon": icon("AI"),
         "empty-fallback": "REJECT"},
        {"name": "奈飞节点", "type": "select", "include-all": True,
         "filter": r"(?i)NF|奈飞|解锁|Netflix|Media", "icon": icon("Netflix"),
         "empty-fallback": "REJECT"},
    ]
    for name, pattern, icon_name in REGIONS:
        groups.append({"name": name, "type": "url-test", "include-all": True,
                       "filter": pattern, "url": "https://www.gstatic.com/generate_204",
                       "interval": 300, "tolerance": 50, "icon": icon(icon_name),
                       "empty-fallback": "REJECT"})
    groups.append({"name": "漏网之鱼", "type": "select", "icon": icon("Final"),
                   "proxies": ["节点选择", "自动选择", "DIRECT", "手动切换"]})
    return groups


def catalog_groups() -> list[dict]:
    groups: list[dict] = []
    modes: dict[str, str] = {}
    for entry in CATALOG:
        # LAN rules target Mihomo's built-in DIRECT policy, so changing the
        # domestic policy group cannot send local traffic through a proxy.
        if entry.group == "DIRECT":
            if entry.mode != "direct":
                raise ValueError(f"built-in DIRECT has non-direct mode: {entry.slug}")
            continue
        previous_mode = modes.get(entry.group)
        if previous_mode is not None:
            if previous_mode != entry.mode:
                raise ValueError(f"conflicting modes in {entry.group}: {previous_mode}, {entry.mode}")
            continue
        modes[entry.group] = entry.mode
        groups.append(group(entry.group, entry.mode, entry.icon))
    return groups


def validate_override(override: dict, provider_files: dict[str, list[str]]) -> None:
    groups = override["proxy-groups"]
    group_names = [entry["name"] for entry in groups]
    if len(group_names) != len(set(group_names)):
        raise ValueError("duplicate proxy group name")
    known = set(group_names) | {"DIRECT", "REJECT", "REJECT-DROP", "PASS"}
    for entry in groups:
        for option in entry.get("proxies", []):
            if option not in known:
                raise ValueError(f"unknown proxy target {option!r} in {entry['name']}")
    for entry in CATALOG:
        name = f"bm7_{entry.slug}"
        if name not in provider_files or not provider_files[name]:
            raise ValueError(f"missing provider payload: {name}")
        if entry.group not in known:
            raise ValueError(f"missing policy group: {entry.group}")
    if override["rules"][-1] != "MATCH,漏网之鱼":
        raise ValueError("MATCH must be last")
    for line in override["rules"][:-1]:
        _, provider, target = line.split(",", 2)
        if provider not in override["rule-providers"] or target not in known:
            raise ValueError(f"invalid rule reference: {line}")


def suffix_conflicts(owners: dict[str, str], limit: int = 80) -> tuple[int, list[dict]]:
    suffixes: dict[str, tuple[str, str]] = {}
    domains: list[tuple[str, str, str]] = []
    for rule, group_name in owners.items():
        match = domain_part(rule)
        if match:
            kind, domain = match
            domains.append((kind, domain, group_name))
            if kind == "DOMAIN-SUFFIX":
                suffixes[domain] = (rule, group_name)
    examples: list[dict] = []
    count = 0
    for kind, domain, group_name in domains:
        labels = domain.split(".")
        for start in range(0 if kind == "DOMAIN" else 1, len(labels) - 1):
            parent = ".".join(labels[start:])
            other = suffixes.get(parent)
            if other and other[1] != group_name:
                count += 1
                if len(examples) < limit:
                    examples.append({"specific": f"{kind},{domain}", "specific_group": group_name,
                                     "broader": other[0], "broader_group": other[1]})
                break
    return count, examples


def compile_rules(data: dict[str, tuple[str, list[str]]]) -> tuple[dict[str, list[str]], dict]:
    provider_files: dict[str, list[str]] = {}
    seen: dict[str, tuple[str, str]] = {}
    exact_pairs: Counter[tuple[str, str]] = Counter()
    exact_examples: list[dict] = []
    policy_conflicts: list[dict] = []
    mode_by_group = {entry.group: entry.mode for entry in CATALOG}
    within_source = 0
    for entry in CATALOG:
        provider = f"bm7_{entry.slug}"
        output: list[str] = []
        local: set[str] = set()
        for source in entry.sources:
            _, rules = data[source]
            for rule in rules:
                key = canonical(rule)
                if key in local:
                    within_source += 1
                    continue
                local.add(key)
                previous = seen.get(key)
                if previous:
                    previous_group, previous_source = previous
                    exact_pairs[(previous_group, entry.group)] += 1
                    if len(exact_examples) < 80 and previous_group != entry.group:
                        exact_examples.append({"rule": key, "kept_group": previous_group,
                                               "kept_source": previous_source,
                                               "removed_group": entry.group, "removed_source": source})
                    previous_mode = mode_by_group[previous_group]
                    if (previous_group != entry.group and
                            "block" in {previous_mode, entry.mode} and
                            previous_mode != entry.mode and len(policy_conflicts) < 100):
                        policy_conflicts.append({"rule": key, "kept_group": previous_group,
                                                 "kept_mode": previous_mode,
                                                 "removed_group": entry.group,
                                                 "removed_mode": entry.mode})
                    continue
                seen[key] = (entry.group, source)
                output.append(rule.strip())
        provider_files[provider] = output
    owners = {rule: info[0] for rule, info in seen.items()}
    suffix_count, suffix_examples = suffix_conflicts(owners)
    conflict_report = {
        "source_rule_count": sum(len(data[source][1]) for entry in CATALOG for source in entry.sources),
        "unique_rule_count": len(seen),
        "duplicate_within_provider": within_source,
        "same_group_duplicates_across_providers": sum(
            count for (first, second), count in exact_pairs.items() if first == second
        ),
        "cross_group_duplicates": sum(
            count for (first, second), count in exact_pairs.items() if first != second
        ),
        "exact_duplicates_by_group_pair": [
            {"kept_group": first, "removed_group": second, "count": count}
            for (first, second), count in exact_pairs.most_common()
        ],
        "exact_duplicate_examples": exact_examples,
        "block_vs_service_examples": policy_conflicts,
        "domain_suffix_overlap_count": suffix_count,
        "domain_suffix_overlap_examples": suffix_examples,
    }
    return provider_files, conflict_report


def make_override(repo: str, sha: str, providers: dict[str, list[str]]) -> dict:
    groups = base_groups() + catalog_groups()
    root_url = f"https://raw.githubusercontent.com/{repo}/main/dist/providers"
    rule_providers = {}
    rules = []
    for entry in CATALOG:
        provider = f"bm7_{entry.slug}"
        rule_providers[provider] = {
            "type": "http", "behavior": "classical", "format": "yaml",
            "url": f"{root_url}/{provider}.yaml",
            "path": f"./rule_provider/bm7/{provider}.yaml", "interval": 86400,
        }
        rules.append(f"RULE-SET,{provider},{entry.group}")
    rules.append("MATCH,漏网之鱼")
    result = {"proxy-groups": groups, "rule-providers": rule_providers, "rules": rules}
    validate_override(result, providers)
    return result


def write_yaml(path: Path, payload: object, header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False, width=120)
    parsed = yaml.safe_load(body)
    if parsed != payload:
        raise ValueError(f"YAML round-trip failed: {path}")
    path.write_text(header + body, encoding="utf-8", newline="\n")


def write_outputs(repo: str, sha: str, data: dict[str, tuple[str, list[str]]],
                  providers: dict[str, list[str]], conflicts: dict) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    temp = Path(tempfile.mkdtemp(prefix="bm7-build-", dir=ROOT / ".cache"))
    if not is_inside_root(temp):
        raise ValueError("unsafe temporary output path")
    try:
        dist = temp / "dist"
        reports = temp / "reports"
        dist.mkdir()
        reports.mkdir()
        override = make_override(repo, sha, providers)
        for entry in CATALOG:
            name = f"bm7_{entry.slug}"
            sources = ", ".join(data[source][0] for source in entry.sources)
            header = (f"# Derived from {UPSTREAM_REPO} (GPL-2.0)\n"
                      f"# Upstream commit: {sha}\n# Sources: {sources}\n")
            write_yaml(dist / "providers" / f"{name}.yaml", {"payload": providers[name]}, header)
        header = ("# Built with ChatGPT (Codex) for personal learning; generated automatically.\n"
                  "# Clash Party YAML override; generated, do not edit directly.\n"
                  f"# Upstream: https://github.com/{UPSTREAM_REPO} @ {sha}\n"
                  "# Rules and generated providers derived from upstream GPL-2.0 data.\n")
        write_yaml(dist / "clash-party.yaml", override, header)
        metadata = {
            "checked_at_utc": now, "upstream_commit": sha,
            "upstream_repository": UPSTREAM_REPO, "published_repository": repo,
            "policy_groups": len(override["proxy-groups"]),
            "rule_providers": len(override["rule-providers"]),
            "source_directories": sum(len(entry.sources) for entry in CATALOG),
            "unique_rules": conflicts["unique_rule_count"],
        }
        (dist / "build-info.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (reports / "conflicts.json").write_text(json.dumps(conflicts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lines = ["# 规则重复与覆盖报告", "", f"- 上游版本：`{sha}`",
                 f"- 原始规则条数：{conflicts['source_rule_count']:,}",
                 f"- 去重后规则条数：{conflicts['unique_rule_count']:,}",
                 f"- 同一规则集内重复：{conflicts['duplicate_within_provider']:,}",
                 f"- 同组不同规则集的相同规则：{conflicts['same_group_duplicates_across_providers']:,}",
                 f"- 跨组相同规则：{conflicts['cross_group_duplicates']:,}",
                 f"- 不同策略组的域名后缀覆盖：{conflicts['domain_suffix_overlap_count']:,}",
                 "", "规则按 `dist/clash-party.yaml` 中的先后顺序匹配。完全相同的规则仅保留先出现的一条。",
                 "域名后缀覆盖保留在报告中，专用规则优先于通用合集。", "", "## 跨组重复最多的策略组", "",
                 "| 先匹配 | 后匹配 | 相同规则数 |", "|---|---|---:|"]
        for pair in conflicts["exact_duplicates_by_group_pair"]:
            if pair["kept_group"] != pair["removed_group"]:
                lines.append(f"| {pair['kept_group']} | {pair['removed_group']} | {pair['count']:,} |")
            if len(lines) > 75:
                break
        lines += ["", "## 域名后缀覆盖示例", "", "| 专用规则 | 策略组 | 通用后缀 | 策略组 |",
                  "|---|---|---|---|"]
        for example in conflicts["domain_suffix_overlap_examples"][:40]:
            lines.append(f"| `{example['specific']}` | {example['specific_group']} | "
                         f"`{example['broader']}` | {example['broader_group']} |")
        lines += ["", "## 拦截规则与服务规则相撞", "",
                  "以下完全相同的规则出现在拦截与非拦截策略中。表格中的先匹配策略生效；",
                  "这些项目需要结合实际连通性决定是否单独放行。", "",
                  "| 规则 | 先匹配 | 后匹配 |", "|---|---|---|"]
        for example in conflicts["block_vs_service_examples"][:60]:
            lines.append(f"| `{example['rule']}` | {example['kept_group']} | {example['removed_group']} |")
        (reports / "conflicts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        for name in ("dist", "reports"):
            target = ROOT / name
            if not is_inside_root(target):
                raise ValueError(f"unsafe output path: {target}")
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(temp / name), str(target))
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "aohaha127/clash-party-rule-compiler"))
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("--repo must be OWNER/REPO")
    slugs = [entry.slug for entry in CATALOG]
    sources = [source for entry in CATALOG for source in entry.sources]
    if len(slugs) != len(set(slugs)) or len(sources) != len(set(sources)):
        raise ValueError("catalog has duplicate slugs or source directories")
    (ROOT / ".cache").mkdir(exist_ok=True)
    sha, files = upstream_snapshot()
    paths = {source: source_path(source, files) for source in sources}
    data: dict[str, tuple[str, list[str]]] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_source, sha, source, path): source
                   for source, path in paths.items()}
        for future in as_completed(futures):
            source, path, rules = future.result()
            data[source] = (path, rules)
    providers, conflicts = compile_rules(data)
    write_outputs(args.repo, sha, data, providers, conflicts)
    print(json.dumps({"repository": args.repo, "upstream_commit": sha,
                      "groups": len(base_groups()) + len(catalog_groups()),
                      "providers": len(providers), "sources": len(sources),
                      "raw_rules": conflicts["source_rule_count"],
                      "unique_rules": conflicts["unique_rule_count"],
                      "suffix_overlaps": conflicts["domain_suffix_overlap_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
