from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import ValidationError

from src.server.config import Settings
from src.server.api.v1.routers.upscaler import router as upscaler_router_v1

# Load application configuration
settings = Settings()  # type: ignore[call-arg]

# Initialize main FastAPI application with metadata from settings
app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    summary=settings.SUMMARY,
    contact=settings.CONTACT,
    license_info=settings.LICENSE_INFO,
)

# Initialize API v1 application
v1 = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Include routers for latest API version
app.include_router(upscaler_router_v1, prefix="/api/latest")

# Include routers for v1 API
v1.include_router(upscaler_router_v1)

# Mount v1 application under /api/v1 path
app.mount("/api/v1", v1)


# noinspection PyUnusedLocal
@app.exception_handler(Exception)
async def exception_error(
        request: Request,
        exc: Exception,
) -> JSONResponse:
    """
    Global exception handler for all uncaught exceptions.

    Parameters:
        request: The incoming request (unused)
        exc: The exception that was raised

    Returns:
        JSONResponse: 500 error response with exception details
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"detail": str(exc)}),
    )


# noinspection PyUnusedLocal
@app.exception_handler(ValidationError)
async def validation_exception_error(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.

    Parameters:
        request: The incoming request (unused)
        exc: The validation error that occurred

    Returns:
        JSONResponse: 422 error response with validation error details
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )
