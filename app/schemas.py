"""Phase 3 request/response schemas for incidents and evidence.

Maximum lengths reuse the shared database configuration pending pod agreement.
Required text rejects blank values but is preserved.
"""

import re
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, BeforeValidator, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from app.config import DESCRIPTION_MAX_LENGTH, SHORT_TEXT_MAX_LENGTH, TITLE_MAX_LENGTH


class APISchema(BaseModel):
    """Accept Python field names and expose camelCase JSON names."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
    )


RequiredText = Annotated[str, Field(min_length=1, strict=True)]


def require_timestamp_format(value: object) -> object:
    """Reject numeric epochs and non-contract strings before datetime coercion."""
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt][0-9]{2}:[0-9]{2}:[0-9]{2}"
        r"(?:\.[0-9]+)?(?:[Zz]|[+-][0-9]{2}:[0-9]{2})",
        value,
    ):
        raise ValueError("Must be an RFC 3339 timestamp with timezone")
    return value


RequestTimestamp = Annotated[AwareDatetime, BeforeValidator(require_timestamp_format)]


class EvidenceCategory(StrEnum):
    TECHNICAL = "TECHNICAL"
    BUSINESS_IMPACT = "BUSINESS_IMPACT"
    LEGAL = "LEGAL"
    OTHER = "OTHER"


class IncidentStatus(StrEnum):
    OPEN = "OPEN"
    NOT_MATERIAL = "NOT_MATERIAL"
    MATERIAL_PENDING_FILING = "MATERIAL_PENDING_FILING"
    FILED = "FILED"


class IncidentCreate(APISchema):
    title: RequiredText = Field(max_length=TITLE_MAX_LENGTH)
    description: RequiredText = Field(max_length=DESCRIPTION_MAX_LENGTH)
    discovered_at: RequestTimestamp
    reporter_name: RequiredText = Field(max_length=SHORT_TEXT_MAX_LENGTH)

    @field_validator("title", "description", "reporter_name")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be blank")
        return value

    @field_validator("discovered_at")
    @classmethod
    def validate_discovery_time(cls, value: datetime) -> datetime:
        if value > datetime.now(UTC):
            raise ValueError("Discovery time must not be in the future")
        return value.astimezone(UTC)


class EvidenceCreate(APISchema):
    category: EvidenceCategory
    summary: RequiredText
    source: RequiredText = Field(max_length=SHORT_TEXT_MAX_LENGTH)
    collected_at: RequestTimestamp

    @field_validator("summary", "source")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be blank")
        return value

    @field_validator("collected_at")
    @classmethod
    def normalize_collection_time(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


class IncidentCreated(APISchema):
    incident_id: str
    status: IncidentStatus = IncidentStatus.OPEN


class EvidenceCreated(APISchema):
    evidence_id: str
    recorded_at: AwareDatetime

    @field_validator("recorded_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


class IncidentResponse(APISchema):
    """Incident fields shared with the retrieval response."""

    incident_id: str
    title: str
    description: str
    discovered_at: AwareDatetime
    reporter_name: str
    status: IncidentStatus = IncidentStatus.OPEN

    @field_validator("discovered_at")
    @classmethod
    def normalize_timestamps(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


class EvidenceResponse(APISchema):
    """Persisted evidence with server-generated identity and recording time."""

    evidence_id: str
    category: EvidenceCategory
    summary: str
    source: str
    collected_at: AwareDatetime
    recorded_at: AwareDatetime

    @field_validator("collected_at", "recorded_at")
    @classmethod
    def normalize_timestamps(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


class MaterialityDecision(StrEnum):
    MATERIAL = "MATERIAL"
    NOT_MATERIAL = "NOT_MATERIAL"


class DecisionCreate(APISchema):
    decision: MaterialityDecision
    determined_at: RequestTimestamp
    decided_by: RequiredText
    rationale: RequiredText
    evidence_ids: list[RequiredText] = Field(min_length=1, strict=True)

    @field_validator("decision", mode="before")
    @classmethod
    def validate_decision(cls, value: object) -> object:
        if value not in ("MATERIAL", "NOT_MATERIAL"):
            raise ValueError("decision must be MATERIAL or NOT_MATERIAL")
        return value

    @field_validator("decided_by", "rationale")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be blank")
        return value

    @field_validator("evidence_ids")
    @classmethod
    def reject_blank_ids(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("evidenceIds must contain nonblank IDs")
        return value

    @field_validator("determined_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


class DecisionDetail(DecisionCreate):
    """Current human decision; deadline is computed by the shared calculator."""

    decision_id: str
    deadline: date | None = None


class DecisionCreated(APISchema):
    decision_id: str
    status: IncidentStatus
    deadline: date | None


class DeadlineState(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PENDING = "PENDING"
    OVERDUE = "OVERDUE"


class DeadlineStatus(APISchema):
    status: DeadlineState
    deadline: date | None
    business_days: int = Field(strict=True, ge=0)


class DeadlineQuery(APISchema):
    """Explicit query alias keeps errors in the public as_of vocabulary."""

    as_of: RequestTimestamp | None = Field(default=None, alias="as_of")


class IncidentDetail(IncidentResponse):
    """Incident, linked evidence and current decision; filings remain Phase 5."""

    evidence: list[EvidenceResponse] = Field(default_factory=list)
    current_decision: DecisionDetail | None = None
    filing: None = None
