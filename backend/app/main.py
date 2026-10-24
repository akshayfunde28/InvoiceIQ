from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import logger
from app.api.routes import (
    health_router,
    invoices_router,
    dashboard_router,
    vendors_router,
    auth_router,
    assistant_router,
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"{settings.PROJECT_NAME} backend initialized successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="InvoiceIQ — AI-Based Smart Invoice Processing & Indian GST Expense Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", [])])
        msg = err.get("msg", "Invalid value")
        errors.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again or contact support."}
    )

# Include Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(invoices_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(vendors_router, prefix="/api")
app.include_router(assistant_router, prefix="/api")
