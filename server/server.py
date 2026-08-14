"""Simple local HTTP server exposing the minimal Stuff HTTP API.

Endpoints implemented (GET):
- /api/message   -> returns a single randomly generated message (JSON)
- /api/messages  -> returns recent messages (JSON list)
- /api/status    -> returns server metadata
- /api/about     -> returns protocol information
- /broadcast     -> Server-Sent Events (SSE) endpoint that streams new messages
- /web/...       -> serve static web UI files from the web/ directory

This server uses ThreadingHTTPServer so multiple clients can connect to /broadcast
and receive messages when they are generated. It stays dependency-free and uses
only Python's standard library.
"""
from __future__ import annotations

import json
import logging
import sys
import os
import threading
import queue
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import List

# Ensure repo root is on sys.path when running server/server.py directly.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.generator import generate_message
from core.messages import Message
from core.config import SERVER_ID, PROTOCOL_VERSION, JSON_VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stuff.server")

# In-memory recent message store (non-persistent). Keep small for safety.
RECENT_MESSAGES: List[Message] = []
MAX_RECENT = 50

# SSE client management
_CLIENTS_LOCK = threading.Lock()
_CLIENT_QUEUES: List[queue.Queue] = []


def broadcast_message(msg: Message) -> None:
    """Push a message to all connected SSE clients (non-blocking put).

    If a client's queue is full or raises, we remove it to avoid blocking the
    server indefinitely.
    """
    with _CLIENTS_LOCK:
        bad = []
        for q in list(_CLIENT_QUEUES):
            try:
                # Use put_nowait so a slow client doesn't block message delivery.
                q.put_nowait(msg)
            except Exception:
                bad.append(q)
        for q in bad:
            try:
                _CLIENT_QUEUES.remove(q)
            except ValueError:
                pass


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
            # Serve web UI files under /web/ or redirect / to the web UI
            if self.path == "/":
                self.send_response(302)
                self.send_header("Location", "/web/index.html")
                self.end_headers()
                return
            if self.path.startswith("/web/"):
                return self._serve_web_file(self.path[len("/web/"):])

            if self.path == "/api/message":
                msg = generate_message("fact")
                RECENT_MESSAGES.append(msg)
                # trim
                while len(RECENT_MESSAGES) > MAX_RECENT:
                    RECENT_MESSAGES.pop(0)
                # broadcast to SSE clients
                broadcast_message(msg)
                self._send_json(msg.to_dict())
            elif self.path == "/api/messages":
                data = [m.to_dict() for m in RECENT_MESSAGES]
                self._send_json({"messages": data})
            elif self.path == "/api/status":
                self._send_json({
                    "server_id": SERVER_ID,
                    "protocol": PROTOCOL_VERSION,
                    "version": "0.1.0",
                    "capabilities": ["messages", "broadcast" if True else ""],
                })
            elif self.path == "/api/about":
                self._send_json({
                    "protocol": PROTOCOL_VERSION,
                    "description": "STUFF — simple message protocol",
                    "formats": ["application/json", "text/stuff"],
                })
            elif self.path == "/broadcast":
                self.handle_sse()
            else:
                self.send_error(404, "Not found")
        except Exception as exc:
            logger.exception("Error handling request: %s", exc)
            try:
                self._send_json({"error": str(exc)}, status=500)
            except Exception:
                # If even sending JSON fails, log and ignore
                logger.exception("Failed to send error response")

    def _serve_web_file(self, relpath: str):
        # Prevent directory traversal
        safe_path = os.path.normpath(relpath).lstrip(os.sep)
        web_root = os.path.join(ROOT, "web")
        full = os.path.join(web_root, safe_path)
        if not full.startswith(web_root) or not os.path.exists(full):
            self.send_error(404, "Web asset not found")
            return
        ctype, _ = mimetypes.guess_type(full)
        if ctype is None:
            ctype = "application/octet-stream"
        try:
            with open(full, "rb") as fh:
                data = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:
            logger.exception("Failed to serve web file: %s", exc)
            self.send_error(500, "Internal server error")

    def handle_sse(self):
        # Prepare SSE response headers
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        q: queue.Queue = queue.Queue(maxsize=10)
        with _CLIENTS_LOCK:
            _CLIENT_QUEUES.append(q)
        logger.info("SSE client connected: %s", self.client_address)

        try:
            # Send a simple comment to establish the stream
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            while True:
                try:
                    msg: Message = q.get(timeout=60)
                except queue.Empty:
                    # send a keepalive comment every minute
                    try:
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
                        continue
                    except (BrokenPipeError, ConnectionResetError):
                        break

                try:
                    payload = json.dumps({"event": "new_message", "message": msg.to_dict()}, ensure_ascii=False)
                    body = f"data: {payload}\n\n".encode("utf-8")
                    self.wfile.write(body)
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    break
        finally:
            # cleanup
            with _CLIENTS_LOCK:
                try:
                    _CLIENT_QUEUES.remove(q)
                except ValueError:
                    pass
            logger.info("SSE client disconnected: %s", self.client_address)

    def log_message(self, format, *args):
        # route HTTP server logs through logging module
        logger.info("%s - %s", self.client_address[0], format % args)


def run(host: str = "127.0.0.1", port: int = 8000):
    server = ThreadingHTTPServer((host, port), StuffRequestHandler)
    logger.info("Stuff server starting at http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Stuff server")
        server.server_close()


if __name__ == "__main__":
    run()
