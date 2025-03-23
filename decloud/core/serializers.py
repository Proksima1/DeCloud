from enum import Enum
from typing import Any

from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    @classmethod
    def create_and_validate(
        cls, data: dict | None = None, files: dict | None = None, **kwargs: Any
    ) -> "BaseSerializer":
        if data is None:
            data = {}
        if files is None:
            files = {}

        data.update(kwargs)
        data.update(files)

        serializer = cls(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer


class ErrorCode(Enum):
    INTERNAL_ERROR = "internal.error"
    NOT_FOUND = "not.found"
    BAD_REQUEST = "bad.request"


class ErrorResponseSerializer(BaseSerializer):
    code = serializers.ChoiceField(choices=[(error.value, error.name) for error in ErrorCode])
    message = serializers.CharField()
