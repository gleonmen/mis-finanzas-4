"""Categories endpoint (read-only: feeds the template form selector)."""
from __future__ import annotations

from fastapi import APIRouter

from app.interfaces.api.deps import ListCategoriesDep
from app.interfaces.api.schemas import CategoryOut

router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(use_case: ListCategoriesDep) -> list[CategoryOut]:
    categories = use_case.execute()
    return [
        CategoryOut.model_validate(c, from_attributes=True) for c in categories
    ]
