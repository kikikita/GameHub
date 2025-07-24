from fastapi import FastAPI
from src.config import settings
from src.routes.gradio_proxy import gradio_router
from src.routes.auth import auth_router
from src.api.auth.router import router as api_router
from src.api.templates.router import router as templates_router
from src.api.sessions.router import router as sessions_router
from src.api.scenes.router import router as scenes_router
from src.api.payments.router import router as payments_router
import logging
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)    


if settings.debug_mode:
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

app.include_router(gradio_router)
app.include_router(auth_router)
app.include_router(api_router)
app.include_router(templates_router)
app.include_router(sessions_router)
app.include_router(scenes_router)
app.include_router(payments_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health-check")
def health_check():
    return {"status": "ok"} 
