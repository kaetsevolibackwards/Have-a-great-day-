# STUFF protocol (v1) - human-readable specification

This document specifies STUFF/1.0 — a tiny application protocol for exchanging
short messages between Stuff servers and clients. The protocol is intentionally
simple and designed to be used over HTTP or as a plain-text format.

Versioning
- Protocol: STUFF/1.0
- Message JSON version: version field in the JSON payload (integer)

Message types
- fact
- joke
- quote
- greeting
- system

JSON message format (recommended for HTTP APIs)
Example:

{
  "version": 1,
  "id": "unique-message-id",
  "type": "fact",
  "timestamp": 1234567890,
  "server_id": "STUFF-SERVER-01",
  "message": "Octopuses have three hearts."
}

Fields:
- version: integer, JSON schema version
- id: string, universally unique identifier for the message
- type: string, one of the message types above
- timestamp: integer, POSIX epoch seconds
- server_id: string, identifier of the originating server
- message: string, the textual payload

HTTP API
Use normal HTTP methods and JSON payloads. Content-Type: application/json is used
for JSON responses.

Endpoints:
- GET /api/message
  - Returns: 200 OK with a single JSON message object (as above)
  - Example response: { ... }

- GET /api/messages
  - Returns: 200 OK with { "messages": [ ... ] }

- GET /api/status
  - Returns server discovery info such as server_id, protocol, version, capabilities

- GET /api/about
  - Returns human-readable protocol information and supported formats

STUFF text format (legacy / alternate)
A compact text representation for human-readable transports.

Example:

STUFF/1.0
TYPE: FACT
ID: 84921
TIME: 1234567890
LENGTH: 31

Wombat poop is cube-shaped.

Notes on usage
- The JSON format is preferred for programmatic access.
- The text format is useful for debugging, logs, or non-JSON transports.
- Servers should assign unique IDs to messages and include a timestamp and server_id.
- When implementing multi-server propagation, messages should carry origin server_id
  and a TTL/count to avoid infinite loops.

Error handling
- HTTP endpoints must return appropriate HTTP status codes.
- For client errors return 4xx with a JSON { "error": "message" } body when possible.
- For server errors return 5xx with JSON error body.

Security
- Default to listening on localhost only.
- Validate and limit request sizes and URL lengths.
- Do not accept arbitrary commands or execute received code.

This spec is intentionally minimal and will be extended in future revisions.
