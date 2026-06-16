"""FastAPI web admin panel - DLBot administration dashboard"""
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import logging

from config import settings as app_settings
from web.auth import get_current_admin
from web.routers import dashboard, users, broadcast, plans, payments, settings as web_settings

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Max Youtube Downloader - Admin Panel",
    description="Max Youtube Downloader Bot - Admin Dashboard",
    version=app_settings.APP_VERSION,
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.environment,
    }


# Root redirect
@app.get("/")
async def root():
    """Root endpoint - redirect to dashboard"""
    return {"message": "DLBot Admin Panel", "docs_url": "/docs"}


# API Routes
# Dashboard routes
app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_admin)],
)

# User management routes
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(get_current_admin)],
)

# Broadcast routes
app.include_router(
    broadcast.router,
    prefix="/api/broadcast",
    tags=["broadcast"],
    dependencies=[Depends(get_current_admin)],
)

# Plans management routes
app.include_router(
    plans.router,
    prefix="/api/plans",
    tags=["plans"],
    dependencies=[Depends(get_current_admin)],
)

# Payment routes
app.include_router(
    payments.router,
    prefix="/api/payments",
    tags=["payments"],
    dependencies=[Depends(get_current_admin)],
)

# Settings routes
app.include_router(
    web_settings.router,
    prefix="/api/settings",
    tags=["settings"],
    dependencies=[Depends(get_current_admin)],
)


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.environment == "development" else None,
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("DLBot Admin Panel starting up...")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("DLBot Admin Panel shutting down...")


# Admin dashboard template route
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(get_current_admin)])
async def admin_dashboard(request: Request):
    """Render admin dashboard template with basic metrics (uses API endpoints for data)"""
    # Local imports to avoid circular imports at module import time
    from web.routers import dashboard as dashboard_api
    from datetime import datetime

    overview = await dashboard_api.get_dashboard_overview(None)
    downloads = await dashboard_api.get_download_chart_data(7)
    revenue = await dashboard_api.get_revenue_chart_data(7)
    users = await dashboard_api.get_users_chart_data(7)

    # Prepare chart data (fallback to sample data)
    user_growth_labels = users.get("labels", [f"Day {i}" for i in range(1,8)])
    user_growth_data = users.get("datasets", [{}])[0].get("data", [1000 + i * 30 for i in range(7)])
    platform_data = downloads.get("datasets", [{}])[0].get("data", [412,78,33,10,5])
    coins_trend_labels = downloads.get("labels", [f"Day {i}" for i in range(1,8)])
    coins_trend_data = downloads.get("datasets", [{}])[0].get("data", [100 + i * 20 for i in range(7)])
    subscription_data = [1000, overview["users"]["premium"], 12] if overview and "users" in overview else [1000,238,12]

    context = {
        "request": request,
        "total_users": overview["users"]["total"] if overview else 0,
        "new_users_today": overview["users"]["new_today"] if overview else 0,
        "total_downloads": (downloads.get("datasets", [{}])[0].get("data", [0])[0]) if downloads else 0,
        "downloads_today": overview["downloads"]["today"] if overview else 0,
        "total_coins": 0,
        "coins_today": 0,
        "premium_users": overview["users"]["premium"] if overview else 0,
        "premium_percentage": round(overview["users"]["premium"] / max(1, overview["users"]["total"]) * 100, 1) if overview else 0,
        "user_growth_labels": user_growth_labels,
        "user_growth_data": user_growth_data,
        "platform_data": platform_data,
        "coins_trend_labels": coins_trend_labels,
        "coins_trend_data": coins_trend_data,
        "subscription_data": subscription_data,
        "top_earners": [],
        "recent_transactions": [],
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    }

    return templates.TemplateResponse("dashboard.html", context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.web_panel.host,
        port=settings.web_panel.port,
        reload=settings.web_panel.reload,
    )

