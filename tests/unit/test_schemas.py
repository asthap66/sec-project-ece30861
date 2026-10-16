"""Contract validation and serialization tests."""

import pytest
from pydantic import ValidationError

from app.schemas import (
    EvidenceCategory,
    EvidenceCreate,
    EvidenceCreated,
    IncidentCreate,
    IncidentCreated,
    IncidentDetail,
    IncidentStatus,
)


@pytest.mark.parametrize("field", ["title", "description", "discoveredAt", "reporterName"])
def test_missing_incident_fields(incident_payload: dict[str, str], field: str) -> None:
    del incident_payload[field]
    with pytest.raises(ValidationError):
        IncidentCreate.model_validate(incident_payload)


@pytest.mark.parametrize("field", ["title", "description", "reporterName"])
@pytest.mark.parametrize("value", ["", " \t\n", 123, None])
def test_invalid_text(incident_payload: dict[str, str], field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        IncidentCreate.model_validate({**incident_payload, field: value})


@pytest.mark.parametrize("value", ["2020-01-01T10:00:00", "9999-01-01T00:00:00Z", "bad"])
def test_invalid_discovery(incident_payload: dict[str, str], value: str) -> None:
    incident_payload["discoveredAt"] = value
    with pytest.raises(ValidationError):
        IncidentCreate.model_validate(incident_payload)


def test_incident_utc_and_aliases(incident_payload: dict[str, str]) -> None:
    incident_payload["title"] = " Preserved title "
    data = IncidentCreate.model_validate(incident_payload)
    serialized = data.model_dump(mode="json", by_alias=True)
    assert serialized["title"] == " Preserved title "
    assert serialized["discoveredAt"] == "2020-01-01T14:00:00Z"
    assert set(serialized) == set(incident_payload)


@pytest.mark.parametrize("category", list(EvidenceCategory))
def test_categories(evidence_payload: dict[str, str], category: str) -> None:
    evidence_payload["category"] = category
    data = EvidenceCreate.model_validate(evidence_payload)
    assert data.category == category
    assert data.model_dump(mode="json")["collectedAt"] == "2020-01-01T15:00:00Z"
    assert data.summary == " Synthetic finding "


@pytest.mark.parametrize("field", ["category", "summary", "source", "collectedAt"])
def test_missing_evidence(evidence_payload: dict[str, str], field: str) -> None:
    del evidence_payload[field]
    with pytest.raises(ValidationError):
        EvidenceCreate.model_validate(evidence_payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("category", "INVALID"),
        ("summary", ""),
        ("source", "  "),
        ("collectedAt", "2020-01-01T00:00:00"),
        ("collectedAt", "bad"),
    ],
)
def test_invalid_evidence(evidence_payload: dict[str, str], field: str, value: str) -> None:
    evidence_payload[field] = value
    with pytest.raises(ValidationError):
        EvidenceCreate.model_validate(evidence_payload)


def test_future_evidence_is_allowed(evidence_payload: dict[str, str]) -> None:
    evidence_payload["collectedAt"] = "9999-01-01T00:00:00Z"
    assert EvidenceCreate.model_validate(evidence_payload).collected_at.year == 9999


def test_response_shapes(incident_payload: dict[str, str]) -> None:
    assert IncidentCreated(incident_id="INC-example").model_dump(mode="json") == {
        "incidentId": "INC-example",
        "status": "OPEN",
    }
    evidence = EvidenceCreated.model_validate(
        {"evidenceId": "EVD-example", "recordedAt": "2020-01-01T10:00:00-04:00"}
    )
    assert evidence.model_dump(mode="json") == {
        "evidenceId": "EVD-example",
        "recordedAt": "2020-01-01T14:00:00Z",
    }
    detail = IncidentDetail.model_validate({"incidentId": "INC-example", **incident_payload})
    serialized = detail.model_dump(mode="json")
    assert set(serialized) == {
        "incidentId",
        "title",
        "description",
        "discoveredAt",
        "reporterName",
        "status",
        "evidence",
        "currentDecision",
        "filing",
    }
    assert serialized["currentDecision"] is None
    assert serialized["filing"] is None
    assert len(IncidentStatus) == 4


@pytest.mark.parametrize(
    "value",
    [
        1577887200,
        "1577887200",
        "2020-01-01_10:00:00Z",
        "2020-01-01T10:00Z",
        "2020-01-01T10:00:00+0400",
    ],
)
def test_non_contract_timestamp_formats(
    incident_payload: dict[str, str], evidence_payload: dict[str, str], value: object
) -> None:
    with pytest.raises(ValidationError):
        IncidentCreate.model_validate({**incident_payload, "discoveredAt": value})
    with pytest.raises(ValidationError):
        EvidenceCreate.model_validate({**evidence_payload, "collectedAt": value})
