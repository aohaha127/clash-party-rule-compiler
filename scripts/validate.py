#!/usr/bin/env python3
"""Validate generated YAML and optionally test it with the Mihomo core."""

from __future__ import annotations

import argparse
from collections import Counter
import copy
from pathlib import Path
import subprocess

import yaml

from build import ROOT, canonical, validate_override


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader: yaml.SafeLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.load(stream, Loader=UniqueKeyLoader)


def check_group_cycles(groups: list[dict]) -> None:
    graph = {group["name"]: [name for name in group.get("proxies", []) if name in
                              {item["name"] for item in groups}] for group in groups}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visiting:
            raise ValueError(f"proxy group cycle at {name}")
        if name in visited:
            return
        visiting.add(name)
        for child in graph[name]:
            visit(child)
        visiting.remove(name)
        visited.add(name)

    for name in graph:
        visit(name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mihomo", type=Path)
    args = parser.parse_args()
    override = read_yaml(ROOT / "dist" / "clash-party.yaml")
    providers = {}
    global_seen: set[str] = set()
    for name in override["rule-providers"]:
        payload = read_yaml(ROOT / "dist" / "providers" / f"{name}.yaml")["payload"]
        if not payload:
            raise ValueError(f"empty provider {name}")
        keys = [canonical(rule) for rule in payload]
        if len(keys) != len(set(keys)):
            raise ValueError(f"duplicate rule inside {name}")
        overlap = global_seen.intersection(keys)
        if overlap:
            raise ValueError(f"duplicate rule across providers: {name}: {next(iter(overlap))}")
        global_seen.update(keys)
        providers[name] = payload
    validate_override(override, providers)
    check_group_cycles(override["proxy-groups"])
    if len(override["rules"]) != len(providers) + 1:
        raise ValueError("rule count does not match provider count")

    if args.mihomo:
        test = copy.deepcopy(override)
        test["mode"] = "rule"
        test["proxies"] = [{"name": "TEST-NODE", "type": "ss", "server": "127.0.0.1",
                            "port": 443, "cipher": "aes-128-gcm", "password": "test123"}]
        for name, provider in test["rule-providers"].items():
            provider.pop("url")
            provider.pop("interval")
            provider["type"] = "file"
            provider["path"] = f"./dist/providers/{name}.yaml"
        scratch = ROOT / ".cache" / "mihomo-validation.yaml"
        scratch.parent.mkdir(exist_ok=True)
        scratch.write_text(yaml.safe_dump(test, allow_unicode=True, sort_keys=False), encoding="utf-8")
        result = subprocess.run([str(args.mihomo.resolve()), "-t", "-d", str(ROOT), "-f", str(scratch)],
                                capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            raise RuntimeError(f"Mihomo validation failed:\n{result.stdout}\n{result.stderr}")
        print(result.stdout.strip())
    counts = Counter(rule.split(",", 1)[0] for payload in providers.values() for rule in payload)
    print(f"validated {len(override['proxy-groups'])} groups, {len(providers)} providers, "
          f"{len(global_seen)} distinct rules; types: {dict(counts)}")


if __name__ == "__main__":
    main()
