from typing import Callable

from fastapi import Depends

from src.server.config import Settings
from src.server.utils.reports import PDFReportGenerator
from src.server.utils.statistics import RequestStatistics


def get_pdf_reports_generator(
        history_file: str,
        settings_injector: Callable[[], Settings],
) -> Callable[[], PDFReportGenerator]:
    def _get_pdf_reports_generator(
            settings: Settings = Depends(settings_injector),
    ) -> PDFReportGenerator:
        return PDFReportGenerator(history_file=history_file, settings=settings)

    return _get_pdf_reports_generator


def get_statistics_processor(
        history_file: str,
        settings_injector: Callable[[], Settings],
) -> Callable[[], RequestStatistics]:
    def _get_statistics_processor(
            settings: Settings = Depends(settings_injector),
    ) -> RequestStatistics:
        return RequestStatistics(history_file=history_file, settings=settings)

    return _get_statistics_processor
