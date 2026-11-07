"""Bound memory before routing, safe errors and allowlisted structured request events."""

import json
import time
from uuid import uuid4

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


def error_response(status: int, code: str, message: str, trace_id: str) -> JSONResponse:
    return JSONResponse(
        {"error": {"code": code, "message": message, "trace_id": trace_id}}, status_code=status
    )


class RequestBoundary:
    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        # Server-generated IDs prevent log injection and misleading cross-request attribution.
        trace_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = trace_id
        started, status, sent = time.monotonic(), 500, False

        async def respond(message: Message) -> None:
            nonlocal status, sent
            if message["type"] == "http.response.start":
                sent = True
                status = message["status"]
                message["headers"] = list(message.get("headers", [])) + [
                    (b"x-request-id", trace_id.encode()),
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                ]
            await send(message)

        try:
            body = bytearray()
            # Check actual bytes, including chunked requests; Content-Length is untrusted.
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > self.max_body_bytes:
                    await error_response(
                        413, "BODY_TOO_LARGE", "Request body is too large", trace_id
                    )(scope, receive, respond)
                    return
                if not message.get("more_body", False):
                    break
            consumed = False

            async def bounded_receive() -> Message:
                nonlocal consumed
                if consumed:
                    return await receive()
                consumed = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}

            await self.app(scope, bounded_receive, respond)
        except Exception:
            if sent:
                raise
            await error_response(500, "INTERNAL_ERROR", "Request could not be completed", trace_id)(
                scope, receive, respond
            )
        finally:
            # Never log bodies, URLs/query strings, headers, secrets or exception messages.
            print(
                json.dumps(
                    {
                        "event": "http_request",
                        "entryPoint": "api",
                        "request_id": trace_id,
                        "method": scope["method"],
                        "status": status,
                        "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    }
                ),
                flush=True,
            )
