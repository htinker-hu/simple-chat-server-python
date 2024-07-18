import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from app_config import AppConfig
from app_router import app as chat_router

log = logging.getLogger("root.app")


@asynccontextmanager
async def lifespan_event(application: FastAPI):
    # Prepare before serving request
    # on startup ...
    log.info("The server is starting up")
    yield
    # Clean after before shutting down
    # on shutdown ...
    log.info("The server is shutting down")


app = FastAPI(
    title="Simple Chat",
    summary="The service provides AI APIs",
    debug=False,
    root_path="",
    openapi_url="/openapi.json",
    version="0.0.1",
    description="""
    Simple Chat will help you run into a magic world.
    """,
    servers=[
        {"url": "https://stag.example.com/", "description": "Staging environment"},
        {"url": "https://prod.example.com/", "description": "Production environment"},
    ],
    lifespan=lifespan_event
)


# add middlewares in reverse order: the last added, the first called
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=AppConfig.TRUSTED_HOSTS)


@app.exception_handler(HTTPException)
async def _http_exception_handler(request: Request, exc: HTTPException) -> Response:
    log.error(f"Unhandled error: {exc}")
    traceback.print_exc()
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> Response:
    log.error(f"Unhandled error: {exc}")
    traceback.print_exc()
    return JSONResponse(
        {"detail": str(exc)}, status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )


@app.get("/health", tags=["DevOps"], operation_id="healthz",
         summary="Check whether the server is ready to service")
async def healthz() -> str:
    return "ok"

# register routers for web admin
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    from os import path

    log_config = path.dirname(path.abspath(__file__)) + "/logging-conf.ini"
    uvicorn.run(app, host="0.0.0.0", port=AppConfig.PORT, log_config=log_config)
