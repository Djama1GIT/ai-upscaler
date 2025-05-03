from io import BytesIO

from fastapi import APIRouter, File, Depends, UploadFile
from fastapi.responses import StreamingResponse

from src.server.dependencies.settings import get_settings
from src.server.dependencies.upscaler import get_upscaler
from src.server.logger import logger
from src.server.upscaler.opencv import Upscaler

router = APIRouter(
    prefix="/upscaler",
    tags=["Upscaler"],
)


@router.post("/upscale/")
async def upscale(
        image: UploadFile = File(...),
        upscaler: Upscaler = Depends(get_upscaler(get_settings)),
) -> StreamingResponse:
    """Upscale image with given settings and defined model."""
    logger.info(f"Upscaling image {image.filename}")
    file = await image.read()
    upscaled_image = await upscaler.upscale(file, output_format="png")
    logger.info(f"Upscaling complete for {image.filename}")
    return StreamingResponse(
        BytesIO(upscaled_image),
        media_type="image/png",
    )
