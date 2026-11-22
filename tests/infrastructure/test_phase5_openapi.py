"""Compare generated Phase 5 OpenAPI with Astha's documented public handoff."""

from typing import Any

import pytest

from app.main import app

pytestmark = pytest.mark.phase5

OPERATIONS = [
    (
        "/incidents/{incidentId}/corrections",
        "post",
        "CorrectionCreate",
        "201",
        "DecisionCreated",
        {"correctsDecisionId", "decision", "determinedAt", "decidedBy", "rationale", "evidenceIds"},
        {"decisionId", "status", "deadline"},
    ),
    (
        "/incidents/{incidentId}/filing",
        "post",
        "FilingCreate",
        "201",
        "FilingCreated",
        {"filedAt", "accessionNumber"},
        {"filingId", "status", "timeliness", "businessDaysLate"},
    ),
    (
        "/incidents/{incidentId}/timeline",
        "get",
        None,
        "200",
        "IncidentTimeline",
        set(),
        {"incidentId", "events", "evidenceCounts", "discoveryToDeterminationDays"},
    ),
]


def _schema_name(reference: dict[str, Any]) -> str:
    return str(reference["$ref"]).removeprefix("#/components/schemas/")


@pytest.mark.parametrize("operation", OPERATIONS, ids=["corrections", "filing", "timeline"])
def test_phase5_openapi_operation_shape(operation: tuple[Any, ...]) -> None:
    path, method, request_name, success_status, response_name, request_fields, response_fields = (
        operation
    )
    document = app.openapi()
    route = document["paths"][path][method]
    assert "ApiKey" in document["components"]["securitySchemes"]
    assert document["security"] == [{"ApiKey": []}]
    assert any(parameter["name"] == "incidentId" for parameter in route["parameters"])
    required_errors = {"401", "404"} if method == "get" else {"400", "401", "404", "409"}
    assert required_errors <= set(route["responses"])
    response_ref = route["responses"][success_status]["content"]["application/json"]["schema"]
    assert _schema_name(response_ref) == response_name
    response = document["components"]["schemas"][response_name]
    assert set(response["required"]) == response_fields
    if request_name is None:
        assert "requestBody" not in route
    else:
        request_ref = route["requestBody"]["content"]["application/json"]["schema"]
        assert _schema_name(request_ref) == request_name
        request = document["components"]["schemas"][request_name]
        assert set(request["required"]) == request_fields


def test_phase5_openapi_timeline_and_filing_details() -> None:
    schemas = app.openapi()["components"]["schemas"]
    assert set(schemas["HistoryEvent"]["required"]) == {"eventType", "recordedAt", "referenceId"}
    assert set(schemas["EvidenceCounts"]["required"]) == {
        "technical",
        "businessImpact",
        "legal",
        "other",
    }
    assert set(schemas["FilingDetail"]["required"]) == {
        "filedAt",
        "accessionNumber",
        "filingId",
        "timeliness",
        "businessDaysLate",
    }
    assert set(schemas["HistoryEventType"]["enum"]) == {
        "INCIDENT_CREATED",
        "EVIDENCE_ADDED",
        "DECISION_RECORDED",
        "DECISION_CORRECTED",
        "FILING_RECORDED",
    }
