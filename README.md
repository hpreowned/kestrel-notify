# kestrel-notify

Shipment status notifications for Kestrel Freight. Accepts notification requests
(directly or via booking-service webhooks), queues them, and delivers them over
email, SMS or webhook channels. Python 3.12, FastAPI.

The real email and SMS senders are stubs: they record to an in-memory outbox.
The webhook channel performs a real HTTP POST to the recipient URL.

## Run

```
uv venv -p 3.12 .venv
uv pip install -p .venv/bin/python -e ".[dev]"
.venv/bin/uvicorn notify.main:app --port 8080
.venv/bin/pytest -q
```

## Configuration

| Variable | Meaning | Default |
|---|---|---|
| `NOTIFY_WEBHOOK_SECRET` | HMAC secret for `POST /v1/webhooks/booking` | unset (endpoint answers 503) |
| `NOTIFY_RATE_LIMIT_PER_MINUTE` | per-recipient token bucket size; 0 disables limiting | 30 |
| `NOTIFY_FEATURE_SMS` | enable the `sms` channel | false |

## API (snake_case JSON)

- `POST /v1/notifications` body `{shipment_reference, recipient, channel, event}`
  with `channel` in `email|sms|webhook` and `event` in
  `CREATED|RESERVED|IN_TRANSIT|DELIVERED`. Returns 202 with the notification.
  429 `notification rate exceeded` when the recipient bucket is empty.
- `GET /v1/notifications/{id}` returns the notification and its delivery status
  (`QUEUED|SENT|DEAD_LETTERED`).
- `POST /v1/webhooks/booking` receives booking events. The raw body must carry an
  `X-Kestrel-Signature: sha256=<hex>` header (HMAC-SHA256 of the body). Invalid
  or missing signature returns 401 `invalid webhook signature`.
- `GET /healthz`

Carrier codes accepted on booking events: `NSL` (NorthStar Lines),
`BLX` (Baltic Express), `PCR` (Pacific Reach).

## Layout

```
notify/main.py          FastAPI app and routes
notify/service.py       enqueue, rate limit, dispatch, status tracking
notify/queue.py         in-memory queue with retry and dead-letter
notify/ratelimit.py     per-recipient token bucket
notify/signature.py     webhook HMAC signing and verification
notify/channels/        channel interface plus email, sms, webhook senders
notify/templates/       per-event message templates
notify/legacy_fanout.py older fan-out implementation
```

Owners: see `CODEOWNERS`.
