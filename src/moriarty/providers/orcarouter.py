"""OrcaRouter Cyber Inference provider.

OrcaRouter is an OpenAI-compatible gateway used by security teams for
authorized, scoped security work.  This module is the single place that knows
about its two origins, the two credential acquisition methods (pasted API key
and OAuth 2.0 + PKCE), model discovery, capability filtering and the chat
completion wire format.  Callers should obtain credentials through
``resolve_credential`` and build analyzers through ``moriarty.providers.ai_factory``.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Mapping, MutableMapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from moriarty.providers.search_backend import SearchBackendError

PROVIDER_ID = "orcarouter"
PROVIDER_DISPLAY_NAME = "OrcaRouter Cyber Inference"
DEFAULT_MODEL = "orcarouter/auto"
FALLBACK_MODEL = "orcarouter/fusion"
APP_NAME = "Gökbörü Intelligence"

DEFAULT_AUTH_BASE = "https://www.orcarouter.ai"
DEFAULT_API_BASE = "https://api.orcarouter.ai/v1"
AUTHORIZE_PATH = "/auth"
EXCHANGE_PATH = "/api/v1/auth/keys"

PROVIDER_PAGE_URL = "https://www.orcarouter.ai/cyber"
CYBER_CATALOG_URL = "https://www.orcarouter.ai/models?tier=cyber"
KEY_DASHBOARD_URL = "https://www.orcarouter.ai/console"
MODEL_DISCOVERY_URL = f"{DEFAULT_API_BASE}/models"

MAX_CATALOG_BYTES = 2_000_000
MAX_CATALOG_ITEMS = 500
DEFAULT_TIMEOUT = 30.0
CATALOG_TIMEOUT = 12.0

TEXT_ENDPOINTS = frozenset({"openai", "anthropic", "gemini", "openai-response"})
NON_TEXT_ENDPOINTS = frozenset({"image-generation", "openai-video", "jina-rerank"})
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1", "[::1]"})

ResponseLoader = Callable[[Request, float], bytes]


class OrcaRouterError(RuntimeError):
    """Base error for the OrcaRouter integration."""


class OrcaConfigurationError(OrcaRouterError):
    """Raised for an unsafe or unusable origin configuration."""


class OrcaAuthError(OrcaRouterError):
    """Raised when upstream rejects the credential; never retried in a loop."""


class OrcaExchangeError(OrcaRouterError):
    """Raised when the PKCE code exchange fails."""

    def __init__(self, status: int | None, code: str = "", description: str = "") -> None:
        self.status = status
        self.code = code or ""
        self.description = description or ""
        detail = self.description or self.code or "authorization failed"
        super().__init__(f"OrcaRouter code exchange failed ({status if status is not None else 'network'}): {detail}")


# ---------------------------------------------------------------------------
# Origins
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OrcaOrigins:
    auth_base: str
    api_base: str


def _loopback(hostname: str | None) -> bool:
    return bool(hostname) and hostname in LOOPBACK_HOSTS


def _validate_origin(raw: str, *, label: str) -> str:
    value = raw.strip().rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise OrcaConfigurationError(f"{label} must be an absolute http(s) URL.")
    if parsed.username or parsed.password or parsed.fragment:
        raise OrcaConfigurationError(f"{label} must not contain credentials or a fragment.")
    if parsed.scheme == "http" and not _loopback(parsed.hostname):
        raise OrcaConfigurationError(
            f"{label} must use HTTPS unless it points at loopback development."
        )
    return value


def resolve_origins(auth_base: str | None = None, api_base: str | None = None) -> OrcaOrigins:
    """Resolve the auth and inference origins independently.

    Authentication lives on ``www.orcarouter.ai`` (paths ``/auth`` and
    ``/api/v1/auth/keys``); inference lives on ``api.orcarouter.ai/v1``.  They
    are deliberately never derived from one another.  ``ORCA_BASE_URL`` is a
    shared self-hosted fallback, while ``ORCA_AUTH_BASE_URL`` and
    ``ORCA_API_BASE_URL`` take precedence.
    """

    shared = (os.environ.get("ORCA_BASE_URL") or "").strip()
    auth_raw = (auth_base or os.environ.get("ORCA_AUTH_BASE_URL") or shared or DEFAULT_AUTH_BASE)
    explicit_api = api_base or os.environ.get("ORCA_API_BASE_URL")
    if explicit_api:
        api_raw = explicit_api
    elif shared:
        api_raw = shared.rstrip("/")
        if not urlsplit(api_raw).path.rstrip("/").endswith("/v1"):
            api_raw = f"{api_raw}/v1"
    else:
        api_raw = DEFAULT_API_BASE
    return OrcaOrigins(
        auth_base=_validate_origin(auth_raw, label="OrcaRouter auth origin"),
        api_base=_validate_origin(api_raw, label="OrcaRouter inference origin"),
    )


# ---------------------------------------------------------------------------
# Provider registry and verified cold-start catalog
# ---------------------------------------------------------------------------


VERIFIED_SEED: tuple[dict[str, Any], ...] = (
    {
        "id": "orcarouter/auto",
        "name": "OrcaRouter Auto",
        "description": "Automatic routing across the OrcaRouter fleet. Default model; works with any OrcaRouter key.",
        "supported_endpoint_types": ["openai", "anthropic"],
        "architecture": {"input_modalities": ["text"]},
        "default": True,
    },
    {
        "id": "orca/orcacyber-ultra-1.0",
        "name": "OrcaCyber Ultra",
        "description": "Dedicated cyber model for authorized security code review and multi-step reasoning over large codebases.",
        "supported_endpoint_types": ["openai", "anthropic"],
        "architecture": {"input_modalities": ["text"]},
        "recommended_for_security_teams": True,
    },
    {
        "id": "orca/orcacyber-zero-1.5",
        "name": "OrcaCyber Zero",
        "description": "Dedicated cyber model driven by the OrcaCyber harness for authorized security work.",
        "supported_endpoint_types": ["openai", "anthropic"],
        "architecture": {"input_modalities": ["text"]},
        "recommended_for_security_teams": True,
    },
    {
        "id": FALLBACK_MODEL,
        "name": "OrcaRouter Fusion",
        "description": "General-purpose fallback model on the same gateway.",
        "supported_endpoint_types": ["openai", "anthropic"],
        "architecture": {"input_modalities": ["text"]},
        "fallback": True,
    },
)


def provider_registry() -> list[dict[str, Any]]:
    """The first-class provider entry consumed by settings UIs and docs."""

    return [{
        "id": PROVIDER_ID,
        "display_name": PROVIDER_DISPLAY_NAME,
        "base_url": DEFAULT_API_BASE,
        "docs_url": PROVIDER_PAGE_URL,
        "model_catalog_url": CYBER_CATALOG_URL,
        "model_discovery_url": MODEL_DISCOVERY_URL,
        "key_dashboard_url": KEY_DASHBOARD_URL,
        "auth_methods": ["api_key", "pkce"],
        "default_model": DEFAULT_MODEL,
        "fallback_model": FALLBACK_MODEL,
        "recommended_models": [
            {"id": "orca/orcacyber-ultra-1.0", "display_name": "OrcaCyber Ultra"},
            {"id": "orca/orcacyber-zero-1.5", "display_name": "OrcaCyber Zero"},
        ],
        "capabilities": ["chat"],
    }]


def _model_endpoints(item: Mapping[str, Any]) -> frozenset[str]:
    for key in ("supported_endpoint_types", "endpoint_types"):
        value = item.get(key)
        if isinstance(value, list):
            return frozenset(str(entry) for entry in value)
    architecture = item.get("architecture")
    if isinstance(architecture, Mapping):
        for key in ("supported_endpoint_types", "endpoint_types"):
            value = architecture.get(key)
            if isinstance(value, list):
                return frozenset(str(entry) for entry in value)
    return frozenset()


def _input_modalities(item: Mapping[str, Any]) -> frozenset[str]:
    architecture = item.get("architecture")
    source = architecture if isinstance(architecture, Mapping) else item
    value = source.get("input_modalities")
    if isinstance(value, list):
        return frozenset(str(entry) for entry in value)
    return frozenset()


def normalise_model(item: Mapping[str, Any]) -> dict[str, Any] | None:
    model_id = item.get("id") or item.get("model") or item.get("slug")
    if not isinstance(model_id, str) or not model_id.strip():
        return None
    endpoints = sorted(_model_endpoints(item))
    modalities = sorted(_input_modalities(item))
    architecture = dict(item.get("architecture") or {}) if isinstance(item.get("architecture"), Mapping) else {}
    if modalities:
        architecture["input_modalities"] = modalities
    if endpoints:
        architecture["supported_endpoint_types"] = endpoints
    normalised: dict[str, Any] = {
        "id": model_id.strip(),
        "name": str(item.get("name") or item.get("display_name") or model_id),
        "supported_endpoint_types": endpoints,
        "architecture": architecture,
        "input_modalities": modalities,
    }
    for key in ("context_length", "description", "capability", "reasoning", "verified", "source", "output_modalities"):
        if item.get(key) not in (None, ""):
            normalised[key] = item.get(key)
    return normalised


def model_supports(model: Mapping[str, Any], capability: str = "chat", modality: str | None = None) -> bool:
    """Capability filtering.  Models that do not declare a capability fail closed."""

    endpoints = _model_endpoints(model)
    if capability == "chat":
        if not endpoints & TEXT_ENDPOINTS:
            return False
        if endpoints & NON_TEXT_ENDPOINTS:
            return False
    elif capability == "multimodal":
        if not model_supports(model, "chat"):
            return False
        if not modality:
            raise ValueError("multimodal filtering requires a modality")
        if modality not in _input_modalities(model):
            return False
    elif capability == "embedding":
        if "embeddings" not in endpoints:
            return False
    elif capability == "image":
        if "image-generation" not in endpoints:
            return False
    elif capability == "video":
        if "openai-video" not in endpoints:
            return False
    elif capability == "rerank":
        if "jina-rerank" not in endpoints:
            return False
    else:
        raise ValueError(f"unknown capability: {capability}")
    return True


def filter_models(models: Any, capability: str = "chat", modality: str | None = None) -> list[dict[str, Any]]:
    if not isinstance(models, (list, tuple)):
        return []
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in models:
        if not isinstance(item, Mapping):
            continue
        model = normalise_model(item)
        if model is None or model["id"] in seen:
            continue
        if model_supports(model, capability, modality):
            seen.add(model["id"])
            result.append(model)
    return result[:MAX_CATALOG_ITEMS]


def seed_models(capability: str = "chat", modality: str | None = None) -> list[dict[str, Any]]:
    return annotate_models(filter_models([dict(item, verified=True, source="orcarouter") for item in VERIFIED_SEED], capability, modality))


CYBER_MODEL_IDS = frozenset({"orca/orcacyber-ultra-1.0", "orca/orcacyber-zero-1.5"})


def annotate_models(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mark the default/recommended/fallback roles and put the default first."""

    annotated: list[dict[str, Any]] = []
    for model in models:
        entry = dict(model)
        if entry["id"] == DEFAULT_MODEL:
            entry["default"] = True
        if entry["id"] == FALLBACK_MODEL:
            entry["fallback"] = True
        if entry["id"] in CYBER_MODEL_IDS:
            entry["recommended_for_security_teams"] = True
        annotated.append(entry)
    annotated.sort(key=lambda item: (not item.get("default"), not item.get("recommended_for_security_teams")))
    return annotated


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OrcaCredential:
    """A resolved credential.  ``key`` is never rendered in UI or logs."""

    key: str = field(repr=False)
    source: str
    generation: int
    account_id: str | None = None
    scope: str | None = None


class CredentialVault(Protocol):
    def get(self, name: str) -> Any: ...
    def set(self, name: str, value: Any) -> None: ...
    def delete(self, name: str) -> None: ...


class MappingVault:
    """Vault over a mapping, with an optional persist callback for real storage."""

    def __init__(self, data: MutableMapping[str, Any], persist: Callable[[], None] | None = None) -> None:
        self._data = data
        self._persist = persist

    def get(self, name: str) -> Any:
        return self._data.get(name)

    def set(self, name: str, value: Any) -> None:
        self._data[name] = value
        if self._persist:
            self._persist()

    def delete(self, name: str) -> None:
        self._data.pop(name, None)
        if self._persist:
            self._persist()


def _generation(vault: CredentialVault) -> int:
    try:
        return int(vault.get("orcarouter_credential_generation") or 0)
    except (TypeError, ValueError):
        return 0


def _persist_credential(
    vault: CredentialVault,
    *,
    key: str,
    source: str,
    account_id: str | None,
    scope: str | None,
) -> OrcaCredential:
    generation = _generation(vault) + 1
    vault.set("orcarouter_api_key", key)
    vault.set("orcarouter_credential_source", source)
    vault.set("orcarouter_credential_generation", generation)
    vault.set("orcarouter_needs_reauth", False)
    if account_id:
        vault.set("orcarouter_account_id", account_id)
    else:
        vault.delete("orcarouter_account_id")
    if scope:
        vault.set("orcarouter_scope", scope)
    else:
        vault.delete("orcarouter_scope")
    return OrcaCredential(key=key, source=source, generation=generation, account_id=account_id, scope=scope)


class ApiKeyCredentialAdapter:
    """Credential seam adapter for a user-pasted ``sk-orca-…`` key."""

    source = "api_key"

    def save(self, vault: CredentialVault, key: str) -> OrcaCredential:
        value = (key or "").strip()
        if not value:
            raise OrcaConfigurationError("Enter an OrcaRouter API key.")
        if not value.startswith("sk-orca-"):
            raise OrcaConfigurationError("OrcaRouter API keys start with sk-orca-.")
        return _persist_credential(vault, key=value, source=self.source, account_id=None, scope="api")


class PkceCredentialAdapter:
    """Credential seam adapter for a key obtained through OAuth 2.0 + PKCE."""

    source = "pkce"

    def save(self, vault: CredentialVault, key: str, *, account_id: str | None, scope: str) -> OrcaCredential:
        value = (key or "").strip()
        if not value.startswith("sk-orca-"):
            raise OrcaConfigurationError("The authorization response did not contain a usable OrcaRouter key.")
        return _persist_credential(vault, key=value, source=self.source, account_id=account_id, scope=scope)


API_KEY_ADAPTER = ApiKeyCredentialAdapter()
PKCE_ADAPTER = PkceCredentialAdapter()


def resolve_credential(vault: CredentialVault) -> OrcaCredential | None:
    """Return the stored credential regardless of which adapter created it."""

    key = vault.get("orcarouter_api_key")
    if not isinstance(key, str) or not key.startswith("sk-orca-"):
        return None
    source = str(vault.get("orcarouter_credential_source") or "api_key")
    if source not in {"api_key", "pkce"}:
        source = "api_key"
    scope = vault.get("orcarouter_scope")
    account = vault.get("orcarouter_account_id")
    return OrcaCredential(
        key=key,
        source=source,
        generation=_generation(vault),
        account_id=str(account) if account else None,
        scope=str(scope) if scope else None,
    )


def clear_credential(vault: CredentialVault) -> None:
    for name in (
        "orcarouter_api_key", "orcarouter_credential_source", "orcarouter_scope",
        "orcarouter_account_id", "orcarouter_needs_reauth",
    ):
        vault.delete(name)
    vault.set("orcarouter_credential_generation", _generation(vault) + 1)


def mark_reauthentication_required(vault: CredentialVault, credential: OrcaCredential) -> bool:
    """Mark only the exact rejected account/generation as needing reauth.

    A late failure from an old request must never poison a credential that was
    reauthorized in the meantime.
    """

    current = resolve_credential(vault)
    if current is None:
        return False
    if current.generation != credential.generation or current.key != credential.key:
        return False
    if current.account_id and credential.account_id and current.account_id != credential.account_id:
        return False
    vault.set("orcarouter_needs_reauth", True)
    return True


def needs_reauthentication(vault: CredentialVault) -> bool:
    return bool(vault.get("orcarouter_needs_reauth"))


# ---------------------------------------------------------------------------
# OAuth 2.0 + PKCE (Flow A — loopback redirect)
# ---------------------------------------------------------------------------


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def new_verifier() -> str:
    return _b64url(secrets.token_bytes(32))


def challenge_for(verifier: str) -> str:
    return _b64url(hashlib.sha256(verifier.encode("ascii")).digest())


def new_state() -> str:
    return _b64url(secrets.token_bytes(16))


def build_authorize_url(
    auth_base: str,
    *,
    callback_url: str,
    verifier: str,
    state: str,
    scope: str = "api",
    app_name: str = APP_NAME,
) -> str:
    if scope not in {"api", "connector"}:
        raise OrcaConfigurationError("Unsupported OrcaRouter scope.")
    query = urlencode({
        "callback_url": callback_url,
        "code_challenge": challenge_for(verifier),
        "code_challenge_method": "S256",
        "state": state,
        "app_name": app_name,
        "scope": scope,
    })
    return f"{auth_base}{AUTHORIZE_PATH}?{query}"


def _validate_callback_url(callback_url: str) -> str:
    parsed = urlsplit(callback_url)
    if parsed.username or parsed.password or parsed.fragment:
        raise OrcaConfigurationError("The callback URL must not contain credentials or a fragment.")
    if parsed.scheme == "https" and parsed.hostname:
        return callback_url
    if parsed.scheme == "http" and _loopback(parsed.hostname):
        return callback_url
    raise OrcaConfigurationError("The callback URL must be HTTPS or loopback HTTP.")


def _load_response(request: Request, timeout: float) -> bytes:
    with urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_CATALOG_BYTES + 1)
    if len(body) > MAX_CATALOG_BYTES:
        raise OrcaRouterError("OrcaRouter response exceeded the size limit.")
    return body


def _oauth_detail(raw: bytes) -> tuple[str, str]:
    try:
        payload = json.loads(raw.decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "", ""
    if not isinstance(payload, Mapping):
        return "", ""
    code = str(payload.get("error") or "")
    description = str(payload.get("error_description") or "")
    # Never let a malformed server echo a credential into our error surface.
    if "sk-orca-" in description:
        description = "authorization refused"
    return code, description


def exchange_code(
    auth_base: str,
    *,
    code: str,
    verifier: str,
    timeout: float = DEFAULT_TIMEOUT,
    loader: ResponseLoader | None = None,
) -> dict[str, Any]:
    """Exchange a one-time code at the auth origin.

    The verifier travels only in the POST body.  It never appears in a URL, an
    error message, or a log line.
    """

    if not code:
        raise OrcaExchangeError(None, "missing_code", "The authorization response had no code.")
    body = json.dumps({
        "code": code,
        "code_verifier": verifier,
        "code_challenge_method": "S256",
    }).encode("utf-8")
    request = Request(
        f"{auth_base}{EXCHANGE_PATH}",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        raw = (loader or _load_response)(request, timeout)
    except HTTPError as exc:
        detail = exc.read(MAX_CATALOG_BYTES)
        error_code, description = _oauth_detail(detail)
        if exc.code == 429:
            description = "Too many authorization requests (10 keys per user per 24 hours). Try again later."
        raise OrcaExchangeError(exc.code, error_code, description) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise OrcaExchangeError(None, "network_error", "Could not reach the OrcaRouter authorization service.") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise OrcaExchangeError(None, "invalid_response", "The authorization service returned invalid JSON.") from exc
    if not isinstance(payload, Mapping):
        raise OrcaExchangeError(None, "invalid_response", "The authorization service returned an unexpected payload.")
    key = payload.get("key")
    if not isinstance(key, str) or not key.startswith("sk-orca-"):
        raise OrcaExchangeError(None, "missing_key", "The authorization response did not contain a key.")
    return {
        "key": key,
        "user_id": str(payload.get("user_id") or "") or None,
        "scope": str(payload.get("scope") or ""),
    }


class LoopbackCallbackServer:
    """Minimal single-shot loopback listener for Flow A."""

    def __init__(self, *, path: str = "/cb", state: str, timeout: float = 180.0) -> None:
        self.path = path
        self.state = state
        self.timeout = timeout
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._done = threading.Event()
        self._result: dict[str, str] = {}
        self._lock = threading.Lock()
        self._closed = False

    @property
    def port(self) -> int:
        if self._server is None:
            raise OrcaRouterError("callback server is not running")
        return int(self._server.server_address[1])

    def callback_url(self) -> str:
        return f"http://127.0.0.1:{self.port}{self.path}"

    def start(self) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urlsplit(self.path)
                if parsed.path != outer.path:
                    self.send_response(HTTPStatus.NOT_FOUND)
                    self.end_headers()
                    return
                params = dict(item.split("=", 1) for item in parsed.query.split("&") if "=" in item)
                from urllib.parse import unquote_plus
                state = unquote_plus(params.get("state", ""))
                if not hmac.compare_digest(state, outer.state):
                    outer._finish({"error": "state_mismatch"})
                    self._page(HTTPStatus.BAD_REQUEST, "Authorization failed: state mismatch. You can close this tab.")
                    return
                error = unquote_plus(params.get("error", ""))
                if error:
                    outer._finish({"error": error})
                    self._page(HTTPStatus.OK, "Authorization was denied. You can close this tab.")
                    return
                code = unquote_plus(params.get("code", ""))
                if not code:
                    outer._finish({"error": "missing_code"})
                    self._page(HTTPStatus.BAD_REQUEST, "Authorization failed: no code returned.")
                    return
                outer._finish({"code": code})
                self._page(HTTPStatus.OK, "Connected. You can close this tab.")

            def _page(self, status: HTTPStatus, message: str) -> None:
                body = f"<!doctype html><meta charset='utf-8'><p>{message}</p>".encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: Any) -> None:
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def _finish(self, result: dict[str, str]) -> None:
        with self._lock:
            if self._result:
                return
            self._result = result
        self._done.set()
        threading.Thread(target=self._shutdown, daemon=True).start()

    def _shutdown(self) -> None:
        if self._server is not None:
            try:
                self._server.shutdown()
            except Exception:
                pass
            try:
                self._server.server_close()
            except Exception:
                pass

    def wait(self, timeout: float | None = None) -> dict[str, str]:
        if not self._done.wait(timeout if timeout is not None else self.timeout):
            self.close()
            return {"error": "timeout"}
        with self._lock:
            return dict(self._result)

    def close(self) -> None:
        with self._lock:
            self._closed = True
        self._done.set()
        self._shutdown()


@dataclass
class ConnectAttempt:
    attempt_id: str
    verifier: str = field(repr=False)
    state: str = field(repr=False)
    server: LoopbackCallbackServer | None = None
    status: str = "pending"
    authorize_url: str = ""
    error: str = ""
    scope: str = ""
    account_id: str | None = None
    created_at: float = 0.0
    expires_at: float = 0.0
    thread: threading.Thread | None = None


class OrcaConnectManager:
    """Owns in-flight PKCE attempts for the local web UI."""

    def __init__(
        self,
        vault: CredentialVault,
        *,
        auth_base: str | None = None,
        app_name: str = APP_NAME,
        attempt_ttl: float = 300.0,
        exchange_loader: ResponseLoader | None = None,
    ) -> None:
        self._vault = vault
        self._auth_base = auth_base
        self._app_name = app_name
        self._ttl = attempt_ttl
        self._exchange_loader = exchange_loader
        self._attempts: dict[str, ConnectAttempt] = {}
        self._lock = threading.Lock()

    def start(self) -> dict[str, Any]:
        origins = resolve_origins(self._auth_base)
        verifier = new_verifier()
        state = new_state()
        server = LoopbackCallbackServer(state=state, timeout=self._ttl)
        server.start()
        attempt = ConnectAttempt(
            attempt_id=secrets.token_urlsafe(12),
            verifier=verifier,
            state=state,
            server=server,
            authorize_url=build_authorize_url(
                origins.auth_base,
                callback_url=_validate_callback_url(server.callback_url()),
                verifier=verifier,
                state=state,
                app_name=self._app_name,
            ),
            created_at=time.time(),
            expires_at=time.time() + self._ttl,
        )
        with self._lock:
            self._prune()
            self._attempts[attempt.attempt_id] = attempt
        attempt.thread = threading.Thread(target=self._run, args=(attempt,), daemon=True)
        attempt.thread.start()
        return {
            "attempt_id": attempt.attempt_id,
            "authorize_url": attempt.authorize_url,
            "expires_in": int(self._ttl),
        }

    def _prune(self) -> None:
        now = time.time()
        for attempt_id, attempt in list(self._attempts.items()):
            if attempt.status != "pending" and now - attempt.created_at > self._ttl:
                self._attempts.pop(attempt_id, None)

    def _run(self, attempt: ConnectAttempt) -> None:
        assert attempt.server is not None
        try:
            callback = attempt.server.wait()
            if attempt.status == "cancelled":
                return
            if callback.get("error") == "timeout":
                self._set(attempt, status="expired", error="Authorization timed out. Start again.")
                return
            if callback.get("error"):
                self._set(attempt, status="denied" if callback["error"] == "access_denied" else "error",
                          error="Authorization was denied." if callback["error"] == "access_denied" else "Authorization failed; start again.")
                return
            result = exchange_code(
                resolve_origins(self._auth_base).auth_base,
                code=callback["code"],
                verifier=attempt.verifier,
                loader=self._exchange_loader,
            )
            scope = result.get("scope") or ""
            if scope != "api":
                self._set(attempt, status="error",
                          error=f"Authorization granted scope '{scope or 'unknown'}', which this app cannot use.")
                return
            PKCE_ADAPTER.save(self._vault, result["key"], account_id=result.get("user_id"), scope=scope)
            self._set(attempt, status="success", scope=scope, account_id=result.get("user_id"),
                      verifier="")
        except OrcaExchangeError as exc:
            self._set(attempt, status="error", error=str(exc), verifier="")
        except Exception:
            self._set(attempt, status="error", error="Authorization failed; start again.", verifier="")

    def _set(self, attempt: ConnectAttempt, *, status: str, error: str = "", scope: str = "", account_id: str | None = None, verifier: str | None = None) -> None:
        with self._lock:
            attempt.status = status
            attempt.error = error
            if scope:
                attempt.scope = scope
            if account_id:
                attempt.account_id = account_id
            if verifier is not None:
                attempt.verifier = verifier
        if attempt.server is not None:
            attempt.server.close()

    def status(self, attempt_id: str) -> dict[str, Any]:
        with self._lock:
            attempt = self._attempts.get(attempt_id)
            if attempt is None:
                return {"status": "unknown", "error": "Unknown authorization attempt."}
            return {
                "status": attempt.status,
                "error": attempt.error,
                "scope": attempt.scope,
                "authorize_url": attempt.authorize_url,
                "expires_in": max(0, int(attempt.expires_at - time.time())),
            }

    def cancel(self, attempt_id: str) -> bool:
        with self._lock:
            attempt = self._attempts.get(attempt_id)
            if attempt is None:
                return False
            if attempt.status == "pending":
                attempt.status = "cancelled"
                attempt.error = ""
        if attempt.server is not None:
            attempt.server.close()
        return True

    def cancel_all(self) -> None:
        with self._lock:
            attempts = list(self._attempts.values())
        for attempt in attempts:
            self.cancel(attempt.attempt_id)


# ---------------------------------------------------------------------------
# Model discovery
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CatalogResult:
    models: list[dict[str, Any]]
    source: str
    degraded: bool
    catalog_url: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "models": self.models,
            "count": len(self.models),
            "source": self.source,
            "degraded": self.degraded,
            "catalog_url": self.catalog_url,
            "error": self.error,
        }


def _catalog_url(api_base: str, capability: str | None) -> str:
    url = f"{api_base}/models"
    if capability:
        url = f"{url}?capability={quote(capability)}"
    return url


def parse_catalog(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, Mapping):
        items = payload.get("data")
        if not isinstance(items, list):
            items = payload.get("models")
        if not isinstance(items, list):
            items = []
    elif isinstance(payload, list):
        items = payload
    else:
        return []
    parsed: list[dict[str, Any]] = []
    for item in items[:MAX_CATALOG_ITEMS]:
        if isinstance(item, Mapping):
            model = normalise_model(item)
            if model is not None:
                parsed.append(model)
    return parsed


def discover_models(
    api_key: str | None = None,
    *,
    capability: str | None = None,
    modality: str | None = None,
    api_base: str | None = None,
    timeout: float = CATALOG_TIMEOUT,
    loader: ResponseLoader | None = None,
) -> CatalogResult:
    """Fetch the live catalog, falling back to the verified seed.

    Live discovery is authoritative.  The seed is used only when the endpoint
    is unreachable, unauthenticated or returns nothing usable, and the result
    is marked ``degraded`` so the UI can say so.
    """

    page = capability or "chat"
    origins = resolve_origins(api_base=api_base)
    url = _catalog_url(origins.api_base, capability)
    seed_page = page if page in {"chat", "embedding", "image", "video", "rerank"} else "chat"
    seed = seed_models(seed_page, modality if page == "multimodal" else None)
    key = (api_key or "").strip()
    if not key:
        return CatalogResult(seed, "fallback", True, url, "No OrcaRouter API key is configured.")
    request = Request(url, headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    try:
        raw = (loader or _load_response)(request, timeout)
        models = parse_catalog(json.loads(raw.decode("utf-8")))
    except HTTPError as exc:
        reason = "credential rejected" if exc.code in {401, 403} else f"HTTP {exc.code}"
        return CatalogResult(seed, "fallback", True, url, f"Model discovery failed: {reason}.")
    except (URLError, TimeoutError, OSError):
        return CatalogResult(seed, "fallback", True, url, "Model discovery failed: network error.")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return CatalogResult(seed, "fallback", True, url, "Model discovery returned invalid JSON.")
    if not models:
        return CatalogResult(seed, "fallback", True, url, "Model discovery returned no models.")
    filtered = annotate_models(filter_models(models, page, modality))
    if not filtered:
        return CatalogResult(seed, "fallback", True, url, "No models matched this capability.")
    return CatalogResult(filtered, "live", False, url, None)


# ---------------------------------------------------------------------------
# Chat completions
# ---------------------------------------------------------------------------


class OrcaRouterClient:
    """Small OpenAI-compatible chat client for the OrcaRouter gateway."""

    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_MODEL,
        api_base: str | None = None,
        timeout: float = 60.0,
        loader: ResponseLoader | None = None,
    ) -> None:
        self._api_key = (api_key or "").strip()
        self._model = model or DEFAULT_MODEL
        self._api_base = resolve_origins(api_base=api_base).api_base
        self._timeout = timeout
        self._loader = loader or _load_response

    @property
    def model(self) -> str:
        return self._model

    def complete(self, messages: list[dict[str, Any]], *, response_format: Mapping[str, Any] | None = None, timeout: float | None = None) -> str:
        if not self._api_key:
            raise OrcaAuthError("No OrcaRouter credential is configured.")
        body: dict[str, Any] = {"model": self._model, "messages": messages, "temperature": 0.1}
        if response_format is not None:
            body["response_format"] = dict(response_format)
        request = Request(
            f"{self._api_base}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            raw = self._loader(request, timeout or self._timeout)
        except HTTPError as exc:
            if exc.code == 401:
                raise OrcaAuthError("OrcaRouter rejected the credential; sign in again or paste a new key.") from exc
            if exc.code == 429:
                raise OrcaRouterError("OrcaRouter rate limit reached; retry shortly.") from exc
            raise OrcaRouterError(f"OrcaRouter request failed with HTTP {exc.code}.") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise OrcaRouterError("OrcaRouter network error.") from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise OrcaRouterError("OrcaRouter returned invalid JSON.") from exc
        return self._content(payload)

    @staticmethod
    def _content(payload: Any) -> str:
        if isinstance(payload, Mapping):
            choices = payload.get("choices")
            if isinstance(choices, list) and choices:
                message = choices[0].get("message") if isinstance(choices[0], Mapping) else None
                if isinstance(message, Mapping):
                    content = message.get("content")
                    if isinstance(content, list):
                        return "".join(str(part.get("text") or "") for part in content if isinstance(part, Mapping))
                    if isinstance(content, str):
                        return content
        raise OrcaRouterError("OrcaRouter returned an unexpected completion payload.")


def _json_object(text: str) -> dict[str, Any]:
    value = (text or "").strip()
    if value.startswith("```"):
        value = value.strip("`")
        if value.lower().startswith("json"):
            value = value[4:]
    start, end = value.find("{"), value.rfind("}")
    if start < 0 or end <= start:
        raise SearchBackendError("OrcaRouter returned no structured JSON.")
    try:
        parsed = json.loads(value[start:end + 1])
    except json.JSONDecodeError as exc:
        raise SearchBackendError("OrcaRouter returned invalid structured JSON.") from exc
    if not isinstance(parsed, dict):
        raise SearchBackendError("OrcaRouter returned a non-object JSON payload.")
    return parsed


_CASE_SCHEMA: dict[str, Any] = {
    "risk_level": "low|medium|high|unknown",
    "confidence": "number 0..1",
    "executive_summary": "string",
    "observed_facts": ["string"],
    "assessments": ["string"],
    "contradictions": ["string"],
    "limitations": ["string"],
    "recommended_actions": ["string"],
}


class OrcaRouterCaseAnalysis:
    """Case analysis on the OrcaRouter Cyber Inference endpoint."""

    def __init__(self, api_key: str | None = None, model: str | None = None, api_base: str | None = None, loader: ResponseLoader | None = None) -> None:
        self._api_key = api_key or os.environ.get("ORCAROUTER_API_KEY") or ""
        self._model = model or os.environ.get("ORCAROUTER_MODEL") or DEFAULT_MODEL
        self._api_base = api_base
        self._loader = loader

    def analyze(self, investigation: dict[str, Any], timeout: float = 60, language: str = "tr") -> dict[str, Any]:
        if not self._api_key:
            raise SearchBackendError("ORCAROUTER_API_KEY is not set; OrcaRouter analysis cannot run.")
        evidence = {
            "subject": investigation.get("subject"),
            "summary": investigation.get("summary"),
            "sources": investigation.get("sources", []),
        }
        output_language = "English" if language == "en" else "Turkish"
        prompt = (
            "You are an evidence-focused analyst working on an authorized security investigation. "
            "Analyze only the supplied audit output. Separate observed facts from inferences. "
            "Never accuse a person of wrongdoing, never infer legal ownership, and treat missing or blocked "
            f"sources as unknown rather than clear. Write every human-readable value in {output_language}. "
            "Return one JSON object matching this shape: " + json.dumps(_CASE_SCHEMA) + "\n\nAUDIT:\n"
            + json.dumps(evidence, ensure_ascii=False)
        )
        client = OrcaRouterClient(self._api_key, model=self._model, api_base=self._api_base, timeout=timeout, loader=self._loader)
        text = client.complete(
            [
                {"role": "system", "content": "Return JSON only. Never add prose outside the JSON object."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            timeout=timeout,
        )
        result = _json_object(text)
        for key, default in (("risk_level", "unknown"), ("confidence", 0.0), ("executive_summary", ""), ("observed_facts", []), ("assessments", []), ("contradictions", []), ("limitations", []), ("recommended_actions", [])):
            result.setdefault(key, default)
        result.update({
            "model": self._model,
            "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "method": "orcarouter_evidence_analysis",
            "language": language,
        })
        return result


class OrcaRouterWebIntelligence:
    def __init__(self, api_key: str | None = None, model: str | None = None, api_base: str | None = None, loader: ResponseLoader | None = None) -> None:
        self._api_key = api_key or os.environ.get("ORCAROUTER_API_KEY") or ""
        self._model = model or os.environ.get("ORCAROUTER_MODEL") or DEFAULT_MODEL
        self._api_base = api_base
        self._loader = loader

    def analyze(self, context: str, expected_e164: str, title: str, timeout: float) -> dict[str, Any]:
        if not self._api_key:
            raise SearchBackendError("ORCAROUTER_API_KEY is not set; web intelligence cannot run.")
        prompt = (
            "Extract structured public information only from this visible web-page excerpt. "
            "Do not use outside knowledge or infer ownership. Every organization, department, address, email, "
            "additional phone, and website must appear verbatim in the excerpt. "
            f"The queried telephone {expected_e164} is already verified. Page title: {title}. "
            "Use empty values when unknown. Return JSON only with keys: page_type, language, organization, "
            "department, queried_phone_role, business_category, address, emails, additional_phones, websites, confidence."
        )
        client = OrcaRouterClient(self._api_key, model=self._model, api_base=self._api_base, timeout=timeout, loader=self._loader)
        text = client.complete(
            [{"role": "system", "content": "Return JSON only."},
             {"role": "user", "content": prompt + "\n\nEXCERPT:\n" + context}],
            response_format={"type": "json_object"},
            timeout=timeout,
        )
        return _json_object(text)


class OrcaRouterDocumentIntelligence:
    def __init__(self, api_key: str | None = None, model: str | None = None, api_base: str | None = None, loader: ResponseLoader | None = None) -> None:
        self._api_key = api_key or os.environ.get("ORCAROUTER_API_KEY") or ""
        self._model = model or os.environ.get("ORCAROUTER_MODEL") or DEFAULT_MODEL
        self._api_base = api_base
        self._loader = loader

    def analyze(self, context: str, expected_e164: str, title: str, timeout: float) -> dict[str, Any]:
        if not self._api_key:
            raise SearchBackendError("ORCAROUTER_API_KEY is not set; document intelligence cannot run.")
        prompt = (
            "Extract structured public contact information only from the supplied document excerpt. "
            "Do not use outside knowledge and do not infer ownership. Every organization, department, address, "
            "email, phone and website value must appear verbatim in the excerpt. "
            f"The already verified queried number is {expected_e164}. Document title: {title}. "
            "Use empty strings or arrays for unknown values and a confidence between 0 and 1. Return JSON only with keys: "
            "document_category, language, organization, department, queried_phone_role, address, emails, "
            "additional_phones, websites, confidence."
        )
        client = OrcaRouterClient(self._api_key, model=self._model, api_base=self._api_base, timeout=timeout, loader=self._loader)
        text = client.complete(
            [{"role": "system", "content": "Return JSON only."},
             {"role": "user", "content": prompt + "\n\nEXCERPT:\n" + context}],
            response_format={"type": "json_object"},
            timeout=timeout,
        )
        return _json_object(text)
