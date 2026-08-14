"""Simple CLI client to fetch a message from a Stuff server.

Usage:
    python -m client.client --server http://localhost:8000
"""
from __future__ import annotations

import argparse
import json
import logging
from urllib import request, error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stuff.client")


def fetch_message(server: str) -> dict:
    url = server.rstrip("/") + "/api/message"
    try:
        with request.urlopen(url, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except error.URLError as e:
        logger.error("Could not connect to server: %s", e)
        raise


def main(argv=None):
    p = argparse.ArgumentParser(description="Stuff CLI client")
    p.add_argument("--server", default="http://127.0.0.1:8000", help="Server base URL")
    args = p.parse_args(argv)

    try:
        msg = fetch_message(args.server)
        print(json.dumps(msg, indent=2, ensure_ascii=False))
    except Exception:
        logger.exception("Failed to fetch message")


if __name__ == "__main__":
    main()
