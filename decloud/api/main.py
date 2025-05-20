from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DeCloud API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Импорт и подключение роутеров
from decloud.api.routers import get_image, mock, presigned_url, status, upload

app.include_router(upload.router, prefix="/api", tags=["Prod"])
app.include_router(status.router, prefix="/api", tags=["Prod"])
app.include_router(presigned_url.router, prefix="/api", tags=["Prod"])
app.include_router(get_image.router, prefix="/api", tags=["Prod"])
app.include_router(mock.router, prefix="/api/mock", tags=["Mock"])
