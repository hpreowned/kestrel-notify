"""FastAPI app: routes for notifications, booking webhook and health."""

from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from notify import __version__
from notify.models import (
    BookingEvent,
    Notification,
    NotificationRequest,
    WebhookAccepted,
)
from notify.ratelimit import RateLimitExceededError
from notify.service import ChannelDisabledError, NotificationService
from notify.settings import Settings
from notify.signature import SIGNATURE_HEADER, InvalidSignatureError, verify


def build_router() -> APIRouter:
    router = APIRouter()

    @router.get("/healthz")
    async def healthz(request: Request) -> dict[str, object]:
        settings: Settings = request.app.state.settings
        return {
            "status": "ok",
            "version": __version__,
            "sms_enabled": settings.feature_sms,
        }

    @router.post("/v1/notifications", status_code=202, response_model=Notification)
    async def create_notification(
        body: NotificationRequest, request: Request, background: BackgroundTasks
    ) -> Notification:
        service: NotificationService = request.app.state.service
        notification = service.submit(body)
        background.add_task(service.process_pending)
        return notification

    @router.get("/v1/notifications/{notification_id}", response_model=Notification)
    async def get_notification(notification_id: str, request: Request) -> Notification:
        service: NotificationService = request.app.state.service
        notification = service.get(notification_id)
        if notification is None:
            raise HTTPException(status_code=404, detail="notification not found")
        return notification

    @router.post("/v1/webhooks/booking", status_code=202, response_model=WebhookAccepted)
    async def booking_webhook(request: Request, background: BackgroundTasks) -> WebhookAccepted:
        settings: Settings = request.app.state.settings
        service: NotificationService = request.app.state.service
        secret = settings.secret_value()
        if secret is None:
            raise HTTPException(status_code=503, detail="webhook secret not configured")
        raw = await request.body()
        verify(secret, raw, request.headers.get(SIGNATURE_HEADER))
        try:
            event = BookingEvent.model_validate_json(raw)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors(include_url=False, include_context=False)) from exc
        notification = service.submit(
            NotificationRequest(
                shipment_reference=event.shipment_reference,
                recipient=event.recipient,
                channel=event.channel,
                event=event.event,
            ),
            carrier_code=event.carrier_code,
        )
        background.add_task(service.process_pending)
        return WebhookAccepted(notification_id=notification.id, status=notification.status)

    return router


def _error(status: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": detail})


def create_app(
    settings: Settings | None = None, service: NotificationService | None = None
) -> FastAPI:
    """Build the app. Tests pass their own settings and service."""
    settings = settings or Settings()
    app = FastAPI(title="kestrel-notify", version=__version__)
    app.state.settings = settings
    app.state.service = service or NotificationService(settings)
    app.include_router(build_router())

    @app.exception_handler(RateLimitExceededError)
    async def _rate_limited(_: Request, exc: RateLimitExceededError) -> JSONResponse:
        return _error(429, str(exc))

    @app.exception_handler(InvalidSignatureError)
    async def _bad_signature(_: Request, exc: InvalidSignatureError) -> JSONResponse:
        return _error(401, str(exc))

    @app.exception_handler(ChannelDisabledError)
    async def _channel_disabled(_: Request, exc: ChannelDisabledError) -> JSONResponse:
        return _error(422, str(exc))

    return app


app = create_app()
