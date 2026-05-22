import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from prometheus_client import make_asgi_app

from src.config import settings
from src.api import router
from src.database import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AgroMind API")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down AgroMind API")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgroMind API",
        description="The Autonomous Intelligence Layer for Post-Chemical Agriculture",
        version="0.0.1",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(GZIPMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Metrics
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # Health check
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {"status": "ok", "version": "0.0.1"}

    # API routes
    app.include_router(router, prefix="/api")

    logger.info("AgroMind API initialized")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
