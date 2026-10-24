"""Model discovery, capability filtering and outage fallback."""

from __future__ import annotations

import json
import urllib.error

import pytest

from tests.fakes import CATALOG, OrcaStub
from moriarty.providers.orcarouter import (
    DEFAULT_MODEL,
    FALLBACK_MODEL,
    annotate_models,
    discover_models,
    filter_models,
    normalise_model,
    parse_catalog,
    provider_registry,
    seed_models,
)


def test_registry_exposes_a_named_cyber_provider() -> None:
    entry = provider_registry()[0]
    assert entry["id"] == "orcarouter"
    assert entry["display_name"] == "OrcaRouter Cyber Inference"
    assert entry["base_url"] == "https://api.orcarouter.ai/v1"
    assert entry["auth_methods"] == ["api_key", "pkce"]
    assert entry["default_model"] == DEFAULT_MODEL
    assert entry["fallback_model"] == FALLBACK_MODEL
    assert entry["model_discovery_url"] == "https://api.orcarouter.ai/v1/models"


def test_parse_catalog_preserves_vendor_namespace_and_metadata() -> None:
    models = parse_catalog(CATALOG)
    by_id = {model["id"]: model for model in models}
    assert "orca/orcacyber-ultra-1.0" in by_id
    assert by_id["openai/gpt-5.5"]["context_length"] == 400000
    assert by_id["openai/gpt-5.5"]["reasoning"]["efforts"] == ["low", "medium", "high", "xhigh"]
    assert by_id["google/gemini-3.5-flash"]["input_modalities"] == ["audio", "image", "text"]


def test_chat_filter_excludes_non_text_endpoint_models() -> None:
    ids = {model["id"] for model in filter_models(parse_catalog(CATALOG), "chat")}
    assert "orcarouter/auto" in ids
    assert "openai/gpt-5.5" in ids
    assert "openai/text-embedding-3-large" not in ids
    assert "openai/gpt-image-1" not in ids
    assert "openai/sora-2" not in ids
    assert "jina/jina-reranker-v3" not in ids


def test_models_without_declared_endpoints_fail_closed() -> None:
    assert filter_models([{"id": "mystery/model"}], "chat") == []


def test_multimodal_filter_requires_an_explicit_input_modality() -> None:
    models = parse_catalog(CATALOG)
    image_ids = {model["id"] for model in filter_models(models, "multimodal", "image")}
    audio_ids = {model["id"] for model in filter_models(models, "multimodal", "audio")}
    video_ids = {model["id"] for model in filter_models(models, "multimodal", "video")}
    assert image_ids == {"google/gemini-3.5-flash"}
    assert audio_ids == {"google/gemini-3.5-flash"}
    assert video_ids == set()


def test_each_capability_uses_its_own_endpoint_type() -> None:
    models = parse_catalog(CATALOG)
    assert [m["id"] for m in filter_models(models, "embedding")] == ["openai/text-embedding-3-large"]
    assert [m["id"] for m in filter_models(models, "image")] == ["openai/gpt-image-1"]
    assert [m["id"] for m in filter_models(models, "video")] == ["openai/sora-2"]
    assert [m["id"] for m in filter_models(models, "rerank")] == ["jina/jina-reranker-v3"]
    with pytest.raises(ValueError):
        filter_models(models, "telepathy")


def test_live_discovery_uses_the_inference_origin_and_bearer_auth() -> None:
    with OrcaStub() as stub:
        result = discover_models("sk-orca-" + "placeholder", capability="chat", api_base=stub.base)
        assert result.source == "live"
        assert result.degraded is False
        assert result.error is None
        assert result.models and result.models[0]["id"] == DEFAULT_MODEL
        request = stub.requests[0]
        assert request["path"] == "/v1/models?capability=chat"
        assert request["headers"]["Authorization"].startswith("Bearer sk-orca-")


def test_default_and_fallback_roles_survive_live_discovery() -> None:
    with OrcaStub() as stub:
        result = discover_models("sk-orca-" + "placeholder", api_base=stub.base)
        roles = {model["id"]: model for model in result.models}
        assert roles[DEFAULT_MODEL]["default"] is True
        assert roles[FALLBACK_MODEL]["fallback"] is True
        assert roles["orca/orcacyber-ultra-1.0"]["recommended_for_security_teams"] is True
        assert result.models[0]["id"] == DEFAULT_MODEL


def test_discovery_failure_falls_back_to_the_verified_seed() -> None:
    with OrcaStub() as stub:
        stub.chat_status = 200
        result = discover_models("sk-orca-" + "placeholder", api_base="http://127.0.0.1:1/v1")
        assert result.source == "fallback"
        assert result.degraded is True
        assert result.error
        assert [model["id"] for model in result.models] == [
            "orcarouter/auto", "orca/orcacyber-ultra-1.0", "orca/orcacyber-zero-1.5", "orcarouter/fusion",
        ]
        assert all(model["verified"] for model in result.models)


def test_no_key_returns_the_seed_without_calling_the_network() -> None:
    result = discover_models(None)
    assert result.source == "fallback"
    assert result.degraded is True
    assert "No OrcaRouter API key" in result.error


def test_seed_metadata_is_preserved() -> None:
    seed = seed_models("chat")
    assert {model["id"] for model in seed} == {
        "orcarouter/auto", "orca/orcacyber-ultra-1.0", "orca/orcacyber-zero-1.5", "orcarouter/fusion",
    }
    assert all(model["architecture"]["input_modalities"] == ["text"] for model in seed)


def test_annotate_puts_the_default_first_and_keeps_ids_verbatim() -> None:
    models = [normalise_model({"id": "zzz/model", "supported_endpoint_types": ["openai"], "architecture": {"input_modalities": ["text"]}}) for _ in range(1)]
    annotated = annotate_models([models[0], normalise_model({"id": DEFAULT_MODEL, "supported_endpoint_types": ["openai"], "architecture": {"input_modalities": ["text"]}})])
    assert annotated[0]["id"] == DEFAULT_MODEL
    assert annotated[0]["default"] is True
    assert all(":" not in model["id"] for model in annotated)


def test_catalog_response_is_bounded_to_the_advertised_item_count() -> None:
    payload = {"data": [{"id": f"vendor/model-{index}", "supported_endpoint_types": ["openai"], "architecture": {"input_modalities": ["text"]}} for index in range(800)]}
    assert len(parse_catalog(payload)) == 500
