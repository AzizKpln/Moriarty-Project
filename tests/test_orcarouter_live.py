"""Live OrcaRouter connectivity through this repository's provider code.

Skipped unless ORCAROUTER_API_KEY is present.  The cyber catalog is tried
first; when our verification key is not unlocked for it, the test falls back
to a public model that the same key can call, which still proves the provider
wiring end to end.
"""

from __future__ import annotations

import os

import pytest

from moriarty.providers.orcarouter import (
    DEFAULT_MODEL,
    OrcaRouterClient,
    OrcaRouterError,
    discover_models,
)

API_KEY = (os.environ.get("ORCAROUTER_API_KEY") or "").strip()

pytestmark = pytest.mark.skipif(not API_KEY, reason="ORCAROUTER_API_KEY is not configured")

VERIFICATION_MODEL = "deepseek/deepseek-v4.1-flash"


def test_live_model_catalog_is_reachable_and_namespaced() -> None:
    result = discover_models(API_KEY, capability="chat", timeout=20)
    assert result.source == "live", result.error
    assert result.degraded is False
    assert len(result.models) > 0
    ids = [model["id"] for model in result.models]
    assert DEFAULT_MODEL in ids
    assert all("/" in model_id for model_id in ids)


def test_live_chat_completion_through_the_provider_client() -> None:
    model = "orca/orcacyber-ultra-1.0"
    try:
        client = OrcaRouterClient(API_KEY, model=model, timeout=45)
        content = client.complete(
            [{"role": "user", "content": 'Reply with a JSON object: {"ok": true}'}],
            response_format={"type": "json_object"},
        )
    except OrcaRouterError as exc:
        if "HTTP 4" not in str(exc):
            raise
        # Verification key not unlocked for the cyber tier: prove the same
        # provider path with a public model.
        client = OrcaRouterClient(API_KEY, model=VERIFICATION_MODEL, timeout=45)
        content = client.complete(
            [{"role": "user", "content": 'Reply with a JSON object: {"ok": true}'}],
            response_format={"type": "json_object"},
        )
        model = VERIFICATION_MODEL
    assert content.strip()
    assert client.model == model
