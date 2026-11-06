# AdCopilot for Google Analytics (GA4)

Google Analytics, GA4, conversions, attribution and reports from your AI client. AdCopilot reads your GA4 properties to report traffic and key events by channel, source and campaign, check that the right events count as conversions, explain your attribution settings and why Google Ads and Analytics disagree, and run funnel, retention and realtime reports. Any change to key events, attribution or data streams is proposed first and made only on your yes; nothing is ever deleted.

What it does today, through the AdCopilot connector:

- **Reports.** Sessions, engaged sessions, key events and revenue by channel, source and medium, campaign and landing page, this period against the last. Also cross-tabs, ordered funnels, weekly retention by first channel and a realtime check that an event is arriving now (`ga4_run_report`, `ga4_run_pivot_report`, `ga4_run_funnel_report`, `ga4_run_cohort_report`, `ga4_run_realtime_report`). Names are checked with `ga4_get_metadata`, never guessed, and every number is labelled as Analytics' own.
- **Key events.** Which events count as conversions, with a flag on an every-visit event such as page_view marked as one. It picks the action worth counting from the event counts, and proposes marking a key event or changing its counting method (`ga4_list_conversion_events`, `ga4_create_conversion_event`, `ga4_update_conversion_event`), then proves it with realtime.
- **Attribution.** The property's attribution model and lookback windows in plain words, why Google Ads and Analytics count different conversions for the same dates, and whether the two are linked (`ga4_get_attribution_settings`, `ga4_update_attribution_settings`, `ga4_list_google_ads_links`, `ga4_create_google_ads_link`, and `explain_conversion_gap`, which needs Google Ads connected).
- **Setup.** A new Analytics account, a property with the right time zone and currency, a web data stream and its measurement ID, custom dimensions, and the Google tag staged in Tag Manager for you to publish.

In short: Works today, in full, through the current AdCopilot connector: reading Analytics reports and settings and, on your yes, marking key events, changing the attribution model and lookback windows, linking Google Ads, and setting up an account, a property, a web data stream and custom dimensions (a new account's Google terms are yours to accept); staging the Google tag for you to publish when Tag Manager is connected; and explaining why Google Ads and Analytics count different conversions when Google Ads is connected. Not possible through AdCopilot: deleting or archiving anything in Analytics or Tag Manager, publishing in Tag Manager, and Analytics audiences, filters, saved explorations, BigQuery links and data retention settings. Nothing here waits for a later connector.

Made by Atromx Intelligence (https://adcopilot.cloud). Not affiliated with or endorsed by Google. Google, Google Analytics, Google Ads and Google Tag Manager are trademarks of Google LLC. AdCopilot is not related to other products named AdCopilot.

The plugin is MIT licensed. The AdCopilot connector it brings is a hosted service, so you need an AdCopilot account to use it.

## Install

Two steps on every surface: add the plugin, then sign in to the connector it brings with it. The second step is the one people miss, and nothing works until it is done. This plugin is written for Claude.

### claude.ai, Cowork and the desktop app

1. Go to **Customize**, then **Plugins**, search for AdCopilot for Google Analytics, and click **Add**.
2. Open the plugin's **Connectors** tab, click **Connect** beside `adcopilot`, and sign in.

The plugin registers the connector for you, so there is no need for "Add custom connector" or the connector address. Claude links a connector by its address, so if you added AdCopilot by hand earlier, it is the same connector.

### Claude Code

```
/plugin marketplace add AtromxIntelligence/adcopilot-google-analytics-plugin
/plugin install adcopilot-google-analytics@adcopilot-google-analytics-plugin
/mcp
```

The last step opens the connector list. Choose `adcopilot` and sign in. There is nothing to add by hand: the plugin registers the connector at `https://mcp.adcopilot.cloud/mcp`. If you added AdCopilot's connector by hand before, the steps to remove that copy are at https://adcopilot.cloud/docs/connect/claude-code-plugin#already-added-the-connector-by-hand.

### Then, once

Connect your Google products in AdCopilot at https://app.adcopilot.cloud, not in your AI client. The `setup` command tells you which are missing and what each would unlock.

### Already use another AdCopilot plugin?

There is one connector and one AdCopilot account, whichever AdCopilot plugins you add. Every AdCopilot plugin points at the same address, so your AI client treats them as one connector. In Claude Code, `/mcp` shows the connector once, under whichever AdCopilot plugin loaded first, and the sign-in belongs to that entry. Every skill here names tools by their plain names, so it works whichever plugin hosts the connection. If Claude asks you to sign in again after you add or remove an AdCopilot plugin, run `/mcp` and sign in once.

## What you get

Three commands (in Claude Code they read `/adcopilot-google-analytics:setup`, `:report` and `:key-events`):

- `setup` checks the connector is connected and signed in and says what is connected.
- `report` answers a question about your traffic and results, or gives the last 28 days against the 28 before.
- `key-events` checks which events count as conversions.

Four skills, which Claude also picks up from what you ask:

- `ga4-reports` uses `get_org_context`, `ga4_list_account_summaries`, `ga4_get_metadata`, `ga4_run_report`, `ga4_run_pivot_report`, `ga4_run_funnel_report`, `ga4_run_cohort_report` and `ga4_run_realtime_report`.
- `ga4-key-events` uses `get_org_context`, `ga4_list_account_summaries`, `ga4_list_conversion_events`, `ga4_run_report`, `ga4_run_realtime_report`, `ga4_create_conversion_event`, `ga4_update_conversion_event`, `gtm_list_containers`, `gtm_list_workspaces` and `gtm_list_tags`.
- `ga4-attribution` uses `get_org_context`, `ga4_list_account_summaries`, `ga4_get_attribution_settings`, `ga4_update_attribution_settings`, `ga4_list_google_ads_links`, `ga4_create_google_ads_link`, `list_accessible_customers` and `explain_conversion_gap`.
- `ga4-setup` uses `get_org_context`, `ga4_list_account_summaries`, `ga4_list_properties`, `ga4_list_data_streams`, `ga4_provision_account`, `ga4_create_property`, `ga4_update_property`, `ga4_create_data_stream`, `ga4_list_custom_dimensions`, `ga4_create_custom_dimension`, `gtm_list_containers`, `gtm_list_workspaces`, `gtm_list_tags`, `gtm_create_tag` and `ga4_run_realtime_report`.

## What it will not do

- Change anything without your explicit yes in the conversation. Every change is proposed first, with what it changes and how to undo it.
- Publish Tag Manager. A tag is staged in a workspace called AdCopilot, and publishing is your click in Tag Manager.
- Delete or archive anything. The connector has no tool that does either in Analytics or Tag Manager, and the skills never ask for one.
- Invent a number. Every figure is the one Analytics returned, and where Analytics and Google Ads disagree it says so.
- Do what the connector has no tool for: audiences, filters, saved explorations, BigQuery links and data retention settings.

## Data

The plugin is instructions only: it runs no code and sends nothing anywhere itself. The AdCopilot connector at mcp.adcopilot.cloud reads and, on your yes, writes your Google products through Google's APIs with your Google sign-in. It is the only destination: https://mcp.adcopilot.cloud/mcp. Read the privacy policy at https://adcopilot.cloud/privacy and the terms at https://adcopilot.cloud/terms. Documentation is at https://adcopilot.cloud/docs/.

## Example prompts

After you sign in, ask in your own words. For example:

- "How did my website traffic and key events do by channel over the last 28 days, against the 28 days before?"
- "Which events count as conversions in my GA4 property, and is the right one marked?"
- "Why do Google Ads and Google Analytics report different conversions for last month?"
- "Set up a GA4 property and a web data stream for my site, and show me what you will change before you change it."

## Support

Open an issue at https://github.com/AtromxIntelligence/adcopilot-google-analytics-plugin/issues, or write to support@adcopilot.cloud.

## Version

**0.1.1 (2026-11-05)**

Changes nothing you use. The plugin folder now holds only the files Claude loads.

**0.1.0 (2026-10-23, written against AdCopilot v2.44.0, live since 2026-10-22)**

First release. Reports, key events, attribution and setup for GA4 properties through the current AdCopilot connector, with every change proposed first and applied only on an explicit yes.

## Licence

MIT. Copyright (c) 2026 Atromx Intelligence Private Limited. See LICENSE.
