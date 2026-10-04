import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(self, type_: str, title: str, status: int, detail: str):
        self.type = type_
        self.title = title
        self.status = status
        self.detail = detail

def setup_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status,
            content={
                "type": exc.type,
                "title": exc.title,
                "status": exc.status,
                "detail": exc.detail
            },
            headers={"Content-Type": "application/problem+json"}
        )
