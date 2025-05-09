import enum
import logging
import logging.config
import warnings
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from pythonjsonlogger import json

from base.exceptions import flatten
from base.log_context import _LOG_CONTEXT
from base.schemas.base import PureBaseModel
from base.utils.json import any_to_json_str


class LoggerFormatter(str, enum.Enum):
    JSON = "JSON"
    CONSOLE = "CONSOLE"


class LoggerSettings(PureBaseModel):
    level: str = "INFO"
    formatter: LoggerFormatter = LoggerFormatter.CONSOLE

    loggers: dict[str, Any] = {
        "aioapns": {"handlers": ["console"], "level": "CRITICAL"},
        "aiokafka": {"handlers": ["console"], "level": "WARNING"},
        "psycopg2": {"handlers": ["console"], "level": "DEBUG"},
        "boto3": {"handlers": ["console"], "level": "INFO"},
        "botocore": {"handlers": ["console"], "level": "INFO"},
        "faststream": {"handlers": ["console"], "level": "INFO"},
        "aiobotocore": {"handlers": ["console"], "level": "INFO"},
        "asyncio": {"handlers": ["console"], "level": "CRITICAL"},
        "uvicorn": {"handlers": ["console"], "level": "WARNING"},
        "grpc": {"handlers": ["console"], "level": "INFO"},
        "urllib3": {"handlers": ["console"], "level": "CRITICAL"},
        "asynch": {"handlers": ["console"], "level": "INFO"},
        "matplotlib": {"handlers": ["console"], "level": "INFO"},
        "tzlocal": {"handlers": ["console"], "level": "INFO"},
        "paramiko": {"handlers": ["console"], "level": "INFO"},
        "httpx": {"handlers": ["console"], "level": "WARNING"},
    }
    update_loggers: dict[str, str] = {}

    def config(self) -> dict[str, Any]:
        loggers = self.loggers
        for logger, level in self.update_loggers.items():
            if logger in loggers:
                loggers[logger]["level"] = level

        formatter = "base.logger.Formatter"
        if self.formatter == LoggerFormatter.JSON:
            formatter = "base.logger.CustomJsonFormatter"

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"default": {"class": formatter}},
            "handlers": {"console": {"level": self.level, "class": "logging.StreamHandler", "formatter": "default"}},
            "loggers": {"": {"handlers": ["console"], "level": self.level}, **loggers},
        }


class _Colors(str, enum.Enum):
    GREEN = "\x1b[32;20m"
    GREEN_BOLD = "\x1b[32;1m"
    YELLOW = "\x1b[33;20m"
    YELLOW_BOLD = "\x1b[33;1m"
    RED = "\x1b[31;20m"
    RED_BOLD = "\x1b[31;1m"
    GREY = "\x1b[30;20m"
    GREY_BOLD = "\x1b[30;1m"
    WHITE = "\x1b[29;20m"
    WHITE_BOLD = "\x1b[29;1m"
    CYAN = "\x1b[36;20m"
    ENDC = "\x1b[0m"


_log_level_to_color: dict[int, str] = {
    logging.DEBUG: _Colors.WHITE,
    logging.INFO: _Colors.GREEN,
    logging.WARNING: _Colors.YELLOW_BOLD,
    logging.ERROR: _Colors.RED_BOLD,
    logging.CRITICAL: _Colors.RED_BOLD,
}


class Formatter(logging.Formatter):
    _format_with_colors: str = (
        "{grey_bold}[%(asctime)s.%(msecs)03d]{endc} {color}%(levelname)s{endc} "
        "{cyan}[%(name)s:%(funcName)s:%(lineno)s]{endc} {white_bold}"
        "%(message)s{endc}%(log_context)s %(_extra)s"
    )
    _format: str = (
        "[%(asctime)s.%(msecs)03d] %(levelname)s "
        "[%(name)s:%(funcName)s:%(lineno)s] %(message)s%(log_context)s %(_extra)s"
    )

    def _with_colors(self, record: logging.LogRecord) -> str:
        fmt = self._format_with_colors.format(
            endc=_Colors.ENDC,
            grey=_Colors.GREY,
            white_bold=_Colors.WHITE_BOLD,
            color=_log_level_to_color[record.levelno],
            cyan=_Colors.CYAN,
            grey_bold=_Colors.GREY_BOLD,
        )
        return logging.Formatter(fmt, datefmt="%d/%b/%Y %H:%M:%S").format(record)

    def _with_no_new_line(self, text: str) -> str:
        return text.replace("\n", " ")

    def format(self, record: logging.LogRecord) -> str:
        ctx = _LOG_CONTEXT.get()
        if len(ctx) != 0:
            record.log_context = " " + any_to_json_str(ctx)
        else:
            record.log_context = ""

        return self._with_no_new_line(self._with_colors(record))


def patch_extra() -> None:
    original_makeRecord = logging.Logger.makeRecord

    def make_record_with_extra(
        self,  # noqa: ANN001
        name: str,
        level,  # noqa: ANN001
        fn,  # noqa: ANN001
        lno: int,
        msg: object,
        args,  # noqa: ANN001
        exc_info,  # noqa: ANN001
        func=None,  # noqa: ANN001
        extra: Mapping[str, Any] | None = None,
        sinfo=None,  # noqa: ANN001
    ) -> logging.LogRecord:
        if extra is not None:
            extra = dict(extra)

            message = extra.pop("message", None)
            if message is not None:
                warnings.warn("Using message as key in extra is forbidden!")
                extra["_message"] = message

        record = original_makeRecord(self, name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)

        if extra is None:
            record._extra = ""
        else:
            record._extra = any_to_json_str(extra)

        return record

    logging.Logger.makeRecord = make_record_with_extra


class CustomJsonFormatter(json.JsonFormatter):
    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["caller"] = f"{record.name}:{record.funcName}:{record.lineno}"
        log_record["level"] = record.levelname
        log_record["time"] = datetime.now().isoformat()[:-3]
        log_record["message"] = record.message

        log_record.update(_LOG_CONTEXT.get())

        if record.exc_info is not None:
            log_record["error"] = flatten(record.exc_info[1])


def init_logger(settings: LoggerSettings) -> None:
    logging.config.dictConfig(settings.config())

    if settings.formatter == LoggerFormatter.CONSOLE:
        patch_extra()
