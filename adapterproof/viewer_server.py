"""Local read-only server for the generated AdapterProof report."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from collections.abc import Callable

VIEWER_ROOT = Path(__file__).parent / "viewer"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/publication.html": ("publication.html", "text/html; charset=utf-8"),
    "/publication.js": ("publication.js", "text/javascript; charset=utf-8"),
    "/publication.css": ("publication.css", "text/css; charset=utf-8"),
}


def _validate_report(report_path: Path) -> bytes:
    content = report_path.read_bytes()
    report = json.loads(content)
    if not isinstance(report, dict) or not isinstance(report.get("adapters"), list):
        msg = "Report must contain an adapters list."
        raise TypeError(msg)
    return content


def _handler(report: bytes) -> type[BaseHTTPRequestHandler]:
    class ViewerHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/api/report":
                self._respond(report, "application/json; charset=utf-8")
                return
            static = STATIC_FILES.get(path)
            if static is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            filename, content_type = static
            self._respond((VIEWER_ROOT / filename).read_bytes(), content_type)

        def _respond(self, content: bytes, content_type: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, _format: str, *_args: Any) -> None:
            return

    return ViewerHandler


def create_viewer_server(
    report_path: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8767,
    server_factory: Callable[..., ThreadingHTTPServer] = ThreadingHTTPServer,
) -> ThreadingHTTPServer:
    """Create a local viewer server; callers own shutdown and close."""
    report = _validate_report(report_path)
    return server_factory((host, port), _handler(report))
