"""PKCE protocol and connect-flow lifecycle."""

from __future__ import annotations

import base64
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import pytest

from tests.fakes import PLACEHOLDER_CODE, PLACEHOLDER_KEY, AuthStub
from moriarty.providers.orcarouter import (
    MappingVault,
    OrcaConnectManager,
    OrcaExchangeError,
    build_authorize_url,
    challenge_for,
    exchange_code,
    new_state,
    new_verifier,
    resolve_credential,
)


def test_verifier_and_challenge_are_fresh_s256() -> None:
    first = new_verifier()
    second = new_verifier()
    assert first != second
    challenge = challenge_for(first)
    expected = base64.urlsafe_b64encode(hashlib.sha256(first.encode("ascii")).digest()).decode("ascii").rstrip("=")
    assert challenge == expected
    assert "=" not in challenge


def test_authorize_url_uses_auth_origin_and_never_contains_the_verifier() -> None:
    verifier = new_verifier()
    state = new_state()
    url = build_authorize_url(
        "https://www.orcarouter.ai",
        callback_url="http://127.0.0.1:51733/cb",
        verifier=verifier,
        state=state,
    )
    parsed = urllib.parse.urlsplit(url)
    params = urllib.parse.parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "www.orcarouter.ai"
    assert parsed.path == "/auth"
    assert params["code_challenge_method"] == ["S256"]
    assert params["code_challenge"] == [challenge_for(verifier)]
    assert params["state"] == [state]
    assert params["callback_url"] == ["http://127.0.0.1:51733/cb"]
    assert verifier not in url


def test_exchange_posts_to_the_auth_api_path_with_the_verifier_in_the_body() -> None:
    with AuthStub() as stub:
        verifier = new_verifier()
        result = exchange_code(stub.base, code=PLACEHOLDER_CODE, verifier=verifier)
        assert result["key"] == PLACEHOLDER_KEY
        assert result["scope"] == "api"
        assert len(stub.requests) == 1
        request = stub.requests[0]
        assert request["path"] == "/api/v1/auth/keys"
        body = json.loads(request["body"])
        assert body["code"] == PLACEHOLDER_CODE
        assert body["code_verifier"] == verifier
        assert body["code_challenge_method"] == "S256"


def test_exchange_never_uses_the_inference_auth_path() -> None:
    with AuthStub() as stub:
        exchange_code(stub.base, code=PLACEHOLDER_CODE, verifier=new_verifier())
        assert all("/v1/auth/keys" not in request["path"] or request["path"].startswith("/api/v1/auth/keys") for request in stub.requests)


def test_exchange_reports_reused_code_without_leaking_the_verifier() -> None:
    with AuthStub() as stub:
        stub.status = 403
        stub.payload = {"error": "invalid_grant", "error_description": "code already used"}
        verifier = new_verifier()
        with pytest.raises(OrcaExchangeError) as caught:
            exchange_code(stub.base, code=PLACEHOLDER_CODE, verifier=verifier)
        assert verifier not in str(caught.value)
        assert exc_status(caught.value) == 403


def exc_status(error: OrcaExchangeError) -> int | None:
    return error.status


def _start(manager: OrcaConnectManager) -> tuple[str, str, str]:
    payload = manager.start()
    url = urllib.parse.urlsplit(payload["authorize_url"])
    state = urllib.parse.parse_qs(url.query)["state"][0]
    callback = urllib.parse.parse_qs(url.query)["callback_url"][0]
    return payload["attempt_id"], state, callback


def _wait(manager: OrcaConnectManager, attempt_id: str, timeout: float = 8.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = manager.status(attempt_id)
        if status["status"] != "pending":
            return status
        time.sleep(0.05)
    raise AssertionError("connect attempt did not settle")


def test_manager_completes_flow_a_and_persists_a_pkce_credential() -> None:
    with AuthStub() as stub:
        vault = MappingVault({})
        manager = OrcaConnectManager(vault, auth_base=stub.base)
        attempt_id, state, callback = _start(manager)
        urllib.request.urlopen(f"{callback}?code={PLACEHOLDER_CODE}&state={state}", timeout=5).read()
        status = _wait(manager, attempt_id)
        assert status["status"] == "success"
        credential = resolve_credential(vault)
        assert credential is not None
        assert credential.source == "pkce"
        assert credential.account_id == "user-123"
        assert credential.scope == "api"
        assert PLACEHOLDER_KEY not in json.dumps(status)


def test_manager_rejects_a_state_mismatch_before_exchange() -> None:
    with AuthStub() as stub:
        vault = MappingVault({})
        manager = OrcaConnectManager(vault, auth_base=stub.base)
        attempt_id, _state, callback = _start(manager)
        with pytest.raises(urllib.error.HTTPError):
            urllib.request.urlopen(f"{callback}?code={PLACEHOLDER_CODE}&state=wrong", timeout=5).read()
        status = _wait(manager, attempt_id)
        assert status["status"] == "error"
        assert stub.requests == []
        assert resolve_credential(vault) is None


def test_manager_handles_denial() -> None:
    with AuthStub() as stub:
        manager = OrcaConnectManager(MappingVault({}), auth_base=stub.base)
        attempt_id, state, callback = _start(manager)
        urllib.request.urlopen(f"{callback}?error=access_denied&state={state}", timeout=5).read()
        status = _wait(manager, attempt_id)
        assert status["status"] == "denied"
        assert "denied" in status["error"].lower()


def test_scope_downgrade_is_refused_and_nothing_is_stored() -> None:
    with AuthStub() as stub:
        stub.payload = {"key": PLACEHOLDER_KEY, "user_id": "user-1", "scope": "connector"}
        vault = MappingVault({})
        manager = OrcaConnectManager(vault, auth_base=stub.base)
        attempt_id, state, callback = _start(manager)
        urllib.request.urlopen(f"{callback}?code={PLACEHOLDER_CODE}&state={state}", timeout=5).read()
        status = _wait(manager, attempt_id)
        assert status["status"] == "error"
        assert "connector" in status["error"]
        assert resolve_credential(vault) is None


def test_rate_limit_message_is_actionable() -> None:
    with AuthStub() as stub:
        stub.status = 429
        stub.payload = {"error": "rate_limited", "error_description": "too many"}
        manager = OrcaConnectManager(MappingVault({}), auth_base=stub.base)
        attempt_id, state, callback = _start(manager)
        urllib.request.urlopen(f"{callback}?code={PLACEHOLDER_CODE}&state={state}", timeout=5).read()
        status = _wait(manager, attempt_id)
        assert status["status"] == "error"
        assert "10 keys" in status["error"]


def test_network_failure_settles_instead_of_hanging() -> None:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        dead_port = sock.getsockname()[1]
    manager = OrcaConnectManager(MappingVault({}), auth_base=f"http://127.0.0.1:{dead_port}")
    attempt_id, state, callback = _start(manager)
    urllib.request.urlopen(f"{callback}?code={PLACEHOLDER_CODE}&state={state}", timeout=5).read()
    status = _wait(manager, attempt_id)
    assert status["status"] == "error"
    assert "authorization" in status["error"].lower()


def test_explicit_cancel_releases_the_attempt() -> None:
    with AuthStub() as stub:
        manager = OrcaConnectManager(MappingVault({}), auth_base=stub.base)
        attempt_id, _state, _callback = _start(manager)
        assert manager.cancel(attempt_id) is True
        status = manager.status(attempt_id)
        assert status["status"] == "cancelled"
        assert manager.cancel("missing") is False
