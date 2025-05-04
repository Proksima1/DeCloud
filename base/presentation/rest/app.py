import logging
import logging.config
from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.exceptions import ExceptionMiddleware

from base.exceptions import ClientError, SupplierError
from base.presentation.rest.exceptions import ErrorBody
from base.settings import settings

logger = logging.getLogger(__name__)


def create_fastapi_app(*, with_logs: bool = True) -> FastAPI:
    openapi_url = None
    if not settings.release and with_logs:
        openapi_url = settings.fastapi.openapi_url

    app = FastAPI(
        title=settings.service_name,
        openapi_url=openapi_url,
        swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
        root_path=settings.fastapi.root_path,
    )

    app.exception_handler(HTTPException)(_starlette_generic_exception_handler)
    app.exception_handler(RequestValidationError)(_request_validation_error_handler)
    app.exception_handler(Exception)(_unhandled_exception_handler)
    app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)

    return app


def _get_log_extras_for_exc(req: Request) -> dict[str, Any]:
    map_: dict[str, Any] = {"method": req.method, "url": req.url.path}

    if len(req.query_params) != 0:
        map_["query_params"] = req.query_params

    if hasattr(req, "_body"):
        map_["body"] = trim_bytes(req._body, size=500)

    return map_


async def _starlette_generic_exception_handler(req: Request, exc: HTTPException) -> Response:
    logger.warning("bad.request.error", exc_info=True)

    return ErrorBody(
        code="bad.request",
        message="Bad request",
    ).to_response(status.HTTP_400_BAD_REQUEST, exc)


async def _request_validation_error_handler(req: Request, exc: RequestValidationError) -> Response:
    extra = _get_log_extras_for_exc(req)
    logger.warning("request.validation.error", extra=extra, exc_info=True)
    return ErrorBody(
        code="request.validation.error",
        message=repr(exc.errors()),
    ).to_response(status.HTTP_422_UNPROCESSABLE_ENTITY, exc)


async def _unhandled_exception_handler(req: Request, exc: Exception) -> Response:
    logs_extra = _get_log_extras_for_exc(req)
    if issubclass(exc.__class__, ClientError):
        logger.warning("client.error", extra=logs_extra, exc_info=exc)
        return ErrorBody(
            code="bad.client.request",
            message="Bad client request",
        ).to_response(status.HTTP_400_BAD_REQUEST, exc)

    if issubclass(exc.__class__, SupplierError):
        logger.exception("supplier.error", extra=logs_extra, exc_info=exc)
        return ErrorBody(
            code="suplier.error",
            message="Supplier failed to process request",
        ).to_response(status.HTTP_500_INTERNAL_SERVER_ERROR, exc)

    logger.exception("internal.server.error", extra=logs_extra, exc_info=exc)
    return ErrorBody(
        code="internal.server.error",
        message="Internal server error",
    ).to_response(status.HTTP_500_INTERNAL_SERVER_ERROR, exc)
