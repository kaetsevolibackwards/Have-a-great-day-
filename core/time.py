"""Time-related helpers for Stuff."""
from __future__ import annotations

import time


def now_timestamp() -> int:
    """Return current POSIX timestamp as integer seconds."""
    return int(time.time())
