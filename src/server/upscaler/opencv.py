import os
from typing import Optional, Tuple
import asyncio

import cv2
import numpy as np
from cv2 import dnn_superres

from src.server.config import Settings
from src.server.enums.models import ModelEnum
from src.server.logger import logger


class Upscaler:
    """
    Класс для увеличения разрешения изображений с использованием нейросетевых моделей.
    Работает с байтами на входе и выходе.
    """

    def __init__(self, model: ModelEnum, settings: Settings, use_cuda: bool = None):
        """
        Инициализация апскейлера.

        :param model: Выбранная модель из ModelEnum.
        :param use_cuda: Использовать ли CUDA для ускорения
        """
        logger.info(f"Initializing Upscaler with model: {model.name}")
        logger.debug(f"Model path: {model.value.model_name}/{model.value.model_type}")
        logger.debug(f"Scale factor: {model.value.scale}")

        self.settings = settings or Settings()
        self.model_path = str(self.settings.MODELS_PATH / model.value.model_name / model.value.model_type)
        self.model_name = model.value.model_name
        self.scale = model.value.scale
        self.use_cuda = use_cuda if use_cuda is not None else self.settings.USE_CUDA
        self.sr = None
        self._initialized = False

        logger.debug(f"Full model path: {self.model_path}")
        logger.info(f"CUDA enabled: {self.use_cuda}")

        if not os.path.exists(self.model_path):
            error_msg = f"Model file not found: {self.model_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    async def initialize(self):
        """Асинхронная инициализация модели super resolution"""
        logger.info("Starting model initialization...")
        try:
            await asyncio.get_event_loop().run_in_executor(None, self._initialize_model_sync)
            self._initialized = True
            logger.info("Model successfully initialized")
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise

    def _initialize_model_sync(self):
        """Синхронная инициализация модели (выполняется в executor)"""
        logger.debug("Creating DnnSuperResImpl instance")
        self.sr = dnn_superres.DnnSuperResImpl_create()  # type: ignore[name-defined]

        logger.debug(f"Reading model from {self.model_path}")
        self.sr.readModel(self.model_path)

        if self.use_cuda:
            try:
                logger.debug("Setting CUDA backend and target")
                self.sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                logger.info("CUDA backend successfully configured")
            except Exception as exc:
                logger.warning(f"CUDA not available: {exc}, falling back to CPU")
                self.use_cuda = False

        if not self.use_cuda:
            logger.debug("Setting OpenCV backend and CPU target")
            self.sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

        logger.debug(f"Setting model: {self.model_name.lower()} with scale {self.scale}")
        self.sr.setModel(self.model_name.lower(), self.scale)

    async def upscale(
            self,
            image_bytes: bytes,
            output_size: Optional[Tuple[int, int]] = None,
            output_format: str = 'png',
    ) -> bytes:
        """
        Асинхронное увеличение разрешения изображения из байтов.

        :param image_bytes: Байты изображения
        :param output_size: Опционально: желаемый размер (ширина, высота)
        :param output_format: Формат выходного изображения ('jpg', 'png')
        :return: Байты увеличенного изображения
        """
        logger.info("Starting upscaling process")
        logger.debug(f"Input size: {len(image_bytes)} bytes")
        logger.debug(f"Output format: {output_format}")
        if output_size:
            logger.debug(f"Target output size: {output_size}")

        if not self._initialized:
            logger.info("Model not initialized, initializing now...")
            await self.initialize()

        try:
            # Запускаем CPU-bound операции в executor
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._upscale_sync,
                image_bytes,
                output_size,
                output_format
            )
            logger.info("Upscaling completed successfully")
            logger.debug(f"Output size: {len(result)} bytes")
            return result
        except Exception as e:
            logger.error(f"Upscaling failed: {str(e)}")
            raise

    def _upscale_sync(
            self,
            image_bytes: bytes,
            output_size: Optional[Tuple[int, int]],
            output_format: str
    ) -> bytes:
        """Синхронная реализация upscale для выполнения в executor"""
        logger.debug("Decoding image from bytes")
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            error_msg = "Failed to decode image from bytes"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug(f"Original image dimensions: {image.shape[1]}x{image.shape[0]}")

        # Увеличение разрешения
        logger.info("Performing upscaling...")
        if output_size:
            logger.debug(f"Using custom output size: {output_size}")
            result = self.sr.upsample(image, output_size)
        else:
            logger.debug("Using default upscaling")
            result = self.sr.upsample(image)

        logger.debug(f"Upscaled image dimensions: {result.shape[1]}x{result.shape[0]}")

        # Кодирование результата в байты
        logger.debug(f"Encoding image to {output_format} format")
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95] if output_format == 'jpg' else []
        success, encoded_image = cv2.imencode(f'.{output_format}', result, encode_param)

        if not success:
            error_msg = f"Failed to encode image to {output_format} format"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        return encoded_image.tobytes()
