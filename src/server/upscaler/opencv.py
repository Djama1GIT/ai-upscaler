import os
from typing import Optional, Tuple

import cv2
import numpy as np
from cv2 import dnn_superres

from src.server.config import Settings
from src.server.enums.models import ModelEnum
from src.server.logger import logger


class Upscaler:  # todo make async
    """
    Класс для увеличения разрешения изображений с использованием нейросетевых моделей.
    Работает с байтами на входе и выходе.
    """

    def __init__(self, model: ModelEnum, settings: Settings, use_cuda: bool = False):
        """
        Инициализация апскейлера.

        :param model: Выбранная модель из ModelEnum.
        :param use_cuda: Использовать ли CUDA для ускорения
        """
        logger.info(f"Initializing Upscaler with model: {model.name}")  # todo logging
        self.settings = settings or Settings()
        self.model_path = str(self.settings.MODELS_PATH / model.value.model_name / model.value.model_type)
        self.model_name = model.value.model_name
        self.scale = model.value.scale
        self.use_cuda = use_cuda

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        self._initialize_model()

    def _initialize_model(self):
        """Инициализация модели super resolution"""
        self.sr = dnn_superres.DnnSuperResImpl_create()  # type: ignore[name-defined]
        self.sr.readModel(self.model_path)

        if self.use_cuda:
            try:
                self.sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            except Exception as exc:
                print(f"CUDA not available: {exc}, falling back to CPU")
                self.use_cuda = False

        if not self.use_cuda:
            self.sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        self.sr.setModel(self.model_name.lower(), self.scale)

    def upscale(
            self,
            image_bytes: bytes,
            output_size: Optional[Tuple[int, int]] = None,
            output_format: str = 'png',
    ) -> bytes:
        """
        Увеличение разрешения изображения из байтов.

        :param image_bytes: Байты изображения
        :param output_size: Опционально: желаемый размер (ширина, высота)
        :param output_format: Формат выходного изображения ('jpg', 'png')
        :return: Байты увеличенного изображения
        """
        # Преобразование байтов в numpy array
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image")

        # Увеличение разрешения
        if output_size:
            result = self.sr.upsample(image, output_size)
        else:
            result = self.sr.upsample(image)

        # Кодирование результата в байты
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95] if output_format == 'jpg' else []
        success, encoded_image = cv2.imencode(f'.{output_format}', result, encode_param)

        if not success:
            raise RuntimeError("Failed to encode image")

        return encoded_image.tobytes()
