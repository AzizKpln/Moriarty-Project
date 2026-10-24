"""Deterministic GUI evidence for the OrcaRouter Cyber Inference provider.

The real web workspace is started on loopback against a temporary data
directory.  ``/api/ai/models`` is pointed at a loopback stub that serves the
documented ``GET /v1/models?capability=chat`` response shape, so the evidence
run needs neither a live account nor network access while still exercising the
production provider code path, the production endpoints, and the production
UI (``orca-settings.js`` / ``orca-settings.css``).

Playwright drives headless Chromium at 1280x900 and asserts the dual-auth
controls, the masked secret, and the model dropdown geometry before writing:

    orca-evidence/auth-methods.png
    orca-evidence/text-model-dropdown.png
    orca-evidence/manifest.json

Exit code is non-zero when any assertion fails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright  # noqa: E402

from tests.fakes import PLACEHOLDER_KEY, OrcaStub, http_json, run_app  # noqa: E402

CATALOG_SOURCE = "https://api.orcarouter.ai/v1/models?capability=chat"
CATALOG_SOURCE_NOTE = (
    "Production requests go to https://api.orcarouter.ai/v1/models?capability=chat. "
    "This run uses a loopback stub serving that documented response shape so the "
    "evidence is reproducible without a live credential; the same URL is exercised "
    "against the real service by tests/test_orcarouter_live.py."
)
DEFAULT_VIEWPORT = {"width": 1280, "height": 900}
MIN_SCREENSHOT = {"width": 800, "height": 450}

CHECKS: dict[str, dict[str, Any]] = {}


def record(name: str, passed: bool, value: Any, detail: str) -> None:
    CHECKS[name] = {"passed": bool(passed), "value": value, "detail": detail}


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    return int(width), int(height)


def screenshot_entry(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    width, height = png_dimensions(path)
    if width < MIN_SCREENSHOT["width"] or height < MIN_SCREENSHOT["height"]:
        raise ValueError(f"{path.name} is {width}x{height}, below the required 800x450")
    return {
        "file": path.name,
        "path": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": width,
        "height": height,
        "bytes": len(data),
    }


def dialog_bounds(page: Any) -> dict[str, float]:
    return page.evaluate(
        """() => {
            const r = document.querySelector('#setupDialog').getBoundingClientRect();
            return {top: r.top, bottom: r.bottom, left: r.left, right: r.right};
        }"""
    )


def scroll_card_into_view(page: Any) -> None:
    page.evaluate(
        """() => {
            const dialog = document.querySelector('#setupDialog');
            const card = document.querySelector('#orcarouterCard');
            const delta = card.getBoundingClientRect().top - dialog.getBoundingClientRect().top;
            dialog.scrollTop += delta - 84;
        }"""
    )
    page.wait_for_timeout(150)


def check_auth_methods(page: Any) -> None:
    api_key = page.evaluate(
        """() => {
            const panel = document.querySelector('#orcaApiKeyPanel');
            const input = document.querySelector('#orcaApiKey');
            const pkce = document.querySelector('#orcaPkcePanel');
            const connect = document.querySelector('#orcaConnect');
            const clear = document.querySelector('#orcaClearKey');
            const trigger = document.querySelector('#orcaModelTrigger');
            const provider = document.querySelector('#aiProvider');
            const rect = input.getBoundingClientRect();
            const pkceRect = pkce.getBoundingClientRect();
            const dialog = document.querySelector('#setupDialog').getBoundingClientRect();
            const visible = (r) => r.width > 0 && r.height > 0 && r.top < dialog.bottom && r.bottom > dialog.top;
            return {
                panelVisible: !panel.hidden && visible(rect),
                inputType: input.type,
                inputValuePresent: input.value.length > 0,
                valueLeakedToText: document.body.innerText.includes(input.value),
                pkceVisible: !pkce.hidden && visible(pkceRect),
                pkceText: pkce.innerText,
                connectEnabled: !connect.disabled,
                clearEnabled: !clear.disabled,
                triggerEnabled: !trigger.disabled,
                providerEnabled: !provider.disabled,
                providerValue: provider.value,
            };
        }"""
    )
    record(
        "api_key_visible",
        api_key["panelVisible"],
        api_key["panelVisible"],
        "The API-key panel and its input are visible inside the setup dialog.",
    )
    record(
        "secret_masked",
        api_key["inputType"] == "password" and api_key["inputValuePresent"] and not api_key["valueLeakedToText"],
        True,
        "The key input is type=password, holds the value, and never appears as page text.",
    )
    record(
        "controls_enabled",
        bool(api_key["connectEnabled"] and api_key["clearEnabled"] and api_key["triggerEnabled"] and api_key["providerEnabled"]),
        True,
        "Provider switch, PKCE connect, clear-key and model trigger are all enabled.",
    )
    record(
        "pkce_visible",
        bool(api_key["pkceVisible"] and "PKCE (S256)" in api_key["pkceText"]),
        True,
        "The PKCE panel states PKCE (S256) and is visible next to the API-key method.",
    )
    if api_key["providerValue"] != "orcarouter":
        raise AssertionError("provider select did not switch to orcarouter")


def check_dropdown(page: Any) -> None:
    metrics = page.evaluate(
        """() => {
            const trigger = document.querySelector('#orcaModelTrigger');
            const panel = document.querySelector('#orcaModelPanel');
            const options = [...document.querySelectorAll('.orca-model-option')];
            const tr = trigger.getBoundingClientRect();
            const pr = panel.getBoundingClientRect();
            const dialog = document.querySelector('#setupDialog').getBoundingClientRect();
            const style = getComputedStyle(panel);
            const color = style.backgroundColor;
            const alpha = (() => {
                const match = color.match(/rgba?\\(([^)]+)\\)/);
                if (!match) return 1;
                const parts = match[1].split(',').map((part) => parseFloat(part));
                return parts.length === 4 ? parts[3] : 1;
            })();
            const borderColor = style.borderTopColor;
            const borderAlpha = (() => {
                const match = borderColor.match(/rgba?\\(([^)]+)\\)/);
                if (!match) return 1;
                const parts = match[1].split(',').map((part) => parseFloat(part));
                return parts.length === 4 ? parts[3] : 1;
            })();
            return {
                expanded: trigger.getAttribute('aria-expanded') === 'true',
                hidden: panel.hidden,
                optionCount: options.length,
                optionIds: options.map((option) => option.dataset.modelId),
                backgroundColor: color,
                backgroundAlpha: alpha,
                borderWidth: parseFloat(style.borderTopWidth),
                borderColor: borderColor,
                borderAlpha: borderAlpha,
                triggerRight: tr.right,
                panelRight: pr.right,
                panelTop: pr.top,
                panelBottom: pr.bottom,
                dialogTop: dialog.top,
                dialogBottom: dialog.bottom,
                panelWidth: pr.width,
                triggerWidth: tr.width,
                label: document.querySelector('#orcaModelLabel').textContent,
                catalogStatus: document.querySelector('#orcaCatalogStatus').textContent,
                fullyVisible: pr.top >= dialog.top - 0.5 && pr.bottom <= dialog.bottom + 0.5,
                allOptionsVisible: options.every((option) => {
                    const r = option.getBoundingClientRect();
                    return r.top >= dialog.top - 0.5 && r.bottom <= dialog.bottom + 0.5;
                }),
            };
        }"""
    )
    delta = abs(round(metrics["triggerRight"] - metrics["panelRight"], 3))
    record(
        "dropdown_open",
        bool(metrics["expanded"] and not metrics["hidden"] and metrics["optionCount"] >= 1),
        metrics["expanded"],
        "The custom model listbox is open (aria-expanded=true, panel visible).",
    )
    record(
        "item_count",
        metrics["optionCount"] >= 2,
        metrics["optionCount"],
        "Chat models were discovered from the live catalog request and rendered as options.",
    )
    record(
        "opaque_background",
        metrics["backgroundAlpha"] >= 0.99,
        True,
        "The dropdown panel is fully opaque, so the trigger and page cannot bleed through.",
    )
    record(
        "visible_border",
        metrics["borderWidth"] >= 1 and metrics["borderAlpha"] > 0,
        True,
        "The dropdown panel has a visible border.",
    )
    record(
        "trigger_panel_right_delta",
        delta <= 2,
        delta,
        "The panel's right edge aligns with the trigger's right edge within 2 px.",
    )
    record(
        "dropdown_fully_visible",
        bool(metrics["fullyVisible"] and metrics["allOptionsVisible"]),
        True,
        "The open panel and every option stay inside the dialog viewport.",
    )
    if "orcarouter/auto" not in metrics["optionIds"]:
        raise AssertionError("the default catalog model is missing from the dropdown")
    if any(model_id.startswith("deepseek/") for model_id in metrics["optionIds"]):
        raise AssertionError("a verification-only model leaked into user-facing options")
    CATALOG_UI["label"] = metrics["label"]
    CATALOG_UI["catalog_status"] = metrics["catalogStatus"]
    CATALOG_UI["option_ids"] = metrics["optionIds"]


CATALOG_UI: dict[str, Any] = {}


def chromium_path(explicit: str | None) -> str:
    candidate = explicit or shutil.which("chromium") or shutil.which("chromium-browser") or ""
    if not candidate:
        raise SystemExit("chromium not found; pass --chromium /path/to/chromium")
    return candidate


def run(output_dir: Path, chromium: str) -> dict[str, Any]:
    started = time.time()
    output_dir.mkdir(parents=True, exist_ok=True)
    auth_png = output_dir / "auth-methods.png"
    dropdown_png = output_dir / "text-model-dropdown.png"
    manifest_path = output_dir / "manifest.json"
    manifest: dict[str, Any] = {
        "automation": {
            "name": "tests/evidence/run_gui_evidence.py",
            "framework": "playwright",
            "browser": "chromium",
            "passed": False,
            "catalog_source": CATALOG_SOURCE,
            "catalog_source_note": CATALOG_SOURCE_NOTE,
        },
        "passed": False,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="orca-evidence-data-") as tmp, OrcaStub() as stub:
            data_dir = Path(tmp)
            (data_dir / "configuration.json").write_text(
                json.dumps({"ai_provider": "orcarouter", "orcarouter_api_key": PLACEHOLDER_KEY}),
                encoding="utf-8",
            )
            with run_app(data_dir, env={"ORCA_API_BASE_URL": stub.base}) as base:
                status, chat_models = http_json(base + "/api/ai/models?provider=orcarouter&capability=chat")
                if status != 200 or chat_models.get("source") != "live":
                    raise AssertionError(f"catalog endpoint did not return live models: {status} {chat_models}")
                chat_ids = [model["id"] for model in chat_models["models"]]
                status, image_models = http_json(base + "/api/ai/models?provider=orcarouter&capability=image")
                if status != 200:
                    raise AssertionError(f"image capability request failed: {status}")
                image_ids = [model["id"] for model in image_models["models"]]
                if not chat_ids:
                    raise AssertionError("chat catalog is empty")
                if set(chat_ids) & set(image_ids):
                    raise AssertionError("image models leaked into the chat catalog")

                with sync_playwright() as pw:
                    browser = pw.chromium.launch(
                        executable_path=chromium,
                        args=["--no-sandbox", "--disable-dev-shm-usage", "--force-color-profile=srgb"],
                    )
                    page = browser.new_page(viewport=DEFAULT_VIEWPORT)
                    console_errors: list[str] = []
                    page.on("pageerror", lambda error: console_errors.append(str(error)))
                    page.goto(base, wait_until="load")
                    page.wait_for_selector("#setupDialog[open]", timeout=20000)
                    page.select_option("#aiProvider", "orcarouter")
                    page.wait_for_function(
                        "document.querySelectorAll('.orca-model-option').length >= 2",
                        timeout=20000,
                    )
                    page.fill("#orcaApiKey", PLACEHOLDER_KEY)
                    page.wait_for_timeout(150)
                    scroll_card_into_view(page)
                    check_auth_methods(page)
                    if any(not item["passed"] for item in CHECKS.values()):
                        raise AssertionError("dual-auth assertions failed before capture")
                    page.screenshot(path=str(auth_png))

                    page.click("#orcaModelTrigger")
                    page.wait_for_selector("#orcaModelPanel:not([hidden])", timeout=5000)
                    page.evaluate(
                        """() => {
                            const dialog = document.querySelector('#setupDialog');
                            dialog.scrollTop = dialog.scrollHeight;
                        }"""
                    )
                    page.wait_for_timeout(250)
                    check_dropdown(page)
                    page.screenshot(path=str(dropdown_png))
                    if console_errors:
                        raise AssertionError(f"page errors: {console_errors}")
                    browser_version = browser.version
                    browser.close()

                manifest["automation"].update({
                    "browser": f"chromium {browser_version}",
                    "catalog_model_count": len(chat_ids),
                    "image_model_count": len(image_ids),
                    "viewport": dict(DEFAULT_VIEWPORT),
                })
                manifest.update({
                    "catalog_model_ids": chat_ids,
                    "image_model_ids": image_ids,
                    "catalog_endpoint_used": stub.base + "/models?capability=chat",
                    "catalog_response_source": chat_models.get("source"),
                    "catalog_response_degraded": chat_models.get("degraded"),
                    "selected_model": CATALOG_UI.get("label"),
                    "rendered_option_ids": CATALOG_UI.get("option_ids"),
                    "catalog_status_text": CATALOG_UI.get("catalog_status"),
                    "viewport": dict(DEFAULT_VIEWPORT),
                })
                if len(CATALOG_UI.get("option_ids") or []) != len(chat_ids):
                    raise AssertionError("the dropdown did not render every discovered chat model")
        manifest["artifacts"] = [
            {
                "kind": "auth-methods",
                **screenshot_entry(auth_png),
                "ui": {
                    "api_key_visible": CHECKS["api_key_visible"]["passed"],
                    "secret_masked": CHECKS["secret_masked"]["passed"],
                    "controls_enabled": CHECKS["controls_enabled"]["passed"],
                    "pkce_visible": CHECKS["pkce_visible"]["passed"],
                },
            },
            {
                "kind": "text-model-dropdown",
                **screenshot_entry(dropdown_png),
                "ui": {
                    "dropdown_open": CHECKS["dropdown_open"]["passed"],
                    "item_count": CHECKS["item_count"]["value"],
                    "opaque_background": CHECKS["opaque_background"]["passed"],
                    "visible_border": CHECKS["visible_border"]["passed"],
                    "trigger_panel_right_delta": CHECKS["trigger_panel_right_delta"]["value"],
                    "dropdown_fully_visible": CHECKS["dropdown_fully_visible"]["passed"],
                },
            },
        ]
        required = {
            "api_key_visible", "secret_masked", "controls_enabled", "pkce_visible",
            "dropdown_open", "item_count", "opaque_background", "visible_border",
            "trigger_panel_right_delta", "dropdown_fully_visible",
        }
        manifest["ui_assertions"] = {
            name: (item["value"] if name in {"item_count", "trigger_panel_right_delta"} else item["passed"])
            for name, item in CHECKS.items() if name in required
        }
        manifest["ui_assertion_details"] = CHECKS
        failed = sorted(name for name, item in CHECKS.items() if not item["passed"])
        manifest["failed_assertions"] = failed
        manifest["passed"] = not failed
        manifest["automation"]["passed"] = manifest["passed"]
    except Exception as exc:  # noqa: BLE001 - the manifest must record the failure
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["ui_assertion_details"] = CHECKS
        manifest["passed"] = False
        manifest["automation"]["passed"] = False
        raise
    finally:
        manifest["automation"]["duration_seconds"] = round(time.time() - started, 2)
        manifest["automation"]["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        manifest["duration_seconds"] = manifest["automation"]["duration_seconds"]
        manifest["generated_at"] = manifest["automation"]["generated_at"]
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "orca-evidence", help="evidence directory")
    parser.add_argument("--chromium", default=None, help="path to the chromium binary")
    args = parser.parse_args(argv)
    manifest = run(args.output, chromium_path(args.chromium))
    automation = manifest["automation"]
    print(json.dumps({
        "passed": automation["passed"],
        "manifest": str(args.output / "manifest.json"),
        "failed_assertions": manifest.get("failed_assertions", []),
        "catalog_model_count": automation.get("catalog_model_count"),
        "image_model_count": automation.get("image_model_count"),
    }, indent=2))
    return 0 if automation["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
