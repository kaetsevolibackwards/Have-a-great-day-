"""Message generator utilities for Stuff.

This module provides a simple, reusable generator that produces Message
instances. It also provides helpers to generate a plaintext message that
matches the original `Stuff/main.py` output and write it to a file so the
legacy scripts continue to work without modification.
"""
from __future__ import annotations

import random
import uuid
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from core.messages import Message
from core.time import now_timestamp
from core.config import JSON_VERSION, SERVER_ID, DEFAULT_TZ

# Keep the same facts as the original Stuff/main.py to preserve behavior.
FACTS: List[str] = [
    "Octopuses have three hearts.",
    "Bananas are berries, but strawberries aren't.",
    "A day on Venus is longer than a year on Venus.",
    "Honey can remain edible for an extremely long time.",
    "Sharks existed before trees.",
    "Wombat poop is cube-shaped.",
    "The Eiffel Tower can grow slightly taller in hot weather.",
    "Some turtles can breathe through their butts.",
    "Cows have best friends and can become stressed when separated.",
    "A group of flamingos is called a flamboyance.",
    "The shortest war in history lasted less than an hour.",
    "Sea otters hold hands while sleeping so they don't drift apart.",
    "There are more possible games of chess than atoms in the observable universe.",
    "A bolt of lightning can be hotter than the surface of the Sun.",
    "Butterflies taste with their feet.",
]


def generate_fact() -> str:
    return random.choice(FACTS)


def _local_greeting(tz_name: str = DEFAULT_TZ) -> str:
    try:
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        now = datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "Good morning. Have a great day"
    elif hour < 18:
        greeting = "Good afternoon. Have a great day"
    else:
        greeting = "Good evening. Have a great day"
    return greeting


def generate_message(msg_type: str = "fact") -> Message:
    """Return a Message dataclass instance with a unique id and timestamp.

    The function is deterministic in shape but random in content for the
    `fact` type so it can safely replace the original main.py behavior.
    """
    content = ""
    if msg_type == "fact":
        content = generate_fact()
    elif msg_type == "greeting":
        content = "Have a great day!"
    else:
        # fallback to a short system message
        content = f"[{msg_type}]"

    msg = Message(
        version=JSON_VERSION,
        id=str(uuid.uuid4()),
        type=msg_type,
        timestamp=now_timestamp(),
        server_id=SERVER_ID,
        message=content,
    )
    return msg


def generate_plaintext_message(path: str = "message.txt", tz_name: str = DEFAULT_TZ) -> None:
    """Generate a plaintext legacy-style message and write it to `path`.

    The output matches the original `Stuff/main.py` format:

        <greeting>\n\nFun fact:\n<fact>

    This helper allows the original scripts to keep working while using the
    new core generator for message metadata and IDs.
    """
    greeting = _local_greeting(tz_name)
    fact = generate_fact()
    message = f"{greeting}\n\nFun fact:\n{fact}"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(message)

