from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import router
from src.api.websocket import ws_router
from src.infrastructure.logger import get_logger, setup_logging
from src.infrastructure.telemetry import setup_telemetry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    setup_telemetry()
    logger.info("AIOps Assistant started")
    yield
    logger.info("AIOps Assistant stopped")


app = FastAPI(
    title="AIOps Assistant",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
app.include_router(ws_router)
