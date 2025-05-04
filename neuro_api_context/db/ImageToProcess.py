from sqlalchemy import Column, Text

from neuro_api_context.db.base import Base, WithCreatedAt, WithId


class ImageToProcess(Base, WithId, WithCreatedAt):
    __tablename__ = "api_image_to_process"

    status = Column(Text, comment="Статус обработки изображения")
    sar_file = Column(Text, nullable=False, comment="Уникальный идентификатор оператора-донора в БДПН")
    range_holder_id = Column(
        Text,
        nullable=False,
        comment="Уникальный идентификатор владельца номера по лицензии в БДПН",
    )
