"""Templates endpoints (read-only in this slice: they feed the draft grid)."""
from __future__ import annotations

from fastapi import APIRouter

from app.interfaces.api.deps import ListTemplatesDep
from app.interfaces.api.schemas import TemplateOut

router = APIRouter(tags=["templates"])


@router.get("/templates", response_model=list[TemplateOut])
def list_templates(use_case: ListTemplatesDep) -> list[TemplateOut]:
    templates = use_case.execute()
    return [
        TemplateOut.model_validate(t, from_attributes=True) for t in templates
    ]
