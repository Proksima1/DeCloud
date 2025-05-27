import logging
from hashlib import md5
from typing import Any, Optional

import humps
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, ValidationError

logger = logging.getLogger(__name__)


class PureBaseModel(BaseModel):
    def jsonable_encoder(self, **kwargs: Any) -> Any:  # noqa: ANN401
        return jsonable_encoder(self, **kwargs)

    model_config = ConfigDict(populate_by_name=True, from_attributes=True, use_enum_values=True)

    def __repr__(self) -> str:
        return self.model_dump_json(by_alias=True)

    def __str__(self) -> str:
        return repr(self)

    def md5(self, **dump_json_kwargs: Any) -> str:  # noqa: ANN401 # * Allowed in proxy methods
        return md5(  # noqa: S324 # * md5 is save here
            string=self.model_dump_json(**dump_json_kwargs).encode()
        ).hexdigest()

    @classmethod
    def model_validate_json_or_warn(
        cls,
        *args: Any,  # noqa: ANN401 # Allowed for this proxy function
        **kwargs: Any,  # noqa: ANN401 # Allowed for this proxy function
    ) -> Optional["PureBaseModel"]:
        try:
            return cls.model_validate_json(*args, **kwargs)
        except ValidationError:
            logger.warning("failed.to.validate.model", extra={"kwargs": kwargs}, exc_info=True)

        return None


class CamelizedBaseModel(PureBaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True, alias_generator=humps.camelize)
