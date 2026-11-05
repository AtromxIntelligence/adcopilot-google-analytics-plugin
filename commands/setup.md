---
name: setup
description: Check the AdCopilot connector is connected and signed in, say what it can do with Google Analytics today, and find the next step.
---

Call `get_org_context` with `source: "claude-plugin/adcopilot-google-analytics/0.1.1"`
first, before any other tool, and send `source` exactly as written, the version
included. If this is a scheduled run, send `source: "claude-scheduled"` instead
and change nothing: this plugin schedules nothing. `get_org_context`'s
`next_step` and `playbook` describe the whole workspace, not this request: do
this request, keep any limit `next_step` adds, and offer the rest afterwards.

Your first answer says this once, in your own plain words, keeping what it says
AdCopilot can and cannot do:

> Works today, in full, through the current AdCopilot connector: reading Analytics reports and settings and, on your yes, marking key events, changing the attribution model and lookback windows, linking Google Ads, and setting up an account, a property, a web data stream and custom dimensions (a new account's Google terms are yours to accept); staging the Google tag for you to publish when Tag Manager is connected; and explaining why Google Ads and Analytics count different conversions when Google Ads is connected. Not possible through AdCopilot: deleting or archiving anything in Analytics or Tag Manager, publishing in Tag Manager, and Analytics audiences, filters, saved explorations, BigQuery links and data retention settings. Nothing here waits for a later connector.

**Work out the surface first.** If you can run `claude mcp list`, this is Claude
Code. If you cannot (claude.ai, Cowork, the desktop app), there is no `/mcp`,
no `claude mcp list` and no `claude mcp remove`, and none of the Claude Code
paragraphs below applies.

**Where the connector is signed in.**

- Claude Code: `/mcp`, choose `adcopilot`, sign in; where Google shows its
  account chooser, pick the Google account that owns the Analytics property. The
  plugin registers the connector at `https://mcp.adcopilot.cloud/mcp` for you;
  there is no `claude mcp add` step.
- claude.ai, Cowork and the desktop app: open the plugin from the plugin list,
  then its **Connectors** tab, and Connect `adcopilot`. Claude links a connector
  by its URL, so a copy added by hand earlier is the same connector, not a
  second one. Never offer "Add custom connector" or the connector URL to someone
  who has this plugin installed in Claude: the plugin already brings it.

**One connector and one AdCopilot account, whichever AdCopilot plugins are
added.** Every AdCopilot plugin declares the same connector. In Claude Code,
`/mcp` lists it once, under whichever AdCopilot plugin loaded first, and the
sign-in belongs to that entry. The entry is named
`plugin:<that plugin's name>:adcopilot`; a plugin that loaded later has its copy
set aside, and this plugin's skills still work, because they name tools by their
plain names. If Claude asks for a sign-in again after an AdCopilot plugin was
added or removed, run `/mcp` and sign in once.

**A hand-added copy, Claude Code only.** In `claude mcp list`, a bare `adcopilot`
line and no `plugin:<name>:adcopilot` line means a copy added by hand is the one
connection in use. It reads the same Analytics, so leave it, and never add the
connector by hand for someone who has the plugin.

If the connector answers but reports nothing connected, that is the server
working, not a fault: the Google products are connected inside AdCopilot, at
the connect link in its answer (the general address is
https://app.adcopilot.cloud), not in this client. Say so and send them there.

Then say what is connected and what connecting each missing product unlocks, in
the server's own words, one product to a line and never as a table. End with one
next step and why it fits: the `ga4-setup` skill if Analytics has no property
yet or the Google tag is not on the site; the `ga4-reports` skill (the report
command) if it is receiving data; the `ga4-key-events` skill (the key-events
command) if a conversion number looks wrong.

Every change is proposed first and applied only on an explicit yes in this conversation.
