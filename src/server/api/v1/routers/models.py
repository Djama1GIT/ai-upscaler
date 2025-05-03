from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.server.enums.models import ModelsList

router = APIRouter(
    prefix="/models",
    tags=["Models"],
)


@router.get("/")
async def models() -> JSONResponse:
    return JSONResponse({"models": list(ModelsList)}, status_code=200)
