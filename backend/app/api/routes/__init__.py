from app.api.routes.health import router as health_router
from app.api.routes.invoices import router as invoices_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.vendors import router as vendors_router
from app.api.routes.auth import router as auth_router
from app.api.routes.assistant import router as assistant_router

__all__ = [
    "health_router",
    "invoices_router",
    "dashboard_router",
    "vendors_router",
    "auth_router",
    "assistant_router",
]
