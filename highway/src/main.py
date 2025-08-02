"""Application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.auth.router import router as api_router
from src.api.worlds.router import router as worlds_router
from src.api.stories.router import router as stories_router
from src.api.sessions.router import router as sessions_router
from src.api.scenes.router import router as scenes_router
from src.api.payments.router import router as payments_router
from src.api.wish_payments.router import router as wish_payments_router 

import logging

logger = logging.getLogger(__name__)    


if settings.debug:
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    logger.info("Debugger enabled!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(worlds_router)
app.include_router(stories_router)
app.include_router(sessions_router)
app.include_router(scenes_router)
app.include_router(payments_router)
app.include_router(wish_payments_router)

@app.get("/health-check")
def health_check() -> dict:
    """Endpoint for liveness probes."""

    return {"status": "ok"}
