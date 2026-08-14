"""Simple local HTTP server exposing the minimal Stuff HTTP API.

Endpoints implemented (GET):
- /api/message   -> returns a single randomly generated message (JSON)
- /api/messages  -> returns recent messages (JSON list)
- /api/status    -> returns server metadata
- /api/about     -> returns protocol information

This server is intentionally minimal and uses only the standard library so
it can be run without extra dependencies.
"""
from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List

from core.generator import generate_message
from core.messages import Message
from core.config import SERVER_ID, PROTOCOL_VERSION, JSON_VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stuff.server")

# In-memory recent message store (non-persistent). Keep small for safety.
RECENT_MESSAGES: List[Message] = []
MAX_RECENT = 50


class StuffRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        try:
            if self.path == "/api/message":
                msg = generate_message("fact")
                RECENT_MESSAGES.append(msg)
                # trim
                while len(RECENT_MESSAGES) > MAX_RECENT:
                    RECENT_MESSAGES.pop(0)
                self._send_json(msg.to_dict())
            elif self.path == "/api/messages":
                data = [m.to_dict() for m in RECENT_MESSAGES]
                self._send_json({"messages": data})
            elif self.path == "/api/status":
                self._send_json({
                    "server_id": SERVER_ID,
                    "protocol": PROTOCOL_VERSION,
                    "version": "0.1.0",
                    "capabilities": ["messages"],
                })
            elif self.path == "/api/about":
                self._send_json({
                    "protocol": PROTOCOL_VERSION,
                    "description": "STUFF — simple message protocol",
                    "formats": ["application/json", "text/stuff"],
                })
            else:
                self.send_error(404, "Not found")
        except Exception as exc:
            logger.exception("Error handling request: %s", exc)
            self._send_json({"error": str(exc)}, status=500)

    def log_message(self, format, *args):
        # route HTTP server logs through logging module
        logger.info("%s - %s", self.client_address[0], format % args)


def run(host: str = "127.0.0.1", port: int = 8000):
    server = HTTPServer((host, port), StuffRequestHandler)
    logger.info("Stuff server starting at http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Stuff server")
        server.server_close()


if __name__ == "__main__":
    run()
