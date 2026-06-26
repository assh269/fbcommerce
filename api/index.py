import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from starlette.types import ASGIApp, Scope, Receive, Send
from app.main import app


class StripPrefixMiddleware:
    def __init__(self, app: ASGIApp, prefix: str = "/api"):
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http" and scope["path"].startswith(self.prefix):
            scope["path"] = scope["path"][len(self.prefix):] or "/"
            scope["root_path"] = self.prefix
        await self.app(scope, receive, send)


app.add_middleware(StripPrefixMiddleware)
