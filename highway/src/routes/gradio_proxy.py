"""Reverse proxy to forward requests to the Gradio service."""

from fastapi import APIRouter, Depends
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import StreamingResponse

import httpx

from src.auth.tg_auth import authenticated_user
from src.config import settings

gradio_router = APIRouter(prefix="/gradio", tags=["gradio"])

client = httpx.AsyncClient(base_url=settings.gradio_app_url)


@gradio_router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    dependencies=[Depends(authenticated_user)],
)
async def gradio_proxy(request: Request) -> StreamingResponse:
    """Forward any request under /gradio/* to the Gradio backend."""

    url = httpx.URL(
        path=request.url.path.replace("/gradio/", "/"),
        query=request.url.query.encode("utf-8"),
    )
    # Convert headers to a mutable dict and remove Host header
    headers = dict(request.headers.raw)
    headers.pop(b"host", None)
    # Set timeout to None (infinite)
    rp_req = client.build_request(
        request.method,
        url,
        headers=list(headers.items()),
        content=request.stream(),
        timeout=None
    )
    rp_resp = await client.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )