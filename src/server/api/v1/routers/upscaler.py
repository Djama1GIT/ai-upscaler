from io import BytesIO

from fastapi import APIRouter, File, Depends
from fastapi.responses import StreamingResponse, Response

from src.server.dependencies.settings import get_settings
from src.server.dependencies.upscaler import get_upscaler
from src.server.upscaler.opencv import Upscaler

router = APIRouter()


@router.post("/upscale/")
def upscale(
        image: bytes = File(...),
        upscaler: Upscaler = Depends(get_upscaler(get_settings)),
) -> StreamingResponse:
    upscaled_image = upscaler.upscale(image, output_format="png")
    return StreamingResponse(
        BytesIO(upscaled_image),
        media_type="image/png",
    )
