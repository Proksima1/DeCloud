from fastapi import Depends, File

from decloud.api.database import get_db

# Создаем синглтоны для зависимостей
db_dependency = Depends(get_db)
file_dependency = File(...)
