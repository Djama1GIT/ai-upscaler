from enum import Enum
from typing import Literal

from src.server.schemas.models import EDSR


class ModelEnum(Enum):
    EDSR_x2 = EDSR(model_type="EDSR_x2.pb", scale=2)
    EDSR_x3 = EDSR(model_type="EDSR_x3.pb", scale=3)
    EDSR_x4 = EDSR(model_type="EDSR_x4.pb", scale=4)


ModelsList = ModelEnum.__members__.keys()
ModelType = Literal[*ModelsList]  # type: ignore
