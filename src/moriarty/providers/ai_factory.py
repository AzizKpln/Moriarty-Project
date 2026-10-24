"""Central selection of the AI provider used by every AI entry point.

The web workspace, the CLI and the unattended phone-audit runner all build
their analyzers here so provider choice, credential lookup and model defaults
live in one place.  OrcaRouter is a first-class named provider; Gemini remains
the default for installations that have not opted in.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

from moriarty.providers.gemini_case_analysis import GeminiCaseAnalysis
from moriarty.providers.gemini_document_intelligence import GeminiDocumentIntelligence
from moriarty.providers.gemini_document_ocr import GeminiDocumentOcr
from moriarty.providers.gemini_web_intelligence import GeminiWebIntelligence
from moriarty.providers.orcarouter import (
    DEFAULT_MODEL,
    OrcaRouterCaseAnalysis,
    OrcaRouterDocumentIntelligence,
    OrcaRouterWebIntelligence,
)

ORCAROUTER = "orcarouter"
GEMINI = "gemini"


def selected_provider(configuration: Mapping[str, Any] | None = None) -> str:
    configuration = configuration or {}
    value = str(configuration.get("ai_provider") or os.environ.get("GOKBORU_AI_PROVIDER") or GEMINI).strip().lower()
    return ORCAROUTER if value == ORCAROUTER else GEMINI


def orcarouter_key(configuration: Mapping[str, Any] | None = None) -> str:
    configuration = configuration or {}
    value = configuration.get("orcarouter_api_key") or os.environ.get("ORCAROUTER_API_KEY") or ""
    return str(value).strip()


def orcarouter_model(configuration: Mapping[str, Any] | None = None, model: str | None = None) -> str:
    configuration = configuration or {}
    if model:
        return model
    return str(configuration.get("orcarouter_model") or os.environ.get("ORCAROUTER_MODEL") or DEFAULT_MODEL)


def uses_orcarouter(configuration: Mapping[str, Any] | None = None) -> bool:
    return selected_provider(configuration) == ORCAROUTER and bool(orcarouter_key(configuration))


def build_case_analysis(configuration: Mapping[str, Any] | None = None):
    configuration = configuration or {}
    if uses_orcarouter(configuration):
        return OrcaRouterCaseAnalysis(api_key=orcarouter_key(configuration), model=orcarouter_model(configuration))
    return GeminiCaseAnalysis(api_key=configuration.get("gemini_api_key"))


def build_web_intelligence(configuration: Mapping[str, Any] | None = None, model: str | None = None):
    configuration = configuration or {}
    if uses_orcarouter(configuration):
        return OrcaRouterWebIntelligence(api_key=orcarouter_key(configuration), model=orcarouter_model(configuration, model))
    return GeminiWebIntelligence(model=model)


def build_document_intelligence(configuration: Mapping[str, Any] | None = None, model: str | None = None):
    configuration = configuration or {}
    if uses_orcarouter(configuration):
        return OrcaRouterDocumentIntelligence(api_key=orcarouter_key(configuration), model=orcarouter_model(configuration, model))
    return GeminiDocumentIntelligence(model=model)


def build_document_ocr(configuration: Mapping[str, Any] | None = None, model: str | None = None):
    """PDF OCR keeps Gemini: OrcaRouter's chat wire format does not accept inline PDFs."""

    return GeminiDocumentOcr(model=model)


def deployment_configuration() -> dict[str, Any]:
    """Environment-only configuration for CLI processes without a config file."""

    value: dict[str, Any] = {}
    for key, env_name in (
        ("gemini_api_key", "GEMINI_API_KEY"),
        ("orcarouter_api_key", "ORCAROUTER_API_KEY"),
        ("ai_provider", "GOKBORU_AI_PROVIDER"),
        ("orcarouter_model", "ORCAROUTER_MODEL"),
    ):
        if os.environ.get(env_name):
            value[key] = os.environ[env_name]
    return value
