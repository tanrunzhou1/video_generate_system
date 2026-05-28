from fastapi import APIRouter
from app.core.settings import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "env": settings.app_env,
        "storage_dir": settings.storage_dir,
    }
