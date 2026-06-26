import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/ping2")
async def ping2():
    return {"status": "alive"}


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

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
    from app.main import app as fastapi_app
    fastapi_app.add_middleware(StripPrefixMiddleware)
    app = fastapi_app

    @app.get("/dbcheck")
    async def db_check():
        from sqlalchemy import select, func
        from app.database import async_session
        from app.models import Category, Product, Seller
        from app.config import settings
        async with async_session() as session:
            cat_c = (await session.execute(select(func.count(Category.id)))).scalar()
            prod_c = (await session.execute(select(func.count(Product.id)))).scalar()
            sell_c = (await session.execute(select(func.count(Seller.id)))).scalar()
            return {"db_url": settings.database_url, "cats": cat_c, "prods": prod_c, "sellers": sell_c}

except Exception:
    import traceback
    tb = traceback.format_exc()

    @app.exception_handler(Exception)
    async def catch_all(request, exc):
        return JSONResponse(
            status_code=500,
            content={"error": "Import failed", "traceback": tb.splitlines()},
        )
