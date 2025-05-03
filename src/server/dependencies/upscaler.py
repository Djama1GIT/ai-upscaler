from typing import Callable

from fastapi import Depends, Body

from src.server.config import Settings
from src.server.enums.models import ModelEnum, ModelType
from src.server.upscaler.opencv import Upscaler


def get_upscaler(get_settings: Callable[[], Settings]) -> Callable[[ModelType], Upscaler]:
    def _get_upscaler(model: ModelType = Body(...), settings: Settings = Depends(get_settings)) -> Upscaler:
        upscaler = Upscaler(model=ModelEnum[model], settings=settings)
        return upscaler

    return _get_upscaler
