"""Export documented Stash overrides and Loon configuration templates."""
from __future__ import annotations

from collections import Counter
import copy
import json
from pathlib import Path
import re

import yaml

from build import ROOT, canonical, write_yaml
from catalog import REGIONS

SUPPORTED = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6", "IP-ASN"}
NON_HK = [name for name, _, _ in REGIONS if name != "香港节点"]
VARIANTS = {"default": "clash-party.yaml", "adblock": "clash-party-adblock.yaml",
            "local": "clash-party-local-services.yaml", "full": "clash-party-full.yaml"}


def portable_rules(payload: list[str]) -> tuple[list[str], Counter]:
    kept, omitted = [], Counter()
    for raw in payload:
        rule = canonical(raw)
        kind = rule.split(",", 1)[0]
        if kind == "PROCESS-NAME":
            omitted[kind] += 1
        elif kind not in SUPPORTED:
            raise ValueError(f"unreviewed portable rule type: {kind}")
        else:
            kept.append(rule)
    return kept, omitted


def stash_groups(groups: list[dict]) -> list[dict]:
    output = copy.deepcopy(groups)
    for entry in output:
        entry.pop("empty-fallback", None)
        entry.pop("exclude-filter", None)
        url = entry.pop("url", None)
        if url:
            entry["benchmark-url"] = url
        if entry["name"] == "非港节点":
            entry.pop("include-all", None)
            entry.pop("filter", None)
            entry["proxies"] = [*NON_HK, "REJECT"]
        elif entry.get("include-all"):
            entry["proxies"] = ["REJECT"]
            if entry.get("filter"):
                entry["filter"] = f"(?:{entry['filter']})|^REJECT$"
    return output


def loon_groups(groups: list[dict]) -> tuple[list[str], list[str]]:
    filters, output = [], []
    for entry in groups:
        name = entry["name"]
        options = list(entry.get("proxies", []))
        if entry.get("include-all"):
            filter_name = f"筛选-{name}"
            pattern = entry.get("filter", ".*")
            if entry.get("exclude-filter"):
                pattern = r"(?i)^(?!.*(?:港|HK|Hong[ _-]?Kong)).*$"
            filters.append(f"{filter_name} = NameRegex,机场订阅,FilterKey = {pattern}")
            options = [filter_name, "REJECT"]
        kind = entry["type"]
        if kind not in {"select", "url-test"}:
            raise ValueError(f"unreviewed Loon group type: {kind}")
        line = f"{name} = {kind}," + ",".join(options)
        if kind == "url-test":
            line += ",url=https://www.gstatic.com/generate_204,interval=300,tolerance=50"
        output.append(line)
    return filters, output


def export_clients(repo: str) -> None:
    root_url = f"https://raw.githubusercontent.com/{repo}/main/dist"
    provider_cache = {}
    report = {"runtime_validation": "Structural validation only; native Loon/Stash apps are not available on Windows.",
              "sources": {"stash": "https://stash.wiki/en/configuration/override",
                          "loon": "https://github.com/Loon0x00/LoonManual"}, "variants": {}}
    for variant, filename in VARIANTS.items():
        source = yaml.safe_load((ROOT / "dist" / filename).read_text(encoding="utf-8"))
        available, omitted = {}, Counter()
        for name in source["rule-providers"]:
            if name not in provider_cache:
                path = ROOT / "dist" / "providers" / f"{name}.yaml"
                raw = path.read_text(encoding="utf-8")
                payload, dropped = portable_rules(yaml.safe_load(raw)["payload"])
                header = "\n".join(line for line in raw.splitlines() if line.startswith("#")) + "\n"
                provider_cache[name] = (payload, dropped, header)
                if payload:
                    write_yaml(ROOT / "dist" / "stash" / "providers" / f"{name}.yaml",
                               {"payload": payload}, header + "# iOS portable export; process rules omitted.\n")
                    loon_path = ROOT / "dist" / "loon" / "providers" / f"{name}.list"
                    loon_path.parent.mkdir(parents=True, exist_ok=True)
                    loon_path.write_text(header + "# Loon rule set; process rules omitted.\n" +
                                         "\n".join(payload) + "\n", encoding="utf-8", newline="\n")
            payload, dropped, _ = provider_cache[name]
            omitted.update(dropped)
            if payload:
                available[name] = payload

        groups = stash_groups(source["proxy-groups"])
        stash = {"name": f"学习分流-{variant}", "desc": "ChatGPT (Codex) 构建；个人学习；blackmatrix7 + ACL4SSR",
                 "proxy-groups": groups, "rule-providers": {}, "rules": []}
        filters, loon_proxy_groups = loon_groups(source["proxy-groups"])
        local_rules, remote_rules = [], []
        for line in source["rules"]:
            kind, matcher, *rest = line.split(",")
            if kind == "RULE-SET":
                name, target = matcher, rest[0]
                if name not in available:
                    continue
                stash["rule-providers"][name] = {
                    "behavior": "classical", "format": "yaml", "interval": 86400,
                    "url": f"{root_url}/stash/providers/{name}.yaml",
                    "path": f"./rules/{name}.yaml"}
                stash["rules"].append(line)
                remote_rules.append(f"{root_url}/loon/providers/{name}.list,policy={target},tag={name},enabled=true")
            elif kind == "MATCH":
                stash["rules"].append(line)
                local_rules.append(f"FINAL,{matcher}")
            else:
                stash["rules"].append(line)
                local_rules.append(line)
        text = yaml.safe_dump(stash, allow_unicode=True, sort_keys=False, width=120)
        # Stash prepends arrays by default. Replace avoids duplicate group names
        # and a second FINAL/MATCH from the subscribed configuration.
        for key in ("proxy-groups", "rule-providers", "rules"):
            text = text.replace(f"\n{key}:\n", f"\n{key}: #!replace\n")
        stash_path = ROOT / "dist" / "stash" / f"{variant}.stoverride"
        stash_path.write_text("# Built with ChatGPT (Codex) for personal learning.\n" + text,
                              encoding="utf-8", newline="\n")
        # Loon local rules have priority over remote rules. FINAL is the fallback;
        # npm's local exact domain deliberately has priority over all remote sets.
        loon = ["# Built with ChatGPT (Codex) for personal learning.",
                "# TEMPLATE: replace the subscription URL below with your Loon subscription.",
                "# Sources/licensing: each remote rule file has its own provenance.",
                "[General]", "dns-server = system", "", "[Proxy]", "", "[Remote Proxy]",
                "机场订阅 = https://example.invalid/replace-with-your-loon-subscription", "",
                "[Remote Filter]", *filters, "", "[Proxy Group]", *loon_proxy_groups,
                "", "[Rule]", *local_rules, "", "[Remote Rule]", *remote_rules, ""]
        (ROOT / "dist" / "loon" / f"{variant}.conf").write_text("\n".join(loon), encoding="utf-8", newline="\n")
        report["variants"][variant] = {"groups": len(groups), "providers": len(available),
                                       "provider_rules": sum(len(rules) for rules in available.values()),
                                       "omitted": dict(omitted),
                                       "stash_non_hk": "Uses the Taiwan/Singapore/Japan/US/Korea region groups.",
                                       "loon_priority": "Loon local rules precede remote rules; domains precede IP rules."}
    (ROOT / "reports" / "clients.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                                     encoding="utf-8")
    metadata_path = ROOT / "dist" / "build-info.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["clients"] = report["variants"]
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_clients() -> None:
    for variant in VARIANTS:
        stash_path = ROOT / "dist" / "stash" / f"{variant}.stoverride"
        text = stash_path.read_text(encoding="utf-8")
        stash = yaml.safe_load(text)
        for key in ("proxy-groups", "rule-providers", "rules"):
            if f"{key}: #!replace" not in text:
                raise ValueError(f"missing Stash replacement marker: {key}")
        names = {group["name"] for group in stash["proxy-groups"]}
        known = names | {"DIRECT", "REJECT"}
        if len(names) != len(stash["proxy-groups"]):
            raise ValueError("duplicate Stash group")
        for group in stash["proxy-groups"]:
            if {"exclude-filter", "empty-fallback", "url"} & set(group):
                raise ValueError("Mihomo-specific option in Stash")
            if any(option not in known for option in group.get("proxies", [])):
                raise ValueError("unknown Stash group reference")
        from validate import check_group_cycles
        check_group_cycles(stash["proxy-groups"])
        for name, provider in stash["rule-providers"].items():
            if {"proxy", "type"} & set(provider):
                raise ValueError("undocumented Stash provider option")
            stash_payload = yaml.safe_load((ROOT / "dist" / "stash" / "providers" / f"{name}.yaml").read_text(encoding="utf-8"))["payload"]
            loon_payload = [line for line in (ROOT / "dist" / "loon" / "providers" / f"{name}.list").read_text(encoding="utf-8").splitlines()
                            if line and not line.startswith("#")]
            if stash_payload != loon_payload or not stash_payload or any(rule.split(",", 1)[0] not in SUPPORTED for rule in stash_payload):
                raise ValueError(f"invalid portable payload: {name}")
        if stash["rules"][-1] != "MATCH,漏网之鱼" or "DOMAIN,registry.npmjs.org,开发工具" not in stash["rules"]:
            raise ValueError("missing portable final/registry route")
        for line in stash["rules"][:-1]:
            kind, matcher, target = line.split(",")
            if target not in known or (kind == "RULE-SET" and matcher not in stash["rule-providers"]):
                raise ValueError(f"unknown Stash rule reference: {line}")
        loon = (ROOT / "dist" / "loon" / f"{variant}.conf").read_text(encoding="utf-8")
        sections = {}
        section = None
        for line in loon.splitlines():
            if line.startswith("["):
                section = line[1:-1]
                sections[section] = []
            elif line and not line.startswith("#") and section:
                sections[section].append(line)
        loon_names = {line.split(" = ", 1)[0] for line in sections["Proxy Group"]}
        filter_names = {line.split(" = ", 1)[0] for line in sections["Remote Filter"]}
        if loon_names != names or len(loon_names) != len(sections["Proxy Group"]):
            raise ValueError("Loon policy groups do not match source")
        for line in sections["Proxy Group"]:
            _, value = line.split(" = ", 1)
            for option in value.split(",")[1:]:
                if "=" not in option and option not in known | filter_names:
                    raise ValueError(f"unknown Loon reference: {option}")
        for line in sections["Remote Filter"]:
            re.compile(line.split("FilterKey = ", 1)[1])
        for line in sections["Remote Rule"]:
            url, policy, *_ = line.split(",")
            if policy.removeprefix("policy=") not in known or not (ROOT / "dist" / "loon" / "providers" / url.rsplit("/", 1)[1]).is_file():
                raise ValueError("invalid Loon remote rule")
        if len(sections["Remote Rule"]) != len(stash["rule-providers"]):
            raise ValueError("Loon/Stash provider reference mismatch")
        expected_local = [line.replace("MATCH,", "FINAL,", 1) if line.startswith("MATCH,") else line
                          for line in stash["rules"] if not line.startswith("RULE-SET,")]
        if sections["Rule"] != expected_local:
            raise ValueError("Loon local rule order/targets differ from source")
        expected_remote = [(line.split(",")[1], line.split(",")[2]) for line in stash["rules"]
                           if line.startswith("RULE-SET,")]
        actual_remote = [(line.split(",")[0].rsplit("/", 1)[1].removesuffix(".list"),
                          line.split(",")[1].removeprefix("policy=")) for line in sections["Remote Rule"]]
        if actual_remote != expected_remote:
            raise ValueError("Loon remote rule order/targets differ from source")
        print(f"validated portable {variant}: {len(names)} groups, {len(stash['rule-providers'])} providers")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="aohaha127/clash-party-rule-compiler")
    args = parser.parse_args()
    export_clients(args.repo)
    validate_clients()
