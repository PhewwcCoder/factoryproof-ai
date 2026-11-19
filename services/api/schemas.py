from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    buyer_id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=4000)
    evidence_type: str = Field(min_length=1, max_length=80)
    months: int | None = Field(default=None, ge=1, le=120)
    days: int | None = Field(default=None, ge=1, le=3650)
    signatures: list[str] = Field(default_factory=list, max_length=20)
    scope: str = 'entire_factory'
    minimum_frequency: int | None = Field(default=None, ge=1, le=1000)
    minimum_value: float | None = None
    mandatory_fields: list[str] = Field(default_factory=lambda: ['event_date'])
    period_start: date | None = None
    period_end: date | None = None
    source_reference: str = 'Fictional demonstration checklist, v1'
    version: int = Field(default=1, ge=1)


class ReviewInput(BaseModel):
    decision: Literal['approved', 'rejected', 'correction_requested']
    note: str = Field(min_length=5, max_length=2000)


class LoginInput(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=256)


class BuyerInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class RunInput(BaseModel):
    reference_date: date = date(2026, 12, 26)
