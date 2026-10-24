"""Web-app wiring: config masking, catalog endpoint, dual-credential inference."""

from __future__ import annotations

import json
from pathlib import Path

from tests.fakes import CATALOG, PLACEHOLDER_KEY, OrcaStub, http_json, run_app

KEY = PLACEHOLDER_KEY


def write_config(data_dir: Path, payload: dict) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "configuration.json").write_text(json.dumps(payload), encoding="utf-8")


def test_provider_endpoint_exposes_the_named_cyber_provider(tmp_path: Path) -> None:
    with run_app(tmp_path) as base:
        status, payload = http_json(base + "/api/ai/providers")
        assert status == 200
        provider = payload["providers"][0]
        assert provider["display_name"] == "OrcaRouter Cyber Inference"
        assert provider["auth_methods"] == ["api_key", "pkce"]
        assert provider["base_url"] == "https://api.orcarouter.ai/v1"
        assert provider["docs_url"] == "https://www.orcarouter.ai/cyber"
        assert provider["model_catalog_url"] == "https://www.orcarouter.ai/models?tier=cyber"


def test_public_config_never_returns_the_secret(tmp_path: Path) -> None:
    with run_app(tmp_path) as base:
        status, saved = http_json(base + "/api/config", method="POST", body={"orcarouter_api_key": KEY, "ai_provider": "orcarouter"})
        assert status == 200
        assert saved["orcarouter"]["configured"] is True
        assert saved["orcarouter"]["credential_source"] == "api_key"
        assert KEY not in json.dumps(saved)
        status, fetched = http_json(base + "/api/config")
        assert KEY not in json.dumps(fetched)
        global_config = tmp_path / "configuration.json"
        assert global_config.exists()


def test_config_rejects_a_key_without_the_orcarouter_prefix(tmp_path: Path) -> None:
    with run_app(tmp_path) as base:
        status, payload = http_json(base + "/api/config", method="POST", body={"orcarouter_api_key": "sk-test-wrong"})
        assert status == 400
        assert "sk-orca-" in payload["error"]


def test_clear_credential_endpoint_removes_the_key(tmp_path: Path) -> None:
    with run_app(tmp_path) as base:
        http_json(base + "/api/config", method="POST", body={"orcarouter_api_key": KEY})
        status, payload = http_json(base + "/api/ai/credentials", method="POST", body={"method": "clear"})
        assert status == 200
        assert payload["orcarouter"]["configured"] is False
        stored = json.loads((tmp_path / "configuration.json").read_text())
        assert "orcarouter_api_key" not in stored


def test_model_catalog_comes_from_the_live_api_with_capability_filtering(tmp_path: Path) -> None:
    write_config(tmp_path, {"orcarouter_api_key": KEY, "ai_provider": "orcarouter"})
    with OrcaStub() as stub, run_app(tmp_path, env={"ORCA_API_BASE_URL": stub.base}) as base:
        status, payload = http_json(base + "/api/ai/models?provider=orcarouter&capability=chat")
        assert status == 200
        assert payload["source"] == "live"
        assert payload["degraded"] is False
        ids = [model["id"] for model in payload["models"]]
        assert ids[0] == "orcarouter/auto"
        assert "google/gemini-3.5-flash" in ids
        assert "openai/text-embedding-3-large" not in ids
        assert "openai/gpt-image-1" not in ids
        assert payload["catalog_url"] == stub.base + "/models?capability=chat"
        assert any(request["path"] == "/v1/models?capability=chat" for request in stub.requests)


def test_multimodal_endpoint_fails_closed_without_a_modality(tmp_path: Path) -> None:
    write_config(tmp_path, {"orcarouter_api_key": KEY})
    with OrcaStub() as stub, run_app(tmp_path, env={"ORCA_API_BASE_URL": stub.base}) as base:
        status, payload = http_json(base + "/api/ai/models?provider=orcarouter&capability=multimodal")
        assert status == 400
        status, payload = http_json(base + "/api/ai/models?provider=orcarouter&capability=multimodal&modality=image")
        assert status == 200
        assert [model["id"] for model in payload["models"]] == ["google/gemini-3.5-flash"]


def test_catalog_outage_returns_a_labelled_fallback_seed(tmp_path: Path) -> None:
    write_config(tmp_path, {"orcarouter_api_key": KEY})
    with run_app(tmp_path, env={"ORCA_API_BASE_URL": "http://127.0.0.1:1/v1"}) as base:
        status, payload = http_json(base + "/api/ai/models?provider=orcarouter&capability=chat")
        assert status == 200
        assert payload["source"] == "fallback"
        assert payload["degraded"] is True
        assert payload["error"]
        assert {model["id"] for model in payload["models"]} == {
            "orcarouter/auto", "orca/orcacyber-ultra-1.0", "orca/orcacyber-zero-1.5", "orcarouter/fusion",
        }
        assert all(model["verified"] for model in payload["models"])


def _create_investigation(base: str) -> str:
    status, payload = http_json(base + "/api/investigations", method="POST", body={"title": "Test case", "subject": "+15555550100"})
    assert status == 201
    return payload["id"]


def test_api_key_credential_routes_case_analysis_through_orcarouter(tmp_path: Path) -> None:
    write_config(tmp_path, {"orcarouter_api_key": KEY, "ai_provider": "orcarouter"})
    with OrcaStub() as stub, run_app(tmp_path, env={"ORCA_API_BASE_URL": stub.base}) as base:
        investigation_id = _create_investigation(base)
        status, payload = http_json(base + f"/api/investigations/{investigation_id}/analysis", method="POST", body={"language": "en"})
        assert status == 200
        assert payload["analysis"]["method"] == "orcarouter_evidence_analysis"
        chat = next(request for request in stub.requests if request["path"] == "/v1/chat/completions")
        body = json.loads(chat["body"])
        assert body["model"] == "orcarouter/auto"
        assert chat["headers"]["Authorization"] == f"Bearer {KEY}"


def test_pkce_credential_routes_inference_identically(tmp_path: Path) -> None:
    write_config(tmp_path, {
        "orcarouter_api_key": KEY,
        "orcarouter_credential_source": "pkce",
        "orcarouter_credential_generation": 4,
        "orcarouter_account_id": "user-4",
        "orcarouter_scope": "api",
        "ai_provider": "orcarouter",
        "orcarouter_model": "orca/orcacyber-ultra-1.0",
    })
    with OrcaStub() as stub, run_app(tmp_path, env={"ORCA_API_BASE_URL": stub.base}) as base:
        investigation_id = _create_investigation(base)
        status, payload = http_json(base + f"/api/investigations/{investigation_id}/analysis", method="POST", body={"language": "en"})
        assert status == 200
        chat = next(request for request in stub.requests if request["path"] == "/v1/chat/completions")
        body = json.loads(chat["body"])
        assert body["model"] == "orca/orcacyber-ultra-1.0"
        assert chat["headers"]["Authorization"] == f"Bearer {KEY}"


def test_terminal_401_marks_only_the_rejected_generation_for_reauth(tmp_path: Path) -> None:
    write_config(tmp_path, {
        "orcarouter_api_key": KEY,
        "orcarouter_credential_generation": 7,
        "ai_provider": "orcarouter",
    })
    with OrcaStub() as stub, run_app(tmp_path, env={"ORCA_API_BASE_URL": stub.base}) as base:
        stub.chat_status = 401
        investigation_id = _create_investigation(base)
        status, payload = http_json(base + f"/api/investigations/{investigation_id}/analysis", method="POST", body={"language": "en"})
        assert status == 502
        assert "sign in again" in payload["error"].lower()
        status, config = http_json(base + "/api/config")
        assert config["orcarouter"]["needs_reauth"] is True
        assert config["orcarouter"]["configured"] is True  # the old secret is kept until replacement
