"""Runs the deterministic GUI evidence automation as part of the suite."""

from __future__ import annotations

import hashlib
import json
import shutil

import pytest

CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser")
CATALOG_URL = "https://api.orcarouter.ai/v1/models?capability=chat"


@pytest.mark.skipif(not CHROMIUM, reason="chromium is not installed")
def test_gui_evidence_automation_passes(tmp_path) -> None:
    pytest.importorskip("playwright.sync_api")
    from tests.evidence.run_gui_evidence import run

    manifest = run(tmp_path, CHROMIUM)

    assert manifest["passed"] is True, manifest.get("failed_assertions")
    assert manifest["failed_assertions"] == []

    automation = manifest["automation"]
    assert isinstance(automation, dict)
    assert automation["framework"] == "playwright"
    assert automation["passed"] is True
    assert automation["catalog_source"] == CATALOG_URL
    assert automation["catalog_model_count"] >= 2
    assert 0 <= automation["image_model_count"] <= automation["catalog_model_count"]

    artifacts = {item["kind"]: item for item in manifest["artifacts"]}
    assert set(artifacts) == {"auth-methods", "text-model-dropdown"}

    auth_ui = artifacts["auth-methods"]["ui"]
    for field in ("api_key_visible", "secret_masked", "controls_enabled", "pkce_visible"):
        assert auth_ui[field] is True, field

    dropdown_ui = artifacts["text-model-dropdown"]["ui"]
    assert dropdown_ui["dropdown_open"] is True
    assert dropdown_ui["item_count"] == automation["catalog_model_count"]
    assert dropdown_ui["opaque_background"] is True
    assert dropdown_ui["visible_border"] is True
    assert abs(dropdown_ui["trigger_panel_right_delta"]) <= 2

    for item in artifacts.values():
        path = tmp_path / item["path"]
        assert path.is_file()
        assert item["width"] >= 800 and item["height"] >= 450
        assert item["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert path.stat().st_size >= 10_000

    on_disk = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert on_disk["automation"]["passed"] is True
    assert on_disk["artifacts"] == manifest["artifacts"]
