from datetime import datetime

from fastapi import Depends, APIRouter, status
from fastapi.responses import Response, JSONResponse

from src.server.dependencies.history import get_pdf_reports_generator, get_statistics_processor
from src.server.dependencies.settings import get_settings
from src.server.logger import logger
from src.server.utils.reports import PDFReportGenerator
from src.server.utils.statistics import RequestStatistics

router = APIRouter(
    prefix="/history",
    tags=["History"],
)


@router.get("/report")
async def get_history_report(
        reports_generator: PDFReportGenerator = Depends(
            get_pdf_reports_generator(
                history_file="request_history.json",
                settings_injector=get_settings,
            ),
        ),
) -> Response:
    """Endpoint to generate and download request history PDF report"""
    pdf_bytes = reports_generator.generate_report()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"request_history_report_{timestamp}.pdf"

    logger.info(f"Request history report generated and saved as {filename} with size {len(pdf_bytes)} bytes")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(pdf_bytes)),
        }
    )


@router.get("/statistics")
async def get_statistics(
        statistics_processor: RequestStatistics = Depends(
            get_statistics_processor(
                history_file="request_history.json",
                settings_injector=get_settings,
            )
        ),
) -> JSONResponse:
    return JSONResponse(
        content=statistics_processor.get_all_stats(),
        status_code=status.HTTP_200_OK,
    )
