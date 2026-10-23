"""The skills, the commands and the README of AdCopilot for Google Analytics (GA4).

What each check exists for:

- A skill or command whose front matter does not parse, or whose `description`
  is not one line of text, stops being found, and the directory blocks it.
- A tool name that the connector does not serve sends a customer's request
  into an error. Every tool named in a skill is checked against
  `tests/connector_tools.txt` (the connector's tool list), and each skill is
  held to the tools it was written for.
- Tools are named by their plain names, never by a full namespaced tool name,
  because that namespace belongs to whichever AdCopilot plugin Claude loaded
  first.
- The `source` sent to `get_org_context` carries this plugin's name and
  version, so the server knows the plugin is here and never hands the turn to
  skills that are not installed.
- Every skill holds the approval rule, and every skill and the setup command
  say plainly what works today and what does not.

Run with `python3 -m unittest discover -s tests -v` from the repository root
(stdlib only; no environment variable is read; CI runs it in checks.yml).
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
VERSION = PLUGIN["version"]
SOURCE = "claude-plugin/%s/%s" % (PLUGIN["name"], VERSION)

# What each skill was written to use: the tools, by plain name.
SKILL_TOOLS = {
    "ga4-reports": {
        "get_org_context", "ga4_list_account_summaries", "ga4_get_metadata",
        "ga4_run_report", "ga4_run_pivot_report", "ga4_run_funnel_report",
        "ga4_run_cohort_report", "ga4_run_realtime_report",
    },
    "ga4-key-events": {
        "get_org_context", "ga4_list_account_summaries", "ga4_list_conversion_events",
        "ga4_run_report", "ga4_run_realtime_report", "ga4_create_conversion_event",
        "ga4_update_conversion_event", "gtm_list_containers", "gtm_list_workspaces",
        "gtm_list_tags",
    },
    "ga4-attribution": {
        "get_org_context", "ga4_list_account_summaries", "ga4_get_attribution_settings",
        "ga4_update_attribution_settings", "ga4_list_google_ads_links",
        "ga4_create_google_ads_link", "list_accessible_customers",
        "explain_conversion_gap",
    },
    "ga4-setup": {
        "get_org_context", "ga4_list_account_summaries", "ga4_list_properties",
        "ga4_list_data_streams", "ga4_provision_account", "ga4_create_property",
        "ga4_update_property", "ga4_create_data_stream", "ga4_list_custom_dimensions",
        "ga4_create_custom_dimension", "gtm_list_containers", "gtm_list_workspaces",
        "gtm_list_tags", "gtm_create_tag", "ga4_run_realtime_report",
    },
}
COMMANDS = {"setup", "report", "key-events"}
COMMAND_SKILL = {"report": "ga4-reports", "key-events": "ga4-key-events"}
COMMAND_TOOLS = {"setup": {"get_org_context"}, "report": set(), "key-events": set()}

# Arguments of a tool that read like tool names. They are not tools.
ARGUMENT_NAMES = {"ga4_property", "ga4_event", "update_mask"}

PRODUCT_PREFIXES = ("gsc_", "ga4_", "gtm_")
VERB_PREFIXES = {
    "create", "update", "set", "add", "remove", "list", "get", "run", "analyze",
    "link", "attach", "pause", "explain", "provision", "enable",
}
BACKTICKED = re.compile(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`")
PRODUCT_TOKEN = re.compile(r"\b((?:gsc|ga4|gtm)_[a-z0-9_]+)\b")

# Said once, in the first answer of every skill and of the setup command.
TODAY_LATER = (
    "Works today, in full, through the current AdCopilot connector: reading "
    "Analytics reports and settings and, on your yes, marking key events, changing "
    "the attribution model and lookback windows, linking Google Ads, and setting up "
    "an account, a property, a web data stream and custom dimensions (a new "
    "account's Google terms are yours to accept); staging the Google tag for you to "
    "publish when Tag Manager is connected; and explaining why Google Ads and "
    "Analytics count different conversions when Google Ads is connected. Not "
    "possible through AdCopilot: deleting or archiving anything in Analytics or Tag "
    "Manager, publishing in Tag Manager, and Analytics audiences, filters, saved "
    "explorations, BigQuery links and data retention settings. Nothing here waits "
    "for a later connector."
)
# The approval rule, in every skill and in the setup command.
APPROVAL = ("Every change is proposed first and applied only on an explicit yes "
            "in this conversation.")

README = (ROOT / "README.md").read_text(encoding="utf-8")


def connector_tools():
    names = set()
    for line in (ROOT / "tests" / "connector_tools.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.add(line)
    return names


def looks_like_tool(token):
    return token.startswith(PRODUCT_PREFIXES) or token.split("_")[0] in VERB_PREFIXES


def tools_named(text):
    """Every tool-like name in `text` (backticked, or a product-prefixed name
    written bare), without the one sentence that says what works today: it
    names a tool in plain prose, and is checked on its own."""
    text = text.replace(TODAY_LATER, "")
    found = {t for t in BACKTICKED.findall(text) if looks_like_tool(t)}
    found |= set(PRODUCT_TOKEN.findall(text))
    return found - ARGUMENT_NAMES


def split_front_matter(text):
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError("no front matter")
    return match.group(1), text[match.end():]


def parse_front_matter(block):
    """The `key: value` lines of a front-matter block, each value one line of
    text. A list item, an indented line or a value that real YAML would read as
    something other than a plain string raises."""
    fields = {}
    for line in block.split("\n"):
        if not line.strip():
            continue
        if line[0] in " \t-":
            raise ValueError("a list or a continued line: %r" % line)
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):[ ]?(.*)$", line)
        if not match:
            raise ValueError("not a key: value line: %r" % line)
        key, value = match.group(1), match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            if ": " in value or " #" in value or value[:1] in "[{&*!|>%@`":
                raise ValueError("an unquoted value YAML would not read as text: %r" % line)
        fields[key] = value
    return fields


def skill_files():
    return sorted((ROOT / "skills").glob("*/SKILL.md"))


def command_files():
    return sorted((ROOT / "commands").glob("*.md"))


class Components(unittest.TestCase):

    def test_the_plugin_has_exactly_these_skills_and_commands(self):
        self.assertEqual({p.parent.name for p in skill_files()}, set(SKILL_TOOLS))
        self.assertEqual({p.stem for p in command_files()}, COMMANDS)
        for folder in (ROOT / "skills").iterdir():
            self.assertEqual([p.name for p in folder.iterdir()], ["SKILL.md"], folder)

    def test_every_skill_and_command_has_front_matter_that_parses(self):
        for path in skill_files() + command_files():
            text = path.read_text(encoding="utf-8")
            block, _ = split_front_matter(text)
            fields = parse_front_matter(block)
            expected = path.parent.name if path.name == "SKILL.md" else path.stem
            self.assertEqual(fields.get("name"), expected, path)
            description = fields.get("description")
            self.assertIsInstance(description, str, path)
            self.assertTrue(description.strip(), path)
            self.assertLessEqual(len(description), 1024, path)

    def test_a_skills_description_says_when_to_use_it(self):
        for path in skill_files():
            fields = parse_front_matter(split_front_matter(path.read_text(encoding="utf-8"))[0])
            self.assertIn("Use when", fields["description"], path)

    def test_a_command_hands_over_to_its_skill(self):
        for name, skill in COMMAND_SKILL.items():
            body = (ROOT / "commands" / (name + ".md")).read_text(encoding="utf-8")
            self.assertIn("Follow the `%s` skill." % skill, body, name)

    def test_the_report_command_takes_the_question_as_its_argument(self):
        body = (ROOT / "commands" / "report.md").read_text(encoding="utf-8")
        self.assertIn("$ARGUMENTS", body)

    def test_every_tool_named_is_one_the_connector_serves(self):
        served = connector_tools()
        self.assertIn("ga4_run_report", served)
        for path in skill_files() + command_files() + [ROOT / "README.md"]:
            for tool in tools_named(path.read_text(encoding="utf-8")):
                self.assertIn(tool, served, "%s names %s, which the connector does not serve"
                              % (path.relative_to(ROOT), tool))

    def test_every_skill_names_the_tools_it_was_written_for_and_no_others(self):
        for skill, expected in SKILL_TOOLS.items():
            text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            named = tools_named(text)
            self.assertEqual(named - expected, set(), "%s names a tool outside its set" % skill)
            self.assertEqual(expected - named, set(), "%s never names a tool of its set" % skill)
        for command, expected in COMMAND_TOOLS.items():
            text = (ROOT / "commands" / (command + ".md")).read_text(encoding="utf-8")
            self.assertEqual(tools_named(text), expected, command)

    def test_the_first_tool_in_every_skill_and_in_setup_is_get_org_context(self):
        for path in skill_files() + [ROOT / "commands" / "setup.md"]:
            _, body = split_front_matter(path.read_text(encoding="utf-8"))
            body = body.replace(TODAY_LATER, "")
            first = [t for t in BACKTICKED.findall(body) if looks_like_tool(t)]
            self.assertTrue(first, path)
            self.assertEqual(first[0], "get_org_context", path)

    def test_no_full_namespaced_tool_name_appears_anywhere(self):
        needle = "mcp_" + "_plugin_"
        needle2 = "mcp_" + "_"
        for path in [ROOT / "README.md"] + skill_files() + command_files():
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(needle, text, path)
            self.assertNotIn(needle2, text, path)

    def test_every_get_org_context_source_carries_this_plugins_name_and_version(self):
        for path in skill_files() + [ROOT / "commands" / "setup.md"]:
            text = path.read_text(encoding="utf-8")
            sources = re.findall(r'source:\s*"([^"]+)"', text)
            plugin_sources = [s for s in sources if s.startswith("claude-plugin")]
            self.assertTrue(plugin_sources, "%s sends no plugin source" % path)
            for source in plugin_sources:
                self.assertEqual(source, SOURCE, path)
            # Neither the bare marker nor a version with no plugin name.
            for match in re.finditer(r"claude-plugin[^\s\"'`)]*", text):
                self.assertEqual(match.group(0), SOURCE, "%s: %s" % (path, match.group(0)))
            # A scheduled run is told apart and changes nothing.
            self.assertIn('source: "claude-scheduled"', text, path)

    def test_every_skill_holds_the_approval_rule(self):
        for path in skill_files() + [ROOT / "commands" / "setup.md"]:
            self.assertIn(APPROVAL, path.read_text(encoding="utf-8"), path)
        for path in skill_files():
            text = path.read_text(encoding="utf-8")
            self.assertIn("never published", text, path)
            self.assertIn("Nothing is ever deleted", text, path)

    def test_every_skill_and_the_setup_command_say_what_works_today(self):
        for path in skill_files() + [ROOT / "commands" / "setup.md"]:
            self.assertIn(TODAY_LATER, path.read_text(encoding="utf-8"), path)

    def test_every_skill_defers_to_the_servers_next_step_and_connect_link(self):
        for path in skill_files():
            text = path.read_text(encoding="utf-8")
            self.assertIn("`next_step` and `playbook` describe the whole workspace", text, path)
            self.assertIn("never an address from memory", text, path)

    def test_no_skill_or_command_names_a_price_or_records_anything_in_the_workspace(self):
        for path in skill_files() + command_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\$\d", text), path)
            self.assertIsNone(re.search("/m" + "o\\b", text), path)
            self.assertNotIn("save_org_context", text, path)


class Readme(unittest.TestCase):

    def words_outside_code(self):
        outside = re.sub(r"```.*?```", "", README, flags=re.S)
        return [w for w in outside.split() if re.search(r"[A-Za-z0-9]", w)]

    def test_it_has_well_over_the_directorys_forty_words_and_stays_readable(self):
        count = len(self.words_outside_code())
        self.assertGreaterEqual(count, 600)
        self.assertLessEqual(count, 1300)

    def test_it_opens_with_the_display_name(self):
        self.assertTrue(README.startswith("# %s\n" % PLUGIN["displayName"]))

    def test_it_holds_the_trademark_line_and_the_plans_line(self):
        self.assertIn("Made by Atromx Intelligence (https://adcopilot.cloud). "
                      "Not affiliated with or endorsed by Google.", README)
        self.assertIn("Google, Google Analytics, Google Ads and Google Tag Manager are "
                      "trademarks of Google LLC.", README)
        self.assertIn("not related to other products named AdCopilot", README)
        self.assertIn("Free plan available; paid plans on https://adcopilot.cloud/pricing", README)

    def test_it_has_the_sections_the_directory_and_the_ship_script_read(self):
        for heading in ("## Install", "### claude.ai, Cowork and the desktop app",
                        "### Claude Code", "## What you get", "## What it will not do",
                        "## Data", "## Support", "## Version", "## Licence",
                        "## What CI runs"):
            self.assertIn("\n" + heading + "\n", README, heading)

    def test_it_says_one_connector_one_account_and_what_to_do_after_an_add_or_removal(self):
        text = " ".join(README.split())
        self.assertIn("There is one connector and one AdCopilot account, whichever "
                      "AdCopilot plugins you add.", text)
        self.assertIn("under whichever AdCopilot plugin loaded first, and the sign-in "
                      "belongs to that entry.", text)
        self.assertIn("If Claude asks you to sign in again after you add or remove an "
                      "AdCopilot plugin, run `/mcp` and sign in once.", text)

    def test_it_discloses_where_the_data_goes_and_links_the_policies(self):
        for needle in ("runs no code and sends nothing anywhere itself",
                       "https://mcp.adcopilot.cloud", "https://adcopilot.cloud/privacy",
                       "https://adcopilot.cloud/terms", "support@adcopilot.cloud",
                       "https://github.com/AtromxIntelligence/adcopilot-google-analytics-plugin/issues"):
            self.assertIn(needle, README, needle)

    def test_its_version_paragraph_matches_the_manifest(self):
        paragraph = ("**%s (2026-10-23, written against AdCopilot v2.44.0, live since "
                     "2026-10-22)**" % VERSION)
        self.assertIn(paragraph, README)

    def test_it_says_what_works_today(self):
        self.assertIn(TODAY_LATER, README)


if __name__ == "__main__":
    unittest.main()
