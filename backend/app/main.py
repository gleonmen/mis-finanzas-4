from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.interfaces.api import (
    routes_categories,
    routes_month_load,
    routes_reports,
    routes_templates,
)

app = FastAPI(title="Finanzas API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(routes_templates.router)
app.include_router(routes_categories.router)
app.include_router(routes_month_load.router)
app.include_router(routes_reports.router)
