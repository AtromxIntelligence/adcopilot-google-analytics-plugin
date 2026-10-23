---
name: ga4-attribution
description: Explain a Google Analytics (GA4) property's attribution settings in plain words, say why Google Ads and Analytics report different conversion counts for the same dates, check whether the property is linked to Google Ads, and propose a model or lookback window change, or the link, each applied only on a yes. Use when the user asks about attribution, the attribution model, lookback windows, data-driven or last click, why Google Ads and Analytics show different conversions, or whether Analytics is linked to Google Ads.
---

# Analytics attribution

Attribution is the rule that decides which visit gets the credit for a result. The customer is asking either what Analytics' rule is, why Analytics and Google Ads disagree about the same results, or whether the two are joined at all. You answer through the AdCopilot connector at `https://mcp.adcopilot.cloud/mcp`. The settings are Analytics' own; the Google Ads side of the comparison needs Google Ads connected, and AdCopilot reads no other ad platform for this. Every figure you give is one a tool returned, never an estimate of your own; and say what you cannot see, which includes whatever Google Ads' own screens hold beyond what the tools read, and visits Analytics never received.

## Before the first call

Call `get_org_context` with `source: "claude-plugin/adcopilot-google-analytics/0.1.0"` first, before any other tool, and send `source` exactly as written, the version included: it tells AdCopilot that this plugin is installed here. If this is a scheduled run (a Claude scheduled task or a Claude Code routine, with nobody there to answer), send `source: "claude-scheduled"` instead and change nothing: this plugin schedules nothing.

`get_org_context`'s `next_step` and `playbook` describe the whole workspace, not this request. Do this request, keep any limit `next_step` adds, and offer the rest afterwards.

If Google Analytics is not connected, say what connecting it unlocks, in the server's own `unlocks` words and with the connect link its answer carries, never an address from memory, and stop: invent nothing about a property you cannot read. Analytics is connected inside AdCopilot, not in this client. Reading the settings needs only Analytics; the gap between Google Ads and Analytics also needs Google Ads, and if it is not connected, say what connecting it unlocks, once, and answer the rest.

Your first answer says this once, in your own plain words, keeping what it says AdCopilot can and cannot do (it holds when you stop at "not connected" too):

> Works today, in full, through the current connector: GA4's 14 reads and 13 non-destructive writes, plus Tag Manager staging and explain_conversion_gap when Google Ads is connected. Not possible through AdCopilot, and said so: deleting or archiving anything, audiences, filters, saved explorations, BigQuery links and data retention settings. Nothing waits for a later connector.

## 1. Read the settings

Take the property from the server's answer, by the name Analytics shows for it; if there are several, ask which (`ga4_list_account_summaries` lists what this login reaches). Call `ga4_get_attribution_settings`. Its answer holds Google's own reply and a `plain` summary of four things; say them in words, never as field names:

- **The reporting attribution model.** The tool can read and set three: data-driven across paid and organic channels, last click across paid and organic channels, and last click across Google paid channels only. Google retired first click, linear, time decay and position-based in November 2023 (checked 23 October 2026). A model changes reports and explorations that use event-scoped traffic dimensions, such as source, medium, campaign and default channel group; user- and session-scoped dimensions do not change.
- **The lookback window for first-visit and first-open key events.** 30 days by default, or 7.
- **The lookback window for every other key event.** 90 days by default, or 30 or 60.
- **Which channels may earn credit for web conversions shared with Google Ads.** This one is read only: AdCopilot can say what it is and cannot change it.

What breaks: judge a channel by a window shorter than the time people take to decide and it looks like it never converts. What it unlocks: the customer knows which rule produced the numbers they are looking at.

## 2. Why Google Ads and Analytics disagree

Analytics and Google Ads count differently, so the two numbers will not match, and both are right for what they count. Say it once, in one sentence, before showing both. Never present an Analytics number as a Google Ads result, or the other way round.

When the customer asks why they differ, call `explain_conversion_gap`. It is read only. It needs the Google Ads account: take `customer_id` from `get_org_context`, which returns the connected accounts, and call `list_accessible_customers` only if that names none. Pass `ga4_property` for the property you chose; add `ga4_event` or `conversion_action_id` to compare one result, and `start_date` and `end_date` (YYYY-MM-DD) for the dates in question. Lead with its largest measured cause and its numbers, then the rest in order, then the part it calls unexplained, as unexplained. Never name a cause it did not measure.

## 3. Is Analytics linked to Google Ads

Call `ga4_list_google_ads_links` and look for the Google Ads account by the name Google Ads shows for it, never by its number. The link is what lets Analytics key events be imported into Google Ads as conversions and lets paid visits join the organic ones in Analytics reports; Google Ads' own screens are where the import is done, not a tool here, and Google's own help is the referee on its steps.

- **Linked:** say so and stop; a second link is not needed.
- **Not linked:** propose `ga4_create_google_ads_link` for the property and that account. Leave `ads_personalization_enabled` off unless the customer asks for it: it shares Analytics audiences and remarketing events with Google Ads, which is a separate decision (Google's own link screen has it switched on by default, checked 23 October 2026, so say that this one will not). There is no unlink tool, so say that before they agree: removing a link is their click in Analytics (at the time of writing: Admin, then Product links, then Google Ads links; checked 23 October 2026), and an unlinked account stops importing key events. Google asks for Editor or above on the property and administrator access on the Google Ads account; if it refuses, report its error in plain words and stop.

Read the links back after the call and report what you read.

## 4. Change a model or a window

Only when the customer asks; never because another setting looks nicer. Propose it first: the setting now, the setting after, and what it touches. A model change applies to past and future Analytics reports; a window change applies from the day it is made, and past days keep the window they had. Name the arguments that put the old values back (the tool's answer carries them, and you read them out again). On an explicit yes, call `ga4_update_attribution_settings` with only what changes: `reporting_attribution_model` (`PAID_AND_ORGANIC_CHANNELS_DATA_DRIVEN`, `PAID_AND_ORGANIC_CHANNELS_LAST_CLICK` or `GOOGLE_PAID_CHANNELS_LAST_CLICK`), `acquisition_lookback_days` (7 or 30) or `other_lookback_days` (30, 60 or 90). Then call `ga4_get_attribution_settings` again and report what you read. Which channels may earn credit for conversions shared with Google Ads is not changed here.

## Changes: proposed first, applied only on a yes

Every change is proposed first and applied only on an explicit yes in this conversation. A proposal says, in plain words, what will change, what it will look like afterwards and how to undo it: the arguments that put the old value back, or the click in Google's own screen. Propose one change at a time, call the tool only after the yes, then read the result back and report what you read, not what you intended. A yes to one change is not a yes to the next. Nothing is ever deleted: the connector has no tool that deletes or archives anything in Analytics or Tag Manager, and you never ask for one. Tag Manager changes are staged in the "AdCopilot" workspace and never published: publishing is the customer's click in Tag Manager (Submit, then Publish, at the time of writing, checked 23 October 2026).

## Prices

This file names no prices. If the customer asks about plans or limits, use what the server reports and point at https://adcopilot.cloud/pricing.
