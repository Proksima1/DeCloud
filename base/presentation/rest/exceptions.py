from fastapi.responses import Response

from base.exceptions import flatten
from base.schemas.base import PureBaseModel
from base.settings import settings


class ErrorBody(PureBaseModel):
    code: str
    message: str
    stack: str | None = None

    def to_response(self, status: int, exc: Exception) -> Response:
        return Response(
            status_code=status,
            media_type="application/json",
            content=ErrorContent(error=self).with_stack(exc).model_dump_json(by_alias=True, exclude_none=True),
        )


class ErrorContent(PureBaseModel):
    error: ErrorBody

    def with_stack(self, exc: Exception) -> "ErrorContent":
        if not settings.release:
            self.error.stack = flatten(exc)

        return self
