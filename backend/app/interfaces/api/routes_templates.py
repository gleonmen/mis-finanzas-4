"""Templates endpoints: list (feeds the draft grid) + CRUD admin."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response

from app.application.errors import TemplateNotFoundError, TemplateValidationError
from app.domain.entities import TemplateData
from app.interfaces.api.deps import (
    CreateTemplateDep,
    DeleteTemplateDep,
    ListTemplatesDep,
    UpdateTemplateDep,
)
from app.interfaces.api.schemas import TemplateOut, TemplateWriteIn

router = APIRouter(tags=["templates"])


def _to_data(payload: TemplateWriteIn) -> TemplateData:
    return TemplateData(
        transaction_type=payload.transaction_type,
        category_id=payload.category_id,
        name=payload.name,
        is_essential=payload.is_essential,
        default_amount=payload.default_amount,
        frequency=payload.frequency,
    )


@router.get("/templates", response_model=list[TemplateOut])
def list_templates(use_case: ListTemplatesDep) -> list[TemplateOut]:
    templates = use_case.execute()
    return [
        TemplateOut.model_validate(t, from_attributes=True) for t in templates
    ]


@router.post("/templates", response_model=TemplateOut, status_code=201)
def create_template(
    payload: TemplateWriteIn, use_case: CreateTemplateDep
) -> TemplateOut:
    try:
        created = use_case.execute(_to_data(payload))
    except TemplateValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return TemplateOut.model_validate(created, from_attributes=True)


@router.put("/templates/{template_id}", response_model=TemplateOut)
def update_template(
    template_id: int, payload: TemplateWriteIn, use_case: UpdateTemplateDep
) -> TemplateOut:
    try:
        updated = use_case.execute(template_id, _to_data(payload))
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return TemplateOut.model_validate(updated, from_attributes=True)


@router.delete("/templates/{template_id}", status_code=204)
def delete_template(template_id: int, use_case: DeleteTemplateDep) -> Response:
    try:
        use_case.execute(template_id)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=204)
