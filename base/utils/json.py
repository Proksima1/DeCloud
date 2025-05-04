import warnings
from typing import Any

import ujson  # type: ignore
from fastapi.encoders import jsonable_encoder


def any_to_json_str(anything: Any) -> str:  # noqa: ANN401 # * reason: jsonable_encoder uses Any type
    """Only for debug and log perposes!"""

    try:
        if isinstance(anything, dict):
            for key, value in anything.items():
                if hasattr(value, "__dump_for_log__") and callable(value.__dump_for_log__):
                    anything[key] = value.__dump_for_log__()

        return ujson.dumps(jsonable_encoder(anything), ensure_ascii=False)

    except Exception as exc:
        warnings.warn(f"Failed to dump object: {exc=}")
        return ujson.dumps({"undumpable": str(anything)})
