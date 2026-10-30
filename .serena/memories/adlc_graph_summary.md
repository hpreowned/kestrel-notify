# adlc_graph_summary — kestrel-notify

Derived from graphify-out/GRAPH_REPORT.md by `adlc baseline`.

## Summary
- 317 nodes · 743 edges · 17 communities (14 shown, 3 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## God nodes (start here for architecture questions)
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

Use `/graphify query|path|explain` for anything structural; `adlc stale` first.
