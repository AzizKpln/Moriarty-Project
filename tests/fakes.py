"""Shared local fakes for the OrcaRouter provider tests.

Everything here is loopback-only and uses placeholder credentials; no real
OrcaRouter account is contacted.
"""

from __future__ import annotations

import contextlib
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER_KEY = "sk-orca-" + "test-placeholder-not-a-real-key"
PLACEHOLDER_CODE = "test-code-not-real"

CATALOG: dict[str, Any] = {
    "data": [
        {
            "id": "orcarouter/auto",
            "name": "OrcaRouter Auto",
            "supported_endpoint_types": ["openai", "anthropic"],
            "architecture": {"input_modalities": ["text"]},
            "context_length": 200000,
        },
        {
            "id": "openai/gpt-5.5",
            "name": "GPT-5.5",
            "supported_endpoint_types": ["openai", "openai-response"],
            "architecture": {"input_modalities": ["text"]},
            "context_length": 400000,
            "reasoning": {"efforts": ["low", "medium", "high", "xhigh"]},
        },
        {
            "id": "orcarouter/fusion",
            "name": "OrcaRouter Fusion",
            "supported_endpoint_types": ["openai", "anthropic"],
            "architecture": {"input_modalities": ["text"]},
        },
        {
            "id": "google/gemini-3.5-flash",
            "name": "Gemini 3.5 Flash",
            "supported_endpoint_types": ["openai", "gemini"],
            "architecture": {"input_modalities": ["text", "image", "audio"]},
            "context_length": 1000000,
        },
        {
            "id": "orca/orcacyber-ultra-1.0",
            "name": "OrcaCyber Ultra",
            "supported_endpoint_types": ["openai", "anthropic"],
            "architecture": {"input_modalities": ["text"]},
        },
        {
            "id": "orca/orcacyber-zero-1.5",
            "name": "OrcaCyber Zero",
            "supported_endpoint_types": ["openai", "anthropic"],
            "architecture": {"input_modalities": ["text"]},
        },
        {
            "id": "openai/text-embedding-3-large",
            "name": "Text Embedding 3 Large",
            "supported_endpoint_types": ["embeddings"],
            "architecture": {"input_modalities": ["text"]},
        },
        {
            "id": "openai/gpt-image-1",
            "name": "GPT Image 1",
            "supported_endpoint_types": ["image-generation"],
            "architecture": {"input_modalities": ["text"], "output_modalities": ["image"]},
        },
        {
            "id": "openai/sora-2",
            "name": "Sora 2",
            "supported_endpoint_types": ["openai-video"],
            "architecture": {"input_modalities": ["text"], "output_modalities": ["video"]},
        },
        {
            "id": "jina/jina-reranker-v3",
            "name": "Jina Reranker v3",
            "supported_endpoint_types": ["jina-rerank"],
            "architecture": {"input_modalities": ["text"]},
        },
    ]
}


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def http_json(url: str, *, method: str = "GET", body: Any = None, headers: dict[str, str] | None = None, timeout: float = 10.0) -> tuple[int, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, raw.decode("utf-8", errors="replace")


class _QuietHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def _json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class OrcaStub:
    """Loopback imitation of the OrcaRouter inference origin."""

    def __init__(self, catalog: dict[str, Any] | None = None) -> None:
        self.catalog = catalog or CATALOG
        self.requests: list[dict[str, Any]] = []
        self.chat_status = 200
        self.chat_payload: dict[str, Any] = {
            "choices": [{"message": {"content": json.dumps({
                "risk_level": "low",
                "confidence": 0.5,
                "executive_summary": "Stub analysis.",
                "observed_facts": ["fact"],
                "assessments": [],
                "contradictions": [],
                "limitations": ["stub"],
                "recommended_actions": [],
            })}}]
        }
        stub = self

        class Handler(_QuietHandler):
            def do_GET(self) -> None:  # noqa: N802
                stub.requests.append({"method": "GET", "path": self.path, "headers": dict(self.headers)})
                if self.path.split("?")[0] == "/v1/models":
                    return self._json(200, stub.catalog)
                return self._json(404, {"error": "not found"})

            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                stub.requests.append({"method": "POST", "path": self.path, "headers": dict(self.headers), "body": body})
                if self.path.split("?")[0] == "/v1/chat/completions":
                    return self._json(stub.chat_status, stub.chat_payload)
                return self._json(404, {"error": "not found"})

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}/v1"

    def __enter__(self) -> "OrcaStub":
        self._thread.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._server.shutdown()
        self._server.server_close()


class AuthStub:
    """Loopback imitation of the OrcaRouter authorization origin."""

    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self.status = 200
        self.payload: dict[str, Any] = {
            "key": PLACEHOLDER_KEY,
            "user_id": "user-123",
            "scope": "api",
        }
        stub = self

        class Handler(_QuietHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                stub.requests.append({"path": self.path, "headers": dict(self.headers), "body": body})
                if self.path == "/api/v1/auth/keys":
                    return self._json(stub.status, stub.payload)
                return self._json(404, {"error": "not found"})

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def __enter__(self) -> "AuthStub":
        self._thread.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self._server.shutdown()
        self._server.server_close()


@contextlib.contextmanager
def run_app(data_dir: Path, *, env: dict[str, str] | None = None) -> Iterator[str]:
    """Run the real web workspace on loopback against a temporary data dir."""

    port = free_port()
    environment = {key: value for key, value in os.environ.items() if not key.startswith("ORCA_") and key != "ORCAROUTER_API_KEY"}
    environment.update({
        "PYTHONPATH": str(ROOT / "src") + (os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else ""),
        "PYTHONUNBUFFERED": "1",
    })
    environment.update(env or {})
    process = subprocess.Popen(
        [sys.executable, "-m", "moriarty.web_workspace_entry", "--no-browser", "--port", str(port), "--data-dir", str(data_dir)],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.time() + 25
        while time.time() < deadline:
            if process.poll() is not None:
                raise RuntimeError("web workspace exited during startup: " + (process.stderr.read() if process.stderr else ""))
            try:
                status, payload = http_json(base + "/api/health", timeout=1.0)
                if status == 200 and payload.get("status") == "ok":
                    break
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                pass
            time.sleep(0.15)
        else:
            raise RuntimeError("web workspace did not become healthy")
        yield base
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
