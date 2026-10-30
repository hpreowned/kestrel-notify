# Graph Report - kestrel-notify  (2026-10-30)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 317 nodes · 743 edges · 17 communities (14 shown, 3 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `86df9daf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 15

## God Nodes (most connected - your core abstractions)
1. `ChannelName` - 31 edges
2. `Outbox` - 29 edges
3. `NotificationService` - 25 edges
4. `Message` - 23 edges
5. `Settings` - 22 edges
6. `create_app()` - 18 edges
7. `ChannelSender` - 17 edges
8. `DeliveryError` - 16 edges
9. `WebhookChannel` - 16 edges
10. `Job` - 16 edges

## Surprising Connections (you probably didn't know these)
- `msg()` --uses--> `ChannelName`  [INFERRED]
  tests/test_channel_webhook.py → notify/models.py
- `test_booking_event_carrier_codes()` --uses--> `ChannelName`  [INFERRED]
  tests/test_models.py → notify/models.py
- `test_request_accepts_all_channels_and_events()` --uses--> `ChannelName`  [INFERRED]
  tests/test_models.py → notify/models.py
- `service()` --uses--> `NotificationService`  [INFERRED]
  tests/conftest.py → notify/service.py
- `test_all_carriers_named()` --uses--> `CarrierCode`  [INFERRED]
  tests/test_templates.py → notify/models.py

## Import Cycles
- None detected.

## Communities (17 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (16): ChannelSender, DeliveryError, Outbox, OutboxEntry, EmailChannel, build_senders(), SmsChannel, WebhookChannel (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (15): build_router(), booking_webhook(), create_notification(), get_notification(), BookingEvent, new_notification_id(), Notification, NotificationRequest (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (20): create_app(), _bad_signature(), _channel_disabled(), _rate_limited(), _error(), Settings, client(), env() (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (17): Job, JobQueue, JobState, NotificationService, Boom, make_queue(), Permanent, test_backoff_grows_and_jitter_scales() (+9 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (9): Status, RateLimitExceededError, RecipientRateLimiter, TokenBucket, Clock, test_allows_up_to_capacity_then_blocks(), test_buckets_are_per_recipient_and_case_insensitive(), test_refills_over_time() (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (28): if, permissions, uses, if, uses, if, uses, jobs (+20 more)

### Community 6 - "Community 6"
Cohesion: 0.22
Nodes (14): make_request(), test_bad_email_dead_letters_without_retry(), test_create_then_get_marks_sent(), test_invalid_body_is_422(), test_rate_limit_returns_429(), test_sms_disabled_by_flag(), test_webhook_channel_recovers(), test_webhook_channel_retries_then_dead_letters() (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.20
Nodes (8): InvalidSignatureError, sign(), verify(), test_sign_has_prefix_and_is_stable(), test_verify_accepts_valid(), test_verify_rejects_bad_headers(), test_verify_rejects_tampered_body(), test_verify_rejects_wrong_secret()

### Community 8 - "Community 8"
Cohesion: 0.24
Nodes (8): CarrierCode, Event, render(), Rendered, test_all_carriers_named(), test_carrier_name_is_rendered(), test_every_event_has_a_template(), test_missing_carrier_falls_back()

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (4): Contact, fan_out(), FanoutResult, _send_one()

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (5): description, excluded_tools, prompt, single_project, tool_description_overrides

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): uvx, serena, start-mcp-server

### Community 12 - "Community 12"
Cohesion: 0.50
Nodes (3): github>kestrel-freight/adlc-kit//monitor/renovate-preset.json#v0.1.0, extends, $schema

### Community 13 - "Community 13"
Cohesion: 0.50
Nodes (3): encoding, language_servers, project_name

## Knowledge Gaps
- **4 isolated node(s):** `uvx`, `start-mcp-server`, `github>kestrel-freight/adlc-kit//monitor/renovate-preset.json#v0.1.0`, `kestrel-notify`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 114 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `NotificationService` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 4`, `Community 6`, `Community 8`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `ChannelName` (e.g. with `ChannelSender` and `Outbox`) actually correct?**
  _`ChannelName` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `uvx`, `start-mcp-server`, `github>kestrel-freight/adlc-kit//monitor/renovate-preset.json#v0.1.0` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.12755102040816327 - nodes in this community are weakly interconnected._
- **Why does `Settings` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Outbox` (e.g. with `ChannelName` and `Message`) actually correct?**
  _`Outbox` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.09041835357624832 - nodes in this community are weakly interconnected._