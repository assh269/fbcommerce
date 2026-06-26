import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Scope, Receive, Send


class StripPrefixMiddleware:
    def __init__(self, app: ASGIApp, prefix: str = "/api"):
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http" and scope["path"].startswith(self.prefix):
            scope["path"] = scope["path"][len(self.prefix):] or "/"
            scope["root_path"] = self.prefix
        await self.app(scope, receive, send)


try:
    from app.main import app
    app.add_middleware(StripPrefixMiddleware)
except Exception as e:
    tb = traceback.format_exc()
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "traceback": tb.splitlines()},
        )
