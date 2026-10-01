import base64
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build import verified_blob
from supplement import parse_list, resolve


class CompilerTests(unittest.TestCase):
    def test_truncated_download_and_corrupt_cache_recover_from_verified_blob(self):
        body = b"DOMAIN-SUFFIX,example.com\n"
        metadata = {"size": len(body), "sha": hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()}
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "source"
            cache.write_bytes(b"corrupt")
            with patch("build.get_bytes", return_value=body[:10]), patch("build.github_api", return_value={
                "encoding": "base64", "content": base64.b64encode(body).decode()
            }) as api:
                self.assertEqual(verified_blob("a/b", "commit", "file", metadata, cache), body)
                api.assert_called_once()
                self.assertEqual(cache.read_bytes(), body)

    def test_integrity_failure_stops_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("build.get_bytes", return_value=b"bad"), patch("build.github_api", return_value={
                "encoding": "base64", "content": base64.b64encode(b"bad").decode()
            }):
                with self.assertRaises(ValueError):
                    verified_blob("a/b", "commit", "file", {"size": 3, "sha": "invalid"}, Path(directory) / "cache")

    def test_shared_auth_and_unsupported_matchers_are_excluded(self):
        accepted, excluded = parse_list(b"DOMAIN-SUFFIX,auth0.com\nURL-REGEX,test\nDOMAIN-SUFFIX,cursor.com\n", "ai")
        self.assertEqual(accepted, ["DOMAIN-SUFFIX,cursor.com"])
        self.assertEqual(len(excluded), 2)

    def test_ai_classification_preserves_blockers_and_deduplicates_later_general_rule(self):
        result, report = resolve([
            ("bm7_privacy", "隐私拦截", ["DOMAIN-SUFFIX,featuregates.org"]),
            ("acl_ai", "AI 服务", ["DOMAIN,api.featuregates.org", "DOMAIN-SUFFIX,cursor.com"]),
            ("bm7_global", "国外网站", ["DOMAIN-SUFFIX,cursor.com", "DOMAIN-SUFFIX,example.com"]),
        ])
        self.assertEqual(result[1][2], ["DOMAIN-SUFFIX,cursor.com"])
        self.assertEqual(result[2][2], ["DOMAIN-SUFFIX,example.com"])
        self.assertEqual(report["unique_rules"], 3)


if __name__ == "__main__":
    unittest.main()
