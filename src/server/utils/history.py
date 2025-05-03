import json
from datetime import datetime
from functools import wraps
from typing import Dict, Any

from src.server.config import Settings
from src.server.logger import logger


class RequestHistory:
    def __init__(self, history_file: str = "request_history.json", settings: Settings = None):
        self.settings = settings or Settings()

        self.history_file = self.settings.APP_FILES_PATH / history_file
        if not self.history_file.exists():
            with open(self.history_file, "w") as f:
                json.dump([], f)

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request_data = self._collect_request_data(*args, **kwargs)

            try:
                # Выполняем запрос
                start_time = datetime.now()
                response = await func(*args, **kwargs)
                end_time = datetime.now()

                # Добавляем информацию о результате
                request_data.update({
                    "status": "success",
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds(),
                })
            except Exception as e:
                request_data.update({
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })
                raise e
            finally:
                self._save_to_history(request_data)

            return response

        return wrapper

    def updated_kwargs(self, kwargs):
        new_kwargs = {}

        for key, value in kwargs.items():
            try:
                # Попробуем сериализовать стандартным образом
                json.dumps(value)
                new_kwargs[key] = value
            except (TypeError, ValueError):
                # Если не получилось, обрабатываем специальные случаи
                if isinstance(value, (datetime, bytes)):
                    if isinstance(value, datetime):
                        new_kwargs[key] = value.isoformat()
                    elif isinstance(value, bytes):
                        new_kwargs[key] = value.decode()
                elif isinstance(value, (dict, list)):
                    if isinstance(value, dict):
                        new_kwargs[key] = {k: self.updated_kwargs({'_': v})['_'] for k, v in value.items()}
                    else:
                        new_kwargs[key] = [self.updated_kwargs({'_': item})['_'] for item in value]
                else:
                    # Для произвольных объектов попробуем получить их атрибуты или строковое представление
                    try:
                        # Игнорируем методы и служебные атрибуты
                        attrs = {k: v for k, v in value.__dict__.items()
                                 if not k.startswith('_') and not callable(v) and not k == "settings"}
                        if attrs:
                            new_kwargs[key] = self.updated_kwargs(attrs)
                        else:
                            new_kwargs[key] = str(value)
                    except:  # noqa
                        new_kwargs[key] = str(value)

        return new_kwargs

    def _collect_request_data(self, *args, **kwargs) -> Dict[str, Any]:
        """Собирает информацию о запросе."""

        return {
            "args": str(args),
            "endpoint": "/upscaler/upscale/",
            "method": "POST",
            "timestamp": datetime.now().isoformat(),
            **self.updated_kwargs(kwargs),
        }

    def _save_to_history(self, record: Dict[str, Any]):
        """Сохраняет запись в файл истории."""
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)

            history.append(record)

            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save request history: {e}")
