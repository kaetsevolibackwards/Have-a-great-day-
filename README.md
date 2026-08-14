## Stuff — local messaging platform (development build)

This repository is being migrated from a tiny message generator into "Stuff" —
a small, local networked messaging platform and protocol. The migration is
happening in phases so the repository remains runnable and the original
scripts (`Stuff/main.py` and `Stuff/other.py`) keep working.

Quick start

From the repository root:

1) Run the original generator and print the message (legacy behavior):

    python Stuff/main.py
    python Stuff/other.py

2) Run the new local HTTP server (serves API and web UI):

    python -m server.server

   - The server listens on 127.0.0.1:8000 by default.
   - Open http://127.0.0.1:8000/ in your browser to reach the web UI.

3) Use the CLI client to fetch a message from the server:

    python -m client.client --server http://127.0.0.1:8000

4) Run tests (requires pytest):

    python -m pytest

What I changed (summary)
- Preserved the original file-based scripts in Stuff/ while centralizing new logic
  in core/ so future extensions are easier and safer.
- Implemented a core Message model, generator utilities, a small HTTP server
  with JSON APIs, basic Server-Sent Events (SSE) broadcasting, and a tiny web UI.

Next steps
- Expand tests and tighten server security (rate limiting, size limits).
- Implement multi-server peer exchange and message deduplication (Phase 10).
- Expand PROTOCOL.md with more examples and formal definitions.
