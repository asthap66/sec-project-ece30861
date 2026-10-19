"""Tester endpoints (course spec, Tester section and Execution rules).

The target system is simulated with httpx.MockTransport; the suite run itself
is replaced by a stub, so these tests need no network.
"""

from collections.abc import Callable, Iterator
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

import tester.main as tester_main
from tester.runner import SuiteRun

TARGET = "https://system.example.edu/system"


@pytest.fixture
def system_response(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    """Control what the simulated system's /test/setup answers."""
    state: dict[str, Any] = {"status": 201, "echo": True, "body": None, "calls": []}

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        sent = json.loads(request.content)
        state["calls"].append((str(request.url), request.headers.get("X-API-Key"), sent))
        if state["body"] is not None:
            return httpx.Response(state["status"], json=state["body"])
        return httpx.Response(
            state["status"], json={"session_id": sent["session_id"] if state["echo"] else "other"}
        )

    def client(timeout: float) -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=timeout)

    monkeypatch.setattr(tester_main, "_http_client", client)
    monkeypatch.setenv("ALLOWED_TARGETS", TARGET)
    monkeypatch.setenv("TARGET_API_KEY", "target-key")
    tester_main._sessions.clear()
    yield state
    tester_main._sessions.clear()


@pytest.fixture
def stub_suite(monkeypatch: pytest.MonkeyPatch) -> Callable[[str | None], None]:
    def install(aborted: str | None = None) -> None:
        planned = ["tests/acceptance/x.py::test_ac01_a", "tests/acceptance/x.py::test_ac02_b"]
        records = {planned[0]: {"nodeid": planned[0], "outcome": "passed"}}
        if not aborted:
            records[planned[1]] = {
                "nodeid": planned[1],
                "outcome": "failed",
                "message": "assert 400 == 201",
                "exception": "AssertionError",
            }
        monkeypatch.setattr(
            tester_main,
            "run_suite",
            lambda *a: SuiteRun(planned=planned, records=records, aborted=aborted),
        )
        monkeypatch.setattr(
            tester_main, "code_coverage", lambda *a: {"covered": 1, "total": 2, "basis": "lines"}
        )

    return install


client = TestClient(tester_main.app)


def setup_session() -> str:
    response = client.post("/test/setup", json={"target_url": TARGET})
    assert response.status_code == 201, response.text
    return str(response.json()["session_id"])


def test_setup_creates_a_uuid_session_and_prepares_the_target(
    system_response: dict[str, Any],
) -> None:
    session_id = setup_session()
    assert len(session_id) == 36
    url, key, sent = system_response["calls"][0]
    assert url == TARGET + "/test/setup" and key == "target-key"
    assert sent == {"session_id": session_id, "setup": {}}


@pytest.mark.parametrize(
    "target",
    [
        "https://evil.example.com",
        "ftp://x",
        TARGET + "?a=1",
        TARGET + "/test",
        "",
        5,
    ],
    ids=["not-approved", "not-http", "query", "test-suffix", "empty", "number"],
)
def test_bad_target_is_400(system_response: dict[str, Any], target: object) -> None:
    response = client.post("/test/setup", json={"target_url": target})
    assert response.status_code == 400 and response.json()["source"] == "tester"
    assert system_response["calls"] == []  # never contacted


def test_system_setup_failure_is_forwarded_unchanged(system_response: dict[str, Any]) -> None:
    system_response.update(status=500, body={"message": "DB down", "source": "system"})
    response = client.post("/test/setup", json={"target_url": TARGET})
    assert response.status_code == 500
    assert response.json() == {"message": "DB down", "source": "system"}
    assert tester_main._sessions == {}  # failed setup: no runnable session


def test_wrong_session_id_from_system_is_rejected(system_response: dict[str, Any]) -> None:
    system_response["echo"] = False
    assert client.post("/test/setup", json={"target_url": TARGET}).status_code == 500


def test_unreachable_system_is_a_communication_error(
    monkeypatch: pytest.MonkeyPatch, system_response: dict[str, Any]
) -> None:
    def broken(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    monkeypatch.setattr(
        tester_main,
        "_http_client",
        lambda timeout: httpx.AsyncClient(transport=httpx.MockTransport(broken), timeout=timeout),
    )
    response = client.post("/test/setup", json={"target_url": TARGET})
    assert response.status_code == 500 and response.json()["source"] == "communication"


def test_run_returns_and_stores_the_report(
    system_response: dict[str, Any], stub_suite: Callable[[str | None], None]
) -> None:
    stub_suite(None)
    session_id = setup_session()
    assert client.get(f"/test/report?session_id={session_id}").status_code == 409  # not run yet
    response = client.post("/test/run", json={"session_id": session_id})
    assert response.status_code == 200
    report = response.json()
    assert [r["outcome"] for r in report["results"]] == ["pass", "fail"]
    stored = client.get(f"/test/report?session_id={session_id}")
    assert stored.status_code == 200 and stored.json() == report


def test_a_session_runs_once(
    system_response: dict[str, Any], stub_suite: Callable[[str | None], None]
) -> None:
    stub_suite(None)
    session_id = setup_session()
    assert client.post("/test/run", json={"session_id": session_id}).status_code == 200
    again = client.post("/test/run", json={"session_id": session_id})
    assert again.status_code == 409 and again.json()["source"] == "tester"


def test_abort_returns_500_and_keeps_available_results(
    system_response: dict[str, Any], stub_suite: Callable[[str | None], None]
) -> None:
    stub_suite("the suite exceeded the run limit")
    session_id = setup_session()
    response = client.post("/test/run", json={"session_id": session_id})
    assert response.status_code == 500 and response.json()["source"] == "tester"
    stored = client.get(f"/test/report?session_id={session_id}").json()
    assert [(r["outcome"], r.get("source")) for r in stored["results"]] == [
        ("pass", None),
        ("error", "tester"),
    ]
    assert client.post("/test/run", json={"session_id": session_id}).status_code == 409


@pytest.mark.parametrize(
    ("method", "path", "body", "status"),
    [
        ("post", "/test/run", {"session_id": "nope"}, 404),
        ("post", "/test/run", {}, 400),
        ("get", "/test/report?session_id=nope", None, 404),
        ("get", "/test/report", None, 400),
    ],
)
def test_bad_requests(
    system_response: dict[str, Any], method: str, path: str, body: object, status: int
) -> None:
    response = client.post(path, json=body) if method == "post" else client.get(path)
    assert response.status_code == status
    assert response.json()["source"] == "tester" and response.json()["message"]
