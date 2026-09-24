#!/usr/bin/env python3
"""Download the latest stable official Linux Mihomo for CI validation."""

import gzip
import hashlib
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

from build import ROOT, github_api


def main() -> None:
    release = github_api("repos/MetaCubeX/mihomo/releases/latest")
    tag = release["tag_name"]
    expected_name = f"mihomo-linux-amd64-{tag}.gz"
    asset = next((item for item in release["assets"] if item["name"] == expected_name), None)
    if not asset:
        raise ValueError(f"official Mihomo asset missing: {expected_name}")
    digest = asset.get("digest", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("official Mihomo asset has no SHA-256 digest")
    url = asset["browser_download_url"]
    with urlopen(Request(url, headers={"User-Agent": "clash-party-rule-compiler/1.0"}), timeout=120) as response:
        compressed = response.read(50_000_001)
    if len(compressed) > 50_000_000:
        raise ValueError("Mihomo asset unexpectedly large")
    actual = hashlib.sha256(compressed).hexdigest()
    if actual != digest.split(":", 1)[1]:
        raise ValueError("Mihomo asset SHA-256 mismatch")
    destination = ROOT / ".cache" / "mihomo"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(gzip.decompress(compressed))
    destination.chmod(0o755)
    print(f"{destination} ({tag}, verified SHA-256)")


if __name__ == "__main__":
    main()
