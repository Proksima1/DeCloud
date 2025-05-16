from contextvars import ContextVar

_LOG_CONTEXT: ContextVar[dict[str, str]] = ContextVar("_LOG_CONTEXT", default={})
