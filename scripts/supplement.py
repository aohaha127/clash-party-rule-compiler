"""Curated ACL4SSR supplements, with separate source attribution and opt-in variants."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import hashlib
from pathlib import Path
import re

import yaml

from build import ROOT, canonical, domain_part, github_api, verified_blob, write_yaml, suffix_conflicts
from catalog import CATALOG

REPO = "ACL4SSR/ACL4SSR"
INLINE_RULES = ["DOMAIN,registry.npmjs.org,开发工具"]
SHARED_AI = {"auth0.com", "identrust.com", "intercom.io", "intercomcdn.com",
             "client-api.arkoselabs.com", "events.statsigapi.net", "featuregates.org"}
NAS = {"plex.direct", "tpddns.cn", "3322.org", "3322.net", "nat123.com", "dnsapi.cn",
       "checkip.synology.com", "checkipv6.synology.com", "checkport.synology.com",
       "ddns.synology.com", "quickconnect.to", "quickconnect.cn", "synology.cn",
       "edge.api.myqnapcloud.com", "myqnapcloud.com"}
REMOTE = {"SunloginClient.exe", "ToDesk_Session.exe", "ToDesk_Service.exe", "ToDesk.exe", "mstsc.exe"}
SPECS = [
    ("ai", "Ruleset/AI.list", "AI 服务", "bm7_telegram", "default"),
    ("developer", "Ruleset/Developer.list", "开发工具", "bm7_cloudflare", "default"),
    ("download", "Ruleset/Download.list", "国内直连", "bm7_download", "default"),
    ("game_download", "Ruleset/GameDownload.list", "游戏直连", "bm7_openai", "default"),
    ("private_tracker", "Ruleset/PrivateTracker.list", "国内直连", "bm7_openai", "local"),
    ("nas", "Ruleset/NaSDDNS.list", "国内直连", "bm7_openai", "local"),
    ("remote_desktop", "Ruleset/RemoteDesktop.list", "国内直连", "bm7_openai", "local"),
    ("easylist", "BanEasyList.list", "广告拦截", "bm7_openai", "ads"),
    ("easylist_china", "BanEasyListChina.list", "广告拦截", "bm7_openai", "ads"),
]


def parse_list(body: bytes, slug: str) -> tuple[list[str], list[dict]]:
    accepted, excluded = [], []
    for number, line in enumerate(body.decode("utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith(("#", "//")):
            continue
        rule = canonical(line)
        parts = rule.split(",")
        kind = parts[0]
        reason = None
        if kind not in {"DOMAIN", "DOMAIN-SUFFIX", "PROCESS-NAME"}:
            reason = "unsupported or intentionally broad matcher"
        elif len(parts) != 2 or not parts[1]:
            raise ValueError(f"malformed ACL4SSR rule at {slug}:{number}: {line}")
        elif kind != "PROCESS-NAME" and not domain_part(rule):
            raise ValueError(f"invalid domain at {slug}:{number}: {line}")
        elif slug == "ai" and parts[1] in SHARED_AI:
            reason = "shared authentication / telemetry domain"
        elif slug == "developer" and parts[1] in {"reddit.com", "medium.com"}:
            reason = "general community service, retain existing policy"
        elif slug == "download" and kind != "PROCESS-NAME":
            reason = "download supplement only permits explicit processes"
        elif slug == "nas" and parts[1] not in NAS:
            reason = "outside explicit NAS/DDNS allowlist"
        elif slug == "remote_desktop" and parts[1] not in REMOTE:
            reason = "generic installer / helper process"
        elif slug not in {"download", "remote_desktop"} and kind == "PROCESS-NAME":
            reason = "process matcher outside intended category"
        if reason:
            excluded.append({"rule": rule, "reason": reason})
        else:
            accepted.append(rule)
    if not accepted:
        raise ValueError(f"no selected ACL4SSR rules: {slug}")
    return accepted, excluded


def resolve(entries: list[tuple[str, str, list[str]]]) -> tuple[list[tuple[str, str, list[str]]], dict]:
    seen, suffixes, result, removed = {}, {}, [], []
    exact_count = coverage_count = classification_count = 0
    for name, target, payload in entries:
        kept = []
        for raw in payload:
            rule = canonical(raw)
            previous = seen.get(rule)
            match = domain_part(rule)
            covering = None
            if match:
                labels = match[1].split(".")
                for start in range(len(labels) - 1):
                    owner = suffixes.get(".".join(labels[start:]))
                    if owner and (owner[1] == target or (name.startswith("acl_") and owner[1] in
                                                        {"广告拦截", "应用净化", "隐私拦截"})):
                        covering = owner
                        break
            # BM7 payloads retain their semantic coverage. ACL supplements omit already
            # covered rules within the same policy, and never bypass earlier blockers.
            if previous or (name.startswith("acl_") and covering):
                owner = previous or covering
                exact_count += bool(previous)
                coverage_count += not bool(previous)
                classification_count += bool(previous and owner[1] != target)
                if len(removed) < 1000:
                    removed.append({"rule": rule, "kept_provider": owner[0], "kept_group": owner[1],
                                    "removed_provider": name, "removed_group": target,
                                    "reason": "exact" if previous else "suffix coverage"})
                continue
            seen[rule] = (name, target)
            if match and match[0] == "DOMAIN-SUFFIX":
                suffixes[match[1]] = (name, target)
            kept.append(rule)
        if kept:
            result.append((name, target, kept))
    count, examples = suffix_conflicts({rule: owner[1] for rule, owner in seen.items()})
    return result, {"unique_rules": len(seen), "removed_examples": removed,
                    "exact_duplicates_removed": exact_count, "covered_supplements_removed": coverage_count,
                    "cross_policy_duplicates": classification_count,
                    "suffix_overlap_count": count, "suffix_overlap_examples": examples}


def augment(published_repo: str) -> None:
    commit = github_api(f"repos/{REPO}/commits/master")
    sha = commit["sha"]
    tree = github_api(f"repos/{REPO}/git/trees/{commit['commit']['tree']['sha']}?recursive=1")
    if tree.get("truncated"):
        raise ValueError("ACL4SSR tree truncated")
    files = {entry["path"]: entry for entry in tree["tree"] if entry["type"] == "blob"}

    def load(spec):
        slug, path, *_ = spec
        full = f"Clash/{path}"
        body = verified_blob(REPO, sha, full, files[full], ROOT / ".cache" / "acl4ssr" / sha / full)
        rules, excluded = parse_list(body, slug)
        return slug, rules, excluded

    with ThreadPoolExecutor(max_workers=4) as executor:
        fetched = list(executor.map(load, SPECS))
    data = {slug: rules for slug, rules, _ in fetched}
    exclusions = {slug: excluded for slug, _, excluded in fetched}
    license_body = verified_blob(REPO, sha, "LICENCE", files["LICENCE"],
                                 ROOT / ".cache" / "acl4ssr" / sha / "LICENCE")
    (ROOT / "licenses").mkdir(exist_ok=True)
    (ROOT / "licenses" / "ACL4SSR-CC-BY-SA-4.0.txt").write_bytes(license_body)
    base = yaml.safe_load((ROOT / "dist" / "clash-party.yaml").read_text(encoding="utf-8"))
    original = []
    for line in base["rules"][:-1]:
        _, name, target = line.split(",")
        payload = yaml.safe_load((ROOT / "dist" / "providers" / f"{name}.yaml").read_text(encoding="utf-8"))["payload"]
        original.append((name, target, payload))
    variants = {}
    emitted = {}
    original_digests = {name: hashlib.sha256("\n".join(canonical(rule) for rule in payload).encode()).hexdigest()
                        for name, _, payload in original}
    for variant, enabled, filename in [
        ("default", {"default"}, "clash-party.yaml"),
        ("adblock", {"default", "ads"}, "clash-party-adblock.yaml"),
        ("local", {"default", "local"}, "clash-party-local-services.yaml"),
        ("full", {"default", "local", "ads"}, "clash-party-full.yaml"),
    ]:
        entries = []
        for original_entry in original:
            for slug, _, target, before, mode in SPECS:
                if mode in enabled and before == original_entry[0]:
                    entries.append((f"acl_{slug}", target, data[slug]))
            entries.append(original_entry)
        resolved, report = resolve(entries)
        config = {"proxy-groups": base["proxy-groups"], "rule-providers": {}, "rules": []}
        for name, target, payload in resolved:
            # Variant names keep modified BM7 files separate; ACL-derived data never
            # receives the BM7 GPL-2.0 provenance header.
            digest = hashlib.sha256("\n".join(payload).encode()).hexdigest()
            identity = (name, digest)
            candidate = name if original_digests.get(name) == digest else f"{variant}_{name}"
            published_name = emitted.setdefault(identity, candidate)
            is_acl = name.startswith("acl_")
            upstream = REPO if is_acl else "blackmatrix7/ios_rule_script"
            license_name = "CC-BY-SA-4.0" if is_acl else "GPL-2.0"
            header = f"# Derived from {upstream}; {license_name}\n"
            if is_acl:
                spec = next(spec for spec in SPECS if name == f"acl_{spec[0]}")
                header += f"# Commit: {sha}; source: Clash/{spec[1]}; curated and deduplicated\n"
            else:
                header += f"# Commit: {json.loads((ROOT / 'dist' / 'build-info.json').read_text())['upstream_commit']}\n"
                entry = next(entry for entry in CATALOG if name == f"bm7_{entry.slug}")
                header += f"# Source directories: {', '.join(entry.sources)}; deduplicated\n"
            write_yaml(ROOT / "dist" / "providers" / f"{published_name}.yaml", {"payload": payload}, header)
            config["rule-providers"][published_name] = {
                "type": "http", "behavior": "classical", "format": "yaml",
                "url": f"https://raw.githubusercontent.com/{published_repo}/main/dist/providers/{published_name}.yaml",
                "path": f"./rule_provider/{'bm7' if published_name.startswith('bm7_') else 'compiled'}/{published_name}.yaml",
                "proxy": "节点选择", "interval": 86400}
            config["rules"].append(f"RULE-SET,{published_name},{target}")
        # Keep LAN protection first; the registry route works even when HTTP
        # rule providers have not downloaded successfully yet.
        config["rules"][1:1] = INLINE_RULES
        config["rules"].append("MATCH,漏网之鱼")
        write_yaml(ROOT / "dist" / filename, config,
                   "# Built with ChatGPT (Codex) for personal learning.\n"
                   "# Provider licenses and source provenance are recorded separately.\n")
        report["groups"] = len(config["proxy-groups"])
        report["providers"] = len(config["rule-providers"])
        report["inline_rules"] = INLINE_RULES
        report["acl_providers"] = {name: len(payload) for name, _, payload in resolved if name.startswith("acl_")}
        variants[variant] = report
    metadata_path = ROOT / "dist" / "build-info.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata.update({"acl4ssr_commit": sha, "acl4ssr_repository": REPO,
                     "rule_providers": variants["default"]["providers"],
                     "unique_rules": variants["default"]["unique_rules"],
                     "variants": {name: {k: v for k, v in report.items() if k not in
                                          {"removed_examples", "suffix_overlap_examples"}}
                                  for name, report in variants.items()}})
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {"repository": REPO, "commit": sha, "excluded_rules": exclusions, "variants": variants}
    (ROOT / "reports" / "acl4ssr.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# ACL4SSR 补充与冲突报告", "", f"上游：{REPO} @ `{sha}`。", "",
             "完全重复保留先匹配的规则；补充规则已被同策略后缀覆盖时省略。拦截策略优先。",
             "原 blackmatrix7 统计见 conflicts.md；合并后统计见本报告及 build-info.json。", "",
             "| 版本 | 策略组 | 规则集 | 规则条目 |", "|---|---:|---:|---:|"]
    for name, detail in variants.items():
        lines.append(f"| {name} | {detail['groups']} | {detail['providers']} | {detail['unique_rules']} |")
    for name, detail in variants.items():
        lines += ["", f"## {name} 重复与策略归类示例", "", "| 规则 | 保留策略 | 原策略 | 原因 |", "|---|---|---|---|"]
        for row in detail["removed_examples"]:
            if "acl_" in row["kept_provider"] or "acl_" in row["removed_provider"]:
                lines.append(f"| `{row['rule']}` | {row['kept_group']} | {row['removed_group']} | {row['reason']} |")
    lines += ["", "## 主动排除", ""]
    for slug, rows in exclusions.items():
        lines.append(f"- {slug}：排除 {len(rows)} 条，完整规则和原因见 acl4ssr.json。")
    (ROOT / "reports" / "acl4ssr.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Preserve legacy bm7_* URLs for subscriptions that have not refreshed their
    # override yet. New configurations use the separately deduplicated variants.
    used = set(emitted.values()) | set(original_digests)
    for path in (ROOT / "dist" / "providers").glob("*.yaml"):
        if path.stem not in used:
            path.unlink()
    print(json.dumps(metadata["variants"], ensure_ascii=False))
