"""Helpers to format and parse the simple STUFF text protocol.

The protocol is intentionally tiny and documented in docs/PROTOCOL.md. These
helpers provide a best-effort formatter/parser for the textual representation.
"""
from __future__ import annotations

from typing import Dict
from core.messages import Message


def format_stuff_text(msg: Message) -> str:
    lines = [
        "STUFF/1.0",
        f"TYPE: {msg.type.upper()}",
        f"ID: {msg.id}",
        f"TIME: {msg.timestamp}",
        f"LENGTH: {len(msg.message)}",
        "",
        msg.message,
    ]
    return "\n".join(lines)


def parse_stuff_text(raw: str) -> Dict[str, str]:
    parts = raw.split("\n\n", 1)
    headers = parts[0].splitlines()
    body = parts[1] if len(parts) > 1 else ""
    result = {"body": body}
    for h in headers:
        if ":" in h:
            k, v = h.split(":", 1)
            result[k.strip()] = v.strip()
    return result
