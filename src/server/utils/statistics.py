import json
from collections import defaultdict
from typing import List, Dict

from src.server.config import Settings


class RequestStatistics:
    def __init__(self, history_file: str = "request_history.json", settings: Settings = None):
        self.settings = settings or Settings()
        self.history_file = self.settings.APP_FILES_PATH / history_file
        self.history_data = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Загружает историю запросов из файла"""
        if not self.history_file.exists():
            return []

        with open(self.history_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _get_full_model_name(self, upscaler_data: Dict) -> str:
        """Возвращает полное имя модели (например, 'edsr_x2')"""
        model_name = upscaler_data.get("model_name", "unknown")
        scale = upscaler_data.get("scale")

        if scale is not None:
            return f"{model_name}_x{scale}"
        return model_name

    def get_model_usage_stats(self) -> Dict[str, Dict[str, float]]:
        """Возвращает статистику использования моделей с детализацией по версиям"""
        if not self.history_data:
            return {}

        # Словарь: тип модели -> версия модели -> количество
        model_stats = defaultdict(lambda: defaultdict(int))
        total_requests = 0

        for record in self.history_data:
            if record.get("status") != "success":
                continue

            upscaler = record.get("upscaler", {})
            model_name = upscaler.get("model_name")
            if model_name:
                full_name = self._get_full_model_name(upscaler)
                model_stats[model_name][full_name] += 1
                total_requests += 1

        if total_requests == 0:
            return {}

        # Преобразуем в проценты
        result = {}
        for model_type, versions in model_stats.items():
            result[model_type] = {
                version: (count / total_requests) * 100
                for version, count in versions.items()
            }

        return result

    def get_average_processing_time(self) -> Dict[str, float]:
        """Возвращает среднее время обработки для каждой версии модели"""
        if not self.history_data:
            return {}

        # Словарь: полное имя модели -> список времен обработки
        model_times = defaultdict(list)

        for record in self.history_data:
            if record.get("status") != "success":
                continue

            upscaler = record.get("upscaler", {})
            full_name = self._get_full_model_name(upscaler)
            duration = record.get("duration_seconds")

            if full_name != "unknown" and duration is not None:
                model_times[full_name].append(duration)

        return {
            model: sum(times) / len(times)
            for model, times in model_times.items()
        }

    def get_average_file_size(self) -> Dict[str, float]:
        """Возвращает средний размер файлов для каждой версии модели"""
        if not self.history_data:
            return {}

        # Словарь: полное имя модели -> список размеров
        model_sizes = defaultdict(list)

        for record in self.history_data:
            if record.get("status") != "success":
                continue

            upscaler = record.get("upscaler", {})
            full_name = self._get_full_model_name(upscaler)
            image = record.get("image", {})
            size = image.get("size")

            if full_name != "unknown" and size is not None:
                model_sizes[full_name].append(size)

        return {
            model: (sum(sizes) / len(sizes))
            for model, sizes in model_sizes.items()
        }

    def get_success_rate(self) -> float:
        """Возвращает процент успешных запросов"""
        if not self.history_data:
            return 0.0

        total = len(self.history_data)
        success = sum(1 for r in self.history_data if r.get("status") == "success")

        return (success / total) * 100 if total > 0 else 0.0

    def get_scale_factors_stats(self) -> Dict[int, float]:
        """Возвращает статистику по коэффициентам масштабирования"""
        if not self.history_data:
            return {}

        scale_counts = defaultdict(int)
        total = 0

        for record in self.history_data:
            if record.get("status") != "success":
                continue

            upscaler = record.get("upscaler", {})
            scale = upscaler.get("scale")

            if scale is not None:
                scale_counts[scale] += 1
                total += 1

        return {
            scale: (count / total) * 100
            for scale, count in scale_counts.items()
        }

    def get_all_stats(self) -> Dict[str, Dict]:
        """Возвращает всю статистику в одном словаре"""
        return {
            "model_usage": self.get_model_usage_stats(),
            "avg_processing_time": self.get_average_processing_time(),
            "avg_file_size": self.get_average_file_size(),
            "success_rate": self.get_success_rate(),
            "scale_factors": self.get_scale_factors_stats(),
        }


if __name__ == '__main__':
    stats = RequestStatistics("request_history.json")

    # Получить всю статистику
    all_stats = stats.get_all_stats()
    print("Полная статистика:")
    print(json.dumps(all_stats, indent=2))

    # Пример вывода отдельных метрик
    print("\nИспользование моделей (%):")
    for model_type, versions in stats.get_model_usage_stats().items():
        print(f"  {model_type}:")
        for version, percent in versions.items():
            print(f"    {version}: {percent:.1f}%")

    print("\nСреднее время обработки:")
    for model, time in stats.get_average_processing_time().items():
        print(f"  {model}: {time:.2f} сек")

    print("\nСредний размер файлов:")
    for model, size in stats.get_average_file_size().items():
        print(f"  {model}: {size:.2f} байт")

    print(f"\nПроцент успешных запросов: {stats.get_success_rate():.1f}%")

    print("\nКоэффициенты масштабирования:")
    for scale, percent in stats.get_scale_factors_stats().items():
        print(f"  x{scale}: {percent:.1f}%")
