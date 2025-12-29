"""Translation routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/translate")
async def translate_text():
    """Translate text between languages"""
    return {"status": "available", "message": "Translation service ready"}
