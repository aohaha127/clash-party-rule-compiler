import unittest

from build import base_groups
from clients import portable_rules, stash_groups, loon_groups


class ClientTests(unittest.TestCase):
    def test_process_rules_are_omitted_but_ip_options_are_preserved(self):
        payload, omitted = portable_rules(["PROCESS-NAME,ToDesk.exe", "IP-CIDR,10.0.0.0/8,no-resolve"])
        self.assertEqual(payload, ["IP-CIDR,10.0.0.0/8,no-resolve"])
        self.assertEqual(omitted["PROCESS-NAME"], 1)

    def test_new_rule_types_fail_instead_of_silent_loss(self):
        with self.assertRaises(ValueError):
            portable_rules(["UNREVIEWED,value"])

    def test_stash_non_hk_uses_only_known_non_hk_groups(self):
        groups = stash_groups(base_groups())
        non_hk = next(group for group in groups if group["name"] == "非港节点")
        self.assertNotIn("香港节点", non_hk["proxies"])
        self.assertNotIn("DIRECT", non_hk["proxies"])
        self.assertIn("REJECT", non_hk["proxies"])
        self.assertNotIn("include-all", non_hk)
        for group in groups:
            if group.get("include-all"):
                self.assertIn("REJECT", group["proxies"])

    def test_loon_non_hk_filter_excludes_hong_kong(self):
        import re
        filters, _ = loon_groups(base_groups())
        line = next(line for line in filters if line.startswith("筛选-非港节点 ="))
        pattern = re.compile(line.split("FilterKey = ", 1)[1])
        for name in ["HK 01", "香港 02", "Hong Kong 03", "俄罗斯 01", "RU 01", "Russia 01",
                     "莫斯科", "🇷🇺 01", "Россия 02", "Moscow 03"]:
            self.assertIsNone(pattern.search(name))
        self.assertIsNotNone(pattern.search("台湾 01"))
        self.assertIsNotNone(pattern.search("Peru 01"))

    def test_mihomo_filter_excludes_russia_without_matching_peru(self):
        import re
        group = next(group for group in base_groups() if group["name"] == "非港节点")
        pattern = re.compile(group["exclude-filter"])
        for name in ["俄罗斯", "俄羅斯", "RU-01", "🇷🇺", "Russia", "Москва"]:
            self.assertIsNotNone(pattern.search(name))
        self.assertIsNone(pattern.search("Peru 01"))


if __name__ == "__main__":
    unittest.main()
