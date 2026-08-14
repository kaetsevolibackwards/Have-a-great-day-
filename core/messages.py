from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict

@dataclass
class Message:
    version: int
    id: str
    type: str
    timestamp: int
    server_id: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            version=int(data.get("version", 1)),
            id=str(data["id"]),
            type=str(data["type"]),
            timestamp=int(data["timestamp"]),
            server_id=str(data["server_id"]),
            message=str(data["message"]),
        )

    @classmethod
    def from_json(cls, raw: str) -> "Message":
        data = json.loads(raw)
        return cls.from_dict(data)
