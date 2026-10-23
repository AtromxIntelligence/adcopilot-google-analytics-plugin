"""The manifest, the marketplace file and the connector file of
AdCopilot for Google Analytics (GA4).

The plugin directory reads `.claude-plugin/plugin.json` for the listing, and
people who add the repository in Claude Code read `.claude-plugin/marketplace.json`.
Both are held here to the exact values the listing was decided with, so a
change to a name, a URL or the connector file is a change someone made on
purpose and not a slip.

Run with `python3 -m unittest discover -s tests -v` from the repository root
(stdlib only; no environment variable is read; CI runs it in checks.yml).
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = ROOT / ".claude-plugin" / "marketplace.json"
MCP_JSON = ROOT / ".mcp.json"

REPO = "adcopilot-google-analytics-plugin"
NAME = "adcopilot-google-analytics"
DISPLAY_NAME = "AdCopilot for Google Analytics (GA4)"
OWNER = "Google"

# The one connector file every AdCopilot plugin carries. The same key and the
# same spelling of the address in every plugin, so that Claude sees one
# connector however many AdCopilot plugins are installed.
CANONICAL_MCP = {
    "mcpServers": {
        "adcopilot": {"type": "http", "url": "https://mcp.adcopilot.cloud/mcp"}
    }
}

NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
KEYWORD = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

EXPECTED_FIELDS = {
    "name", "version", "description", "author", "homepage",
    "documentationUrl", "privacyPolicyUrl", "termsOfServiceUrl", "supportUrl",
    "repository", "license", "keywords", "displayName", "icon",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def urls_in(value):
    """Every string in a JSON value that is shaped like an address."""
    if isinstance(value, str):
        if "://" in value:
            yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from urls_in(v)
    elif isinstance(value, list):
        for v in value:
            yield from urls_in(v)


class PluginManifest(unittest.TestCase):

    def setUp(self):
        self.plugin = load(PLUGIN_JSON)

    def test_the_field_set_is_exactly_the_decided_one(self):
        self.assertEqual(set(self.plugin), EXPECTED_FIELDS)

    def test_name_and_display_name_are_the_decided_strings(self):
        self.assertEqual(self.plugin["name"], NAME)
        self.assertRegex(self.plugin["name"], NAME_PATTERN)
        self.assertEqual(self.plugin["displayName"], DISPLAY_NAME)

    def test_author_and_urls(self):
        self.assertEqual(self.plugin["author"],
                         {"name": "Atromx Intelligence", "url": "https://adcopilot.cloud"})
        self.assertEqual(self.plugin["homepage"], "https://adcopilot.cloud")
        self.assertEqual(self.plugin["documentationUrl"], "https://adcopilot.cloud/docs/")
        self.assertEqual(self.plugin["privacyPolicyUrl"], "https://adcopilot.cloud/privacy")
        self.assertEqual(self.plugin["termsOfServiceUrl"], "https://adcopilot.cloud/terms")
        self.assertEqual(self.plugin["supportUrl"],
                         "https://github.com/AtromxIntelligence/%s/issues" % REPO)
        self.assertEqual(self.plugin["repository"],
                         "https://github.com/AtromxIntelligence/%s" % REPO)
        self.assertEqual(self.plugin["license"], "MIT")

    def test_version_is_semver(self):
        self.assertRegex(self.plugin["version"], SEMVER)

    def test_description_leads_with_the_words_people_search_and_ends_with_the_maker(self):
        description = self.plugin["description"]
        self.assertLessEqual(len(description), 600, len(description))
        self.assertTrue(description.startswith("Google Analytics, GA4"), description)
        self.assertTrue(
            description.endswith("Made by Atromx Intelligence, not by %s." % OWNER),
            description)

    def test_keywords_are_at_most_fifteen_and_kebab_case(self):
        keywords = self.plugin["keywords"]
        self.assertLessEqual(len(keywords), 15)
        self.assertEqual(len(set(keywords)), len(keywords), "a keyword is repeated")
        for keyword in keywords:
            self.assertRegex(keyword, KEYWORD)

    def test_the_icon_is_the_plugins_own_png(self):
        self.assertEqual(self.plugin["icon"], "./.claude-plugin/icon.png")
        icon = ROOT / ".claude-plugin" / "icon.png"
        self.assertTrue(icon.is_file())
        self.assertEqual(icon.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertFalse((ROOT / ".claude-plugin" / "icon.svg").exists())

    def test_every_address_is_https(self):
        for path in (PLUGIN_JSON, MARKETPLACE_JSON, MCP_JSON):
            for url in urls_in(load(path)):
                self.assertTrue(url.startswith("https://"), "%s: %s" % (path.name, url))


class MarketplaceFile(unittest.TestCase):

    def test_it_lists_this_plugin_from_the_repository_root_and_nothing_else(self):
        market = load(MARKETPLACE_JSON)
        self.assertEqual(set(market), {"name", "description", "owner", "plugins"})
        self.assertEqual(market["name"], REPO)
        self.assertEqual(market["owner"],
                         {"name": "Atromx Intelligence", "url": "https://adcopilot.cloud"})
        self.assertEqual(len(market["plugins"]), 1)
        entry = market["plugins"][0]
        self.assertEqual(entry["name"], NAME)
        self.assertEqual(entry["source"], "./")
        # The directory-listing fields do not belong in a marketplace entry:
        # `claude plugin validate` reports them there as unknown.
        self.assertEqual(set(entry), {"name", "source", "description", "category"})
        self.assertTrue(entry["description"].strip())


class ConnectorFile(unittest.TestCase):

    def test_mcp_json_is_the_one_connector_file_every_adcopilot_plugin_carries(self):
        self.assertEqual(load(MCP_JSON), CANONICAL_MCP)

    def test_no_package_launcher_and_no_header_is_declared(self):
        server = load(MCP_JSON)["mcpServers"]["adcopilot"]
        self.assertEqual(set(server), {"type", "url"})


if __name__ == "__main__":
    unittest.main()
