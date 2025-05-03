from typing import NamedTuple


class EDSR(NamedTuple):
    model_type: str
    scale: int
    model_name: str = "edsr"
